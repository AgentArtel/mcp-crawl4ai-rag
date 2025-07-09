#!/usr/bin/env python3
"""
Individual MCP tool testing to identify specific failures
"""

import sys
import os
import asyncio
import json
from typing import Dict, List, Any
sys.path.append('src')

# Import all required modules
from utils import get_supabase_client
from crawl4ai_mcp import *

class MockContext:
    """Mock context for MCP tool testing"""
    def __init__(self):
        self.supabase_client = get_supabase_client()
        self.repo_extractor = None
        # Add request_context for FastMCP compatibility
        self.request_context = {}
        # Add session for compatibility
        self.session = None

async def test_individual_tools():
    """Test each MCP tool individually to identify failures"""
    print("🔍 INDIVIDUAL MCP TOOL TESTING")
    print("="*50)
    
    ctx = MockContext()
    results = {}
    
    # List of all 27 MCP tools to test
    tools_to_test = [
        # RAG and Search Tools
        ("get_available_sources", get_available_sources, {}),
        ("perform_rag_query", perform_rag_query, {"query": "psychology courses"}),
        ("search_courses", search_courses, {"query": "psychology"}),
        ("search_degree_programs", search_degree_programs, {"query": "psychology"}),
        
        # Academic Analysis Tools
        ("calculate_credits", calculate_credits, {"course_list": "PSYC 1010, BIOL 3450"}),
        ("analyze_disciplines", analyze_disciplines, {"course_list": "PSYC 1010, BIOL 3450"}),
        ("check_prerequisites", check_prerequisites, {"course_code": "PSYC 1010"}),
        ("validate_iap_requirements", validate_iap_requirements, {"course_list": "PSYC 1010, BIOL 3450"}),
        
        # IAP Template Management
        ("create_iap_template", create_iap_template, {
            "student_name": "Test Student",
            "student_id": "TEST001",
            "degree_emphasis": "Psychology and Communication"
        }),
        ("update_iap_section", update_iap_section, {
            "student_id": "TEST001",
            "section": "mission_statement",
            "data": '{"mission": "Test mission"}'
        }),
        ("generate_iap_suggestions", generate_iap_suggestions, {
            "degree_emphasis": "Psychology",
            "section": "mission_statement"
        }),
        ("validate_complete_iap", validate_complete_iap, {"student_id": "TEST001"}),
        
        # Advanced IAP Tools
        ("conduct_market_research", conduct_market_research, {"degree_emphasis": "Psychology"}),
        ("track_general_education", track_general_education, {"student_id": "TEST001"}),
        ("validate_concentration_areas", validate_concentration_areas, {
            "student_id": "TEST001",
            "concentration_areas": '["Psychology", "Communication", "Business"]',
            "course_mappings": '{"Psychology": ["PSYC 1010"], "Communication": ["COMM 1010"], "Business": ["BUSN 1010"]}'
        }),
        
        # Graph-Enhanced Tools (may fail if Neo4j not available)
        ("get_prerequisite_chain", get_prerequisite_chain, {"course_code": "PSYC 1010"}),
        ("recommend_course_sequence", recommend_course_sequence, {"target_courses": "PSYC 1010, PSYC 2010"}),
        ("validate_course_sequence", validate_course_sequence, {"course_list": "PSYC 1010, PSYC 2010"}),
        
        # Utility Tools
        ("find_alternative_courses", find_alternative_courses, {"course_code": "PSYC 1010"}),
        ("smart_crawl_url", smart_crawl_url, {"url": "https://catalog.utahtech.edu/courses/psyc/"}),
        ("crawl_single_page", crawl_single_page, {"url": "https://catalog.utahtech.edu/courses/psyc/"}),
        
        # Knowledge Graph Tools (may fail if Neo4j not available)
        ("build_academic_knowledge_graph", build_academic_knowledge_graph, {}),
        ("query_knowledge_graph", query_knowledge_graph, {"command": "repos"}),
        ("parse_github_repository", parse_github_repository, {"repo_url": "https://github.com/test/test.git"}),
        ("check_ai_script_hallucinations", check_ai_script_hallucinations, {"script_path": "/tmp/test.py"}),
        
        # Data Population Tools
        ("populate_supabase_backup", populate_supabase_backup, {}),
        ("analyze_degree_progress", analyze_degree_progress, {
            "completed_courses": "PSYC 1010",
            "target_courses": "PSYC 1010, PSYC 2010"
        }),
    ]
    
    print(f"Testing {len(tools_to_test)} MCP tools...\n")
    
    for tool_name, tool_func, params in tools_to_test:
        try:
            print(f"🧪 Testing {tool_name}...")
            
            # Call the tool function
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(ctx, **params)
            else:
                result = tool_func(ctx, **params)
            
            # Parse result if it's JSON
            if isinstance(result, str):
                try:
                    parsed_result = json.loads(result)
                    if "error" in parsed_result:
                        results[tool_name] = f"❌ {parsed_result['error']}"
                    else:
                        results[tool_name] = "✅ Success"
                except json.JSONDecodeError:
                    results[tool_name] = "✅ Success (non-JSON response)"
            else:
                results[tool_name] = "✅ Success"
                
        except Exception as e:
            results[tool_name] = f"❌ Exception: {str(e)[:100]}..."
    
    # Print results
    print("\n" + "="*60)
    print("📊 INDIVIDUAL TOOL TEST RESULTS")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for tool_name, result in results.items():
        print(f"{result} {tool_name}")
        if "✅" in result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 SUMMARY:")
    print(f"  Total Tools: {len(tools_to_test)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Success Rate: {(passed/len(tools_to_test))*100:.1f}%")
    
    if failed > 0:
        print(f"\n🔧 FAILED TOOLS ANALYSIS:")
        for tool_name, result in results.items():
            if "❌" in result:
                print(f"  • {tool_name}: {result}")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(test_individual_tools())
    sys.exit(0 if success else 1)
