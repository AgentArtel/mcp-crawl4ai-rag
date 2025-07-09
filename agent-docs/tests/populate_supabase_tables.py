#!/usr/bin/env python3
"""
Standalone script to populate Supabase academic tables from crawled content.
This script extracts academic entities from the crawled content and populates
the academic_departments, academic_programs, and academic_courses tables.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

@dataclass
class Course:
    code: str
    title: str
    credits: int
    description: str
    prerequisites: List[str]
    level: str  # 'lower-division' or 'upper-division'
    prefix: str
    number: str
    source_id: str

@dataclass
class Program:
    name: str
    degree_type: str
    department: str
    description: str
    requirements: str
    total_credits: Optional[int]
    source_id: str

@dataclass
class Department:
    name: str
    code: str
    description: str
    source_id: str

class SupabaseAcademicPopulator:
    def __init__(self):
        """Initialize Supabase client and academic data structures."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Data containers
        self.departments: List[Department] = []
        self.programs: List[Program] = []
        self.courses: List[Course] = []
        
        print("✅ Supabase client initialized")

    def extract_academic_entities(self):
        """Extract academic entities from crawled content."""
        print("🔍 Extracting academic entities from crawled content...")
        
        try:
            # Get all crawled content from Supabase
            response = self.supabase.table('crawled_pages').select('*').execute()
            crawled_pages = response.data
            
            print(f"📄 Found {len(crawled_pages)} crawled pages")
            
            for page in crawled_pages:
                content = page.get('content', '')
                url = page.get('url', '')
                source_id = page.get('source_id', 'catalog.utahtech.edu')
                
                # Extract entities based on content type
                self._extract_from_content(content, url, source_id)
            
            print(f"✅ Extracted {len(self.departments)} departments, {len(self.programs)} programs, {len(self.courses)} courses")
            
        except Exception as e:
            print(f"❌ Error extracting academic entities: {e}")
            raise

    def _extract_from_content(self, content: str, url: str, source_id: str):
        """Extract academic entities from a single page's content."""
        
        # Extract courses using course code patterns
        course_pattern = r'([A-Z]{2,5})\s+(\d{4}[A-Z]?)\s*[-–]\s*([^(]+?)(?:\s*\((\d+(?:\.\d+)?)\s*credits?\))?'
        course_matches = re.finditer(course_pattern, content, re.MULTILINE | re.IGNORECASE)
        
        for match in course_matches:
            prefix = match.group(1).upper()
            number = match.group(2)
            title = match.group(3).strip()
            credits_str = match.group(4)
            
            # Parse credits
            try:
                credits = float(credits_str) if credits_str else 3.0
                credits = int(credits) if credits.is_integer() else credits
            except (ValueError, AttributeError):
                credits = 3
            
            # Determine level
            course_number = int(re.search(r'\d+', number).group())
            level = 'upper-division' if course_number >= 3000 else 'lower-division'
            
            # Extract prerequisites (simplified)
            prereqs = self._extract_prerequisites(content, f"{prefix} {number}")
            
            # Create course
            course = Course(
                code=f"{prefix} {number}",
                title=title,
                credits=credits,
                description="",  # Would need more sophisticated extraction
                prerequisites=prereqs,
                level=level,
                prefix=prefix,
                number=number,
                source_id=source_id
            )
            
            # Avoid duplicates
            if not any(c.code == course.code for c in self.courses):
                self.courses.append(course)
        
        # Extract programs
        program_patterns = [
            r'(Bachelor of [^|]+)',
            r'(Master of [^|]+)',
            r'(Associate of [^|]+)',
            r'([^|]+Certificate)',
            r'([^|]+Degree)',
        ]
        
        for pattern in program_patterns:
            program_matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in program_matches:
                program_name = match.group(1).strip()
                
                # Clean and validate program name
                program_name = program_name.strip()[:500]  # Truncate to 500 chars max
                
                # Skip if too generic, already exists, or invalid
                if (len(program_name) < 10 or 
                    any(p.name == program_name for p in self.programs) or
                    program_name.lower() in ['degree', 'certificate'] or
                    '|' in program_name):
                    continue
                
                # Determine degree type
                if 'bachelor' in program_name.lower():
                    degree_type = 'Bachelor'
                elif 'master' in program_name.lower():
                    degree_type = 'Master'
                elif 'associate' in program_name.lower():
                    degree_type = 'Associate'
                elif 'certificate' in program_name.lower():
                    degree_type = 'Certificate'
                else:
                    degree_type = 'Other'
                
                program = Program(
                    name=program_name,
                    degree_type=degree_type,
                    department="Unknown",  # Would need more sophisticated extraction
                    description="",
                    requirements="",
                    total_credits=None,
                    source_id=source_id
                )
                
                self.programs.append(program)
        
        # Extract departments from URL or content
        if '/departments/' in url or '/dept/' in url:
            dept_match = re.search(r'/(?:departments?|dept)/([^/]+)', url)
            if dept_match:
                dept_name = dept_match.group(1).replace('-', ' ').title()
                
                if not any(d.name == dept_name for d in self.departments):
                    department = Department(
                        name=dept_name,
                        code=dept_name.upper()[:4],
                        description="",
                        source_id=source_id
                    )
                    self.departments.append(department)

    def _extract_prerequisites(self, content: str, course_code: str) -> List[str]:
        """Extract prerequisites for a specific course."""
        prereqs = []
        
        # Look for prerequisite patterns near the course
        prereq_patterns = [
            r'prerequisite[s]?:?\s*([A-Z]{2,5}\s+\d{4}[A-Z]?(?:\s*,?\s*(?:and|or)?\s*[A-Z]{2,5}\s+\d{4}[A-Z]?)*)',
            r'prereq[s]?:?\s*([A-Z]{2,5}\s+\d{4}[A-Z]?(?:\s*,?\s*(?:and|or)?\s*[A-Z]{2,5}\s+\d{4}[A-Z]?)*)',
        ]
        
        for pattern in prereq_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                prereq_text = match.group(1)
                # Extract individual course codes
                course_codes = re.findall(r'[A-Z]{2,5}\s+\d{4}[A-Z]?', prereq_text)
                prereqs.extend(course_codes)
        
        return list(set(prereqs))  # Remove duplicates

    def populate_supabase_tables(self):
        """Populate Supabase academic tables with extracted data."""
        print("📊 Populating Supabase academic tables...")
        
        try:
            # Clear existing data
            print("🧹 Clearing existing academic data...")
            self.supabase.table('academic_courses').delete().neq('course_id', 0).execute()
            self.supabase.table('academic_programs').delete().neq('program_id', '00000000-0000-0000-0000-000000000000').execute()
            self.supabase.table('academic_departments').delete().neq('department_id', '00000000-0000-0000-0000-000000000000').execute()
            
            # Insert departments
            if self.departments:
                print(f"🏦️ Inserting {len(self.departments)} departments...")
                dept_data = []
                for dept in self.departments:
                    dept_data.append({
                        'department_name': dept.name,
                        'prefix': dept.code,
                        'description': dept.description,
                        'source_id': dept.source_id
                    })
                
                response = self.supabase.table('academic_departments').insert(dept_data).execute()
                print(f"✅ Inserted {len(response.data)} departments")
            
            # Insert programs
            if self.programs:
                print(f"📚 Inserting {len(self.programs)} programs...")
                program_data = []
                for program in self.programs:
                    # Determine level from degree_type
                    level = 'graduate' if program.degree_type in ['Master', 'Doctorate'] else 'undergraduate'
                    
                    program_data.append({
                        'program_name': program.name,
                        'program_type': program.degree_type,
                        'level': level,
                        'description': program.description,
                        'requirements': program.requirements,
                        'source_id': program.source_id
                    })
                
                response = self.supabase.table('academic_programs').insert(program_data).execute()
                print(f"✅ Inserted {len(response.data)} programs")
            
            # Insert courses
            if self.courses:
                print(f"📖 Inserting {len(self.courses)} courses...")
                course_data = []
                for course in self.courses:
                    course_data.append({
                        'course_code': course.code,
                        'title': course.title,
                        'credits': course.credits,
                        'description': course.description,
                        'prerequisites': ', '.join(course.prerequisites) if course.prerequisites else '',
                        'level': course.level,
                        'prefix': course.prefix,
                        'course_number': course.number,
                        'source_id': course.source_id
                    })
                
                # Insert in batches to avoid size limits
                batch_size = 100
                for i in range(0, len(course_data), batch_size):
                    batch = course_data[i:i + batch_size]
                    response = self.supabase.table('academic_courses').insert(batch).execute()
                    print(f"✅ Inserted batch {i//batch_size + 1}: {len(response.data)} courses")
            
            print("🎉 Successfully populated all Supabase academic tables!")
            
        except Exception as e:
            print(f"❌ Error populating Supabase tables: {e}")
            raise

    def verify_population(self):
        """Verify that the tables were populated correctly."""
        print("🔍 Verifying table population...")
        
        try:
            # Check departments
            dept_response = self.supabase.table('academic_departments').select('*', count='exact').execute()
            dept_count = dept_response.count
            print(f"📊 academic_departments: {dept_count} records")
            
            # Check programs
            prog_response = self.supabase.table('academic_programs').select('*', count='exact').execute()
            prog_count = prog_response.count
            print(f"📊 academic_programs: {prog_count} records")
            
            # Check courses
            course_response = self.supabase.table('academic_courses').select('*', count='exact').execute()
            course_count = course_response.count
            print(f"📊 academic_courses: {course_count} records")
            
            # Show sample data
            if dept_count > 0:
                sample_dept = self.supabase.table('academic_departments').select('*').limit(3).execute()
                print(f"📋 Sample departments: {[d['name'] for d in sample_dept.data]}")
            
            if prog_count > 0:
                sample_prog = self.supabase.table('academic_programs').select('*').limit(3).execute()
                print(f"📋 Sample programs: {[p['name'] for p in sample_prog.data]}")
            
            if course_count > 0:
                sample_course = self.supabase.table('academic_courses').select('*').limit(3).execute()
                print(f"📋 Sample courses: {[c['code'] + ' - ' + c['title'] for c in sample_course.data]}")
            
            return dept_count > 0 or prog_count > 0 or course_count > 0
            
        except Exception as e:
            print(f"❌ Error verifying population: {e}")
            return False

def main():
    """Main function to run the Supabase population script."""
    print("🚀 Starting Supabase Academic Tables Population")
    print("=" * 50)
    
    try:
        # Initialize populator
        populator = SupabaseAcademicPopulator()
        
        # Extract academic entities
        populator.extract_academic_entities()
        
        # Populate Supabase tables
        populator.populate_supabase_tables()
        
        # Verify population
        success = populator.verify_population()
        
        if success:
            print("\n🎉 SUCCESS: Supabase academic tables populated successfully!")
        else:
            print("\n⚠️ WARNING: Tables may not have been populated correctly")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
