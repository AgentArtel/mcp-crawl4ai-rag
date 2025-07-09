-- Custom Access Token Hook for Utah Tech IAP Advisor
-- This function adds onboarding-related claims to JWT tokens
-- Created in public schema to avoid permission issues

CREATE OR REPLACE FUNCTION public.custom_access_token_hook(event jsonb)
RETURNS jsonb
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
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
  
  -- Add student info if available
  IF student_profile_exists AND length(trim(student_id_value)) > 0 THEN
    claims := jsonb_set(claims, '{student_id}', 
      to_jsonb(student_id_value));
  END IF;
  
  IF student_profile_exists AND length(trim(full_name_value)) > 0 THEN
    claims := jsonb_set(claims, '{full_name}', 
      to_jsonb(full_name_value));
  END IF;
  
  IF student_profile_exists AND length(trim(email_value)) > 0 THEN
    claims := jsonb_set(claims, '{email}', 
      to_jsonb(email_value));
  END IF;
  
  -- Add user metadata for easier access
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
  
  -- Return the modified event with updated claims
  RETURN jsonb_set(event, '{claims}', claims);
END;
$$;

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION public.custom_access_token_hook(jsonb) TO supabase_auth_admin;
GRANT EXECUTE ON FUNCTION public.custom_access_token_hook(jsonb) TO postgres;
