#!/usr/bin/env python3
"""
Comprehensive test of backup tool logic before Docker rebuild
"""

import sys
import os
import asyncio
sys.path.append('src')

from academic_graph_builder import AcademicGraphBuilder
from utils import get_supabase_client

async def test_backup_tool_comprehensive():
    """Test the complete backup tool workflow"""
    print("🧪 Testing comprehensive backup tool workflow...")
    
    try:
        # Initialize components
        builder = AcademicGraphBuilder()
        supabase = get_supabase_client()
        print("✅ Components initialized successfully")
        
        # Test 1: Check if we have crawled content
        print("\n📋 Test 1: Checking for crawled content...")
        response = supabase.table("crawled_pages").select("*").eq(
            "source_id", "catalog.utahtech.edu"
        ).limit(1).execute()
        
        if response.data:
            print(f"✅ Found crawled content: {len(response.data)} sample pages")
        else:
            print("⚠️  No crawled content found - backup tool will return empty data")
        
        # Test 2: Test academic data extraction
        print("\n📋 Test 2: Testing academic data extraction...")
        try:
            academic_data = await builder._extract_academic_data()
            if academic_data:
                courses = academic_data.get('courses', {})
                programs = academic_data.get('programs', {})
                departments = academic_data.get('departments', {})
                print(f"✅ Extracted: {len(courses)} courses, {len(programs)} programs, {len(departments)} departments")
            else:
                print("⚠️  No academic data extracted (empty result)")
        except Exception as e:
            print(f"❌ Error in academic data extraction: {e}")
            return False
        
        # Test 3: Check Supabase table access
        print("\n📋 Test 3: Testing Supabase table access...")
        try:
            # Test academic_departments table
            dept_response = supabase.table("academic_departments").select("*").limit(1).execute()
            print("✅ academic_departments table accessible")
            
            # Test academic_courses table  
            course_response = supabase.table("academic_courses").select("*").limit(1).execute()
            print("✅ academic_courses table accessible")
            
            # Test academic_programs table
            prog_response = supabase.table("academic_programs").select("*").limit(1).execute()
            print("✅ academic_programs table accessible")
            
        except Exception as e:
            print(f"❌ Error accessing Supabase tables: {e}")
            print("💡 Make sure academic tables are created with SQL migration")
            return False
        
        # Test 4: Test populate method exists
        print("\n📋 Test 4: Testing populate method...")
        if hasattr(builder, '_populate_supabase_tables'):
            print("✅ _populate_supabase_tables method exists")
        else:
            print("❌ _populate_supabase_tables method missing")
            return False
        
        builder.close()
        print("\n🎉 All backup tool tests PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Error in comprehensive test: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backup_tool_comprehensive())
    if success:
        print("\n✅ Backup tool is ready for Docker rebuild")
    else:
        print("\n❌ Fix issues before Docker rebuild")
    
    sys.exit(0 if success else 1)
