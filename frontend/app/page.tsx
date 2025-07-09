'use client'

import { useState, useEffect, useCallback } from 'react'
import { Settings, User, LogOut, Menu, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import ChatInterface from './components/ChatInterface'
import Dashboard from './components/Dashboard'
import SettingsModal from './components/SettingsModal'
import ProfileDropdown from './components/ProfileDropdown'
import ProfileModal from './components/ProfileModal'
import IAPsModal from './components/IAPsModal'
import ErrorBoundary, { ChatErrorBoundary, DashboardErrorBoundary } from './components/ErrorBoundary'
import { ToastContainer, useToast } from './components/Toast'
import { useErrorHandler } from './hooks/useErrorHandler'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { PageLoading, NetworkError } from './components/LoadingStates'
import { IAPData, Message } from './types'

function MainApp() {
  const { logout } = useAuth()

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: "Hi! I'm your Utah Tech IAP Advisor. I'm here to help you create your personalized Individualized Academic Plan for the Bachelor of Individualized Studies program. Let's start by getting to know your academic interests and career goals. What would you like to focus on in your degree?",
      timestamp: new Date(),
    }
  ])
  
  const [iapData, setIapData] = useState<IAPData>({
    studentName: '',
    studentId: '',
    degreeEmphasis: '',
    missionStatement: '',
    programGoals: [],
    concentrationAreas: [],
    totalCredits: 0,
    upperDivisionCredits: 0,
    completionPercentage: 0,
  })

  const [isLoading, setIsLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const [showIAPs, setShowIAPs] = useState(false)
  const [currentTool, setCurrentTool] = useState<string | null>(null)
  const { toasts, addToast, removeToast, success, warning, info } = useToast()

  // Quick Actions handlers
  const handleExportIAP = () => {
    const iapJson = JSON.stringify({
      studentInfo: {
        name: iapData.studentName || 'Student Name',
        id: iapData.studentId || 'Student ID',
        email: iapData.studentEmail || 'student@utahtech.edu'
      },
      degreeEmphasis: iapData.degreeEmphasis || 'Not specified',
      missionStatement: iapData.missionStatement || 'Mission statement not yet defined',
      programGoals: iapData.programGoals || [],
      concentrationAreas: iapData.concentrationAreas || [],
      courseMappings: iapData.courseMappings || {},
      exportDate: new Date().toISOString()
    }, null, 2)
    
    const blob = new Blob([iapJson], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${iapData.studentName || 'Student'}_IAP_Draft.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    success('IAP Exported', 'Your IAP draft has been downloaded as JSON file')
  }

  const handleSearchCourses = () => {
    const searchQuery = 'I want to search for courses that might fit my degree emphasis. Can you help me find relevant courses?'
    handleSendMessage(searchQuery)
  }

  const handleCheckRequirements = () => {
    const requirementsQuery = 'Can you check my current IAP progress and tell me what requirements I still need to complete for my BIS degree?'
    handleSendMessage(requirementsQuery)
  }

  const [settings, setSettings] = useState({
    aiProvider: 'openai' as 'openai' | 'anthropic' | 'gemini',
    model: 'gpt-4',
    temperature: 0.7,
    maxTokens: 1000,
    systemPrompt: 'You are a helpful academic advisor for Utah Tech University.',
    openaiApiKey: '',
    anthropicApiKey: '',
    geminiApiKey: ''
  })

  const { handleError, handleMCPError } = useErrorHandler()

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('iap-advisor-settings')
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings))
    }
  }, [])

  const handleSaveSettings = (newSettings: typeof settings) => {
    setSettings(newSettings)
    localStorage.setItem('iap-advisor-settings', JSON.stringify(newSettings))
    success('Settings saved', 'Your preferences have been updated successfully')
  }

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setCurrentTool('processing')

    try {
      // Check if API keys are configured
      if (!settings.openaiApiKey && !settings.anthropicApiKey) {
        warning('API Keys Required', 'Please configure your API keys in settings to use the AI advisor')
        setIsLoading(false)
        setCurrentTool(null)
        return
      }

      // Show tool loading indicator
      info('Processing request', 'Analyzing your message and selecting appropriate tools...')
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          context: {
            conversationHistory: messages,
            iapData: iapData
          },
          settings: settings
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      if (data.error) {
        throw new Error(data.error)
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.response,
        timestamp: new Date(),
        toolResults: data.toolResults,
      }

      setMessages(prev => [...prev, assistantMessage])

      // Update IAP data if provided
      if (data.iapUpdate) {
        setIapData(prev => ({ ...prev, ...data.iapUpdate }))
        success('IAP Updated', 'Your academic plan has been updated with new information')
      }

      // Show success for tool usage
      if (data.toolResults && data.toolResults.length > 0) {
        const toolNames = data.toolResults.map((t: any) => t.toolName).join(', ')
        success('Tools Executed', `Successfully used: ${toolNames}`)
      }

    } catch (error: any) {
      console.error('Error sending message:', error)
      
      let errorTitle = 'Connection Error'
      let errorMessage = 'Unable to connect to the AI advisor. Please check your internet connection and try again.'
      
      if (error.message.includes('401')) {
        errorTitle = 'Authentication Error'
        errorMessage = 'Invalid API key. Please check your API key in settings.'
      } else if (error.message.includes('429')) {
        errorTitle = 'Rate Limit Exceeded'
        errorMessage = 'Too many requests. Please wait a moment before trying again.'
      } else if (error.message.includes('500')) {
        errorTitle = 'Server Error'
        errorMessage = 'The AI service is temporarily unavailable. Please try again later.'
      }
      
      addToast({
        type: 'error',
        title: errorTitle,
        message: errorMessage,
        duration: 7000,
        action: {
          label: 'Retry',
          onClick: () => handleSendMessage(content)
        }
      })
      
      const errorResponseMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `I apologize, but I encountered an error: ${errorTitle}. ${errorMessage}`,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorResponseMessage])
    } finally {
      setIsLoading(false)
      setCurrentTool(null)
    }
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
      {/* Updated Header with Profile Menu */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">UT</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Utah Tech IAP Advisor</h1>
                <p className="text-sm text-gray-600">Individualized Academic Planning Assistant</p>
              </div>
            </div>
            
            {/* Profile Dropdown */}
            <div className="flex items-center gap-2">
              <ProfileDropdown
                onSettingsClick={() => setShowSettings(true)}
                onProfileClick={() => setShowProfile(true)}
                onIAPsClick={() => setShowIAPs(true)}
                onLogoutClick={logout}
              />
            </div>
          </div>
        </div>
      </header>
      
      <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          {/* Chat Interface - Takes up 2/3 on large screens, full width on mobile */}
          <div className="lg:col-span-2 order-1 lg:order-1">
            <ChatErrorBoundary>
              <ChatInterface
                messages={messages}
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
              />
            </ChatErrorBoundary>
          </div>
          
          {/* Dashboard - Takes up 1/3 on large screens, full width on mobile */}
          <div className="lg:col-span-1 order-2 lg:order-2">
            <DashboardErrorBoundary>
              <Dashboard 
                iapData={iapData}
                onExportIAP={handleExportIAP}
                onSearchCourses={handleSearchCourses}
                onCheckRequirements={handleCheckRequirements}
              />
            </DashboardErrorBoundary>
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <SettingsModal
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
          onSave={handleSaveSettings}
        />
      )}

      {/* Profile Modal */}
      <ProfileModal
        isOpen={showProfile}
        onClose={() => setShowProfile(false)}
      />

      {/* IAPs Modal */}
      <IAPsModal
        isOpen={showIAPs}
        onClose={() => setShowIAPs(false)}
      />

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onClose={removeToast} />
      
      {/* Loading Overlay */}
      {isLoading && currentTool && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-40 p-4">
          <div className="bg-white rounded-lg p-4 sm:p-6 max-w-sm w-full mx-4">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-utah-red"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">Processing...</p>
                <p className="text-xs text-gray-500 capitalize">
                  {currentTool.replace(/_/g, ' ')}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </ErrorBoundary>
  )
}

// Wrap MainApp with AuthProvider
export default function Home() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  )
}
