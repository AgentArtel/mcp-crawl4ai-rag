-- Add email column to student_profiles table
-- This migration adds the missing email column that's causing registration failures

ALTER TABLE student_profiles 
ADD COLUMN email TEXT;

-- Add a comment to document the column
COMMENT ON COLUMN student_profiles.email IS 'Student email address from auth.users';

-- Optionally, you can populate existing records with email from auth.users
-- UPDATE student_profiles 
-- SET email = auth.users.email 
-- FROM auth.users 
-- WHERE student_profiles.user_id = auth.users.id 
-- AND student_profiles.email IS NULL;
