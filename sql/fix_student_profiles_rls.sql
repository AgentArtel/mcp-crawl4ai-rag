-- FOCUSED FIX FOR STUDENT_PROFILES RLS
-- This addresses the specific "new row violates row-level security policy" error

-- ===============================
-- SECTION 1: Disable RLS temporarily to clean up
-- ===============================

-- Disable RLS temporarily
ALTER TABLE public.student_profiles DISABLE ROW LEVEL SECURITY;

-- Drop ALL existing policies (clean slate)
DROP POLICY IF EXISTS "Enable insert for authenticated users on own profile" ON public.student_profiles;
DROP POLICY IF EXISTS "Enable select for authenticated users on own profile" ON public.student_profiles;  
DROP POLICY IF EXISTS "Enable update for authenticated users on own profile" ON public.student_profiles;
DROP POLICY IF EXISTS "Users can insert their own profile" ON public.student_profiles;
DROP POLICY IF EXISTS "Users can view their own profile" ON public.student_profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON public.student_profiles;

-- ===============================
-- SECTION 2: Re-enable RLS and create simple policies
-- ===============================

-- Re-enable RLS
ALTER TABLE public.student_profiles ENABLE ROW LEVEL SECURITY;

-- Create simple, permissive policies for authenticated users
CREATE POLICY "Allow authenticated users to insert profiles"
ON public.student_profiles FOR INSERT
TO authenticated
WITH CHECK (true);  -- Allow any authenticated user to insert

CREATE POLICY "Allow users to view own profiles"  
ON public.student_profiles FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Allow users to update own profiles"
ON public.student_profiles FOR UPDATE  
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- ===============================
-- SECTION 3: Verification
-- ===============================

-- Verify policies exist
SELECT policyname, cmd, roles
FROM pg_policies
WHERE tablename = 'student_profiles' AND schemaname = 'public';

-- Check RLS status
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'student_profiles' AND schemaname = 'public';

-- Show current user for debugging
SELECT auth.uid() as current_user_id;
