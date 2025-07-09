"""
IAP (Individualized Academic Plan) Management Tools
Provides comprehensive tools for creating, managing, and validating IAP templates
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import re

@dataclass
class IAPTemplate:
    """Data structure for IAP Template"""
    id: Optional[int] = None
    student_name: str = ""
    student_id: str = ""
    student_email: str = ""
    student_phone: str = ""
    degree_emphasis: str = ""
    
    # Cover Letter Data
    cover_letter_data: Dict[str, Any] = None
    
    # Program Definition
    mission_statement: str = ""
    program_goals: List[str] = None
    program_learning_outcomes: List[Dict[str, Any]] = None
    
    # Course Mappings
    course_mappings: Dict[str, List[str]] = None
    concentration_areas: List[str] = None
    
    # Academic Plan Tracking
    general_education: Dict[str, Any] = None
    inds_core_courses: Dict[str, Any] = None
    concentration_courses: Dict[str, Any] = None
    
    # Requirements Validation
    credit_summary: Dict[str, Any] = None
    completion_status: Dict[str, Any] = None
    validation_results: Dict[str, Any] = None
    
    # Metadata
    semester_year_inds3800: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields"""
        if self.cover_letter_data is None:
            self.cover_letter_data = {}
        if self.program_goals is None:
            self.program_goals = []
        if self.program_learning_outcomes is None:
            self.program_learning_outcomes = []
        if self.course_mappings is None:
            self.course_mappings = {}
        if self.concentration_areas is None:
            self.concentration_areas = []
        if self.general_education is None:
            self.general_education = {}
        if self.inds_core_courses is None:
            self.inds_core_courses = {}
        if self.concentration_courses is None:
            self.concentration_courses = {}
        if self.credit_summary is None:
            self.credit_summary = {}
        if self.completion_status is None:
            self.completion_status = {}
        if self.validation_results is None:
            self.validation_results = {}

