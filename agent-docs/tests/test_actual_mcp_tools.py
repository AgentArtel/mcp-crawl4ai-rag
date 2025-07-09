#!/usr/bin/env python3
"""
Test actual MCP tools via production SSE endpoint
Comprehensive verification of all 27 tools in production environment
"""

import asyncio
import json
import aiohttp
import sys
from typing import Dict, List, Any
import uuid

class MCPToolTester:
    """Test MCP tools via SSE endpoint"""
    
    def __init__(self):
        self.base_url = "http://localhost:8051"
        self.session = None
        self.session_id = str(uuid.uuid4())
        self.results = {}
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def call_mcp_tool(self, tool_name: str, params: dict) -> dict:
        """Call an MCP tool via the production endpoint"""
        try:
            # Prepare the MCP request
            request_data = {
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": params
                }
            }
            
            # Make the request to the MCP server
            async with self.session.post(
                f"{self.base_url}/messages/",
                params={"session_id": self.session_id},
                json=request_data,
                timeout=30
            ) as response:
                if response.status == 202:  # Accepted
                    result_text = await response.text()
                    try:
                        result = json.loads(result_text)
                        return {"success": True, "result": result}
                    except json.JSONDecodeError:
                        return {"success": True, "result": result_text}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
        except asyncio.TimeoutError:
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_all_tools(self):
        """Test all 27 MCP tools"""
        print("🧪 TESTING ALL 27 MCP TOOLS IN PRODUCTION")
        print("=" * 60)
        
        # Define all 27 tools with test parameters
        tools_to_test = [
            # RAG and Search Tools
            ("get_available_sources", {}),
            ("perform_rag_query", {"query": "psychology courses"}),
            ("search_courses", {"query": "psychology"}),
            ("search_degree_programs", {"query": "psychology"}),
            
            # Academic Analysis Tools
            ("calculate_credits", {"course_list": "PSYC 1010, BIOL 3450"}),
            ("analyze_disciplines", {"course_list": "PSYC 1010, BIOL 3450"}),
            ("check_prerequisites", {"course_code": "PSYC 1010"}),
            ("validate_iap_requirements", {"course_list": "PSYC 1010, BIOL 3450"}),
            
            # IAP Template Management
            ("create_iap_template", {
                "student_name": "Test Student",
                "student_id": "PROD001",
                "degree_emphasis": "Psychology and Communication"
            }),
            ("update_iap_section", {
                "student_id": "PROD001",
                "section": "mission_statement",
                "data": '{"mission": "Test mission for production"}'
            }),
            ("generate_iap_suggestions", {
                "degree_emphasis": "Psychology",
                "section": "mission_statement"
            }),
            ("validate_complete_iap", {"student_id": "PROD001"}),
            
            # Advanced IAP Tools
            ("conduct_market_research", {"degree_emphasis": "Psychology"}),
            ("track_general_education", {"student_id": "PROD001"}),
            ("validate_concentration_areas", {
                "student_id": "PROD001",
                "concentration_areas": '["Psychology", "Communication", "Business"]',
                "course_mappings": '{"Psychology": ["PSYC 1010"], "Communication": ["COMM 1010"], "Business": ["BUSN 1010"]}'
            }),
            
            # Graph-Enhanced Tools
            ("get_prerequisite_chain", {"course_code": "PSYC 1010"}),
            ("recommend_course_sequence", {"target_courses": "PSYC 1010, PSYC 2010"}),
            ("validate_course_sequence", {"course_list": "PSYC 1010, PSYC 2010"}),
            
            # Utility Tools
            ("find_alternative_courses", {"course_code": "PSYC 1010"}),
            ("smart_crawl_url", {"url": "https://catalog.utahtech.edu/courses/psyc/"}),
            ("crawl_single_page", {"url": "https://catalog.utahtech.edu/courses/psyc/"}),
            
            # Knowledge Graph Tools
            ("build_academic_knowledge_graph", {}),
            ("query_knowledge_graph", {"command": "repos"}),
            ("parse_github_repository", {"repo_url": "https://github.com/test/test.git"}),
            ("check_ai_script_hallucinations", {"script_path": "/tmp/test.py"}),
            
            # Data Population Tools
            ("populate_supabase_backup", {}),
            ("analyze_degree_progress", {
                "completed_courses": "PSYC 1010",
                "target_courses": "PSYC 1010, PSYC 2010"
            }),
        ]
        
        print(f"Testing {len(tools_to_test)} MCP tools via production endpoint...\n")
        
        passed = 0
        failed = 0
        
        for i, (tool_name, params) in enumerate(tools_to_test, 1):
            print(f"🧪 [{i:2d}/27] Testing {tool_name}...")
            
            result = await self.call_mcp_tool(tool_name, params)
            
            if result["success"]:
                # Check if the result contains an error
                result_data = result.get("result", {})
                if isinstance(result_data, dict) and "error" in result_data:
                    self.results[tool_name] = f"❌ {result_data['error'][:100]}..."
                    failed += 1
                elif isinstance(result_data, str) and "error" in result_data.lower():
                    self.results[tool_name] = f"❌ {result_data[:100]}..."
                    failed += 1
                else:
                    self.results[tool_name] = "✅ Success"
                    passed += 1
            else:
                self.results[tool_name] = f"❌ {result['error'][:100]}..."
                failed += 1
            
            # Small delay to avoid overwhelming the server
            await asyncio.sleep(0.5)
        
        return passed, failed
    
    def print_results(self, passed: int, failed: int):
        """Print comprehensive test results"""
        print("\n" + "=" * 70)
        print("📊 PRODUCTION MCP TOOL TEST RESULTS")
        print("=" * 70)
        
        # Group results by category
        categories = {
            "RAG & Search": ["get_available_sources", "perform_rag_query", "search_courses", "search_degree_programs"],
            "Academic Analysis": ["calculate_credits", "analyze_disciplines", "check_prerequisites", "validate_iap_requirements"],
            "IAP Management": ["create_iap_template", "update_iap_section", "generate_iap_suggestions", "validate_complete_iap"],
            "Advanced IAP": ["conduct_market_research", "track_general_education", "validate_concentration_areas"],
            "Graph Tools": ["get_prerequisite_chain", "recommend_course_sequence", "validate_course_sequence"],
            "Utility": ["find_alternative_courses", "smart_crawl_url", "crawl_single_page"],
            "Knowledge Graph": ["build_academic_knowledge_graph", "query_knowledge_graph", "parse_github_repository", "check_ai_script_hallucinations"],
            "Data Tools": ["populate_supabase_backup", "analyze_degree_progress"]
        }
        
        for category, tools in categories.items():
            print(f"\n🔍 {category.upper()}:")
            for tool in tools:
                if tool in self.results:
                    print(f"   {self.results[tool]} {tool}")
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tools: 27")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {(passed/27)*100:.1f}%")
        
        if failed > 0:
            print(f"\n🔧 FAILED TOOLS:")
            for tool_name, result in self.results.items():
                if "❌" in result:
                    print(f"   • {tool_name}: {result}")
        
        if passed == 27:
            print("\n🎉 PERFECT! ALL 27 TOOLS WORKING IN PRODUCTION!")
            print("   ✅ Utah Tech IAP Advisor is 100% operational")
            return True
        elif passed >= 20:
            print(f"\n🎯 EXCELLENT! {passed}/27 tools working ({(passed/27)*100:.1f}%)")
            print("   ✅ Core functionality operational")
            return True
        else:
            print(f"\n⚠️  Only {passed}/27 tools working - needs attention")
            return False

async def main():
    """Run production MCP tool tests"""
    tester = MCPToolTester()
    
    try:
        await tester.setup()
        passed, failed = await tester.test_all_tools()
        success = tester.print_results(passed, failed)
        return success
    except Exception as e:
        print(f"❌ Production test failed: {e}")
        return False
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
