'use client'

import { useState, useRef, useEffect } from 'react'
import { User, Settings, LogOut, Edit, BookOpen, Download, HelpCircle } from 'lucide-react'

interface ProfileMenuProps {
  user?: {
    name: string
    email: string
    studentId?: string
    avatar?: string
  }
  onSettingsClick: () => void
  onProfileEdit: () => void
  onLogout: () => void
}

export default function ProfileMenu({ user, onSettingsClick, onProfileEdit, onLogout }: ProfileMenuProps) {
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const defaultUser = {
    name: user?.name || 'Student User',
    email: user?.email || 'student@utahtech.edu',
    studentId: user?.studentId || 'UT123456',
    avatar: user?.avatar
  }

  const menuItems = [
    {
      icon: Edit,
      label: 'Edit Profile',
      onClick: onProfileEdit,
      description: 'Update your information'
    },
    {
      icon: BookOpen,
      label: 'My IAPs',
      onClick: () => console.log('View IAPs'),
      description: 'View saved academic plans'
    },
    {
      icon: Download,
      label: 'Export Data',
      onClick: () => console.log('Export data'),
      description: 'Download your IAP documents'
    },
    {
      icon: Settings,
      label: 'Settings',
      onClick: onSettingsClick,
      description: 'AI preferences and API keys'
    },
    {
      icon: HelpCircle,
      label: 'Help & Support',
      onClick: () => console.log('Help'),
      description: 'Get help using the advisor'
    }
  ]

  return (
    <div className="relative" ref={menuRef}>
      {/* Profile Picture Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 transition-colors group"
        aria-label="Open profile menu"
      >
        <div className="relative">
          {defaultUser.avatar ? (
            <img
              src={defaultUser.avatar}
              alt={defaultUser.name}
              className="w-8 h-8 rounded-full object-cover"
            />
          ) : (
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">
                {defaultUser.name.split(' ').map(n => n[0]).join('').toUpperCase()}
              </span>
            </div>
          )}
          <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
        </div>
        <div className="hidden md:block text-left">
          <div className="text-sm font-medium text-gray-900">{defaultUser.name}</div>
          <div className="text-xs text-gray-500">{defaultUser.studentId}</div>
        </div>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-72 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
          {/* User Info Header */}
          <div className="px-4 py-3 border-b border-gray-100">
            <div className="flex items-center gap-3">
              {defaultUser.avatar ? (
                <img
                  src={defaultUser.avatar}
                  alt={defaultUser.name}
                  className="w-10 h-10 rounded-full object-cover"
                />
              ) : (
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-medium">
                    {defaultUser.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                  </span>
                </div>
              )}
              <div>
                <div className="font-medium text-gray-900">{defaultUser.name}</div>
                <div className="text-sm text-gray-500">{defaultUser.email}</div>
                <div className="text-xs text-gray-400">ID: {defaultUser.studentId}</div>
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <div className="py-2">
            {menuItems.map((item, index) => {
              const Icon = item.icon
              return (
                <button
                  key={index}
                  onClick={() => {
                    item.onClick()
                    setIsOpen(false)
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2 text-left hover:bg-gray-50 transition-colors"
                >
                  <Icon className="w-4 h-4 text-gray-500" />
                  <div>
                    <div className="text-sm font-medium text-gray-900">{item.label}</div>
                    <div className="text-xs text-gray-500">{item.description}</div>
                  </div>
                </button>
              )
            })}
          </div>

          {/* Logout */}
          <div className="border-t border-gray-100 pt-2">
            <button
              onClick={() => {
                onLogout()
                setIsOpen(false)
              }}
              className="w-full flex items-center gap-3 px-4 py-2 text-left hover:bg-red-50 transition-colors text-red-600"
            >
              <LogOut className="w-4 h-4" />
              <div>
                <div className="text-sm font-medium">Sign Out</div>
                <div className="text-xs text-red-500">End your session</div>
              </div>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
