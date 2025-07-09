'use client'

import { GraduationCap, User, Menu } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'

export default function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const { user, signOut } = useAuth()

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-3 sm:py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title - Responsive */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            <div className="bg-utah-red p-1.5 sm:p-2 rounded-lg">
              <GraduationCap className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
            </div>
            <div className="min-w-0 flex-1">
              <h1 className="text-lg sm:text-2xl font-bold text-gray-900 truncate">
                Utah Tech IAP Advisor
              </h1>
              <p className="text-xs sm:text-sm text-gray-600 hidden sm:block">
                Individualized Academic Plan Assistant
              </p>
            </div>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                {user?.user_metadata?.full_name || 'Student Portal'}
              </p>
              <p className="text-xs text-gray-500">Bachelor of Individualized Studies</p>
            </div>
            <button 
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="bg-gray-100 hover:bg-gray-200 p-2 rounded-full transition-colors"
            >
              <User className="h-6 w-6 text-gray-600" />
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden bg-gray-100 hover:bg-gray-200 p-2 rounded-lg transition-colors"
          >
            <Menu className="h-5 w-5 text-gray-600" />
          </button>
        </div>

        {/* Mobile Menu Dropdown */}
        {isMobileMenuOpen && (
          <div className="md:hidden mt-3 pt-3 border-t border-gray-200">
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="bg-gray-100 p-2 rounded-full">
                  <User className="h-5 w-5 text-gray-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {user?.user_metadata?.full_name || 'Student'}
                  </p>
                  <p className="text-xs text-gray-500">BIS Program</p>
                </div>
              </div>
              <div className="flex flex-col space-y-2 pt-2 border-t border-gray-100">
                <button className="text-left text-sm text-gray-700 hover:text-gray-900 py-2">
                  Profile Settings
                </button>
                <button className="text-left text-sm text-gray-700 hover:text-gray-900 py-2">
                  Help & Support
                </button>
                <button 
                  onClick={signOut}
                  className="text-left text-sm text-red-600 hover:text-red-700 py-2"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
