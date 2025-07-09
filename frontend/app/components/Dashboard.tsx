'use client'

import { 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  BookOpen, 
  Target, 
  TrendingUp,
  Download,
  Plus
} from 'lucide-react'
import { IAPData } from '../types'

interface DashboardProps {
  iapData: IAPData
  onExportIAP: () => void
  onSearchCourses: () => void
  onCheckRequirements: () => void
}

export default function Dashboard({ 
  iapData, 
  onExportIAP, 
  onSearchCourses, 
  onCheckRequirements 
}: DashboardProps) {
  const progressItems = [
    {
      label: 'Student Information',
      completed: !!(iapData.studentName && iapData.studentId),
      icon: CheckCircle,
    },
    {
      label: 'Degree Emphasis',
      completed: !!iapData.degreeEmphasis,
      icon: Target,
    },
    {
      label: 'Mission Statement',
      completed: !!iapData.missionStatement,
      icon: BookOpen,
    },
    {
      label: 'Program Goals',
      completed: iapData.programGoals.length >= 6,
      icon: Target,
      detail: `${iapData.programGoals.length}/6 goals`,
    },
    {
      label: 'Concentration Areas',
      completed: iapData.concentrationAreas.length >= 3,
      icon: BookOpen,
      detail: `${iapData.concentrationAreas.length}/3 areas`,
    },
    {
      label: 'Credit Requirements',
      completed: iapData.totalCredits >= 120 && iapData.upperDivisionCredits >= 40,
      icon: TrendingUp,
      detail: `${iapData.totalCredits}/120 total, ${iapData.upperDivisionCredits}/40 upper`,
    },
  ]

  const completedItems = progressItems.filter(item => item.completed).length
  const progressPercentage = Math.round((completedItems / progressItems.length) * 100)

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Progress Overview */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
        <div className="flex items-center justify-between mb-3 sm:mb-4">
          <h3 className="text-base sm:text-lg font-semibold text-gray-900">IAP Progress</h3>
          <span className="text-xl sm:text-2xl font-bold text-utah-red">{progressPercentage}%</span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2 sm:h-3 mb-3 sm:mb-4">
          <div 
            className="bg-utah-red h-2 sm:h-3 rounded-full transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
        
        <p className="text-xs sm:text-sm text-gray-600">
          {completedItems} of {progressItems.length} sections completed
        </p>
      </div>

      {/* Progress Checklist */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
        <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">Requirements Checklist</h3>
        
        <div className="space-y-2 sm:space-y-3">
          {progressItems.map((item, index) => {
            const Icon = item.icon
            return (
              <div key={index} className="flex items-center space-x-2 sm:space-x-3">
                <div className={`p-1 rounded-full flex-shrink-0 ${
                  item.completed ? 'bg-green-100' : 'bg-gray-100'
                }`}>
                  <Icon className={`h-3 w-3 sm:h-4 sm:w-4 ${
                    item.completed ? 'text-green-600' : 'text-gray-400'
                  }`} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-xs sm:text-sm font-medium truncate ${
                    item.completed ? 'text-gray-900' : 'text-gray-600'
                  }`}>
                    {item.label}
                  </p>
                  {item.detail && (
                    <p className="text-xs text-gray-500 truncate">{item.detail}</p>
                  )}
                </div>
                {item.completed ? (
                  <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5 text-green-500 flex-shrink-0" />
                ) : (
                  <Clock className="h-4 w-4 sm:h-5 sm:w-5 text-gray-400 flex-shrink-0" />
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Student Information */}
      {(iapData.studentName || iapData.degreeEmphasis) && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Student Information</h3>
          
          <div className="space-y-2">
            {iapData.studentName && (
              <div>
                <p className="text-sm font-medium text-gray-700">Name</p>
                <p className="text-sm text-gray-900">{iapData.studentName}</p>
              </div>
            )}
            
            {iapData.studentId && (
              <div>
                <p className="text-sm font-medium text-gray-700">Student ID</p>
                <p className="text-sm text-gray-900">{iapData.studentId}</p>
              </div>
            )}
            
            {iapData.degreeEmphasis && (
              <div>
                <p className="text-sm font-medium text-gray-700">Degree Emphasis</p>
                <p className="text-sm text-gray-900">{iapData.degreeEmphasis}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Concentration Areas */}
      {iapData.concentrationAreas.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Concentration Areas</h3>
          
          <div className="space-y-3">
            {iapData.concentrationAreas.map((area, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{area.name}</h4>
                  <span className="text-sm text-gray-600">
                    {area.credits} credits
                  </span>
                </div>
                <p className="text-xs text-gray-500">
                  {area.courses.length} courses • {area.upperDivisionCredits} upper-division
                </p>
              </div>
            ))}
            
            {iapData.concentrationAreas.length < 3 && (
              <button className="w-full border-2 border-dashed border-gray-300 rounded-lg p-3 text-gray-500 hover:border-gray-400 hover:text-gray-600 transition-colors">
                <Plus className="h-5 w-5 mx-auto mb-1" />
                <p className="text-sm">Add Concentration Area</p>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        
        <div className="space-y-2">
          <button 
            onClick={onExportIAP}
            className="w-full bg-utah-red text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
          >
            <Download className="h-4 w-4 inline mr-2" />
            Export IAP Draft
          </button>
          
          <button 
            onClick={onSearchCourses}
            className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
          >
            <BookOpen className="h-4 w-4 inline mr-2" />
            Search Courses
          </button>
          
          <button 
            onClick={onCheckRequirements}
            className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
          >
            <TrendingUp className="h-4 w-4 inline mr-2" />
            Check Requirements
          </button>
        </div>
      </div>

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-blue-900">Tip</h4>
            <p className="text-sm text-blue-700 mt-1">
              Ask me about specific courses, degree requirements, or career prospects for your emphasis area. I can help you find the perfect courses for your IAP!
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
