-- SQL-ONLY FIXES (what we CAN do via SQL Editor)
-- Run this in your Supabase SQL Editor first

-- ===============================
-- SECTION 1: Create Storage Bucket
-- ===============================

-- Create the student-documents bucket if it doesn't exist
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'student-documents',
    'student-documents', 
    false, -- Private bucket
    10485760, -- 10MB limit
    ARRAY['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
)
ON CONFLICT (id) DO NOTHING;

-- ===============================
-- SECTION 2: Fix student_profiles RLS (we CAN do this)
-- ===============================

-- Enable RLS on student_profiles
ALTER TABLE public.student_profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies first
DROP POLICY IF EXISTS "Users can insert their own profile" ON public.student_profiles;
DROP POLICY IF EXISTS "Users can view their own profile" ON public.student_profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON public.student_profiles;

-- Create comprehensive policies for student_profiles
CREATE POLICY "Enable insert for authenticated users on own profile"
ON public.student_profiles FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable select for authenticated users on own profile"  
ON public.student_profiles FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Enable update for authenticated users on own profile"
ON public.student_profiles FOR UPDATE  
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- ===============================
-- SECTION 3: Verification Queries
-- ===============================

-- Verify bucket exists
SELECT id, name, public, file_size_limit 
FROM storage.buckets 
WHERE id = 'student-documents';

-- Verify student_profiles policies exist  
SELECT policyname, cmd, roles
FROM pg_policies
WHERE tablename = 'student_profiles' AND schemaname = 'public';

-- Show current user (for debugging)
SELECT auth.uid() as current_user_id;
