-- Migration: Update subscription functions to use portfolio terminology
-- Description: Rename functions, triggers, and variables from "profile" to "portfolio"

-- ============================================
-- 1. DROP OLD TRIGGERS AND FUNCTIONS
-- ============================================

-- Drop old trigger
DROP TRIGGER IF EXISTS check_profile_limit_trigger ON portfolios;

-- Drop old functions
DROP FUNCTION IF EXISTS public.enforce_profile_limit();
DROP FUNCTION IF EXISTS public.check_profile_limit(UUID);
DROP FUNCTION IF EXISTS public.get_user_subscription_info(UUID);

-- ============================================
-- 2. CREATE NEW PORTFOLIO LIMIT CHECK FUNCTION
-- ============================================
CREATE OR REPLACE FUNCTION public.check_portfolio_limit(user_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    user_subscription TEXT;
    portfolio_count INTEGER;
    max_portfolios INTEGER;
BEGIN
    -- Get user's subscription type
    SELECT subscription_type INTO user_subscription
    FROM profiles
    WHERE id = user_uuid;
    
    -- Default to 'free' if not set
    IF user_subscription IS NULL THEN
        user_subscription := 'free';
    END IF;
    
    -- Set max portfolios based on subscription
    IF user_subscription = 'pro' THEN
        max_portfolios := 1000; -- Unlimited for pro
    ELSE
        max_portfolios := 3; -- Free users limited to 3
    END IF;
    
    -- Count existing portfolios
    SELECT COUNT(*) INTO portfolio_count
    FROM portfolios
    WHERE user_id = user_uuid;
    
    -- Return true if under limit
    RETURN portfolio_count < max_portfolios;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 3. CREATE NEW PORTFOLIO LIMIT ENFORCEMENT TRIGGER FUNCTION
-- ============================================
CREATE OR REPLACE FUNCTION public.enforce_portfolio_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT public.check_portfolio_limit(NEW.user_id) THEN
        RAISE EXCEPTION 'Portfolio limit reached. Free users are limited to 3 portfolios. Upgrade to Pro for unlimited portfolios.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create new trigger
CREATE TRIGGER check_portfolio_limit_trigger
    BEFORE INSERT ON portfolios
    FOR EACH ROW
    EXECUTE FUNCTION public.enforce_portfolio_limit();

-- ============================================
-- 4. CREATE NEW SUBSCRIPTION INFO FUNCTION
-- ============================================
CREATE OR REPLACE FUNCTION public.get_user_subscription_info(user_uuid UUID)
RETURNS JSON AS $$
DECLARE
    user_subscription TEXT;
    portfolio_count INTEGER;
    max_portfolios INTEGER;
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
    
    -- Set max portfolios based on subscription
    IF user_subscription = 'pro' THEN
        max_portfolios := 1000; -- Unlimited for pro
    ELSE
        max_portfolios := 3; -- Free users limited to 3
    END IF;
    
    -- Count existing portfolios
    SELECT COUNT(*) INTO portfolio_count
    FROM portfolios
    WHERE user_id = user_uuid;
    
    -- Build result JSON with new field names
    result := json_build_object(
        'subscription_type', user_subscription,
        'portfolio_count', portfolio_count,
        'max_portfolios', max_portfolios,
        'can_add_portfolio', portfolio_count < max_portfolios
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 5. UPDATE COMMENTS
-- ============================================
COMMENT ON FUNCTION public.check_portfolio_limit(UUID) IS 'Checks if user can add more portfolios based on subscription';
COMMENT ON FUNCTION public.enforce_portfolio_limit() IS 'Trigger function to enforce portfolio limits on insert';
COMMENT ON FUNCTION public.get_user_subscription_info(UUID) IS 'Returns user subscription info including portfolio counts and limits';

