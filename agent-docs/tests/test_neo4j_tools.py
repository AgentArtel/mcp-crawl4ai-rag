#!/usr/bin/env python3
"""
Test script to verify Neo4j-dependent tools are working correctly.
This tests prerequisite chains, course sequence validation, and knowledge graph queries.
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Import the context helper and Neo4j-dependent tools
from crawl4ai_mcp import (
    get_supabase_from_context, 
    get_prerequisite_chain,
    validate_course_sequence,
    recommend_course_sequence,
    query_knowledge_graph
)

class MockContext:
    """Mock context for testing"""
    def __init__(self):
        # Standard FastMCP context structure
        self.request_context = MockRequestContext()

class MockRequestContext:
    def __init__(self):
        self.lifespan_context = MockLifespanContext()

class MockLifespanContext:
    def __init__(self):
        from utils import get_supabase_client
        self.supabase_client = get_supabase_client()
        # Add repo_extractor mock for knowledge graph tools
        self.repo_extractor = None

async def test_neo4j_connectivity():
    """Test basic Neo4j connectivity"""
    print("🔌 Testing Neo4j Connectivity")
    print("=" * 60)
    
    mock_ctx = MockContext()
    
    try:
        # Test basic knowledge graph query
        result_json = await query_knowledge_graph(
            ctx=mock_ctx,
            command="repos"
        )
        
        result = json.loads(result_json)
        
        if result.get('success'):
            print("✅ Neo4j connection successful!")
            print(f"   Found {len(result.get('repositories', []))} repositories in knowledge graph")
            return True
        else:
            print(f"❌ Neo4j connection failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Neo4j connection error: {str(e)}")
        return False

async def test_prerequisite_chains():
    """Test prerequisite chain analysis"""
    print(f"\n🔗 Testing Prerequisite Chain Analysis")
    print("=" * 60)
    
    # Test courses with known prerequisite chains
    test_courses = [
        {
            "course": "CS 2420",
            "description": "Data Structures (should have CS prerequisites)"
        },
        {
            "course": "MATH 2210", 
            "description": "Calculus III (should have Calc I/II prerequisites)"
        },
        {
            "course": "BIOL 3450",
            "description": "Genetics (should have biology prerequisites)"
        }
    ]
    
    mock_ctx = MockContext()
    
    for i, test_case in enumerate(test_courses, 1):
        print(f"\n📋 Test {i}: {test_case['course']} - {test_case['description']}")
        
        try:
            result_json = await get_prerequisite_chain(
                ctx=mock_ctx,
                course_code=test_case['course'],
                max_depth=5
            )
            
            result = json.loads(result_json)
            
            if result.get('success'):
                chain = result.get('prerequisite_chain', {})
                print(f"✅ Success!")
                print(f"   Course: {chain.get('course_code', 'Unknown')}")
                print(f"   Total Prerequisites: {chain.get('total_prerequisites', 0)}")
                print(f"   Chain Depth: {chain.get('max_depth', 0)}")
                
                # Show prerequisite levels
                levels = chain.get('prerequisite_levels', [])
                for level_idx, level in enumerate(levels):
                    if level:
                        print(f"   Level {level_idx + 1}: {', '.join(level)}")
                        
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def test_course_sequence_validation():
    """Test course sequence validation"""
    print(f"\n✅ Testing Course Sequence Validation")
    print("=" * 60)
    
    # Test sequences with different prerequisite scenarios
    test_sequences = [
        {
            "name": "Valid CS Sequence",
            "courses": "CS 1400, CS 1410, CS 2420",
            "expected": "Should be valid progression"
        },
        {
            "name": "Valid Math Sequence", 
            "courses": "MATH 1050, MATH 1210, MATH 2210",
            "expected": "Should be valid calculus progression"
        },
        {
            "name": "Invalid Sequence",
            "courses": "CS 2420, CS 1400, CS 1410", 
            "expected": "Should show prerequisite violations"
        }
    ]
    
    mock_ctx = MockContext()
    
    for i, test_case in enumerate(test_sequences, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"   Sequence: {test_case['courses']}")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            result_json = await validate_course_sequence(
                ctx=mock_ctx,
                course_list=test_case['courses']
            )
            
            result = json.loads(result_json)
            
            if result.get('success'):
                validation = result.get('validation', {})
                print(f"✅ Success!")
                print(f"   Valid Sequence: {validation.get('is_valid', False)}")
                print(f"   Total Courses: {validation.get('total_courses', 0)}")
                
                violations = validation.get('prerequisite_violations', [])
                if violations:
                    print(f"   Violations Found: {len(violations)}")
                    for violation in violations[:2]:  # Show first 2
                        print(f"     - {violation.get('course')}: {violation.get('issue')}")
                else:
                    print(f"   No prerequisite violations found")
                    
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def test_course_sequence_recommendation():
    """Test course sequence recommendation"""
    print(f"\n🎯 Testing Course Sequence Recommendation")
    print("=" * 60)
    
    # Test recommendation for courses with prerequisites
    test_cases = [
        {
            "name": "CS Core Courses",
            "courses": "CS 2420, CS 3150, CS 4550",
            "expected": "Should recommend proper prerequisite order"
        },
        {
            "name": "Mixed Discipline Courses",
            "courses": "BIOL 3450, MATH 2210, PSYC 3010",
            "expected": "Should handle cross-discipline prerequisites"
        }
    ]
    
    mock_ctx = MockContext()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"   Target Courses: {test_case['courses']}")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            result_json = await recommend_course_sequence(
                ctx=mock_ctx,
                target_courses=test_case['courses'],
                max_semesters=6
            )
            
            result = json.loads(result_json)
            
            if result.get('success'):
                recommendation = result.get('recommendation', {})
                print(f"✅ Success!")
                print(f"   Total Semesters: {recommendation.get('total_semesters', 0)}")
                print(f"   Total Courses: {recommendation.get('total_courses', 0)}")
                
                # Show semester plan
                semester_plan = recommendation.get('semester_plan', [])
                for sem_idx, semester in enumerate(semester_plan[:3], 1):  # Show first 3
                    courses = semester.get('courses', [])
                    if courses:
                        course_codes = [c.get('course_code', 'Unknown') for c in courses]
                        print(f"   Semester {sem_idx}: {', '.join(course_codes)}")
                        
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def main():
    """Main test function"""
    print("🚀 Starting Neo4j Graph-Dependent Tools Test")
    print("=" * 60)
    
    # Test Neo4j connectivity first
    neo4j_working = await test_neo4j_connectivity()
    
    if neo4j_working:
        # Test prerequisite chains
        await test_prerequisite_chains()
        
        # Test course sequence validation
        await test_course_sequence_validation()
        
        # Test course sequence recommendation
        await test_course_sequence_recommendation()
        
        print(f"\n🎉 Neo4j Graph-Dependent Tools Test Complete!")
    else:
        print(f"\n⚠️  Neo4j not available - skipping graph-dependent tests")
        print("   Make sure Neo4j Docker container is running:")
        print("   docker run -d --name neo4j-utah-tech -p 7474:7474 -p 7687:7687 \\")
        print("     -e NEO4J_AUTH=neo4j/password123 neo4j:latest")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
