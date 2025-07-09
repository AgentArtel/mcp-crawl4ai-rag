-- Custom Access Token Hook for Utah Tech IAP Advisor
-- This function adds onboarding-related claims to JWT tokens
-- to enable seamless registration-to-onboarding flow

CREATE OR REPLACE FUNCTION auth.custom_access_token_hook(event jsonb)
RETURNS jsonb
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
  claims jsonb;
  user_id uuid;
  student_profile_exists boolean;
  profile_complete boolean;
  student_id_value text;
  full_name_value text;
  email_value text;
BEGIN
  -- Extract the claims and user_id from the event
  claims := event->'claims';
  user_id := (event->>'user_id')::uuid;
  
  -- Check if student profile exists and is complete
  SELECT 
    EXISTS(SELECT 1 FROM public.student_profiles WHERE id = user_id),
    COALESCE(
      (SELECT 
        student_id IS NOT NULL 
        AND full_name IS NOT NULL 
        AND length(trim(student_id)) > 0 
        AND length(trim(full_name)) > 0
       FROM public.student_profiles 
       WHERE id = user_id), 
      false
    ),
    COALESCE((SELECT student_id FROM public.student_profiles WHERE id = user_id), ''),
    COALESCE((SELECT full_name FROM public.student_profiles WHERE id = user_id), ''),
    COALESCE((SELECT email FROM public.student_profiles WHERE id = user_id), '')
  INTO student_profile_exists, profile_complete, student_id_value, full_name_value, email_value;
  
  -- Add custom claims to the token
  claims := jsonb_set(claims, '{needs_onboarding}', 
    to_jsonb(NOT student_profile_exists OR NOT profile_complete));
  
  claims := jsonb_set(claims, '{profile_exists}', 
    to_jsonb(student_profile_exists));
    
  claims := jsonb_set(claims, '{profile_complete}', 
    to_jsonb(profile_complete));
  
  -- Add student information if available
  IF student_profile_exists THEN
    claims := jsonb_set(claims, '{student_id}', 
      to_jsonb(student_id_value));
    claims := jsonb_set(claims, '{full_name}', 
      to_jsonb(full_name_value));
    claims := jsonb_set(claims, '{profile_email}', 
      to_jsonb(email_value));
  END IF;
  
  -- Add user metadata for easier access (avoiding app_metadata conflicts)
  claims := jsonb_set(claims, '{user_metadata}', 
    COALESCE(claims->'user_metadata', '{}'::jsonb) || jsonb_build_object(
      'onboarding_status', 
      CASE 
        WHEN NOT student_profile_exists THEN 'not_started'
        WHEN NOT profile_complete THEN 'incomplete'
        ELSE 'complete'
      END,
      'profile_created_at', 
      COALESCE(
        (SELECT created_at FROM public.student_profiles WHERE id = user_id)::text, 
        null
      )
    )
  );

  -- Return the event with updated claims
  RETURN jsonb_set(event, '{claims}', claims);
END;
$$;

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION auth.custom_access_token_hook TO supabase_auth_admin;
GRANT EXECUTE ON FUNCTION auth.custom_access_token_hook TO postgres;

-- Add comment for documentation
COMMENT ON FUNCTION auth.custom_access_token_hook IS 
'Custom Access Token Hook that adds onboarding-related claims to JWT tokens. 
Checks student_profiles table to determine if user needs onboarding and adds 
relevant claims like needs_onboarding, profile_complete, student_id, etc.';
