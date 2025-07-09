"""
Graph-Enhanced Academic Planning Tools

This module provides advanced academic planning tools that leverage the Neo4j knowledge graph
containing prerequisite relationships, course hierarchies, and academic program structures.
These tools enable intelligent academic advising for Utah Tech's IAP (Individualized Academic Plan) program.
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv
import os

# Load environment variables from project root
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / '.env')

@dataclass
class CourseNode:
    """Represents a course in the knowledge graph"""
    code: str
    title: str
    credits: int
    level: str  # 'lower-division', 'upper-division', 'graduate'
    department: str
    description: str
    prerequisites: List[str]

@dataclass
class PrerequisitePath:
    """Represents a prerequisite path/chain"""
    target_course: str
    path: List[str]
    total_credits: int
    semesters_needed: int

@dataclass
class AcademicPlan:
    """Represents an academic plan with course sequencing"""
    courses: List[str]
    total_credits: int
    upper_division_credits: int
    disciplines: Set[str]
    prerequisite_violations: List[str]
    recommended_sequence: List[List[str]]  # Semester-by-semester

class GraphEnhancedAcademicPlanner:
    """
    Advanced academic planning using Neo4j knowledge graph with prerequisite relationships.
    """
    
    def __init__(self):
        # Force localhost connection to avoid Docker internal hostname issues
        self.neo4j_uri = 'bolt://localhost:7687'
        self.neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        self.neo4j_password = os.getenv('NEO4J_PASSWORD', 'password123')
        self.driver = None
    
    async def connect(self):
        """Connect to Neo4j database"""
        if not self.driver:
            self.driver = AsyncGraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
        return self.driver
    
    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
            self.driver = None
    
    async def get_course_prerequisites(self, course_code: str) -> List[str]:
        """Get direct prerequisites for a course"""
        driver = await self.connect()
        
        async with driver.session() as session:
            result = await session.run("""
                MATCH (prereq:Course)-[:PREREQUISITE_FOR]->(course:Course {code: $course_code})
                RETURN prereq.code as prerequisite
                ORDER BY prereq.code
            """, course_code=course_code)
            
            prerequisites = []
            async for record in result:
                prerequisites.append(record["prerequisite"])
            
            return prerequisites
    
    async def get_prerequisite_chain(self, course_code: str, max_depth: int = 10) -> List[PrerequisitePath]:
        """Get complete prerequisite chain for a course"""
        driver = await self.connect()
        
        async with driver.session() as session:
            result = await session.run("""
                MATCH path = (start:Course)-[:PREREQUISITE_FOR*1..10]->(target:Course {code: $course_code})
                WITH path, length(path) as depth
                WHERE depth <= $max_depth
                RETURN [node in nodes(path) | node.code] as course_path,
                       [node in nodes(path) | node.credits] as credit_path,
                       depth
                ORDER BY depth DESC
            """, course_code=course_code, max_depth=max_depth)
            
            paths = []
            async for record in result:
                course_path = record["course_path"]
                credit_path = record["credit_path"]
                depth = record["depth"]
                
                # Calculate total credits and estimated semesters
                total_credits = sum(credit_path)
                semesters_needed = max(1, (depth + 1) // 2)  # Rough estimate
                
                paths.append(PrerequisitePath(
                    target_course=course_code,
                    path=course_path,
                    total_credits=total_credits,
                    semesters_needed=semesters_needed
                ))
            
            return paths
    
    async def find_courses_by_level(self, level: str, department: str = None, limit: int = 50) -> List[CourseNode]:
        """Find courses by level (upper-division, lower-division, graduate)"""
        driver = await self.connect()
        
        # Build query based on parameters
        where_clauses = ["course.level = $level"]
        params = {"level": level, "limit": limit}
        
        if department:
            where_clauses.append("course.department = $department")
            params["department"] = department
        
        where_clause = " AND ".join(where_clauses)
        
        async with driver.session() as session:
            result = await session.run(f"""
                MATCH (course:Course)
                WHERE {where_clause}
                OPTIONAL MATCH (prereq:Course)-[:PREREQUISITE_FOR]->(course)
                RETURN course.code as code,
                       course.title as title,
                       course.credits as credits,
                       course.level as level,
                       course.department as department,
                       course.description as description,
                       collect(prereq.code) as prerequisites
                ORDER BY course.code
                LIMIT $limit
            """, **params)
            
            courses = []
            async for record in result:
                courses.append(CourseNode(
                    code=record["code"],
                    title=record["title"],
                    credits=record["credits"] or 3,  # Default to 3 credits
                    level=record["level"],
                    department=record["department"],
                    description=record["description"] or "",
                    prerequisites=[p for p in record["prerequisites"] if p]
                ))
            
            return courses
    
    async def validate_course_sequence(self, course_codes: List[str]) -> Dict[str, Any]:
        """Validate if a sequence of courses respects prerequisite requirements"""
        driver = await self.connect()
        
        violations = []
        course_info = {}
        
        # Get course information and prerequisites
        async with driver.session() as session:
            for course_code in course_codes:
                result = await session.run("""
                    MATCH (course:Course {code: $course_code})
                    OPTIONAL MATCH (prereq:Course)-[:PREREQUISITE_FOR]->(course)
                    RETURN course.code as code,
                           course.title as title,
                           course.credits as credits,
                           course.level as level,
                           course.department as department,
                           collect(prereq.code) as prerequisites
                """, course_code=course_code)
                
                record = await result.single()
                if record:
                    course_info[course_code] = {
                        "code": record["code"],
                        "title": record["title"],
                        "credits": record["credits"] or 3,
                        "level": record["level"],
                        "department": record["department"],
                        "prerequisites": [p for p in record["prerequisites"] if p]
                    }
        
        # Check prerequisite violations
        completed_courses = set()
        for course_code in course_codes:
            if course_code in course_info:
                prerequisites = course_info[course_code]["prerequisites"]
                missing_prereqs = [p for p in prerequisites if p not in completed_courses]
                
                if missing_prereqs:
                    violations.append({
                        "course": course_code,
                        "missing_prerequisites": missing_prereqs,
                        "message": f"{course_code} requires {', '.join(missing_prereqs)} which are not completed yet"
                    })
                
                completed_courses.add(course_code)
        
        # Calculate statistics
        total_credits = sum(info["credits"] for info in course_info.values())
        upper_division_credits = sum(
            info["credits"] for info in course_info.values() 
            if info["level"] == "upper-division"
        )
        disciplines = set(info["department"] for info in course_info.values())
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "statistics": {
                "total_courses": len(course_info),
                "total_credits": total_credits,
                "upper_division_credits": upper_division_credits,
                "disciplines": list(disciplines),
                "discipline_count": len(disciplines)
            },
            "course_details": course_info
        }
    
    async def recommend_course_sequence(self, target_courses: List[str], max_credits_per_semester: int = 15, max_semesters: int = 8) -> AcademicPlan:
        """Recommend optimal course sequence respecting prerequisites"""
        driver = await self.connect()
        
        # Get all courses and their prerequisites
        all_courses = {}
        prerequisite_graph = {}
        
        async with driver.session() as session:
            # Get course information
            for course_code in target_courses:
                result = await session.run("""
                    MATCH (course:Course {code: $course_code})
                    OPTIONAL MATCH (prereq:Course)-[:PREREQUISITE_FOR]->(course)
                    RETURN course.code as code,
                           course.title as title,
                           course.credits as credits,
                           course.level as level,
                           course.department as department,
                           collect(prereq.code) as prerequisites
                """, course_code=course_code)
                
                record = await result.single()
                if record:
                    all_courses[course_code] = CourseNode(
                        code=record["code"],
                        title=record["title"],
                        credits=record["credits"] or 3,
                        level=record["level"],
                        department=record["department"],
                        description="",
                        prerequisites=[p for p in record["prerequisites"] if p]
                    )
                    prerequisite_graph[course_code] = [p for p in record["prerequisites"] if p]
        
        # Topological sort to determine course order
        sequence = self._topological_sort(target_courses, prerequisite_graph)
        
        # Group courses into semesters (assuming 15 credits per semester max)
        semester_sequence = []
        current_semester = []
        current_credits = 0
        # Use the provided max_credits_per_semester parameter
        
        for course_code in sequence:
            if course_code in all_courses:
                course = all_courses[course_code]
                
                # Check if adding this course would exceed semester credit limit
                if current_credits + course.credits > max_credits_per_semester and current_semester:
                    semester_sequence.append(current_semester)
                    current_semester = [course_code]
                    current_credits = course.credits
                else:
                    current_semester.append(course_code)
                    current_credits += course.credits
        
        # Add final semester if not empty
        if current_semester:
            semester_sequence.append(current_semester)
        
        # Calculate plan statistics
        total_credits = sum(course.credits for course in all_courses.values())
        upper_division_credits = sum(
            course.credits for course in all_courses.values() 
            if course.level == "upper-division"
        )
        disciplines = set(course.department for course in all_courses.values())
        
        return AcademicPlan(
            courses=list(all_courses.keys()),
            total_credits=total_credits,
            upper_division_credits=upper_division_credits,
            disciplines=disciplines,
            prerequisite_violations=[],  # Should be none with proper sequencing
            recommended_sequence=semester_sequence
        )
    
    def _topological_sort(self, courses: List[str], prerequisite_graph: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort on course prerequisite graph"""
        # Build in-degree count
        in_degree = {course: 0 for course in courses}
        
        for course in courses:
            for prereq in prerequisite_graph.get(course, []):
                if prereq in in_degree:
                    in_degree[course] += 1
        
        # Queue courses with no prerequisites
        queue = [course for course, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Reduce in-degree for courses that depend on current course
            for course in courses:
                if current in prerequisite_graph.get(course, []):
                    in_degree[course] -= 1
                    if in_degree[course] == 0:
                        queue.append(course)
        
        return result
    
    async def find_alternative_courses(self, course_code: str, same_department: bool = True, limit: int = 10) -> List[CourseNode]:
        """Find alternative courses that could substitute for a given course"""
        driver = await self.connect()
        
        async with driver.session() as session:
            # Get the target course info
            result = await session.run("""
                MATCH (course:Course {code: $course_code})
                RETURN course.level as level, course.department as department, course.credits as credits
            """, course_code=course_code)
            
            record = await result.single()
            if not record:
                return []
            
            level = record["level"]
            department = record["department"]
            credits = record["credits"]
            
            # Find similar courses
            where_clauses = ["alt.code <> $course_code", "alt.level = $level"]
            params = {"course_code": course_code, "level": level, "limit": limit}
            
            if same_department and department:
                where_clauses.append("alt.department = $department")
                params["department"] = department
            
            if credits:
                where_clauses.append("alt.credits = $credits")
                params["credits"] = credits
            
            where_clause = " AND ".join(where_clauses)
            
            result = await session.run(f"""
                MATCH (alt:Course)
                WHERE {where_clause}
                OPTIONAL MATCH (prereq:Course)-[:PREREQUISITE_FOR]->(alt)
                RETURN alt.code as code,
                       alt.title as title,
                       alt.credits as credits,
                       alt.level as level,
                       alt.department as department,
                       alt.description as description,
                       collect(prereq.code) as prerequisites
                ORDER BY alt.code
                LIMIT $limit
            """, **params)
            
            alternatives = []
            async for record in result:
                alternatives.append(CourseNode(
                    code=record["code"],
                    title=record["title"],
                    credits=record["credits"] or 3,
                    level=record["level"],
                    department=record["department"],
                    description=record["description"] or "",
                    prerequisites=[p for p in record["prerequisites"] if p]
                ))
            
            return alternatives
    
    async def analyze_degree_progress(self, completed_courses: List[str], target_courses: List[str]) -> Dict[str, Any]:
        """Analyze progress toward degree completion"""
        driver = await self.connect()
        
        # Get information about completed and target courses
        all_course_codes = list(set(completed_courses + target_courses))
        course_info = {}
        
        async with driver.session() as session:
            for course_code in all_course_codes:
                result = await session.run("""
                    MATCH (course:Course {code: $course_code})
                    RETURN course.code as code,
                           course.title as title,
                           course.credits as credits,
                           course.level as level,
                           course.department as department
                """, course_code=course_code)
                
                record = await result.single()
                if record:
                    course_info[course_code] = {
                        "code": record["code"],
                        "title": record["title"],
                        "credits": record["credits"] or 3,
                        "level": record["level"],
                        "department": record["department"]
                    }
        
        # Calculate completed statistics
        completed_credits = sum(
            course_info[code]["credits"] for code in completed_courses 
            if code in course_info
        )
        completed_upper_division = sum(
            course_info[code]["credits"] for code in completed_courses 
            if code in course_info and course_info[code]["level"] == "upper-division"
        )
        completed_disciplines = set(
            course_info[code]["department"] for code in completed_courses 
            if code in course_info
        )
        
        # Calculate remaining requirements
        remaining_courses = [code for code in target_courses if code not in completed_courses]
        remaining_credits = sum(
            course_info[code]["credits"] for code in remaining_courses 
            if code in course_info
        )
        remaining_upper_division = sum(
            course_info[code]["credits"] for code in remaining_courses 
            if code in course_info and course_info[code]["level"] == "upper-division"
        )
        
        total_credits = completed_credits + remaining_credits
        total_upper_division = completed_upper_division + remaining_upper_division
        
        # IAP requirements check
        meets_credit_requirement = total_credits >= 120
        meets_upper_division_requirement = total_upper_division >= 40
        meets_discipline_requirement = len(completed_disciplines) >= 3
        
        return {
            "completed": {
                "courses": len(completed_courses),
                "credits": completed_credits,
                "upper_division_credits": completed_upper_division,
                "disciplines": list(completed_disciplines),
                "discipline_count": len(completed_disciplines)
            },
            "remaining": {
                "courses": len(remaining_courses),
                "course_list": remaining_courses,
                "credits": remaining_credits,
                "upper_division_credits": remaining_upper_division
            },
            "totals": {
                "credits": total_credits,
                "upper_division_credits": total_upper_division,
                "disciplines": list(completed_disciplines)
            },
            "iap_requirements": {
                "total_credits": {
                    "required": 120,
                    "current": total_credits,
                    "met": meets_credit_requirement,
                    "remaining": max(0, 120 - total_credits)
                },
                "upper_division_credits": {
                    "required": 40,
                    "current": total_upper_division,
                    "met": meets_upper_division_requirement,
                    "remaining": max(0, 40 - total_upper_division)
                },
                "disciplines": {
                    "required": 3,
                    "current": len(completed_disciplines),
                    "met": meets_discipline_requirement,
                    "remaining": max(0, 3 - len(completed_disciplines))
                }
            },
            "overall_progress": {
                "percentage": min(100, (total_credits / 120) * 100),
                "ready_to_graduate": meets_credit_requirement and meets_upper_division_requirement and meets_discipline_requirement
            }
        }
