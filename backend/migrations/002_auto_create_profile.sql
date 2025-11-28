-- ============================================
-- Auto-Create Profile on User Signup
-- ============================================
-- This migration adds a trigger to automatically create a profile
-- entry when a new user signs up through Supabase Auth

-- ============================================
-- FUNCTION: Auto-create profile for new users
-- ============================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    generated_username TEXT;
    counter INTEGER := 0;
BEGIN
    -- Generate initial username from email (everything before @)
    generated_username := split_part(NEW.email, '@', 1);
    
    -- Replace any non-alphanumeric characters with hyphens
    generated_username := regexp_replace(generated_username, '[^a-z0-9-]', '-', 'gi');
    
    -- Convert to lowercase
    generated_username := lower(generated_username);
    
    -- Ensure it doesn't start or end with hyphen
    generated_username := trim(both '-' from generated_username);
    
    -- Ensure minimum length
    IF length(generated_username) < 3 THEN
        generated_username := 'user-' || substring(NEW.id::text, 1, 8);
    END IF;
    
    -- If username is taken or reserved, append numbers until we find available one
    WHILE NOT public.is_username_available(generated_username) LOOP
        counter := counter + 1;
        generated_username := split_part(NEW.email, '@', 1) || '-' || counter;
        generated_username := lower(regexp_replace(generated_username, '[^a-z0-9-]', '-', 'gi'));
        generated_username := trim(both '-' from generated_username);
        
        -- Failsafe: if we've tried 100 times, use UUID
        IF counter > 100 THEN
            generated_username := 'user-' || substring(NEW.id::text, 1, 8);
            EXIT;
        END IF;
    END LOOP;
    
    -- Create the profile
    INSERT INTO public.profiles (
        id,
        username,
        full_name,
        github_username,
        github_avatar_url,
        is_published
    )
    VALUES (
        NEW.id,
        generated_username,
        COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
        NEW.raw_user_meta_data->>'github_username',
        NEW.raw_user_meta_data->>'avatar_url',
        false
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- TRIGGER: Create profile on user signup
-- ============================================
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- GRANT PERMISSIONS
-- ============================================
-- Allow the trigger to insert into profiles
GRANT INSERT ON public.profiles TO supabase_auth_admin;

-- ============================================
-- NOTES
-- ============================================
-- This trigger will:
-- 1. Automatically create a profile when a user signs up
-- 2. Generate a username from their email (before @ symbol)
-- 3. Handle conflicts by appending numbers (user, user-1, user-2, etc.)
-- 4. Extract metadata from signup (full_name, github_username, avatar_url)
-- 5. Set is_published to false by default
--
-- To pass metadata during signup in your frontend:
--
-- const { data, error } = await supabase.auth.signUp({
--   email: 'user@example.com',
--   password: 'password',
--   options: {
--     data: {
--       full_name: 'John Doe',
--       github_username: 'johndoe',
--       avatar_url: 'https://github.com/johndoe.png'
--     }
--   }
-- })
-- ============================================

