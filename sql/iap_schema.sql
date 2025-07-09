-- IAP Template Management Schema
-- This schema supports the complete Individualized Academic Plan (IAP) workflow

-- Main IAP templates table
CREATE TABLE IF NOT EXISTS iap_templates (
    id SERIAL PRIMARY KEY,
    student_name VARCHAR(255) NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    student_email VARCHAR(255),
    student_phone VARCHAR(50),
    degree_emphasis VARCHAR(255) NOT NULL,
    
    -- Cover Letter Data
    cover_letter_data JSONB DEFAULT '{}',
    
    -- Program Definition
    mission_statement TEXT,
    program_goals JSONB DEFAULT '[]', -- Array of goal strings
    program_learning_outcomes JSONB DEFAULT '[]', -- Array of PLO objects
    
    -- Course Mappings
    course_mappings JSONB DEFAULT '{}', -- Maps PLO IDs to course arrays
    concentration_areas JSONB DEFAULT '[]', -- Array of concentration area names
    
    -- Academic Plan Tracking
    general_education JSONB DEFAULT '{}', -- GE completion tracking
    inds_core_courses JSONB DEFAULT '{}', -- INDS required courses
    concentration_courses JSONB DEFAULT '{}', -- Lower/upper division courses
    
    -- Requirements Validation
    credit_summary JSONB DEFAULT '{}', -- Total credits, upper division, etc.
    completion_status JSONB DEFAULT '{}', -- Section completion tracking
    validation_results JSONB DEFAULT '{}', -- Latest validation results
    
    -- Metadata
    semester_year_inds3800 VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(student_id, degree_emphasis)
);

-- Index for efficient lookups
CREATE INDEX IF NOT EXISTS idx_iap_student_id ON iap_templates(student_id);
CREATE INDEX IF NOT EXISTS idx_iap_emphasis ON iap_templates(degree_emphasis);
CREATE INDEX IF NOT EXISTS idx_iap_updated ON iap_templates(updated_at);

