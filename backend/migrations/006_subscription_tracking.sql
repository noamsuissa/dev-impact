-- Migration: Subscription Tracking
-- Description: Add subscription tracking to profiles table and enforce free user limits

-- ============================================
-- 1. ADD SUBSCRIPTION TYPE TO PROFILES
-- ============================================
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS subscription_type TEXT DEFAULT 'free' CHECK (subscription_type IN ('free', 'pro'));

-- Create index for subscription queries
CREATE INDEX IF NOT EXISTS idx_profiles_subscription_type ON profiles(subscription_type);

-- ============================================
-- 2. FUNCTION TO CHECK PROFILE LIMIT
-- ============================================
CREATE OR REPLACE FUNCTION public.check_profile_limit(user_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    user_subscription TEXT;
    profile_count INTEGER;
    max_profiles INTEGER;
BEGIN
    -- Get user's subscription type
    SELECT subscription_type INTO user_subscription
    FROM profiles
    WHERE id = user_uuid;
    
    -- Default to 'free' if not set
    IF user_subscription IS NULL THEN
        user_subscription := 'free';
    END IF;
    
    -- Set max profiles based on subscription
    IF user_subscription = 'pro' THEN
        max_profiles := 1000; -- Unlimited for pro
    ELSE
        max_profiles := 3; -- Free users limited to 3
    END IF;
    
    -- Count existing profiles
    SELECT COUNT(*) INTO profile_count
    FROM user_profiles
    WHERE user_id = user_uuid;
    
    -- Return true if under limit
    RETURN profile_count < max_profiles;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 3. TRIGGER TO ENFORCE PROFILE LIMIT
-- ============================================
CREATE OR REPLACE FUNCTION public.enforce_profile_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT public.check_profile_limit(NEW.user_id) THEN
        RAISE EXCEPTION 'Profile limit reached. Free users are limited to 3 profiles. Upgrade to Pro for unlimited profiles.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop trigger if exists
DROP TRIGGER IF EXISTS check_profile_limit_trigger ON user_profiles;

-- Create trigger before insert
CREATE TRIGGER check_profile_limit_trigger
    BEFORE INSERT ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.enforce_profile_limit();

-- ============================================
-- 4. FUNCTION TO GET USER SUBSCRIPTION INFO
-- ============================================
CREATE OR REPLACE FUNCTION public.get_user_subscription_info(user_uuid UUID)
RETURNS JSON AS $$
DECLARE
    user_subscription TEXT;
    profile_count INTEGER;
    max_profiles INTEGER;
    result JSON;
BEGIN
    -- Get user's subscription type
    SELECT subscription_type INTO user_subscription
    FROM profiles
    WHERE id = user_uuid;
    
    -- Default to 'free' if not set
    IF user_subscription IS NULL THEN
        user_subscription := 'free';
    END IF;
    
    -- Set max profiles based on subscription
    IF user_subscription = 'pro' THEN
        max_profiles := 1000; -- Unlimited for pro
    ELSE
        max_profiles := 3; -- Free users limited to 3
    END IF;
    
    -- Count existing profiles
    SELECT COUNT(*) INTO profile_count
    FROM user_profiles
    WHERE user_id = user_uuid;
    
    -- Build result JSON
    result := json_build_object(
        'subscription_type', user_subscription,
        'profile_count', profile_count,
        'max_profiles', max_profiles,
        'can_add_profile', profile_count < max_profiles
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

