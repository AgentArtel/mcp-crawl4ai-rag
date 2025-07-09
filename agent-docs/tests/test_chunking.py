#!/usr/bin/env python3
"""
Test script for debugging the course-boundary chunking logic.
This allows us to quickly test and iterate on the regex and chunking without Docker builds.
"""

import re
import requests
from typing import List, Dict, Any
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
import asyncio

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
            if 'Art Department' in line or 'Department Degrees and Minors' in line or line.startswith('#'):
                dept_lines.append(line)
            elif line.strip() and not any(skip in line.lower() for skip in ['skip to content', 'catalog home', 'academic calendar', 'print options']):
                if len(dept_lines) < 10:  # Only include first few relevant lines
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
                # Create one chunk per section with all its programs
                full_section = f"#### **{section_name}**\n{section_content}"
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

# This function is no longer needed since we're chunking by sections, not individual programs
# def extract_programs_from_section(section_content: str, section_type: str) -> List[Dict[str, Any]]:

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
    # Use the original course-boundary chunking for course catalogs
    course_pattern = re.compile(r'\n([A-Z]{2,4}\s\d{3,4}[A-Z]?)\s')
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

async def test_chunking():
    """Test the comprehensive academic chunking logic on the Utah Tech Art department page."""
    
    print("🔍 Testing comprehensive academic content chunking on ART department...")
    
    # Initialize crawler
    crawler = AsyncWebCrawler(verbose=True)
    await crawler.start()
    
    try:
        # Test on the Art department overview page (has programs, not individual courses)
        url = "https://catalog.utahtech.edu/programs/art/"
        print(f"📄 Crawling: {url}")
        
        run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
        result = await crawler.arun(url=url, config=run_config)
        
        if result.success and result.markdown:
            print(f"✅ Successfully crawled page ({len(result.markdown)} characters)")
            
            # Save the raw markdown for inspection
            with open("raw_markdown.txt", "w", encoding="utf-8") as f:
                f.write(result.markdown)
            print("💾 Raw markdown saved to 'raw_markdown.txt'")
            
            # Test content type detection
            content_type = detect_content_type(result.markdown)
            print(f"🔍 Content type detected: {content_type}")
            
            # Test our chunking logic
            print("\n🔧 Testing chunking logic...")
            chunks = chunk_academic_content(result.markdown)
            
            print(f"\n📊 Results:")
            print(f"   - Total chunks: {len(chunks)}")
            
            for i, chunk in enumerate(chunks, 1):
                metadata = chunk['metadata']
                content_preview = chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content']
                
                print(f"\n📋 Chunk {i}:")
                print(f"   - Content type: {metadata.get('content_type', 'unknown')}")
                print(f"   - Character count: {metadata.get('char_count', 0)}")
                print(f"   - Word count: {metadata.get('word_count', 0)}")
                print(f"   - Course codes found: {metadata.get('course_codes', [])}")
                
                # Show section-specific metadata
                if metadata.get('section_type'):
                    print(f"   - Section type: {metadata.get('section_type')}")
                    print(f"   - Degree level: {metadata.get('degree_level')}")
                    print(f"   - Programs in section: {metadata.get('programs_in_section', 0)}")
                    if metadata.get('program_names'):
                        print(f"   - Program names: {metadata.get('program_names')[:3]}{'...' if len(metadata.get('program_names', [])) > 3 else ''}")
                
                # Show department-specific metadata
                if metadata.get('is_department_overview'):
                    print(f"   - Masters programs: {metadata.get('masters_programs', 0)}")
                    print(f"   - Bachelors programs: {metadata.get('bachelors_programs', 0)}")
                    print(f"   - Minors: {metadata.get('minors_count', 0)}")
                    print(f"   - Certificates: {metadata.get('certificates_count', 0)}")
                
                print(f"   - Content preview: {content_preview}")
                
                # Save each chunk for inspection
                with open(f"chunk_{i}.txt", "w", encoding="utf-8") as f:
                    f.write(chunk['content'])
            
            print(f"\n💾 Individual chunks saved as 'chunk_1.txt', 'chunk_2.txt', etc.")
            
        else:
            print(f"❌ Failed to crawl page: {result.error_message}")
            
    finally:
        await crawler.close()

if __name__ == "__main__":
    asyncio.run(test_chunking())
