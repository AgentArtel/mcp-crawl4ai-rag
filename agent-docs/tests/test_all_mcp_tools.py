#!/usr/bin/env python3
"""
Comprehensive test suite for all MCP tools before Docker rebuild
Tests all tool dependencies, method access, and basic functionality
"""

import sys
import os
import asyncio
import json
from typing import Dict, List, Any
sys.path.append('src')

# Import all required modules
from academic_graph_builder import AcademicGraphBuilder
from iap_tools import IAPManager
from utils import get_supabase_client
from crawl4ai_mcp import *

class MCPToolTester:
    """Comprehensive MCP tool testing suite"""
    
    def __init__(self):
        self.results = {}
        self.supabase = None
        self.neo4j_driver = None
        self.builder = None
        self.iap_manager = None
        
    async def setup(self):
        """Initialize all components"""
        print("🔧 Setting up test environment...")
        try:
            self.supabase = get_supabase_client()
            print("✅ Supabase client initialized")
            
            # Neo4j driver will be accessed through AcademicGraphBuilder
            print("✅ Neo4j will be accessed through AcademicGraphBuilder")
            
            self.builder = AcademicGraphBuilder()
            print("✅ AcademicGraphBuilder initialized")
            
            self.iap_manager = IAPManager(self.supabase)
            print("✅ IAPManager initialized")
            
            return True
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    def test_supabase_tables(self):
        """Test access to all required Supabase tables"""
        print("\n📋 Testing Supabase table access...")
        
        required_tables = [
            'crawled_pages', 'sources', 'academic_departments', 
            'academic_courses', 'academic_programs', 'iap_templates',
            'iap_general_education', 'iap_market_research', 
            'iap_concentration_validation', 'iap_course_plo_mappings'
        ]
        
        results = {}
        for table in required_tables:
            try:
                response = self.supabase.table(table).select("*").limit(1).execute()
                results[table] = "✅ Accessible"
                print(f"  ✅ {table}")
            except Exception as e:
                results[table] = f"❌ Error: {e}"
                print(f"  ❌ {table}: {e}")
        
        self.results['supabase_tables'] = results
        return all("✅" in result for result in results.values())
    
    def test_neo4j_connection(self):
        """Test Neo4j connection and basic queries"""
        print("\n📋 Testing Neo4j connection...")
        
        try:
            with self.builder.neo4j_driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                if record and record["test"] == 1:
                    print("  ✅ Neo4j connection working")
                    
                    # Test academic nodes exist
                    course_count = session.run("MATCH (c:Course) RETURN count(c) as count").single()["count"]
                    program_count = session.run("MATCH (p:Program) RETURN count(p) as count").single()["count"]
                    dept_count = session.run("MATCH (d:Department) RETURN count(d) as count").single()["count"]
                    
                    print(f"  📊 Neo4j data: {course_count} courses, {program_count} programs, {dept_count} departments")
                    
                    self.results['neo4j'] = {
                        'connection': '✅ Working',
                        'courses': course_count,
                        'programs': program_count,
                        'departments': dept_count
                    }
                    return True
                else:
                    print("  ❌ Neo4j test query failed")
                    return False
        except Exception as e:
            error_msg = str(e)
            if "Cannot resolve address host.docker.internal" in error_msg:
                print("  ⚠️  Neo4j connection failed (Docker networking issue - expected in local testing)")
                print("  💡 Neo4j will work correctly when running inside Docker container")
                self.results['neo4j'] = '⚠️ Docker networking issue (expected in local testing)'
                return True  # Don't fail the test for Docker networking issues
            else:
                print(f"  ❌ Neo4j connection failed: {e}")
                self.results['neo4j'] = f"❌ Error: {e}"
                return False
    
    async def test_academic_tools(self):
        """Test academic planning tools"""
        print("\n📋 Testing academic planning tools...")
        
        tools_to_test = [
            ('_extract_academic_data', 'Academic data extraction'),
            ('_populate_supabase_tables', 'Supabase population'),
            ('build_academic_graph', 'Graph building')
        ]
        
        results = {}
        for method_name, description in tools_to_test:
            try:
                if hasattr(self.builder, method_name):
                    if callable(getattr(self.builder, method_name)):
                        results[method_name] = f"✅ {description} method available"
                        print(f"  ✅ {description}")
                    else:
                        results[method_name] = f"❌ {description} method not callable"
                        print(f"  ❌ {description} method not callable")
                else:
                    results[method_name] = f"❌ {description} method missing"
                    print(f"  ❌ {description} method missing")
            except Exception as e:
                results[method_name] = f"❌ Error: {e}"
                print(f"  ❌ {description}: {e}")
        
        self.results['academic_tools'] = results
        return all("✅" in result for result in results.values())
    
    def test_iap_tools(self):
        """Test IAP management tools"""
        print("\n📋 Testing IAP management tools...")
        
        iap_methods = [
            ('create_iap_template', 'IAP template creation'),
            ('update_iap_section', 'IAP section updates'),
            ('validate_iap_requirements', 'Complete IAP validation'),
            ('track_general_education', 'General education tracking'),
            ('validate_concentration_areas', 'Concentration validation'),
            ('conduct_market_research', 'Market research'),
            ('generate_iap_suggestions', 'AI suggestions')
        ]
        
        results = {}
        for method_name, description in iap_methods:
            try:
                if hasattr(self.iap_manager, method_name):
                    results[method_name] = f"✅ {description} available"
                    print(f"  ✅ {description}")
                else:
                    results[method_name] = f"❌ {description} missing"
                    print(f"  ❌ {description} missing")
            except Exception as e:
                results[method_name] = f"❌ Error: {e}"
                print(f"  ❌ {description}: {e}")
        
        self.results['iap_tools'] = results
        return all("✅" in result for result in results.values())
    
    def test_crawled_content(self):
        """Test crawled content availability"""
        print("\n📋 Testing crawled content...")
        
        try:
            # Check for Utah Tech catalog content
            response = self.supabase.table("crawled_pages").select("*").eq(
                "source_id", "catalog.utahtech.edu"
            ).limit(5).execute()
            
            if response.data:
                page_count = len(response.data)
                print(f"  ✅ Found {page_count} sample crawled pages")
                
                # Get total count
                total_response = self.supabase.table("crawled_pages").select("*", count="exact").eq(
                    "source_id", "catalog.utahtech.edu"
                ).execute()
                
                total_count = total_response.count if hasattr(total_response, 'count') else 'Unknown'
                print(f"  📊 Total crawled pages: {total_count}")
                
                self.results['crawled_content'] = {
                    'status': '✅ Available',
                    'sample_count': page_count,
                    'total_count': str(total_count)  # Convert to string to avoid type issues
                }
                return True
            else:
                print("  ❌ No crawled content found")
                self.results['crawled_content'] = '❌ No content found'
                return False
                
        except Exception as e:
            print(f"  ❌ Error checking crawled content: {e}")
            self.results['crawled_content'] = f"❌ Error: {e}"
            return False
    
    async def test_data_extraction(self):
        """Test actual data extraction"""
        print("\n📋 Testing data extraction...")
        
        try:
            academic_data = await self.builder._extract_academic_data()
            
            if academic_data:
                courses = academic_data.get('courses', {})
                programs = academic_data.get('programs', {})
                departments = academic_data.get('departments', {})
                
                print(f"  ✅ Extracted: {len(courses)} courses, {len(programs)} programs, {len(departments)} departments")
                
                self.results['data_extraction'] = {
                    'status': '✅ Working',
                    'courses': len(courses),
                    'programs': len(programs),
                    'departments': len(departments)
                }
                return True
            else:
                print("  ❌ No data extracted")
                self.results['data_extraction'] = '❌ No data extracted'
                return False
                
        except Exception as e:
            print(f"  ❌ Data extraction failed: {e}")
            self.results['data_extraction'] = f"❌ Error: {e}"
            return False
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.builder:
                self.builder.close()
            # Neo4j driver cleanup handled by AcademicGraphBuilder
            print("🧹 Cleanup completed")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE MCP TOOL TEST SUMMARY")
        print("="*60)
        
        total_tests = 0
        passed_tests = 0
        
        for category, results in self.results.items():
            print(f"\n🔍 {category.upper().replace('_', ' ')}:")
            
            if isinstance(results, dict):
                for test_name, result in results.items():
                    print(f"  {result}")
                    total_tests += 1
                    if "✅" in str(result):  # Convert to string to handle mixed types
                        passed_tests += 1
            else:
                print(f"  {results}")
                total_tests += 1
                if "✅" in str(results):  # Convert to string to handle mixed types
                    passed_tests += 1
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED - Ready for Docker rebuild!")
            return True
        else:
            print(f"\n💥 {total_tests - passed_tests} TESTS FAILED - Fix issues before Docker rebuild!")
            return False

async def main():
    """Run comprehensive MCP tool tests"""
    print("🧪 COMPREHENSIVE MCP TOOL TEST SUITE")
    print("="*50)
    
    tester = MCPToolTester()
    
    try:
        # Setup
        if not await tester.setup():
            print("❌ Setup failed - cannot continue tests")
            return False
        
        # Run all tests
        tests = [
            tester.test_supabase_tables(),
            tester.test_neo4j_connection(),
            await tester.test_academic_tools(),
            tester.test_iap_tools(),
            tester.test_crawled_content(),
            await tester.test_data_extraction()
        ]
        
        # Print summary
        success = tester.print_summary()
        
        return success
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return False
    finally:
        tester.cleanup()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
