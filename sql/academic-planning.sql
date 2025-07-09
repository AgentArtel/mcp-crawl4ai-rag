-- 1. Academic courses (extended from crawled content)
CREATE TABLE IF NOT EXISTS academic_courses (
    course_id SERIAL PRIMARY KEY,
    course_code TEXT NOT NULL,  -- e.g., "CS 1010"
    title TEXT NOT NULL,
    credits NUMERIC(3,1),
    level TEXT,  -- 'lower' or 'upper' division
    description TEXT,
    prerequisites TEXT,
    url TEXT,  -- Link back to the original page
    source_id TEXT REFERENCES sources(source_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(course_code)
);

-- 2. Map crawled pages to academic courses
CREATE TABLE IF NOT EXISTS crawled_page_course_mapping (
    id SERIAL PRIMARY KEY,
    page_id BIGINT REFERENCES crawled_pages(id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES academic_courses(course_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(page_id, course_id)
);

-- 3. General education requirements
CREATE TABLE IF NOT EXISTS gen_ed_requirements (
    requirement_id SERIAL PRIMARY KEY,
    code TEXT NOT NULL,  -- e.g., "EN", "QL"
    name TEXT NOT NULL,  -- e.g., "English", "Quantitative Literacy"
    description TEXT,
    credits_required INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Course to Gen Ed requirement mapping
CREATE TABLE IF NOT EXISTS course_gen_ed_mapping (
    course_id INTEGER REFERENCES academic_courses(course_id) ON DELETE CASCADE,
    requirement_id INTEGER REFERENCES gen_ed_requirements(requirement_id) ON DELETE CASCADE,
    PRIMARY KEY (course_id, requirement_id)
);

-- 5. Student plans (IAPs)
CREATE TABLE IF NOT EXISTS student_plans (
    plan_id SERIAL PRIMARY KEY,
    student_id TEXT NOT NULL,
    emphasis_title TEXT,
    mission_statement TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Plan courses (courses in a student's IAP)
CREATE TABLE IF NOT EXISTS plan_courses (
    plan_course_id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES student_plans(plan_id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES academic_courses(course_id) ON DELETE CASCADE,
    semester TEXT,  -- e.g., "Fall 2024"
    is_completed BOOLEAN DEFAULT FALSE,
    grade TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(plan_id, course_id, semester)
);

-- 7. Create a view for searching academic content
CREATE OR REPLACE VIEW academic_search AS
SELECT 
    cp.id,
    cp.url,
    cp.content,
    cp.metadata,
    cp.source_id,
    cp.embedding,
    ac.course_id,
    ac.course_code,
    ac.title as course_title,
    ac.credits,
    ac.level
FROM 
    crawled_pages cp
LEFT JOIN 
    crawled_page_course_mapping cpcm ON cp.id = cpcm.page_id
LEFT JOIN 
    academic_courses ac ON cpcm.course_id = ac.course_id;