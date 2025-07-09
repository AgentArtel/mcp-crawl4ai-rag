-- DEBUG CURRENT STATE OF STUDENT_PROFILES
-- Run this to see what's happening with RLS

-- Check current policies on student_profiles
SELECT 
    policyname,
    cmd,
    roles,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'student_profiles' AND schemaname = 'public';

-- Check if RLS is enabled
SELECT 
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE tablename = 'student_profiles' AND schemaname = 'public';

-- Check table structure and constraints
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'student_profiles' AND table_schema = 'public'
ORDER BY ordinal_position;

-- Test current authentication context
SELECT 
    auth.uid() as current_user_id,
    auth.role() as current_role;
