#!/usr/bin/env python3
"""
Backup Supabase Population Tool for Utah Tech Academic Data

This standalone tool extracts academic data from crawled content and populates
Supabase tables with proper duplicate handling and error recovery.

Usage:
    python populate_supabase_backup.py [--clear] [--batch-size 100] [--dry-run]

Options:
    --clear         Clear existing data before population
    --batch-size    Number of records per batch (default: 100)
    --dry-run       Show what would be inserted without actually inserting
    --verbose       Show detailed progress information
"""

import sys
import os
import asyncio
import argparse
from typing import Dict, List, Set
from dotenv import load_dotenv
from supabase import create_client

# Add src to path
sys.path.append('src')
from academic_graph_builder import AcademicGraphBuilder

class SupabaseBackupPopulator:
    """Standalone tool for populating Supabase academic tables"""
    
    def __init__(self, batch_size: int = 100, verbose: bool = False):
        load_dotenv()
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'), 
            os.getenv('SUPABASE_SERVICE_KEY')
        )
        self.batch_size = batch_size
        self.verbose = verbose
        self.stats = {
            'departments_processed': 0,
            'courses_processed': 0,
            'programs_processed': 0,
            'departments_inserted': 0,
            'courses_inserted': 0,
            'programs_inserted': 0,
            'duplicates_skipped': 0,
            'errors': []
        }
    
    async def populate_all_tables(self, clear_existing: bool = False, dry_run: bool = False):
        """Main method to populate all Supabase academic tables"""
        print("🚀 Starting Backup Supabase Population Process...")
        print(f"   📊 Batch size: {self.batch_size}")
        print(f"   🧹 Clear existing: {clear_existing}")
        print(f"   🔍 Dry run: {dry_run}")
        
        try:
            # Step 1: Extract academic data
            academic_data = await self._extract_academic_data()
            
            # Step 2: Clear existing data if requested
            if clear_existing and not dry_run:
                await self._clear_existing_data()
            
            # Step 3: Populate tables
            await self._populate_departments(academic_data.get('departments', {}), dry_run)
            await self._populate_courses(academic_data.get('courses', {}), dry_run)
            await self._populate_programs(academic_data.get('programs', {}), dry_run)
            
            # Step 4: Show final statistics
            self._show_final_stats()
            
            return True
            
        except Exception as e:
            print(f"❌ Population process failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _extract_academic_data(self) -> Dict:
        """Extract academic data using the academic graph builder"""
        print("\n1️⃣ Extracting Academic Data...")
        
        builder = AcademicGraphBuilder()
        try:
            academic_data = await builder._extract_academic_data()
            
            courses = academic_data.get('courses', {})
            programs = academic_data.get('programs', {})
            departments = academic_data.get('departments', {})
            
            print(f"   📊 Extracted: {len(courses)} courses, {len(programs)} programs, {len(departments)} departments")
            
            return academic_data
        finally:
            builder.close()
    
    async def _clear_existing_data(self):
        """Clear existing academic data from Supabase tables"""
        print("\n2️⃣ Clearing Existing Data...")
        
        try:
            # Clear in reverse dependency order
            self.supabase.table('academic_courses').delete().neq('course_code', '').execute()
            print("   ✅ Cleared academic_courses")
            
            self.supabase.table('academic_programs').delete().neq('program_name', '').execute()
            print("   ✅ Cleared academic_programs")
            
            self.supabase.table('academic_departments').delete().neq('department_name', '').execute()
            print("   ✅ Cleared academic_departments")
            
        except Exception as e:
            print(f"   ⚠️ Warning during data clearing: {e}")
    
    async def _populate_departments(self, departments: Dict, dry_run: bool = False):
        """Populate departments table with duplicate handling"""
        if not departments:
            return
            
        print(f"\n3️⃣ Populating Departments ({len(departments)} total)...")
        
        dept_records = []
        seen_prefixes: Set[str] = set()
        
        for dept_name, dept_info in departments.items():
            self.stats['departments_processed'] += 1
            
            # Skip duplicates based on prefix
            if dept_info.prefix in seen_prefixes:
                self.stats['duplicates_skipped'] += 1
                if self.verbose:
                    print(f"   ⏭️ Skipping duplicate prefix: {dept_info.prefix}")
                continue
            
            seen_prefixes.add(dept_info.prefix)
            
            department_data = {
                'department_name': dept_info.name,
                'prefix': dept_info.prefix,
                'description': dept_info.description,
                'source_id': 'catalog.utahtech.edu'
            }
            dept_records.append(department_data)
            
            if self.verbose:
                print(f"   📝 Prepared: {dept_info.prefix} - {dept_info.name}")
        
        # Insert in batches
        if dept_records and not dry_run:
            try:
                for i in range(0, len(dept_records), self.batch_size):
                    batch = dept_records[i:i + self.batch_size]
                    self.supabase.table('academic_departments').upsert(batch).execute()
                    self.stats['departments_inserted'] += len(batch)
                    print(f"   ✅ Upserted batch {i//self.batch_size + 1}: {len(batch)} departments")
                    
            except Exception as e:
                error_msg = f"Department insertion failed: {e}"
                self.stats['errors'].append(error_msg)
                print(f"   ❌ {error_msg}")
        
        print(f"   📊 Departments: {len(dept_records)} unique records prepared")
    
    async def _populate_courses(self, courses: Dict, dry_run: bool = False):
        """Populate courses table with duplicate handling"""
        if not courses:
            return
            
        print(f"\n4️⃣ Populating Courses ({len(courses)} total)...")
        
        course_records = []
        seen_courses: Set[str] = set()
        
        for course_code, course_info in courses.items():
            self.stats['courses_processed'] += 1
            
            # Skip duplicates based on course_code
            if course_info.code in seen_courses:
                self.stats['duplicates_skipped'] += 1
                if self.verbose:
                    print(f"   ⏭️ Skipping duplicate course: {course_info.code}")
                continue
            
            seen_courses.add(course_info.code)
            
            course_record = {
                'course_code': course_info.code,
                'title': course_info.title,
                'credits': course_info.credits,
                'level': course_info.level,
                'description': course_info.description[:1000] if course_info.description else None,
                'prerequisites': ', '.join(course_info.prerequisites) if course_info.prerequisites else None,
                'prefix': course_info.prefix,
                'course_number': course_info.number,
                'source_id': 'catalog.utahtech.edu'
            }
            course_records.append(course_record)
            
            if self.verbose:
                print(f"   📝 Prepared: {course_info.code} - {course_info.title[:50]}...")
        
        # Insert in batches
        if course_records and not dry_run:
            try:
                for i in range(0, len(course_records), self.batch_size):
                    batch = course_records[i:i + self.batch_size]
                    self.supabase.table('academic_courses').upsert(batch).execute()
                    self.stats['courses_inserted'] += len(batch)
                    print(f"   ✅ Upserted batch {i//self.batch_size + 1}: {len(batch)} courses")
                    
            except Exception as e:
                error_msg = f"Course insertion failed: {e}"
                self.stats['errors'].append(error_msg)
                print(f"   ❌ {error_msg}")
        
        print(f"   📊 Courses: {len(course_records)} unique records prepared")
    
    async def _populate_programs(self, programs: Dict, dry_run: bool = False):
        """Populate programs table with duplicate handling"""
        if not programs:
            return
            
        print(f"\n5️⃣ Populating Programs ({len(programs)} total)...")
        
        program_records = []
        seen_programs: Set[str] = set()
        
        for program_name, program_info in programs.items():
            self.stats['programs_processed'] += 1
            
            # Skip duplicates based on truncated program_name
            truncated_name = program_info.name[:500]  # Truncate to avoid index issues
            if truncated_name in seen_programs:
                self.stats['duplicates_skipped'] += 1
                if self.verbose:
                    print(f"   ⏭️ Skipping duplicate program: {truncated_name[:50]}...")
                continue
            
            seen_programs.add(truncated_name)
            
            program_record = {
                'program_name': truncated_name,
                'program_type': program_info.type,
                'level': program_info.level,
                'description': program_info.description[:1000] if program_info.description else None,
                'source_id': 'catalog.utahtech.edu'
            }
            program_records.append(program_record)
            
            if self.verbose:
                print(f"   📝 Prepared: {program_info.type} - {truncated_name[:50]}...")
        
        # Insert in batches
        if program_records and not dry_run:
            try:
                for i in range(0, len(program_records), self.batch_size):
                    batch = program_records[i:i + self.batch_size]
                    self.supabase.table('academic_programs').upsert(batch).execute()
                    self.stats['programs_inserted'] += len(batch)
                    print(f"   ✅ Upserted batch {i//self.batch_size + 1}: {len(batch)} programs")
                    
            except Exception as e:
                error_msg = f"Program insertion failed: {e}"
                self.stats['errors'].append(error_msg)
                print(f"   ❌ {error_msg}")
        
        print(f"   📊 Programs: {len(program_records)} unique records prepared")
    
    def _show_final_stats(self):
        """Display final population statistics"""
        print(f"\n🏁 Final Population Statistics:")
        print(f"   📊 Records Processed:")
        print(f"      - Departments: {self.stats['departments_processed']} → {self.stats['departments_inserted']} inserted")
        print(f"      - Courses: {self.stats['courses_processed']} → {self.stats['courses_inserted']} inserted")
        print(f"      - Programs: {self.stats['programs_processed']} → {self.stats['programs_inserted']} inserted")
        print(f"   ⏭️ Duplicates Skipped: {self.stats['duplicates_skipped']}")
        
        if self.stats['errors']:
            print(f"   ❌ Errors ({len(self.stats['errors'])}):")
            for error in self.stats['errors']:
                print(f"      - {error}")
        else:
            print(f"   ✅ No errors encountered")
        
        total_inserted = (self.stats['departments_inserted'] + 
                         self.stats['courses_inserted'] + 
                         self.stats['programs_inserted'])
        print(f"\n🎉 Total Records Inserted: {total_inserted}")

async def main():
    """Main entry point with command line argument parsing"""
    parser = argparse.ArgumentParser(description='Backup Supabase Population Tool')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before population')
    parser.add_argument('--batch-size', type=int, default=100, help='Number of records per batch')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be inserted without inserting')
    parser.add_argument('--verbose', action='store_true', help='Show detailed progress information')
    
    args = parser.parse_args()
    
    populator = SupabaseBackupPopulator(
        batch_size=args.batch_size,
        verbose=args.verbose
    )
    
    success = await populator.populate_all_tables(
        clear_existing=args.clear,
        dry_run=args.dry_run
    )
    
    if success:
        print("\n✅ Backup population completed successfully!")
        return 0
    else:
        print("\n❌ Backup population failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
