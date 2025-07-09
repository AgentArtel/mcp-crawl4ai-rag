#!/usr/bin/env python3
"""
Test script for the new academic tools in the Utah Tech MCP server.
Tests search_degree_programs, search_courses, and validate_iap_requirements tools.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from crawl4ai_mcp import (
    search_degree_programs,
    search_courses, 
    validate_iap_requirements,
    calculate_credits,
    check_prerequisites,
    analyze_disciplines,
    get_available_sources
)
from utils import get_supabase_client
from mcp.server.fastmcp import Context
from types import SimpleNamespace

class MockContext:
    """Mock context for testing MCP tools"""
    def __init__(self):
        self.request_context = SimpleNamespace()
        self.request_context.lifespan_context = SimpleNamespace()
        self.request_context.lifespan_context.supabase_client = get_supabase_client()
        self.request_context.lifespan_context.reranking_model = None

async def test_get_available_sources():
    """Test getting available sources"""
    print("🔍 Testing get_available_sources...")
    try:
        ctx = MockContext()
        result = await get_available_sources(ctx)
        result_data = json.loads(result)
        
        if result_data.get("success"):
            sources = result_data.get("sources", [])
            print(f"✅ Found {len(sources)} sources:")
            for source in sources[:3]:  # Show first 3
                print(f"   - {source.get('source_id', 'Unknown')}: {source.get('summary', 'No summary')[:100]}...")
            return sources
        else:
            print(f"❌ Failed: {result_data.get('error', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []

async def test_search_degree_programs():
    """Test the search_degree_programs tool"""
    print("\n🎓 Testing search_degree_programs...")
    
    test_queries = [
        ("psychology programs", None),
        ("business degrees", "catalog.utahtech.edu"),
        ("art bachelor", "catalog.utahtech.edu")
    ]
    
    ctx = MockContext()
    
    for query, source_id in test_queries:
        print(f"\n   Query: '{query}' (source: {source_id or 'any'})")
        try:
            result = await search_degree_programs(ctx, query, source_id=source_id, match_count=3)
            result_data = json.loads(result)
            
            if result_data.get("success"):
                results = result_data.get("results", [])
                print(f"   ✅ Found {len(results)} results")
                for i, res in enumerate(results[:2]):  # Show first 2
                    content_preview = res.get("content", "")[:150].replace("\n", " ")
                    similarity = res.get("similarity", 0)
                    print(f"      {i+1}. Similarity: {similarity:.3f}")
                    print(f"         Content: {content_preview}...")
                    print(f"         URL: {res.get('url', 'No URL')}")
            else:
                print(f"   ❌ Failed: {result_data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

async def test_search_courses():
    """Test the search_courses tool"""
    print("\n📚 Testing search_courses...")
    
    test_queries = [
        ("statistics", None, None),
        ("biology lab", "upper-division", None),
        ("psychology", None, "PSYC"),
        ("writing intensive", "lower-division", None)
    ]
    
    ctx = MockContext()
    
    for query, level, department in test_queries:
        filters = []
        if level:
            filters.append(f"level={level}")
        if department:
            filters.append(f"dept={department}")
        filter_str = f" ({', '.join(filters)})" if filters else ""
        
        print(f"\n   Query: '{query}'{filter_str}")
        try:
            result = await search_courses(
                ctx, 
                query, 
                level=level, 
                department=department, 
                source_id="catalog.utahtech.edu",
                match_count=3
            )
            result_data = json.loads(result)
            
            if result_data.get("success"):
                results = result_data.get("results", [])
                print(f"   ✅ Found {len(results)} results")
                for i, res in enumerate(results[:2]):  # Show first 2
                    content_preview = res.get("content", "")[:150].replace("\n", " ")
                    similarity = res.get("similarity", 0)
                    print(f"      {i+1}. Similarity: {similarity:.3f}")
                    print(f"         Content: {content_preview}...")
                    
                    # Try to extract course codes from content
                    import re
                    course_codes = re.findall(r'\b[A-Z]{2,4}\s+\d{4}\b', res.get("content", ""))
                    if course_codes:
                        print(f"         Courses found: {', '.join(course_codes[:3])}")
            else:
                print(f"   ❌ Failed: {result_data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

async def test_validate_iap_requirements():
    """Test the validate_iap_requirements tool"""
    print("\n✅ Testing validate_iap_requirements...")
    
    test_cases = [
        ("PSYC 1010, BIOL 3450, BUSN 4200", "Health Psychology"),
        ("ART 1010, ART 2020, ART 3030", "Digital Arts"),
        ("MATH 1050, STAT 2040, CS 1400", None)
    ]
    
    ctx = MockContext()
    
    for course_list, emphasis_title in test_cases:
        print(f"\n   Courses: {course_list}")
        print(f"   Emphasis: {emphasis_title or 'None'}")
        try:
            result = await validate_iap_requirements(
                ctx, 
                course_list, 
                emphasis_title=emphasis_title,
                source_id="catalog.utahtech.edu"
            )
            result_data = json.loads(result)
            
            if result_data.get("success"):
                validation = result_data.get("validation_results", {})
                courses_analyzed = validation.get("courses_analyzed", [])
                course_count = validation.get("course_count", 0)
                
                print(f"   ✅ Analyzed {course_count} courses: {', '.join(courses_analyzed)}")
                
                # Show requirements info
                req_info = validation.get("requirements_info", [])
                if req_info:
                    print(f"   📋 Found {len(req_info)} requirement references")
                
                # Show course details
                course_details = validation.get("course_details", [])
                for detail in course_details[:2]:  # Show first 2
                    course_code = detail.get("course_code", "Unknown")
                    search_results = detail.get("search_results", [])
                    print(f"      {course_code}: {len(search_results)} matches found")
                
                # Show title conflicts
                title_conflicts = validation.get("title_conflicts", [])
                if title_conflicts and emphasis_title:
                    print(f"   ⚠️  Found {len(title_conflicts)} potential title conflicts for '{emphasis_title}'")
                
                # Show validation notes
                notes = validation.get("validation_notes", [])
                for note in notes:
                    print(f"   📝 {note}")
                    
            else:
                print(f"   ❌ Failed: {result_data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

async def test_calculate_credits():
    """Test the calculate_credits tool"""
    print("\n💰 Testing calculate_credits...")
    
    test_cases = [
        "PSYC 1010, BIOL 3450, BUSN 4200",
        "ART 1010, ART 2020, ART 3030, ART 4040",
        "MATH 1050, STAT 2040, CS 1400, CS 3400, CS 4600"
    ]
    
    ctx = MockContext()
    
    for course_list in test_cases:
        print(f"\n   Courses: {course_list}")
        try:
            result = await calculate_credits(
                ctx, 
                course_list, 
                source_id="catalog.utahtech.edu"
            )
            result_data = json.loads(result)
            
            if result_data.get("success"):
                analysis = result_data.get("analysis", {})
                total_courses = analysis.get("total_courses", 0)
                total_credits = analysis.get("total_credits", 0)
                upper_credits = analysis.get("upper_division_credits", 0)
                lower_credits = analysis.get("lower_division_credits", 0)
                
                print(f"   ✅ Analyzed {total_courses} courses")
                print(f"      Total Credits: {total_credits}")
                print(f"      Upper Division: {upper_credits} credits")
                print(f"      Lower Division: {lower_credits} credits")
                
                # Show requirement compliance
                meets_120 = analysis.get("meets_120_credit_requirement", False)
                meets_40_upper = analysis.get("meets_40_upper_division_requirement", False)
                print(f"      120 Credit Requirement: {'✅' if meets_120 else '❌'}")
                print(f"      40 Upper-Division Requirement: {'✅' if meets_40_upper else '❌'}")
                
                # Show recommendations
                recommendations = analysis.get("recommendations", [])
                for rec in recommendations[:2]:  # Show first 2
                    print(f"      💡 {rec}")
                    
            else:
                print(f"   ❌ Failed: {result_data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

async def test_check_prerequisites():
    """Test the check_prerequisites tool"""
    print("\n🔗 Testing check_prerequisites...")
    
    test_courses = [
        "BIOL 3450",
        "CS 3400", 
        "PSYC 1010",
        "MATH 1210"
    ]
    
    ctx = MockContext()
    
    for course_code in test_courses:
        print(f"\n   Course: {course_code}")
        try:
            result = await check_prerequisites(
                ctx, 
                course_code, 
                source_id="catalog.utahtech.edu"
            )
            result_data = json.loads(result)
            
            if result_data.get("success"):
                analysis = result_data.get("analysis", {})
                has_prereqs = analysis.get("has_prerequisites", False)
                prereq_count = analysis.get("prerequisite_count", 0)
                complexity = analysis.get("complexity_level", "unknown")
                
                print(f"   ✅ Prerequisites: {'Yes' if has_prereqs else 'None found'}")
                if has_prereqs:
                    print(f"      Count: {prereq_count} prerequisites")
                    print(f"      Complexity: {complexity}")
                    
                    prereqs_found = analysis.get("prerequisites_found", [])
                    if prereqs_found:
                        print(f"      Required: {', '.join(prereqs_found)}")
                
                # Show course description snippet
                description = analysis.get("course_description_snippet", "")
                if description:
                    desc_preview = description[:100].replace("\n", " ")
                    print(f"      Description: {desc_preview}...")
                    
            else:
                print(f"   ❌ Failed: {result_data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

async def test_analyze_disciplines():
    """Test the analyze_disciplines tool"""
    print("\n🎯 Testing analyze_disciplines...")
    
    test_cases = [
        ("PSYC 1010, BIOL 3450, BUSN 4200", "3 different disciplines"),
        ("ART 1010, ART 2020, ART 3030", "1 discipline only"),
        ("MATH 1050, STAT 2040, CS 1400, PSYC 1010, BIOL 1610", "5 different disciplines")
    ]
    
    ctx = MockContext()
    
    for course_list, description in test_cases:
        print(f"\n   Test: {description}")
        print(f"   Courses: {course_list}")
        try:
            result = await analyze_disciplines(
                ctx, 
                course_list, 
                source_id="catalog.utahtech.edu"
            )
            result_data = json.loads(result)
            
            if result_data.get("success"):
                analysis = result_data.get("analysis", {})
                total_courses = analysis.get("total_courses", 0)
                total_disciplines = analysis.get("total_disciplines", 0)
                meets_requirement = analysis.get("meets_three_discipline_requirement", False)
                
                print(f"   ✅ Analyzed {total_courses} courses")
                print(f"      Disciplines Found: {total_disciplines}")
                print(f"      3+ Discipline Requirement: {'✅' if meets_requirement else '❌'}")
                
                # Show discipline distribution
                discipline_dist = analysis.get("discipline_distribution", {})
                print(f"      Distribution:")
                for prefix, info in list(discipline_dist.items())[:4]:  # Show first 4
                    discipline_name = info.get("discipline_name", prefix)
                    course_count = info.get("course_count", 0)
                    courses = info.get("courses", [])
                    print(f"        {prefix} ({discipline_name}): {course_count} courses - {', '.join(courses)}")
                
                # Show recommendations
                recommendations = analysis.get("recommendations", [])
                for rec in recommendations[:2]:  # Show first 2
                    print(f"      💡 {rec}")
                    
            else:
                print(f"   ❌ Failed: {result_data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

async def main():
    """Run all tests"""
    print("🧪 Testing Utah Tech MCP Academic Tools")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running tests.")
        return
    
    print("✅ Environment variables found")
    
    # Test each tool
    sources = await test_get_available_sources()
    
    if not sources:
        print("\n⚠️  No sources found. Make sure you have crawled some academic content first.")
        print("You can test the tools anyway, but results may be limited.")
    
    await test_search_degree_programs()
    await test_search_courses()
    await test_validate_iap_requirements()
    await test_calculate_credits()
    await test_check_prerequisites()
    await test_analyze_disciplines()
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    print("\nNext steps:")
    print("1. If all tests passed, rebuild the Docker container")
    print("2. If any tests failed, check the error messages and fix issues")
    print("3. Test the tools via MCP client once Docker is running")

if __name__ == "__main__":
    asyncio.run(main())
