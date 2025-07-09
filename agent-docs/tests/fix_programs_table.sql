-- Fix academic_programs table to allow long program names
-- Run this in Supabase SQL Editor

-- Remove the UNIQUE constraint on program_name that's causing the index size error
ALTER TABLE academic_programs DROP CONSTRAINT IF EXISTS academic_programs_program_name_key;

-- Add a partial index instead for shorter names only (optional, for performance)
CREATE INDEX IF NOT EXISTS idx_academic_programs_name_partial 
ON academic_programs(program_name) 
WHERE length(program_name) < 500;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Fixed academic_programs table - removed UNIQUE constraint on program_name';
    RAISE NOTICE 'Ready for data population with long program names';
END $$;
