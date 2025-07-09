'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { authService, AuthUser } from '../../lib/auth'
import { User as SupabaseUser } from '@supabase/supabase-js'

interface User {
  id: string
  name: string
  email: string
  studentId?: string
  role: 'student' | 'advisor' | 'admin'
  avatar?: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  signIn: (email: string, password: string) => Promise<{ user: SupabaseUser | null; error: string | null }>
  signUp: (email: string, password: string, fullName: string, studentId?: string) => Promise<{ user: SupabaseUser | null; error: string | null }>
  signOut: () => Promise<void>
  updateUser: (updates: Partial<User>) => void
  // Legacy support
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const currentUser = await authService.getCurrentUser()
        if (currentUser) {
          const profile = await authService.getStudentProfile(currentUser.id)
          setUser({
            id: currentUser.id,
            name: profile?.full_name || currentUser.user_metadata?.full_name || 'Student',
            email: currentUser.email || '',
            studentId: profile?.student_id || currentUser.user_metadata?.student_id,
            role: 'student',
            avatar: profile?.avatar_url
          })
        }
      } catch (error) {
        console.error('Error checking auth:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    checkAuth()

    // Listen for auth changes
    const { data: { subscription } } = authService.supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (event === 'SIGNED_IN' && session?.user) {
          const profile = await authService.getStudentProfile(session.user.id)
          setUser({
            id: session.user.id,
            name: profile?.full_name || session.user.user_metadata?.full_name || 'Student',
            email: session.user.email || '',
            studentId: profile?.student_id || session.user.user_metadata?.student_id,
            role: 'student',
            avatar: profile?.avatar_url
          })
        } else if (event === 'SIGNED_OUT') {
          setUser(null)
        }
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  // New Supabase authentication methods
  const signIn = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const result = await authService.signIn(email, password)
      return result
    } catch (error: any) {
      return { user: null, error: error.message }
    } finally {
      setIsLoading(false)
    }
  }

  const signUp = async (email: string, password: string, fullName: string, studentId?: string) => {
    setIsLoading(true)
    try {
      const result = await authService.signUp(email, password, fullName, studentId)
      return result
    } catch (error: any) {
      return { user: null, error: error.message }
    } finally {
      setIsLoading(false)
    }
  }

  const signOut = async () => {
    setIsLoading(true)
    try {
      await authService.signOut()
      setUser(null)
    } catch (error) {
      console.error('Error signing out:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Legacy login method for backward compatibility
  const login = async (email: string, password: string): Promise<boolean> => {
    const result = await signIn(email, password)
    return !!result.user && !result.error
  }

  const logout = async () => {
    await signOut()
  }

  const updateUser = (updates: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...updates }
      setUser(updatedUser)
      // Note: In production, this should update the Supabase profile
      // For now, we'll just update local state
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    signIn,
    signUp,
    signOut,
    updateUser,
    // Legacy support
    login,
    logout
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

// Export for external use
export type { User, AuthContextType }
