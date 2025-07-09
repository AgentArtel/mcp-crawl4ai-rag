#!/usr/bin/env python3
"""
Test script to verify that the academic content chunking works universally
across different departments and page types at Utah Tech.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).resolve().parent / 'src'
sys.path.insert(0, str(src_path))

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai_mcp import chunk_academic_content, detect_content_type

async def test_department_pages():
    """Test chunking on different department overview pages."""
    
    test_urls = [
        # Different departments
        ("Art Department", "https://catalog.utahtech.edu/programs/art/"),
        ("Computer Science", "https://catalog.utahtech.edu/programs/computer-science/"),
        ("Business", "https://catalog.utahtech.edu/programs/business/"),
        ("Engineering", "https://catalog.utahtech.edu/programs/engineering/"),
        ("Education", "https://catalog.utahtech.edu/programs/education/"),
        
        # Different page types
        ("Course Descriptions", "https://catalog.utahtech.edu/courses/art/"),
        ("Specific Program", "https://catalog.utahtech.edu/programs/art/studio-art-mfa/"),
    ]
    
    # Initialize crawler
    browser_config = BrowserConfig(
        headless=True,
        verbose=False
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("🔍 Testing academic content chunking universality across Utah Tech...")
        print("=" * 80)
        
        for dept_name, url in test_urls:
            print(f"\n📚 Testing: {dept_name}")
            print(f"🔗 URL: {url}")
            
            try:
                # Crawl the page
                run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
                result = await crawler.arun(url=url, config=run_config)
                
                if result.success and result.markdown:
                    # Test content type detection
                    content_type = detect_content_type(result.markdown)
                    print(f"🔍 Content type detected: {content_type}")
                    
                    # Test chunking
                    chunks = chunk_academic_content(result.markdown)
                    print(f"📊 Chunks created: {len(chunks)}")
                    
                    # Analyze chunk types and content
                    chunk_types = {}
                    total_programs = 0
                    total_courses = 0
                    
                    for i, chunk in enumerate(chunks):
                        metadata = chunk['metadata']
                        chunk_type = metadata.get('content_type', 'unknown')
                        
                        # Count chunk types
                        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
                        
                        # Count programs and courses
                        total_programs += metadata.get('programs_in_section', 0)
                        total_courses += len(metadata.get('course_codes', []))
                        
                        # Show first few chunks in detail
                        if i < 3:
                            print(f"   📋 Chunk {i+1}:")
                            print(f"      - Type: {chunk_type}")
                            print(f"      - Characters: {metadata.get('char_count', 0)}")
                            print(f"      - Words: {metadata.get('word_count', 0)}")
                            
                            if chunk_type == 'program_section':
                                section_type = metadata.get('section_type', 'Unknown')
                                degree_level = metadata.get('degree_level', 'unknown')
                                programs = metadata.get('programs_in_section', 0)
                                print(f"      - Section: {section_type} ({degree_level})")
                                print(f"      - Programs: {programs}")
                                
                                # Show program names if available
                                program_names = metadata.get('program_names', [])
                                if program_names:
                                    print(f"      - Program names: {program_names[:3]}{'...' if len(program_names) > 3 else ''}")
                            
                            elif chunk_type == 'course':
                                course_codes = metadata.get('course_codes', [])
                                if course_codes:
                                    print(f"      - Course codes: {course_codes}")
                    
                    # Summary
                    print(f"📈 Summary:")
                    print(f"   - Chunk types: {dict(chunk_types)}")
                    print(f"   - Total programs found: {total_programs}")
                    print(f"   - Total course codes found: {total_courses}")
                    
                    # Check for common issues
                    if len(chunks) > 50:
                        print(f"⚠️  Warning: High chunk count ({len(chunks)}) - might be over-fragmenting")
                    
                    if content_type == 'generic' and any('degree' in url.lower() or 'program' in url.lower() for url in [url]):
                        print(f"⚠️  Warning: Academic page detected as generic - content type detection may need improvement")
                    
                else:
                    print(f"❌ Failed to crawl: {result.error_message if result else 'Unknown error'}")
                    
            except Exception as e:
                print(f"❌ Error testing {dept_name}: {str(e)}")
            
            print("-" * 60)

async def test_course_code_patterns():
    """Test that course code detection works for different departments."""
    
    print("\n🧪 Testing course code pattern detection...")
    print("=" * 50)
    
    test_patterns = [
        # Different department codes
        "ART 1010 Introduction to Art",
        "MATH 1050 College Algebra", 
        "ENGL 1010 Introduction to Writing",
        "CS 1400 Fundamentals of Programming",
        "BIOL 1610 Biology I",
        "HIST 1700 American Civilization",
        "PHYS 2210 Physics for Scientists and Engineers I",
        "CHEM 1210 Principles of Chemistry I",
        "PSY 1010 General Psychology",
        "ECON 2010 Principles of Microeconomics",
        
        # Different formats
        "MUSC 1010A Applied Music",  # With letter suffix
        "PE 1097 Fitness for Life",   # Short department code
        "COMM 2110 Interpersonal Communication",  # 4-letter department
    ]
    
    from crawl4ai_mcp import extract_academic_info
    
    for pattern in test_patterns:
        # Test course code extraction
        metadata = extract_academic_info(pattern, "course")
        course_codes = metadata.get('course_codes', [])
        
        print(f"📝 '{pattern}'")
        print(f"   Detected codes: {course_codes}")
        
        if not course_codes:
            print(f"   ⚠️  No course codes detected!")
        elif len(course_codes) > 1:
            print(f"   ⚠️  Multiple codes detected - check pattern")

if __name__ == "__main__":
    print("🚀 Starting universality tests for Utah Tech academic content chunking...")
    
    # Run the tests
    asyncio.run(test_department_pages())
    asyncio.run(test_course_code_patterns())
    
    print("\n✅ Universality testing complete!")
