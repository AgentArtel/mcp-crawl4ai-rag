-- Utah Tech Academic Tables Creation Script
-- Run this directly in your Supabase SQL Editor

-- 1. Create Academic Departments Table
CREATE TABLE IF NOT EXISTS academic_departments (
    department_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    department_name TEXT NOT NULL UNIQUE,
    prefix TEXT NOT NULL UNIQUE, -- 'CS', 'ART', 'NURS', etc.
    description TEXT,
    url TEXT,
    source_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create Academic Programs Table
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
    source_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Extend existing academic_courses table (if it exists) or create it
DO $$
BEGIN
    -- Check if academic_courses table exists
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'academic_courses') THEN
        -- Add missing columns to existing table
        ALTER TABLE academic_courses 
        ADD COLUMN IF NOT EXISTS department_id UUID REFERENCES academic_departments(department_id),
        ADD COLUMN IF NOT EXISTS prefix TEXT,
        ADD COLUMN IF NOT EXISTS course_number TEXT,
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
        
        -- Update prefix and course_number from course_code if they're empty
        UPDATE academic_courses 
        SET prefix = SPLIT_PART(course_code, ' ', 1),
            course_number = SPLIT_PART(course_code, ' ', 2)
        WHERE prefix IS NULL OR course_number IS NULL;
    ELSE
        -- Create academic_courses table from scratch
        CREATE TABLE academic_courses (
            course_id SERIAL PRIMARY KEY,
            course_code TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            credits NUMERIC(3,1) DEFAULT 3.0,
            level TEXT, -- 'lower-division' or 'upper-division'
            description TEXT,
            prerequisites TEXT,
            prefix TEXT,
            course_number TEXT,
            department_id UUID REFERENCES academic_departments(department_id),
            url TEXT,
            source_id TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
    END IF;
END $$;

-- 4. Create Course Prerequisites Table
CREATE TABLE IF NOT EXISTS course_prerequisites (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES academic_courses(course_id) ON DELETE CASCADE,
    prerequisite_course_id INTEGER REFERENCES academic_courses(course_id) ON DELETE CASCADE,
    requirement_type TEXT DEFAULT 'prerequisite', -- 'prerequisite', 'corequisite', 'recommended'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(course_id, prerequisite_course_id)
);

-- 5. Create Program Course Mappings Table
CREATE TABLE IF NOT EXISTS program_course_mappings (
    id SERIAL PRIMARY KEY,
    program_id UUID REFERENCES academic_programs(program_id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES academic_courses(course_id) ON DELETE CASCADE,
    requirement_type TEXT NOT NULL, -- 'core', 'elective', 'concentration'
    is_required BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(program_id, course_id)
);

-- 6. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_academic_departments_prefix ON academic_departments(prefix);
CREATE INDEX IF NOT EXISTS idx_academic_programs_type ON academic_programs(program_type);
CREATE INDEX IF NOT EXISTS idx_academic_programs_level ON academic_programs(level);
CREATE INDEX IF NOT EXISTS idx_academic_programs_department ON academic_programs(department_id);
CREATE INDEX IF NOT EXISTS idx_academic_courses_prefix ON academic_courses(prefix);
CREATE INDEX IF NOT EXISTS idx_academic_courses_level ON academic_courses(level);
CREATE INDEX IF NOT EXISTS idx_academic_courses_department ON academic_courses(department_id);
CREATE INDEX IF NOT EXISTS idx_academic_courses_course_code ON academic_courses(course_code);
CREATE INDEX IF NOT EXISTS idx_course_prerequisites_course ON course_prerequisites(course_id);
CREATE INDEX IF NOT EXISTS idx_course_prerequisites_prereq ON course_prerequisites(prerequisite_course_id);
CREATE INDEX IF NOT EXISTS idx_program_course_mappings_program ON program_course_mappings(program_id);
CREATE INDEX IF NOT EXISTS idx_program_course_mappings_course ON program_course_mappings(course_id);

-- 7. Create updated_at trigger function (if it doesn't exist)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 8. Create triggers for updated_at columns (drop first if they exist)
DROP TRIGGER IF EXISTS update_academic_departments_updated_at ON academic_departments;
CREATE TRIGGER update_academic_departments_updated_at 
    BEFORE UPDATE ON academic_departments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_academic_programs_updated_at ON academic_programs;
CREATE TRIGGER update_academic_programs_updated_at 
    BEFORE UPDATE ON academic_programs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_academic_courses_updated_at ON academic_courses;
CREATE TRIGGER update_academic_courses_updated_at 
    BEFORE UPDATE ON academic_courses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 9. Insert some sample data to verify tables work
INSERT INTO academic_departments (department_name, prefix, description) VALUES
('Computer Science', 'CS', 'Computer Science Department'),
('Mathematics', 'MATH', 'Mathematics Department'),
('English', 'ENGL', 'English Department'),
('Psychology', 'PSYC', 'Psychology Department'),
('Biology', 'BIOL', 'Biology Department')
ON CONFLICT (department_name) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Academic tables created successfully!';
    RAISE NOTICE 'Tables created: academic_departments, academic_programs, academic_courses (extended), course_prerequisites, program_course_mappings';
    RAISE NOTICE 'Sample departments inserted. Ready for data population.';
END $$;
