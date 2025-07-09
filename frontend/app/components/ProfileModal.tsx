'use client'

import { useState } from 'react'
import { X, User, Mail, Phone, Calendar, GraduationCap, Edit2, Save } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface ProfileModalProps {
  isOpen: boolean
  onClose: () => void
}

interface StudentProfile {
  name: string
  email: string
  phone: string
  studentId: string
  major: string
  classification: string
  gpa: string
  expectedGraduation: string
  advisor: string
}

export default function ProfileModal({ isOpen, onClose }: ProfileModalProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [profile, setProfile] = useState<StudentProfile>({
    name: 'Student User',
    email: 'student@utahtech.edu',
    phone: '(435) 555-0123',
    studentId: '00123456',
    major: 'Bachelor of Individualized Studies',
    classification: 'Senior',
    gpa: '3.45',
    expectedGraduation: 'Spring 2024',
    advisor: 'Dr. Academic Advisor'
  })

  const handleSave = () => {
    // Here you would normally save to backend/database
    console.log('Saving profile:', profile)
    setIsEditing(false)
    // Could add a toast notification here
  }

  const handleCancel = () => {
    setIsEditing(false)
    // Reset any unsaved changes if needed
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-utah-red rounded-full flex items-center justify-center">
                  <User className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Student Profile</h2>
                  <p className="text-sm text-gray-500">Manage your account information</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {!isEditing && (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="flex items-center gap-2 px-3 py-2 text-sm bg-utah-red text-white rounded-md hover:bg-utah-red/90 transition-colors"
                  >
                    <Edit2 className="h-4 w-4" />
                    Edit
                  </button>
                )}
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Personal Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Personal Information
                  </h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Full Name
                    </label>
                    {isEditing ? (
                      <input
                        type="text"
                        value={profile.name}
                        onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-utah-red"
                      />
                    ) : (
                      <p className="px-3 py-2 bg-gray-50 rounded-md">{profile.name}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email Address
                    </label>
                    {isEditing ? (
                      <input
                        type="email"
                        value={profile.email}
                        onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-utah-red"
                      />
                    ) : (
                      <p className="px-3 py-2 bg-gray-50 rounded-md flex items-center gap-2">
                        <Mail className="h-4 w-4 text-gray-400" />
                        {profile.email}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Phone Number
                    </label>
                    {isEditing ? (
                      <input
                        type="tel"
                        value={profile.phone}
                        onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-utah-red"
                      />
                    ) : (
                      <p className="px-3 py-2 bg-gray-50 rounded-md flex items-center gap-2">
                        <Phone className="h-4 w-4 text-gray-400" />
                        {profile.phone}
                      </p>
                    )}
                  </div>
                </div>

                {/* Academic Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
                    <GraduationCap className="h-5 w-5" />
                    Academic Information
                  </h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Student ID
                    </label>
                    <p className="px-3 py-2 bg-gray-50 rounded-md">{profile.studentId}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Major
                    </label>
                    <p className="px-3 py-2 bg-gray-50 rounded-md">{profile.major}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Classification
                    </label>
                    <p className="px-3 py-2 bg-gray-50 rounded-md">{profile.classification}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current GPA
                    </label>
                    <p className="px-3 py-2 bg-gray-50 rounded-md">{profile.gpa}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Expected Graduation
                    </label>
                    <p className="px-3 py-2 bg-gray-50 rounded-md flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      {profile.expectedGraduation}
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Academic Advisor
                    </label>
                    <p className="px-3 py-2 bg-gray-50 rounded-md">{profile.advisor}</p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              {isEditing && (
                <div className="flex items-center gap-3 mt-6 pt-6 border-t border-gray-200">
                  <button
                    onClick={handleSave}
                    className="flex items-center gap-2 px-4 py-2 bg-utah-red text-white rounded-md hover:bg-utah-red/90 transition-colors"
                  >
                    <Save className="h-4 w-4" />
                    Save Changes
                  </button>
                  <button
                    onClick={handleCancel}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
