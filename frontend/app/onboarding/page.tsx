'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { OnboardingWizard } from '../../components/onboarding/OnboardingWizard'
import { toast } from 'react-hot-toast'
import { userNeedsOnboarding, getOnboardingStatus } from '../../lib/jwt-claims'
import authService from '../../lib/auth'

export default function OnboardingPage() {
  const router = useRouter()
  const { user, loading } = useAuth()

  useEffect(() => {
    const checkUserAndOnboarding = async () => {
      try {
        console.log('Onboarding: Checking user authentication and onboarding status')
        
        // Check if user is authenticated via AuthContext
        if (!loading && !user) {
          console.log('No authenticated user found, redirecting to auth')
          router.push('/auth')
          return
        }
        
        if (!user) {
          // Still loading, wait
          return
        }
        
        console.log('User found:', user.id)
        console.log('JWT claims:', user.app_metadata)
        
        // Check JWT claims for onboarding status
        const needsOnboarding = userNeedsOnboarding(user)
        
        console.log('Onboarding status from JWT claims:', {
          needsOnboarding,
          claims: {
            needs_onboarding: user.app_metadata?.needs_onboarding,
            profile_exists: user.app_metadata?.profile_exists,
            profile_complete: user.app_metadata?.profile_complete
          }
        })
        
        // If user doesn't need onboarding, redirect to dashboard
        if (!needsOnboarding) {
          console.log('User does not need onboarding, redirecting to dashboard')
          router.push('/')
          return
        }
        
        // User needs onboarding, show the wizard
        console.log('User needs onboarding, showing wizard')
        // User state is managed by AuthContext, no need to set it here
        
      } catch (error) {
        console.error('Error checking user and onboarding status:', error)
        toast.error('Authentication error. Please try again.')
        router.push('/auth')
      }
    }

    checkUserAndOnboarding()
  }, [])

  const handleOnboardingComplete = async () => {
    console.log('Onboarding completed, forcing session refresh to update JWT claims')
    
    try {
      // Force session refresh to get updated JWT claims
      const { data, error } = await authService.supabase.auth.refreshSession()
      console.log('Session refresh after onboarding:', { session: data.session, error })
      
      if (error) {
        console.error('Session refresh error after onboarding:', error)
        toast.error('Session refresh failed. Please log in again.')
        router.push('/auth')
        return
      }
      
      if (data.session) {
        console.log('Updated JWT claims:', data.session.user.app_metadata)
        // Small delay to ensure session is fully updated
        setTimeout(() => {
          console.log('Redirecting to dashboard with updated session')
          router.push('/')
        }, 500)
      } else {
        console.error('No session after refresh')
        toast.error('Authentication error. Please log in again.')
        router.push('/auth')
      }
    } catch (error) {
      console.error('Error refreshing session after onboarding:', error)
      toast.error('Session update failed. Please log in again.')
      router.push('/auth')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Redirecting to sign in...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <OnboardingWizard user={user} onComplete={handleOnboardingComplete} />
    </div>
  )
}
