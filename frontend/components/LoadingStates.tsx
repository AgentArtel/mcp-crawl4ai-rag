'use client'

import { Loader2, Brain, Search, Calculator, TrendingUp } from 'lucide-react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function LoadingSpinner({ size = 'md', className = '' }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  }

  return (
    <Loader2 className={`animate-spin ${sizeClasses[size]} ${className}`} />
  )
}

interface TypingIndicatorProps {
  className?: string
}

export function TypingIndicator({ className = '' }: TypingIndicatorProps) {
  return (
    <div className={`flex items-center gap-2 text-gray-500 ${className}`}>
      <div className="flex gap-1">
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
      </div>
      <span className="text-sm">AI is thinking...</span>
    </div>
  )
}

interface MCPToolLoadingProps {
  toolName?: string
  className?: string
}

export function MCPToolLoading({ toolName, className = '' }: MCPToolLoadingProps) {
  const getToolIcon = (tool: string) => {
    switch (tool) {
      case 'search_courses':
      case 'search_degree_programs':
        return Search
      case 'calculate_credits':
        return Calculator
      case 'conduct_market_research':
        return TrendingUp
      default:
        return Brain
    }
  }

  const Icon = toolName ? getToolIcon(toolName) : Brain

  return (
    <div className={`flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg ${className}`}>
      <Icon className="w-5 h-5 text-blue-600 animate-pulse" />
      <div>
        <div className="text-sm font-medium text-blue-900">
          {toolName ? `Running ${toolName.replace('_', ' ')}...` : 'Processing request...'}
        </div>
        <div className="text-xs text-blue-600">Using MCP tools to help you</div>
      </div>
      <LoadingSpinner size="sm" className="text-blue-600" />
    </div>
  )
}

interface SkeletonProps {
  className?: string
  lines?: number
}

export function Skeleton({ className = '', lines = 1 }: SkeletonProps) {
  return (
    <div className={`animate-pulse ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={`bg-gray-200 rounded ${i === lines - 1 ? 'w-3/4' : 'w-full'} h-4 ${i > 0 ? 'mt-2' : ''}`}
        ></div>
      ))}
    </div>
  )
}

interface MessageSkeletonProps {
  className?: string
}

export function MessageSkeleton({ className = '' }: MessageSkeletonProps) {
  return (
    <div className={`flex gap-3 p-4 ${className}`}>
      <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse"></div>
      <div className="flex-1">
        <Skeleton lines={3} />
      </div>
    </div>
  )
}

interface ProgressBarProps {
  progress: number
  label?: string
  className?: string
}

export function ProgressBar({ progress, label, className = '' }: ProgressBarProps) {
  return (
    <div className={`w-full ${className}`}>
      {label && <div className="text-sm font-medium text-gray-700 mb-2">{label}</div>}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        ></div>
      </div>
      <div className="text-xs text-gray-500 mt-1">{Math.round(progress)}% complete</div>
    </div>
  )
}
