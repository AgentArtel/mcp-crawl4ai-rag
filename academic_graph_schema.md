# Academic Knowledge Graph Schema Design

## Overview
This document outlines the Neo4j knowledge graph schema for Utah Tech University's academic data to support the IAP AI Agent's advanced academic planning capabilities.

## Node Types

### 1. University
```cypher
(u:University {
  name: string,
  code: string,
  website: string,
  created_at: datetime
})
```

### 2. College
```cypher
(c:College {
  name: string,
  code: string,
  description: string,
  website: string,
  created_at: datetime
})
```

### 3. Department
```cypher
(d:Department {
  name: string,
  code: string,
  prefix: string,  // e.g., "CS", "MATH", "BIOL"
  description: string,
  website: string,
  created_at: datetime
})
```

### 4. Program
```cypher
(p:Program {
  name: string,
  code: string,
  type: string,  // "Bachelor", "Master", "Certificate", "Minor"
  level: string, // "undergraduate", "graduate"
  total_credits: integer,
  description: string,
  mission_statement: string,
  website: string,
  created_at: datetime
})
```

### 5. Course
```cypher
(course:Course {
  code: string,        // "CS 1400"
  prefix: string,      // "CS"
  number: string,      // "1400"
  title: string,       // "Fundamentals of Programming"
  credits: integer,    // 3
  level: string,       // "lower_division", "upper_division", "graduate"
  description: string,
  prerequisites_text: string,
  corequisites_text: string,
  offered_semesters: [string], // ["Fall", "Spring", "Summer"]
  created_at: datetime
})
```

### 6. Requirement
```cypher
(r:Requirement {
  name: string,
  type: string,  // "core", "elective", "general_education", "emphasis"
  credits_required: integer,
  description: string,
  created_at: datetime
})
```

### 7. Emphasis
```cypher
(e:Emphasis {
  name: string,
  code: string,
  description: string,
  credits_required: integer,
  created_at: datetime
})
```

## Relationships

### Organizational Structure
```cypher
(u:University)-[:HAS_COLLEGE]->(c:College)
(c:College)-[:HAS_DEPARTMENT]->(d:Department)
(d:Department)-[:OFFERS_PROGRAM]->(p:Program)
(d:Department)-[:OFFERS_COURSE]->(course:Course)
```

### Program Structure
```cypher
(p:Program)-[:HAS_REQUIREMENT]->(r:Requirement)
(p:Program)-[:HAS_EMPHASIS]->(e:Emphasis)
(e:Emphasis)-[:HAS_REQUIREMENT]->(r:Requirement)
```

### Course Relationships
```cypher
(course1:Course)-[:PREREQUISITE_FOR]->(course2:Course)
(course1:Course)-[:COREQUISITE_WITH]->(course2:Course)
(r:Requirement)-[:SATISFIED_BY]->(course:Course)
(course:Course)-[:BELONGS_TO_DISCIPLINE]->(d:Department)
```

### Academic Planning
```cypher
(course:Course)-[:COUNTS_TOWARD]->(r:Requirement)
(course:Course)-[:APPLICABLE_TO]->(p:Program)
(course:Course)-[:FULFILLS_EMPHASIS]->(e:Emphasis)
```

## Sample Queries

### 1. Find all prerequisites for a course
```cypher
MATCH (prereq:Course)-[:PREREQUISITE_FOR*]->(target:Course {code: 'CS 3400'})
RETURN prereq.code, prereq.title
ORDER BY prereq.code
```

### 2. Find courses that count toward multiple disciplines
```cypher
MATCH (course:Course)-[:BELONGS_TO_DISCIPLINE]->(d:Department)
WITH course, count(d) as discipline_count
WHERE discipline_count > 1
RETURN course.code, course.title, discipline_count
```

### 3. Find all requirements for a program
```cypher
MATCH (p:Program {name: 'Bachelor of Individualized Studies'})-[:HAS_REQUIREMENT]->(r:Requirement)
OPTIONAL MATCH (r)-[:SATISFIED_BY]->(course:Course)
RETURN r.name, r.type, r.credits_required, collect(course.code) as applicable_courses
```

### 4. Find courses for cross-disciplinary planning
```cypher
MATCH (d1:Department)-[:OFFERS_COURSE]->(c1:Course)
MATCH (d2:Department)-[:OFFERS_COURSE]->(c2:Course)
WHERE d1.prefix <> d2.prefix
AND c1.level = 'upper_division'
AND c2.level = 'upper_division'
RETURN d1.prefix, c1.code, c1.title, d2.prefix, c2.code, c2.title
LIMIT 20
```

## Implementation Plan

### Phase 1: Schema Creation
1. Create Cypher scripts to define node labels and relationships
2. Set up indexes for performance optimization
3. Create constraints for data integrity

### Phase 2: Data Extraction
1. Parse crawled academic content to extract structured data
2. Identify courses, programs, departments, and requirements
3. Extract prerequisite relationships from course descriptions

### Phase 3: Graph Population
1. Create academic entities in Neo4j
2. Build relationships between courses, programs, departments
3. Populate prerequisite chains and requirement mappings

### Phase 4: Graph-Enhanced Tools
1. Implement graph-based academic planning queries
2. Create tools that leverage relationship traversal
3. Enable complex multi-step academic planning scenarios

## Data Sources
- Utah Tech University course catalog (catalog.utahtech.edu)
- Department pages with program information
- Course description pages with prerequisite details
- Program requirement pages

## Performance Considerations
- Index on Course.code, Course.prefix, Course.number
- Index on Program.name, Program.type
- Index on Department.prefix
- Composite indexes for common query patterns
