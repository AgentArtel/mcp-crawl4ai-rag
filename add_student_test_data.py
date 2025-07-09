#!/usr/bin/env python3
"""
Student Test Data Population Script for Utah Tech MCP Server

This script adds realistic student test data and IAP templates to enable
comprehensive testing of all IAP-related MCP tools without affecting
existing academic data.
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

class StudentTestDataPopulator:
    """Adds student test data for IAP tool testing"""
    
    def __init__(self):
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'), 
            os.getenv('SUPABASE_SERVICE_KEY')
        )
        
    async def add_student_test_data(self):
        """Add comprehensive student test data"""
        print("🎓 Adding Student Test Data for IAP Tool Testing...")
        
        # Add test data in logical order
        await self._add_iap_templates()
        await self._add_general_education_data()
        await self._add_market_research_data()
        await self._add_concentration_validation_data()
        await self._add_course_plo_mappings()
        
        print("\n✅ Student Test Data Addition Complete!")
        await self._show_summary()
    
    async def _add_iap_templates(self):
        """Add diverse IAP template test cases"""
        print("\n1️⃣ Adding IAP Templates...")
        
        templates = [
            {
                'student_name': 'Sarah Johnson',
                'student_id': 'SJ2024001',
                'student_email': 'sarah.johnson@utahtech.edu',
                'student_phone': '(435) 555-0101',
                'degree_emphasis': 'Psychology and Digital Media',
                'mission_statement': 'The BIS with an emphasis in Psychology and Digital Media at UT prepares students to create evidence-based digital content for mental health awareness by having students complete research projects, media production assignments, and interdisciplinary case studies that integrate psychological principles with digital storytelling techniques.',
                'program_goals': [
                    'Students will demonstrate mastery of psychological research methods and statistical analysis',
                    'Students will create professional-quality digital media content across multiple platforms',
                    'Students will apply psychological principles to digital media design and user experience',
                    'Students will evaluate the effectiveness of digital mental health interventions',
                    'Students will integrate interdisciplinary knowledge to address complex social issues',
                    'Students will communicate psychological concepts to diverse audiences through digital media'
                ],
                'program_learning_outcomes': [
                    {
                        'outcome': 'Students will design and conduct psychological research using appropriate methodologies and statistical analysis',
                        'lower_division_courses': ['PSYC 1010 General Psychology', 'MATH 1040 Introduction to Statistics'],
                        'upper_division_courses': ['PSYC 3030 Research Methods in Psychology', 'PSYC 4400 Advanced Social Psychology']
                    },
                    {
                        'outcome': 'Students will create professional-quality digital content using industry-standard tools and techniques',
                        'lower_division_courses': ['MDIA 1010 Introduction to Digital Media', 'MDIA 2500 Digital Design Fundamentals'],
                        'upper_division_courses': ['MDIA 3400 Advanced Digital Production', 'MDIA 4200 Interactive Media Design']
                    },
                    {
                        'outcome': 'Students will apply psychological principles to enhance user experience and engagement in digital media',
                        'lower_division_courses': ['PSYC 2010 Developmental Psychology', 'COMM 1010 Public Speaking'],
                        'upper_division_courses': ['PSYC 4500 Cognitive Psychology', 'COMM 3200 Interpersonal Communication']
                    },
                    {
                        'outcome': 'Students will evaluate the effectiveness and ethical implications of digital mental health interventions',
                        'lower_division_courses': ['PHIL 2050 Ethics', 'HLTH 1010 Personal Health'],
                        'upper_division_courses': ['PSYC 4600 Health Psychology', 'PHIL 3400 Bioethics']
                    },
                    {
                        'outcome': 'Students will synthesize knowledge from multiple disciplines to solve complex problems',
                        'lower_division_courses': ['ENGL 1010 College Writing', 'SOC 1010 Introduction to Sociology'],
                        'upper_division_courses': ['INTS 3100 Interdisciplinary Studies', 'ENGL 3030 Advanced College Writing']
                    },
                    {
                        'outcome': 'Students will communicate effectively with diverse audiences through written, oral, and digital formats',
                        'lower_division_courses': ['COMM 1010 Public Speaking', 'ENGL 1010 College Writing'],
                        'upper_division_courses': ['COMM 4100 Advanced Public Communication', 'ENGL 3130 Grant & Proposal Writing']
                    }
                ],
                'concentration_areas': ['Psychology', 'Digital Media', 'Communication'],
                'course_mappings': {
                    'Psychology': {
                        'lower_division': ['PSYC 1010 General Psychology', 'PSYC 2010 Developmental Psychology'],
                        'upper_division': ['PSYC 3030 Research Methods in Psychology', 'PSYC 4400 Advanced Social Psychology', 'PSYC 4500 Cognitive Psychology', 'PSYC 4600 Health Psychology']
                    },
                    'Digital Media': {
                        'lower_division': ['MDIA 1010 Introduction to Digital Media', 'MDIA 2500 Digital Design Fundamentals'],
                        'upper_division': ['MDIA 3400 Advanced Digital Production', 'MDIA 4200 Interactive Media Design']
                    },
                    'Communication': {
                        'lower_division': ['COMM 1010 Public Speaking'],
                        'upper_division': ['COMM 3200 Interpersonal Communication', 'COMM 4100 Advanced Public Communication']
                    }
                },
                'cover_letter': 'Dear Individualized Studies Committee Members,\n\nI am pursuing the Bachelor of Individualized Studies with an emphasis in Psychology and Digital Media because I am passionate about addressing the growing mental health crisis through innovative digital solutions. My academic journey has led me to recognize that traditional approaches to mental health education and intervention can be enhanced through evidence-based digital media strategies.\n\nThis interdisciplinary approach directly supports my mission statement: "The BIS with an emphasis in Psychology and Digital Media at UT prepares students to create evidence-based digital content for mental health awareness." My post-graduation goal is to work with healthcare organizations and mental health nonprofits to develop engaging, scientifically-grounded digital content that reduces stigma and increases access to mental health resources.\n\nMy coursework strategically combines psychological research methods with digital media production skills. Core courses like PSYC 3030 Research Methods in Psychology provide the scientific foundation for evidence-based practice, while MDIA 3400 Advanced Digital Production develops the technical skills needed to create professional-quality content. PSYC 4600 Health Psychology bridges these disciplines by exploring how psychological principles apply to health communication and behavior change.\n\nMarket research demonstrates strong viability for this degree emphasis. The digital health market is projected to reach $659.8 billion by 2025, with mental health apps alone growing at 23.6% annually. Utah\'s thriving health technology sector, including companies like Domo and Health Catalyst, creates abundant opportunities for professionals who can bridge psychology and digital media.\n\nThis proposed degree meets my goals in ways that existing programs cannot. Traditional psychology programs lack the technical digital media skills essential for modern health communication, while digital media programs often lack the scientific rigor and ethical framework necessary for mental health applications. My individualized program uniquely prepares me to be a leader in the emerging field of digital mental health.\n\nYours sincerely,\nSarah Johnson\nBachelor of Individualized Studies with an emphasis in Psychology and Digital Media',
                'semester_year_inds3800': 'Fall 2024',
                'ge_requirements_complete': False,
                'remaining_ge': [
                    {'category': 'Social Sciences', 'requirement': 'Social Science Elective', 'credits': 3},
                    {'category': 'Fine Arts', 'requirement': 'Fine Arts Elective', 'credits': 3}
                ],
                'written_comprehension_course': 'INTS 3100 Interdisciplinary Studies',
                'total_credits': 124,
                'upper_division_credits': 45,
                'concentration_credits': 44,
                'upper_division_concentration_credits': 24,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            },
            {
                'student_name': 'Marcus Rodriguez',
                'student_id': 'MR2024002',
                'student_email': 'marcus.rodriguez@utahtech.edu',
                'student_phone': '(435) 555-0102',
                'degree_emphasis': 'Business Analytics and Environmental Science',
                'mission_statement': 'To leverage data analytics and business acumen to drive sustainable environmental solutions and corporate responsibility initiatives.',
                'program_goals': [
                    'Develop expertise in business analytics and data visualization',
                    'Understand environmental science principles and sustainability practices',
                    'Apply quantitative methods to environmental business problems',
                    'Lead sustainable business transformation initiatives'
                ],
                'program_learning_outcomes': [
                    {
                        'outcome': 'Data Analysis Mastery',
                        'description': 'Apply advanced statistical and analytical methods to business problems'
                    },
                    {
                        'outcome': 'Environmental Literacy',
                        'description': 'Understand ecological principles and environmental impact assessment'
                    },
                    {
                        'outcome': 'Strategic Thinking',
                        'description': 'Develop and implement sustainable business strategies'
                    }
                ],
                'concentration_areas': ['Business', 'Environmental Science', 'Mathematics'],
                'course_mappings': {
                    'Business': ['BUSN 1010', 'BUSN 3100', 'BUSN 4200', 'BUSN 4500'],
                    'Environmental Science': ['ENVS 1010', 'ENVS 3200', 'ENVS 4100', 'ENVS 4300'],
                    'Mathematics': ['MATH 1040', 'MATH 2040', 'MATH 3400', 'MATH 4200']
                },
                'cover_letter': 'The intersection of business analytics and environmental science represents the future of sustainable enterprise. My degree prepares me to lead data-driven environmental initiatives in the corporate sector.',
                'semester_year_inds3800': 'Spring 2025',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            },
            {
                'student_name': 'Emily Chen',
                'student_id': 'EC2024003',
                'student_email': 'emily.chen@utahtech.edu',
                'student_phone': '(435) 555-0103',
                'degree_emphasis': 'Health Sciences and Technology Innovation',
                'mission_statement': 'To bridge healthcare and technology by developing innovative solutions that improve patient outcomes and healthcare accessibility.',
                'program_goals': [
                    'Master health sciences fundamentals and healthcare systems',
                    'Develop technical skills in health informatics and medical technology',
                    'Design user-centered healthcare technology solutions',
                    'Understand healthcare policy and ethical considerations'
                ],
                'program_learning_outcomes': [
                    {
                        'outcome': 'Healthcare Knowledge',
                        'description': 'Demonstrate comprehensive understanding of health sciences and healthcare delivery'
                    },
                    {
                        'outcome': 'Technology Integration',
                        'description': 'Design and implement technology solutions for healthcare challenges'
                    },
                    {
                        'outcome': 'Ethical Reasoning',
                        'description': 'Apply ethical frameworks to healthcare technology decisions'
                    }
                ],
                'concentration_areas': ['Health Sciences', 'Computer Science', 'Ethics'],
                'course_mappings': {
                    'Health Sciences': ['HLTH 1010', 'HLTH 2500', 'HLTH 3400', 'HLTH 4200'],
                    'Computer Science': ['CS 1400', 'CS 2420', 'CS 3500', 'CS 4600'],
                    'Ethics': ['PHIL 2050', 'PHIL 3400', 'PHIL 4100']
                },
                'cover_letter': 'Healthcare technology is transforming patient care. My interdisciplinary background in health sciences and technology positions me to lead innovation in digital health solutions.',
                'semester_year_inds3800': 'Fall 2024',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            },
            {
                'student_name': 'David Thompson',
                'student_id': 'DT2024004',
                'student_email': 'david.thompson@utahtech.edu',
                'degree_emphasis': 'Education and Community Development',
                'mission_statement': 'To create educational programs and community initiatives that promote lifelong learning and social equity in underserved populations.',
                'program_goals': [
                    'Understand educational theory and pedagogical best practices',
                    'Develop community engagement and program development skills',
                    'Address educational inequities through innovative approaches',
                    'Build partnerships between educational institutions and communities'
                ],
                'program_learning_outcomes': [
                    {
                        'outcome': 'Educational Leadership',
                        'description': 'Design and implement effective educational programs and curricula'
                    },
                    {
                        'outcome': 'Community Engagement',
                        'description': 'Facilitate meaningful partnerships between institutions and communities'
                    },
                    {
                        'outcome': 'Social Justice Advocacy',
                        'description': 'Address systemic barriers to educational access and success'
                    }
                ],
                'concentration_areas': ['Education', 'Sociology', 'Public Administration'],
                'course_mappings': {
                    'Education': ['EDUC 2010', 'EDUC 3100', 'EDUC 4200', 'EDUC 4500'],
                    'Sociology': ['SOC 1010', 'SOC 3200', 'SOC 4100'],
                    'Public Administration': ['POLS 2100', 'POLS 3400', 'POLS 4300']
                },
                'semester_year_inds3800': 'Spring 2025',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        ]
        
        result = self.supabase.table('iap_templates').upsert(templates).execute()
        print(f"   ✅ Added {len(templates)} IAP templates")
    
    async def _add_general_education_data(self):
        """Add general education tracking data for test students"""
        print("\n2️⃣ Adding General Education Data...")
        
        ge_data = []
        
        # Sarah Johnson's GE progress (mostly complete)
        sarah_ge = [
            {
                'student_id': 'SJ2024001',
                'category': 'English',
                'requirement': 'College Writing',
                'credits_required': 3,
                'credits_completed': 3,
                'courses_completed': ['ENGL 1010'],
                'status': 'completed'
            },
            {
                'student_id': 'SJ2024001',
                'category': 'Mathematics',
                'requirement': 'Quantitative Reasoning',
                'credits_required': 4,
                'credits_completed': 4,
                'courses_completed': ['MATH 1040'],
                'status': 'completed'
            },
            {
                'student_id': 'SJ2024001',
                'category': 'Natural Sciences',
                'requirement': 'Laboratory Science',
                'credits_required': 4,
                'credits_completed': 4,
                'courses_completed': ['BIOL 1010'],
                'status': 'completed'
            },
            {
                'student_id': 'SJ2024001',
                'category': 'Social Sciences',
                'requirement': 'Social Science Elective',
                'credits_required': 3,
                'credits_completed': 0,
                'courses_completed': [],
                'status': 'in_progress'
            }
        ]
        
        # Marcus Rodriguez's GE progress (partial)
        marcus_ge = [
            {
                'student_id': 'MR2024002',
                'category': 'English',
                'requirement': 'College Writing',
                'credits_required': 3,
                'credits_completed': 3,
                'courses_completed': ['ENGL 1010'],
                'status': 'completed'
            },
            {
                'student_id': 'MR2024002',
                'category': 'Mathematics',
                'requirement': 'Quantitative Reasoning',
                'credits_required': 4,
                'credits_completed': 4,
                'courses_completed': ['MATH 1040'],
                'status': 'completed'
            },
            {
                'student_id': 'MR2024002',
                'category': 'Natural Sciences',
                'requirement': 'Laboratory Science',
                'credits_required': 4,
                'credits_completed': 0,
                'courses_completed': [],
                'status': 'not_started'
            }
        ]
        
        # Add timestamps to all records
        for record in sarah_ge + marcus_ge:
            record['created_at'] = datetime.now().isoformat()
            record['updated_at'] = datetime.now().isoformat()
        
        ge_data.extend(sarah_ge + marcus_ge)
        
        result = self.supabase.table('iap_general_education').upsert(ge_data).execute()
        print(f"   ✅ Added {len(ge_data)} GE tracking records")
    
    async def _add_market_research_data(self):
        """Add market research data for different degree emphases"""
        print("\n3️⃣ Adding Market Research Data...")
        
        market_data = [
            {
                'degree_emphasis': 'Psychology and Digital Media',
                'geographic_focus': 'Utah',
                'job_market_score': 88,
                'salary_range_min': 45000,
                'salary_range_max': 85000,
                'growth_projection': 'Much Faster Than Average',
                'key_skills': ['Content Creation', 'Data Analysis', 'User Experience', 'Mental Health Awareness'],
                'top_employers': ['Digital Health Companies', 'Media Agencies', 'Healthcare Systems', 'Educational Technology'],
                'viability_score': 92,
                'recommendations': [
                    'Strong growth in digital mental health sector',
                    'Consider certification in UX design or data visualization',
                    'Build portfolio showcasing psychology-informed media projects'
                ],
                'created_at': datetime.now().isoformat()
            },
            {
                'degree_emphasis': 'Business Analytics and Environmental Science',
                'geographic_focus': 'Utah',
                'job_market_score': 91,
                'salary_range_min': 55000,
                'salary_range_max': 95000,
                'growth_projection': 'Much Faster Than Average',
                'key_skills': ['Data Analytics', 'Sustainability Consulting', 'Environmental Impact Assessment', 'Business Strategy'],
                'top_employers': ['Environmental Consulting Firms', 'Renewable Energy Companies', 'Government Agencies', 'Corporate Sustainability Departments'],
                'viability_score': 95,
                'recommendations': [
                    'Excellent job prospects in Utah\'s growing clean energy sector',
                    'Consider GIS certification for environmental analysis',
                    'Network with Utah Clean Energy and environmental organizations'
                ],
                'created_at': datetime.now().isoformat()
            },
            {
                'degree_emphasis': 'Health Sciences and Technology Innovation',
                'geographic_focus': 'Utah',
                'job_market_score': 94,
                'salary_range_min': 60000,
                'salary_range_max': 110000,
                'growth_projection': 'Much Faster Than Average',
                'key_skills': ['Health Informatics', 'Medical Device Development', 'Healthcare Analytics', 'Regulatory Compliance'],
                'top_employers': ['Health Technology Companies', 'Hospitals and Health Systems', 'Medical Device Manufacturers', 'Telehealth Platforms'],
                'viability_score': 96,
                'recommendations': [
                    'Utah is a major hub for health technology innovation',
                    'Consider internships with local health tech companies',
                    'Pursue healthcare informatics certification'
                ],
                'created_at': datetime.now().isoformat()
            }
        ]
        
        result = self.supabase.table('iap_market_research').upsert(market_data).execute()
        print(f"   ✅ Added {len(market_data)} market research records")
    
    async def _add_concentration_validation_data(self):
        """Add concentration area validation data"""
        print("\n4️⃣ Adding Concentration Validation Data...")
        
        validation_data = [
            {
                'student_id': 'SJ2024001',
                'concentration_name': 'Psychology',
                'total_credits': 16,
                'upper_division_credits': 9,
                'lower_division_credits': 7,
                'courses': ['PSYC 1010', 'PSYC 2010', 'PSYC 3030', 'PSYC 4400', 'PSYC 4500'],
                'meets_requirements': True,
                'validation_notes': 'Exceeds minimum requirements with strong upper-division focus',
                'created_at': datetime.now().isoformat()
            },
            {
                'student_id': 'SJ2024001',
                'concentration_name': 'Digital Media',
                'total_credits': 14,
                'upper_division_credits': 7,
                'lower_division_credits': 7,
                'courses': ['MDIA 1010', 'MDIA 2500', 'MDIA 3400', 'MDIA 4200'],
                'meets_requirements': True,
                'validation_notes': 'Meets minimum requirements exactly',
                'created_at': datetime.now().isoformat()
            },
            {
                'student_id': 'MR2024002',
                'concentration_name': 'Business',
                'total_credits': 15,
                'upper_division_credits': 9,
                'lower_division_credits': 6,
                'courses': ['BUSN 1010', 'BUSN 3100', 'BUSN 4200', 'BUSN 4500'],
                'meets_requirements': True,
                'validation_notes': 'Strong upper-division emphasis in business strategy',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        result = self.supabase.table('iap_concentration_validation').upsert(validation_data).execute()
        print(f"   ✅ Added {len(validation_data)} concentration validation records")
    
    async def _add_course_plo_mappings(self):
        """Add course to Program Learning Outcome mappings"""
        print("\n5️⃣ Adding Course-PLO Mappings...")
        
        mappings = [
            {
                'student_id': 'SJ2024001',
                'course_code': 'PSYC 3030',
                'plo_name': 'Research Competency',
                'mapping_strength': 'Primary',
                'justification': 'Core research methods course directly develops research design and analysis skills',
                'created_at': datetime.now().isoformat()
            },
            {
                'student_id': 'SJ2024001',
                'course_code': 'MDIA 3400',
                'plo_name': 'Digital Media Proficiency',
                'mapping_strength': 'Primary',
                'justification': 'Advanced digital media production course builds professional-level skills',
                'created_at': datetime.now().isoformat()
            },
            {
                'student_id': 'SJ2024001',
                'course_code': 'COMM 3200',
                'plo_name': 'Interdisciplinary Integration',
                'mapping_strength': 'Supporting',
                'justification': 'Interpersonal communication principles support psychology-media integration',
                'created_at': datetime.now().isoformat()
            },
            {
                'student_id': 'MR2024002',
                'course_code': 'MATH 3400',
                'plo_name': 'Data Analysis Mastery',
                'mapping_strength': 'Primary',
                'justification': 'Advanced statistics course provides quantitative analysis foundation',
                'created_at': datetime.now().isoformat()
            },
            {
                'student_id': 'MR2024002',
                'course_code': 'ENVS 4100',
                'plo_name': 'Environmental Literacy',
                'mapping_strength': 'Primary',
                'justification': 'Environmental impact assessment course develops core environmental science skills',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        result = self.supabase.table('iap_course_plo_mappings').upsert(mappings).execute()
        print(f"   ✅ Added {len(mappings)} course-PLO mappings")
    
    async def _show_summary(self):
        """Show summary of added student test data"""
        print("\n📊 Student Test Data Summary:")
        
        tables = [
            'iap_templates', 'iap_general_education', 'iap_market_research',
            'iap_concentration_validation', 'iap_course_plo_mappings'
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
    populator = StudentTestDataPopulator()
    await populator.add_student_test_data()
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
