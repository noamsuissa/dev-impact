-- Migration: Add Subscription Status tracking
-- Description: Add columns for detailed subscription tracking

-- ============================================
-- ADD SUBSCRIPTION STATUS COLUMNS TO PROFILES
-- ============================================
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS subscription_status TEXT,
ADD COLUMN IF NOT EXISTS cancel_at_period_end BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS current_period_end TIMESTAMP WITH TIME ZONE;

-- Create index for status queries
CREATE INDEX IF NOT EXISTS idx_profiles_subscription_status ON profiles(subscription_status);

-- Add comments
COMMENT ON COLUMN profiles.subscription_status IS 'Stripe subscription status (active, incomplete, past_due, canceled, etc.)';
COMMENT ON COLUMN profiles.cancel_at_period_end IS 'Whether the subscription will be canceled at the end of the current period';
COMMENT ON COLUMN profiles.current_period_end IS 'End of the current billing period';
