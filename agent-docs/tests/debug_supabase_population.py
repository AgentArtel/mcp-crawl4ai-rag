#!/usr/bin/env python3
"""
Debug script to test Supabase population directly
"""
import sys
import os
import asyncio
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')
from academic_graph_builder import AcademicGraphBuilder

async def debug_supabase_population():
    """Debug the Supabase population process"""
    print("🔍 Debugging Supabase Population Process...")
    
    builder = AcademicGraphBuilder()
    
    try:
        # Step 1: Extract academic data
        print("\n1️⃣ Extracting academic data...")
        academic_data = await builder._extract_academic_data()
        
        courses = academic_data.get('courses', {})
        programs = academic_data.get('programs', {})
        departments = academic_data.get('departments', {})
        
        print(f"   📊 Extracted: {len(courses)} courses, {len(programs)} programs, {len(departments)} departments")
        
        # Step 2: Test Supabase population directly
        print("\n2️⃣ Testing Supabase population...")
        
        try:
            # Test clearing existing data
            print("   🧹 Clearing existing data...")
            builder.supabase.table('academic_courses').delete().neq('course_code', '').execute()
            builder.supabase.table('academic_programs').delete().neq('program_name', '').execute()
            builder.supabase.table('academic_departments').delete().neq('department_name', '').execute()
            print("   ✅ Cleared existing data")
            
            # Test department insertion (with duplicate handling)
            if departments:
                print(f"   🏢 Testing department insertion ({len(departments)} departments)...")
                dept_records = []
                seen_prefixes = set()
                
                for dept_name, dept_info in list(departments.items())[:10]:  # Test first 10
                    # Skip duplicates based on prefix
                    if dept_info.prefix in seen_prefixes:
                        continue
                    seen_prefixes.add(dept_info.prefix)
                    
                    department_data = {
                        'department_name': dept_info.name,
                        'prefix': dept_info.prefix,
                        'description': dept_info.description,
                        'source_id': 'catalog.utahtech.edu'
                    }
                    dept_records.append(department_data)
                
                if dept_records:
                    result = builder.supabase.table('academic_departments').upsert(dept_records).execute()
                    print(f"   ✅ Upserted {len(dept_records)} unique departments successfully")
                    print(f"   📄 Sample department: {dept_records[0]}")
            
            # Test course insertion
            if courses:
                print(f"   📚 Testing course insertion ({len(courses)} courses)...")
                course_records = []
                for course_code, course_info in list(courses.items())[:5]:  # Test first 5
                    course_record = {
                        'course_code': course_info.code,
                        'title': course_info.title,
                        'credits': course_info.credits,
                        'level': course_info.level,
                        'description': course_info.description[:500] if course_info.description else None,
                        'prerequisites': ', '.join(course_info.prerequisites) if course_info.prerequisites else None,
                        'prefix': course_info.prefix,
                        'course_number': course_info.number,
                        'source_id': 'catalog.utahtech.edu'
                    }
                    course_records.append(course_record)
                
                if course_records:
                    result = builder.supabase.table('academic_courses').insert(course_records).execute()
                    print(f"   ✅ Inserted {len(course_records)} courses successfully")
                    print(f"   📄 Sample course: {course_records[0]['course_code']} - {course_records[0]['title']}")
            
            # Test program insertion
            if programs:
                print(f"   🎓 Testing program insertion ({len(programs)} programs)...")
                program_records = []
                for program_name, program_info in list(programs.items())[:5]:  # Test first 5
                    program_record = {
                        'program_name': program_info.name[:500],  # Truncate to avoid index issues
                        'program_type': program_info.type,
                        'level': program_info.level,
                        'description': program_info.description[:1000] if program_info.description else None,
                        'source_id': 'catalog.utahtech.edu'
                    }
                    program_records.append(program_record)
                
                if program_records:
                    result = builder.supabase.table('academic_programs').insert(program_records).execute()
                    print(f"   ✅ Inserted {len(program_records)} programs successfully")
                    print(f"   📄 Sample program: {program_records[0]['program_name']}")
            
            print("\n✅ Supabase population test completed successfully!")
            
            # Verify the data was inserted
            print("\n3️⃣ Verifying inserted data...")
            courses_count = builder.supabase.table('academic_courses').select('*', count='exact').execute()
            programs_count = builder.supabase.table('academic_programs').select('*', count='exact').execute()
            departments_count = builder.supabase.table('academic_departments').select('*', count='exact').execute()
            
            print(f"   📊 Final counts:")
            print(f"   - Courses: {courses_count.count}")
            print(f"   - Programs: {programs_count.count}")
            print(f"   - Departments: {departments_count.count}")
            
        except Exception as e:
            print(f"   ❌ Supabase population failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Debug process failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        builder.close()

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(debug_supabase_population())
