'use client'

import { useState } from 'react'
import { Eye, EyeOff, Mail, Lock, User, CreditCard, UserPlus, AlertCircle, CheckCircle } from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { supabase } from '../../lib/supabase'
import { useToast } from '../../hooks/useToast'
import { ToastContainer } from '../ui/Toast'

interface RegisterFormProps {
  onSwitchToLogin: () => void
}

export default function RegisterForm({ onSwitchToLogin }: RegisterFormProps) {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    studentId: '',
    password: '',
    confirmPassword: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState(0)
  
  const { signUp } = useAuth()
  const { success, error: showError, info, warning, toasts, removeToast } = useToast()

  const validatePassword = (password: string) => {
    let strength = 0
    if (password.length >= 8) strength++
    if (/[A-Z]/.test(password)) strength++
    if (/[a-z]/.test(password)) strength++
    if (/[0-9]/.test(password)) strength++
    if (/[^A-Za-z0-9]/.test(password)) strength++
    return strength
  }

  const handleInputChange = (field: string, value: string) => {
    console.log('=== INPUT CHANGE ===' , { field, value, length: value.length })
    setFormData(prev => {
      const newData = { ...prev, [field]: value }
      console.log('Updated form data:', newData)
      return newData
    })
    
    if (field === 'password') {
      setPasswordStrength(validatePassword(value))
    }
    
    // Clear error when user starts typing
    if (error) setError('')
  }

  const validateForm = () => {
    if (!formData.fullName.trim()) {
      setError('Full name is required')
      return false
    }
    
    if (!formData.email.trim()) {
      setError('Email is required')
      return false
    }
    
    if (!formData.email.includes('@')) {
      setError('Please enter a valid email address')
      return false
    }
    
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long')
      return false
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return false
    }
    
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    console.log('=== FORM SUBMISSION TRIGGERED ===')
    e.preventDefault()
    setError('')
    
    console.log('Form data:', formData)
    console.log('Validating form...')
    const isValid = validateForm()
    console.log('Form validation result:', isValid)
    
    if (!isValid) {
      console.log('Form validation failed, stopping submission')
      return
    }
    
    setIsLoading(true)

    try {
      console.log('Starting registration process...', { email: formData.email, fullName: formData.fullName })
      
      const { user, error } = await signUp(
        formData.email,
        formData.password,
        formData.fullName,
        formData.studentId || undefined
      )
      
      console.log('Registration result:', { user: !!user, error, userId: user?.id })
      console.log('Full user object:', user)
      console.log('Full error object:', error)
      
      if (error) {
        console.error('Registration error:', error)
        setError(error)
        showError(
          'Registration Failed',
          error.includes('already registered') 
            ? 'An account with this email already exists. Please try signing in instead.'
            : error
        )
      } else if (user) {
        console.log('Registration successful!')
        
        // Show success message
        const successId = success(
          'Account Created Successfully!',
          'Please check your email and click the confirmation link to activate your account.'
        )
        
        const infoId = info(
          'Email Confirmation Required',
          `We've sent a confirmation email to ${formData.email}. Please check your inbox and click the confirmation link to complete your registration. You'll be automatically redirected to complete your profile setup after confirmation.`,
          12000
        )
        
        // Clear form on success
        setFormData({
          fullName: '',
          email: '',
          studentId: '',
          password: '',
          confirmPassword: ''
        })
        setPasswordStrength(0)
        
        // Set up auth state listener for email confirmation
        const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
          console.log('Auth state change:', event, !!session)
          
          if (event === 'SIGNED_IN' && session) {
            console.log('User confirmed email and signed in, redirecting to onboarding')
            
            // Show confirmation success
            success(
              'Email Confirmed!',
              'Your email has been confirmed. Redirecting to complete your profile setup.'
            )
            
            // Redirect to onboarding
            setTimeout(() => {
              window.location.href = '/onboarding'
            }, 2000)
            
            // Clean up subscription
            subscription.unsubscribe()
          }
        })
        
        // Clean up subscription after 10 minutes if no confirmation
        setTimeout(() => {
          subscription.unsubscribe()
        }, 600000) // 10 minutes
      } else {
        console.warn('Registration completed but no user or error returned')
        showError('Registration Issue', 'Registration completed but no confirmation received. Please try signing in.')
      }
    } catch (err: any) {
      console.error('Registration exception:', err)
      const errorMessage = err.message || 'An unexpected error occurred'
      setError(errorMessage)
      showError('Registration Error', errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const getPasswordStrengthColor = () => {
    if (passwordStrength <= 2) return 'bg-red-500'
    if (passwordStrength <= 3) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getPasswordStrengthText = () => {
    if (passwordStrength <= 2) return 'Weak'
    if (passwordStrength <= 3) return 'Medium'
    return 'Strong'
  }

  return (
    <>
      <ToastContainer toasts={toasts} onClose={removeToast} />
      <div className="w-full max-w-md mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <UserPlus className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Create Account</h2>
          <p className="text-gray-600 mt-2">Join Utah Tech IAP Advisor</p>
          
          {/* Test Toast Button - Remove after debugging */}
          <button 
            type="button"
            onClick={() => {
              console.log('Test toast button clicked')
              success('Test Toast', 'This is a test toast message')
            }}
            className="mt-2 px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600"
          >
            Test Toast
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-2">
              Full Name *
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                id="fullName"
                type="text"
                value={formData.fullName}
                onChange={(e) => handleInputChange('fullName', e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Enter your full name"
                required
                disabled={isLoading}
              />
            </div>
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email Address *
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="your.email@utahtech.edu"
                required
                disabled={isLoading}
              />
            </div>
          </div>

          <div>
            <label htmlFor="studentId" className="block text-sm font-medium text-gray-700 mb-2">
              Student ID (Optional)
            </label>
            <div className="relative">
              <CreditCard className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                id="studentId"
                type="text"
                value={formData.studentId}
                onChange={(e) => handleInputChange('studentId', e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="UT123456"
                disabled={isLoading}
              />
            </div>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password *
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Create a strong password"
                required
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                disabled={isLoading}
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            
            {formData.password && (
              <div className="mt-2">
                <div className="flex items-center gap-2 mb-1">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all ${getPasswordStrengthColor()}`}
                      style={{ width: `${(passwordStrength / 5) * 100}%` }}
                    ></div>
                  </div>
                  <span className={`text-xs font-medium ${
                    passwordStrength <= 2 ? 'text-red-600' : 
                    passwordStrength <= 3 ? 'text-yellow-600' : 'text-green-600'
                  }`}>
                    {getPasswordStrengthText()}
                  </span>
                </div>
                <p className="text-xs text-gray-500">
                  Use 8+ characters with uppercase, lowercase, numbers, and symbols
                </p>
              </div>
            )}
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
              Confirm Password *
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                id="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Confirm your password"
                required
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                disabled={isLoading}
              >
                {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            
            {formData.confirmPassword && (
              <div className="mt-1 flex items-center gap-1">
                {formData.password === formData.confirmPassword ? (
                  <>
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-xs text-green-600">Passwords match</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-4 h-4 text-red-600" />
                    <span className="text-xs text-red-600">Passwords don't match</span>
                  </>
                )}
              </div>
            )}
          </div>

          <div className="flex items-start gap-2">
            <input
              type="checkbox"
              id="terms"
              className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500 mt-1"
              required
              disabled={isLoading}
            />
            <label htmlFor="terms" className="text-sm text-gray-600">
              I agree to the{' '}
              <a href="#" className="text-green-600 hover:text-green-800">Terms of Service</a>
              {' '}and{' '}
              <a href="#" className="text-green-600 hover:text-green-800">Privacy Policy</a>
            </label>
          </div>

          {/* DEBUG: Form State */}
          <div className="text-xs text-gray-500 p-2 bg-gray-100 rounded mb-2">
            <div>Form Debug:</div>
            <div>Full Name: {formData.fullName ? '✓' : '✗'} ({formData.fullName.length} chars)</div>
            <div>Email: {formData.email ? '✓' : '✗'} ({formData.email.length} chars)</div>
            <div>Student ID: {formData.studentId ? '✓' : '✗'} ({formData.studentId.length} chars)</div>
            <div>Password: {formData.password ? '✓' : '✗'} ({formData.password.length} chars)</div>
            <div>Confirm Password: {formData.confirmPassword ? '✓' : '✗'} ({formData.confirmPassword.length} chars)</div>
            <div>Loading: {isLoading ? 'YES' : 'NO'}</div>
            <div>Button Disabled: {(isLoading || !formData.fullName || !formData.email || !formData.password || !formData.confirmPassword) ? 'YES' : 'NO'}</div>
          </div>

          <button
            type="submit"
            disabled={isLoading || !formData.fullName || !formData.email || !formData.password || !formData.confirmPassword}
            onClick={() => {
              console.log('=== SUBMIT BUTTON CLICKED ===')
              console.log('Button disabled?', isLoading || !formData.fullName || !formData.email || !formData.password || !formData.confirmPassword)
              console.log('Form data check:', {
                fullName: !!formData.fullName,
                email: !!formData.email,
                password: !!formData.password,
                confirmPassword: !!formData.confirmPassword,
                isLoading
              })
            }}
            className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <div className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Creating account...
              </div>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-gray-600">
            Already have an account?{' '}
            <button
              onClick={onSwitchToLogin}
              className="text-green-600 hover:text-green-800 font-medium"
              disabled={isLoading}
            >
              Sign in here
            </button>
          </p>
        </div>
        </div>
      </div>
    </>
  )
}
