-- DEBUG STUDENT_PROFILES RLS POLICIES
-- Run this to see what policies currently exist

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
    rowsecurity 
FROM pg_tables 
WHERE tablename = 'student_profiles' AND schemaname = 'public';

-- Check table structure
\d public.student_profiles

-- Test current user context
SELECT 
    auth.uid() as current_user_id,
    auth.role() as current_role;
