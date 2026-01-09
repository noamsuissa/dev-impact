-- Migration: Update hobby plan portfolio limit to 1
-- Description: Change the portfolio limit for free/hobby plan users from 3 to 1

-- ============================================
-- 1. UPDATE PORTFOLIO LIMIT CHECK FUNCTION
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
        max_portfolios := 1; -- Free/hobby users limited to 1
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
-- 2. UPDATE PORTFOLIO LIMIT ENFORCEMENT TRIGGER FUNCTION
-- ============================================
CREATE OR REPLACE FUNCTION public.enforce_portfolio_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT public.check_portfolio_limit(NEW.user_id) THEN
        RAISE EXCEPTION 'Portfolio limit reached. Free users are limited to 1 portfolio. Upgrade to Pro for unlimited portfolios.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 3. UPDATE SUBSCRIPTION INFO FUNCTION
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
        max_portfolios := 1; -- Free/hobby users limited to 1
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
