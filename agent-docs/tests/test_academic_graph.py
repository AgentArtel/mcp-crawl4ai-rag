#!/usr/bin/env python3
"""
Test script for Academic Knowledge Graph Builder

This script tests the academic graph building functionality including:
- Neo4j connection and schema creation
- Academic data extraction from crawled content
- Graph population with courses, programs, and departments
- Relationship creation (prerequisites, program mappings)
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).resolve().parent / 'src'
sys.path.insert(0, str(src_path))

# Set up environment
from dotenv import load_dotenv
project_root = Path(__file__).resolve().parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path, override=True)

from academic_graph_builder import AcademicGraphBuilder


class MockContext:
    """Mock context for testing"""
    pass


async def test_neo4j_connection():
    """Test Neo4j connection"""
    print("🔌 Testing Neo4j connection...")
    
    builder = AcademicGraphBuilder()
    
    if builder.neo4j_driver:
        try:
            with builder.neo4j_driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                if record and record["test"] == 1:
                    print("   ✅ Neo4j connection successful")
                    return True
                else:
                    print("   ❌ Neo4j query failed")
                    return False
        except Exception as e:
            print(f"   ❌ Neo4j connection error: {e}")
            return False
        finally:
            builder.close()
    else:
        print("   ❌ No Neo4j driver available")
        return False


async def test_academic_data_extraction():
    """Test academic data extraction from Supabase"""
    print("\n🔍 Testing academic data extraction...")
    
    builder = AcademicGraphBuilder()
    
    try:
        # Test data extraction
        academic_data = await builder._extract_academic_data()
        
        courses = academic_data.get("courses", {})
        programs = academic_data.get("programs", {})
        departments = academic_data.get("departments", {})
        
        print(f"   📊 Extracted:")
        print(f"      Courses: {len(courses)}")
        print(f"      Programs: {len(programs)}")
        print(f"      Departments: {len(departments)}")
        
        # Show sample courses
        if courses:
            print(f"\n   📚 Sample Courses:")
            for i, (code, course) in enumerate(list(courses.items())[:3]):
                print(f"      {code}: {course.title} ({course.credits} credits, {course.level})")
                if course.prerequisites:
                    print(f"         Prerequisites: {', '.join(course.prerequisites)}")
        
        # Show sample programs
        if programs:
            print(f"\n   🎓 Sample Programs:")
            for i, (name, program) in enumerate(list(programs.items())[:3]):
                print(f"      {name} ({program.type}, {program.level})")
        
        # Show sample departments
        if departments:
            print(f"\n   🏢 Sample Departments:")
            for i, (name, dept) in enumerate(list(departments.items())[:3]):
                print(f"      {name} (Prefix: {dept.prefix})")
        
        return len(courses) > 0 or len(programs) > 0 or len(departments) > 0
        
    except Exception as e:
        print(f"   ❌ Data extraction failed: {e}")
        return False
    finally:
        builder.close()


async def test_schema_creation():
    """Test Neo4j schema creation"""
    print("\n📋 Testing Neo4j schema creation...")
    
    builder = AcademicGraphBuilder()
    
    if not builder.neo4j_driver:
        print("   ❌ No Neo4j connection available")
        return False
    
    try:
        # Create schema
        await builder._create_schema()
        
        # Verify constraints were created
        with builder.neo4j_driver.session() as session:
            # Check for some key constraints
            constraints_query = "SHOW CONSTRAINTS"
            result = session.run(constraints_query)
            constraints = [record["name"] for record in result]
            
            expected_constraints = [
                "university_name",
                "course_code", 
                "department_prefix",
                "program_name"
            ]
            
            found_constraints = []
            for expected in expected_constraints:
                if any(expected in constraint for constraint in constraints):
                    found_constraints.append(expected)
            
            print(f"   ✅ Created {len(found_constraints)}/{len(expected_constraints)} expected constraints")
            
            # Check for indexes
            indexes_query = "SHOW INDEXES"
            result = session.run(indexes_query)
            indexes = [record["name"] for record in result]
            
            expected_indexes = [
                "course_prefix",
                "course_level",
                "program_type"
            ]
            
            found_indexes = []
            for expected in expected_indexes:
                if any(expected in index for index in indexes):
                    found_indexes.append(expected)
            
            print(f"   ✅ Created {len(found_indexes)}/{len(expected_indexes)} expected indexes")
            
            return len(found_constraints) > 0 and len(found_indexes) > 0
            
    except Exception as e:
        print(f"   ❌ Schema creation failed: {e}")
        return False
    finally:
        builder.close()


async def test_graph_population():
    """Test full graph building process"""
    print("\n🏗️ Testing complete graph building...")
    
    builder = AcademicGraphBuilder()
    
    if not builder.neo4j_driver:
        print("   ❌ No Neo4j connection available")
        return False
    
    try:
        # Build the complete graph
        academic_data = await builder.build_academic_graph()
        
        # Verify data was populated
        with builder.neo4j_driver.session() as session:
            # Count nodes
            university_count = session.run("MATCH (u:University) RETURN count(u) as count").single()["count"]
            department_count = session.run("MATCH (d:Department) RETURN count(d) as count").single()["count"]
            course_count = session.run("MATCH (c:Course) RETURN count(c) as count").single()["count"]
            program_count = session.run("MATCH (p:Program) RETURN count(p) as count").single()["count"]
            
            print(f"   📊 Graph Population Results:")
            print(f"      Universities: {university_count}")
            print(f"      Departments: {department_count}")
            print(f"      Courses: {course_count}")
            print(f"      Programs: {program_count}")
            
            # Count relationships
            prereq_count = session.run("MATCH ()-[r:PREREQUISITE_FOR]->() RETURN count(r) as count").single()["count"]
            offers_count = session.run("MATCH ()-[r:OFFERS_COURSE]->() RETURN count(r) as count").single()["count"]
            
            print(f"   🔗 Relationships Created:")
            print(f"      Prerequisites: {prereq_count}")
            print(f"      Course Offerings: {offers_count}")
            
            # Show sample prerequisite chain
            if prereq_count > 0:
                prereq_sample = session.run("""
                    MATCH (prereq:Course)-[:PREREQUISITE_FOR]->(course:Course)
                    RETURN prereq.code, course.code
                    LIMIT 3
                """).data()
                
                print(f"   📚 Sample Prerequisites:")
                for record in prereq_sample:
                    print(f"      {record['prereq.code']} → {record['course.code']}")
            
            return course_count > 0 or program_count > 0
            
    except Exception as e:
        print(f"   ❌ Graph building failed: {e}")
        return False
    finally:
        builder.close()


async def test_graph_queries():
    """Test sample graph queries"""
    print("\n🔍 Testing graph queries...")
    
    builder = AcademicGraphBuilder()
    
    if not builder.neo4j_driver:
        print("   ❌ No Neo4j connection available")
        return False
    
    try:
        with builder.neo4j_driver.session() as session:
            # Test 1: Find courses with prerequisites
            prereq_courses = session.run("""
                MATCH (course:Course)
                WHERE course.prerequisites_text <> ''
                RETURN course.code, course.title, course.prerequisites_text
                LIMIT 5
            """).data()
            
            if prereq_courses:
                print(f"   📚 Courses with Prerequisites:")
                for record in prereq_courses:
                    code = record['course.code']
                    title = record['course.title']
                    prereqs = record['course.prerequisites_text']
                    print(f"      {code}: {title}")
                    print(f"         Prerequisites: {prereqs}")
            
            # Test 2: Find upper-division courses by department
            upper_div_courses = session.run("""
                MATCH (d:Department)-[:OFFERS_COURSE]->(c:Course)
                WHERE c.level = 'upper_division'
                RETURN d.prefix, count(c) as course_count
                ORDER BY course_count DESC
                LIMIT 5
            """).data()
            
            if upper_div_courses:
                print(f"\n   🎓 Upper-Division Courses by Department:")
                for record in upper_div_courses:
                    prefix = record['d.prefix']
                    count = record['course_count']
                    print(f"      {prefix}: {count} courses")
            
            # Test 3: Find prerequisite chains
            prereq_chains = session.run("""
                MATCH path = (start:Course)-[:PREREQUISITE_FOR*1..3]->(end:Course)
                WHERE start.level = 'lower_division' AND end.level = 'upper_division'
                RETURN start.code, end.code, length(path) as chain_length
                ORDER BY chain_length DESC
                LIMIT 3
            """).data()
            
            if prereq_chains:
                print(f"\n   🔗 Sample Prerequisite Chains:")
                for record in prereq_chains:
                    start = record['start.code']
                    end = record['end.code']
                    length = record['chain_length']
                    print(f"      {start} → ... → {end} (chain length: {length})")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Graph queries failed: {e}")
        return False
    finally:
        builder.close()


async def main():
    """Run all academic graph tests"""
    print("🧪 Testing Academic Knowledge Graph Builder")
    print("=" * 50)
    
    # Test results
    results = {}
    
    # Test Neo4j connection
    results["neo4j_connection"] = await test_neo4j_connection()
    
    # Test data extraction
    results["data_extraction"] = await test_academic_data_extraction()
    
    # Test schema creation
    results["schema_creation"] = await test_schema_creation()
    
    # Test graph population
    results["graph_population"] = await test_graph_population()
    
    # Test graph queries
    results["graph_queries"] = await test_graph_queries()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Academic knowledge graph is ready.")
        print("\nNext steps:")
        print("1. Use build_academic_knowledge_graph MCP tool")
        print("2. Test graph-enhanced academic planning queries")
        print("3. Validate prerequisite chains and program requirements")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Verify Neo4j is running and accessible")
        print("2. Check environment variables (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)")
        print("3. Ensure crawled academic content exists in Supabase")


if __name__ == "__main__":
    asyncio.run(main())
