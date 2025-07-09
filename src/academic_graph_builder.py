"""
Academic Knowledge Graph Builder

This module extracts academic entities from crawled content and populates
the Neo4j knowledge graph with structured academic data for Utah Tech University.
"""

import re
import json
import asyncio
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

from neo4j import GraphDatabase
from utils import get_supabase_client, create_embedding
import os


@dataclass
class CourseInfo:
    """Structured course information"""
    code: str
    prefix: str
    number: str
    title: str
    credits: int
    level: str  # lower_division, upper_division, graduate
    description: str
    prerequisites: List[str]
    corequisites: List[str]
    offered_semesters: List[str]


@dataclass
class ProgramInfo:
    """Structured program information"""
    name: str
    code: str
    type: str  # Bachelor, Master, Certificate, Minor
    level: str  # undergraduate, graduate
    total_credits: int
    description: str
    department: str
    requirements: List[str]


@dataclass
class DepartmentInfo:
    """Structured department information"""
    name: str
    code: str
    prefix: str
    description: str
    programs: List[str]
    courses: List[str]


class AcademicGraphBuilder:
    """Builds and populates the academic knowledge graph"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.neo4j_driver = None
        self._setup_neo4j()
        
    def _setup_neo4j(self):
        """Initialize Neo4j connection"""
        try:
            # Get Neo4j connection details from environment
            neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        
            self.neo4j_driver = GraphDatabase.driver(
                neo4j_uri, 
                auth=(neo4j_user, neo4j_password)
            )
            print(f"✅ Connected to Neo4j at {neo4j_uri}")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            self.neo4j_driver = None
    
    def close(self):
        """Close Neo4j connection"""
        if self.neo4j_driver:
            self.neo4j_driver.close()
    
    async def build_academic_graph(self):
        """Main method to build the complete academic graph"""
        print("🏗️ Building Academic Knowledge Graph...")
        
        # Step 1: Create schema and constraints
        await self._create_schema()
        
        # Step 2: Extract academic data from crawled content
        academic_data = await self._extract_academic_data()
        
        # Step 3: Populate the graph
        await self._populate_graph(academic_data)
        
        # Step 4: Create relationships
        await self._create_relationships(academic_data)
        
        print("✅ Academic Knowledge Graph built successfully!")
        return academic_data
    
    async def _create_schema(self):
        """Create Neo4j schema, indexes, and constraints"""
        print("📋 Creating Neo4j schema...")
        
        if not self.neo4j_driver:
            print("❌ No Neo4j connection available")
            return
        
        schema_queries = [
            # Constraints for uniqueness
            "CREATE CONSTRAINT university_name IF NOT EXISTS FOR (u:University) REQUIRE u.name IS UNIQUE",
            "CREATE CONSTRAINT college_name IF NOT EXISTS FOR (c:College) REQUIRE c.name IS UNIQUE", 
            "CREATE CONSTRAINT department_prefix IF NOT EXISTS FOR (d:Department) REQUIRE d.prefix IS UNIQUE",
            "CREATE CONSTRAINT program_name IF NOT EXISTS FOR (p:Program) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT course_code IF NOT EXISTS FOR (course:Course) REQUIRE course.code IS UNIQUE",
            "CREATE CONSTRAINT requirement_name IF NOT EXISTS FOR (r:Requirement) REQUIRE r.name IS UNIQUE",
            
            # Indexes for performance
            "CREATE INDEX course_prefix IF NOT EXISTS FOR (course:Course) ON (course.prefix)",
            "CREATE INDEX course_number IF NOT EXISTS FOR (course:Course) ON (course.number)",
            "CREATE INDEX course_level IF NOT EXISTS FOR (course:Course) ON (course.level)",
            "CREATE INDEX program_type IF NOT EXISTS FOR (p:Program) ON (p.type)",
            "CREATE INDEX program_level IF NOT EXISTS FOR (p:Program) ON (p.level)",
        ]
        
        with self.neo4j_driver.session() as session:
            for query in schema_queries:
                try:
                    session.run(query)
                    print(f"   ✅ {query.split()[1]} created")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"   ⚠️ {query}: {e}")
    
    async def _extract_academic_data(self) -> Dict:
        """Extract structured academic data from crawled content"""
        print("🔍 Extracting academic data from crawled content...")
        
        # Get all crawled pages from Utah Tech catalog
        response = self.supabase.table("crawled_pages").select("*").eq(
            "source_id", "catalog.utahtech.edu"
        ).execute()
        
        if not response.data:
            print("❌ No crawled academic content found")
            return {}
        
        print(f"📄 Processing {len(response.data)} crawled pages...")
        
        courses = {}
        programs = {}
        departments = {}
        
        for page in response.data:
            content = page.get("content", "")
            url = page.get("url", "")
            
            # Extract courses from content
            page_courses = self._extract_courses_from_content(content, url)
            courses.update(page_courses)
            
            # Extract programs from content
            page_programs = self._extract_programs_from_content(content, url)
            programs.update(page_programs)
            
            # Extract departments from content
            page_departments = self._extract_departments_from_content(content, url)
            departments.update(page_departments)
        
        print(f"📊 Extracted: {len(courses)} courses, {len(programs)} programs, {len(departments)} departments")
        
        return {
            "courses": courses,
            "programs": programs,
            "departments": departments
        }
    
    def _extract_courses_from_content(self, content: str, url: str) -> Dict[str, CourseInfo]:
        """Extract course information from content"""
        courses = {}
        
        # More precise pattern to match actual course codes and descriptions
        # Must have proper course structure: PREFIX NNNN. Title. Description
        course_pattern = r'\b([A-Z]{2,4})\s+(\d{4})\.\s+([^.\n]+)\.\s*(?:(\d+)\s*(?:Hours?|Credits?))?'
        
        matches = re.finditer(course_pattern, content, re.MULTILINE)
        
        for match in matches:
            prefix = match.group(1).upper()
            number = match.group(2)
            title = match.group(3).strip()
            credits_str = match.group(4)  # Credits from regex group 4
            
            code = f"{prefix} {number}"
            
            # Validate course code - filter out invalid patterns
            if not self._is_valid_course_code(prefix, number, title):
                continue
            
            # Determine credit hours
            credits = 3  # default
            if credits_str:
                try:
                    credits = int(credits_str)
                except ValueError:
                    pass
            
            # Determine course level
            level = "lower_division"
            if int(number) >= 3000:
                level = "upper_division"
            elif int(number) >= 5000:
                level = "graduate"
            
            # Extract description (next few sentences after the course title)
            description = self._extract_course_description(content, match.end())
            
            # Extract prerequisites
            prerequisites = self._extract_prerequisites(description)
            
            courses[code] = CourseInfo(
                code=code,
                prefix=prefix,
                number=number,
                title=title,
                credits=credits,
                level=level,
                description=description,
                prerequisites=prerequisites,
                corequisites=[],  # TODO: Extract corequisites
                offered_semesters=["Fall", "Spring"]  # Default assumption
            )
        
        return courses
    
    def _is_valid_course_code(self, prefix: str, number: str, title: str) -> bool:
        """Validate if a course code is legitimate"""
        # Filter out invalid prefixes (years, common false positives)
        invalid_prefixes = {
            'FALL', 'SPRING', 'SUMMER', 'WINTER',  # Semesters
            'IN', 'ON', 'AT', 'TO', 'FOR', 'THE',  # Common words
            'NTIL', 'CHIN', 'YEAR', 'PAGE',        # False positives from content
            'AND', 'OR', 'BUT', 'NOT', 'WITH'      # Conjunctions
        }
        
        if prefix in invalid_prefixes:
            return False
            
        # Filter out years (1900-2099)
        if number.startswith(('19', '20')) and len(number) == 4:
            return False
            
        # Must have a reasonable title (not just numbers or very short)
        if len(title.strip()) < 5 or title.strip().isdigit():
            return False
            
        # Filter out titles that look like building names or facilities
        title_lower = title.lower()
        facility_keywords = ['stadium', 'center', 'building', 'facility', 'hall', 'library']
        if any(keyword in title_lower for keyword in facility_keywords):
            return False
            
        return True
    
    def _extract_course_description(self, content: str, start_pos: int) -> str:
        """Extract complete course description including prerequisites"""
        # Get a larger chunk to capture complete course information including prerequisites
        # Most course descriptions with prerequisites are 800-1500 characters
        snippet = content[start_pos:start_pos + 2000]
        
        # Find the end of the description (usually at next course or section)
        end_patterns = [
            r'\n[A-Z]{2,4}\s+\d{4}\.',  # Next course (e.g., "\nCS 1410.")
            r'\n[A-Z][A-Z\s]+:',        # Next section header
            r'\n\n\n',                   # Triple newline (stronger section break)
        ]
        
        end_pos = len(snippet)
        for pattern in end_patterns:
            match = re.search(pattern, snippet)
            if match:
                end_pos = min(end_pos, match.start())
        
        # Extract the full description without arbitrary length limits
        description = snippet[:end_pos].strip()
        
        # Clean up the description
        # Remove excessive whitespace and normalize line breaks
        description = re.sub(r'\s+', ' ', description)
        description = re.sub(r'\*\*', '', description)  # Remove markdown formatting
        
        return description
    
    def _extract_prerequisites(self, description: str) -> List[str]:
        """Extract prerequisite course codes from description"""
        prerequisites = []
        
        # First, find all course codes in the text using a comprehensive pattern
        # This captures course codes like CS 1030, MATH 1010, etc.
        all_course_codes = re.findall(r'\b([A-Z]{2,4})\s+(\d{4}[A-Z]?)\b', description, re.IGNORECASE)
        
        # Convert tuples to formatted strings
        all_courses = [f"{prefix.upper()} {number.upper()}" for prefix, number in all_course_codes]
        
        # Look for prerequisite sections in the text
        prereq_sections = []
        
        # Pattern to find prerequisite sections
        prereq_patterns = [
            r'Prerequisites?:([^.]*?)(?:\.|$)',
            r'Prereq:([^.]*?)(?:\.|$)',
            r'Required:([^.]*?)(?:\.|$)',
        ]
        
        for pattern in prereq_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE | re.DOTALL)
            prereq_sections.extend(matches)
        
        # Extract course codes from prerequisite sections
        for section in prereq_sections:
            # Find all course codes in this prerequisite section
            section_courses = re.findall(r'\b([A-Z]{2,4})\s+(\d{4}[A-Z]?)\b', section, re.IGNORECASE)
            for prefix, number in section_courses:
                course_code = f"{prefix.upper()} {number.upper()}"
                if course_code not in prerequisites:
                    prerequisites.append(course_code)
        
        # If no prerequisite sections found, but we have course codes in the description,
        # check if they appear in contexts that suggest prerequisites
        if not prerequisites and all_courses:
            # Look for course codes that appear before certain keywords
            prereq_context_patterns = [
                r'([A-Z]{2,4}\s+\d{4}[A-Z]?)\s+\(Grade [A-Z] or higher\)',
                r'([A-Z]{2,4}\s+\d{4}[A-Z]?)\s+or higher',
                r'completion of\s+([A-Z]{2,4}\s+\d{4}[A-Z]?)',
            ]
            
            for pattern in prereq_context_patterns:
                matches = re.findall(pattern, description, re.IGNORECASE)
                for match in matches:
                    course_code = re.sub(r'\s+', ' ', match.strip().upper())
                    if course_code not in prerequisites:
                        prerequisites.append(course_code)
        
        # Clean up and validate prerequisites
        cleaned_prereqs = []
        for prereq in prerequisites:
            # Normalize spacing and format
            cleaned = re.sub(r'\s+', ' ', prereq.strip().upper())
            # Validate format (should be like "CS 1030" or "MATH 1010")
            if re.match(r'^[A-Z]{2,4}\s+\d{4}[A-Z]?$', cleaned) and cleaned not in cleaned_prereqs:
                cleaned_prereqs.append(cleaned)
        
        return cleaned_prereqs
    
    def _extract_programs_from_content(self, content: str, url: str) -> Dict[str, ProgramInfo]:
        """Extract program information from content"""
        programs = {}
        
        # Pattern to match program names and types
        program_patterns = [
            r'(Bachelor of [^,\n]+)',
            r'(Master of [^,\n]+)',
            r'([A-Z][^,\n]+ Certificate)',
            r'([A-Z][^,\n]+ Minor)',
        ]
        
        for pattern in program_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                program_name = match.group(1).strip()
                
                # Determine program type and level
                if "Bachelor" in program_name:
                    program_type = "Bachelor"
                    level = "undergraduate"
                elif "Master" in program_name:
                    program_type = "Master"
                    level = "graduate"
                elif "Certificate" in program_name:
                    program_type = "Certificate"
                    level = "undergraduate"  # Assume unless specified
                elif "Minor" in program_name:
                    program_type = "Minor"
                    level = "undergraduate"
                else:
                    continue
                
                # Extract department from URL or content
                department = self._extract_department_from_url(url)
                
                programs[program_name] = ProgramInfo(
                    name=program_name,
                    code=program_name.replace(" ", "_").upper(),
                    type=program_type,
                    level=level,
                    total_credits=120,  # Default assumption
                    description=f"{program_name} program",
                    department=department,
                    requirements=[]
                )
        
        return programs
    
    def _extract_departments_from_content(self, content: str, url: str) -> Dict[str, DepartmentInfo]:
        """Extract department information from content"""
        departments = {}
        
        # Extract department from URL pattern
        dept_match = re.search(r'/([^/]+)/?$', url)
        if dept_match:
            dept_slug = dept_match.group(1)
            
            # Convert slug to department name
            dept_name = dept_slug.replace('-', ' ').title()
            
            # Try to find department prefix from course codes in content
            prefixes = set(re.findall(r'([A-Z]{2,4})\s+\d{4}', content))
            main_prefix = max(prefixes, key=lambda p: content.count(p)) if prefixes else "UNKN"
            
            departments[dept_name] = DepartmentInfo(
                name=dept_name,
                code=dept_slug.upper(),
                prefix=main_prefix,
                description=f"{dept_name} Department",
                programs=[],
                courses=[]
            )
        
        return departments
    
    def _extract_department_from_url(self, url: str) -> str:
        """Extract department name from URL"""
        dept_match = re.search(r'/([^/]+)/?$', url)
        if dept_match:
            return dept_match.group(1).replace('-', ' ').title()
        return "Unknown Department"
    
    async def _populate_graph(self, academic_data: Dict):
        """Populate both Neo4j graph and Supabase tables with academic entities"""
        print("📊 Populating Neo4j graph and Supabase tables with academic entities...")
        
        # First populate Neo4j (existing functionality)
        await self._populate_neo4j(academic_data)
        
        # Then populate Supabase tables
        await self._populate_supabase_tables(academic_data)
    
    async def _populate_neo4j(self, academic_data: Dict):
        """Populate the Neo4j graph with academic entities"""
        print("📊 Populating Neo4j graph...")
        
        if not self.neo4j_driver:
            print("❌ No Neo4j connection available")
            return
        
        with self.neo4j_driver.session() as session:
            # Create university node
            session.run("""
                MERGE (u:University {name: "Utah Tech University"})
                SET u.location = "St. George, Utah",
                    u.website = "https://utahtech.edu",
                    u.created_at = datetime()
            """)
            
            # Create departments (MERGE on prefix since that's the unique constraint)
            for dept_name, dept_info in academic_data["departments"].items():
                session.run("""
                    MERGE (d:Department {prefix: $prefix})
                    SET d.name = $name,
                        d.code = $code,
                        d.description = $description,
                        d.created_at = datetime()
                """, {
                    "prefix": dept_info.prefix,
                    "name": dept_info.name,
                    "code": dept_info.code,
                    "description": dept_info.description
                })
            
            # Create courses
            for course_code, course_info in academic_data["courses"].items():
                session.run("""
                    MERGE (c:Course {code: $code})
                    SET c.prefix = $prefix,
                        c.number = $number,
                        c.title = $title,
                        c.credits = $credits,
                        c.level = $level,
                        c.description = $description,
                        c.prerequisites_text = $prerequisites_text,
                        c.offered_semesters = $offered_semesters,
                        c.created_at = datetime()
                """, {
                    "code": course_info.code,
                    "prefix": course_info.prefix,
                    "number": course_info.number,
                    "title": course_info.title,
                    "credits": course_info.credits,
                    "level": course_info.level,
                    "description": course_info.description,
                    "prerequisites_text": ", ".join(course_info.prerequisites),
                    "offered_semesters": course_info.offered_semesters
                })
            
            # Create programs (MERGE on name since that's the unique constraint)
            for program_name, program_info in academic_data["programs"].items():
                session.run("""
                    MERGE (p:Program {name: $name})
                    SET p.code = $code,
                        p.type = $type,
                        p.level = $level,
                        p.total_credits = $total_credits,
                        p.description = $description,
                        p.created_at = datetime()
                """, {
                    "name": program_info.name,
                    "code": program_info.code,
                    "type": program_info.type,
                    "level": program_info.level,
                    "total_credits": program_info.total_credits,
                    "description": program_info.description
                })
        
        print(f"✅ Neo4j: Created {len(academic_data['departments'])} departments, {len(academic_data['courses'])} courses, {len(academic_data['programs'])} programs")
    
    async def _populate_supabase_tables(self, academic_data: Dict):
        """Populate Supabase academic tables with extracted data"""
        print("📊 Populating Supabase tables...")
        
        try:
            # Clear existing data to avoid duplicates
            print("   🧹 Clearing existing academic data...")
            # Use truncate-like approach by deleting all records
            self.supabase.table('academic_courses').delete().neq('course_code', '').execute()
            self.supabase.table('academic_programs').delete().neq('program_name', '').execute()
            self.supabase.table('academic_departments').delete().neq('department_name', '').execute()
            
            # Insert departments (with duplicate handling)
            if academic_data.get("departments"):
                print(f"   🏢 Inserting {len(academic_data['departments'])} departments...")
                dept_records = []
                seen_prefixes = set()
                
                for dept_name, dept_info in academic_data["departments"].items():
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
                    self.supabase.table('academic_departments').upsert(dept_records).execute()
                    print(f"   ✅ Upserted {len(dept_records)} unique departments")
            
            # Insert courses (with duplicate handling)
            if academic_data.get("courses"):
                print(f"   📚 Inserting {len(academic_data['courses'])} courses...")
                course_records = []
                seen_courses = set()
                
                for course_code, course_info in academic_data["courses"].items():
                    # Skip duplicates based on course_code
                    if course_info.code in seen_courses:
                        continue
                    seen_courses.add(course_info.code)
                    
                    course_records.append({
                        'course_code': course_info.code,
                        'title': course_info.title,
                        'credits': course_info.credits,
                        'level': course_info.level,
                        'description': course_info.description[:1000] if course_info.description else None,  # Truncate description
                        'prerequisites': ', '.join(course_info.prerequisites) if course_info.prerequisites else None,
                        'prefix': course_info.prefix,
                        'course_number': course_info.number,
                        'source_id': 'catalog.utahtech.edu'
                    })
                
                if course_records:
                    # Insert in batches using upsert to avoid size limits and duplicates
                    batch_size = 100
                    for i in range(0, len(course_records), batch_size):
                        batch = course_records[i:i + batch_size]
                        self.supabase.table('academic_courses').upsert(batch).execute()
                    print(f"   ✅ Upserted {len(course_records)} unique courses")
            
            # Insert programs (with duplicate handling)
            if academic_data.get("programs"):
                print(f"   🎓 Inserting {len(academic_data['programs'])} programs...")
                program_records = []
                seen_programs = set()
                
                for program_name, program_info in academic_data["programs"].items():
                    # Skip duplicates based on program_name (truncated)
                    truncated_name = program_info.name[:500]  # Truncate to avoid index issues
                    if truncated_name in seen_programs:
                        continue
                    seen_programs.add(truncated_name)
                    
                    program_records.append({
                        'program_name': truncated_name,
                        'program_type': program_info.type,
                        'level': program_info.level,
                        'description': program_info.description[:1000] if program_info.description else None,  # Truncate description
                        'source_id': 'catalog.utahtech.edu'
                    })
                
                if program_records:
                    # Insert in batches using upsert
                    batch_size = 100
                    for i in range(0, len(program_records), batch_size):
                        batch = program_records[i:i + batch_size]
                        self.supabase.table('academic_programs').upsert(batch).execute()
                    print(f"   ✅ Upserted {len(program_records)} unique programs")
            
            print("✅ Supabase tables populated successfully!")
            
        except Exception as e:
            print(f"❌ Error populating Supabase tables: {e}")
            # Continue with Neo4j population even if Supabase fails
    
    async def _create_relationships(self, academic_data: Dict):
        """Create relationships between academic entities"""
        print("🔗 Creating relationships between academic entities...")
        
        if not self.neo4j_driver:
            print("❌ No Neo4j connection available")
            return
        
        relationship_counts = {
            "department_course": 0,
            "prerequisites": 0,
            "program_department": 0,
            "university_college": 0
        }
        
        with self.neo4j_driver.session() as session:
            # 1. Connect courses to departments
            print("   🏢 Linking courses to departments...")
            for course_code, course_info in academic_data["courses"].items():
                result = session.run("""
                    MATCH (c:Course {code: $course_code})
                    MATCH (d:Department {prefix: $prefix})
                    MERGE (d)-[:OFFERS_COURSE]->(c)
                    MERGE (c)-[:BELONGS_TO_DISCIPLINE]->(d)
                    RETURN count(*) as created
                """, {
                    "course_code": course_info.code,
                    "prefix": course_info.prefix
                })
                if result.single():
                    relationship_counts["department_course"] += 1
            
            # 2. Create prerequisite relationships
            print("   📚 Creating prerequisite relationships...")
            prereq_created = 0
            for course_code, course_info in academic_data["courses"].items():
                if course_info.prerequisites:
                    print(f"     Processing {course_info.code} with prereqs: {course_info.prerequisites}")
                    for prereq_code in course_info.prerequisites:
                        try:
                            result = session.run("""
                                MATCH (prereq:Course {code: $prereq_code})
                                MATCH (course:Course {code: $course_code})
                                MERGE (prereq)-[:PREREQUISITE_FOR]->(course)
                                RETURN count(*) as created
                            """, {
                                "prereq_code": prereq_code,
                                "course_code": course_info.code
                            })
                            if result.single():
                                prereq_created += 1
                        except Exception as e:
                            print(f"     ⚠️ Failed to create prerequisite {prereq_code} -> {course_info.code}: {e}")
            
            relationship_counts["prerequisites"] = prereq_created
            
            # 3. Connect programs to departments
            print("   🎓 Linking programs to departments...")
            for program_name, program_info in academic_data["programs"].items():
                if program_info.department:
                    # Try to match department by name or extract prefix
                    dept_prefix = self._extract_department_prefix(program_info.department)
                    if dept_prefix:
                        try:
                            result = session.run("""
                                MATCH (p:Program {name: $program_name})
                                MATCH (d:Department {prefix: $dept_prefix})
                                MERGE (d)-[:OFFERS_PROGRAM]->(p)
                                MERGE (p)-[:BELONGS_TO_DEPARTMENT]->(d)
                                RETURN count(*) as created
                            """, {
                                "program_name": program_info.name,
                                "dept_prefix": dept_prefix
                            })
                            if result.single():
                                relationship_counts["program_department"] += 1
                        except Exception as e:
                            print(f"     ⚠️ Failed to link program {program_info.name} to department: {e}")
            
            # 4. Connect university to colleges/departments
            print("   🏛️ Creating university hierarchy...")
            try:
                result = session.run("""
                    MATCH (u:University), (d:Department)
                    WHERE NOT EXISTS((u)-[:HAS_DEPARTMENT]->(d))
                    MERGE (u)-[:HAS_DEPARTMENT]->(d)
                    RETURN count(*) as created
                """)
                if result.single():
                    relationship_counts["university_college"] = result.single()["created"]
            except Exception as e:
                print(f"     ⚠️ Failed to create university hierarchy: {e}")
        
        print(f"   ✅ Relationships created:")
        print(f"      Department-Course: {relationship_counts['department_course']}")
        print(f"      Prerequisites: {relationship_counts['prerequisites']}")
        print(f"      Program-Department: {relationship_counts['program_department']}")
        print(f"      University-Department: {relationship_counts['university_college']}")
        
        return relationship_counts
    
    def _extract_department_prefix(self, department_name: str) -> str:
        """Extract department prefix from department name"""
        # Common mappings
        dept_mappings = {
            "art": "ART",
            "computer science": "CS",
            "nursing": "NURS",
            "business": "BUS",
            "english": "ENGL",
            "mathematics": "MATH",
            "biology": "BIOL",
            "chemistry": "CHEM",
            "physics": "PHYS",
            "psychology": "PSY",
            "history": "HIST",
            "geography": "GEOG"
        }
        
        dept_lower = department_name.lower().strip()
        for key, prefix in dept_mappings.items():
            if key in dept_lower:
                return prefix
        
        # Fallback: use first few letters
        words = dept_lower.split()
        if words:
            return words[0][:4].upper()
        
        return ""
        
        print("✅ Relationships created successfully")


async def main():
    """Main function to build the academic graph"""
    builder = AcademicGraphBuilder()
    
    try:
        academic_data = await builder.build_academic_graph()
        
        # Print summary
        print("\n📊 Academic Graph Summary:")
        print(f"   Departments: {len(academic_data.get('departments', {}))}")
        print(f"   Courses: {len(academic_data.get('courses', {}))}")
        print(f"   Programs: {len(academic_data.get('programs', {}))}")
        
        # Show sample courses
        courses = academic_data.get("courses", {})
        if courses:
            print(f"\n📚 Sample Courses:")
            for i, (code, info) in enumerate(list(courses.items())[:5]):
                print(f"   {code}: {info.title} ({info.credits} credits, {info.level})")
                if info.prerequisites:
                    print(f"      Prerequisites: {', '.join(info.prerequisites)}")
        
    except Exception as e:
        print(f"❌ Error building academic graph: {e}")
    finally:
        builder.close()


if __name__ == "__main__":
    asyncio.run(main())
