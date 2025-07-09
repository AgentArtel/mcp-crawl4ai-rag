-- Fix student_name column issue in student_profiles table
-- The table has 'student_name' but our code is trying to insert 'full_name'

-- Option 1: Rename student_name to full_name to match our code
ALTER TABLE student_profiles 
RENAME COLUMN student_name TO full_name;

-- OR Option 2: If you prefer to keep student_name, we'll update the code instead
-- (Comment out the above line and uncomment the line below if you prefer this approach)
-- ALTER TABLE student_profiles ALTER COLUMN student_name DROP NOT NULL;

-- Check the current table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'student_profiles' 
ORDER BY ordinal_position;