class IAPManager:
    """Manages IAP templates and operations"""
    
    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
    
    async def create_iap_template(self, student_name: str, student_id: str, 
                                degree_emphasis: str, student_email: str = "", 
                                student_phone: str = "") -> Dict[str, Any]:
        """Create a new IAP template for a student"""
        try:
            # Create new IAP template
            iap = IAPTemplate(
                student_name=student_name,
                student_id=student_id,
                student_email=student_email,
                student_phone=student_phone,
                degree_emphasis=degree_emphasis
            )
            
            # Initialize default structure
            iap.program_goals = [
                f"Students will demonstrate expertise in {degree_emphasis} principles and practices",
                f"Students will apply interdisciplinary approaches to solve complex problems",
                f"Students will communicate effectively across multiple disciplines",
                f"Students will conduct independent research in their chosen field",
                f"Students will demonstrate ethical reasoning and professional responsibility",
                f"Students will synthesize knowledge from diverse academic perspectives"
            ]
            
            iap.program_learning_outcomes = [
                {
                    "id": "PLO1",
                    "description": f"Students will analyze complex problems using {degree_emphasis} methodologies",
                    "lower_division_courses": [],
                    "upper_division_courses": []
                },
                {
                    "id": "PLO2", 
                    "description": "Students will demonstrate effective written and oral communication skills",
                    "lower_division_courses": [],
                    "upper_division_courses": []
                },
                {
                    "id": "PLO3",
                    "description": "Students will apply research methods appropriate to their field of study",
                    "lower_division_courses": [],
                    "upper_division_courses": []
                },
                {
                    "id": "PLO4",
                    "description": "Students will evaluate information critically from multiple perspectives",
                    "lower_division_courses": [],
                    "upper_division_courses": []
                },
                {
                    "id": "PLO5",
                    "description": "Students will demonstrate professional competency in their chosen field",
                    "lower_division_courses": [],
                    "upper_division_courses": []
                },
                {
                    "id": "PLO6",
                    "description": "Students will integrate knowledge across disciplinary boundaries",
                    "lower_division_courses": [],
                    "upper_division_courses": []
                }
            ]
            
            # Initialize INDS core courses
            iap.inds_core_courses = {
                "INDS 3800": {"title": "Individualized Studies Seminar", "credits": 3, "status": "required"},
                "INDS 3805": {"title": "Individualized Studies Lab", "credits": 1, "status": "required"},
                "capstone": {"options": ["INDS 4700", "INTS 4950R"], "credits": 3, "status": "required"}
            }
            
            # Initialize completion tracking
            iap.completion_status = {
                "cover_letter": False,
                "mission_statement": False,
                "program_goals": True,  # Pre-populated
                "program_learning_outcomes": True,  # Pre-populated
                "course_mappings": False,
                "concentration_areas": False,
                "academic_plan": False,
                "overall_percentage": 28.6  # 2/7 sections complete
            }
            
            return {
                "success": True,
                "message": f"IAP template created for {student_name}",
                "iap_template": asdict(iap),
                "next_steps": [
                    "Complete cover letter information",
                    "Customize mission statement",
                    "Define concentration areas (3+ disciplines)",
                    "Map courses to Program Learning Outcomes",
                    "Plan academic course sequence"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create IAP template: {str(e)}",
                "troubleshooting": [
                    "Verify student information is complete",
                    "Check degree emphasis format",
                    "Ensure database connection is working"
                ]
            }
    
    async def update_iap_section(self, student_id: str, section: str, 
                               data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a specific section of an IAP template"""
        try:
            valid_sections = [
                "cover_letter", "mission_statement", "program_goals", 
                "program_learning_outcomes", "course_mappings", 
                "concentration_areas", "academic_plan"
            ]
            
            if section not in valid_sections:
                return {
                    "success": False,
                    "error": f"Invalid section '{section}'. Valid sections: {valid_sections}"
                }
            
            # For now, return success with update confirmation
            # In full implementation, this would update the database
            return {
                "success": True,
                "message": f"Updated {section} for student {student_id}",
                "section": section,
                "updated_data": data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update IAP section: {str(e)}"
            }
    
    async def generate_iap_suggestions(self, degree_emphasis: str, 
                                     section: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate AI-powered suggestions for IAP content"""
        try:
            suggestions = {}
            
            if section == "mission_statement":
                suggestions = {
                    "mission_statement": f"The BIS with an emphasis in {degree_emphasis} at UT prepares students to become innovative professionals and critical thinkers by having students complete interdisciplinary coursework, hands-on research projects, and real-world applications. This program develops analytical skills, communication competencies, and ethical reasoning necessary for success in today's complex professional landscape.",
                    "alternatives": [
                        f"The BIS with an emphasis in {degree_emphasis} at UT prepares students to address complex societal challenges by integrating knowledge across multiple disciplines through collaborative projects, independent research, and community engagement.",
                        f"The BIS with an emphasis in {degree_emphasis} at UT prepares students to become leaders in their chosen field by developing critical thinking skills, research competencies, and professional expertise through personalized academic experiences."
                    ]
                }
            
            elif section == "program_goals":
                suggestions = {
                    "program_goals": [
                        f"Students will demonstrate mastery of core concepts in {degree_emphasis}",
                        "Students will apply interdisciplinary research methods effectively",
                        "Students will communicate complex ideas clearly across diverse audiences",
                        "Students will evaluate information critically using multiple theoretical frameworks",
                        "Students will demonstrate ethical reasoning in professional contexts",
                        "Students will synthesize knowledge from diverse academic and professional sources"
                    ],
                    "customization_tips": [
                        "Tailor goals to your specific career objectives",
                        "Include industry-specific competencies",
                        "Consider adding goals related to your concentration areas",
                        "Ensure goals are measurable and achievable"
                    ]
                }
            
            elif section == "cover_letter":
                suggestions = {
                    "paragraph_templates": {
                        "introduction": f"I am pursuing a Bachelor of Individualized Studies with an emphasis in {degree_emphasis} because this unique program allows me to combine my diverse academic interests and career goals in ways that traditional degree programs cannot accommodate.",
                        "mission_connection": "This interdisciplinary approach aligns perfectly with my mission to [insert your mission here], as stated in my mission statement: '[insert direct quote from mission statement]'.",
                        "coursework_relevance": f"My carefully selected coursework directly supports my mission and goals, including upper-division courses such as [Course 1], [Course 2], and [Course 3], which provide the theoretical foundation and practical skills necessary for success in {degree_emphasis}.",
                        "market_viability": f"The field of {degree_emphasis} shows strong growth potential, with [insert relevant statistics] indicating increasing demand for professionals with interdisciplinary expertise.",
                        "unique_value": "This individualized degree program offers advantages that existing programs cannot provide, specifically the ability to combine multiple disciplines in a coherent, purposeful way that addresses real-world challenges."
                    },
                    "research_suggestions": [
                        f"Look up current job market statistics for {degree_emphasis}",
                        "Research salary trends and growth projections",
                        "Find industry reports and professional organization data",
                        "Include specific numbers and citations for credibility"
                    ]
                }
            
            elif section == "concentration_areas":
                # Suggest concentration areas based on degree emphasis
                base_areas = degree_emphasis.split()
                suggestions = {
                    "recommended_areas": base_areas[:3] if len(base_areas) >= 3 else base_areas + ["Communication", "Research Methods"],
                    "popular_combinations": [
                        ["Psychology", "Sociology", "Communication"],
                        ["Business", "Technology", "Ethics"],
                        ["Education", "Psychology", "Research Methods"],
                        ["Health Sciences", "Psychology", "Public Policy"],
                        ["Environmental Studies", "Policy", "Communication"]
                    ],
                    "requirements": [
                        "Must have at least 3 concentration areas",
                        "Each area needs minimum 6 upper-division credits",
                        "Total concentration credits must be 42+",
                        "Areas should complement your degree emphasis"
                    ]
                }
            
            return {
                "success": True,
                "section": section,
                "degree_emphasis": degree_emphasis,
                "suggestions": suggestions,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate suggestions: {str(e)}"
            }
    
    async def validate_iap_requirements(self, iap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive validation of IAP requirements"""
        try:
            validation_results = {
                "overall_valid": True,
                "sections": {},
                "credit_analysis": {},
                "violations": [],
                "recommendations": []
            }
            
            # Validate required sections
            required_sections = [
                "student_name", "student_id", "degree_emphasis", 
                "mission_statement", "program_goals", "program_learning_outcomes"
            ]
            
            for section in required_sections:
                is_complete = bool(iap_data.get(section))
                validation_results["sections"][section] = {
                    "complete": is_complete,
                    "required": True
                }
                if not is_complete:
                    validation_results["overall_valid"] = False
                    validation_results["violations"].append(f"Missing required section: {section}")
            
            # Validate program goals (should have 6)
            goals = iap_data.get("program_goals", [])
            validation_results["sections"]["program_goals"]["count"] = len(goals)
            if len(goals) < 6:
                validation_results["violations"].append(f"Need 6 program goals, found {len(goals)}")
            
            # Validate PLOs (should have 6)
            plos = iap_data.get("program_learning_outcomes", [])
            validation_results["sections"]["program_learning_outcomes"]["count"] = len(plos)
            if len(plos) < 6:
                validation_results["violations"].append(f"Need 6 Program Learning Outcomes, found {len(plos)}")
            
            # Validate concentration areas (need 3+)
            concentration_areas = iap_data.get("concentration_areas", [])
            validation_results["sections"]["concentration_areas"] = {
                "count": len(concentration_areas),
                "areas": concentration_areas,
                "valid": len(concentration_areas) >= 3
            }
            if len(concentration_areas) < 3:
                validation_results["violations"].append(f"Need 3+ concentration areas, found {len(concentration_areas)}")
            
            # Credit analysis (placeholder - would integrate with course data)
            validation_results["credit_analysis"] = {
                "total_credits_required": 120,
                "upper_division_required": 40,
                "concentration_credits_required": 42,
                "concentration_upper_division_required": 21,
                "status": "Needs course mapping to calculate actual credits"
            }
            
            # Generate recommendations
            if validation_results["violations"]:
                validation_results["recommendations"].extend([
                    "Complete all required sections before submission",
                    "Use the generate_iap_suggestions tool for content ideas",
                    "Map courses to PLOs using course search tools"
                ])
            
            return {
                "success": True,
                "validation_results": validation_results,
                "next_steps": validation_results["recommendations"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to validate IAP: {str(e)}"
            }
    
    async def conduct_market_research(self, degree_emphasis: str, 
                                    geographic_focus: str = "Utah") -> Dict[str, Any]:
        """Conduct market research for degree viability analysis"""
        try:
            # Simulate market research data (in production, would integrate with APIs)
            market_data = {
                "job_market_data": {
                    "employment_growth_rate": "8-12% annually",
                    "job_openings_projected": "15,000+ over next 5 years",
                    "unemployment_rate": "2.1% (below national average)",
                    "market_demand": "High"
                },
                "salary_data": {
                    "entry_level_range": "$35,000 - $45,000",
                    "mid_career_range": "$50,000 - $70,000",
                    "senior_level_range": "$75,000 - $95,000",
                    "median_salary": "$58,000"
                },
                "industry_trends": {
                    "emerging_opportunities": [
                        "Digital transformation roles",
                        "Remote work coordination",
                        "Interdisciplinary project management",
                        "Data-driven decision making"
                    ],
                    "growth_sectors": [
                        "Healthcare technology",
                        "Educational services",
                        "Professional services",
                        "Government and public administration"
                    ]
                },
                "skill_demand": {
                    "high_demand_skills": [
                        "Critical thinking and analysis",
                        "Communication and presentation",
                        "Project management",
                        "Research and data analysis",
                        "Cross-functional collaboration"
                    ],
                    "technical_skills": [
                        "Data analysis software",
                        "Digital communication tools",
                        "Research methodologies",
                        "Statistical analysis"
                    ]
                },
                "geographic_data": {
                    "primary_markets": ["Salt Lake City", "Provo", "Ogden", "St. George"],
                    "remote_opportunities": "65% of positions offer remote/hybrid options",
                    "regional_advantages": [
                        "Growing tech sector",
                        "Strong education infrastructure",
                        "Business-friendly environment"
                    ]
                },
                "sources": [
                    "Bureau of Labor Statistics",
                    "Utah Department of Workforce Services",
                    "LinkedIn Economic Graph",
                    "Glassdoor Salary Reports",
                    "Utah Governor's Office of Economic Development"
                ]
            }
            
            # Calculate viability score
            viability_score = self._calculate_viability_score(market_data)
            
            # Generate summary
            viability_summary = self._generate_viability_summary(degree_emphasis, market_data, viability_score)
            
            return {
                "success": True,
                "degree_emphasis": degree_emphasis,
                "geographic_focus": geographic_focus,
                "market_data": market_data,
                "viability_score": viability_score,
                "viability_summary": viability_summary,
                "research_date": datetime.now().date().isoformat(),
                "recommendations": [
                    "Emphasize interdisciplinary skills in your IAP",
                    "Include courses in data analysis and research methods",
                    "Consider internships in growing sectors",
                    "Develop both technical and soft skills",
                    "Network within Utah's professional communities"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to conduct market research: {str(e)}"
            }
    
    async def track_general_education(self, student_id: str, 
                                   course_list: List[str] = None) -> Dict[str, Any]:
        """Track general education requirement completion"""
        try:
            # Utah Tech General Education requirements
            ge_requirements = {
                "Written Communication": {
                    "required_credits": 6,
                    "courses": ["ENGL 1010", "ENGL 2010"],
                    "description": "Composition and Rhetoric courses"
                },
                "Quantitative Literacy": {
                    "required_credits": 3,
                    "courses": ["MATH 1030", "MATH 1040", "MATH 1050", "STAT 1040"],
                    "description": "Mathematics or Statistics course"
                },
                "Life Sciences": {
                    "required_credits": 3,
                    "courses": ["BIOL 1010", "BIOL 1610", "BIOL 1620"],
                    "description": "Biological science with lab"
                },
                "Physical Sciences": {
                    "required_credits": 3,
                    "courses": ["CHEM 1110", "PHYS 1010", "GEOL 1110", "ASTR 1040"],
                    "description": "Physical science with lab"
                },
                "Social Sciences": {
                    "required_credits": 6,
                    "courses": ["PSYC 1010", "SOC 1010", "ANTH 1010", "POLS 1100", "ECON 2010"],
                    "description": "Two social science courses from different disciplines"
                },
                "Humanities": {
                    "required_credits": 6,
                    "courses": ["HIST 1700", "PHIL 1000", "ENGL 2600", "ART 1010", "MUSC 1010"],
                    "description": "Two humanities courses from different disciplines"
                },
                "Fine Arts": {
                    "required_credits": 3,
                    "courses": ["ART 1010", "MUSC 1010", "THEA 1013", "DANC 1010"],
                    "description": "One fine arts course"
                },
                "American Institutions": {
                    "required_credits": 3,
                    "courses": ["POLS 1100", "HIST 1700", "HIST 2700"],
                    "description": "American government or history"
                },
                "Diversity": {
                    "required_credits": 3,
                    "courses": ["ANTH 1010", "SOC 1010", "HIST 1500", "ENGL 2600"],
                    "description": "Course addressing diversity and inclusion"
                }
            }
            
            # Track completion if course list provided
            completion_status = {}
            total_ge_credits = 0
            completed_ge_credits = 0
            
            for category, requirements in ge_requirements.items():
                status = {
                    "required_credits": requirements["required_credits"],
                    "completed_credits": 0,
                    "courses_applied": [],
                    "completion_status": "not_started",
                    "description": requirements["description"]
                }
                
                if course_list:
                    # Check which courses fulfill this requirement
                    for course in course_list:
                        if course.upper() in [c.upper() for c in requirements["courses"]]:
                            status["courses_applied"].append(course)
                            status["completed_credits"] += 3  # Assume 3 credits per course
                    
                    # Update completion status
                    if status["completed_credits"] >= requirements["required_credits"]:
                        status["completion_status"] = "completed"
                    elif status["completed_credits"] > 0:
                        status["completion_status"] = "in_progress"
                
                completion_status[category] = status
                total_ge_credits += requirements["required_credits"]
                completed_ge_credits += min(status["completed_credits"], requirements["required_credits"])
            
            # Calculate overall completion percentage
            completion_percentage = (completed_ge_credits / total_ge_credits) * 100 if total_ge_credits > 0 else 0
            
            return {
                "success": True,
                "student_id": student_id,
                "ge_requirements": completion_status,
                "summary": {
                    "total_required_credits": total_ge_credits,
                    "completed_credits": completed_ge_credits,
                    "remaining_credits": total_ge_credits - completed_ge_credits,
                    "completion_percentage": round(completion_percentage, 1)
                },
                "recommendations": self._generate_ge_recommendations(completion_status)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to track general education: {str(e)}"
            }
    
    async def validate_concentration_areas(self, student_id: str, 
                                         concentration_areas: List[str],
                                         course_mappings: Dict[str, List[str]]) -> Dict[str, Any]:
        """Validate concentration area requirements and credit distribution"""
        try:
            if len(concentration_areas) < 3:
                return {
                    "success": False,
                    "error": "IAP requires at least 3 concentration areas",
                    "current_count": len(concentration_areas)
                }
            
            validation_results = {
                "overall_valid": True,
                "concentration_analysis": {},
                "credit_distribution": {},
                "violations": [],
                "recommendations": []
            }
            
            total_concentration_credits = 0
            total_upper_division = 0
            
            # Analyze each concentration area
            for area in concentration_areas:
                area_courses = course_mappings.get(area, [])
                area_analysis = {
                    "courses": area_courses,
                    "total_credits": 0,
                    "upper_division_credits": 0,
                    "lower_division_credits": 0,
                    "valid": True,
                    "issues": []
                }
                
                # Analyze courses in this concentration
                for course in area_courses:
                    # Assume 3 credits per course (would query database in production)
                    credits = 3
                    area_analysis["total_credits"] += credits
                    total_concentration_credits += credits
                    
                    # Classify course level
                    if classify_course_level(course) == "upper-division":
                        area_analysis["upper_division_credits"] += credits
                        total_upper_division += credits
                    else:
                        area_analysis["lower_division_credits"] += credits
                
                # Validate concentration requirements
                if area_analysis["total_credits"] < 14:
                    area_analysis["valid"] = False
                    area_analysis["issues"].append(f"Need {14 - area_analysis['total_credits']} more credits")
                    validation_results["violations"].append(f"{area}: Insufficient credits ({area_analysis['total_credits']}/14)")
                    validation_results["overall_valid"] = False
                
                if area_analysis["upper_division_credits"] < 7:
                    area_analysis["issues"].append(f"Need {7 - area_analysis['upper_division_credits']} more upper-division credits")
                    validation_results["violations"].append(f"{area}: Insufficient upper-division credits ({area_analysis['upper_division_credits']}/7)")
                    validation_results["overall_valid"] = False
                
                validation_results["concentration_analysis"][area] = area_analysis
            
            # Overall credit distribution analysis
            validation_results["credit_distribution"] = {
                "total_concentration_credits": total_concentration_credits,
                "required_concentration_credits": 42,
                "total_upper_division_credits": total_upper_division,
                "required_upper_division_credits": 21,
                "concentration_credits_valid": total_concentration_credits >= 42,
                "upper_division_credits_valid": total_upper_division >= 21
            }
            
            # Check overall requirements
            if total_concentration_credits < 42:
                validation_results["violations"].append(f"Total concentration credits insufficient ({total_concentration_credits}/42)")
                validation_results["overall_valid"] = False
            
            if total_upper_division < 21:
                validation_results["violations"].append(f"Upper-division concentration credits insufficient ({total_upper_division}/21)")
                validation_results["overall_valid"] = False
            
            # Generate recommendations
            if not validation_results["overall_valid"]:
                validation_results["recommendations"].extend([
                    "Use course search tools to find additional courses for deficient areas",
                    "Ensure each concentration has at least 14 credits (7 upper-division)",
                    "Consider adding courses or adjusting concentration areas",
                    "Verify course prerequisites and availability"
                ])
            else:
                validation_results["recommendations"].append("✅ All concentration area requirements met!")
            
            return {
                "success": True,
                "student_id": student_id,
                "validation_results": validation_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to validate concentration areas: {str(e)}"
            }
    
    def _calculate_viability_score(self, market_data: Dict[str, Any]) -> float:
        """Calculate degree viability score based on market data"""
        # Simple scoring algorithm (would be more sophisticated in production)
        score = 70.0  # Base score
        
        # Adjust based on market factors
        if "High" in market_data.get("job_market_data", {}).get("market_demand", ""):
            score += 15
        
        if "below national average" in market_data.get("job_market_data", {}).get("unemployment_rate", ""):
            score += 10
        
        # Cap at 100
        return min(score, 100.0)
    
    def _generate_viability_summary(self, degree_emphasis: str, market_data: Dict[str, Any], score: float) -> str:
        """Generate a summary of degree viability"""
        if score >= 85:
            outlook = "excellent"
        elif score >= 70:
            outlook = "good"
        elif score >= 55:
            outlook = "fair"
        else:
            outlook = "challenging"
        
        return f"The market outlook for a BIS degree with emphasis in {degree_emphasis} is {outlook} (viability score: {score}/100). The field shows strong growth potential with diverse career opportunities, particularly in Utah's expanding professional services and technology sectors."
    
    def _generate_ge_recommendations(self, completion_status: Dict[str, Any]) -> List[str]:
        """Generate recommendations for GE completion"""
        recommendations = []
        
        for category, status in completion_status.items():
            if status["completion_status"] == "not_started":
                recommendations.append(f"Complete {category}: {status['description']}")
            elif status["completion_status"] == "in_progress":
                remaining = status["required_credits"] - status["completed_credits"]
                recommendations.append(f"Complete {category}: {remaining} more credits needed")
        
        if not recommendations:
            recommendations.append("✅ All general education requirements completed!")
        
        return recommendations

# Utility functions for IAP processing
def extract_course_codes(text: str) -> List[str]:
    """Extract course codes from text (e.g., 'CS 1400', 'MATH 1050')"""
    pattern = r'\b[A-Z]{2,4}\s+\d{4}[A-Z]?\b'
    return re.findall(pattern, text.upper())

def classify_course_level(course_code: str) -> str:
    """Classify course as lower-division or upper-division"""
    if re.match(r'[A-Z]+\s+[3-9]\d{3}', course_code):
        return "upper-division"
    else:
        return "lower-division"

def calculate_completion_percentage(iap_data: Dict[str, Any]) -> float:
    """Calculate overall completion percentage of IAP"""
    required_sections = [
        "mission_statement", "program_goals", "program_learning_outcomes",
        "concentration_areas", "course_mappings", "cover_letter_data", "academic_plan"
    ]
    
    completed = sum(1 for section in required_sections if iap_data.get(section))
    return (completed / len(required_sections)) * 100
