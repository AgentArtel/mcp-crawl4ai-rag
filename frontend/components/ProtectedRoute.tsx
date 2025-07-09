'use client'

import { useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from './LoadingSpinner'

interface ProtectedRouteProps {
  children: ReactNode
  requireOnboarding?: boolean
}

export default function ProtectedRoute({ children, requireOnboarding = false }: ProtectedRouteProps) {
  const { user, loading, hasCompletedOnboarding } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading) {
      if (!user) {
        // Redirect to auth page if not authenticated
        router.push('/auth')
      } else if (requireOnboarding && !hasCompletedOnboarding) {
        // Redirect to onboarding if required but not completed
        router.push('/onboarding')
      }
    }
  }, [user, loading, hasCompletedOnboarding, requireOnboarding, router])

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  // Don't render children if not authenticated
  if (!user) {
    return null
  }

  // Don't render children if onboarding is required but not completed
  if (requireOnboarding && !hasCompletedOnboarding) {
    return null
  }

  return <>{children}</>
}
