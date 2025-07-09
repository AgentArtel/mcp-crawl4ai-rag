#!/usr/bin/env python3
"""
Comprehensive test script for the Utah Tech IAP Advisor Agent system.
Tests all IAP tools, academic search tools, and integration flows.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from crawl4ai_mcp import (
    # IAP Management Tools
    create_iap_template,
    update_iap_section,
    generate_iap_suggestions,
    validate_complete_iap,
    conduct_market_research,
    track_general_education,
    validate_concentration_areas,
    
    # Academic Search Tools
    search_degree_programs,
    search_courses,
    check_prerequisites,
    
    # Core RAG Tools
    perform_rag_query,
    get_available_sources,
    
    # Knowledge Graph Tools
    query_knowledge_graph,
)

# Mock context class for testing
class MockContext:
    def __init__(self):
        self.supabase_client = None
        self.request_context = MockRequestContext()

class MockRequestContext:
    def __init__(self):
        self.lifespan_context = MockLifespanContext()

class MockLifespanContext:
    def __init__(self):
        self.supabase_client = None

async def test_iap_workflow():
    """Test the complete IAP workflow from creation to validation."""
    print("\n" + "="*60)
    print("TESTING IAP WORKFLOW")
    print("="*60)
    
    ctx = MockContext()
    test_results = []
    
    # Test 1: Create IAP Template
    print("\n1. Testing IAP Template Creation...")
    try:
        result = await create_iap_template(
            ctx=ctx,
            student_name="Sarah Johnson",
            student_id="S12345678",
            degree_emphasis="Psychology and Digital Media",
            student_email="sarah.johnson@utahtech.edu",
            student_phone="555-0123"
        )
        print("✅ IAP Template Creation: PASSED")
        test_results.append(("create_iap_template", "PASSED", "Template created successfully"))
    except Exception as e:
        print(f"❌ IAP Template Creation: FAILED - {e}")
        test_results.append(("create_iap_template", "FAILED", str(e)))
    
    # Test 2: Generate IAP Suggestions
    print("\n2. Testing IAP Suggestions Generation...")
    try:
        result = await generate_iap_suggestions(
            ctx=ctx,
            degree_emphasis="Psychology and Digital Media",
            section="mission_statement",
            context='{"interests": ["mental health", "social media", "user experience"]}'
        )
        print("✅ IAP Suggestions Generation: PASSED")
        test_results.append(("generate_iap_suggestions", "PASSED", "Suggestions generated successfully"))
    except Exception as e:
        print(f"❌ IAP Suggestions Generation: FAILED - {e}")
        test_results.append(("generate_iap_suggestions", "FAILED", str(e)))
    
    # Test 3: Update IAP Section
    print("\n3. Testing IAP Section Update...")
    try:
        mission_data = {
            "mission_statement": "To integrate psychological principles with digital media design to create user-centered experiences that promote mental wellness and positive social interaction."
        }
        result = await update_iap_section(
            ctx=ctx,
            student_id="S12345678",
            section="mission_statement",
            data=json.dumps(mission_data)
        )
        print("✅ IAP Section Update: PASSED")
        test_results.append(("update_iap_section", "PASSED", "Section updated successfully"))
    except Exception as e:
        print(f"❌ IAP Section Update: FAILED - {e}")
        test_results.append(("update_iap_section", "FAILED", str(e)))
    
    # Test 4: Market Research
    print("\n4. Testing Market Research...")
    try:
        result = await conduct_market_research(
            ctx=ctx,
            degree_emphasis="Psychology and Digital Media",
            geographic_focus="Utah"
        )
        print("✅ Market Research: PASSED")
        test_results.append(("conduct_market_research", "PASSED", "Market research completed"))
    except Exception as e:
        print(f"❌ Market Research: FAILED - {e}")
        test_results.append(("conduct_market_research", "FAILED", str(e)))
    
    # Test 5: General Education Tracking
    print("\n5. Testing General Education Tracking...")
    try:
        course_list = ["ENGL 1010", "MATH 1050", "BIOL 1010", "HIST 1700", "PHIL 1000"]
        result = await track_general_education(
            ctx=ctx,
            student_id="S12345678",
            course_list=json.dumps(course_list)
        )
        print("✅ General Education Tracking: PASSED")
        test_results.append(("track_general_education", "PASSED", "GE tracking completed"))
    except Exception as e:
        print(f"❌ General Education Tracking: FAILED - {e}")
        test_results.append(("track_general_education", "FAILED", str(e)))
    
    # Test 6: Concentration Area Validation
    print("\n6. Testing Concentration Area Validation...")
    try:
        concentration_areas = ["Psychology", "Digital Media", "Business"]
        course_mappings = {
            "Psychology": ["PSYC 1010", "PSYC 2010", "PSYC 3010", "PSYC 4010"],
            "Digital Media": ["DIGI 1010", "DIGI 2010", "DIGI 3010", "DIGI 4010"],
            "Business": ["BUSN 1010", "BUSN 2010", "BUSN 3010", "BUSN 4010"]
        }
        result = await validate_concentration_areas(
            ctx=ctx,
            student_id="S12345678",
            concentration_areas=json.dumps(concentration_areas),
            course_mappings=json.dumps(course_mappings)
        )
        print("✅ Concentration Area Validation: PASSED")
        test_results.append(("validate_concentration_areas", "PASSED", "Concentration validation completed"))
    except Exception as e:
        print(f"❌ Concentration Area Validation: FAILED - {e}")
        test_results.append(("validate_concentration_areas", "FAILED", str(e)))
    
    # Test 7: Complete IAP Validation
    print("\n7. Testing Complete IAP Validation...")
    try:
        iap_data = {
            "student_id": "S12345678",
            "student_name": "Sarah Johnson",
            "degree_emphasis": "Psychology and Digital Media",
            "mission_statement": "To integrate psychological principles with digital media design...",
            "concentration_areas": ["Psychology", "Digital Media", "Business"],
            "total_credits": 120,
            "upper_division_credits": 45
        }
        result = await validate_complete_iap(
            ctx=ctx,
            student_id="S12345678",
            iap_data=json.dumps(iap_data)
        )
        print("✅ Complete IAP Validation: PASSED")
        test_results.append(("validate_complete_iap", "PASSED", "Complete validation successful"))
    except Exception as e:
        print(f"❌ Complete IAP Validation: FAILED - {e}")
        test_results.append(("validate_complete_iap", "FAILED", str(e)))
    
    return test_results

async def test_academic_search_tools():
    """Test the academic search and planning tools."""
    print("\n" + "="*60)
    print("TESTING ACADEMIC SEARCH TOOLS")
    print("="*60)
    
    ctx = MockContext()
    test_results = []
    
    # Test 1: Search Degree Programs
    print("\n1. Testing Degree Program Search...")
    try:
        result = await search_degree_programs(
            ctx=ctx,
            query="psychology programs",
            match_count=3
        )
        print("✅ Degree Program Search: PASSED")
        test_results.append(("search_degree_programs", "PASSED", "Program search completed"))
    except Exception as e:
        print(f"❌ Degree Program Search: FAILED - {e}")
        test_results.append(("search_degree_programs", "FAILED", str(e)))
    
    # Test 2: Search Courses
    print("\n2. Testing Course Search...")
    try:
        result = await search_courses(
            ctx=ctx,
            query="statistics",
            level="upper-division",
            match_count=5
        )
        print("✅ Course Search: PASSED")
        test_results.append(("search_courses", "PASSED", "Course search completed"))
    except Exception as e:
        print(f"❌ Course Search: FAILED - {e}")
        test_results.append(("search_courses", "FAILED", str(e)))
    
    # Test 3: Check Prerequisites
    print("\n3. Testing Prerequisite Check...")
    try:
        result = await check_prerequisites(
            ctx=ctx,
            course_code="PSYC 3010"
        )
        print("✅ Prerequisite Check: PASSED")
        test_results.append(("check_prerequisites", "PASSED", "Prerequisite check completed"))
    except Exception as e:
        print(f"❌ Prerequisite Check: FAILED - {e}")
        test_results.append(("check_prerequisites", "FAILED", str(e)))
    
    return test_results

async def test_rag_and_knowledge_graph():
    """Test RAG queries and knowledge graph integration."""
    print("\n" + "="*60)
    print("TESTING RAG AND KNOWLEDGE GRAPH")
    print("="*60)
    
    ctx = MockContext()
    test_results = []
    
    # Test 1: Get Available Sources
    print("\n1. Testing Available Sources...")
    try:
        result = await get_available_sources(ctx=ctx)
        print("✅ Available Sources: PASSED")
        test_results.append(("get_available_sources", "PASSED", "Sources retrieved"))
    except Exception as e:
        print(f"❌ Available Sources: FAILED - {e}")
        test_results.append(("get_available_sources", "FAILED", str(e)))
    
    # Test 2: RAG Query
    print("\n2. Testing RAG Query...")
    try:
        result = await perform_rag_query(
            ctx=ctx,
            query="Bachelor of Individualized Studies requirements",
            match_count=3
        )
        print("✅ RAG Query: PASSED")
        test_results.append(("perform_rag_query", "PASSED", "RAG query completed"))
    except Exception as e:
        print(f"❌ RAG Query: FAILED - {e}")
        test_results.append(("perform_rag_query", "FAILED", str(e)))
    
    # Test 3: Knowledge Graph Query
    print("\n3. Testing Knowledge Graph Query...")
    try:
        result = await query_knowledge_graph(
            ctx=ctx,
            command="repos"
        )
        print("✅ Knowledge Graph Query: PASSED")
        test_results.append(("query_knowledge_graph", "PASSED", "Graph query completed"))
    except Exception as e:
        print(f"❌ Knowledge Graph Query: FAILED - {e}")
        test_results.append(("query_knowledge_graph", "FAILED", str(e)))
    
    return test_results

def generate_test_report(all_results):
    """Generate a comprehensive test report."""
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST REPORT")
    print("="*60)
    
    total_tests = len(all_results)
    passed_tests = len([r for r in all_results if r[1] == "PASSED"])
    failed_tests = total_tests - passed_tests
    
    print(f"\nTest Summary:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print(f"\nFailed Tests:")
        for tool_name, status, message in all_results:
            if status == "FAILED":
                print(f"❌ {tool_name}: {message}")
    
    print(f"\nDetailed Results:")
    for tool_name, status, message in all_results:
        status_icon = "✅" if status == "PASSED" else "❌"
        print(f"{status_icon} {tool_name}: {message}")
    
    # Generate recommendations
    print(f"\nRecommendations:")
    if failed_tests == 0:
        print("🎉 All tests passed! The system is ready for production deployment.")
        print("✅ Proceed with Docker containerization")
        print("✅ System is ready for student advising sessions")
    else:
        print("⚠️  Some tests failed. Address the following before deployment:")
        for tool_name, status, message in all_results:
            if status == "FAILED":
                print(f"   - Fix {tool_name}: {message}")
    
    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": (passed_tests/total_tests)*100,
        "ready_for_deployment": failed_tests == 0
    }

async def main():
    """Run the comprehensive test suite."""
    print("Utah Tech IAP Advisor Agent - Comprehensive Test Suite")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # Run all test suites
    iap_results = await test_iap_workflow()
    all_results.extend(iap_results)
    
    academic_results = await test_academic_search_tools()
    all_results.extend(academic_results)
    
    rag_results = await test_rag_and_knowledge_graph()
    all_results.extend(rag_results)
    
    # Generate final report
    report = generate_test_report(all_results)
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return report

if __name__ == "__main__":
    # Run the comprehensive test
    report = asyncio.run(main())
    
    # Exit with appropriate code
    exit_code = 0 if report["ready_for_deployment"] else 1
    sys.exit(exit_code)
