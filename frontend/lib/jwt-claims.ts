// JWT Claims utility for handling custom claims from Supabase Auth Hooks
import { User } from '@supabase/supabase-js'

export interface CustomClaims {
  needs_onboarding?: boolean
  profile_exists?: boolean
  profile_complete?: boolean
  student_id?: string
  full_name?: string
  profile_email?: string
  app_metadata?: {
    onboarding_status?: 'not_started' | 'incomplete' | 'complete'
    profile_created_at?: string
  }
}

export interface UserWithClaims extends User {
  app_metadata: Record<string, any>
  user_metadata: Record<string, any>
}

/**
 * Extract custom claims from user JWT token
 */
export function getCustomClaims(user: User | null): CustomClaims {
  if (!user) return {}

  // Access custom claims from the JWT token
  const claims: CustomClaims = {}

  // Extract claims from user object (these come from the Custom Access Token Hook)
  if (user.app_metadata) {
    claims.app_metadata = user.app_metadata as any
  }

  // Extract direct claims (if available in user metadata or app metadata)
  const metadata = { ...user.user_metadata, ...user.app_metadata }
  
  if (typeof metadata.needs_onboarding === 'boolean') {
    claims.needs_onboarding = metadata.needs_onboarding
  }
  
  if (typeof metadata.profile_exists === 'boolean') {
    claims.profile_exists = metadata.profile_exists
  }
  
  if (typeof metadata.profile_complete === 'boolean') {
    claims.profile_complete = metadata.profile_complete
  }
  
  if (typeof metadata.student_id === 'string') {
    claims.student_id = metadata.student_id
  }
  
  if (typeof metadata.full_name === 'string') {
    claims.full_name = metadata.full_name
  }
  
  if (typeof metadata.profile_email === 'string') {
    claims.profile_email = metadata.profile_email
  }

  return claims
}

/**
 * Check if user needs onboarding based on JWT claims
 */
export function userNeedsOnboarding(user: User | null): boolean {
  if (!user) return false
  
  const claims = getCustomClaims(user)
  
  // Check the needs_onboarding claim first
  if (typeof claims.needs_onboarding === 'boolean') {
    return claims.needs_onboarding
  }
  
  // Fallback: check onboarding status from app_metadata
  if (claims.app_metadata?.onboarding_status) {
    return claims.app_metadata.onboarding_status !== 'complete'
  }
  
  // Default fallback: if no profile exists, needs onboarding
  return !claims.profile_exists
}

/**
 * Get onboarding status from JWT claims
 */
export function getOnboardingStatus(user: User | null): 'not_started' | 'incomplete' | 'complete' | 'unknown' {
  if (!user) return 'unknown'
  
  const claims = getCustomClaims(user)
  
  if (claims.app_metadata?.onboarding_status) {
    return claims.app_metadata.onboarding_status
  }
  
  // Derive status from other claims
  if (!claims.profile_exists) {
    return 'not_started'
  }
  
  if (!claims.profile_complete) {
    return 'incomplete'
  }
  
  return 'complete'
}

/**
 * Get student profile information from JWT claims
 */
export function getStudentProfileFromClaims(user: User | null): {
  studentId?: string
  fullName?: string
  email?: string
} {
  if (!user) return {}
  
  const claims = getCustomClaims(user)
  
  return {
    studentId: claims.student_id,
    fullName: claims.full_name,
    email: claims.profile_email || user.email
  }
}
