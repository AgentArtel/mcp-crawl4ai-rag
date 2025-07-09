-- Simplified Custom Access Token Hook for Utah Tech IAP Advisor
-- This function adds basic onboarding claims to JWT tokens
-- Uses auth.users table which is guaranteed to exist

CREATE OR REPLACE FUNCTION public.custom_access_token_hook(event jsonb)
RETURNS jsonb
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
AS $$
DECLARE
  claims jsonb;
  user_id uuid;
  user_created_at timestamp with time zone;
  is_new_user boolean;
BEGIN
  -- Extract the claims and user_id from the event
  claims := event->'claims';
  user_id := (event->>'user_id')::uuid;
  
  -- Get user creation time from auth.users (guaranteed to exist)
  SELECT created_at INTO user_created_at
  FROM auth.users 
  WHERE id = user_id;
  
  -- Consider user "new" if created within last 5 minutes
  -- This is a simple heuristic for onboarding detection
  is_new_user := (user_created_at > NOW() - INTERVAL '5 minutes');
  
  -- Add custom claims to the token
  claims := jsonb_set(claims, '{needs_onboarding}', to_jsonb(is_new_user));
  claims := jsonb_set(claims, '{profile_exists}', to_jsonb(NOT is_new_user));
  claims := jsonb_set(claims, '{profile_complete}', to_jsonb(NOT is_new_user));
  claims := jsonb_set(claims, '{user_created_at}', to_jsonb(user_created_at));
  
  -- Return the modified event with updated claims
  RETURN jsonb_set(event, '{claims}', claims);
END;
$$;

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION public.custom_access_token_hook(jsonb) TO supabase_auth_admin;
GRANT EXECUTE ON FUNCTION public.custom_access_token_hook(jsonb) TO postgres;
GRANT EXECUTE ON FUNCTION public.custom_access_token_hook(jsonb) TO service_role;

-- Add comment for documentation
COMMENT ON FUNCTION public.custom_access_token_hook(jsonb) IS 
'Custom Access Token Hook that adds onboarding-related claims to JWT tokens. Uses simple time-based heuristic to determine if user needs onboarding.';
