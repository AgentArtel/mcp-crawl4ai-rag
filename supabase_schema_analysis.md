# Supabase Schema Analysis and Alignment

## Current Supabase Schema (Based on API Analysis)

### Existing Tables

1. **`academic_search`** - Main content storage table
   - `id` (integer, primary key)
   - `url` (text)
   - `content` (text) - Large text content with embeddings
   - `embedding` (vector) - Vector embeddings for semantic search
   - `course_id` (text, nullable)
   - `course_code` (text, nullable) 
   - `course_title` (text, nullable)
   - `credits` (text, nullable)
   - `level` (text, nullable)

2. **`academic_courses`** - Dedicated course table (appears empty)
   - `course_id` (text)
   - `course_code` (text)
   - `title` (text)
   - `credits` (text)
   - `level` (text)
   - `description` (text)
   - `prerequisites` (text)
   - `url` (text)
   - `source_id` (text)
   - `created_at` (timestamp)

3. **`sources`** - Source metadata table
   - `source_id` (text, primary key)
   - `summary` (text)
   - `total_word_count` (integer, nullable)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

### Missing Tables for Academic Entities

Based on our Neo4j academic graph schema and extracted data, we need additional tables:

## Required Schema Additions

### 1. Academic Programs Table
```sql
CREATE TABLE academic_programs (
    program_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_name TEXT NOT NULL UNIQUE,
    program_type TEXT NOT NULL, -- 'Bachelor', 'Master', 'Certificate', 'Minor'
    level TEXT NOT NULL, -- 'undergraduate', 'graduate'
    department_id UUID REFERENCES academic_departments(department_id),
    description TEXT,
    requirements TEXT,
    emphasis TEXT,
    url TEXT,
    source_id TEXT REFERENCES sources(source_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. Academic Departments Table
```sql
CREATE TABLE academic_departments (
    department_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    department_name TEXT NOT NULL UNIQUE,
    prefix TEXT NOT NULL UNIQUE, -- 'CS', 'ART', 'NURS', etc.
    college_id UUID REFERENCES academic_colleges(college_id),
    description TEXT,
    url TEXT,
    source_id TEXT REFERENCES sources(source_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. Academic Colleges Table
```sql
CREATE TABLE academic_colleges (
    college_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    college_name TEXT NOT NULL UNIQUE,
    university_id UUID REFERENCES academic_universities(university_id),
    description TEXT,
    url TEXT,
    source_id TEXT REFERENCES sources(source_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. Academic Universities Table
```sql
CREATE TABLE academic_universities (
    university_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    university_name TEXT NOT NULL UNIQUE,
    description TEXT,
    url TEXT,
    source_id TEXT REFERENCES sources(source_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 5. Course Prerequisites Table (Many-to-Many)
```sql
CREATE TABLE course_prerequisites (
    prerequisite_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_code TEXT NOT NULL REFERENCES academic_courses(course_code),
    prerequisite_course_code TEXT NOT NULL REFERENCES academic_courses(course_code),
    requirement_type TEXT DEFAULT 'prerequisite', -- 'prerequisite', 'corequisite', 'recommended'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(course_code, prerequisite_course_code)
);
```

### 6. Program Requirements Table
```sql
CREATE TABLE program_requirements (
    requirement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID REFERENCES academic_programs(program_id),
    requirement_type TEXT NOT NULL, -- 'core', 'elective', 'general_education', 'emphasis'
    course_code TEXT REFERENCES academic_courses(course_code),
    credit_hours INTEGER,
    requirement_description TEXT,
    is_required BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Schema Modifications Needed

### 1. Update `academic_courses` Table
```sql
-- Add missing columns to academic_courses
ALTER TABLE academic_courses 
ADD COLUMN IF NOT EXISTS department_id UUID REFERENCES academic_departments(department_id),
ADD COLUMN IF NOT EXISTS prefix TEXT,
ADD COLUMN IF NOT EXISTS course_number TEXT,
ADD COLUMN IF NOT EXISTS prerequisites_text TEXT,
ADD COLUMN IF NOT EXISTS semesters_offered TEXT,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Update credits column to integer
ALTER TABLE academic_courses 
ALTER COLUMN credits TYPE INTEGER USING credits::integer;

-- Add constraints
ALTER TABLE academic_courses 
ADD CONSTRAINT unique_course_code UNIQUE (course_code);
```

### 2. Update `academic_search` Table
```sql
-- Add academic entity references to academic_search
ALTER TABLE academic_search 
ADD COLUMN IF NOT EXISTS department_id UUID REFERENCES academic_departments(department_id),
ADD COLUMN IF NOT EXISTS program_id UUID REFERENCES academic_programs(program_id),
ADD COLUMN IF NOT EXISTS content_type TEXT, -- 'course', 'program', 'department', 'general'
ADD COLUMN IF NOT EXISTS chunk_metadata JSONB; -- Store chunking metadata
```

## Indexes for Performance

```sql
-- Course search indexes
CREATE INDEX IF NOT EXISTS idx_academic_courses_prefix ON academic_courses(prefix);
CREATE INDEX IF NOT EXISTS idx_academic_courses_level ON academic_courses(level);
CREATE INDEX IF NOT EXISTS idx_academic_courses_department ON academic_courses(department_id);

-- Program search indexes
CREATE INDEX IF NOT EXISTS idx_academic_programs_type ON academic_programs(program_type);
CREATE INDEX IF NOT EXISTS idx_academic_programs_level ON academic_programs(level);
CREATE INDEX IF NOT EXISTS idx_academic_programs_department ON academic_programs(department_id);

-- Content search indexes
CREATE INDEX IF NOT EXISTS idx_academic_search_content_type ON academic_search(content_type);
CREATE INDEX IF NOT EXISTS idx_academic_search_course_code ON academic_search(course_code);

-- Prerequisites indexes
CREATE INDEX IF NOT EXISTS idx_course_prerequisites_course ON course_prerequisites(course_code);
CREATE INDEX IF NOT EXISTS idx_course_prerequisites_prereq ON course_prerequisites(prerequisite_course_code);
```

## Data Migration Strategy

1. **Create new tables** in the order: universities → colleges → departments → programs
2. **Populate base data** from Neo4j extraction results
3. **Update existing courses** with department references
4. **Extract and populate prerequisites** from course descriptions
5. **Link programs to requirements** based on catalog content

## Alignment with Neo4j Schema

The Supabase schema will complement the Neo4j graph by:
- **Supabase**: Storing detailed content, descriptions, and metadata
- **Neo4j**: Modeling relationships, prerequisites chains, and graph queries
- **Sync Strategy**: Academic graph builder populates both systems simultaneously

## Benefits of Enhanced Schema

1. **Structured Academic Data**: Proper normalization of academic entities
2. **Relationship Modeling**: Prerequisites, program requirements, department structure
3. **Enhanced Search**: Better filtering and categorization capabilities
4. **Data Integrity**: Foreign key constraints and proper data types
5. **Performance**: Optimized indexes for common academic queries
6. **Scalability**: Supports future academic entity types and relationships
