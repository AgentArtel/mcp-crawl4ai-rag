#!/usr/bin/env python3
"""
Test Data Population Script for Utah Tech MCP Server

This script populates Supabase tables with comprehensive test data to enable
testing of all 27 MCP tools including academic planning, IAP management, 
and data extraction tools.
"""

import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

class TestDataPopulator:
    """Populates Supabase with comprehensive test data"""
    
    def __init__(self):
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'), 
            os.getenv('SUPABASE_SERVICE_KEY')
        )
        
    async def populate_all_test_data(self, clear_existing: bool = True):
        """Populate all tables with test data"""
        print("🚀 Starting Test Data Population...")
        
        if clear_existing:
            await self._clear_existing_data()
        
        # Populate in dependency order
        await self._populate_sources()
        await self._populate_departments()
        await self._populate_courses()
        await self._populate_programs()
        await self._populate_crawled_pages()
        await self._populate_iap_templates()
        await self._populate_general_education()
        await self._populate_market_research()
        
        print("\n✅ Test Data Population Complete!")
        await self._show_summary()
    
    async def _clear_existing_data(self):
        """Clear existing test data"""
        print("\n🧹 Clearing existing data...")
        
        tables = [
            'iap_market_research',
            'iap_general_education', 
            'iap_templates',
            'crawled_pages',
            'academic_programs',
            'academic_courses',
            'academic_departments',
            'sources'
        ]
        
        for table in tables:
            try:
                self.supabase.table(table).delete().neq('id', 0).execute()
                print(f"   ✅ Cleared {table}")
            except Exception as e:
                print(f"   ⚠️ Could not clear {table}: {e}")
    
    async def _populate_sources(self):
        """Populate sources table"""
        print("\n1️⃣ Populating Sources...")
        
        sources = [
            {
                'source_id': 'catalog.utahtech.edu',
                'domain': 'catalog.utahtech.edu',
                'summary': 'Utah Tech University Academic Catalog',
                'total_pages': 500,
                'total_words': 250000,
                'last_crawled': datetime.now().isoformat()
            }
        ]
        
        self.supabase.table('sources').upsert(sources).execute()
        print(f"   ✅ Inserted {len(sources)} sources")
    
    async def _populate_departments(self):
        """Populate academic departments"""
        print("\n2️⃣ Populating Departments...")
        
        departments = [
            {
                'department_code': 'PSYC',
                'department_name': 'Psychology Department',
                'prefix': 'PSYC',
                'description': 'Department of Psychology offering undergraduate and graduate programs in psychology, counseling, and related fields.',
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'department_code': 'BIOL',
                'department_name': 'Biology Department', 
                'prefix': 'BIOL',
                'description': 'Department of Biology offering comprehensive programs in biological sciences, biotechnology, and environmental science.',
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'department_code': 'BUSN',
                'department_name': 'Business Department',
                'prefix': 'BUSN', 
                'description': 'Department of Business offering programs in business administration, management, marketing, and entrepreneurship.',
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'department_code': 'MATH',
                'department_name': 'Mathematics Department',
                'prefix': 'MATH',
                'description': 'Department of Mathematics offering programs in mathematics, statistics, and applied mathematics.',
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'department_code': 'ENGL',
                'department_name': 'English Department',
                'prefix': 'ENGL',
                'description': 'Department of English offering programs in English literature, composition, and creative writing.',
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'department_code': 'COMM',
                'department_name': 'Communication Department',
                'prefix': 'COMM',
                'description': 'Department of Communication offering programs in communication studies, media, and public relations.',
                'source_id': 'catalog.utahtech.edu'
            }
        ]
        
        self.supabase.table('academic_departments').upsert(departments).execute()
        print(f"   ✅ Inserted {len(departments)} departments")
    
    async def _populate_courses(self):
        """Populate academic courses"""
        print("\n3️⃣ Populating Courses...")
        
        courses = [
            # Psychology Courses
            {
                'course_code': 'PSYC 1010',
                'course_title': 'General Psychology',
                'credits': 4,
                'level': 'lower-division',
                'department_prefix': 'PSYC',
                'description': 'Introduction to the scientific study of behavior and mental processes. Covers major areas of psychology including learning, memory, cognition, development, personality, and social psychology.',
                'prerequisites': [],
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'course_code': 'PSYC 2010',
                'course_title': 'Developmental Psychology',
                'credits': 3,
                'level': 'lower-division', 
                'department_prefix': 'PSYC',
                'description': 'Study of human development from conception through death. Examines physical, cognitive, and social-emotional development across the lifespan.',
                'prerequisites': ['PSYC 1010'],
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'course_code': 'PSYC 3030',
                'course_title': 'Research Methods in Psychology',
                'credits': 4,
                'level': 'upper-division',
                'department_prefix': 'PSYC',
                'description': 'Introduction to research methods and statistical analysis in psychology. Includes experimental design, data collection, and interpretation of results.',
                'prerequisites': ['PSYC 1010', 'MATH 1040'],
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'course_code': 'PSYC 4400',
                'course_title': 'Advanced Social Psychology',
                'credits': 3,
                'level': 'upper-division',
                'department_prefix': 'PSYC',
                'description': 'Advanced study of social psychological theories and research. Topics include attitude formation, group dynamics, and interpersonal relationships.',
                'prerequisites': ['PSYC 3030'],
                'source_id': 'catalog.utahtech.edu'
            },
            
            # Biology Courses
            {
                'course_code': 'BIOL 1010',
                'course_title': 'General Biology',
                'credits': 4,
                'level': 'lower-division',
                'department_prefix': 'BIOL',
                'description': 'Introduction to biological principles including cell structure, genetics, evolution, and ecology. Includes laboratory component.',
                'prerequisites': [],
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'course_code': 'BIOL 3450',
                'course_title': 'Molecular Biology',
                'credits': 4,
                'level': 'upper-division',
                'department_prefix': 'BIOL',
                'description': 'Study of molecular mechanisms of gene expression, protein synthesis, and cellular regulation. Includes advanced laboratory techniques.',
                'prerequisites': ['BIOL 1010', 'CHEM 1110'],
                'source_id': 'catalog.utahtech.edu'
            },
            
            # Business Courses
            {
                'course_code': 'BUSN 1010',
                'course_title': 'Introduction to Business',
                'credits': 3,
                'level': 'lower-division',
                'department_prefix': 'BUSN',
                'description': 'Overview of business principles, including management, marketing, finance, and entrepreneurship.',
                'prerequisites': [],
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'course_code': 'BUSN 4200',
                'course_title': 'Strategic Management',
                'credits': 3,
                'level': 'upper-division',
                'department_prefix': 'BUSN',
                'description': 'Capstone course integrating business functions. Focus on strategic planning, competitive analysis, and organizational leadership.',
                'prerequisites': ['BUSN 1010', 'BUSN 3100'],
                'source_id': 'catalog.utahtech.edu'
            },
            
            # Math Courses
            {
                'course_code': 'MATH 1040',
                'course_title': 'Introduction to Statistics',
                'credits': 4,
                'level': 'lower-division',
                'department_prefix': 'MATH',
                'description': 'Introduction to statistical concepts including descriptive statistics, probability, hypothesis testing, and regression analysis.',
                'prerequisites': [],
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'course_code': 'MATH 3400',
                'course_title': 'Advanced Statistics',
                'credits': 3,
                'level': 'upper-division',
                'department_prefix': 'MATH',
                'description': 'Advanced statistical methods including ANOVA, multivariate analysis, and non-parametric statistics.',
                'prerequisites': ['MATH 1040'],
                'source_id': 'catalog.utahtech.edu'
            },
            
            # English Courses
            {
                'course_code': 'ENGL 1010',
                'course_title': 'College Writing',
                'credits': 3,
                'level': 'lower-division',
                'department_prefix': 'ENGL',
                'description': 'Development of college-level writing skills including essay composition, research methods, and critical thinking.',
                'prerequisites': [],
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'course_code': 'ENGL 3500',
                'course_title': 'Advanced Composition',
                'credits': 3,
                'level': 'upper-division',
                'department_prefix': 'ENGL',
                'description': 'Advanced study of rhetorical strategies and writing techniques for various audiences and purposes.',
                'prerequisites': ['ENGL 1010'],
                'source_id': 'catalog.utahtech.edu'
            },
            
            # Communication Courses
            {
                'course_code': 'COMM 1010',
                'course_title': 'Public Speaking',
                'credits': 3,
                'level': 'lower-division',
                'department_prefix': 'COMM',
                'description': 'Development of public speaking skills including speech preparation, delivery techniques, and audience analysis.',
                'prerequisites': [],
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'course_code': 'COMM 3200',
                'course_title': 'Interpersonal Communication',
                'credits': 3,
                'level': 'upper-division',
                'department_prefix': 'COMM',
                'description': 'Study of communication in interpersonal relationships including verbal and nonverbal communication, conflict resolution, and relationship development.',
                'prerequisites': ['COMM 1010'],
                'source_id': 'catalog.utahtech.edu'
            }
        ]
        
        self.supabase.table('academic_courses').upsert(courses).execute()
        print(f"   ✅ Inserted {len(courses)} courses")
    
    async def _populate_programs(self):
        """Populate academic programs"""
        print("\n4️⃣ Populating Programs...")
        
        programs = [
            {
                'program_code': 'PSYC-BS',
                'program_name': 'Bachelor of Science in Psychology',
                'degree_type': 'Bachelor',
                'department_prefix': 'PSYC',
                'description': 'Comprehensive undergraduate program in psychology preparing students for graduate study or careers in mental health, research, and human services.',
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'program_code': 'BIOL-BS',
                'program_name': 'Bachelor of Science in Biology',
                'degree_type': 'Bachelor',
                'department_prefix': 'BIOL',
                'description': 'Rigorous undergraduate program in biological sciences with emphasis on research, laboratory skills, and preparation for graduate study or professional programs.',
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'program_code': 'BUSN-BS',
                'program_name': 'Bachelor of Science in Business Administration',
                'degree_type': 'Bachelor',
                'department_prefix': 'BUSN',
                'description': 'Comprehensive business program covering management, marketing, finance, and entrepreneurship with practical application and internship opportunities.',
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'program_code': 'BIS',
                'program_name': 'Bachelor of Individualized Studies',
                'degree_type': 'Bachelor',
                'department_prefix': 'INDS',
                'description': 'Flexible interdisciplinary program allowing students to design custom degree emphasis across multiple disciplines to meet specific career and academic goals.',
                'source_id': 'catalog.utahtech.edu'
            },
            {
                'program_code': 'PSYC-MS',
                'program_name': 'Master of Science in Psychology',
                'degree_type': 'Master',
                'department_prefix': 'PSYC',
                'description': 'Graduate program in psychology with emphasis on research methods, advanced theory, and preparation for doctoral study or professional practice.',
                'source_id': 'catalog.utahtech.edu'
            }
        ]
        
        self.supabase.table('academic_programs').upsert(programs).execute()
        print(f"   ✅ Inserted {len(programs)} programs")
    
    async def _populate_crawled_pages(self):
        """Populate crawled pages for RAG functionality"""
        print("\n5️⃣ Populating Crawled Pages...")
        
        # Sample academic content for RAG testing
        pages = [
            {
                'url': 'https://catalog.utahtech.edu/programs/psychology/',
                'title': 'Psychology Department Programs',
                'content': 'The Psychology Department at Utah Tech University offers comprehensive undergraduate and graduate programs designed to provide students with a strong foundation in psychological science. Our Bachelor of Science in Psychology program emphasizes research methods, statistical analysis, and practical application of psychological principles. Students can choose from various concentration areas including clinical psychology, developmental psychology, and social psychology. The program prepares graduates for careers in mental health services, research, education, and human resources, or for advanced study in graduate programs.',
                'source_id': 'catalog.utahtech.edu',
                'chunk_number': 1,
                'metadata': {
                    'department': 'Psychology',
                    'content_type': 'program_overview',
                    'programs': ['Bachelor of Science in Psychology', 'Master of Science in Psychology']
                }
            },
            {
                'url': 'https://catalog.utahtech.edu/courses/psychology/',
                'title': 'Psychology Course Catalog',
                'content': 'PSYC 1010 - General Psychology (4 credits): Introduction to the scientific study of behavior and mental processes. This foundational course covers major areas including learning, memory, cognition, development, personality, social psychology, and abnormal psychology. Students will learn about research methods and statistical concepts used in psychological research. Prerequisites: None. PSYC 3030 - Research Methods in Psychology (4 credits): Comprehensive introduction to research design, data collection methods, and statistical analysis in psychology. Students will design and conduct original research projects. Prerequisites: PSYC 1010, MATH 1040.',
                'source_id': 'catalog.utahtech.edu',
                'chunk_number': 1,
                'metadata': {
                    'department': 'Psychology',
                    'content_type': 'course_catalog',
                    'courses': ['PSYC 1010', 'PSYC 3030']
                }
            },
            {
                'url': 'https://catalog.utahtech.edu/programs/biology/',
                'title': 'Biology Department Programs',
                'content': 'The Biology Department offers a rigorous Bachelor of Science program that prepares students for careers in biological research, healthcare, environmental science, and biotechnology. Our curriculum emphasizes hands-on laboratory experience, field research opportunities, and interdisciplinary collaboration. Students can specialize in areas such as molecular biology, ecology, genetics, or pre-professional tracks for medical, dental, or veterinary school. The program includes advanced courses in biochemistry, cell biology, genetics, and evolution.',
                'source_id': 'catalog.utahtech.edu',
                'chunk_number': 1,
                'metadata': {
                    'department': 'Biology',
                    'content_type': 'program_overview',
                    'programs': ['Bachelor of Science in Biology']
                }
            },
            {
                'url': 'https://catalog.utahtech.edu/programs/individualized-studies/',
                'title': 'Bachelor of Individualized Studies Program',
                'content': 'The Bachelor of Individualized Studies (BIS) program is designed for students who wish to create a unique, interdisciplinary degree that meets their specific academic and career goals. Students work with faculty advisors to develop a personalized curriculum that draws from at least three different academic disciplines. The program requires 120 total credit hours with at least 40 upper-division credits. Students must complete concentration areas with minimum credit requirements and demonstrate coherent academic planning through their Individualized Academic Plan (IAP). The program emphasizes critical thinking, research skills, and practical application of knowledge across disciplines.',
                'source_id': 'catalog.utahtech.edu',
                'chunk_number': 1,
                'metadata': {
                    'department': 'Individualized Studies',
                    'content_type': 'program_overview',
                    'programs': ['Bachelor of Individualized Studies'],
                    'requirements': ['120 total credits', '40 upper-division credits', '3+ disciplines']
                }
            }
        ]
        
        self.supabase.table('crawled_pages').upsert(pages).execute()
        print(f"   ✅ Inserted {len(pages)} crawled pages")
    
    async def _populate_iap_templates(self):
        """Populate IAP templates for testing"""
        print("\n6️⃣ Populating IAP Templates...")
        
        templates = [
            {
                'student_name': 'Test Student',
                'student_id': 'TEST123',
                'student_email': 'test@utahtech.edu',
                'degree_emphasis': 'Psychology and Communication',
                'mission_statement': 'To develop expertise in psychological principles and communication strategies to pursue a career in organizational psychology and human resources management.',
                'program_goals': [
                    'Demonstrate mastery of psychological theories and research methods',
                    'Apply communication principles to organizational settings',
                    'Integrate interdisciplinary knowledge to solve complex human behavior problems',
                    'Conduct independent research in applied psychology'
                ],
                'program_learning_outcomes': [
                    {
                        'outcome': 'Research and Analysis',
                        'description': 'Students will design and conduct psychological research using appropriate methodologies and statistical analysis.'
                    },
                    {
                        'outcome': 'Communication Skills',
                        'description': 'Students will demonstrate effective written and oral communication skills for diverse audiences.'
                    },
                    {
                        'outcome': 'Critical Thinking',
                        'description': 'Students will analyze complex problems using interdisciplinary perspectives and evidence-based reasoning.'
                    }
                ],
                'concentration_areas': ['Psychology', 'Communication', 'Business'],
                'course_mappings': {
                    'Psychology': ['PSYC 1010', 'PSYC 2010', 'PSYC 3030', 'PSYC 4400'],
                    'Communication': ['COMM 1010', 'COMM 3200'],
                    'Business': ['BUSN 1010', 'BUSN 4200']
                },
                'semester_year_inds3800': 'Fall 2024',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        ]
        
        self.supabase.table('iap_templates').upsert(templates).execute()
        print(f"   ✅ Inserted {len(templates)} IAP templates")
    
    async def _populate_general_education(self):
        """Populate general education tracking data"""
        print("\n7️⃣ Populating General Education Data...")
        
        ge_data = [
            {
                'student_id': 'TEST123',
                'category': 'English',
                'requirement': 'College Writing',
                'credits_required': 3,
                'credits_completed': 3,
                'courses_completed': ['ENGL 1010'],
                'status': 'completed',
                'created_at': datetime.now().isoformat()
            },
            {
                'student_id': 'TEST123',
                'category': 'Mathematics',
                'requirement': 'Quantitative Reasoning',
                'credits_required': 4,
                'credits_completed': 4,
                'courses_completed': ['MATH 1040'],
                'status': 'completed',
                'created_at': datetime.now().isoformat()
            },
            {
                'student_id': 'TEST123',
                'category': 'Natural Sciences',
                'requirement': 'Laboratory Science',
                'credits_required': 4,
                'credits_completed': 4,
                'courses_completed': ['BIOL 1010'],
                'status': 'completed',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        self.supabase.table('iap_general_education').upsert(ge_data).execute()
        print(f"   ✅ Inserted {len(ge_data)} GE records")
    
    async def _populate_market_research(self):
        """Populate market research data"""
        print("\n8️⃣ Populating Market Research Data...")
        
        market_data = [
            {
                'degree_emphasis': 'Psychology and Communication',
                'geographic_focus': 'Utah',
                'job_market_score': 85,
                'salary_range_min': 45000,
                'salary_range_max': 75000,
                'growth_projection': 'Above Average',
                'key_skills': ['Research Methods', 'Data Analysis', 'Communication', 'Project Management'],
                'top_employers': ['Healthcare Systems', 'Educational Institutions', 'Government Agencies', 'Consulting Firms'],
                'viability_score': 90,
                'recommendations': [
                    'Strong job market in Utah for psychology and communication professionals',
                    'Consider additional certification in data analysis or project management',
                    'Network with local healthcare and education organizations'
                ],
                'created_at': datetime.now().isoformat()
            }
        ]
        
        self.supabase.table('iap_market_research').upsert(market_data).execute()
        print(f"   ✅ Inserted {len(market_data)} market research records")
    
    async def _show_summary(self):
        """Show summary of populated data"""
        print("\n📊 Test Data Summary:")
        
        tables = [
            'sources', 'academic_departments', 'academic_courses', 
            'academic_programs', 'crawled_pages', 'iap_templates',
            'iap_general_education', 'iap_market_research'
        ]
        
        for table in tables:
            try:
                result = self.supabase.table(table).select('*', count='exact').execute()
                count = result.count if hasattr(result, 'count') else len(result.data)
                print(f"   📋 {table}: {count} records")
            except Exception as e:
                print(f"   ❌ {table}: Error - {e}")

async def main():
    """Main execution function"""
    populator = TestDataPopulator()
    await populator.populate_all_test_data(clear_existing=True)
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
