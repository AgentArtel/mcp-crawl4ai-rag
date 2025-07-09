-- Authentication and User Profile Schema
-- This schema supports user authentication and student profile management

-- Student profiles table (linked to Supabase auth.users)
CREATE TABLE IF NOT EXISTS student_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    student_id VARCHAR(50) UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    major VARCHAR(255),
    classification VARCHAR(50), -- Freshman, Sophomore, Junior, Senior, Graduate
    gpa DECIMAL(3,2),
    expected_graduation DATE,
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id),
    UNIQUE(email)
);

-- Indexes for efficient lookups
CREATE INDEX IF NOT EXISTS idx_student_profiles_user_id ON student_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_student_profiles_student_id ON student_profiles(student_id);
CREATE INDEX IF NOT EXISTS idx_student_profiles_email ON student_profiles(email);

-- Student documents table (for transcript uploads, etc.)
CREATE TABLE IF NOT EXISTS student_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES student_profiles(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL, -- 'transcript', 'degree_audit', 'transfer_credit', 'other'
    file_name VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    parsed_data JSONB DEFAULT '{}',
    parsing_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    parsing_errors TEXT[],
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for student documents
CREATE INDEX IF NOT EXISTS idx_student_documents_student_id ON student_documents(student_id);
CREATE INDEX IF NOT EXISTS idx_student_documents_type ON student_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_student_documents_status ON student_documents(parsing_status);

-- Student course history table
CREATE TABLE IF NOT EXISTS student_course_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES student_profiles(id) ON DELETE CASCADE,
    course_code VARCHAR(20) NOT NULL,
    course_title VARCHAR(255),
    credits INTEGER,
    grade VARCHAR(5),
    grade_points DECIMAL(3,2),
    semester VARCHAR(20), -- 'Fall', 'Spring', 'Summer'
    year INTEGER,
    institution VARCHAR(255) DEFAULT 'Utah Tech University',
    transfer_credit BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'completed', -- 'completed', 'in_progress', 'planned', 'dropped', 'withdrawn'
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for course history
CREATE INDEX IF NOT EXISTS idx_student_course_history_student_id ON student_course_history(student_id);
CREATE INDEX IF NOT EXISTS idx_student_course_history_course_code ON student_course_history(course_code);
CREATE INDEX IF NOT EXISTS idx_student_course_history_status ON student_course_history(status);
CREATE INDEX IF NOT EXISTS idx_student_course_history_semester_year ON student_course_history(semester, year);

-- Student graph preferences table
CREATE TABLE IF NOT EXISTS student_graph_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES student_profiles(id) ON DELETE CASCADE,
    layout_type VARCHAR(20) DEFAULT 'force-directed', -- 'force-directed', 'hierarchical', 'circular', 'tree'
    show_prerequisites BOOLEAN DEFAULT TRUE,
    show_corequisites BOOLEAN DEFAULT TRUE,
    highlight_completed BOOLEAN DEFAULT TRUE,
    highlight_in_progress BOOLEAN DEFAULT TRUE,
    color_scheme VARCHAR(20) DEFAULT 'default', -- 'default', 'colorblind', 'high-contrast', 'dark'
    zoom_level DECIMAL(3,2) DEFAULT 1.0,
    center_node VARCHAR(20),
    hidden_nodes TEXT[],
    custom_positions JSONB DEFAULT '{}',
    filter_by_discipline TEXT[],
    show_credit_hours BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(student_id)
);

-- Index for graph preferences
CREATE INDEX IF NOT EXISTS idx_student_graph_preferences_student_id ON student_graph_preferences(student_id);

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_course_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_graph_preferences ENABLE ROW LEVEL SECURITY;

-- Policies for student_profiles
CREATE POLICY "Users can view own profile" ON student_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON student_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON student_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policies for student_documents
CREATE POLICY "Users can view own documents" ON student_documents
    FOR SELECT USING (
        student_id IN (
            SELECT id FROM student_profiles WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own documents" ON student_documents
    FOR INSERT WITH CHECK (
        student_id IN (
            SELECT id FROM student_profiles WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own documents" ON student_documents
    FOR UPDATE USING (
        student_id IN (
            SELECT id FROM student_profiles WHERE user_id = auth.uid()
        )
    );

-- Policies for student_course_history
CREATE POLICY "Users can view own course history" ON student_course_history
    FOR SELECT USING (
        student_id IN (
            SELECT id FROM student_profiles WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage own course history" ON student_course_history
    FOR ALL USING (
        student_id IN (
            SELECT id FROM student_profiles WHERE user_id = auth.uid()
        )
    );

-- Policies for student_graph_preferences
CREATE POLICY "Users can manage own graph preferences" ON student_graph_preferences
    FOR ALL USING (
        student_id IN (
            SELECT id FROM student_profiles WHERE user_id = auth.uid()
        )
    );

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

-- Function to automatically create student profile after user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.student_profiles (user_id, full_name, email, student_id)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        NEW.email,
        NEW.raw_user_meta_data->>'student_id'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically create profile when user signs up
CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
