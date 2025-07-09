"""
MCP server for web crawling with Crawl4AI.

This server provides tools to crawl websites using Crawl4AI, automatically detecting
the appropriate crawl method based on URL type (sitemap, txt file, or regular webpage).
Also includes AI hallucination detection and repository parsing tools using Neo4j knowledge graphs.
"""
from mcp.server.fastmcp import FastMCP, Context
from sentence_transformers import CrossEncoder
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urldefrag
from xml.etree import ElementTree
from dotenv import load_dotenv
from supabase import Client
from pathlib import Path
import requests
import asyncio
import json
import os
import re
import concurrent.futures
import sys
from datetime import datetime

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher

# Add knowledge_graphs folder to path for importing knowledge graph modules
knowledge_graphs_path = Path(__file__).resolve().parent.parent / 'knowledge_graphs'
sys.path.append(str(knowledge_graphs_path))

from utils import (
    get_supabase_client, 
    add_documents_to_supabase, 
    search_documents,
    extract_code_blocks,
    generate_code_example_summary,
    add_code_examples_to_supabase,
    update_source_info,
    extract_source_summary,
    search_code_examples
)

# Import IAP tools
from iap_tools import IAPManager

# Import knowledge graph modules
from knowledge_graph_validator import KnowledgeGraphValidator
from parse_repo_into_neo4j import DirectNeo4jExtractor
from ai_script_analyzer import AIScriptAnalyzer
from hallucination_reporter import HallucinationReporter

# Import graph-enhanced academic planning tools
from graph_enhanced_tools import GraphEnhancedAcademicPlanner
from academic_graph_builder import AcademicGraphBuilder

# Load environment variables from the project root .env file
project_root = Path(__file__).resolve().parent.parent
dotenv_path = project_root / '.env'

# Force override of existing environment variables
load_dotenv(dotenv_path, override=True)

# Helper functions for Neo4j validation and error handling
def validate_neo4j_connection() -> bool:
    """Check if Neo4j environment variables are configured."""
    return all([
        os.getenv("NEO4J_URI"),
        os.getenv("NEO4J_USER"),
        os.getenv("NEO4J_PASSWORD")
    ])

def format_neo4j_error(error: Exception) -> str:
    """Format Neo4j connection errors for user-friendly messages."""
    error_str = str(error).lower()
    if "authentication" in error_str or "unauthorized" in error_str:
        return "Neo4j authentication failed. Check NEO4J_USER and NEO4J_PASSWORD."
    elif "connection" in error_str or "refused" in error_str or "timeout" in error_str:
        return "Cannot connect to Neo4j. Check NEO4J_URI and ensure Neo4j is running."
    elif "database" in error_str:
        return "Neo4j database error. Check if the database exists and is accessible."
    else:
        return f"Neo4j error: {str(error)}"

def validate_script_path(script_path: str) -> Dict[str, Any]:
    """Validate script path and return error info if invalid."""
    if not script_path or not isinstance(script_path, str):
        return {"valid": False, "error": "Script path is required"}
    
    if not os.path.exists(script_path):
        return {"valid": False, "error": f"Script not found: {script_path}"}
    
    if not script_path.endswith('.py'):
        return {"valid": False, "error": "Only Python (.py) files are supported"}
    
    try:
        # Check if file is readable
        with open(script_path, 'r', encoding='utf-8') as f:
            f.read(1)  # Read first character to test
        return {"valid": True}
    except Exception as e:
        return {"valid": False, "error": f"Cannot read script file: {str(e)}"}

def validate_github_url(repo_url: str) -> Dict[str, Any]:
    """Validate GitHub repository URL."""
    if not repo_url or not isinstance(repo_url, str):
        return {"valid": False, "error": "Repository URL is required"}
    
    repo_url = repo_url.strip()
    
    # Basic GitHub URL validation
    if not ("github.com" in repo_url.lower() or repo_url.endswith(".git")):
        return {"valid": False, "error": "Please provide a valid GitHub repository URL"}
    
    # Check URL format
    if not (repo_url.startswith("https://") or repo_url.startswith("git@")):
        return {"valid": False, "error": "Repository URL must start with https:// or git@"}
    
    return {"valid": True, "repo_name": repo_url.split('/')[-1].replace('.git', '')}

# Create a dataclass for our application context
@dataclass
class Crawl4AIContext:
    """Context for the Crawl4AI MCP server."""
    crawler: AsyncWebCrawler
    supabase_client: Client
    reranking_model: Optional[CrossEncoder] = None
    knowledge_validator: Optional[Any] = None  # KnowledgeGraphValidator when available
    repo_extractor: Optional[Any] = None       # DirectNeo4jExtractor when available

@asynccontextmanager
async def crawl4ai_lifespan(server: FastMCP) -> AsyncIterator[Crawl4AIContext]:
    """
    Manages the Crawl4AI client lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        Crawl4AIContext: The context containing the Crawl4AI crawler and Supabase client
    """
    # Create browser configuration
    browser_config = BrowserConfig(
        headless=True,
        verbose=False
    )
    
    # Initialize the crawler
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.__aenter__()
    
    # Initialize Supabase client
    supabase_client = get_supabase_client()
    
    # Initialize cross-encoder model for reranking if enabled
    reranking_model = None
    if os.getenv("USE_RERANKING", "false") == "true":
        try:
            reranking_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        except Exception as e:
            print(f"Failed to load reranking model: {e}")
            reranking_model = None
    
    # Initialize Neo4j components if configured and enabled
    knowledge_validator = None
    repo_extractor = None
    
    # Check if knowledge graph functionality is enabled
    knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"
    
    if knowledge_graph_enabled:
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = os.getenv("NEO4J_USER")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        
        if neo4j_uri and neo4j_user and neo4j_password:
            try:
                print("Initializing knowledge graph components...")
                
                # Initialize knowledge graph validator
                knowledge_validator = KnowledgeGraphValidator(neo4j_uri, neo4j_user, neo4j_password)
                await knowledge_validator.initialize()
                print("✓ Knowledge graph validator initialized")
                
                # Initialize repository extractor
                repo_extractor = DirectNeo4jExtractor(neo4j_uri, neo4j_user, neo4j_password)
                await repo_extractor.initialize()
                print("✓ Repository extractor initialized")
                
            except Exception as e:
                print(f"Failed to initialize Neo4j components: {format_neo4j_error(e)}")
                knowledge_validator = None
                repo_extractor = None
        else:
            print("Neo4j credentials not configured - knowledge graph tools will be unavailable")
    else:
        print("Knowledge graph functionality disabled - set USE_KNOWLEDGE_GRAPH=true to enable")
    
    try:
        yield Crawl4AIContext(
            crawler=crawler,
            supabase_client=supabase_client,
            reranking_model=reranking_model,
            knowledge_validator=knowledge_validator,
            repo_extractor=repo_extractor
        )
    finally:
        # Clean up all components
        await crawler.__aexit__(None, None, None)
        if knowledge_validator:
            try:
                await knowledge_validator.close()
                print("✓ Knowledge graph validator closed")
            except Exception as e:
                print(f"Error closing knowledge validator: {e}")
        if repo_extractor:
            try:
                await repo_extractor.close()
                print("✓ Repository extractor closed")
            except Exception as e:
                print(f"Error closing repository extractor: {e}")

# Initialize FastMCP server
mcp = FastMCP(
    "mcp-crawl4ai-rag",
    description="MCP server for RAG and web crawling with Crawl4AI",
    lifespan=crawl4ai_lifespan,
    host=os.getenv("HOST", "0.0.0.0"),
    port=os.getenv("PORT", "8051")
)

def rerank_results(model: CrossEncoder, query: str, results: List[Dict[str, Any]], content_key: str = "content") -> List[Dict[str, Any]]:
    """
    Rerank search results using a cross-encoder model.
    
    Args:
        model: The cross-encoder model to use for reranking
        query: The search query
        results: List of search results
        content_key: The key in each result dict that contains the text content
        
    Returns:
        Reranked list of results
    """
    if not model or not results:
        return results
    
    try:
        # Extract content from results
        texts = [result.get(content_key, "") for result in results]
        
        # Create pairs of [query, document] for the cross-encoder
        pairs = [[query, text] for text in texts]
        
        # Get relevance scores from the cross-encoder
        scores = model.predict(pairs)
        
        # Add scores to results and sort by score (descending)
        for i, result in enumerate(results):
            result["rerank_score"] = float(scores[i])
        
        # Sort by rerank score
        reranked = sorted(results, key=lambda x: x.get("rerank_score", 0), reverse=True)
        
        return reranked
    except Exception as e:
        print(f"Error during reranking: {e}")
        return results

def is_sitemap(url: str) -> bool:
    """
    Check if a URL is a sitemap.
    
    Args:
        url: URL to check
        
    Returns:
        True if the URL is a sitemap, False otherwise
    """
    return url.endswith('sitemap.xml') or 'sitemap' in urlparse(url).path

def is_txt(url: str) -> bool:
    """
    Check if a URL is a text file.
    
    Args:
        url: URL to check
        
    Returns:
        True if the URL is a text file, False otherwise
    """
    return url.endswith('.txt')

def parse_sitemap(sitemap_url: str) -> List[str]:
    """
    Parse a sitemap and extract URLs.
    
    Args:
        sitemap_url: URL of the sitemap
        
    Returns:
        List of URLs found in the sitemap
    """
    resp = requests.get(sitemap_url)
    urls = []

    if resp.status_code == 200:
        try:
            tree = ElementTree.fromstring(resp.content)
            urls = [loc.text for loc in tree.findall('.//{*}loc')]
        except Exception as e:
            print(f"Error parsing sitemap XML: {e}")

    return urls

def chunk_academic_content(markdown_text: str) -> List[Dict[str, Any]]:
    """
    Intelligently chunks academic content based on content type.
    Handles degree programs, courses, and their relationships.
    """
    content_type = detect_content_type(markdown_text)
    
    if content_type == "department_overview":
        return chunk_department_overview(markdown_text)
    elif content_type == "program_detail":
        return chunk_program_detail(markdown_text)
    elif content_type == "course_catalog":
        return chunk_course_catalog(markdown_text)
    else:
        # Fallback to generic chunking
        return chunk_generic_content(markdown_text)

def detect_content_type(markdown_text: str) -> str:
    """
    Detects the type of academic content to determine chunking strategy.
    """
    # Check for department overview patterns
    if re.search(r'#{1,4}\s*\*\*Master\'s Degree\*\*', markdown_text) or \
       re.search(r'#{1,4}\s*\*\*Bachelor Degrees\*\*', markdown_text) or \
       re.search(r'Department Degrees and Minors', markdown_text):
        return "department_overview"
    
    # Check for course catalog patterns (multiple course codes)
    course_codes = re.findall(r'\b[A-Z]{2,4}\s\d{3,4}[A-Z]?\b', markdown_text)
    if len(course_codes) >= 3:
        return "course_catalog"
    
    # Check for program detail patterns
    if re.search(r'Bachelor of|Master of|Associate of', markdown_text) and \
       re.search(r'Requirements|Prerequisites|Credits', markdown_text, re.IGNORECASE):
        return "program_detail"
    
    return "generic"

def chunk_department_overview(markdown_text: str) -> List[Dict[str, Any]]:
    """
    Chunks department overview pages by program sections.
    Each section (Master's, Bachelor's, Minors, etc.) becomes one chunk.
    """
    chunks = []
    
    # Split by major program sections using the exact pattern from Utah Tech
    section_pattern = re.compile(r'####\s*\*\*([^*]+)\*\*')
    sections = section_pattern.split(markdown_text)
    
    # First part is the department header (before any sections)
    if sections[0].strip():
        header_content = sections[0].strip()
        # Extract just the department info, not the navigation/footer
        header_lines = header_content.split('\n')
        dept_lines = []
        for line in header_lines:
            if any(dept_word in line for dept_word in ['Department', 'Programs']) and not any(skip in line.lower() for skip in ['skip to content', 'catalog home', 'academic calendar']):
                dept_lines.append(line)
            elif line.strip() and line.startswith('#'):
                dept_lines.append(line)
        
        if dept_lines:
            chunks.append({
                'content': '\n'.join(dept_lines),
                'metadata': extract_academic_info('\n'.join(dept_lines), "department_header")
            })
    
    # Process each section (Master's, Bachelor's, etc.)
    for i in range(1, len(sections), 2):
        if i < len(sections):
            section_name = sections[i].strip()
            section_content = sections[i + 1].strip() if i + 1 < len(sections) else ""
            
            if section_content:
                # Clean up section content - remove footer navigation
                content_lines = section_content.split('\n')
                clean_lines = []
                for line in content_lines:
                    # Stop at common footer patterns
                    if any(footer_marker in line for footer_marker in [
                        'Click here for the', 'Website (following this link',
                        'Edition', 'Search catalog', 'Welcome Trailblazers',
                        'Getting Started at Utah Tech', 'Academic Policies'
                    ]):
                        break
                    clean_lines.append(line)
                
                clean_content = '\n'.join(clean_lines).strip()
                if clean_content:
                    # Create one chunk per section with all its programs
                    full_section = f"#### **{section_name}**\n{clean_content}"
                    chunks.append({
                        'content': full_section,
                        'metadata': extract_academic_info(full_section, "program_section", {
                            'section_type': section_name,
                            'degree_level': classify_degree_level(section_name)
                        })
                    })
    
    return chunks if chunks else [{
        'content': markdown_text,
        'metadata': extract_academic_info(markdown_text, "department_overview")
    }]

def chunk_program_detail(markdown_text: str) -> List[Dict[str, Any]]:
    """
    Chunks individual program detail pages.
    """
    return [{
        'content': markdown_text,
        'metadata': extract_academic_info(markdown_text, "program_detail")
    }]

def chunk_course_catalog(markdown_text: str) -> List[Dict[str, Any]]:
    """
    Chunks course catalog pages by individual courses.
    """
    # Pattern to match course codes in Utah Tech format: **ART 1001. Course Name**
    course_pattern = re.compile(r'\*\*([A-Z]{2,4}\s\d{3,4}[A-Z]?)\.')
    matches = list(course_pattern.finditer(markdown_text))
    
    if not matches:
        return [{
            'content': markdown_text,
            'metadata': extract_academic_info(markdown_text, "course_catalog")
        }]
    
    chunks = []
    for i, match in enumerate(matches):
        start_pos = match.start()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        
        chunk_content = markdown_text[start_pos:end_pos].strip()
        if chunk_content:
            chunks.append({
                'content': chunk_content,
                'metadata': extract_academic_info(chunk_content, "course")
            })
    
    return chunks

def chunk_generic_content(markdown_text: str) -> List[Dict[str, Any]]:
    """
    Generic chunking for unclassified content.
    """
    return [{
        'content': markdown_text,
        'metadata': extract_academic_info(markdown_text, "generic")
    }]

def classify_degree_level(section_type: str) -> str:
    """
    Classifies the degree level based on section type.
    """
    section_lower = section_type.lower()
    if 'master' in section_lower or 'graduate' in section_lower:
        return 'graduate'
    elif 'bachelor' in section_lower or 'undergraduate' in section_lower:
        return 'undergraduate'
    elif 'minor' in section_lower:
        return 'minor'
    elif 'certificate' in section_lower:
        return 'certificate'
    else:
        return 'unknown'

