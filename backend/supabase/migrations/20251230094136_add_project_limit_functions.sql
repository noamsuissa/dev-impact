-- Migration: Add project limit checking functions
-- Description: Add functions to check and enforce project limits based on subscription type

-- ============================================
-- 1. CREATE PROJECT LIMIT CHECK FUNCTION
-- ============================================
CREATE OR REPLACE FUNCTION public.check_project_limit(user_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    user_subscription TEXT;
    project_count INTEGER;
    max_projects INTEGER;
BEGIN
    -- Get user's subscription type
    SELECT subscription_type INTO user_subscription
    FROM profiles
    WHERE id = user_uuid;
    
    -- Default to 'free' if not set
    IF user_subscription IS NULL THEN
        user_subscription := 'free';
    END IF;
    
    -- Set max projects based on subscription
    IF user_subscription = 'pro' THEN
        max_projects := 1000; -- Unlimited for pro
    ELSE
        max_projects := 10; -- Free/hobby users limited to 10
    END IF;
    
    -- Count existing projects
    SELECT COUNT(*) INTO project_count
    FROM impact_projects
    WHERE user_id = user_uuid;
    
    -- Return true if under limit
    RETURN project_count < max_projects;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 2. CREATE PROJECT LIMIT ENFORCEMENT TRIGGER FUNCTION
-- ============================================
CREATE OR REPLACE FUNCTION public.enforce_project_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT public.check_project_limit(NEW.user_id) THEN
        RAISE EXCEPTION 'Project limit reached. Free users are limited to 10 projects. Upgrade to Pro for unlimited projects.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger
CREATE TRIGGER check_project_limit_trigger
    BEFORE INSERT ON impact_projects
    FOR EACH ROW
    EXECUTE FUNCTION public.enforce_project_limit();

-- ============================================
-- 3. UPDATE SUBSCRIPTION INFO FUNCTION TO INCLUDE PROJECT INFO
-- ============================================
CREATE OR REPLACE FUNCTION public.get_user_subscription_info(user_uuid UUID)
RETURNS JSON AS $$
DECLARE
    user_subscription TEXT;
    portfolio_count INTEGER;
    max_portfolios INTEGER;
    project_count INTEGER;
    max_projects INTEGER;
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
    
    -- Set max projects based on subscription
    IF user_subscription = 'pro' THEN
        max_projects := 1000; -- Unlimited for pro
    ELSE
        max_projects := 10; -- Free/hobby users limited to 10
    END IF;
    
    -- Count existing portfolios
    SELECT COUNT(*) INTO portfolio_count
    FROM portfolios
    WHERE user_id = user_uuid;
    
    -- Count existing projects
    SELECT COUNT(*) INTO project_count
    FROM impact_projects
    WHERE user_id = user_uuid;
    
    -- Build result JSON with portfolio and project info
    result := json_build_object(
        'subscription_type', user_subscription,
        'portfolio_count', portfolio_count,
        'max_portfolios', max_portfolios,
        'can_add_portfolio', portfolio_count < max_portfolios,
        'project_count', project_count,
        'max_projects', max_projects,
        'can_add_project', project_count < max_projects
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 4. UPDATE COMMENTS
-- ============================================
COMMENT ON FUNCTION public.check_project_limit(UUID) IS 'Checks if user can add more projects based on subscription';
COMMENT ON FUNCTION public.enforce_project_limit() IS 'Trigger function to enforce project limits on insert';

