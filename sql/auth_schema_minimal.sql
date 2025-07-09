-- Minimal Authentication Schema for Supabase
-- This version avoids all auth.users references to prevent errors

-- Student profiles table (minimal version)
CREATE TABLE IF NOT EXISTS student_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    student_id VARCHAR(50),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    major VARCHAR(255),
    classification VARCHAR(50),
    gpa DECIMAL(3,2),
    expected_graduation DATE,
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Simple constraints without foreign keys
    UNIQUE(user_id),
    UNIQUE(email)
);

-- Basic indexes
CREATE INDEX IF NOT EXISTS idx_student_profiles_user_id ON student_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_student_profiles_email ON student_profiles(email);

-- Enable Row Level Security
ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;

-- Simple RLS policy for user access
CREATE POLICY "Users can manage own profile" ON student_profiles
    FOR ALL USING (auth.uid() = user_id);

-- Grant basic permissions
GRANT ALL ON student_profiles TO authenticated;
GRANT ALL ON student_profiles TO anon;
