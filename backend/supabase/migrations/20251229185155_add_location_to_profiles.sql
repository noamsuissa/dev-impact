-- Migration: Add Location Fields to Profiles
-- Description: Add optional city and country columns to profiles table for user location

-- Add city and country columns to profiles table
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS city TEXT,
ADD COLUMN IF NOT EXISTS country TEXT;

-- Add comment for documentation
COMMENT ON COLUMN profiles.city IS 'User city (optional)';
COMMENT ON COLUMN profiles.country IS 'User country (optional)';