def extract_academic_info(chunk: str, content_type: str, extra_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Extracts comprehensive academic metadata from a chunk based on its content type.
    """
    metadata = {
        "content_type": content_type,
        "char_count": len(chunk),
        "word_count": len(chunk.split())
    }
    
    # Add extra metadata if provided
    if extra_metadata:
        metadata.update(extra_metadata)
    
    # Extract course codes
    course_codes = re.findall(r'\b([A-Z]{2,4}\s\d{3,4}[A-Z]?)\b', chunk)
    metadata["course_codes"] = course_codes
    metadata["course_count"] = len(course_codes)
    
    # Extract degree information
    degree_matches = re.findall(r'(Bachelor of [^,\n]+|Master of [^,\n]+|Associate of [^,\n]+)', chunk)
    metadata["degrees"] = degree_matches
    
    # Extract department information
    dept_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*) Department', chunk)
    if dept_match:
        metadata["department"] = dept_match.group(1)
    
    # Content-specific extractions
    if content_type == "course":
        # Extract course-specific information
        if course_codes:
            metadata["primary_course_code"] = course_codes[0]
            metadata["is_single_course"] = len(course_codes) == 1
        
        # Extract credits
        credit_match = re.search(r'(\d+)\s*credits?', chunk, re.IGNORECASE)
        if credit_match:
            metadata["credits"] = int(credit_match.group(1))
    
    elif content_type in ["program_listing", "program_section"]:
        # Extract program-specific information
        metadata["is_program"] = True
        
        # Count programs in this section
        program_links = re.findall(r'\*\s*\[([^\]]+)\]\(([^)]+)\)', chunk)
        metadata["programs_in_section"] = len(program_links)
        metadata["program_names"] = [name for name, url in program_links]
        
        # Extract emphasis/specialization
        emphasis_matches = re.findall(r'([^-\[]+)\s*Emphasis', chunk)
        if emphasis_matches:
            metadata["emphases"] = [emp.strip() for emp in emphasis_matches]
    
    elif content_type == "department_overview":
        # Extract department overview information
        metadata["is_department_overview"] = True
        
        # Count programs by type
        metadata["masters_programs"] = len(re.findall(r'Master of|MFA|MS|MA', chunk))
        metadata["bachelors_programs"] = len(re.findall(r'Bachelor of|BA|BS', chunk))
        metadata["minors_count"] = len(re.findall(r'Minor', chunk))
        metadata["certificates_count"] = len(re.findall(r'Certificate', chunk))
    
    return metadata

def process_code_example(args):
    """
    Process a single code example to generate its summary.
    This function is designed to be used with concurrent.futures.
    
    Args:
        args: Tuple containing (code, context_before, context_after)
        
    Returns:
        The generated summary
    """
    code, context_before, context_after = args
    return generate_code_example_summary(code, context_before, context_after)


def get_supabase_from_context(ctx: Context):
    """
    Safely extract supabase client from context with multiple fallback approaches.
    This handles different MCP context structures and deployment environments.
    """
    try:
        # Try the standard FastMCP approach first
        if hasattr(ctx, 'request_context') and hasattr(ctx.request_context, 'lifespan_context'):
            if hasattr(ctx.request_context.lifespan_context, 'supabase_client'):
                return ctx.request_context.lifespan_context.supabase_client
    except AttributeError:
        pass
    
    try:
        # Try direct access
        if hasattr(ctx, 'supabase_client'):
            return ctx.supabase_client
    except AttributeError:
        pass
    
    try:
        # Try lifespan_context directly on ctx
        if hasattr(ctx, 'lifespan_context') and hasattr(ctx.lifespan_context, 'supabase_client'):
            return ctx.lifespan_context.supabase_client
    except AttributeError:
        pass
    
    # Last resort - create a new client using environment variables
    try:
        from utils import get_supabase_client
        return get_supabase_client()
    except Exception as e:
        raise Exception(f"Unable to access Supabase client from context. Tried multiple approaches. Last error: {str(e)}")


@mcp.tool()
async def debug_context_structure(ctx: Context) -> str:
    """
    Debug tool to inspect the MCP context structure.
    This helps understand how to properly access the supabase_client.
    """
    try:
        context_info = {
            "context_type": str(type(ctx)),
            "context_attributes": dir(ctx),
            "has_request_context": hasattr(ctx, 'request_context'),
            "has_supabase_client": hasattr(ctx, 'supabase_client'),
        }
        
        if hasattr(ctx, 'request_context'):
            context_info["request_context_type"] = str(type(ctx.request_context))
            context_info["request_context_attributes"] = dir(ctx.request_context)
            
            if hasattr(ctx.request_context, 'lifespan_context'):
                context_info["has_lifespan_context"] = True
                context_info["lifespan_context_type"] = str(type(ctx.request_context.lifespan_context))
                context_info["lifespan_context_attributes"] = dir(ctx.request_context.lifespan_context)
                context_info["has_supabase_in_lifespan"] = hasattr(ctx.request_context.lifespan_context, 'supabase_client')
            else:
                context_info["has_lifespan_context"] = False
        
        return json.dumps(context_info, indent=2, default=str)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to debug context: {str(e)}",
            "context_type": str(type(ctx)) if ctx else "None"
        }, indent=2)


@mcp.tool()
async def crawl_single_page(ctx: Context, url: str) -> str:
    """
    Crawl a single web page and store its content in Supabase.
    
    This tool is ideal for quickly retrieving content from a specific URL without following links.
    The content is stored in Supabase for later retrieval and querying.
    
    Args:
        ctx: The MCP server provided context
        url: URL of the web page to crawl
    
    Returns:
        Summary of the crawling operation and storage in Supabase
    """
    try:
        # Get the crawler from the context
        crawler = ctx.request_context.lifespan_context.crawler
        supabase_client = get_supabase_from_context(ctx)
        
        # Configure the crawl
        run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
        
        # Crawl the page
        result = await crawler.arun(url=url, config=run_config)
        
        if result.success and result.markdown:
            # Use the new academic chunking system
            chunk_data_list = chunk_academic_content(result.markdown)
            
            # Extract source_id
            parsed_url = urlparse(url)
            source_id = parsed_url.netloc or parsed_url.path
            
            # Prepare data for Supabase storage
            urls = []
            chunk_numbers = []
            contents = []
            metadatas = []
            
            for i, chunk_data in enumerate(chunk_data_list):
                content = chunk_data['content']
                meta = chunk_data['metadata']
                
                # Add source and URL info to metadata
                meta["source_id"] = source_id
                meta["url"] = url
                meta["crawl_time"] = datetime.now().isoformat()
                
                urls.append(url)
                chunk_numbers.append(i)
                contents.append(content)
                metadatas.append(meta)
            
            # Create url_to_full_document mapping
            url_to_full_document = {url: result.markdown}
            
            # Generate source summary
            source_summary = extract_source_summary(source_id, result.markdown[:5000])
            word_count = len(result.markdown.split())
            update_source_info(supabase_client, source_id, source_summary, word_count)
            
            # Store chunks in Supabase
            add_documents_to_supabase(supabase_client, urls, chunk_numbers, contents, metadatas, url_to_full_document)
            
            return json.dumps({
                "success": True,
                "url": url,
                "source_id": source_id,
                "chunks_created": len(chunk_data_list),
                "content_type": chunk_data_list[0]['metadata'].get('content_type', 'unknown') if chunk_data_list else 'none',
                "total_characters": len(result.markdown),
                "total_words": word_count,
                "chunk_summary": [
                    {
                        "chunk_id": i,
                        "content_type": chunk['metadata'].get('content_type', 'unknown'),
                        "char_count": chunk['metadata'].get('char_count', 0),
                        "word_count": chunk['metadata'].get('word_count', 0),
                        "course_codes": chunk['metadata'].get('course_codes', []),
                        "programs_in_section": chunk['metadata'].get('programs_in_section', 0)
                    } for i, chunk in enumerate(chunk_data_list)
                ]
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "url": url,
                "error": result.error_message or "No content retrieved"
            }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "url": url,
            "error": str(e)
        }, indent=2)

@mcp.tool()
async def smart_crawl_url(ctx: Context, url: str, max_depth: int = 3, max_concurrent: int = 10, chunk_size: int = 5000) -> str:
    """
    Intelligently crawl a URL based on its type and store content in Supabase.
    
    This tool automatically detects the URL type and applies the appropriate crawling method:
    - For sitemaps: Extracts and crawls all URLs in parallel
    - For text files (llms.txt): Directly retrieves the content
    - For regular webpages: Recursively crawls internal links up to the specified depth
    
    All crawled content is chunked and stored in Supabase for later retrieval and querying.
    
    Args:
        ctx: The MCP server provided context
        url: URL to crawl (can be a regular webpage, sitemap.xml, or .txt file)
        max_depth: Maximum recursion depth for regular URLs (default: 3)
        max_concurrent: Maximum number of concurrent browser sessions (default: 10)
        chunk_size: Maximum size of each content chunk in characters (default: 1000)
    
    Returns:
        JSON string with crawl summary and storage information
    """
    try:
        # Get the crawler from the context
        crawler = ctx.request_context.lifespan_context.crawler
        supabase_client = get_supabase_from_context(ctx)
        
        # Determine the crawl strategy
        crawl_results = []
        crawl_type = None
        
        if is_txt(url):
            # For text files, use simple crawl
            crawl_results = await crawl_markdown_file(crawler, url)
            crawl_type = "text_file"
        elif is_sitemap(url):
            # For sitemaps, extract URLs and crawl in parallel
            sitemap_urls = parse_sitemap(url)
            if not sitemap_urls:
                return json.dumps({
                    "success": False,
                    "url": url,
                    "error": "No URLs found in sitemap"
                }, indent=2)
            crawl_results = await crawl_batch(crawler, sitemap_urls, max_concurrent=max_concurrent)
            crawl_type = "sitemap"
        else:
            # For regular URLs, use recursive crawl
            crawl_results = await crawl_recursive_internal_links(crawler, [url], max_depth=max_depth, max_concurrent=max_concurrent)
            crawl_type = "webpage"
        
        if not crawl_results:
            return json.dumps({
                "success": False,
                "url": url,
                "error": "No content found"
            }, indent=2)
        
        # Process results and store in Supabase
        urls = []
        chunk_numbers = []
        contents = []
        metadatas = []
        chunk_count = 0
        
        # Track sources and their content
        source_content_map = {}
        source_word_counts = {}
        
        # Process documentation chunks
        for doc in crawl_results:
            source_url = doc['url']
            md = doc['markdown']
            chunk_data_list = chunk_academic_content(md)
            
            # Extract source_id
            parsed_url = urlparse(source_url)
            source_id = parsed_url.netloc or parsed_url.path
            
            # Store content for source summary generation
            if source_id not in source_content_map:
                source_content_map[source_id] = md[:5000]  # Store first 5000 chars
                source_word_counts[source_id] = 0
            
            for i, chunk_data in enumerate(chunk_data_list):
                content = chunk_data['content']
                meta = chunk_data['metadata']

                urls.append(source_url)
                chunk_numbers.append(i)
                contents.append(content)
                
                # Add additional metadata
                meta["chunk_index"] = i
                meta["url"] = source_url
                meta["source"] = source_id
                meta["crawl_type"] = crawl_type
                meta["crawl_time"] = str(asyncio.current_task().get_coro().__name__)
                metadatas.append(meta)
                
                # Accumulate word count
                source_word_counts[source_id] += meta.get("word_count", 0)
                
                chunk_count += 1
        
        # Create url_to_full_document mapping
        url_to_full_document = {}
        for doc in crawl_results:
            url_to_full_document[doc['url']] = doc['markdown']
        
        # Update source information for each unique source FIRST (before inserting documents)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            source_summary_args = [(source_id, content) for source_id, content in source_content_map.items()]
            source_summaries = list(executor.map(lambda args: extract_source_summary(args[0], args[1]), source_summary_args))
        
        for (source_id, _), summary in zip(source_summary_args, source_summaries):
            word_count = source_word_counts.get(source_id, 0)
            update_source_info(supabase_client, source_id, summary, word_count)
        
        # Add documentation chunks to Supabase (AFTER sources exist)
        batch_size = 20
        add_documents_to_supabase(supabase_client, urls, chunk_numbers, contents, metadatas, url_to_full_document, batch_size=batch_size)
        
        # Extract and process code examples from all documents only if enabled
        extract_code_examples_enabled = os.getenv("USE_AGENTIC_RAG", "false") == "true"
        if extract_code_examples_enabled:
            all_code_blocks = []
            code_urls = []
            code_chunk_numbers = []
            code_examples = []
            code_summaries = []
            code_metadatas = []
            
            # Extract code blocks from all documents
            for doc in crawl_results:
                source_url = doc['url']
                md = doc['markdown']
                code_blocks = extract_code_blocks(md)
                
                if code_blocks:
                    # Process code examples in parallel
                    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                        # Prepare arguments for parallel processing
                        summary_args = [(block['code'], block['context_before'], block['context_after']) 
                                        for block in code_blocks]
                        
                        # Generate summaries in parallel
                        summaries = list(executor.map(process_code_example, summary_args))
                    
                    # Prepare code example data
                    parsed_url = urlparse(source_url)
                    source_id = parsed_url.netloc or parsed_url.path
                    
                    for i, (block, summary) in enumerate(zip(code_blocks, summaries)):
                        code_urls.append(source_url)
                        code_chunk_numbers.append(len(code_examples))  # Use global code example index
                        code_examples.append(block['code'])
                        code_summaries.append(summary)
                        
                        # Create metadata for code example
                        code_meta = {
                            "chunk_index": len(code_examples) - 1,
                            "url": source_url,
                            "source": source_id,
                            "char_count": len(block['code']),
                            "word_count": len(block['code'].split())
                        }
                        code_metadatas.append(code_meta)
            
            # Add all code examples to Supabase
            if code_examples:
                add_code_examples_to_supabase(
                    supabase_client, 
                    code_urls, 
                    code_chunk_numbers, 
                    code_examples, 
                    code_summaries, 
                    code_metadatas,
                    batch_size=batch_size
                )
        
        return json.dumps({
            "success": True,
            "url": url,
            "crawl_type": crawl_type,
            "pages_crawled": len(crawl_results),
            "chunks_stored": chunk_count,
            "code_examples_stored": len(code_examples),
            "sources_updated": len(source_content_map),
            "urls_crawled": [doc['url'] for doc in crawl_results][:5] + (["..."] if len(crawl_results) > 5 else [])
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "url": url,
            "error": str(e)
        }, indent=2)

@mcp.tool()
async def get_available_sources(ctx: Context) -> str:
    """
    Get all available sources from the sources table.
    
    This tool returns a list of all unique sources (domains) that have been crawled and stored
    in the database, along with their summaries and statistics. This is useful for discovering 
    what content is available for querying.

    Always use this tool before calling the RAG query or code example query tool
    with a specific source filter!
    
    Args:
        ctx: The MCP server provided context
    
    Returns:
        JSON string with the list of available sources and their details
    """
    try:
        # Get the Supabase client from the context
        supabase_client = get_supabase_from_context(ctx)
        
        # Query the sources table directly
        result = supabase_client.from_('sources')\
            .select('*')\
            .order('source_id')\
            .execute()
        
        # Format the sources with their details
        sources = []
        if result.data:
            for source in result.data:
                sources.append({
                    "source_id": source.get("source_id"),
                    "summary": source.get("summary"),
                    "total_words": source.get("total_words"),
                    "created_at": source.get("created_at"),
                    "updated_at": source.get("updated_at")
                })
        
        return json.dumps({
            "success": True,
            "sources": sources,
            "count": len(sources)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

@mcp.tool()
async def perform_rag_query(ctx: Context, query: str, source: str = None, match_count: int = 5) -> str:
    """
    Perform a RAG (Retrieval Augmented Generation) query on the stored content.
    
    This tool searches the vector database for content relevant to the query and returns
    the matching documents. Optionally filter by source domain.
    Get the source by using the get_available_sources tool before calling this search!
    
    Args:
        ctx: The MCP server provided context
        query: The search query
        source: Optional source domain to filter results (e.g., 'example.com')
        match_count: Maximum number of results to return (default: 5)
    
    Returns:
        JSON string with the search results
    """
    try:
        # Get the Supabase client from the context
        supabase_client = get_supabase_from_context(ctx)
        
        # Check if hybrid search is enabled
        use_hybrid_search = os.getenv("USE_HYBRID_SEARCH", "false") == "true"
        
        # Prepare source filter if provided
        source_filter = source.strip() if source and source.strip() else None
        
        if use_hybrid_search:
            # Hybrid search: combine vector and keyword search
            
            # 1. Get vector search results (get more to account for filtering)
            vector_results = search_documents(
                client=supabase_client,
                query=query,
                match_count=match_count * 2,  # Get double to have room for filtering
                source_filter=source_filter
            )
            
            # 2. Get keyword search results using ILIKE
            keyword_query = supabase_client.from_('crawled_pages')\
                .select('id, url, chunk_number, content, metadata, source_id')\
                .ilike('content', f'%{query}%')
            
            # Apply source filter if provided
            if source and source.strip():
                keyword_query = keyword_query.eq('source_id', source)
            
            # Execute keyword search
            keyword_response = keyword_query.limit(match_count * 2).execute()
            keyword_results = keyword_response.data if keyword_response.data else []
            
            # 3. Combine results with preference for items appearing in both
            seen_ids = set()
            combined_results = []
            
            # First, add items that appear in both searches (these are the best matches)
            vector_ids = {r.get('id') for r in vector_results if r.get('id')}
            for kr in keyword_results:
                if kr['id'] in vector_ids and kr['id'] not in seen_ids:
                    # Find the vector result to get similarity score
                    for vr in vector_results:
                        if vr.get('id') == kr['id']:
                            # Boost similarity score for items in both results
                            vr['similarity'] = min(1.0, vr.get('similarity', 0) * 1.2)
                            combined_results.append(vr)
                            seen_ids.add(kr['id'])
                            break
            
            # Then add remaining vector results (semantic matches without exact keyword)
            for vr in vector_results:
                if vr.get('id') and vr['id'] not in seen_ids and len(combined_results) < match_count:
                    combined_results.append(vr)
                    seen_ids.add(vr['id'])
            
            # Finally, add pure keyword matches if we still need more results
            for kr in keyword_results:
                if kr['id'] not in seen_ids and len(combined_results) < match_count:
                    # Convert keyword result to match vector result format
                    combined_results.append({
                        'id': kr['id'],
                        'url': kr['url'],
                        'chunk_number': kr['chunk_number'],
                        'content': kr['content'],
                        'metadata': kr['metadata'],
                        'source_id': kr['source_id'],
                        'similarity': 0.5  # Default similarity for keyword-only matches
                    })
                    seen_ids.add(kr['id'])
            
            # Use combined results
            results = combined_results[:match_count]
            
        else:
            # Standard vector search only
            results = search_documents(
                client=supabase_client,
                query=query,
                match_count=match_count,
                source_filter=source_filter
            )
        
        # Apply reranking if enabled
        use_reranking = os.getenv("USE_RERANKING", "false") == "true"
        if use_reranking and ctx.request_context.lifespan_context.reranking_model:
            results = rerank_results(ctx.request_context.lifespan_context.reranking_model, query, results, content_key="content")
        
        # Format the results
        formatted_results = []
        for result in results:
            formatted_result = {
                "url": result.get("url"),
                "content": result.get("content"),
                "metadata": result.get("metadata"),
                "similarity": result.get("similarity")
            }
            # Include rerank score if available
            if "rerank_score" in result:
                formatted_result["rerank_score"] = result["rerank_score"]
            formatted_results.append(formatted_result)
        
        return json.dumps({
            "success": True,
            "query": query,
            "source_filter": source,
            "search_mode": "hybrid" if use_hybrid_search else "vector",
            "reranking_applied": use_reranking and ctx.request_context.lifespan_context.reranking_model is not None,
            "results": formatted_results,
            "count": len(formatted_results)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "query": query,
            "error": str(e)
        }, indent=2)

@mcp.tool()
async def search_degree_programs(ctx: Context, query: str, source_id: str = None, match_count: int = 5) -> str:
    """
    Search for degree programs and majors relevant to the query.
    
    This tool searches the academic catalog for degree programs, majors, and academic
    emphases that match the query. Useful for IAP development and academic planning.
    
    **Student Collaboration Context:**
    - **When to Use**: When exploring potential concentration areas or comparing programs
    - **How to Introduce**: "Let's explore what programs Utah Tech offers in your areas of interest"
    - **Student Involvement**: Discuss which programs align with student's interests and goals
    - **Follow-up**: "Which of these programs interests you most? How might they fit into your IAP?"
    
    **Communication Tips:**
    - Help students see connections between different programs
    - Encourage exploration of interdisciplinary opportunities
    - Connect program features to student's career aspirations
    
    Args:
        ctx: The MCP server provided context
        query: The search query (e.g., "psychology programs", "business degrees")
        source_id: Optional source ID to filter results (e.g., 'catalog.utahtech.edu')
        match_count: Maximum number of results to return (default: 5)
    
    Returns:
        JSON string with degree program search results
    """
    try:
        # Get the Supabase client from the context
        supabase_client = get_supabase_from_context(ctx)
        
        # Enhance query for degree program search
        enhanced_query = f"degree program major emphasis {query} bachelor master"
        
        # Prepare source filter if provided
        source_filter = source_id.strip() if source_id and source_id.strip() else None
        
        # Check if hybrid search is enabled
        use_hybrid_search = os.getenv("USE_HYBRID_SEARCH", "false") == "true"
        
        if use_hybrid_search:
            # Hybrid search: combine vector and keyword search
            
            # 1. Get vector search results
            vector_results = search_documents(
                client=supabase_client,
                query=enhanced_query,
                match_count=match_count * 2,
                source_filter=source_filter
            )
            
            # 2. Get keyword search results using ILIKE
            keyword_query = supabase_client.from_('crawled_pages')\
                .select('id, url, chunk_number, content, metadata, source_id')\
                .ilike('content', f'%{query}%')
            
            # Apply source filter if provided
            if source_filter:
                keyword_query = keyword_query.eq('source_id', source_filter)
            
            # Execute keyword search
            keyword_response = keyword_query.limit(match_count * 2).execute()
            keyword_results = keyword_response.data if keyword_response.data else []
            
            # 3. Combine results with preference for items appearing in both
            seen_ids = set()
            combined_results = []
            
            # First, add items that appear in both searches (these are the best matches)
            vector_ids = {r.get('id') for r in vector_results if r.get('id')}
            for kr in keyword_results:
                if kr['id'] in vector_ids and kr['id'] not in seen_ids:
                    # Find the vector result to get similarity score
                    for vr in vector_results:
                        if vr.get('id') == kr['id']:
                            # Boost similarity score for items in both results
                            vr['similarity'] = min(1.0, vr.get('similarity', 0) * 1.2)
                            combined_results.append(vr)
                            seen_ids.add(kr['id'])
                            break
            
            # Then add remaining vector results (semantic matches without exact keyword)
            for vr in vector_results:
                if vr.get('id') and vr['id'] not in seen_ids and len(combined_results) < match_count:
                    combined_results.append(vr)
                    seen_ids.add(vr['id'])
            
            # Finally, add pure keyword matches if we still need more results
            for kr in keyword_results:
                if kr['id'] not in seen_ids and len(combined_results) < match_count:
                    # Convert keyword result to match vector result format
                    combined_results.append({
                        'id': kr['id'],
                        'url': kr['url'],
                        'chunk_number': kr['chunk_number'],
                        'content': kr['content'],
                        'metadata': kr['metadata'],
                        'source_id': kr['source_id'],
                        'similarity': 0.5  # Default similarity for keyword-only matches
                    })
                    seen_ids.add(kr['id'])
            
            # Use combined results
            results = combined_results[:match_count]
            
        else:
            # Standard vector search only
            results = search_documents(
                client=supabase_client,
                query=enhanced_query,
                match_count=match_count,
                source_filter=source_filter
            )
        
        # Apply reranking if enabled
        use_reranking = os.getenv("USE_RERANKING", "false") == "true"
        if use_reranking and ctx.request_context.lifespan_context.reranking_model:
            results = rerank_results(ctx.request_context.lifespan_context.reranking_model, query, results, content_key="content")
        
        # Format the results
        formatted_results = []
        for result in results:
            formatted_result = {
                "url": result.get("url"),
                "content": result.get("content"),
                "metadata": result.get("metadata"),
                "source_id": result.get("source_id"),
                "similarity": result.get("similarity")
            }
            # Include rerank score if available
            if "rerank_score" in result:
                formatted_result["rerank_score"] = result["rerank_score"]
            formatted_results.append(formatted_result)
        
        return json.dumps({
            "success": True,
            "query": query,
            "source_filter": source_id,
            "search_mode": "hybrid" if use_hybrid_search else "vector",
            "reranking_applied": use_reranking and ctx.request_context.lifespan_context.reranking_model is not None,
            "results": formatted_results,
            "count": len(formatted_results)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "query": query,
            "error": str(e)
        }, indent=2)

@mcp.tool()
async def search_courses(ctx: Context, query: str, level: str = None, department: str = None, source_id: str = None, match_count: int = 5) -> str:
    """
    Search for individual courses relevant to the query.
    
    This tool searches the academic catalog for specific courses that match the query.
    Useful for finding courses for IAP development, checking prerequisites, and academic planning.
    
    **Student Collaboration Context:**
    - **When to Use**: When building course lists for concentration areas or exploring options
    - **How to Introduce**: "Let's find courses that match your interests and degree goals"
    - **Student Involvement**: Discuss course descriptions and how they fit the student's plan
    - **Follow-up**: "Which of these courses excites you most? How do they connect to your other interests?"
    
    **Communication Tips:**
    - Help students understand course prerequisites and sequencing
    - Connect courses to their broader academic and career goals
    - Encourage exploration of courses outside their comfort zone
    
    Args:
        ctx: The MCP server provided context
        query: The search query (e.g., "statistics", "biology lab", "writing intensive")
        level: Optional level filter ("upper-division", "lower-division", "graduate")
        department: Optional department filter (e.g., "PSYC", "BIOL", "BUSN")
        source_id: Optional source ID to filter results (e.g., 'catalog.utahtech.edu')
        match_count: Maximum number of results to return (default: 5)
    
    Returns:
        JSON string with course search results
    """
    try:
        # Get the Supabase client from the context
        supabase_client = get_supabase_from_context(ctx)
        
        # Enhance query for course search
        enhanced_query = f"course {query} credit hours prerequisite"
        if level:
            enhanced_query += f" {level}"
        if department:
            enhanced_query += f" {department}"
        
        # Prepare source filter if provided
        source_filter = source_id.strip() if source_id and source_id.strip() else None
        
        # Check if hybrid search is enabled
        use_hybrid_search = os.getenv("USE_HYBRID_SEARCH", "false") == "true"
        
        if use_hybrid_search:
            # Hybrid search: combine vector and keyword search
            
            # 1. Get vector search results
            vector_results = search_documents(
                client=supabase_client,
                query=enhanced_query,
                match_count=match_count * 2,
                source_filter=source_filter
            )
            
            # 2. Get keyword search results using ILIKE
            keyword_query = supabase_client.from_('crawled_pages')\
                .select('id, url, chunk_number, content, metadata, source_id')\
                .ilike('content', f'%{query}%')
            
            # Apply filters
            if source_filter:
                keyword_query = keyword_query.eq('source_id', source_filter)
            if level:
                keyword_query = keyword_query.ilike('content', f'%{level}%')
            if department:
                keyword_query = keyword_query.ilike('content', f'%{department}%')
            
            # Execute keyword search
            keyword_response = keyword_query.limit(match_count * 2).execute()
            keyword_results = keyword_response.data if keyword_response.data else []
            
            # 3. Combine results with preference for items appearing in both
            seen_ids = set()
            combined_results = []
            
            # First, add items that appear in both searches (these are the best matches)
            vector_ids = {r.get('id') for r in vector_results if r.get('id')}
            for kr in keyword_results:
                if kr['id'] in vector_ids and kr['id'] not in seen_ids:
                    # Find the vector result to get similarity score
                    for vr in vector_results:
                        if vr.get('id') == kr['id']:
                            # Boost similarity score for items in both results
                            vr['similarity'] = min(1.0, vr.get('similarity', 0) * 1.2)
                            combined_results.append(vr)
                            seen_ids.add(kr['id'])
                            break
            
            # Then add remaining vector results (semantic matches without exact keyword)
            for vr in vector_results:
                if vr.get('id') and vr['id'] not in seen_ids and len(combined_results) < match_count:
                    combined_results.append(vr)
                    seen_ids.add(vr['id'])
            
            # Finally, add pure keyword matches if we still need more results
            for kr in keyword_results:
                if kr['id'] not in seen_ids and len(combined_results) < match_count:
                    # Convert keyword result to match vector result format
                    combined_results.append({
                        'id': kr['id'],
                        'url': kr['url'],
                        'chunk_number': kr['chunk_number'],
                        'content': kr['content'],
                        'metadata': kr['metadata'],
                        'source_id': kr['source_id'],
                        'similarity': 0.5  # Default similarity for keyword-only matches
                    })
                    seen_ids.add(kr['id'])
            
            # Use combined results
            results = combined_results[:match_count]
            
        else:
            # Standard vector search only
            results = search_documents(
                client=supabase_client,
                query=enhanced_query,
                match_count=match_count,
                source_filter=source_filter
            )
        
        # Apply reranking if enabled
        use_reranking = os.getenv("USE_RERANKING", "false") == "true"
        if use_reranking and ctx.request_context.lifespan_context.reranking_model:
            results = rerank_results(ctx.request_context.lifespan_context.reranking_model, query, results, content_key="content")
        
        # Format the results
        formatted_results = []
        for result in results:
            formatted_result = {
                "url": result.get("url"),
                "content": result.get("content"),
                "metadata": result.get("metadata"),
                "source_id": result.get("source_id"),
                "similarity": result.get("similarity")
            }
            # Include rerank score if available
            if "rerank_score" in result:
                formatted_result["rerank_score"] = result["rerank_score"]
            formatted_results.append(formatted_result)
        
        return json.dumps({
            "success": True,
            "query": query,
            "level_filter": level,
            "department_filter": department,
            "source_filter": source_id,
            "search_mode": "hybrid" if use_hybrid_search else "vector",
            "reranking_applied": use_reranking and ctx.request_context.lifespan_context.reranking_model is not None,
            "results": formatted_results,
            "count": len(formatted_results)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "query": query,
            "error": str(e)
        }, indent=2)

@mcp.tool()
async def validate_iap_requirements(ctx: Context, course_list: str, emphasis_title: str = None, source_id: str = None) -> str:
    """
    Validate if a course list meets IAP (Individualized Academic Plan) requirements.
    
    This tool checks course selections against Utah Tech's BIS degree requirements including:
    - 120 total credit hours
    - 40+ upper-division credits
    - 3+ discipline requirement
    - Statistical and written comprehension requirements
    - General education completion
    
    Args:
        ctx: The MCP server provided context
        course_list: Comma-separated list of course codes (e.g., "PSYC 1010, BIOL 3450, BUSN 4200")
        emphasis_title: Optional proposed degree emphasis title for validation
        source_id: Optional source ID to filter results (e.g., 'catalog.utahtech.edu')
    
    Returns:
        JSON string with validation results and recommendations
    """
    try:
        # Get the Supabase client from the context
        supabase_client = get_supabase_from_context(ctx)
        
        # Parse course list
        courses = [course.strip() for course in course_list.split(',') if course.strip()]
        
        # Prepare source filter if provided
        source_filter = source_id.strip() if source_id and source_id.strip() else None
        
        # Search for IAP requirements information
        requirements_query = "IAP individualized academic plan requirements 120 credits upper division three disciplines statistical comprehension"
        requirements_results = search_documents(
            client=supabase_client,
            query=requirements_query,
            match_count=3,
            source_filter=source_filter
        )
        
        # Search for information about each course
        course_info = []
        for course in courses:
            course_query = f"course {course} credit hours prerequisite upper division lower division"
            course_results = search_documents(
                client=supabase_client,
                query=course_query,
                match_count=2,
                source_filter=source_filter
            )
            course_info.append({
                "course_code": course,
                "search_results": course_results
            })
        
        # Check if emphasis title conflicts with existing programs
        existing_programs = []
        if emphasis_title:
            title_query = f"degree program major {emphasis_title} bachelor"
            title_results = search_documents(
                client=supabase_client,
                query=title_query,
                match_count=3,
                source_filter=source_filter
            )
            existing_programs = title_results
        
        # Format validation results
        validation_results = {
            "courses_analyzed": courses,
            "course_count": len(courses),
            "emphasis_title": emphasis_title,
            "requirements_info": requirements_results,
            "course_details": course_info,
            "title_conflicts": existing_programs,
            "validation_notes": [
                f"Found {len(courses)} courses to analyze",
                "Manual review needed for credit hour calculation",
                "Manual review needed for upper/lower division classification",
                "Manual review needed for discipline distribution"
            ]
        }
        
        return json.dumps({
            "success": True,
            "course_list": course_list,
            "emphasis_title": emphasis_title,
            "source_filter": source_id,
            "validation_results": validation_results
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "course_list": course_list,
            "error": str(e)
        }, indent=2)

@mcp.tool()
async def calculate_credits(ctx: Context, course_list: str, source_id: str = None) -> str:
    """
    Calculate total credit hours and classify upper/lower division courses.
    
    This tool analyzes a list of courses to extract credit hours, classify courses by level,
    and validate IAP requirements (120 total credits, 40+ upper-division credits).
    
    Args:
        ctx: The MCP server provided context
        course_list: Comma-separated list of course codes (e.g., "PSYC 1010, BIOL 3450, BUSN 4200")
        source_id: Optional source ID to filter results (e.g., 'catalog.utahtech.edu')
    
    Returns:
        JSON string with credit analysis and classification
    """
    try:
        # Get the Supabase client from the context
        supabase_client = get_supabase_from_context(ctx)
        
        # Parse course list
        courses = [course.strip() for course in course_list.split(',') if course.strip()]
        
        # Prepare source filter if provided
        source_filter = source_id.strip() if source_id and source_id.strip() else None
        
        # Analyze each course for credit information
        course_analysis = []
        total_credits = 0
        upper_division_credits = 0
        lower_division_credits = 0
        
        for course in courses:
            # Search for course credit information
            credit_query = f"course {course} credit hours credits units"
            credit_results = search_documents(
                client=supabase_client,
                query=credit_query,
                match_count=2,
                source_filter=source_filter
            )
            
            # Extract credit information from results
            credits_found = None
            course_level = "unknown"
            course_info = ""
            
            for result in credit_results:
                content = result.get("content", "")
                course_info = content[:200]  # Store snippet for reference
                
                # Extract credit hours using improved regex patterns
                import re
                
                # More specific patterns that look for credits in context
                credit_patterns = [
                    r'\((\d+)\s*credit\s*hours?\)',  # (3 credit hours)
                    r'\((\d+)\s*credits?\)',         # (4 credits)
                    r'(?:^|\s)(\d+)\s*credit\s*hours?(?:\s|$|\.|,)',
                    r'(?:^|\s)(\d+)\s*credits?(?:\s|$|\.|,)',
                    r'(?:^|\s)(\d+)\s*cr\.?(?:\s|$|\.|,)',
                    r'\((\d+)\s*units?\)',           # (3 units)
                    r'(?:^|\s)(\d+)\s*units?(?:\s|$|\.|,)',
                    r'(?:^|\s)(\d+)\s*hrs?(?:\s|$|\.|,)'
                ]
                
                for pattern in credit_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        try:
                            # Filter out unrealistic credit values (1-6 credits typical)
                            potential_credits = [int(m) for m in matches if 1 <= int(m) <= 6]
                            if potential_credits:
                                credits_found = potential_credits[0]  # Take first valid match
                                break
                        except ValueError:
                            continue
                
                if credits_found:
                    break
            
            # Determine course level from course number (improved pattern)
            course_number_match = re.search(r'(\d{3,4})', course)
            if course_number_match:
                course_number = int(course_number_match.group(1))
                if course_number >= 3000:
                    course_level = "upper-division"
                elif course_number >= 1000:
                    course_level = "lower-division"
                else:
                    course_level = "developmental"
            
            # Default to 3 credits if not found (common assumption)
            if credits_found is None:
                credits_found = 3
            
            # Add to totals
            total_credits += credits_found
            if course_level == "upper-division":
                upper_division_credits += credits_found
            elif course_level == "lower-division":
                lower_division_credits += credits_found
            
            course_analysis.append({
                "course_code": course,
                "credits": credits_found,
                "level": course_level,
                "course_info_snippet": course_info,
                "search_results_count": len(credit_results)
            })
        
        # Calculate requirements compliance
        meets_total_requirement = total_credits >= 120
        meets_upper_division_requirement = upper_division_credits >= 40
        
        # Generate recommendations
        recommendations = []
        if not meets_total_requirement:
            needed_credits = 120 - total_credits
            recommendations.append(f"Need {needed_credits} more credits to reach 120 total")
        
        if not meets_upper_division_requirement:
            needed_upper = 40 - upper_division_credits
            recommendations.append(f"Need {needed_upper} more upper-division credits (3000+ level)")
        
        if meets_total_requirement and meets_upper_division_requirement:
            recommendations.append("Credit requirements appear to be met!")
        
        return json.dumps({
            "success": True,
            "course_list": course_list,
            "source_filter": source_id,
            "analysis": {
                "total_courses": len(courses),
                "total_credits": total_credits,
                "upper_division_credits": upper_division_credits,
                "lower_division_credits": lower_division_credits,
                "meets_120_credit_requirement": meets_total_requirement,
                "meets_40_upper_division_requirement": meets_upper_division_requirement,
                "course_breakdown": course_analysis,
                "recommendations": recommendations
            }
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "course_list": course_list,
            "error": str(e)
        }, indent=2)

@mcp.tool()
async def check_prerequisites(ctx: Context, course_code: str, source_id: str = None) -> str:
    """
    Check prerequisite requirements for a specific course.
    
    This tool searches for prerequisite information for a given course and attempts to
    identify the prerequisite chain and requirements.
    
    **Student Collaboration Context:**
    - **When to Use**: When planning course sequences or checking if student is ready for a course
    - **How to Introduce**: "Let's check what prerequisites you'll need for this course"
    - **Student Involvement**: Review prerequisites together and plan the course sequence
    - **Follow-up**: "Based on these prerequisites, when do you think you could take this course?"
    
    **Communication Tips:**
    - Help students understand the logic behind prerequisite sequences
    - Identify alternative pathways when prerequisites seem challenging
    - Connect prerequisites to the student's overall academic timeline
    
    Args:
        ctx: The MCP server provided context
        course_code: Course code to check prerequisites for (e.g., "BIOL 3450")
        source_id: Optional source ID to filter results (e.g., 'catalog.utahtech.edu')
    
    Returns:
        JSON string with prerequisite information and chain
    """
    try:
        # Get the Supabase client from the context
        supabase_client = get_supabase_from_context(ctx)
        
        # Prepare source filter if provided
        source_filter = source_id.strip() if source_id and source_id.strip() else None
        
        # Search for prerequisite information
        prereq_query = f"course {course_code} prerequisite prerequisites required completion"
        prereq_results = search_documents(
            client=supabase_client,
            query=prereq_query,
            match_count=3,
            source_filter=source_filter
        )
        
        # Extract prerequisite information
        prerequisites_found = []
        course_description = ""
        
        import re
        for result in prereq_results:
            content = result.get("content", "")
            
            # Store course description from first result
            if not course_description and course_code.upper() in content.upper():
                course_description = content[:300]
            
            # Look for prerequisite patterns
            prereq_patterns = [
                r'prerequisite[s]?[:\s]+([^.]+)',
                r'required[:\s]+([^.]+)',
                r'completion of ([^.]+)',
                r'must complete ([^.]+)'
            ]
            
            for pattern in prereq_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Extract course codes from the match
                    course_codes = re.findall(r'[A-Z]{2,4}\s+\d{4}', match)
                    for code in course_codes:
                        if code not in prerequisites_found:
                            prerequisites_found.append(code)
        
        # Search for information about each prerequisite
        prerequisite_details = []
        for prereq in prerequisites_found:
            prereq_info_query = f"course {prereq} credit hours description"
            prereq_info_results = search_documents(
                client=supabase_client,
                query=prereq_info_query,
                match_count=1,
                source_filter=source_filter
            )
            
            prereq_info = ""
            if prereq_info_results:
                prereq_info = prereq_info_results[0].get("content", "")[:200]
            
            prerequisite_details.append({
                "course_code": prereq,
                "description_snippet": prereq_info
            })
        
        # Generate analysis
        has_prerequisites = len(prerequisites_found) > 0
        complexity_level = "low" if len(prerequisites_found) <= 1 else "medium" if len(prerequisites_found) <= 3 else "high"
        
        return json.dumps({
            "success": True,
            "course_code": course_code,
            "source_filter": source_id,
            "analysis": {
                "has_prerequisites": has_prerequisites,
                "prerequisite_count": len(prerequisites_found),
                "complexity_level": complexity_level,
                "prerequisites_found": prerequisites_found,
                "prerequisite_details": prerequisite_details,
                "course_description_snippet": course_description,
                "search_results_count": len(prereq_results)
            }
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "course_code": course_code,
            "error": str(e)
        }, indent=2)

@mcp.tool()
async def analyze_disciplines(ctx: Context, course_list: str, source_id: str = None) -> str:
    """
    Analyze discipline distribution across a list of courses.
    
    This tool groups courses by academic discipline and validates the IAP requirement
    of having courses from 3+ different disciplines.
    
    Args:
        ctx: The MCP server provided context
        course_list: Comma-separated list of course codes (e.g., "PSYC 1010, BIOL 3450, BUSN 4200")
        source_id: Optional source ID to filter results (e.g., 'catalog.utahtech.edu')
    
    Returns:
        JSON string with discipline analysis and distribution
    """
    try:
        # Get the Supabase client from the context
        supabase_client = get_supabase_from_context(ctx)
        
        # Parse course list
        courses = [course.strip() for course in course_list.split(',') if course.strip()]
        
        # Prepare source filter if provided
        source_filter = source_id.strip() if source_id and source_id.strip() else None
        
        # Extract discipline prefixes and group courses
        import re
        discipline_groups = {}
        course_details = []
        
        for course in courses:
            # Extract discipline prefix (e.g., "PSYC" from "PSYC 1010")
            prefix_match = re.match(r'^([A-Z]{2,4})', course.strip())
            discipline_prefix = prefix_match.group(1) if prefix_match else "UNKNOWN"
            
            # Search for department/discipline information
            discipline_query = f"department {discipline_prefix} {course} major program"
            discipline_results = search_documents(
                client=supabase_client,
                query=discipline_query,
                match_count=2,
                source_filter=source_filter
            )
            
            # Extract discipline name from results
            discipline_name = discipline_prefix  # Default to prefix
            department_info = ""
            
            for result in discipline_results:
                content = result.get("content", "")
                department_info = content[:200]  # Store snippet
                
                # Try to extract full department name
                dept_patterns = [
                    rf'{discipline_prefix}[^a-zA-Z]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                    r'Department of ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Department'
                ]
                
                for pattern in dept_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        discipline_name = matches[0]
                        break
                
                if discipline_name != discipline_prefix:
                    break
            
            # Group by discipline
            if discipline_prefix not in discipline_groups:
                discipline_groups[discipline_prefix] = {
                    "discipline_name": discipline_name,
                    "courses": [],
                    "course_count": 0
                }
            
            discipline_groups[discipline_prefix]["courses"].append(course)
            discipline_groups[discipline_prefix]["course_count"] += 1
            
            course_details.append({
                "course_code": course,
                "discipline_prefix": discipline_prefix,
                "discipline_name": discipline_name,
                "department_info_snippet": department_info
            })
        
        # Calculate discipline distribution
        total_disciplines = len(discipline_groups)
        meets_three_discipline_requirement = total_disciplines >= 3
        
        # Generate recommendations
        recommendations = []
        if not meets_three_discipline_requirement:
            needed_disciplines = 3 - total_disciplines
            recommendations.append(f"Need courses from {needed_disciplines} more discipline(s) to meet 3+ discipline requirement")
            recommendations.append("Consider adding courses from different departments (e.g., MATH, ENGL, HIST, etc.)")
        else:
            recommendations.append("Three or more disciplines requirement is met!")
        
        # Sort disciplines by course count for better presentation
        sorted_disciplines = dict(sorted(discipline_groups.items(), key=lambda x: x[1]["course_count"], reverse=True))
        
        return json.dumps({
            "success": True,
            "course_list": course_list,
            "source_filter": source_id,
            "analysis": {
                "total_courses": len(courses),
                "total_disciplines": total_disciplines,
                "meets_three_discipline_requirement": meets_three_discipline_requirement,
                "discipline_distribution": sorted_disciplines,
                "course_details": course_details,
                "recommendations": recommendations
            }
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "course_list": course_list,
            "error": str(e)
        }, indent=2)

@mcp.tool()
async def check_ai_script_hallucinations(ctx: Context, script_path: str) -> str:
    """
    Check an AI-generated Python script for hallucinations using the knowledge graph.
    
    This tool analyzes a Python script for potential AI hallucinations by validating
    imports, method calls, class instantiations, and function calls against a Neo4j
    knowledge graph containing real repository data.
    
    The tool performs comprehensive analysis including:
    - Import validation against known repositories
    - Method call validation on classes from the knowledge graph
    - Class instantiation parameter validation
    - Function call parameter validation
    - Attribute access validation
    
    Args:
        ctx: The MCP server provided context
        script_path: Absolute path to the Python script to analyze
    
    Returns:
        JSON string with hallucination detection results, confidence scores, and recommendations
    """
    try:
        # Check if knowledge graph functionality is enabled
        knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"
        if not knowledge_graph_enabled:
            return json.dumps({
                "success": False,
                "error": "Knowledge graph functionality is disabled. Set USE_KNOWLEDGE_GRAPH=true in environment."
            }, indent=2)
        
        # Get the knowledge validator from context
        knowledge_validator = ctx.request_context.lifespan_context.knowledge_validator
        
        if not knowledge_validator:
            return json.dumps({
                "success": False,
                "error": "Knowledge graph validator not available. Check Neo4j configuration in environment variables."
            }, indent=2)
        
        # Validate script path
        validation = validate_script_path(script_path)
        if not validation["valid"]:
            return json.dumps({
                "success": False,
                "script_path": script_path,
                "error": validation["error"]
            }, indent=2)
        
        # Step 1: Analyze script structure using AST
        analyzer = AIScriptAnalyzer()
        analysis_result = analyzer.analyze_script(script_path)
        
        if analysis_result.errors:
            print(f"Analysis warnings for {script_path}: {analysis_result.errors}")
        
        # Step 2: Validate against knowledge graph
        validation_result = await knowledge_validator.validate_script(analysis_result)
        
        # Step 3: Generate comprehensive report
        reporter = HallucinationReporter()
        report = reporter.generate_comprehensive_report(validation_result)
        
        # Format response with comprehensive information
        return json.dumps({
            "success": True,
            "script_path": script_path,
            "overall_confidence": validation_result.overall_confidence,
            "validation_summary": {
                "total_validations": report["validation_summary"]["total_validations"],
                "valid_count": report["validation_summary"]["valid_count"],
                "invalid_count": report["validation_summary"]["invalid_count"],
                "uncertain_count": report["validation_summary"]["uncertain_count"],
                "not_found_count": report["validation_summary"]["not_found_count"],
                "hallucination_rate": report["validation_summary"]["hallucination_rate"]
            },
            "hallucinations_detected": report["hallucinations_detected"],
            "recommendations": report["recommendations"],
            "analysis_metadata": {
                "total_imports": report["analysis_metadata"]["total_imports"],
                "total_classes": report["analysis_metadata"]["total_classes"],
                "total_methods": report["analysis_metadata"]["total_methods"],
                "total_attributes": report["analysis_metadata"]["total_attributes"],
                "total_functions": report["analysis_metadata"]["total_functions"]
            },
            "libraries_analyzed": report.get("libraries_analyzed", [])
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "script_path": script_path,
            "error": f"Analysis failed: {str(e)}"
        }, indent=2)

@mcp.tool()
async def query_knowledge_graph(ctx: Context, command: str) -> str:
    """
    Query and explore the Neo4j knowledge graph containing repository data.
    
    This tool provides comprehensive access to the knowledge graph for exploring repositories,
    classes, methods, functions, and their relationships. Perfect for understanding what data
    is available for hallucination detection and debugging validation results.
    
    **⚠️ IMPORTANT: Always start with the `repos` command first!**
    Before using any other commands, run `repos` to see what repositories are available
    in your knowledge graph. This will help you understand what data you can explore.
    
    ## Available Commands:
    
    **Repository Commands:**
    - `repos` - **START HERE!** List all repositories in the knowledge graph
    - `explore <repo_name>` - Get detailed overview of a specific repository
    
    **Class Commands:**  
    - `classes` - List all classes across all repositories (limited to 20)
    - `classes <repo_name>` - List classes in a specific repository
    - `class <class_name>` - Get detailed information about a specific class including methods and attributes
    
    **Method Commands:**
    - `method <method_name>` - Search for methods by name across all classes
    - `method <method_name> <class_name>` - Search for a method within a specific class
    
    **Custom Query:**
    - `query <cypher_query>` - Execute a custom Cypher query (results limited to 20 records)
    
    ## Knowledge Graph Schema:
    
    **Node Types:**
    - Repository: `(r:Repository {name: string})`
    - File: `(f:File {path: string, module_name: string})`
    - Class: `(c:Class {name: string, full_name: string})`
    - Method: `(m:Method {name: string, params_list: [string], params_detailed: [string], return_type: string, args: [string]})`
    - Function: `(func:Function {name: string, params_list: [string], params_detailed: [string], return_type: string, args: [string]})`
    - Attribute: `(a:Attribute {name: string, type: string})`
    
    **Relationships:**
    - `(r:Repository)-[:CONTAINS]->(f:File)`
    - `(f:File)-[:DEFINES]->(c:Class)`
    - `(c:Class)-[:HAS_METHOD]->(m:Method)`
    - `(c:Class)-[:HAS_ATTRIBUTE]->(a:Attribute)`
    - `(f:File)-[:DEFINES]->(func:Function)`
    
    ## Example Workflow:
    ```
    1. repos                                    # See what repositories are available
    2. explore pydantic-ai                      # Explore a specific repository
    3. classes pydantic-ai                      # List classes in that repository
    4. class Agent                              # Explore the Agent class
    5. method run_stream                        # Search for run_stream method
    6. method __init__ Agent                    # Find Agent constructor
    7. query "MATCH (c:Class)-[:HAS_METHOD]->(m:Method) WHERE m.name = 'run' RETURN c.name, m.name LIMIT 5"
    ```
    
    Args:
        ctx: The MCP server provided context
        command: Command string to execute (see available commands above)
    
    Returns:
        JSON string with query results, statistics, and metadata
    """
    try:
        # Check if knowledge graph functionality is enabled
        knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"
        if not knowledge_graph_enabled:
            return json.dumps({
                "success": False,
                "error": "Knowledge graph functionality is disabled. Set USE_KNOWLEDGE_GRAPH=true in environment."
            }, indent=2)
        
        # Get Neo4j driver from context
        repo_extractor = ctx.request_context.lifespan_context.repo_extractor
        if not repo_extractor or not repo_extractor.driver:
            return json.dumps({
                "success": False,
                "error": "Neo4j connection not available. Check Neo4j configuration in environment variables."
            }, indent=2)
        
        # Parse command
        command = command.strip()
        if not command:
            return json.dumps({
                "success": False,
                "command": "",
                "error": "Command cannot be empty. Available commands: repos, explore <repo>, classes [repo], class <name>, method <name> [class], query <cypher>"
            }, indent=2)
        
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        async with repo_extractor.driver.session() as session:
            # Route to appropriate handler
            if cmd == "repos":
                return await _handle_repos_command(session, command)
            elif cmd == "explore":
                if not args:
                    return json.dumps({
                        "success": False,
                        "command": command,
                        "error": "Repository name required. Usage: explore <repo_name>"
                    }, indent=2)
                return await _handle_explore_command(session, command, args[0])
            elif cmd == "classes":
                repo_name = args[0] if args else None
                return await _handle_classes_command(session, command, repo_name)
            elif cmd == "class":
                if not args:
                    return json.dumps({
                        "success": False,
                        "command": command,
                        "error": "Class name required. Usage: class <class_name>"
                    }, indent=2)
                return await _handle_class_command(session, command, args[0])
            elif cmd == "method":
                if not args:
                    return json.dumps({
                        "success": False,
                        "command": command,
                        "error": "Method name required. Usage: method <method_name> [class_name]"
                    }, indent=2)
                method_name = args[0]
                class_name = args[1] if len(args) > 1 else None
                return await _handle_method_command(session, command, method_name, class_name)
            elif cmd == "query":
                if not args:
                    return json.dumps({
                        "success": False,
                        "command": command,
                        "error": "Cypher query required. Usage: query <cypher_query>"
                    }, indent=2)
                cypher_query = " ".join(args)
                return await _handle_query_command(session, command, cypher_query)
            else:
                return json.dumps({
                    "success": False,
                    "command": command,
                    "error": f"Unknown command '{cmd}'. Available commands: repos, explore <repo>, classes [repo], class <name>, method <name> [class], query <cypher>"
                }, indent=2)
                
    except Exception as e:
        return json.dumps({
            "success": False,
            "command": command,
            "error": f"Query execution failed: {str(e)}"
        }, indent=2)


async def _handle_repos_command(session, command: str) -> str:
    """Handle 'repos' command - list all repositories"""
    query = "MATCH (r:Repository) RETURN r.name as name ORDER BY r.name"
    result = await session.run(query)
    
    repos = []
    async for record in result:
        repos.append(record['name'])
    
    return json.dumps({
        "success": True,
        "command": command,
        "data": {
            "repositories": repos
        },
        "metadata": {
            "total_results": len(repos),
            "limited": False
        }
    }, indent=2)


async def _handle_explore_command(session, command: str, repo_name: str) -> str:
    """Handle 'explore <repo>' command - get repository overview"""
    # Check if repository exists
    repo_check_query = "MATCH (r:Repository {name: $repo_name}) RETURN r.name as name"
    result = await session.run(repo_check_query, repo_name=repo_name)
    repo_record = await result.single()
    
    if not repo_record:
        return json.dumps({
            "success": False,
            "command": command,
            "error": f"Repository '{repo_name}' not found in knowledge graph"
        }, indent=2)
    
    # Get file count
    files_query = """
    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)
    RETURN count(f) as file_count
    """
    result = await session.run(files_query, repo_name=repo_name)
    file_count = (await result.single())['file_count']
    
    # Get class count
    classes_query = """
    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)
    RETURN count(DISTINCT c) as class_count
    """
    result = await session.run(classes_query, repo_name=repo_name)
    class_count = (await result.single())['class_count']
    
    # Get function count
    functions_query = """
    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(func:Function)
    RETURN count(DISTINCT func) as function_count
    """
    result = await session.run(functions_query, repo_name=repo_name)
    function_count = (await result.single())['function_count']
    
    # Get method count
    methods_query = """
    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)-[:HAS_METHOD]->(m:Method)
    RETURN count(DISTINCT m) as method_count
    """
    result = await session.run(methods_query, repo_name=repo_name)
    method_count = (await result.single())['method_count']
    
    return json.dumps({
        "success": True,
        "command": command,
        "data": {
            "repository": repo_name,
            "statistics": {
                "files": file_count,
                "classes": class_count,
                "functions": function_count,
                "methods": method_count
            }
        },
        "metadata": {
            "total_results": 1,
            "limited": False
        }
    }, indent=2)


async def _handle_classes_command(session, command: str, repo_name: str = None) -> str:
    """Handle 'classes [repo]' command - list classes"""
    limit = 20
    
    if repo_name:
        query = """
        MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)
        RETURN c.name as name, c.full_name as full_name
        ORDER BY c.name
        LIMIT $limit
        """
        result = await session.run(query, repo_name=repo_name, limit=limit)
    else:
        query = """
        MATCH (c:Class)
        RETURN c.name as name, c.full_name as full_name
        ORDER BY c.name
        LIMIT $limit
        """
        result = await session.run(query, limit=limit)
    
    classes = []
    async for record in result:
        classes.append({
            'name': record['name'],
            'full_name': record['full_name']
        })
    
    return json.dumps({
        "success": True,
        "command": command,
        "data": {
            "classes": classes,
            "repository_filter": repo_name
        },
        "metadata": {
            "total_results": len(classes),
            "limited": len(classes) >= limit
        }
    }, indent=2)


async def _handle_class_command(session, command: str, class_name: str) -> str:
    """Handle 'class <name>' command - explore specific class"""
    # Find the class
    class_query = """
    MATCH (c:Class)
    WHERE c.name = $class_name OR c.full_name = $class_name
    RETURN c.name as name, c.full_name as full_name
    LIMIT 1
    """
    result = await session.run(class_query, class_name=class_name)
    class_record = await result.single()
    
    if not class_record:
        return json.dumps({
            "success": False,
            "command": command,
            "error": f"Class '{class_name}' not found in knowledge graph"
        }, indent=2)
    
    actual_name = class_record['name']
    full_name = class_record['full_name']
    
    # Get methods
    methods_query = """
    MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
    WHERE c.name = $class_name OR c.full_name = $class_name
    RETURN m.name as name, m.params_list as params_list, m.params_detailed as params_detailed, m.return_type as return_type
    ORDER BY m.name
    """
    result = await session.run(methods_query, class_name=class_name)
    
    methods = []
    async for record in result:
        # Use detailed params if available, fall back to simple params
        params_to_use = record['params_detailed'] or record['params_list'] or []
        methods.append({
            'name': record['name'],
            'parameters': params_to_use,
            'return_type': record['return_type'] or 'Any'
        })
    
    # Get attributes
    attributes_query = """
    MATCH (c:Class)-[:HAS_ATTRIBUTE]->(a:Attribute)
    WHERE c.name = $class_name OR c.full_name = $class_name
    RETURN a.name as name, a.type as type
    ORDER BY a.name
    """
    result = await session.run(attributes_query, class_name=class_name)
    
    attributes = []
    async for record in result:
        attributes.append({
            'name': record['name'],
            'type': record['type'] or 'Any'
        })
    
    return json.dumps({
        "success": True,
        "command": command,
        "data": {
            "class": {
                "name": actual_name,
                "full_name": full_name,
                "methods": methods,
                "attributes": attributes
            }
        },
        "metadata": {
            "total_results": 1,
            "methods_count": len(methods),
            "attributes_count": len(attributes),
            "limited": False
        }
    }, indent=2)


async def _handle_method_command(session, command: str, method_name: str, class_name: str = None) -> str:
    """Handle 'method <name> [class]' command - search for methods"""
    if class_name:
        query = """
        MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
        WHERE (c.name = $class_name OR c.full_name = $class_name)
          AND m.name = $method_name
        RETURN c.name as class_name, c.full_name as class_full_name,
               m.name as method_name, m.params_list as params_list, 
               m.params_detailed as params_detailed, m.return_type as return_type, m.args as args
        """
        result = await session.run(query, class_name=class_name, method_name=method_name)
    else:
        query = """
        MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
        WHERE m.name = $method_name
        RETURN c.name as class_name, c.full_name as class_full_name,
               m.name as method_name, m.params_list as params_list, 
               m.params_detailed as params_detailed, m.return_type as return_type, m.args as args
        ORDER BY c.name
        LIMIT 20
        """
        result = await session.run(query, method_name=method_name)
    
    methods = []
    async for record in result:
        # Use detailed params if available, fall back to simple params
        params_to_use = record['params_detailed'] or record['params_list'] or []
        methods.append({
            'class_name': record['class_name'],
            'class_full_name': record['class_full_name'],
            'method_name': record['method_name'],
            'parameters': params_to_use,
            'return_type': record['return_type'] or 'Any',
            'legacy_args': record['args'] or []
        })
    
    if not methods:
        return json.dumps({
            "success": False,
            "command": command,
            "error": f"Method '{method_name}'" + (f" in class '{class_name}'" if class_name else "") + " not found"
        }, indent=2)
    
    return json.dumps({
        "success": True,
        "command": command,
        "data": {
            "methods": methods,
            "class_filter": class_name
        },
        "metadata": {
            "total_results": len(methods),
            "limited": len(methods) >= 20 and not class_name
        }
    }, indent=2)


async def _handle_query_command(session, command: str, cypher_query: str) -> str:
    """Handle 'query <cypher>' command - execute custom Cypher query"""
    try:
        # Execute the query with a limit to prevent overwhelming responses
        result = await session.run(cypher_query)
        
        records = []
        count = 0
        async for record in result:
            records.append(dict(record))
            count += 1
            if count >= 20:  # Limit results to prevent overwhelming responses
                break
        
        return json.dumps({
            "success": True,
            "command": command,
            "data": {
                "query": cypher_query,
                "results": records
            },
            "metadata": {
                "total_results": len(records),
                "limited": len(records) >= 20
            }
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "command": command,
            "error": f"Cypher query error: {str(e)}",
            "data": {
                "query": cypher_query
            }
        }, indent=2)


@mcp.tool()
async def parse_github_repository(ctx: Context, repo_url: str) -> str:
    """
    Parse a GitHub repository into the Neo4j knowledge graph.
    
    This tool clones a GitHub repository, analyzes its Python files, and stores
    the code structure (classes, methods, functions, imports) in Neo4j for use
    in hallucination detection. The tool:
    
    - Clones the repository to a temporary location
    - Analyzes Python files to extract code structure
    - Stores classes, methods, functions, and imports in Neo4j
    - Provides detailed statistics about the parsing results
    - Automatically handles module name detection for imports
    
    Args:
        ctx: The MCP server provided context
        repo_url: GitHub repository URL (e.g., 'https://github.com/user/repo.git')
    
    Returns:
        JSON string with parsing results, statistics, and repository information
    """
    try:
        # Check if knowledge graph functionality is enabled
        knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"
        if not knowledge_graph_enabled:
            return json.dumps({
                "success": False,
                "error": "Knowledge graph functionality is disabled. Set USE_KNOWLEDGE_GRAPH=true in environment."
            }, indent=2)
        
        # Get the repository extractor from context
        repo_extractor = ctx.request_context.lifespan_context.repo_extractor
        
        if not repo_extractor:
            return json.dumps({
                "success": False,
                "error": "Repository extractor not available. Check Neo4j configuration in environment variables."
            }, indent=2)
        
        # Validate repository URL
        validation = validate_github_url(repo_url)
        if not validation["valid"]:
            return json.dumps({
                "success": False,
                "repo_url": repo_url,
                "error": validation["error"]
            }, indent=2)
        
        repo_name = validation["repo_name"]
        
        # Parse the repository (this includes cloning, analysis, and Neo4j storage)
        print(f"Starting repository analysis for: {repo_name}")
        await repo_extractor.analyze_repository(repo_url)
        print(f"Repository analysis completed for: {repo_name}")
        
        # Query Neo4j for statistics about the parsed repository
        async with repo_extractor.driver.session() as session:
            # Get comprehensive repository statistics
            stats_query = """
            MATCH (r:Repository {name: $repo_name})
            OPTIONAL MATCH (r)-[:CONTAINS]->(f:File)
            OPTIONAL MATCH (f)-[:DEFINES]->(c:Class)
            OPTIONAL MATCH (c)-[:HAS_METHOD]->(m:Method)
            OPTIONAL MATCH (f)-[:DEFINES]->(func:Function)
            OPTIONAL MATCH (c)-[:HAS_ATTRIBUTE]->(a:Attribute)
            WITH r, 
                 count(DISTINCT f) as files_count,
                 count(DISTINCT c) as classes_count,
                 count(DISTINCT m) as methods_count,
                 count(DISTINCT func) as functions_count,
                 count(DISTINCT a) as attributes_count
            
            // Get some sample module names
            OPTIONAL MATCH (r)-[:CONTAINS]->(sample_f:File)
            WITH r, files_count, classes_count, methods_count, functions_count, attributes_count,
                 collect(DISTINCT sample_f.module_name)[0..5] as sample_modules
            
            RETURN 
                r.name as repo_name,
                files_count,
                classes_count, 
                methods_count,
                functions_count,
                attributes_count,
                sample_modules
            """
            
            result = await session.run(stats_query, repo_name=repo_name)
            record = await result.single()
            
            if record:
                stats = {
                    "repository": record['repo_name'],
                    "files_processed": record['files_count'],
                    "classes_created": record['classes_count'],
                    "methods_created": record['methods_count'], 
                    "functions_created": record['functions_count'],
                    "attributes_created": record['attributes_count'],
                    "sample_modules": record['sample_modules'] or []
                }
            else:
                return json.dumps({
                    "success": False,
                    "repo_url": repo_url,
                    "error": f"Repository '{repo_name}' not found in database after parsing"
                }, indent=2)
        
        return json.dumps({
            "success": True,
            "repo_url": repo_url,
            "repo_name": repo_name,
            "message": f"Successfully parsed repository '{repo_name}' into knowledge graph",
            "statistics": stats,
            "ready_for_validation": True,
            "next_steps": [
                "Repository is now available for hallucination detection",
                f"Use check_ai_script_hallucinations to validate scripts against {repo_name}",
                "The knowledge graph contains classes, methods, and functions from this repository"
            ]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "repo_url": repo_url,
            "error": f"Repository parsing failed: {str(e)}"
        }, indent=2)

async def crawl_markdown_file(crawler: AsyncWebCrawler, url: str) -> List[Dict[str, Any]]:
    """
    Crawl a .txt or markdown file.
    
    Args:
        crawler: AsyncWebCrawler instance
        url: URL of the file
        
    Returns:
        List of dictionaries with URL and markdown content
    """
    crawl_config = CrawlerRunConfig()

    result = await crawler.arun(url=url, config=crawl_config)
    if result.success and result.markdown:
        return [{'url': url, 'markdown': result.markdown}]
    else:
        print(f"Failed to crawl {url}: {result.error_message}")
        return []

async def crawl_batch(crawler: AsyncWebCrawler, urls: List[str], max_concurrent: int = 10) -> List[Dict[str, Any]]:
    """
    Batch crawl multiple URLs in parallel.
    
    Args:
        crawler: AsyncWebCrawler instance
        urls: List of URLs to crawl
        max_concurrent: Maximum number of concurrent browser sessions
        
    Returns:
        List of dictionaries with URL and markdown content
    """
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=max_concurrent
    )

    results = await crawler.arun_many(urls=urls, config=crawl_config, dispatcher=dispatcher)
    return [{'url': r.url, 'markdown': r.markdown} for r in results if r.success and r.markdown]

async def crawl_recursive_internal_links(crawler: AsyncWebCrawler, start_urls: List[str], max_depth: int = 3, max_concurrent: int = 10) -> List[Dict[str, Any]]:
    """
    Recursively crawl internal links from start URLs up to a maximum depth.
    
    Args:
        crawler: AsyncWebCrawler instance
        start_urls: List of starting URLs
        max_depth: Maximum recursion depth
        max_concurrent: Maximum number of concurrent browser sessions
        
    Returns:
        List of dictionaries with URL and markdown content
    """
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=max_concurrent
    )

    visited = set()

    def normalize_url(url):
        return urldefrag(url)[0]

    current_urls = set([normalize_url(u) for u in start_urls])
    results_all = []

    for depth in range(max_depth):
        urls_to_crawl = [normalize_url(url) for url in current_urls if normalize_url(url) not in visited]
        if not urls_to_crawl:
            break

        results = await crawler.arun_many(urls=urls_to_crawl, config=run_config, dispatcher=dispatcher)
        next_level_urls = set()

        for result in results:
            norm_url = normalize_url(result.url)
            visited.add(norm_url)

            if result.success and result.markdown:
                results_all.append({'url': result.url, 'markdown': result.markdown})
                for link in result.links.get("internal", []):
                    next_url = normalize_url(link["href"])
                    if next_url not in visited:
                        next_level_urls.add(next_url)

        current_urls = next_level_urls

    return results_all

@mcp.tool()
async def build_academic_knowledge_graph(ctx: Context) -> str:
    """
    Build and populate the academic knowledge graph from crawled content.
    
    This tool extracts academic entities (courses, programs, departments, prerequisites)
    from the crawled Utah Tech catalog content and populates a Neo4j knowledge graph
    to enable advanced academic planning and relationship queries.
    
    The tool performs:
    - Schema creation with constraints and indexes
    - Academic data extraction from crawled content
    - Entity creation (University, Departments, Courses, Programs)
    - Relationship mapping (prerequisites, program requirements, etc.)
    
    Args:
        ctx: The MCP server provided context
    
    Returns:
        JSON string with graph building results and statistics
    """
    try:
        print("🏗️ Building Academic Knowledge Graph...")
        
        # Initialize the academic graph builder
        builder = AcademicGraphBuilder()
        
        try:
            # Build the complete academic graph
            academic_data = await builder.build_academic_graph()
            
            # Generate summary statistics
            stats = {
                "departments": len(academic_data.get("departments", {})),
                "courses": len(academic_data.get("courses", {})),
                "programs": len(academic_data.get("programs", {})),
            }
            
            # Count prerequisite relationships
            prereq_count = sum(
                len(course.prerequisites) 
                for course in academic_data.get("courses", {}).values()
            )
            
            # Sample entities for verification
            sample_courses = list(academic_data.get("courses", {}).keys())[:5]
            sample_programs = list(academic_data.get("programs", {}).keys())[:3]
            sample_departments = list(academic_data.get("departments", {}).keys())[:3]
            
            result = {
                "success": True,
                "message": "Academic knowledge graph built successfully",
                "statistics": {
                    "total_departments": stats["departments"],
                    "total_courses": stats["courses"],
                    "total_programs": stats["programs"],
                    "prerequisite_relationships": prereq_count,
                    "graph_populated": True
                },
                "samples": {
                    "courses": sample_courses,
                    "programs": sample_programs,
                    "departments": sample_departments
                },
                "capabilities_enabled": [
                    "Graph-based prerequisite chain analysis",
                    "Cross-disciplinary course discovery",
                    "Program requirement validation",
                    "Academic pathway planning",
                    "Relationship-based course recommendations"
                ],
                "next_steps": [
                    "Use query_knowledge_graph tool to explore academic entities",
                    "Test graph-enhanced academic planning queries",
                    "Validate prerequisite chains and program requirements"
                ]
            }
            
        finally:
            # Always close the builder connection
            builder.close()
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Failed to build academic knowledge graph",
            "troubleshooting": [
                "Check Neo4j connection (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)",
                "Ensure crawled academic content exists in Supabase",
                "Verify academic content parsing patterns",
                "Check for sufficient academic data in catalog.utahtech.edu source"
            ]
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def populate_supabase_backup(ctx: Context, clear_existing: bool = False, batch_size: int = 100, dry_run: bool = False) -> str:
    """
    Backup tool to populate Supabase academic tables directly from crawled content.
    
    This tool serves as a reliable fallback when the main build_academic_knowledge_graph
    tool encounters issues. It extracts academic data from crawled content and populates
    Supabase tables with intelligent duplicate handling and batch processing.
    
    Key Features:
    - Intelligent duplicate handling with UPSERT logic
    - Batch processing for performance
    - Data truncation for database constraints
    - Comprehensive error handling and recovery
    - Detailed statistics and progress reporting
    
    Args:
        ctx: The MCP server provided context
        clear_existing: Whether to clear existing data before population (default: False)
        batch_size: Number of records per batch (default: 100)
        dry_run: Show what would be inserted without actually inserting (default: False)
    
    Returns:
        JSON string with population results and statistics
    """
    try:
        print("🔄 Starting Supabase Backup Population...")
        
        # Initialize stats
        stats = {
            'departments_processed': 0,
            'courses_processed': 0,
            'programs_processed': 0,
            'departments_inserted': 0,
            'courses_inserted': 0,
            'programs_inserted': 0,
            'duplicates_skipped': 0,
            'errors': []
        }
        
        # Get Supabase client from context
        supabase = ctx.request_context.lifespan_context.supabase_client
        
        # Clear existing data if requested
        if clear_existing and not dry_run:
            print("🗑️ Clearing existing academic data...")
            try:
                supabase.table('academic_programs').delete().neq('id', 0).execute()
                supabase.table('academic_courses').delete().neq('id', 0).execute()
                supabase.table('academic_departments').delete().neq('id', 0).execute()
                print("✅ Existing data cleared")
            except Exception as e:
                print(f"⚠️ Warning: Could not clear existing data: {e}")
        
        # Initialize the academic graph builder to extract data
        builder = AcademicGraphBuilder()
        
        try:
            # Extract academic data from crawled content
            print("📊 Extracting academic data from crawled content...")
            academic_data = await builder._extract_academic_data()
            
            if not academic_data:
                return json.dumps({
                    "success": False,
                    "error": "No academic data found in crawled content",
                    "message": "Please ensure Utah Tech catalog content has been crawled first"
                })
            
            # Track existing records to avoid duplicates
            existing_departments = set()
            existing_courses = set()
            existing_programs = set()
            
            if not clear_existing:
                # Get existing records
                try:
                    dept_result = supabase.table('academic_departments').select('prefix').execute()
                    existing_departments = {row['prefix'] for row in dept_result.data}
                    
                    course_result = supabase.table('academic_courses').select('course_code').execute()
                    existing_courses = {row['course_code'] for row in course_result.data}
                    
                    program_result = supabase.table('academic_programs').select('program_code').execute()
                    existing_programs = {row['program_code'] for row in program_result.data}
                except Exception as e:
                    print(f"⚠️ Warning: Could not fetch existing records: {e}")
            
            # Process departments
            departments_to_insert = []
            for dept_prefix, dept_data in academic_data.get('departments', {}).items():
                stats['departments_processed'] += 1
                
                if dept_prefix in existing_departments:
                    stats['duplicates_skipped'] += 1
                    continue
                
                # Truncate name if too long for database constraint
                dept_name = dept_data.name[:100] if len(dept_data.name) > 100 else dept_data.name
                
                dept_record = {
                    'prefix': dept_prefix,
                    'name': dept_name,
                    'description': dept_data.description[:500] if dept_data.description else None
                }
                departments_to_insert.append(dept_record)
                
                if len(departments_to_insert) >= batch_size:
                    if not dry_run:
                        result = supabase.table('academic_departments').upsert(departments_to_insert).execute()
                        stats['departments_inserted'] += len(departments_to_insert)
                    departments_to_insert = []
            
            # Insert remaining departments
            if departments_to_insert and not dry_run:
                result = supabase.table('academic_departments').upsert(departments_to_insert).execute()
                stats['departments_inserted'] += len(departments_to_insert)
            elif dry_run:
                stats['departments_inserted'] = len(departments_to_insert)
            
            # Process courses
            courses_to_insert = []
            for course_code, course_data in academic_data.get('courses', {}).items():
                stats['courses_processed'] += 1
                
                if course_code in existing_courses:
                    stats['duplicates_skipped'] += 1
                    continue
                
                # Extract department prefix
                dept_prefix = course_code.split()[0] if ' ' in course_code else course_code[:4]
                
                course_record = {
                    'course_code': course_code,
                    'title': course_data.title[:200] if course_data.title else course_code,
                    'description': course_data.description[:1000] if course_data.description else None,
                    'credits': course_data.credits,
                    'department_prefix': dept_prefix,
                    'prerequisites': ', '.join(course_data.prerequisites) if course_data.prerequisites else None
                }
                courses_to_insert.append(course_record)
                
                if len(courses_to_insert) >= batch_size:
                    if not dry_run:
                        result = supabase.table('academic_courses').upsert(courses_to_insert).execute()
                        stats['courses_inserted'] += len(courses_to_insert)
                    courses_to_insert = []
            
            # Insert remaining courses
            if courses_to_insert and not dry_run:
                result = supabase.table('academic_courses').upsert(courses_to_insert).execute()
                stats['courses_inserted'] += len(courses_to_insert)
            elif dry_run:
                stats['courses_inserted'] = len(courses_to_insert)
            
            # Process programs
            programs_to_insert = []
            for program_code, program_data in academic_data.get('programs', {}).items():
                stats['programs_processed'] += 1
                
                if program_code in existing_programs:
                    stats['duplicates_skipped'] += 1
                    continue
                
                # Truncate name if too long
                program_name = program_data.name[:150] if len(program_data.name) > 150 else program_data.name
                
                program_record = {
                    'program_code': program_code,
                    'program_name': program_name,
                    'degree_type': program_data.type,
                    'department_prefix': program_data.department,
                    'description': program_data.description[:1000] if program_data.description else None
                }
                programs_to_insert.append(program_record)
                
                if len(programs_to_insert) >= batch_size:
                    if not dry_run:
                        result = supabase.table('academic_programs').upsert(programs_to_insert).execute()
                        stats['programs_inserted'] += len(programs_to_insert)
                    programs_to_insert = []
            
            # Insert remaining programs
            if programs_to_insert and not dry_run:
                result = supabase.table('academic_programs').upsert(programs_to_insert).execute()
                stats['programs_inserted'] += len(programs_to_insert)
            elif dry_run:
                stats['programs_inserted'] = len(programs_to_insert)
            
        finally:
            # Always close the builder connection
            builder.close()
        
        # Calculate totals
        total_inserted = stats['departments_inserted'] + stats['courses_inserted'] + stats['programs_inserted']
        total_processed = stats['departments_processed'] + stats['courses_processed'] + stats['programs_processed']
        
        result = {
            "success": True,
            "message": "Supabase backup population completed successfully" if not dry_run else "Dry run completed - no data was actually inserted",
            "mode": "dry_run" if dry_run else "live",
            "statistics": {
                "total_processed": total_processed,
                "total_inserted": total_inserted,
                "duplicates_skipped": stats['duplicates_skipped'],
                "departments": {
                    "processed": stats['departments_processed'],
                    "inserted": stats['departments_inserted']
                },
                "courses": {
                    "processed": stats['courses_processed'],
                    "inserted": stats['courses_inserted']
                },
                "programs": {
                    "processed": stats['programs_processed'],
                    "inserted": stats['programs_inserted']
                },
                "batch_size": batch_size,
                "errors": stats['errors']
            },
            "recommendations": [
                "Verify data integrity with sample queries",
                "Check for any missing prerequisite relationships",
                "Test academic search tools with populated data",
                "Consider running build_academic_knowledge_graph for Neo4j population"
            ] if not dry_run else [
                "Run without --dry-run flag to actually insert data",
                "Consider using --clear flag if you want to replace existing data",
                "Adjust --batch-size if needed for performance"
            ]
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Failed to populate Supabase tables with backup tool",
            "troubleshooting": [
                "Check Supabase connection (SUPABASE_URL, SUPABASE_SERVICE_KEY)",
                "Ensure academic tables exist (run SQL migration first)",
                "Verify crawled academic content exists in database",
                "Check for data constraint violations (name lengths, etc.)",
                "Try with smaller batch_size or dry_run mode first"
            ]
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def get_prerequisite_chain(ctx: Context, course_code: str, max_depth: int = 10) -> str:
    """
    Get the complete prerequisite chain for a course using the knowledge graph.
    
    This tool traces all prerequisite relationships for a given course, showing
    the complete dependency chain and estimated pathway to completion.
    
    Args:
        ctx: The MCP server provided context
        course_code: Course code to analyze (e.g., "CS 3150", "BIOL 3450")
        max_depth: Maximum depth to search for prerequisites (default: 10)
    
    Returns:
        JSON string with prerequisite chain analysis and pathway recommendations
    """
    try:
        planner = GraphEnhancedAcademicPlanner()
        
        # Get prerequisite chains
        chains = await planner.get_prerequisite_chain(course_code, max_depth)
        
        if not chains:
            result = {
                "course": course_code,
                "prerequisite_chains": [],
                "message": f"No prerequisite chains found for {course_code}. This course may have no prerequisites or may not exist in the knowledge graph.",
                "recommendations": [
                    "Verify the course code is correct",
                    "Check if the course exists in the catalog",
                    "This course may be suitable for early enrollment"
                ]
            }
        else:
            # Find the longest and shortest paths
            longest_path = max(chains, key=lambda x: len(x.path))
            shortest_path = min(chains, key=lambda x: len(x.path))
            
            result = {
                "course": course_code,
                "prerequisite_chains": [
                    {
                        "path": chain.path,
                        "total_credits": chain.total_credits,
                        "estimated_semesters": chain.semesters_needed,
                        "path_length": len(chain.path)
                    } for chain in chains
                ],
                "analysis": {
                    "total_chains_found": len(chains),
                    "longest_path": {
                        "courses": longest_path.path,
                        "length": len(longest_path.path),
                        "credits": longest_path.total_credits
                    },
                    "shortest_path": {
                        "courses": shortest_path.path,
                        "length": len(shortest_path.path),
                        "credits": shortest_path.total_credits
                    }
                },
                "recommendations": [
                    f"Plan for {shortest_path.semesters_needed}-{longest_path.semesters_needed} semesters to complete prerequisites",
                    f"Total prerequisite credits: {shortest_path.total_credits}-{longest_path.total_credits}",
                    "Consider taking prerequisite courses in the suggested sequence",
                    "Verify course availability and scheduling before planning"
                ]
            }
        
        await planner.close()
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "error": f"Failed to analyze prerequisite chain: {str(e)}",
            "course": course_code,
            "troubleshooting": [
                "Verify Neo4j connection is working",
                "Check if academic knowledge graph is populated",
                "Ensure course code format is correct (e.g., 'CS 1400')"
            ]
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def validate_course_sequence(ctx: Context, course_list: str) -> str:
    """
    Validate if a sequence of courses respects prerequisite requirements.
    
    This tool checks if the given course sequence can be completed in order
    without prerequisite violations, and provides detailed analysis.
    
    Args:
        ctx: The MCP server provided context
        course_list: Comma-separated list of course codes in intended order (e.g., "CS 1400, CS 1410, CS 2420")
    
    Returns:
        JSON string with sequence validation results and recommendations
    """
    try:
        # Parse course list
        courses = [course.strip().upper() for course in course_list.split(',') if course.strip()]
        
        if not courses:
            return json.dumps({
                "error": "No courses provided",
                "message": "Please provide a comma-separated list of course codes"
            }, indent=2)
        
        planner = GraphEnhancedAcademicPlanner()
        
        # Validate sequence
        validation = await planner.validate_course_sequence(courses)
        
        # Add recommendations based on validation results
        recommendations = []
        if validation["valid"]:
            recommendations.extend([
                "✅ Course sequence is valid - no prerequisite violations detected",
                "Consider course scheduling and availability when planning",
                "Verify credit hour limits per semester"
            ])
        else:
            recommendations.extend([
                "❌ Prerequisite violations detected - sequence needs adjustment",
                "Review prerequisite requirements for flagged courses",
                "Consider reordering courses to satisfy prerequisites"
            ])
        
        # Add IAP-specific recommendations
        stats = validation["statistics"]
        if stats["total_credits"] < 120:
            recommendations.append(f"⚠️ Only {stats['total_credits']} credits - need {120 - stats['total_credits']} more for graduation")
        
        if stats["upper_division_credits"] < 40:
            recommendations.append(f"⚠️ Only {stats['upper_division_credits']} upper-division credits - need {40 - stats['upper_division_credits']} more")
        
        if stats["discipline_count"] < 3:
            recommendations.append(f"⚠️ Only {stats['discipline_count']} disciplines - need {3 - stats['discipline_count']} more for IAP requirement")
        
        result = {
            "course_sequence": courses,
            "validation_result": validation["valid"],
            "violations": validation["violations"],
            "statistics": validation["statistics"],
            "course_details": validation["course_details"],
            "recommendations": recommendations
        }
        
        await planner.close()
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "error": f"Failed to validate course sequence: {str(e)}",
            "course_list": course_list,
            "troubleshooting": [
                "Verify Neo4j connection is working",
                "Check if academic knowledge graph is populated",
                "Ensure course codes are formatted correctly"
            ]
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def recommend_course_sequence(ctx: Context, target_courses: str, max_semesters: int = 8) -> str:
    """
    Recommend optimal course sequence respecting prerequisites and credit limits.
    
    This tool creates an intelligent semester-by-semester course plan that
    respects prerequisite requirements and credit hour limitations.
    
    Args:
        ctx: The MCP server provided context
        target_courses: Comma-separated list of desired courses (e.g., "CS 3150, CS 4550, BIOL 3450")
        max_semesters: Maximum number of semesters to plan (default: 8)
    
    Returns:
        JSON string with recommended course sequence and academic plan
    """
    try:
        # Parse course list
        courses = [course.strip().upper() for course in target_courses.split(',') if course.strip()]
        
        if not courses:
            return json.dumps({
                "error": "No courses provided",
                "message": "Please provide a comma-separated list of course codes"
            }, indent=2)
        
        planner = GraphEnhancedAcademicPlanner()
        
        # Generate academic plan
        plan = await planner.recommend_course_sequence(courses, max_semesters)
        
        # Format semester sequence with details
        formatted_sequence = []
        for i, semester in enumerate(plan.recommended_sequence, 1):
            semester_credits = 0
            semester_courses = []
            
            for course_code in semester:
                # This is a simplified approach - in a real implementation,
                # you'd want to get actual course details from the graph
                semester_courses.append({
                    "code": course_code,
                    "credits": 3  # Default assumption
                })
                semester_credits += 3
            
            formatted_sequence.append({
                "semester": i,
                "courses": semester_courses,
                "total_credits": semester_credits
            })
        
        # Generate recommendations
        recommendations = [
            f"Plan spans {len(plan.recommended_sequence)} semesters",
            f"Total credits: {plan.total_credits}",
            f"Upper-division credits: {plan.upper_division_credits}",
            f"Disciplines covered: {len(plan.disciplines)}"
        ]
        
        # IAP requirement checks
        if plan.total_credits >= 120:
            recommendations.append("✅ Meets 120 credit hour requirement")
        else:
            recommendations.append(f"⚠️ Need {120 - plan.total_credits} more credits for graduation")
        
        if plan.upper_division_credits >= 40:
            recommendations.append("✅ Meets 40 upper-division credit requirement")
        else:
            recommendations.append(f"⚠️ Need {40 - plan.upper_division_credits} more upper-division credits")
        
        if len(plan.disciplines) >= 3:
            recommendations.append("✅ Meets 3+ discipline requirement")
        else:
            recommendations.append(f"⚠️ Need courses from {3 - len(plan.disciplines)} more disciplines")
        
        result = {
            "target_courses": courses,
            "academic_plan": {
                "total_courses": len(plan.courses),
                "total_credits": plan.total_credits,
                "upper_division_credits": plan.upper_division_credits,
                "disciplines": list(plan.disciplines),
                "estimated_semesters": len(plan.recommended_sequence)
            },
            "semester_sequence": formatted_sequence,
            "prerequisite_violations": plan.prerequisite_violations,
            "recommendations": recommendations
        }
        
        await planner.close()
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "error": f"Failed to recommend course sequence: {str(e)}",
            "target_courses": target_courses,
            "troubleshooting": [
                "Verify Neo4j connection is working",
                "Check if academic knowledge graph is populated",
                "Ensure course codes are formatted correctly"
            ]
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def analyze_degree_progress(ctx: Context, completed_courses: str, target_courses: str) -> str:
    """
    Analyze progress toward degree completion and IAP requirements.
    
    This tool provides comprehensive analysis of academic progress including
    completed requirements, remaining needs, and graduation readiness.
    
    Args:
        ctx: The MCP server provided context
        completed_courses: Comma-separated list of completed course codes
        target_courses: Comma-separated list of all courses needed for degree
    
    Returns:
        JSON string with degree progress analysis and recommendations
    """
    try:
        # Parse course lists
        completed = [course.strip().upper() for course in completed_courses.split(',') if course.strip()]
        target = [course.strip().upper() for course in target_courses.split(',') if course.strip()]
        
        if not target:
            return json.dumps({
                "error": "No target courses provided",
                "message": "Please provide target courses for degree completion analysis"
            }, indent=2)
        
        planner = GraphEnhancedAcademicPlanner()
        
        # Analyze progress
        progress = await planner.analyze_degree_progress(completed, target)
        
        # Generate actionable recommendations
        recommendations = []
        
        # Progress-based recommendations
        if progress["overall_progress"]["percentage"] < 25:
            recommendations.append("🎯 Early stage - focus on foundational and prerequisite courses")
        elif progress["overall_progress"]["percentage"] < 50:
            recommendations.append("📚 Mid-progress - balance lower and upper-division requirements")
        elif progress["overall_progress"]["percentage"] < 75:
            recommendations.append("🎓 Advanced stage - prioritize upper-division and capstone courses")
        else:
            recommendations.append("🏁 Near completion - focus on remaining requirements")
        
        # Requirement-specific recommendations
        iap_reqs = progress["iap_requirements"]
        
        if not iap_reqs["total_credits"]["met"]:
            recommendations.append(f"📊 Need {iap_reqs['total_credits']['remaining']} more credits for graduation")
        
        if not iap_reqs["upper_division_credits"]["met"]:
            recommendations.append(f"📈 Need {iap_reqs['upper_division_credits']['remaining']} more upper-division credits")
        
        if not iap_reqs["disciplines"]["met"]:
            recommendations.append(f"🔬 Need courses from {iap_reqs['disciplines']['remaining']} more disciplines")
        
        # Graduation readiness
        if progress["overall_progress"]["ready_to_graduate"]:
            recommendations.append("🎉 Ready to graduate! All IAP requirements met")
        else:
            recommendations.append("📋 Review remaining requirements before graduation application")
        
        result = {
            "completed_courses": completed,
            "target_courses": target,
            "progress_analysis": progress,
            "recommendations": recommendations,
            "next_steps": [
                "Review remaining course list for scheduling",
                "Check course prerequisites and availability",
                "Consider course load and semester planning",
                "Consult with academic advisor for final validation"
            ]
        }
        
        await planner.close()
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "error": f"Failed to analyze degree progress: {str(e)}",
            "completed_courses": completed_courses,
            "target_courses": target_courses,
            "troubleshooting": [
                "Verify Neo4j connection is working",
                "Check if academic knowledge graph is populated",
                "Ensure course codes are formatted correctly"
            ]
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def find_alternative_courses(ctx: Context, course_code: str, same_department: bool = True, limit: int = 5) -> str:
    """
    Find alternative courses that could substitute for a given course.
    
    This tool helps find equivalent or similar courses when the original
    course is unavailable, full, or doesn't fit the schedule.
    
    Args:
        ctx: The MCP server provided context
        course_code: Course code to find alternatives for (e.g., "PSYC 1010")
        same_department: Whether to limit search to same department (default: True)
        limit: Maximum number of alternatives to return (default: 5)
    
    Returns:
        JSON string with alternative course suggestions and analysis
    """
    try:
        planner = GraphEnhancedAcademicPlanner()
        
        # Find alternatives
        alternatives = await planner.find_alternative_courses(course_code, same_department)
        
        if not alternatives:
            result = {
                "original_course": course_code,
                "alternatives": [],
                "message": f"No alternative courses found for {course_code}",
                "suggestions": [
                    "Try expanding search to other departments (set same_department=False)",
                    "Check if the course code is correct",
                    "Consider courses with similar content or level",
                    "Consult with academic advisor for manual alternatives"
                ]
            }
        else:
            # Limit results
            limited_alternatives = alternatives[:limit]
            
            result = {
                "original_course": course_code,
                "alternatives": [
                    {
                        "code": alt.code,
                        "title": alt.title,
                        "credits": alt.credits,
                        "level": alt.level,
                        "department": alt.department,
                        "prerequisites": alt.prerequisites,
                        "description_preview": alt.description[:200] + "..." if len(alt.description) > 200 else alt.description
                    } for alt in limited_alternatives
                ],
                "analysis": {
                    "total_alternatives_found": len(alternatives),
                    "showing": len(limited_alternatives),
                    "departments_represented": list(set(alt.department for alt in limited_alternatives)),
                    "credit_range": {
                        "min": min(alt.credits for alt in limited_alternatives),
                        "max": max(alt.credits for alt in limited_alternatives)
                    }
                },
                "recommendations": [
                    "Compare course descriptions and learning outcomes",
                    "Verify prerequisites for alternative courses",
                    "Check course scheduling and availability",
                    "Confirm alternatives meet degree requirements",
                    "Consult with academic advisor before substituting"
                ]
            }
        
        await planner.close()
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "error": f"Failed to find alternative courses: {str(e)}",
            "course_code": course_code,
            "troubleshooting": [
                "Verify Neo4j connection is working",
                "Check if academic knowledge graph is populated",
                "Ensure course code format is correct"
            ]
        }
        return json.dumps(error_result, indent=2)

# ============================================================================
# IAP (Individualized Academic Plan) Management Tools
# ============================================================================

@mcp.tool()
async def create_iap_template(ctx: Context, student_name: str, student_id: str, 
                            degree_emphasis: str, student_email: str = "", 
                            student_phone: str = "") -> str:
    """
    Create a new IAP (Individualized Academic Plan) template for a student.
    
    This tool initializes a comprehensive IAP template with default program goals,
    learning outcomes, and structure for Utah Tech's Bachelor of Individualized Studies.
    
    **Student Collaboration Context:**
    - **When to Use**: At the beginning of the first advising session
    - **How to Introduce**: "Let's start by creating your personalized IAP template"
    - **Student Involvement**: Have student provide their information directly
    - **Follow-up**: "Great! I've created your IAP foundation. Now we can start building your plan together."
    
    **Communication Tips:**
    - Explain that this creates their "academic blueprint"
    - Reassure students that everything can be modified later
    - Emphasize that this is the start of a collaborative process
    
    Args:
        ctx: The MCP server provided context
        student_name: Full name of the student
        student_id: Student ID number
        degree_emphasis: Proposed degree emphasis (e.g., "Psychology and Communication")
        student_email: Optional student email address
        student_phone: Optional student phone number
    
    Returns:
        JSON string with IAP template creation results and next steps
    """
    try:
        supabase_client = get_supabase_from_context(ctx)
        iap_manager = IAPManager(supabase_client)
        result = await iap_manager.create_iap_template(
            student_name=student_name,
            student_id=student_id,
            degree_emphasis=degree_emphasis,
            student_email=student_email,
            student_phone=student_phone
        )
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to create IAP template: {str(e)}",
            "troubleshooting": [
                "Verify all required student information is provided",
                "Check database connection",
                "Ensure degree emphasis is descriptive and specific"
            ]
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def update_iap_section(ctx: Context, student_id: str, section: str, 
                           data: str) -> str:
    """
    Update a specific section of an IAP template.
    
    This tool allows updating individual sections of an IAP including mission statement,
    program goals, learning outcomes, course mappings, and academic plans.
    
    **Student Collaboration Context:**
    - **When to Use**: After collaborative discussions and decisions
    - **How to Introduce**: "Let's update your IAP with what we've discussed"
    - **Student Involvement**: Review changes together before implementing
    - **Follow-up**: "Perfect! Your IAP now reflects our discussion. What should we work on next?"
    
    **Communication Tips:**
    - Always review the content with the student before updating
    - Explain what section is being modified and why
    - Confirm student agreement with changes
    
    Args:
        ctx: The MCP server provided context
        student_id: Student ID to identify the IAP template
        section: Section to update (mission_statement, program_goals, program_learning_outcomes, 
                course_mappings, concentration_areas, cover_letter, academic_plan)
        data: JSON string containing the section data to update
    
    Returns:
        JSON string with update results and confirmation
    """
    try:
        # Parse data as JSON
        try:
            section_data = json.loads(data)
        except json.JSONDecodeError:
            # If not JSON, treat as plain text for simple sections
            section_data = data
        
        supabase_client = get_supabase_from_context(ctx)
        iap_manager = IAPManager(supabase_client)
        result = await iap_manager.update_iap_section(
            student_id=student_id,
            section=section,
            data=section_data
        )
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to update IAP section: {str(e)}",
            "troubleshooting": [
                "Verify student ID exists",
                "Check section name is valid",
                "Ensure data format is correct (JSON for complex data)"
            ]
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def generate_iap_suggestions(ctx: Context, degree_emphasis: str, 
                                 section: str, context: str = "") -> str:
    """
    Generate AI-powered suggestions for IAP content.
    
    This tool provides intelligent suggestions for mission statements, program goals,
    learning outcomes, cover letter content, and concentration areas based on the
    student's degree emphasis and context.
    
    **Student Collaboration Context:**
    - **When to Use**: When students need inspiration or are stuck
    - **How to Introduce**: "Let me generate some ideas to help spark your thinking"
    - **Student Involvement**: Review suggestions together and choose/modify preferred options
    - **Follow-up**: "Which of these resonates with you? How would you modify it to make it your own?"
    
    **Communication Tips:**
    - Present suggestions as starting points, not final answers
    - Encourage students to personalize and modify suggestions
    - Use suggestions to facilitate discussion about student goals
    
    Args:
        ctx: The MCP server provided context
        degree_emphasis: Student's proposed degree emphasis
        section: Section to generate suggestions for (mission_statement, program_goals, 
                cover_letter, concentration_areas)
        context: Optional additional context to inform suggestions
    
    Returns:
        JSON string with AI-generated suggestions and customization tips
    """
    try:
        # Parse context if provided
        context_data = {}
        if context:
            try:
                context_data = json.loads(context)
            except json.JSONDecodeError:
                context_data = {"additional_info": context}
        
        supabase_client = get_supabase_from_context(ctx)
        iap_manager = IAPManager(supabase_client)
        result = await iap_manager.generate_iap_suggestions(
            degree_emphasis=degree_emphasis,
            section=section,
            context=context_data
        )
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to generate IAP suggestions: {str(e)}",
            "troubleshooting": [
                "Verify degree emphasis is descriptive",
                "Check section name is valid",
                "Ensure context is properly formatted if provided"
            ]
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def validate_complete_iap(ctx: Context, student_id: str, 
                              iap_data: str = "") -> str:
    """
    Perform comprehensive validation of a complete IAP template.
    
    This tool validates all IAP requirements including required sections, credit hours,
    concentration areas, prerequisite compliance, and Utah Tech BIS degree requirements.
    
    **Student Collaboration Context:**
    - **When to Use**: Before finalizing IAP or when student wants to check progress
    - **How to Introduce**: "Let's run a comprehensive check on your IAP to see how we're doing"
    - **Student Involvement**: Review validation results together and prioritize next steps
    - **Follow-up**: "Here's what we've accomplished and what still needs attention. Which area would you like to focus on next?"
    
    **Communication Tips:**
    - Frame validation as progress assessment, not criticism
    - Celebrate completed requirements before addressing gaps
    - Help students prioritize remaining tasks
    
    Args:
        ctx: The MCP server provided context
        student_id: Student ID to identify the IAP template
        iap_data: Optional JSON string with IAP data (if not retrieving from database)
    
    Returns:
        JSON string with comprehensive validation results and recommendations
    """
    try:
        # Parse IAP data if provided, otherwise would retrieve from database
        if iap_data:
            try:
                iap_dict = json.loads(iap_data)
            except json.JSONDecodeError:
                return json.dumps({
                    "success": False,
                    "error": "Invalid JSON format for IAP data"
                }, indent=2)
        else:
            # In full implementation, would retrieve from database using student_id
            iap_dict = {
                "student_id": student_id,
                "message": "Database retrieval not implemented - provide iap_data parameter"
            }
        
        supabase_client = get_supabase_from_context(ctx)
        iap_manager = IAPManager(supabase_client)
        result = await iap_manager.validate_iap_requirements(iap_dict)
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to validate IAP: {str(e)}",
            "troubleshooting": [
                "Verify student ID exists",
                "Check IAP data format if provided",
                "Ensure all required sections are present"
            ]
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def conduct_market_research(ctx: Context, degree_emphasis: str, 
                                geographic_focus: str = "Utah") -> str:
    """
    Conduct market research for degree viability analysis.
    
    This tool analyzes job market data, salary information, industry trends,
    and skill demand to assess the viability of a specific degree emphasis.
    Provides comprehensive market intelligence for IAP cover letter development.
    
    **Student Collaboration Context:**
    - **When to Use**: When developing cover letter or validating degree emphasis
    - **How to Introduce**: "Let's research the job market for your degree emphasis"
    - **Student Involvement**: Discuss findings and how they align with student's career goals
    - **Follow-up**: "Based on this research, how does this align with your career aspirations? Should we adjust anything?"
    
    **Communication Tips:**
    - Present data objectively while remaining supportive
    - Help students interpret market trends in context of their goals
    - Use findings to strengthen their IAP narrative
    
    Args:
        ctx: The MCP server provided context
        degree_emphasis: Student's proposed degree emphasis
        geographic_focus: Geographic region for market analysis (default: Utah)
    
    Returns:
        JSON string with comprehensive market research data and viability assessment
    """
    try:
        supabase_client = get_supabase_from_context(ctx)
        iap_manager = IAPManager(supabase_client)
        result = await iap_manager.conduct_market_research(
            degree_emphasis=degree_emphasis,
            geographic_focus=geographic_focus
        )
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to conduct market research: {str(e)}",
            "troubleshooting": [
                "Verify degree emphasis is specified",
                "Check geographic focus parameter",
                "Ensure market data sources are accessible"
            ]
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def track_general_education(ctx: Context, student_id: str, 
                                course_list: str = "") -> str:
    """
    Track general education requirement completion for Utah Tech University.
    
    This tool analyzes a student's completed courses against Utah Tech's
    general education requirements, providing completion status and recommendations
    for remaining requirements.
    
    **Student Collaboration Context:**
    - **When to Use**: When reviewing transcript or planning remaining coursework
    - **How to Introduce**: "Let's check your general education progress"
    - **Student Involvement**: Review completed requirements together and plan remaining courses
    - **Follow-up**: "Great progress! Here's what you still need. Which GE areas interest you most?"
    
    **Communication Tips:**
    - Celebrate completed GE requirements first
    - Help students choose interesting courses for remaining requirements
    - Connect GE courses to their degree emphasis when possible
    
    Args:
        ctx: The MCP server provided context
        student_id: Student's unique identifier
        course_list: JSON array or comma-separated list of completed courses
    
    Returns:
        JSON string with GE completion analysis and recommendations
    """
    try:
        # Parse course list
        courses = []
        if course_list:
            try:
                # Try parsing as JSON array first
                courses = json.loads(course_list)
            except json.JSONDecodeError:
                # Fall back to comma-separated parsing
                courses = [course.strip() for course in course_list.split(',') if course.strip()]
        
        supabase_client = get_supabase_from_context(ctx)
        iap_manager = IAPManager(supabase_client)
        result = await iap_manager.track_general_education(
            student_id=student_id,
            course_list=courses
        )
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to track general education: {str(e)}",
            "troubleshooting": [
                "Verify student ID is provided",
                "Check course list format (JSON array or comma-separated)",
                "Ensure course codes are valid Utah Tech courses"
            ]
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def validate_concentration_areas(ctx: Context, student_id: str, 
                                     concentration_areas: str, 
                                     course_mappings: str) -> str:
    """
    Validate concentration area requirements and credit distribution.
    
    This tool ensures that concentration areas meet BIS program requirements:
    - At least 3 concentration areas
    - Minimum 14 credits per concentration (7 upper-division)
    - Proper credit distribution across disciplines
    
    **Student Collaboration Context:**
    - **When to Use**: When finalizing concentration areas or checking credit distribution
    - **How to Introduce**: "Let's validate your concentration areas to ensure they meet BIS requirements"
    - **Student Involvement**: Review validation results and adjust course selections together
    - **Follow-up**: "Your concentrations look good! Here are some suggestions to strengthen them further."
    
    **Communication Tips:**
    - Help students understand the rationale behind BIS requirements
    - Suggest courses that could strengthen weak concentration areas
    - Emphasize the interdisciplinary nature of their unique degree
    
    Args:
        ctx: The MCP server provided context
        student_id: Student's unique identifier
        concentration_areas: JSON array of concentration area names
        course_mappings: JSON object mapping concentration areas to course lists
    
    Returns:
        JSON string with detailed validation results and recommendations
    """
    try:
        # Parse concentration areas
        try:
            areas = json.loads(concentration_areas)
        except json.JSONDecodeError:
            areas = [area.strip() for area in concentration_areas.split(',') if area.strip()]
        
        # Parse course mappings
        try:
            mappings = json.loads(course_mappings)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "error": "course_mappings must be valid JSON object",
                "example": '{"Psychology": ["PSYC 1010", "PSYC 2010"], "Communication": ["COMM 1010", "COMM 2110"]}'
            }, indent=2)
        
        supabase_client = get_supabase_from_context(ctx)
        iap_manager = IAPManager(supabase_client)
        result = await iap_manager.validate_concentration_areas(
            student_id=student_id,
            concentration_areas=areas,
            course_mappings=mappings
        )
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to validate concentration areas: {str(e)}",
            "troubleshooting": [
                "Verify student ID is provided",
                "Check concentration_areas format (JSON array or comma-separated)",
                "Ensure course_mappings is valid JSON object",
                "Verify course codes are properly formatted"
            ]
        }
        return json.dumps(error_result, indent=2)

async def main():
    """Main function to run the MCP server"""
    print("Starting Crawl4AI MCP Server...")
    transport = os.getenv("TRANSPORT", "sse")
    if transport == 'sse':
        print("Starting MCP server in SSE mode")
        # Run the MCP server with sse transport
        await mcp.run_sse_async()
    else:
        print("Starting MCP server in STDIO mode")
        # Run the MCP server with stdio transport
        await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())