-- Add missing columns to student_profiles table
-- This migration adds all the missing columns that are causing registration failures

-- Add full_name column
ALTER TABLE student_profiles 
ADD COLUMN IF NOT EXISTS full_name TEXT;

-- Add email column (if not already added)
ALTER TABLE student_profiles 
ADD COLUMN IF NOT EXISTS email TEXT;

-- Add student_id column (if not already exists)
ALTER TABLE student_profiles 
ADD COLUMN IF NOT EXISTS student_id TEXT;

-- Add preferences column (if not already exists)
ALTER TABLE student_profiles 
ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{"theme": "light", "notifications": true, "onboarding_completed": false}'::jsonb;

-- Add comments to document the columns
COMMENT ON COLUMN student_profiles.full_name IS 'Student full name from registration';
COMMENT ON COLUMN student_profiles.email IS 'Student email address from auth.users';
COMMENT ON COLUMN student_profiles.student_id IS 'Student ID number (auto-generated if not provided)';
COMMENT ON COLUMN student_profiles.preferences IS 'Student preferences and settings as JSON';

-- Show the current structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'student_profiles' 
ORDER BY ordinal_position;
