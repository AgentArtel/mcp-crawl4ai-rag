-- Utah Tech Academic Schema Migration - Refined for Existing Database
-- This script extends your existing schema with academic hierarchy and knowledge graph support

-- 1. Create Academic Universities Table
CREATE TABLE IF NOT EXISTS academic_universities (
    university_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    university_name TEXT NOT NULL UNIQUE,
    description TEXT,
    url TEXT,
    source_id TEXT REFERENCES sources(source_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create Academic Colleges Table
CREATE TABLE IF NOT EXISTS academic_colleges (
    college_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    college_name TEXT NOT NULL UNIQUE,
    university_id UUID REFERENCES academic_universities(university_id),
    description TEXT,
    url TEXT,
    source_id TEXT REFERENCES sources(source_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create Academic Departments Table
CREATE TABLE IF NOT EXISTS academic_departments (
    department_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    department_name TEXT NOT NULL UNIQUE,
    prefix TEXT NOT NULL UNIQUE, -- 'CS', 'ART', 'NURS', etc.
    college_id UUID REFERENCES academic_colleges(college_id),
    description TEXT,
    url TEXT,
    source_id TEXT REFERENCES sources(source_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Create Academic Programs Table (degree programs, emphases)
CREATE TABLE IF NOT EXISTS academic_programs (
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
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Extend existing academic_courses table with department reference
ALTER TABLE academic_courses 
ADD COLUMN IF NOT EXISTS department_id UUID REFERENCES academic_departments(department_id),
ADD COLUMN IF NOT EXISTS prefix TEXT,
ADD COLUMN IF NOT EXISTS course_number TEXT,
ADD COLUMN IF NOT EXISTS prerequisites_text TEXT,
ADD COLUMN IF NOT EXISTS semesters_offered TEXT,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- 6. Create Course Prerequisites Table (structured prerequisite relationships)
CREATE TABLE IF NOT EXISTS course_prerequisites (
    prerequisite_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id INTEGER REFERENCES academic_courses(course_id) ON DELETE CASCADE,
    prerequisite_course_id INTEGER REFERENCES academic_courses(course_id) ON DELETE CASCADE,
    requirement_type TEXT DEFAULT 'prerequisite', -- 'prerequisite', 'corequisite', 'recommended'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(course_id, prerequisite_course_id)
);

-- 7. Create Program Requirements Table (which courses are required for which programs)
CREATE TABLE IF NOT EXISTS program_requirements (
    requirement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID REFERENCES academic_programs(program_id) ON DELETE CASCADE,
    requirement_type TEXT NOT NULL, -- 'core', 'elective', 'general_education', 'emphasis'
    course_id INTEGER REFERENCES academic_courses(course_id) ON DELETE CASCADE,
    credit_hours NUMERIC(3,1),
    requirement_description TEXT,
    is_required BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Extend crawled_pages table with academic entity references
ALTER TABLE crawled_pages 
ADD COLUMN IF NOT EXISTS department_id UUID REFERENCES academic_departments(department_id),
ADD COLUMN IF NOT EXISTS program_id UUID REFERENCES academic_programs(program_id),
ADD COLUMN IF NOT EXISTS content_type TEXT, -- 'course', 'program', 'department', 'general'
ADD COLUMN IF NOT EXISTS chunk_metadata JSONB; -- Additional chunking metadata

-- 9. Create Performance Indexes

-- Course search indexes
CREATE INDEX IF NOT EXISTS idx_academic_courses_prefix ON academic_courses(prefix);
CREATE INDEX IF NOT EXISTS idx_academic_courses_level ON academic_courses(level);
CREATE INDEX IF NOT EXISTS idx_academic_courses_department ON academic_courses(department_id);
CREATE INDEX IF NOT EXISTS idx_academic_courses_course_code ON academic_courses(course_code);

-- Program search indexes
CREATE INDEX IF NOT EXISTS idx_academic_programs_type ON academic_programs(program_type);
CREATE INDEX IF NOT EXISTS idx_academic_programs_level ON academic_programs(level);
CREATE INDEX IF NOT EXISTS idx_academic_programs_department ON academic_programs(department_id);

-- Department indexes
CREATE INDEX IF NOT EXISTS idx_academic_departments_prefix ON academic_departments(prefix);
CREATE INDEX IF NOT EXISTS idx_academic_departments_college ON academic_departments(college_id);

-- Content search indexes
CREATE INDEX IF NOT EXISTS idx_crawled_pages_content_type ON crawled_pages(content_type);
CREATE INDEX IF NOT EXISTS idx_crawled_pages_department ON crawled_pages(department_id);
CREATE INDEX IF NOT EXISTS idx_crawled_pages_program ON crawled_pages(program_id);

-- Prerequisites indexes
CREATE INDEX IF NOT EXISTS idx_course_prerequisites_course ON course_prerequisites(course_id);
CREATE INDEX IF NOT EXISTS idx_course_prerequisites_prereq ON course_prerequisites(prerequisite_course_id);

-- Program requirements indexes
CREATE INDEX IF NOT EXISTS idx_program_requirements_program ON program_requirements(program_id);
CREATE INDEX IF NOT EXISTS idx_program_requirements_type ON program_requirements(requirement_type);
CREATE INDEX IF NOT EXISTS idx_program_requirements_course ON program_requirements(course_id);

-- 10. Create Row Level Security (RLS) Policies

-- Enable RLS on new tables
ALTER TABLE academic_universities ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_colleges ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_prerequisites ENABLE ROW LEVEL SECURITY;
ALTER TABLE program_requirements ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access (matching your existing pattern)
CREATE POLICY IF NOT EXISTS "Allow public read access to academic_universities"
  ON academic_universities FOR SELECT TO public USING (true);

CREATE POLICY IF NOT EXISTS "Allow public read access to academic_colleges"
  ON academic_colleges FOR SELECT TO public USING (true);

CREATE POLICY IF NOT EXISTS "Allow public read access to academic_departments"
  ON academic_departments FOR SELECT TO public USING (true);

CREATE POLICY IF NOT EXISTS "Allow public read access to academic_programs"
  ON academic_programs FOR SELECT TO public USING (true);

CREATE POLICY IF NOT EXISTS "Allow public read access to course_prerequisites"
  ON course_prerequisites FOR SELECT TO public USING (true);

CREATE POLICY IF NOT EXISTS "Allow public read access to program_requirements"
  ON program_requirements FOR SELECT TO public USING (true);

-- 11. Insert Initial Data

-- Insert Utah Tech University
INSERT INTO academic_universities (university_name, description, url, source_id)
VALUES (
    'Utah Tech University',
    'Utah Tech University is a public university in St. George, Utah, offering undergraduate and graduate programs.',
    'https://utahtech.edu/',
    'catalog.utahtech.edu'
) ON CONFLICT (university_name) DO NOTHING;

-- 12. Create Functions for Data Maintenance

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at (only for new tables, academic_courses already has created_at)
CREATE TRIGGER IF NOT EXISTS update_academic_universities_updated_at 
    BEFORE UPDATE ON academic_universities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_academic_colleges_updated_at 
    BEFORE UPDATE ON academic_colleges FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_academic_departments_updated_at 
    BEFORE UPDATE ON academic_departments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_academic_programs_updated_at 
    BEFORE UPDATE ON academic_programs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_academic_courses_updated_at 
    BEFORE UPDATE ON academic_courses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 13. Enhanced Search Functions

-- Enhanced function to search academic content with hierarchy
CREATE OR REPLACE FUNCTION match_academic_content (
  query_embedding vector(1536),
  match_count int default 10,
  filter jsonb DEFAULT '{}'::jsonb,
  source_filter text DEFAULT NULL,
  content_type_filter text DEFAULT NULL,
  department_filter text DEFAULT NULL
) returns table (
  id bigint,
  url varchar,
  chunk_number integer,
  content text,
  metadata jsonb,
  source_id text,
  content_type text,
  department_name text,
  program_name text,
  course_code text,
  course_title text,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    cp.id,
    cp.url,
    cp.chunk_number,
    cp.content,
    cp.metadata,
    cp.source_id,
    cp.content_type,
    d.department_name,
    p.program_name,
    ac.course_code,
    ac.title as course_title,
    1 - (cp.embedding <=> query_embedding) as similarity
  from crawled_pages cp
  left join academic_departments d on cp.department_id = d.department_id
  left join academic_programs p on cp.program_id = p.program_id
  left join crawled_page_course_mapping cpcm on cp.id = cpcm.page_id
  left join academic_courses ac on cpcm.course_id = ac.course_id
  where cp.metadata @> filter
    AND (source_filter IS NULL OR cp.source_id = source_filter)
    AND (content_type_filter IS NULL OR cp.content_type = content_type_filter)
    AND (department_filter IS NULL OR d.prefix = department_filter)
  order by cp.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- 14. Create Enhanced Views

-- Enhanced academic_search view with hierarchy
CREATE OR REPLACE VIEW academic_search_enhanced AS
SELECT 
    cp.id,
    cp.url,
    cp.content,
    cp.metadata,
    cp.source_id,
    cp.embedding,
    cp.content_type,
    cp.chunk_metadata,
    -- Course information
    ac.course_id,
    ac.course_code,
    ac.title as course_title,
    ac.credits,
    ac.level,
    ac.description as course_description,
    ac.prerequisites,
    -- Department information
    d.department_id,
    d.department_name,
    d.prefix as department_prefix,
    -- Program information
    p.program_id,
    p.program_name,
    p.program_type,
    p.level as program_level,
    p.emphasis,
    -- College information
    c.college_id,
    c.college_name,
    -- University information
    u.university_id,
    u.university_name
FROM 
    crawled_pages cp
LEFT JOIN crawled_page_course_mapping cpcm ON cp.id = cpcm.page_id
LEFT JOIN academic_courses ac ON cpcm.course_id = ac.course_id
LEFT JOIN academic_departments d ON cp.department_id = d.department_id OR ac.department_id = d.department_id
LEFT JOIN academic_programs p ON cp.program_id = p.program_id
LEFT JOIN academic_colleges c ON d.college_id = c.college_id
LEFT JOIN academic_universities u ON c.university_id = u.university_id;

-- View for courses with full hierarchy
CREATE OR REPLACE VIEW courses_with_hierarchy AS
SELECT 
    ac.*,
    d.department_name,
    d.prefix as department_prefix,
    c.college_name,
    u.university_name
FROM academic_courses ac
LEFT JOIN academic_departments d ON ac.department_id = d.department_id
LEFT JOIN academic_colleges c ON d.college_id = c.college_id
LEFT JOIN academic_universities u ON c.university_id = u.university_id;

-- View for programs with hierarchy
CREATE OR REPLACE VIEW programs_with_hierarchy AS
SELECT 
    p.*,
    d.department_name,
    d.prefix as department_prefix,
    c.college_name,
    u.university_name
FROM academic_programs p
LEFT JOIN academic_departments d ON p.department_id = d.department_id
LEFT JOIN academic_colleges c ON d.college_id = c.college_id
LEFT JOIN academic_universities u ON c.university_id = u.university_id;

-- View for prerequisite chains with course details
CREATE OR REPLACE VIEW prerequisite_chains AS
SELECT 
    cp.course_id,
    c1.course_code,
    c1.title as course_title,
    cp.prerequisite_course_id,
    c2.course_code as prerequisite_course_code,
    c2.title as prerequisite_title,
    cp.requirement_type
FROM course_prerequisites cp
LEFT JOIN academic_courses c1 ON cp.course_id = c1.course_id
LEFT JOIN academic_courses c2 ON cp.prerequisite_course_id = c2.course_id;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Utah Tech Academic Schema Migration completed successfully!';
    RAISE NOTICE 'Extended existing schema with: academic_universities, academic_colleges, academic_departments, academic_programs';
    RAISE NOTICE 'Added relationship tables: course_prerequisites, program_requirements';
    RAISE NOTICE 'Enhanced existing tables: academic_courses, crawled_pages';
    RAISE NOTICE 'Created enhanced views and search functions';
    RAISE NOTICE 'Ready for academic data population from Neo4j graph builder';
END $$;
