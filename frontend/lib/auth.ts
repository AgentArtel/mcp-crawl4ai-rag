import { createBrowserClient } from '@supabase/ssr'
import { User } from '@supabase/supabase-js'
import { userNeedsOnboarding, getOnboardingStatus, getStudentProfileFromClaims, UserWithClaims } from './jwt-claims'

export interface AuthUser {
  id: string
  email: string
  name: string
  studentId?: string
  avatar?: string
  isNewUser?: boolean
}

export interface StudentProfile {
  id: string
  user_id: string
  student_id: string
  full_name: string
  email: string
  phone?: string
  major?: string
  classification?: string
  gpa?: number
  expected_graduation?: string
  avatar_url?: string
  preferences?: any
  created_at: string
  updated_at: string
}

class AuthService {
  public supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )

  // Sign up new user
  async signUp(email: string, password: string, fullName: string, studentId?: string) {
    try {
      console.log('AuthService: Starting signUp process...', { email, fullName })
      
      const { data, error } = await this.supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
            student_id: studentId,
          }
        }
      })

      console.log('AuthService: Supabase auth.signUp result:', { 
        user: !!data.user, 
        userId: data.user?.id,
        userEmail: data.user?.email,
        userConfirmedAt: data.user?.email_confirmed_at,
        session: !!data.session,
        sessionAccessToken: data.session?.access_token ? 'present' : 'missing',
        error: error?.message,
        fullData: data,
        fullError: error
      })

      if (error) {
        console.error('AuthService: Supabase auth error:', error)
        throw error
      }

      // Check if email confirmation is required
      if (data.user && !data.session) {
        console.warn('AuthService: User created but no session - email confirmation may be required')
        console.log('AuthService: User email_confirmed_at:', data.user.email_confirmed_at)
        console.log('AuthService: User confirmation_sent_at:', data.user.confirmation_sent_at)
      }

      // Create student profile if signup successful
      if (data.user) {
        console.log('AuthService: Creating student profile...')
        const profileResult = await this.createStudentProfile(data.user, fullName, studentId)
        console.log('AuthService: Student profile creation result:', profileResult)
        
        if (!profileResult.success) {
          console.error('AuthService: Profile creation failed, cleaning up user account')
          // Profile creation failed, return error
          return { user: null, error: `Registration failed: ${profileResult.error}` }
        }
        
        // Check session state after profile creation
        console.log('AuthService: Checking session state after profile creation...')
        const { data: sessionData } = await this.supabase.auth.getSession()
        console.log('AuthService: Current session after profile creation:', {
          hasSession: !!sessionData.session,
          sessionUserId: sessionData.session?.user?.id,
          sessionAccessToken: sessionData.session?.access_token ? 'present' : 'missing'
        })
      } else {
        console.warn('AuthService: No user returned from signUp')
        return { user: null, error: 'Registration failed: No user account created' }
      }

      return { user: data.user, error: null }
    } catch (error: any) {
      console.error('AuthService: SignUp exception:', error)
      return { user: null, error: error.message }
    }
  }

  // Sign in existing user
  async signIn(email: string, password: string) {
    try {
      const { data, error } = await this.supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) throw error

      return { user: data.user, error: null }
    } catch (error: any) {
      return { user: null, error: error.message }
    }
  }

  // Sign out user
  async signOut() {
    try {
      const { error } = await this.supabase.auth.signOut()
      if (error) throw error
      return { error: null }
    } catch (error: any) {
      return { error: error.message }
    }
  }

  // Get current user
  async getCurrentUser(): Promise<User | null> {
    try {
      const { data: { user } } = await this.supabase.auth.getUser()
      return user
    } catch (error) {
      console.error('Error getting current user:', error)
      return null
    }
  }

  // Get user session
  async getSession() {
    try {
      const { data: { session } } = await this.supabase.auth.getSession()
      return session
    } catch (error) {
      console.error('Error getting session:', error)
      return null
    }
  }

  // Create student profile
  private async createStudentProfile(user: User, fullName: string, studentId?: string) {
    try {
      console.log('AuthService: Attempting to create student profile...', {
        userId: user.id,
        email: user.email,
        fullName,
        studentId
      })

      const profileData = {
        user_id: user.id,
        student_id: studentId || `UT${Date.now()}`,
        student_name: fullName,
        student_email: user.email!,
        preferences: {
          theme: 'light',
          notifications: true,
          onboarding_completed: false
        }
      }

      console.log('AuthService: Profile data to insert:', profileData)

      const { data, error } = await this.supabase
        .from('student_profiles')
        .insert(profileData)
        .select()

      if (error) {
        console.error('AuthService: Error creating student profile:', error)
        return { success: false, error: error.message }
      }

      console.log('AuthService: Student profile created successfully:', data)
      return { success: true, data }
    } catch (error: any) {
      console.error('AuthService: Exception creating student profile:', error)
      return { success: false, error: error.message }
    }
  }

  // Get student profile
  async getStudentProfile(userId: string): Promise<StudentProfile | null> {
    try {
      const { data, error } = await this.supabase
        .from('student_profiles')
        .select('*')
        .eq('user_id', userId)
        .single()

      if (error) {
        console.error('Error fetching student profile:', error)
        return null
      }

      return data
    } catch (error) {
      console.error('Error fetching student profile:', error)
      return null
    }
  }

  // Update student profile
  async updateStudentProfile(userId: string, updates: Partial<StudentProfile>) {
    try {
      const { data, error } = await this.supabase
        .from('student_profiles')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)
        .select()
        .single()

      if (error) throw error
      return { data, error: null }
    } catch (error: any) {
      return { data: null, error: error.message }
    }
  }

  // Check if user has completed onboarding
  async hasCompletedOnboarding(userId: string): Promise<boolean> {
    try {
      const profile = await this.getStudentProfile(userId)
      return profile?.preferences?.onboarding_completed || false
    } catch (error) {
      console.error('Error checking onboarding status:', error)
      return false
    }
  }

  // Mark onboarding as completed
  async completeOnboarding(userId: string) {
    try {
      const profile = await this.getStudentProfile(userId)
      if (profile) {
        await this.updateStudentProfile(userId, {
          preferences: {
            ...profile.preferences,
            onboarding_completed: true
          }
        })
      }
    } catch (error) {
      console.error('Error completing onboarding:', error)
    }
  }

  // Listen to auth state changes
  onAuthStateChange(callback: (user: User | null) => void) {
    return this.supabase.auth.onAuthStateChange((event, session) => {
      callback(session?.user || null)
    })
  }

  // Reset password
  async resetPassword(email: string) {
    try {
      const { error } = await this.supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`
      })

      if (error) throw error
      return { error: null }
    } catch (error: any) {
      return { error: error.message }
    }
  }

  // Update password
  async updatePassword(newPassword: string) {
    try {
      const { error } = await this.supabase.auth.updateUser({
        password: newPassword
      })

      if (error) throw error
      return { error: null }
    } catch (error: any) {
      return { error: error.message }
    }
  }
}

export const authService = new AuthService()
export default authService
