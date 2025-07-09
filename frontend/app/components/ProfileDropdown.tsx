'use client'

import { useState } from 'react'
import { User, Settings, LogOut, UserCircle, GraduationCap } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface ProfileDropdownProps {
  onSettingsClick: () => void
  onProfileClick: () => void
  onIAPsClick: () => void
  onLogoutClick: () => void
}

export default function ProfileDropdown({ 
  onSettingsClick, 
  onProfileClick,
  onIAPsClick, 
  onLogoutClick 
}: ProfileDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)

  const toggleDropdown = () => setIsOpen(!isOpen)

  return (
    <div className="relative">
      {/* Profile Button */}
      <button
        onClick={toggleDropdown}
        className="flex items-center gap-2 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        title="Profile Menu"
      >
        <div className="w-8 h-8 bg-utah-red rounded-full flex items-center justify-center">
          <User className="h-4 w-4 text-white" />
        </div>
        <span className="hidden sm:block text-sm font-medium">Student</span>
      </button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <div 
              className="fixed inset-0 z-10" 
              onClick={() => setIsOpen(false)}
            />
            
            {/* Menu */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 z-20"
            >
              <div className="py-1">
                {/* Profile Header */}
                <div className="px-4 py-3 border-b border-gray-100">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-utah-red rounded-full flex items-center justify-center">
                      <User className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Student User</p>
                      <p className="text-xs text-gray-500">student@utahtech.edu</p>
                    </div>
                  </div>
                </div>

                {/* Menu Items */}
                <button
                  onClick={() => {
                    onProfileClick()
                    setIsOpen(false)
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <UserCircle className="h-4 w-4" />
                  View Profile
                </button>

                <button
                  onClick={() => {
                    onIAPsClick()
                    setIsOpen(false)
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <GraduationCap className="h-4 w-4" />
                  My IAPs
                </button>

                <button
                  onClick={() => {
                    onSettingsClick()
                    setIsOpen(false)
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <Settings className="h-4 w-4" />
                  Settings
                </button>

                <div className="border-t border-gray-100">
                  <button
                    onClick={() => {
                      onLogoutClick()
                      setIsOpen(false)
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign Out
                  </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
