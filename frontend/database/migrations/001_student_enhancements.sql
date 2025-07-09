-- Migration: Student Profile Enhancements for Production Features
-- Date: 2025-01-06
-- Description: Add support for PDF uploads, transcript parsing, and graph visualization

-- 1. Create student profiles table (for frontend authentication and profile management)
-- This is separate from iap_templates which handles IAP-specific data
CREATE TABLE IF NOT EXISTS student_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_user_id UUID UNIQUE, -- References Supabase auth.users.id
  student_name TEXT NOT NULL,
  student_id TEXT UNIQUE NOT NULL, -- Utah Tech student ID
  student_email TEXT UNIQUE NOT NULL,
  student_phone TEXT,
  degree_emphasis TEXT,
  transcript_uploaded BOOLEAN DEFAULT FALSE,
  transcript_file_url TEXT,
  transcript_parsed_data JSONB,
  onboarding_completed BOOLEAN DEFAULT FALSE,
  onboarding_step INTEGER DEFAULT 0,
  degree_audit_data JSONB,
  transfer_credits JSONB,
  academic_standing TEXT,
  expected_graduation DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Document Storage Table
CREATE TABLE IF NOT EXISTS student_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES student_profiles(id) ON DELETE CASCADE,
  document_type TEXT NOT NULL CHECK (document_type IN ('transcript', 'degree_audit', 'transfer_credit', 'other')),
  file_name TEXT NOT NULL,
  file_url TEXT NOT NULL,
  file_size INTEGER,
  mime_type TEXT,
  parsed_data JSONB,
  parsing_status TEXT DEFAULT 'pending' CHECK (parsing_status IN ('pending', 'processing', 'completed', 'failed')),
  parsing_errors TEXT[],
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  processed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Course Enrollments & History Table
CREATE TABLE IF NOT EXISTS student_course_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES student_profiles(id) ON DELETE CASCADE,
  course_code TEXT NOT NULL,
  course_title TEXT,
  credits DECIMAL(3,1),
  grade TEXT,
  grade_points DECIMAL(3,2), -- For GPA calculations
  semester TEXT,
  year INTEGER,
  institution TEXT DEFAULT 'Utah Tech University',
  transfer_credit BOOLEAN DEFAULT FALSE,
  status TEXT DEFAULT 'completed' CHECK (status IN ('completed', 'in_progress', 'planned', 'dropped', 'withdrawn')),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Graph Visualization Settings Table
CREATE TABLE IF NOT EXISTS student_graph_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES student_profiles(id) ON DELETE CASCADE,
  layout_type TEXT DEFAULT 'force-directed' CHECK (layout_type IN ('force-directed', 'hierarchical', 'circular', 'tree')),
  show_prerequisites BOOLEAN DEFAULT TRUE,
  show_corequisites BOOLEAN DEFAULT TRUE,
  highlight_completed BOOLEAN DEFAULT TRUE,
  highlight_in_progress BOOLEAN DEFAULT TRUE,
  color_scheme TEXT DEFAULT 'default' CHECK (color_scheme IN ('default', 'colorblind', 'high-contrast', 'dark')),
  zoom_level DECIMAL(3,2) DEFAULT 1.0,
  center_node TEXT,
  hidden_nodes TEXT[],
  custom_positions JSONB,
  filter_by_discipline TEXT[],
  show_credit_hours BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Student Authentication & Session Management
CREATE TABLE IF NOT EXISTS student_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES student_profiles(id) ON DELETE CASCADE,
  session_token TEXT UNIQUE NOT NULL,
  refresh_token TEXT UNIQUE,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ip_address INET,
  user_agent TEXT
);

