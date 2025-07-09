# Additional IAP AI Agent Tools Plan

## High Priority Tools (Implement Next)

### 1. Credit Hour Calculator
**Function**: `calculate_credits(course_list: str) -> str`
**Purpose**: Extract credit hours and classify upper/lower division
**Implementation**: Parse course content for credit patterns, classify by course numbers

### 2. Prerequisite Chain Checker  
**Function**: `check_prerequisites(course_code: str) -> str`
**Purpose**: Validate prerequisite requirements and show chains
**Implementation**: Search for prerequisite information in course descriptions

### 3. Discipline Distribution Analyzer
**Function**: `analyze_disciplines(course_list: str) -> str` 
**Purpose**: Group courses by discipline, validate 3+ disciplines requirement
**Implementation**: Parse course prefixes, group by department codes

## Medium Priority Tools

### 4. Academic Plan Timeline Generator
**Function**: `generate_semester_plan(course_list: str, start_semester: str) -> str`
**Purpose**: Create semester-by-semester schedules
**Implementation**: Consider prerequisites, typical course offerings

### 5. General Education Checker
**Function**: `check_gen_ed_requirements(course_list: str) -> str`
**Purpose**: Validate gen ed requirements
**Implementation**: Search for gen ed categories and requirements

## Knowledge Graph Enhancement Needed

### Current State
- Neo4j knowledge graph exists but is empty
- Designed for code repositories, not academic structures

### Required Academic Schema
```cypher
// Nodes
(p:Program {name, degree_type, department, requirements})
(c:Course {code, title, credits, level, description, prerequisites})
(d:Department {name, college, prefix})
(r:Requirement {type, description, credits_needed})

// Relationships  
(c:Course)-[:PREREQUISITE]->(prereq:Course)
(c:Course)-[:BELONGS_TO]->(d:Department)
(p:Program)-[:REQUIRES]->(c:Course)
(p:Program)-[:OFFERED_BY]->(d:Department)
(r:Requirement)-[:APPLIES_TO]->(p:Program)
```

### Implementation Strategy
1. Parse crawled academic content to extract structured data
2. Create academic entities in Neo4j
3. Build relationships between courses, programs, departments
4. Enable graph-based queries for complex academic planning

## Tool Implementation Order
1. **Phase 1**: Credit calculator, prerequisite checker, discipline analyzer (RAG-based)
2. **Phase 2**: Knowledge graph schema implementation
3. **Phase 3**: Graph-enhanced tools for complex planning
4. **Phase 4**: Timeline generator and advanced planning tools
