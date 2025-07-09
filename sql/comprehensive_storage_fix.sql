-- COMPREHENSIVE STORAGE AND RLS FIX
-- Run each section one by one in Supabase SQL Editor

-- ===============================
-- SECTION 1: Create Storage Bucket
-- ===============================

-- Check if bucket exists first
DO $$
BEGIN
    -- Try to create the bucket, ignore if it already exists
    INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
    VALUES (
        'student-documents',
        'student-documents', 
        false,
        10485760, -- 10MB
        ARRAY['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    )
    ON CONFLICT (id) DO NOTHING;
    RAISE NOTICE 'Storage bucket student-documents created or already exists';
END $$;

-- ===============================
-- SECTION 2: Enable RLS and Drop Existing Policies
-- ===============================

-- Enable RLS on storage.objects (should already be enabled)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Drop all existing storage policies to start fresh
DROP POLICY IF EXISTS "Users can upload their own documents" ON storage.objects;
DROP POLICY IF EXISTS "Users can view their own documents" ON storage.objects;  
DROP POLICY IF EXISTS "Users can delete their own documents" ON storage.objects;

-- ===============================
-- SECTION 3: Create Storage Policies
-- ===============================

-- Policy 1: Allow authenticated users to upload to student-documents bucket
CREATE POLICY "Allow authenticated upload to student-documents"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'student-documents'
);

-- Policy 2: Allow users to view their own files
CREATE POLICY "Allow users to view own files in student-documents"
ON storage.objects FOR SELECT
TO authenticated  
USING (
    bucket_id = 'student-documents' AND
    (auth.uid()::text = (string_to_array(name, '/'))[1])
);

-- Policy 3: Allow users to delete their own files
CREATE POLICY "Allow users to delete own files in student-documents"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'student-documents' AND  
    (auth.uid()::text = (string_to_array(name, '/'))[1])
);

-- ===============================
-- SECTION 4: Fix student_profiles RLS
-- ===============================

-- Enable RLS on student_profiles
ALTER TABLE public.student_profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
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
-- SECTION 5: Grant Permissions
-- ===============================

-- Grant necessary permissions
GRANT ALL ON storage.buckets TO authenticated;
GRANT ALL ON storage.objects TO authenticated;
GRANT ALL ON public.student_profiles TO authenticated;

-- ===============================
-- SECTION 6: Verification Queries
-- ===============================

-- Verify bucket exists
SELECT id, name, public, file_size_limit 
FROM storage.buckets 
WHERE id = 'student-documents';

-- Verify storage policies exist
SELECT policyname, cmd, roles 
FROM pg_policies 
WHERE tablename = 'objects' AND schemaname = 'storage';

-- Verify student_profiles policies exist  
SELECT policyname, cmd, roles
FROM pg_policies
WHERE tablename = 'student_profiles' AND schemaname = 'public';
