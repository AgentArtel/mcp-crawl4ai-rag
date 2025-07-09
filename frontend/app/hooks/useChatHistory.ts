'use client'

import { useState, useEffect } from 'react'
import { Message } from '../types'

export interface ChatSession {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
  studentId?: string
}

export interface ChatHistoryHook {
  sessions: ChatSession[]
  currentSession: ChatSession | null
  createSession: (title?: string) => ChatSession
  switchSession: (sessionId: string) => void
  updateSession: (sessionId: string, messages: Message[]) => void
  deleteSession: (sessionId: string) => void
  clearAllHistory: () => void
}

const STORAGE_KEY = 'utah-tech-iap-chat-history'

export function useChatHistory(studentId?: string): ChatHistoryHook {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null)

  // Load chat history from localStorage on mount
  useEffect(() => {
    try {
      const storedHistory = localStorage.getItem(STORAGE_KEY)
      if (storedHistory) {
        const parsed = JSON.parse(storedHistory)
        const sessionsWithDates = parsed.map((session: any) => ({
          ...session,
          createdAt: new Date(session.createdAt),
          updatedAt: new Date(session.updatedAt),
          messages: session.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }))
        }))
        
        // Filter sessions by studentId if provided
        const filteredSessions = studentId 
          ? sessionsWithDates.filter((s: ChatSession) => s.studentId === studentId)
          : sessionsWithDates
        
        setSessions(filteredSessions)
        
        // Set the most recent session as current
        if (filteredSessions.length > 0) {
          const mostRecent = filteredSessions.sort((a: ChatSession, b: ChatSession) => 
            b.updatedAt.getTime() - a.updatedAt.getTime()
          )[0]
          setCurrentSession(mostRecent)
        }
      }
    } catch (error) {
      console.error('Failed to load chat history:', error)
    }
  }, [studentId])

  // Save sessions to localStorage whenever sessions change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions))
    } catch (error) {
      console.error('Failed to save chat history:', error)
    }
  }, [sessions])

  const generateSessionTitle = (messages: Message[]): string => {
    if (messages.length === 0) return 'New Chat'
    
    const firstUserMessage = messages.find(m => m.type === 'user')
    if (firstUserMessage) {
      // Take first 50 characters and add ellipsis if longer
      const title = firstUserMessage.content.trim()
      return title.length > 50 ? title.substring(0, 50) + '...' : title
    }
    
    return 'New Chat'
  }

  const createSession = (title?: string): ChatSession => {
    const newSession: ChatSession = {
      id: `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
      title: title || 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      studentId
    }

    setSessions(prev => [newSession, ...prev])
    setCurrentSession(newSession)
    return newSession
  }

  const switchSession = (sessionId: string): void => {
    const session = sessions.find(s => s.id === sessionId)
    if (session) {
      setCurrentSession(session)
    }
  }

  const updateSession = (sessionId: string, messages: Message[]): void => {
    setSessions(prev => prev.map(session => {
      if (session.id === sessionId) {
        const updatedSession = {
          ...session,
          messages,
          updatedAt: new Date(),
          title: session.title === 'New Chat' ? generateSessionTitle(messages) : session.title
        }
        
        // Update current session if it's the one being updated
        if (currentSession?.id === sessionId) {
          setCurrentSession(updatedSession)
        }
        
        return updatedSession
      }
      return session
    }))
  }

  const deleteSession = (sessionId: string): void => {
    setSessions(prev => prev.filter(s => s.id !== sessionId))
    
    // If deleting current session, switch to most recent or create new
    if (currentSession?.id === sessionId) {
      const remainingSessions = sessions.filter(s => s.id !== sessionId)
      if (remainingSessions.length > 0) {
        const mostRecent = remainingSessions.sort((a, b) => 
          b.updatedAt.getTime() - a.updatedAt.getTime()
        )[0]
        setCurrentSession(mostRecent)
      } else {
        const newSession = createSession()
        setCurrentSession(newSession)
      }
    }
  }

  const clearAllHistory = (): void => {
    setSessions([])
    setCurrentSession(null)
    localStorage.removeItem(STORAGE_KEY)
  }

  return {
    sessions,
    currentSession,
    createSession,
    switchSession,
    updateSession,
    deleteSession,
    clearAllHistory
  }
}
