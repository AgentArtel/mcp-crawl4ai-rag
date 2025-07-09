'use client'

import { useState } from 'react'
import { MessageSquare, Plus, Trash2, Clock, Search, X } from 'lucide-react'
import { ChatSession } from '../hooks/useChatHistory'

interface ChatHistoryProps {
  sessions: ChatSession[]
  currentSession: ChatSession | null
  onNewChat: () => void
  onSwitchSession: (sessionId: string) => void
  onDeleteSession: (sessionId: string) => void
  onClearAll: () => void
  isOpen: boolean
  onClose: () => void
}

export default function ChatHistory({
  sessions,
  currentSession,
  onNewChat,
  onSwitchSession,
  onDeleteSession,
  onClearAll,
  isOpen,
  onClose
}: ChatHistoryProps) {
  const [searchTerm, setSearchTerm] = useState('')

  const filteredSessions = sessions.filter(session =>
    session.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    session.messages.some(msg => 
      msg.content.toLowerCase().includes(searchTerm.toLowerCase())
    )
  )

  const formatDate = (date: Date): string => {
    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    
    if (diffInHours < 1) {
      const diffInMinutes = Math.floor(diffInHours * 60)
      return diffInMinutes <= 1 ? 'Just now' : `${diffInMinutes}m ago`
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`
    } else if (diffInHours < 24 * 7) {
      return `${Math.floor(diffInHours / 24)}d ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  const handleDeleteSession = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation()
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      onDeleteSession(sessionId)
    }
  }

  const handleClearAll = () => {
    if (window.confirm('Are you sure you want to clear all chat history? This cannot be undone.')) {
      onClearAll()
    }
  }

  if (!isOpen) return null

  return (
    <>
      {/* Overlay for mobile */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <div className={`
        fixed lg:relative top-0 left-0 h-full w-80 bg-white border-r border-gray-200 z-50
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        flex flex-col
      `}>
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <MessageSquare className="h-5 w-5 mr-2" />
              Chat History
            </h2>
            <button
              onClick={onClose}
              className="lg:hidden p-1 text-gray-500 hover:text-gray-700"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          {/* New Chat Button */}
          <button
            onClick={onNewChat}
            className="w-full bg-utah-red text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Search */}
        <div className="p-4 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-utah-red focus:border-transparent text-sm"
            />
          </div>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto">
          {filteredSessions.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              {searchTerm ? 'No conversations match your search' : 'No chat history yet'}
            </div>
          ) : (
            <div className="space-y-1 p-2">
              {filteredSessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => onSwitchSession(session.id)}
                  className={`
                    p-3 rounded-lg cursor-pointer transition-colors group
                    ${currentSession?.id === session.id 
                      ? 'bg-utah-red bg-opacity-10 border border-utah-red border-opacity-30' 
                      : 'hover:bg-gray-50'
                    }
                  `}
                >
                  <div className="flex items-start justify-between">
                    <div className="min-w-0 flex-1">
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {session.title}
                      </h3>
                      <div className="flex items-center mt-1 text-xs text-gray-500">
                        <Clock className="h-3 w-3 mr-1" />
                        {formatDate(session.updatedAt)}
                        <span className="mx-2">•</span>
                        <span>{session.messages.length} messages</span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleDeleteSession(e, session.id)}
                      className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-all"
                      title="Delete conversation"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  
                  {/* Preview of last message */}
                  {session.messages.length > 0 && (
                    <div className="mt-2 text-xs text-gray-600 truncate">
                      {session.messages[session.messages.length - 1].content}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {sessions.length > 0 && (
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={handleClearAll}
              className="w-full text-sm text-red-600 hover:text-red-700 transition-colors flex items-center justify-center space-x-2"
            >
              <Trash2 className="h-4 w-4" />
              <span>Clear All History</span>
            </button>
          </div>
        )}
      </div>
    </>
  )
}
