-- Fix Missing Storage Bucket and RLS Policy Issues
-- Run this in your Supabase SQL Editor

-- 1. Create the missing 'student-documents' storage bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'student-documents',
  'student-documents',
  false, -- Private bucket
  10485760, -- 10MB limit
  ARRAY['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
);

-- 2. Create storage policy for authenticated users to upload their own files
CREATE POLICY "Users can upload their own documents" 
ON storage.objects 
FOR INSERT 
WITH CHECK (
  bucket_id = 'student-documents' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- 3. Create storage policy for authenticated users to view their own files
CREATE POLICY "Users can view their own documents" 
ON storage.objects 
FOR SELECT 
USING (
  bucket_id = 'student-documents' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- 4. Create storage policy for authenticated users to delete their own files
CREATE POLICY "Users can delete their own documents" 
ON storage.objects 
FOR DELETE 
USING (
  bucket_id = 'student-documents' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- 5. Fix RLS policy for student_profiles table - allow authenticated users to insert their own profile
DROP POLICY IF EXISTS "Users can insert their own profile" ON public.student_profiles;

CREATE POLICY "Users can insert their own profile" 
ON public.student_profiles 
FOR INSERT 
TO authenticated 
WITH CHECK (auth.uid() = user_id);

-- 6. Also allow users to view and update their own profile
DROP POLICY IF EXISTS "Users can view their own profile" ON public.student_profiles;
CREATE POLICY "Users can view their own profile" 
ON public.student_profiles 
FOR SELECT 
TO authenticated 
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own profile" ON public.student_profiles;
CREATE POLICY "Users can update their own profile" 
ON public.student_profiles 
FOR UPDATE 
TO authenticated 
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- 7. Enable RLS on student_profiles if not already enabled
ALTER TABLE public.student_profiles ENABLE ROW LEVEL SECURITY;

-- 8. Grant necessary permissions for storage bucket
GRANT ALL ON storage.buckets TO authenticated;
GRANT ALL ON storage.objects TO authenticated;
