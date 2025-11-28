-- Migration: Published Profiles
-- Description: Add published profile functionality with unique usernames and public visibility

-- Create published_profiles table
CREATE TABLE IF NOT EXISTS published_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    username TEXT UNIQUE NOT NULL,
    profile_data JSONB NOT NULL,
    is_published BOOLEAN DEFAULT true,
    view_count INTEGER DEFAULT 0,
    published_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT username_format CHECK (username ~ '^[a-z0-9-]+$'),
    CONSTRAINT username_length CHECK (char_length(username) >= 3 AND char_length(username) <= 50)
);

-- Create index for faster username lookups
CREATE INDEX IF NOT EXISTS idx_published_profiles_username ON published_profiles(username);
CREATE INDEX IF NOT EXISTS idx_published_profiles_user_id ON published_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_published_profiles_is_published ON published_profiles(is_published);

-- Add username column to profiles table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='profiles' AND column_name='username') THEN
        ALTER TABLE profiles ADD COLUMN username TEXT UNIQUE;
        ALTER TABLE profiles ADD CONSTRAINT username_format CHECK (username ~ '^[a-z0-9-]+$');
        ALTER TABLE profiles ADD CONSTRAINT username_length CHECK (char_length(username) >= 3 AND char_length(username) <= 50);
    END IF;
END $$;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_published_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updating updated_at
DROP TRIGGER IF EXISTS update_published_profiles_updated_at_trigger ON public.published_profiles;
CREATE TRIGGER update_published_profiles_updated_at_trigger
    BEFORE UPDATE ON public.published_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_published_profiles_updated_at();

-- Enable Row Level Security
ALTER TABLE published_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can read published profiles
CREATE POLICY "Public profiles are viewable by everyone"
    ON published_profiles FOR SELECT
    USING (is_published = true);

-- Policy: Users can insert their own published profile
CREATE POLICY "Users can publish their own profile"
    ON published_profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own published profile
CREATE POLICY "Users can update their own published profile"
    ON published_profiles FOR UPDATE
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own published profile
CREATE POLICY "Users can delete their own published profile"
    ON published_profiles FOR DELETE
    USING (auth.uid() = user_id);

-- Create view for public profile display (without sensitive data)
CREATE OR REPLACE VIEW public_profiles AS
SELECT 
    pp.username,
    pp.profile_data,
    pp.view_count,
    pp.published_at,
    pp.updated_at,
    p.full_name,
    p.github_username,
    p.github_avatar_url
FROM published_profiles pp
JOIN profiles p ON pp.user_id = p.id
WHERE pp.is_published = true;

-- Grant access to public_profiles view
GRANT SELECT ON public_profiles TO anon, authenticated;

COMMENT ON TABLE published_profiles IS 'Stores published profiles with unique usernames for public sharing';
COMMENT ON COLUMN published_profiles.username IS 'Unique username for the profile URL (lowercase, alphanumeric, hyphens only)';
COMMENT ON COLUMN published_profiles.profile_data IS 'JSON data containing projects and profile information';
COMMENT ON COLUMN published_profiles.view_count IS 'Number of times this profile has been viewed';

