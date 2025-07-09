#!/usr/bin/env python3
"""
Create Realistic Test Data for IAP MCP Tools

This script creates comprehensive test data that matches the exact Supabase schema
to enable thorough testing of all 31 MCP tools.
"""

import os
import json
import asyncio
from datetime import datetime, date
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

class RealisticTestDataCreator:
    """Creates realistic test data matching the exact Supabase schema"""
    
    def __init__(self):
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'), 
            os.getenv('SUPABASE_SERVICE_KEY')
        )
        
    async def create_comprehensive_test_data(self):
        """Create comprehensive test data for all IAP tools"""
        print("🎓 Creating Realistic Test Data for IAP MCP Tools...")
        
        # Create test data in logical order (respecting foreign key dependencies)
        iap_id = await self._create_iap_template()
        await self._create_course_mappings(iap_id)
        await self._create_general_education_data(iap_id)
        await self._create_market_research_data(iap_id)
        await self._create_concentration_validation_data(iap_id)
        await self._create_course_plo_mappings(iap_id)
        
        # Create additional test students
        await self._create_additional_test_students()
        
        print("\n✅ Comprehensive test data creation complete!")
        print("🚀 Ready for MCP tool testing!")
        
    async def _create_iap_template(self):
        """Create a comprehensive IAP template"""
        print("\n1️⃣ Creating IAP Template...")
        
        iap_template = {
            'student_name': 'Sarah Johnson',
            'student_id': 'SJ2024001',
            'student_email': 'sarah.johnson@utahtech.edu',
            'student_phone': '(435) 555-0123',
            'degree_emphasis': 'Psychology and Digital Media',
            
            # Cover Letter Data
            'cover_letter_data': {
                'career_goals': 'Mental health content creator and digital wellness advocate',
                'market_research_summary': 'Growing demand for digital mental health resources',
                'unique_value_proposition': 'Combining psychological expertise with digital media skills'
            },
            
            # Program Definition
            'mission_statement': 'The BIS with an emphasis in Psychology and Digital Media at UT prepares students to create evidence-based digital content that promotes mental health awareness and wellness through innovative multimedia approaches.',
            
            'program_goals': [
                'Students will demonstrate mastery of psychological research methods and theories',
                'Students will create professional-quality digital media content across multiple platforms',
                'Students will integrate interdisciplinary knowledge to address real-world mental health challenges',
                'Students will develop ethical frameworks for digital mental health communication'
            ],
            
            'program_learning_outcomes': [
                {
                    'id': 'PLO1',
                    'description': 'Apply psychological theories and research methods to analyze human behavior',
                    'assessment_methods': ['Research projects', 'Case study analyses', 'Comprehensive exams']
                },
                {
                    'id': 'PLO2', 
                    'description': 'Design and produce digital media content using industry-standard tools and techniques',
                    'assessment_methods': ['Portfolio development', 'Capstone project', 'Peer reviews']
                },
                {
                    'id': 'PLO3',
                    'description': 'Integrate knowledge from psychology and digital media to create innovative solutions',
                    'assessment_methods': ['Interdisciplinary projects', 'Internship evaluations', 'Thesis defense']
                }
            ],
            
            # Course Mappings
            'course_mappings': {
                'PLO1': ['PSYC 1010', 'PSYC 3030', 'PSYC 3500', 'PSYC 4800'],
                'PLO2': ['MDIA 1010', 'MDIA 2400', 'MDIA 3400', 'MDIA 4500'],
                'PLO3': ['INDS 3800', 'INDS 4800', 'COMM 3150', 'PSYC 4900']
            },
            
            'concentration_areas': ['Psychology', 'Digital Media', 'Communication'],
            
            # Academic Plan Tracking
            'general_education': {
                'completed_credits': 36,
                'remaining_requirements': ['Fine Arts', 'Physical Science Lab']
            },
            
            'inds_core_courses': {
                'INDS 3800': {'status': 'planned', 'semester': 'Fall 2024'},
                'INDS 4800': {'status': 'planned', 'semester': 'Spring 2025'}
            },
            
            'concentration_courses': {
                'Psychology': {
                    'lower_division': ['PSYC 1010', 'PSYC 2000'],
                    'upper_division': ['PSYC 3030', 'PSYC 3500', 'PSYC 4800', 'PSYC 4900']
                },
                'Digital Media': {
                    'lower_division': ['MDIA 1010', 'MDIA 2400'],
                    'upper_division': ['MDIA 3400', 'MDIA 4500', 'MDIA 4600']
                },
                'Communication': {
                    'lower_division': ['COMM 1010', 'COMM 2110'],
                    'upper_division': ['COMM 3150', 'COMM 4200']
                }
            },
            
            # Requirements Validation
            'credit_summary': {
                'total_credits': 120,
                'upper_division_credits': 45,
                'concentration_credits': 42,
                'general_education_credits': 36,
                'inds_core_credits': 6
            },
            
            'completion_status': {
                'mission_statement': True,
                'program_goals': True,
                'program_learning_outcomes': True,
                'course_mappings': True,
                'concentration_areas': True,
                'cover_letter': False,
                'academic_plan': True
            },
            
            'validation_results': {
                'overall_status': 'valid',
                'credit_requirements_met': True,
                'discipline_requirements_met': True,
                'concentration_requirements_met': True,
                'last_validated': datetime.now().isoformat()
            },
            
            # Metadata
            'semester_year_inds3800': 'Fall 2024',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table('iap_templates').upsert(iap_template).execute()
            iap_id = result.data[0]['id']
            print(f"   ✅ Created IAP template for {iap_template['student_name']} (ID: {iap_id})")
            return iap_id
        except Exception as e:
            print(f"   ❌ Failed to create IAP template: {e}")
            return None
    
    async def _create_course_mappings(self, iap_id):
        """Create detailed course mappings"""
        if not iap_id:
            return
            
        print("\n2️⃣ Creating Course Mappings...")
        
        course_mappings = [
            # Psychology Courses
            {
                'iap_id': iap_id,
                'course_code': 'PSYC 1010',
                'course_title': 'General Psychology',
                'course_credits': 3,
                'course_level': 'lower-division',
                'concentration_area': 'Psychology',
                'mapped_plos': ['PLO1'],
                'course_type': 'concentration',
                'semester_planned': 'Fall 2023',
                'completion_status': 'completed',
                'grade': 'A-'
            },
            {
                'iap_id': iap_id,
                'course_code': 'PSYC 3030',
                'course_title': 'Research Methods in Psychology',
                'course_credits': 4,
                'course_level': 'upper-division',
                'concentration_area': 'Psychology',
                'mapped_plos': ['PLO1', 'PLO3'],
                'course_type': 'concentration',
                'semester_planned': 'Spring 2024',
                'completion_status': 'completed',
                'grade': 'A'
            },
            # Digital Media Courses
            {
                'iap_id': iap_id,
                'course_code': 'MDIA 1010',
                'course_title': 'Introduction to Digital Media',
                'course_credits': 3,
                'course_level': 'lower-division',
                'concentration_area': 'Digital Media',
                'mapped_plos': ['PLO2'],
                'course_type': 'concentration',
                'semester_planned': 'Fall 2023',
                'completion_status': 'completed',
                'grade': 'B+'
            },
            {
                'iap_id': iap_id,
                'course_code': 'MDIA 3400',
                'course_title': 'Digital Video Production',
                'course_credits': 3,
                'course_level': 'upper-division',
                'concentration_area': 'Digital Media',
                'mapped_plos': ['PLO2', 'PLO3'],
                'course_type': 'concentration',
                'semester_planned': 'Fall 2024',
                'completion_status': 'planned'
            },
            # INDS Core Courses
            {
                'iap_id': iap_id,
                'course_code': 'INDS 3800',
                'course_title': 'Interdisciplinary Seminar',
                'course_credits': 3,
                'course_level': 'upper-division',
                'concentration_area': 'Core',
                'mapped_plos': ['PLO3'],
                'course_type': 'inds_core',
                'semester_planned': 'Fall 2024',
                'completion_status': 'planned'
            }
        ]
        
        try:
            result = self.supabase.table('iap_course_mappings').insert(course_mappings).execute()
            print(f"   ✅ Created {len(course_mappings)} course mappings")
        except Exception as e:
            print(f"   ❌ Failed to create course mappings: {e}")
    
    async def _create_general_education_data(self, iap_id):
        """Create general education tracking data"""
        if not iap_id:
            return
            
        print("\n3️⃣ Creating General Education Data...")
        
        ge_data = [
            {
                'iap_id': iap_id,
                'ge_category': 'Written Communication',
                'ge_requirement': 'College Writing (ENGL 1010)',
                'required_credits': 3,
                'completed_credits': 3,
                'courses_applied': ['ENGL 1010'],
                'completion_status': 'completed',
                'notes': 'Completed with grade A-'
            },
            {
                'iap_id': iap_id,
                'ge_category': 'Quantitative Literacy',
                'ge_requirement': 'College Algebra or higher',
                'required_credits': 3,
                'completed_credits': 4,
                'courses_applied': ['MATH 1050'],
                'completion_status': 'completed',
                'notes': 'Exceeded requirement with Statistics'
            },
            {
                'iap_id': iap_id,
                'ge_category': 'Fine Arts',
                'ge_requirement': 'Fine Arts Distribution',
                'required_credits': 3,
                'completed_credits': 0,
                'courses_applied': [],
                'completion_status': 'not_started',
                'notes': 'Planning to take ART 1010 or MUS 1010'
            }
        ]
        
        try:
            result = self.supabase.table('iap_general_education').insert(ge_data).execute()
            print(f"   ✅ Created {len(ge_data)} GE tracking records")
        except Exception as e:
            print(f"   ❌ Failed to create GE data: {e}")
    
    async def _create_market_research_data(self, iap_id):
        """Create market research data"""
        if not iap_id:
            return
            
        print("\n4️⃣ Creating Market Research Data...")
        
        market_data = {
            'iap_id': iap_id,
            'degree_emphasis': 'Psychology and Digital Media',
            'job_market_data': {
                'employment_growth': '8% (faster than average)',
                'job_openings_annually': 2400,
                'key_employers': ['Healthcare systems', 'Digital agencies', 'Nonprofits', 'Educational institutions']
            },
            'salary_data': {
                'entry_level': 42000,
                'mid_career': 65000,
                'senior_level': 85000,
                'median': 58000,
                'utah_adjustment': 0.95
            },
            'industry_trends': {
                'digital_health_growth': 'Expanding rapidly post-COVID',
                'mental_health_awareness': 'Increased focus on workplace wellness',
                'content_creator_economy': 'Growing demand for specialized content'
            },
            'skill_demand': {
                'high_demand': ['Video editing', 'Social media strategy', 'Data analysis', 'Counseling techniques'],
                'emerging': ['VR/AR therapy', 'AI-assisted content', 'Telehealth platforms']
            },
            'geographic_data': {
                'utah_opportunities': 'Strong healthcare and tech sectors',
                'remote_work_potential': 'High - 70% of roles offer remote options',
                'relocation_markets': ['California', 'Colorado', 'Texas']
            },
            'sources': [
                'Bureau of Labor Statistics',
                'Utah Department of Workforce Services',
                'Indeed Salary Data',
                'LinkedIn Economic Graph'
            ],
            'research_date': date.today().isoformat(),
            'viability_score': 88.5,
            'viability_summary': 'Strong career prospects with growing demand for digital mental health content creators. Salary potential is competitive with good growth opportunities.'
        }
        
        try:
            result = self.supabase.table('iap_market_research').insert(market_data).execute()
            print(f"   ✅ Created market research data (Viability Score: {market_data['viability_score']})")
        except Exception as e:
            print(f"   ❌ Failed to create market research data: {e}")
    
    async def _create_concentration_validation_data(self, iap_id):
        """Create concentration validation data"""
        if not iap_id:
            return
            
        print("\n5️⃣ Creating Concentration Validation Data...")
        
        concentration_data = [
            {
                'iap_id': iap_id,
                'concentration_name': 'Psychology',
                'required_credits': 14,
                'completed_credits': 10,
                'upper_division_credits': 7,
                'lower_division_credits': 3,
                'courses': [
                    {'code': 'PSYC 1010', 'credits': 3, 'level': 'lower-division', 'status': 'completed'},
                    {'code': 'PSYC 3030', 'credits': 4, 'level': 'upper-division', 'status': 'completed'},
                    {'code': 'PSYC 3500', 'credits': 3, 'level': 'upper-division', 'status': 'planned'}
                ],
                'validation_status': 'valid',
                'validation_notes': 'On track to meet requirements'
            },
            {
                'iap_id': iap_id,
                'concentration_name': 'Digital Media',
                'required_credits': 14,
                'completed_credits': 6,
                'upper_division_credits': 3,
                'lower_division_credits': 3,
                'courses': [
                    {'code': 'MDIA 1010', 'credits': 3, 'level': 'lower-division', 'status': 'completed'},
                    {'code': 'MDIA 3400', 'credits': 3, 'level': 'upper-division', 'status': 'planned'},
                    {'code': 'MDIA 4500', 'credits': 3, 'level': 'upper-division', 'status': 'planned'}
                ],
                'validation_status': 'incomplete',
                'validation_notes': 'Need additional upper-division credits'
            }
        ]
        
        try:
            result = self.supabase.table('iap_concentration_validation').insert(concentration_data).execute()
            print(f"   ✅ Created {len(concentration_data)} concentration validation records")
        except Exception as e:
            print(f"   ❌ Failed to create concentration validation data: {e}")
    
    async def _create_course_plo_mappings(self, iap_id):
        """Create detailed course-to-PLO mappings"""
        if not iap_id:
            return
            
        print("\n6️⃣ Creating Course-PLO Mappings...")
        
        plo_mappings = [
            {
                'iap_id': iap_id,
                'course_code': 'PSYC 3030',
                'course_title': 'Research Methods in Psychology',
                'plo_id': 'PLO1',
                'plo_description': 'Apply psychological theories and research methods',
                'mapping_strength': 'strong',
                'evidence_description': 'Students design and conduct original research studies using statistical analysis',
                'assessment_methods': ['Research proposal', 'Data analysis project', 'Final research paper']
            },
            {
                'iap_id': iap_id,
                'course_code': 'MDIA 3400',
                'course_title': 'Digital Video Production',
                'plo_id': 'PLO2',
                'plo_description': 'Design and produce digital media content',
                'mapping_strength': 'strong',
                'evidence_description': 'Students create professional video content using industry-standard software',
                'assessment_methods': ['Video portfolio', 'Technical skills assessment', 'Creative project']
            },
            {
                'iap_id': iap_id,
                'course_code': 'INDS 3800',
                'course_title': 'Interdisciplinary Seminar',
                'plo_id': 'PLO3',
                'plo_description': 'Integrate knowledge across disciplines',
                'mapping_strength': 'strong',
                'evidence_description': 'Students synthesize concepts from multiple fields to address complex problems',
                'assessment_methods': ['Interdisciplinary project', 'Reflection essays', 'Peer collaboration']
            }
        ]
        
        try:
            result = self.supabase.table('iap_course_plo_mappings').insert(plo_mappings).execute()
            print(f"   ✅ Created {len(plo_mappings)} course-PLO mappings")
        except Exception as e:
            print(f"   ❌ Failed to create course-PLO mappings: {e}")
    
    async def _create_additional_test_students(self):
        """Create additional test students for comprehensive testing"""
        print("\n7️⃣ Creating Additional Test Students...")
        
        additional_students = [
            {
                'student_name': 'Marcus Chen',
                'student_id': 'MC2024002',
                'student_email': 'marcus.chen@utahtech.edu',
                'degree_emphasis': 'Business and Computer Science',
                'mission_statement': 'Developing innovative business solutions through technology integration.',
                'program_goals': [
                    'Master business analysis and strategy development',
                    'Develop advanced programming and system design skills',
                    'Create technology-driven business solutions'
                ],
                'concentration_areas': ['Business Administration', 'Computer Science', 'Information Systems'],
                'semester_year_inds3800': 'Spring 2025'
            },
            {
                'student_name': 'Elena Rodriguez',
                'student_id': 'ER2024003',
                'student_email': 'elena.rodriguez@utahtech.edu',
                'degree_emphasis': 'Environmental Science and Communication',
                'mission_statement': 'Communicating environmental science to promote sustainable practices.',
                'program_goals': [
                    'Understand environmental systems and sustainability',
                    'Develop effective science communication skills',
                    'Create impactful environmental advocacy campaigns'
                ],
                'concentration_areas': ['Environmental Science', 'Communication', 'Public Relations'],
                'semester_year_inds3800': 'Fall 2024'
            }
        ]
        
        try:
            result = self.supabase.table('iap_templates').insert(additional_students).execute()
            print(f"   ✅ Created {len(additional_students)} additional test students")
        except Exception as e:
            print(f"   ❌ Failed to create additional students: {e}")

async def main():
    """Main execution function"""
    creator = RealisticTestDataCreator()
    await creator.create_comprehensive_test_data()
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
