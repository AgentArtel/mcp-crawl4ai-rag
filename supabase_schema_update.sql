-- Supabase Schema Update Script for Utah Tech Academic Knowledge Graph
-- This script creates the necessary tables and relationships for academic entities

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Create Academic Universities Table
CREATE TABLE IF NOT EXISTS academic_universities (
    university_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    university_name TEXT NOT NULL UNIQUE,
    description TEXT,
    url TEXT,
    source_id TEXT REFERENCES sources(source_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create Academic Colleges Table
CREATE TABLE IF NOT EXISTS academic_colleges (
    college_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    college_name TEXT NOT NULL UNIQUE,
    university_id UUID REFERENCES academic_universities(university_id),
    description TEXT,
    url TEXT,
    source_id TEXT REFERENCES sources(source_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create Academic Programs Table
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Update Academic Courses Table (add missing columns)
ALTER TABLE academic_courses 
ADD COLUMN IF NOT EXISTS department_id UUID REFERENCES academic_departments(department_id),
ADD COLUMN IF NOT EXISTS prefix TEXT,
ADD COLUMN IF NOT EXISTS course_number TEXT,
ADD COLUMN IF NOT EXISTS prerequisites_text TEXT,
ADD COLUMN IF NOT EXISTS semesters_offered TEXT,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Update credits column to integer (handle existing data safely)
DO $$
BEGIN
    -- Check if credits column exists and is not integer
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'academic_courses' 
        AND column_name = 'credits' 
        AND data_type != 'integer'
    ) THEN
        -- Update credits to integer, handling non-numeric values
        UPDATE academic_courses 
        SET credits = CASE 
            WHEN credits ~ '^[0-9]+$' THEN credits::integer::text
            ELSE '3' -- Default to 3 credits for non-numeric values
        END;
        
        -- Change column type
        ALTER TABLE academic_courses 
        ALTER COLUMN credits TYPE INTEGER USING COALESCE(credits::integer, 3);
    END IF;
END $$;

-- Add constraints to academic_courses
ALTER TABLE academic_courses 
ADD CONSTRAINT IF NOT EXISTS unique_course_code UNIQUE (course_code);

-- 6. Create Course Prerequisites Table (Many-to-Many)
CREATE TABLE IF NOT EXISTS course_prerequisites (
    prerequisite_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_code TEXT NOT NULL,
    prerequisite_course_code TEXT NOT NULL,
    requirement_type TEXT DEFAULT 'prerequisite', -- 'prerequisite', 'corequisite', 'recommended'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(course_code, prerequisite_course_code)
);

-- Add foreign key constraints for prerequisites (after courses are populated)
-- ALTER TABLE course_prerequisites 
-- ADD CONSTRAINT fk_course_prerequisites_course 
-- FOREIGN KEY (course_code) REFERENCES academic_courses(course_code);

-- ALTER TABLE course_prerequisites 
-- ADD CONSTRAINT fk_course_prerequisites_prereq 
-- FOREIGN KEY (prerequisite_course_code) REFERENCES academic_courses(course_code);

-- 7. Create Program Requirements Table
CREATE TABLE IF NOT EXISTS program_requirements (
    requirement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID REFERENCES academic_programs(program_id),
    requirement_type TEXT NOT NULL, -- 'core', 'elective', 'general_education', 'emphasis'
    course_code TEXT,
    credit_hours INTEGER,
    requirement_description TEXT,
    is_required BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Update Academic Search Table (add academic entity references)
ALTER TABLE academic_search 
ADD COLUMN IF NOT EXISTS department_id UUID REFERENCES academic_departments(department_id),
ADD COLUMN IF NOT EXISTS program_id UUID REFERENCES academic_programs(program_id),
ADD COLUMN IF NOT EXISTS content_type TEXT, -- 'course', 'program', 'department', 'general'
ADD COLUMN IF NOT EXISTS chunk_metadata JSONB; -- Store chunking metadata

-- 9. Create Performance Indexes

-- Course search indexes
CREATE INDEX IF NOT EXISTS idx_academic_courses_prefix ON academic_courses(prefix);
CREATE INDEX IF NOT EXISTS idx_academic_courses_level ON academic_courses(level);
CREATE INDEX IF NOT EXISTS idx_academic_courses_department ON academic_courses(department_id);
CREATE INDEX IF NOT EXISTS idx_academic_courses_credits ON academic_courses(credits);

-- Program search indexes
CREATE INDEX IF NOT EXISTS idx_academic_programs_type ON academic_programs(program_type);
CREATE INDEX IF NOT EXISTS idx_academic_programs_level ON academic_programs(level);
CREATE INDEX IF NOT EXISTS idx_academic_programs_department ON academic_programs(department_id);

-- Department indexes
CREATE INDEX IF NOT EXISTS idx_academic_departments_prefix ON academic_departments(prefix);
CREATE INDEX IF NOT EXISTS idx_academic_departments_college ON academic_departments(college_id);

-- Content search indexes
CREATE INDEX IF NOT EXISTS idx_academic_search_content_type ON academic_search(content_type);
CREATE INDEX IF NOT EXISTS idx_academic_search_course_code ON academic_search(course_code);
CREATE INDEX IF NOT EXISTS idx_academic_search_department ON academic_search(department_id);
CREATE INDEX IF NOT EXISTS idx_academic_search_program ON academic_search(program_id);

-- Prerequisites indexes
CREATE INDEX IF NOT EXISTS idx_course_prerequisites_course ON course_prerequisites(course_code);
CREATE INDEX IF NOT EXISTS idx_course_prerequisites_prereq ON course_prerequisites(prerequisite_course_code);

-- Program requirements indexes
CREATE INDEX IF NOT EXISTS idx_program_requirements_program ON program_requirements(program_id);
CREATE INDEX IF NOT EXISTS idx_program_requirements_type ON program_requirements(requirement_type);
CREATE INDEX IF NOT EXISTS idx_program_requirements_course ON program_requirements(course_code);

-- 10. Create Row Level Security (RLS) Policies

-- Enable RLS on new tables
ALTER TABLE academic_universities ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_colleges ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_prerequisites ENABLE ROW LEVEL SECURITY;
ALTER TABLE program_requirements ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access (adjust as needed for your security requirements)
CREATE POLICY IF NOT EXISTS "Public read access" ON academic_universities FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "Public read access" ON academic_colleges FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "Public read access" ON academic_departments FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "Public read access" ON academic_programs FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "Public read access" ON course_prerequisites FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "Public read access" ON program_requirements FOR SELECT USING (true);

-- Service role policies for full access (for MCP server operations)
CREATE POLICY IF NOT EXISTS "Service role full access" ON academic_universities FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY IF NOT EXISTS "Service role full access" ON academic_colleges FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY IF NOT EXISTS "Service role full access" ON academic_departments FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY IF NOT EXISTS "Service role full access" ON academic_programs FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY IF NOT EXISTS "Service role full access" ON course_prerequisites FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY IF NOT EXISTS "Service role full access" ON program_requirements FOR ALL USING (auth.role() = 'service_role');

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

-- Create triggers for updated_at
CREATE TRIGGER update_academic_universities_updated_at BEFORE UPDATE ON academic_universities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_academic_colleges_updated_at BEFORE UPDATE ON academic_colleges FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_academic_departments_updated_at BEFORE UPDATE ON academic_departments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_academic_programs_updated_at BEFORE UPDATE ON academic_programs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_academic_courses_updated_at BEFORE UPDATE ON academic_courses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 13. Create Views for Common Queries

-- View for courses with department information
CREATE OR REPLACE VIEW courses_with_departments AS
SELECT 
    c.*,
    d.department_name,
    d.prefix as department_prefix,
    col.college_name,
    u.university_name
FROM academic_courses c
LEFT JOIN academic_departments d ON c.department_id = d.department_id
LEFT JOIN academic_colleges col ON d.college_id = col.college_id
LEFT JOIN academic_universities u ON col.university_id = u.university_id;

-- View for programs with department information
CREATE OR REPLACE VIEW programs_with_departments AS
SELECT 
    p.*,
    d.department_name,
    d.prefix as department_prefix,
    col.college_name,
    u.university_name
FROM academic_programs p
LEFT JOIN academic_departments d ON p.department_id = d.department_id
LEFT JOIN academic_colleges col ON d.college_id = col.college_id
LEFT JOIN academic_universities u ON col.university_id = u.university_id;

-- View for prerequisite chains
CREATE OR REPLACE VIEW prerequisite_chains AS
SELECT 
    cp.course_code,
    c1.title as course_title,
    cp.prerequisite_course_code,
    c2.title as prerequisite_title,
    cp.requirement_type
FROM course_prerequisites cp
LEFT JOIN academic_courses c1 ON cp.course_code = c1.course_code
LEFT JOIN academic_courses c2 ON cp.prerequisite_course_code = c2.course_code;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Utah Tech Academic Schema Update completed successfully!';
    RAISE NOTICE 'Created tables: academic_universities, academic_colleges, academic_departments, academic_programs, course_prerequisites, program_requirements';
    RAISE NOTICE 'Updated tables: academic_courses, academic_search';
    RAISE NOTICE 'Created indexes, policies, triggers, and views';
    RAISE NOTICE 'Ready for academic data population from Neo4j graph builder';
END $$;
