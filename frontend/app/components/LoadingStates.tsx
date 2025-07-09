'use client'

import React from 'react'
import { Loader2, MessageSquare, Search, Calculator, TrendingUp, FileText } from 'lucide-react'

// Generic loading spinner
export function LoadingSpinner({ size = 'md', className = '' }: { 
  size?: 'sm' | 'md' | 'lg'
  className?: string 
}) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6', 
    lg: 'h-8 w-8'
  }
  
  return (
    <Loader2 className={`animate-spin ${sizeClasses[size]} ${className}`} />
  )
}

// Skeleton loading components
export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse bg-gray-200 rounded-lg ${className}`}>
      <div className="p-4 space-y-3">
        <div className="h-4 bg-gray-300 rounded w-3/4"></div>
        <div className="h-3 bg-gray-300 rounded w-1/2"></div>
        <div className="h-3 bg-gray-300 rounded w-5/6"></div>
      </div>
    </div>
  )
}

export function SkeletonMessage() {
  return (
    <div className="animate-pulse">
      <div className="flex space-x-3 mb-4">
        <div className="h-8 w-8 bg-gray-300 rounded-full"></div>
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-gray-300 rounded w-3/4"></div>
          <div className="h-4 bg-gray-300 rounded w-1/2"></div>
        </div>
      </div>
    </div>
  )
}

export function SkeletonDashboard() {
  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Progress Overview Skeleton */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
        <div className="animate-pulse">
          <div className="flex items-center justify-between mb-3 sm:mb-4">
            <div className="h-5 bg-gray-300 rounded w-32"></div>
            <div className="h-8 bg-gray-300 rounded w-12"></div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 sm:h-3 mb-3 sm:mb-4">
            <div className="bg-gray-300 h-2 sm:h-3 rounded-full w-1/3"></div>
          </div>
          <div className="h-4 bg-gray-300 rounded w-48"></div>
        </div>
      </div>

      {/* Checklist Skeleton */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
        <div className="animate-pulse">
          <div className="h-5 bg-gray-300 rounded w-40 mb-3 sm:mb-4"></div>
          <div className="space-y-2 sm:space-y-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="flex items-center space-x-2 sm:space-x-3">
                <div className="h-6 w-6 bg-gray-300 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-300 rounded w-3/4 mb-1"></div>
                  <div className="h-3 bg-gray-300 rounded w-1/2"></div>
                </div>
                <div className="h-5 w-5 bg-gray-300 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// MCP Tool specific loading states
export function MCPToolLoading({ toolName }: { toolName: string }) {
  const getToolIcon = (name: string) => {
    if (name.includes('search')) return Search
    if (name.includes('calculate')) return Calculator
    if (name.includes('market')) return TrendingUp
    if (name.includes('iap') || name.includes('template')) return FileText
    return MessageSquare
  }

  const Icon = getToolIcon(toolName)

  return (
    <div className="flex items-center space-x-3">
      <div className="relative">
        <Icon className="h-6 w-6 text-utah-red" />
        <LoadingSpinner size="sm" className="absolute -top-1 -right-1 text-utah-red" />
      </div>
      <div>
        <p className="text-sm font-medium text-gray-900">Processing...</p>
        <p className="text-xs text-gray-500 capitalize">
          {toolName.replace(/_/g, ' ')}
        </p>
      </div>
    </div>
  )
}

// Chat loading states
export function ChatLoading() {
  return (
    <div className="flex items-center space-x-2 text-gray-500 p-3">
      <LoadingSpinner size="sm" />
      <span className="text-sm">AI is thinking...</span>
    </div>
  )
}

export function TypingIndicator() {
  return (
    <div className="flex items-center space-x-1 p-3">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
      </div>
      <span className="text-xs text-gray-500 ml-2">AI is typing...</span>
    </div>
  )
}

// Full page loading
export function PageLoading() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner size="lg" className="text-utah-red mx-auto mb-4" />
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Loading Utah Tech IAP Advisor</h2>
        <p className="text-gray-600">Preparing your academic planning experience...</p>
      </div>
    </div>
  )
}

// Network error retry component
export function NetworkError({ onRetry, message }: { 
  onRetry: () => void
  message?: string 
}) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
      <div className="text-red-600 mb-3">
        <svg className="h-8 w-8 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 className="text-sm font-medium text-red-800 mb-2">Connection Error</h3>
      <p className="text-sm text-red-700 mb-4">
        {message || 'Unable to connect to the server. Please check your internet connection.'}
      </p>
      <button
        onClick={onRetry}
        className="inline-flex items-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
      >
        <Loader2 className="h-4 w-4 mr-2" />
        Try Again
      </button>
    </div>
  )
}
