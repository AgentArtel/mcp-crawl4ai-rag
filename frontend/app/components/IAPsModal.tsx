'use client'

import { useState, useEffect } from 'react'
import { X, Plus, FileText, Calendar, CheckCircle, Clock, AlertCircle, Download, Edit3, Trash2, Eye } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface IAPsModalProps {
  isOpen: boolean
  onClose: () => void
}

interface IAP {
  id: string
  title: string
  degreeEmphasis: string
  status: 'draft' | 'in-review' | 'approved' | 'completed'
  lastModified: string
  progress: number
  creditsCompleted: number
  totalCredits: number
  concentrationAreas: string[]
}

const mockIAPs: IAP[] = [
  {
    id: '1',
    title: 'Psychology & Digital Media IAP',
    degreeEmphasis: 'Psychology and Digital Media Studies',
    status: 'in-review',
    lastModified: '2024-01-15',
    progress: 75,
    creditsCompleted: 90,
    totalCredits: 120,
    concentrationAreas: ['Psychology', 'Digital Media', 'Communication']
  },
  {
    id: '2',
    title: 'Business Analytics IAP',
    degreeEmphasis: 'Business Intelligence and Data Analytics',
    status: 'draft',
    lastModified: '2024-01-10',
    progress: 45,
    creditsCompleted: 54,
    totalCredits: 120,
    concentrationAreas: ['Business', 'Mathematics', 'Computer Science']
  },
  {
    id: '3',
    title: 'Environmental Science IAP',
    degreeEmphasis: 'Environmental Conservation and Policy',
    status: 'approved',
    lastModified: '2023-12-20',
    progress: 100,
    creditsCompleted: 120,
    totalCredits: 120,
    concentrationAreas: ['Biology', 'Environmental Science', 'Political Science']
  }
]

const getStatusColor = (status: IAP['status']) => {
  switch (status) {
    case 'draft': return 'bg-gray-100 text-gray-700'
    case 'in-review': return 'bg-yellow-100 text-yellow-700'
    case 'approved': return 'bg-green-100 text-green-700'
    case 'completed': return 'bg-blue-100 text-blue-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

const getStatusIcon = (status: IAP['status']) => {
  switch (status) {
    case 'draft': return <Edit3 className="h-4 w-4" />
    case 'in-review': return <Clock className="h-4 w-4" />
    case 'approved': return <CheckCircle className="h-4 w-4" />
    case 'completed': return <CheckCircle className="h-4 w-4" />
    default: return <AlertCircle className="h-4 w-4" />
  }
}

export default function IAPsModal({ isOpen, onClose }: IAPsModalProps) {
  const [iaps, setIaps] = useState<IAP[]>(mockIAPs)
  const [selectedIAP, setSelectedIAP] = useState<IAP | null>(null)

  const handleCreateNew = () => {
    console.log('Creating new IAP...')
    // Here you would navigate to IAP creation wizard
    // For now, just close modal and show a message
    onClose()
  }

  const handleViewIAP = (iap: IAP) => {
    setSelectedIAP(iap)
    console.log('Viewing IAP:', iap)
  }

  const handleEditIAP = (iap: IAP) => {
    console.log('Editing IAP:', iap)
    // Navigate to edit mode
  }

  const handleDeleteIAP = (iapId: string) => {
    console.log('Deleting IAP:', iapId)
    setIaps(iaps.filter(iap => iap.id !== iapId))
  }

  const handleDownloadIAP = (iap: IAP) => {
    console.log('Downloading IAP:', iap)
    // Generate and download PDF
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-y-auto"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-utah-red rounded-full flex items-center justify-center">
                  <FileText className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">My IAPs</h2>
                  <p className="text-sm text-gray-500">Manage your Individualized Academic Plans</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCreateNew}
                  className="flex items-center gap-2 px-3 py-2 text-sm bg-utah-red text-white rounded-md hover:bg-utah-red/90 transition-colors"
                >
                  <Plus className="h-4 w-4" />
                  Create New IAP
                </button>
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
              {iaps.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No IAPs Yet</h3>
                  <p className="text-gray-500 mb-4">Get started by creating your first Individualized Academic Plan</p>
                  <button
                    onClick={handleCreateNew}
                    className="flex items-center gap-2 px-4 py-2 bg-utah-red text-white rounded-md hover:bg-utah-red/90 transition-colors mx-auto"
                  >
                    <Plus className="h-4 w-4" />
                    Create Your First IAP
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                  {iaps.map((iap) => (
                    <motion.div
                      key={iap.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow"
                    >
                      {/* Status Badge */}
                      <div className="flex items-center justify-between mb-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(iap.status)}`}>
                          {getStatusIcon(iap.status)}
                          {iap.status.charAt(0).toUpperCase() + iap.status.slice(1).replace('-', ' ')}
                        </span>
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleViewIAP(iap)}
                            className="p-1 hover:bg-gray-100 rounded transition-colors"
                            title="View IAP"
                          >
                            <Eye className="h-4 w-4 text-gray-500" />
                          </button>
                          <button
                            onClick={() => handleEditIAP(iap)}
                            className="p-1 hover:bg-gray-100 rounded transition-colors"
                            title="Edit IAP"
                          >
                            <Edit3 className="h-4 w-4 text-gray-500" />
                          </button>
                          <button
                            onClick={() => handleDownloadIAP(iap)}
                            className="p-1 hover:bg-gray-100 rounded transition-colors"
                            title="Download IAP"
                          >
                            <Download className="h-4 w-4 text-gray-500" />
                          </button>
                          <button
                            onClick={() => handleDeleteIAP(iap.id)}
                            className="p-1 hover:bg-gray-100 rounded transition-colors"
                            title="Delete IAP"
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </button>
                        </div>
                      </div>

                      {/* IAP Info */}
                      <div className="mb-4">
                        <h3 className="font-semibold text-gray-900 mb-1">{iap.title}</h3>
                        <p className="text-sm text-gray-600 mb-2">{iap.degreeEmphasis}</p>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <Calendar className="h-3 w-3" />
                          <span>Modified {new Date(iap.lastModified).toLocaleDateString()}</span>
                        </div>
                      </div>

                      {/* Progress */}
                      <div className="mb-4">
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="text-gray-600">Progress</span>
                          <span className="font-medium">{iap.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-utah-red h-2 rounded-full transition-all duration-300"
                            style={{ width: `${iap.progress}%` }}
                          />
                        </div>
                      </div>

                      {/* Credits */}
                      <div className="mb-4">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Credits</span>
                          <span className="font-medium">
                            {iap.creditsCompleted}/{iap.totalCredits}
                          </span>
                        </div>
                      </div>

                      {/* Concentration Areas */}
                      <div>
                        <p className="text-xs text-gray-500 mb-2">Concentration Areas:</p>
                        <div className="flex flex-wrap gap-1">
                          {iap.concentrationAreas.map((area, index) => (
                            <span
                              key={index}
                              className="inline-block px-2 py-1 bg-gray-100 text-xs text-gray-700 rounded"
                            >
                              {area}
                            </span>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
