'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, History, X } from 'lucide-react'
import { Message } from '../types'
import MessageBubble from './MessageBubble'
import ChatHistory from './ChatHistory'
import { useChatHistory } from '../hooks/useChatHistory'

interface ChatInterfaceProps {
  messages: Message[]
  onSendMessage: (content: string) => void
  isLoading: boolean
  studentId?: string
}

export default function ChatInterface({ messages, onSendMessage, isLoading, studentId }: ChatInterfaceProps) {
  const [inputValue, setInputValue] = useState('')
  const [showHistory, setShowHistory] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  
  // Chat history management
  const {
    sessions,
    currentSession,
    createSession,
    switchSession,
    updateSession,
    deleteSession,
    clearAllHistory
  } = useChatHistory(studentId)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize first session if none exists
  useEffect(() => {
    if (!currentSession && sessions.length === 0) {
      createSession()
    }
  }, [currentSession, sessions.length, createSession])

  // Update current session when messages change
  useEffect(() => {
    if (currentSession && messages.length > 0) {
      updateSession(currentSession.id, messages)
    }
  }, [messages, currentSession, updateSession])

  // Handle switching sessions
  const handleSwitchSession = (sessionId: string) => {
    switchSession(sessionId)
    setShowHistory(false)
  }

  // Handle creating new session
  const handleNewChat = () => {
    createSession()
    setShowHistory(false)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim())
      setInputValue('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="flex h-[500px] sm:h-[600px] relative">
      {/* Chat History Sidebar */}
      <ChatHistory
        sessions={sessions}
        currentSession={currentSession}
        onNewChat={handleNewChat}
        onSwitchSession={handleSwitchSession}
        onDeleteSession={deleteSession}
        onClearAll={clearAllHistory}
        isOpen={showHistory}
        onClose={() => setShowHistory(false)}
      />
      
      {/* Main Chat Interface */}
      <div className={`flex-1 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col ${showHistory ? 'lg:ml-0' : ''}`}>
        {/* Chat Header */}
        <div className="p-3 sm:p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
          <div className="flex items-center space-x-2 sm:space-x-3">
            <button
              onClick={() => setShowHistory(true)}
              className="lg:hidden p-1.5 text-gray-600 hover:text-utah-red transition-colors"
              title="Show chat history"
            >
              <History className="h-4 w-4" />
            </button>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="hidden lg:block p-1.5 text-gray-600 hover:text-utah-red transition-colors"
              title={showHistory ? 'Hide chat history' : 'Show chat history'}
            >
              <History className="h-4 w-4" />
            </button>
            <div className="bg-utah-red p-1.5 sm:p-2 rounded-full">
              <Bot className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="font-semibold text-gray-900 text-sm sm:text-base truncate">
                {currentSession?.title || 'IAP Advisor Assistant'}
              </h3>
              <p className="text-xs sm:text-sm text-gray-600 truncate">
                {isLoading ? 'Thinking...' : 'Online • Ready to help with your IAP'}
              </p>
            </div>
          </div>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div className="flex items-start space-x-2 sm:space-x-3">
              <div className="bg-utah-red p-1.5 sm:p-2 rounded-full flex-shrink-0">
                <Bot className="h-3 w-3 sm:h-4 sm:w-4 text-white" />
              </div>
              <div className="bg-gray-100 rounded-lg px-3 py-2 sm:px-4 sm:py-2 max-w-[80%] sm:max-w-xs">
                <div className="flex items-center space-x-2">
                  <Loader2 className="h-3 w-3 sm:h-4 sm:w-4 animate-spin text-gray-600" />
                  <span className="text-xs sm:text-sm text-gray-600">Analyzing your request...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <div className="p-3 sm:p-4 border-t border-gray-200">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about courses, requirements, or your IAP..."
              className="flex-1 px-3 py-2 sm:px-4 sm:py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-utah-red focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="bg-utah-red text-white px-3 py-2 sm:px-4 sm:py-2 rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-utah-red focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
            >
              <Send className="h-4 w-4 sm:h-5 sm:w-5" />
            </button>
          </form>
          
          <div className="mt-2 flex flex-wrap gap-1 sm:gap-2">
            {!isLoading && messages.length <= 2 && (
              <>
                <button
                  onClick={() => onSendMessage("I want to create an emphasis in Psychology and Digital Media")}
                  className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 sm:px-3 sm:py-1 rounded-full text-gray-700 transition-colors"
                >
                  Psychology & Digital Media
                </button>
                <button
                  onClick={() => onSendMessage("Help me find courses for my concentration areas")}
                  className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 sm:px-3 sm:py-1 rounded-full text-gray-700"
                >
                  Find Courses
                </button>
                <button
                  onClick={() => onSendMessage("What are the BIS degree requirements?")}
                  className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 sm:px-3 sm:py-1 rounded-full text-gray-700 transition-colors"
                >
                  BIS Requirements
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
