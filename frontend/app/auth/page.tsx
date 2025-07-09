'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../../contexts/AuthContext'
import { userNeedsOnboarding } from '../../lib/jwt-claims'
import LoginForm from '../../components/auth/LoginForm'
import RegisterForm from '../../components/auth/RegisterForm'
import ForgotPasswordForm from '../../components/auth/ForgotPasswordForm'

type AuthMode = 'login' | 'register' | 'forgot-password'

export default function AuthPage() {
  const [mode, setMode] = useState<AuthMode>('login')
  const { user, loading } = useAuth()
  const router = useRouter()

  // Redirect authenticated users
  useEffect(() => {
    if (!loading && user) {
      console.log('Auth page: User is authenticated, checking redirect...')
      console.log('User data:', { id: user.id, app_metadata: user.app_metadata })
      
      const needsOnboarding = userNeedsOnboarding(user)
      console.log('Needs onboarding:', needsOnboarding)
      
      if (needsOnboarding) {
        console.log('Redirecting to onboarding...')
        router.push('/onboarding')
      } else {
        console.log('Redirecting to dashboard...')
        router.push('/')
      }
    }
  }, [user, loading, router])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {mode === 'login' && (
          <LoginForm
            onSwitchToRegister={() => setMode('register')}
            onForgotPassword={() => setMode('forgot-password')}
          />
        )}
        
        {mode === 'register' && (
          <RegisterForm
            onSwitchToLogin={() => setMode('login')}
          />
        )}
        
        {mode === 'forgot-password' && (
          <ForgotPasswordForm
            onBackToLogin={() => setMode('login')}
          />
        )}
      </div>
    </div>
  )
}