-- IAP Course Mappings table (for detailed course-to-PLO relationships)
CREATE TABLE IF NOT EXISTS iap_course_mappings (
    id SERIAL PRIMARY KEY,
    iap_id INTEGER REFERENCES iap_templates(id) ON DELETE CASCADE,
    course_code VARCHAR(20) NOT NULL,
    course_title VARCHAR(255),
    course_credits INTEGER,
    course_level VARCHAR(20), -- 'lower-division', 'upper-division'
    concentration_area VARCHAR(255),
    mapped_plos JSONB DEFAULT '[]', -- Array of PLO IDs this course maps to
    course_type VARCHAR(50), -- 'general_education', 'inds_core', 'concentration', 'elective'
    semester_planned VARCHAR(50),
    completion_status VARCHAR(20) DEFAULT 'planned', -- 'planned', 'in_progress', 'completed'
    grade VARCHAR(5),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for efficient course lookups
CREATE INDEX IF NOT EXISTS idx_iap_course_iap_id ON iap_course_mappings(iap_id);
CREATE INDEX IF NOT EXISTS idx_iap_course_code ON iap_course_mappings(course_code);
CREATE INDEX IF NOT EXISTS idx_iap_course_type ON iap_course_mappings(course_type);

-- General Education Tracking table
CREATE TABLE IF NOT EXISTS iap_general_education (
    id SERIAL PRIMARY KEY,
    iap_id INTEGER REFERENCES iap_templates(id) ON DELETE CASCADE,
    ge_category VARCHAR(100) NOT NULL, -- 'Written Communication', 'Quantitative Literacy', etc.
    ge_requirement VARCHAR(255) NOT NULL, -- Specific requirement description
    required_credits INTEGER DEFAULT 3,
    completed_credits INTEGER DEFAULT 0,
    courses_applied JSONB DEFAULT '[]', -- Array of course codes that fulfill this requirement
    completion_status VARCHAR(20) DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed'
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Market Research Data table
CREATE TABLE IF NOT EXISTS iap_market_research (
    id SERIAL PRIMARY KEY,
    iap_id INTEGER REFERENCES iap_templates(id) ON DELETE CASCADE,
    degree_emphasis VARCHAR(255) NOT NULL,
    job_market_data JSONB DEFAULT '{}', -- Employment statistics, growth rates, etc.
    salary_data JSONB DEFAULT '{}', -- Salary ranges, median income, etc.
    industry_trends JSONB DEFAULT '{}', -- Industry growth, emerging opportunities
    skill_demand JSONB DEFAULT '{}', -- In-demand skills and competencies
    geographic_data JSONB DEFAULT '{}', -- Regional job availability
    sources JSONB DEFAULT '[]', -- Data sources and citations
    research_date DATE DEFAULT CURRENT_DATE,
    viability_score FLOAT, -- 0-100 score for degree viability
    viability_summary TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Concentration Area Validation table
CREATE TABLE IF NOT EXISTS iap_concentration_validation (
    id SERIAL PRIMARY KEY,
    iap_id INTEGER REFERENCES iap_templates(id) ON DELETE CASCADE,
    concentration_name VARCHAR(255) NOT NULL,
    required_credits INTEGER DEFAULT 14, -- Minimum credits per concentration
    completed_credits INTEGER DEFAULT 0,
    upper_division_credits INTEGER DEFAULT 0,
    lower_division_credits INTEGER DEFAULT 0,
    courses JSONB DEFAULT '[]', -- Array of course objects with codes, credits, levels
    validation_status VARCHAR(20) DEFAULT 'incomplete', -- 'incomplete', 'valid', 'invalid'
    validation_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Course-to-PLO Mapping Enhancement table
CREATE TABLE IF NOT EXISTS iap_course_plo_mappings (
    id SERIAL PRIMARY KEY,
    iap_id INTEGER REFERENCES iap_templates(id) ON DELETE CASCADE,
    course_code VARCHAR(20) NOT NULL,
    course_title VARCHAR(255),
    plo_id VARCHAR(10) NOT NULL, -- PLO1, PLO2, etc.
    plo_description TEXT,
    mapping_strength VARCHAR(20) DEFAULT 'strong', -- 'strong', 'moderate', 'weak'
    evidence_description TEXT, -- How the course supports the PLO
    assessment_methods JSONB DEFAULT '[]', -- How PLO achievement is assessed
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_iap_ge_iap_id ON iap_general_education(iap_id);
CREATE INDEX IF NOT EXISTS idx_iap_ge_category ON iap_general_education(ge_category);
CREATE INDEX IF NOT EXISTS idx_iap_market_iap_id ON iap_market_research(iap_id);
CREATE INDEX IF NOT EXISTS idx_iap_market_emphasis ON iap_market_research(degree_emphasis);
CREATE INDEX IF NOT EXISTS idx_iap_conc_iap_id ON iap_concentration_validation(iap_id);
CREATE INDEX IF NOT EXISTS idx_iap_conc_name ON iap_concentration_validation(concentration_name);
CREATE INDEX IF NOT EXISTS idx_iap_plo_iap_id ON iap_course_plo_mappings(iap_id);
CREATE INDEX IF NOT EXISTS idx_iap_plo_course ON iap_course_plo_mappings(course_code);

-- Enhanced IAP Templates View (for easy querying)
CREATE OR REPLACE VIEW iap_summary AS
SELECT 
    t.id,
    t.student_name,
    t.student_id,
    t.degree_emphasis,
    t.mission_statement IS NOT NULL as has_mission,
    jsonb_array_length(t.program_goals) as goals_count,
    jsonb_array_length(t.program_learning_outcomes) as plo_count,
    jsonb_array_length(t.concentration_areas) as concentration_count,
    (t.credit_summary->>'total_credits')::INTEGER as total_credits,
    (t.credit_summary->>'upper_division_credits')::INTEGER as upper_division_credits,
    (t.completion_status->>'overall_percentage')::FLOAT as completion_percentage,
    -- GE completion summary
    COALESCE(ge_stats.total_ge_categories, 0) as total_ge_categories,
    COALESCE(ge_stats.completed_ge_categories, 0) as completed_ge_categories,
    COALESCE(ge_stats.ge_completion_percentage, 0) as ge_completion_percentage,
    -- Market research availability
    mr.viability_score,
    mr.research_date as market_research_date,
    -- Concentration validation summary
    COALESCE(conc_stats.total_concentrations, 0) as total_concentrations,
    COALESCE(conc_stats.valid_concentrations, 0) as valid_concentrations,
    t.updated_at
FROM iap_templates t
LEFT JOIN (
    SELECT 
        iap_id,
        COUNT(*) as total_ge_categories,
        COUNT(CASE WHEN completion_status = 'completed' THEN 1 END) as completed_ge_categories,
        ROUND((COUNT(CASE WHEN completion_status = 'completed' THEN 1 END) * 100.0 / COUNT(*)), 2) as ge_completion_percentage
    FROM iap_general_education
    GROUP BY iap_id
) ge_stats ON t.id = ge_stats.iap_id
LEFT JOIN iap_market_research mr ON t.id = mr.iap_id
LEFT JOIN (
    SELECT 
        iap_id,
        COUNT(*) as total_concentrations,
        COUNT(CASE WHEN validation_status = 'valid' THEN 1 END) as valid_concentrations
    FROM iap_concentration_validation
    GROUP BY iap_id
) conc_stats ON t.id = conc_stats.iap_id;

-- Sample data structure comments:
/*
program_goals example:
[
  "Students will demonstrate proficiency in interdisciplinary research methods",
  "Students will apply critical thinking skills across multiple disciplines",
  ...
]

program_learning_outcomes example:
[
  {
    "id": "PLO1",
    "description": "Students will analyze complex problems using interdisciplinary approaches",
    "lower_division_courses": ["PSYC 1010", "SOC 1010"],
    "upper_division_courses": ["PSYC 3100", "SOC 3200"]
  },
  ...
]

course_mappings example:
{
  "PLO1": ["PSYC 1010", "PSYC 3100", "SOC 1010"],
  "PLO2": ["ENGL 2010", "COMM 3000"],
  ...
}

concentration_areas example:
["Psychology", "Sociology", "Communication"]

credit_summary example:
{
  "total_credits": 120,
  "upper_division_credits": 45,
  "concentration_credits": 42,
  "general_education_credits": 39,
  "inds_core_credits": 7
}
*/
