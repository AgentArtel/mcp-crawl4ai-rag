'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User } from '@supabase/supabase-js'
import authService, { AuthUser, StudentProfile } from '../lib/auth'

interface AuthContextType {
  user: User | null
  profile: StudentProfile | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<{ user: User | null; error: string | null }>
  signUp: (email: string, password: string, fullName: string, studentId?: string) => Promise<{ user: User | null; error: string | null }>
  signOut: () => Promise<{ error: string | null }>
  updateProfile: (updates: Partial<StudentProfile>) => Promise<{ data: StudentProfile | null; error: string | null }>
  hasCompletedOnboarding: boolean
  completeOnboarding: () => Promise<void>
  resetPassword: (email: string) => Promise<{ error: string | null }>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<StudentProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(false)

  useEffect(() => {
    // Get initial session
    const getInitialSession = async () => {
      try {
        const session = await authService.getSession()
        if (session?.user) {
          setUser(session.user)
          await loadUserProfile(session.user.id)
        }
      } catch (error) {
        console.error('Error getting initial session:', error)
      } finally {
        setLoading(false)
      }
    }

    getInitialSession()

    // Listen for auth changes
    const { data: { subscription } } = authService.onAuthStateChange(async (user) => {
      setUser(user)
      if (user) {
        await loadUserProfile(user.id)
      } else {
        setProfile(null)
        setHasCompletedOnboarding(false)
      }
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const loadUserProfile = async (userId: string) => {
    try {
      const userProfile = await authService.getStudentProfile(userId)
      setProfile(userProfile)
      
      if (userProfile) {
        const onboardingCompleted = await authService.hasCompletedOnboarding(userId)
        setHasCompletedOnboarding(onboardingCompleted)
      }
    } catch (error) {
      console.error('Error loading user profile:', error)
    }
  }

  const signIn = async (email: string, password: string) => {
    setLoading(true)
    try {
      const result = await authService.signIn(email, password)
      if (result.user) {
        console.log('AuthContext: Setting user state after successful sign-in')
        setUser(result.user)
        await loadUserProfile(result.user.id)
      }
      return result
    } finally {
      setLoading(false)
    }
  }

  const signUp = async (email: string, password: string, fullName: string, studentId?: string) => {
    setLoading(true)
    try {
      const result = await authService.signUp(email, password, fullName, studentId)
      if (result.user) {
        await loadUserProfile(result.user.id)
      }
      return result
    } finally {
      setLoading(false)
    }
  }

  const signOut = async () => {
    setLoading(true)
    try {
      const result = await authService.signOut()
      setUser(null)
      setProfile(null)
      setHasCompletedOnboarding(false)
      return result
    } finally {
      setLoading(false)
    }
  }

  const updateProfile = async (updates: Partial<StudentProfile>) => {
    if (!user) return { data: null, error: 'No user logged in' }
    
    try {
      const result = await authService.updateStudentProfile(user.id, updates)
      if (result.data) {
        setProfile(result.data)
      }
      return result
    } catch (error: any) {
      return { data: null, error: error.message }
    }
  }

  const completeOnboarding = async () => {
    if (!user) return
    
    try {
      await authService.completeOnboarding(user.id)
      setHasCompletedOnboarding(true)
    } catch (error) {
      console.error('Error completing onboarding:', error)
    }
  }

  const resetPassword = async (email: string) => {
    return await authService.resetPassword(email)
  }

  const value: AuthContextType = {
    user,
    profile,
    loading,
    signIn,
    signUp,
    signOut,
    updateProfile,
    hasCompletedOnboarding,
    completeOnboarding,
    resetPassword
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
