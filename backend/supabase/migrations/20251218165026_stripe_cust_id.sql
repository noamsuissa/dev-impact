-- Migration: Add Stripe Customer ID to Profiles
-- Description: Add stripe_customer_id column to profiles table for linking users to Stripe customers

-- ============================================
-- ADD STRIPE_CUSTOMER_ID TO PROFILES TABLE
-- ============================================
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT;

-- Create index for faster lookups by Stripe customer ID
CREATE INDEX IF NOT EXISTS idx_profiles_stripe_customer_id ON profiles(stripe_customer_id);

-- Add comment to document the column
COMMENT ON COLUMN profiles.stripe_customer_id IS 'Stripe customer ID for subscription management';
