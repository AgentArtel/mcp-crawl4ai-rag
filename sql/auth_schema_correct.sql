-- Correct Authentication Schema for Supabase
-- Using auth_user_id column name that already exists

-- Update existing student_profiles table structure
-- First, let's add any missing columns to the existing table

-- Add missing columns if they don't exist
ALTER TABLE student_profiles 
ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
ADD COLUMN IF NOT EXISTS major VARCHAR(255),
ADD COLUMN IF NOT EXISTS classification VARCHAR(50),
ADD COLUMN IF NOT EXISTS gpa DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS expected_graduation DATE,
ADD COLUMN IF NOT EXISTS avatar_url TEXT,
ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- Add indexes for efficient lookups (using correct column name)
CREATE INDEX IF NOT EXISTS idx_student_profiles_auth_user_id ON student_profiles(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_student_profiles_student_id ON student_profiles(student_id);

-- Enable Row Level Security
ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own profile" ON student_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON student_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON student_profiles;
DROP POLICY IF EXISTS "Users can manage own profile" ON student_profiles;

-- Create RLS policies using the correct column name (auth_user_id)
CREATE POLICY "Users can view own profile" ON student_profiles
    FOR SELECT USING (auth.uid() = auth_user_id);

CREATE POLICY "Users can update own profile" ON student_profiles
    FOR UPDATE USING (auth.uid() = auth_user_id);

CREATE POLICY "Users can insert own profile" ON student_profiles
    FOR INSERT WITH CHECK (auth.uid() = auth_user_id);

-- Function for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS update_student_profiles_updated_at ON student_profiles;

-- Trigger for automatic timestamp updates
CREATE TRIGGER update_student_profiles_updated_at BEFORE UPDATE ON student_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically create student profile after user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.student_profiles (auth_user_id, student_name, student_id)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        NEW.raw_user_meta_data->>'student_id'
    );
    RETURN NEW;
EXCEPTION
    WHEN others THEN
        -- Log error but don't fail the user creation
        RAISE WARNING 'Failed to create student profile: %', SQLERRM;
        RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Trigger to automatically create profile when user signs up
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Grant necessary permissions
GRANT ALL ON student_profiles TO authenticated;
GRANT ALL ON student_profiles TO anon;
