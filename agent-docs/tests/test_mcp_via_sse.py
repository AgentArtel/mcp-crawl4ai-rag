#!/usr/bin/env python3
"""
Test MCP tools via proper SSE connection
Uses the MCP client library to connect to the production server
"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.types import CallToolRequest
import aiohttp

class MCPSSEToolTester:
    """Test MCP tools via proper SSE connection"""
    
    def __init__(self):
        self.base_url = "http://localhost:8051"
        self.session = None
        self.results = {}
        
    async def test_with_sse_client(self):
        """Test tools using proper MCP SSE client"""
        print("🔌 CONNECTING TO MCP SERVER VIA SSE...")
        
        try:
            # Connect to the SSE endpoint
            async with sse_client(f"{self.base_url}/sse") as (read, write):
                async with ClientSession(read, write) as session:
                    print("✅ Connected to MCP server!")
                    
                    # Initialize the session
                    await session.initialize()
                    print("✅ Session initialized!")
                    
                    # List available tools
                    tools_result = await session.list_tools()
                    available_tools = [tool.name for tool in tools_result.tools]
                    print(f"✅ Found {len(available_tools)} available tools")
                    
                    # Test a few key tools
                    test_cases = [
                        ("get_available_sources", {}),
                        ("search_courses", {"query": "psychology"}),
                        ("calculate_credits", {"course_list": "PSYC 1010, BIOL 3450"}),
                        ("create_iap_template", {
                            "student_name": "Test Student",
                            "student_id": "SSE001", 
                            "degree_emphasis": "Psychology"
                        })
                    ]
                    
                    passed = 0
                    failed = 0
                    
                    for tool_name, params in test_cases:
                        if tool_name in available_tools:
                            print(f"\n🧪 Testing {tool_name}...")
                            try:
                                result = await session.call_tool(tool_name, params)
                                if result.isError:
                                    print(f"   ❌ Error: {result.content[0].text}")
                                    failed += 1
                                else:
                                    print(f"   ✅ Success: {result.content[0].text[:100]}...")
                                    passed += 1
                            except Exception as e:
                                print(f"   ❌ Exception: {str(e)}")
                                failed += 1
                        else:
                            print(f"   ❌ Tool {tool_name} not available")
                            failed += 1
                    
                    return passed, failed, available_tools
                    
        except Exception as e:
            print(f"❌ SSE connection failed: {e}")
            return 0, 0, []

    async def test_direct_http(self):
        """Test direct HTTP connection to verify server is responding"""
        print("\n🌐 TESTING DIRECT HTTP CONNECTION...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test SSE endpoint
                async with session.get(f"{self.base_url}/sse") as response:
                    print(f"   SSE endpoint status: {response.status}")
                    if response.status == 200:
                        print("   ✅ SSE endpoint is accessible")
                        return True
                    else:
                        print(f"   ❌ SSE endpoint returned {response.status}")
                        return False
        except Exception as e:
            print(f"   ❌ HTTP connection failed: {e}")
            return False

    async def run_comprehensive_test(self):
        """Run comprehensive MCP tool test"""
        print("🧪 COMPREHENSIVE MCP TOOL TEST VIA SSE")
        print("=" * 50)
        
        # Test 1: Direct HTTP connection
        http_ok = await self.test_direct_http()
        
        if not http_ok:
            print("\n❌ Cannot proceed - HTTP connection failed")
            return False
        
        # Test 2: SSE MCP connection and tools
        passed, failed, available_tools = await self.test_with_sse_client()
        
        print(f"\n📊 RESULTS:")
        print(f"   Available tools: {len(available_tools)}")
        print(f"   Tested tools: {passed + failed}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        
        if len(available_tools) >= 25:  # We expect 27 tools
            print(f"\n✅ EXCELLENT! {len(available_tools)} tools available")
            if passed > 0:
                print("✅ MCP tools are working correctly!")
                return True
            else:
                print("⚠️  Tools available but tests failed")
                return False
        else:
            print(f"\n⚠️  Only {len(available_tools)} tools available (expected ~27)")
            return False

async def main():
    """Run MCP SSE tool tests"""
    tester = MCPSSEToolTester()
    
    try:
        success = await tester.run_comprehensive_test()
        return success
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