-- Performance Indexes
-- Student profiles indexes
CREATE INDEX IF NOT EXISTS idx_student_profiles_auth_user ON student_profiles(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_student_profiles_student_id ON student_profiles(student_id);
CREATE INDEX IF NOT EXISTS idx_student_profiles_email ON student_profiles(student_email);
CREATE INDEX IF NOT EXISTS idx_student_profiles_onboarding ON student_profiles(onboarding_completed);

-- Document indexes
CREATE INDEX IF NOT EXISTS idx_student_documents_student_id ON student_documents(student_id);
CREATE INDEX IF NOT EXISTS idx_student_documents_type ON student_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_student_documents_status ON student_documents(parsing_status);
CREATE INDEX IF NOT EXISTS idx_student_documents_uploaded ON student_documents(uploaded_at);

CREATE INDEX IF NOT EXISTS idx_course_history_student_id ON student_course_history(student_id);
CREATE INDEX IF NOT EXISTS idx_course_history_course_code ON student_course_history(course_code);
CREATE INDEX IF NOT EXISTS idx_course_history_status ON student_course_history(status);
CREATE INDEX IF NOT EXISTS idx_course_history_semester_year ON student_course_history(semester, year);
CREATE INDEX IF NOT EXISTS idx_course_history_institution ON student_course_history(institution);

CREATE INDEX IF NOT EXISTS idx_graph_preferences_student_id ON student_graph_preferences(student_id);

CREATE INDEX IF NOT EXISTS idx_student_sessions_student_id ON student_sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_student_sessions_token ON student_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_student_sessions_expires ON student_sessions(expires_at);

-- Row Level Security (RLS) Policies
ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_course_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_graph_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_sessions ENABLE ROW LEVEL SECURITY;

-- Students can only access their own data
CREATE POLICY student_profiles_policy ON student_profiles
  FOR ALL USING (auth.uid() = auth_user_id);

CREATE POLICY student_documents_policy ON student_documents
  FOR ALL USING (student_id IN (
    SELECT id FROM student_profiles WHERE auth_user_id = auth.uid()
  ));

CREATE POLICY student_course_history_policy ON student_course_history
  FOR ALL USING (student_id IN (
    SELECT id FROM student_profiles WHERE auth_user_id = auth.uid()
  ));

CREATE POLICY student_graph_preferences_policy ON student_graph_preferences
  FOR ALL USING (student_id IN (
    SELECT id FROM student_profiles WHERE auth_user_id = auth.uid()
  ));

CREATE POLICY student_sessions_policy ON student_sessions
  FOR ALL USING (student_id IN (
    SELECT id FROM student_profiles WHERE auth_user_id = auth.uid()
  ));

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_student_profiles_updated_at BEFORE UPDATE ON student_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_documents_updated_at BEFORE UPDATE ON student_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_course_history_updated_at BEFORE UPDATE ON student_course_history
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_graph_preferences_updated_at BEFORE UPDATE ON student_graph_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE OR REPLACE VIEW student_academic_summary AS
SELECT 
  sp.id as student_id,
  sp.student_name,
  sp.student_email,
  sp.degree_emphasis,
  sp.onboarding_completed,
  sp.transcript_uploaded,
  sp.expected_graduation,
  COUNT(sch.id) as total_courses,
  SUM(CASE WHEN sch.status = 'completed' THEN sch.credits ELSE 0 END) as completed_credits,
  SUM(CASE WHEN sch.status = 'completed' AND sch.course_code ~ '^[A-Z]{2,4} [3-9]' THEN sch.credits ELSE 0 END) as upper_division_credits,
  ROUND(AVG(CASE WHEN sch.status = 'completed' AND sch.grade_points IS NOT NULL THEN sch.grade_points END), 2) as gpa
FROM student_profiles sp
LEFT JOIN student_course_history sch ON sp.id = sch.student_id
GROUP BY sp.id, sp.student_name, sp.student_email, sp.degree_emphasis, sp.onboarding_completed, sp.transcript_uploaded, sp.expected_graduation;

-- Sample data for testing (optional - remove in production)
-- INSERT INTO student_profiles (student_name, student_id, student_email, degree_emphasis) 
-- VALUES ('Test Student', 'TEST001', 'test@utahtech.edu', 'Psychology and Digital Media')
-- ON CONFLICT (student_id) DO NOTHING;

COMMENT ON TABLE student_documents IS 'Stores uploaded student documents like transcripts and degree audits';
COMMENT ON TABLE student_course_history IS 'Complete academic history including completed, in-progress, and planned courses';
COMMENT ON TABLE student_graph_preferences IS 'User preferences for knowledge graph visualization';
COMMENT ON TABLE student_sessions IS 'Authentication session management';
COMMENT ON VIEW student_academic_summary IS 'Summary view of student academic progress and statistics';
