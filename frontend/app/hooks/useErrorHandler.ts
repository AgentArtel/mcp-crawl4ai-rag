'use client'

import { useCallback } from 'react'
import { useToast } from '../components/Toast'

export interface ErrorHandlerOptions {
  showToast?: boolean
  logError?: boolean
  fallbackMessage?: string
}

export function useErrorHandler() {
  const { error: showErrorToast, warning: showWarningToast } = useToast()

  const handleError = useCallback((
    error: Error | string,
    context?: string,
    options: ErrorHandlerOptions = {}
  ) => {
    const {
      showToast = true,
      logError = true,
      fallbackMessage = 'An unexpected error occurred'
    } = options

    const errorMessage = typeof error === 'string' ? error : error.message
    const errorTitle = context || 'Error'

    // Log error for debugging
    if (logError) {
      console.error(`[${errorTitle}]`, error)
      
      // In production, send to error monitoring service
      if (process.env.NODE_ENV === 'production') {
        // logErrorToService(error, context)
      }
    }

    // Show user-friendly toast notification
    if (showToast) {
      showErrorToast(
        errorTitle,
        errorMessage || fallbackMessage
      )
    }

    return errorMessage
  }, [showErrorToast])

  const handleNetworkError = useCallback((
    error: Error,
    context?: string
  ) => {
    const isNetworkError = 
      error.message.includes('fetch') ||
      error.message.includes('network') ||
      error.message.includes('Failed to fetch')

    if (isNetworkError) {
      return handleError(
        'Unable to connect to the server. Please check your internet connection.',
        context || 'Network Error',
        { fallbackMessage: 'Connection failed' }
      )
    }

    return handleError(error, context)
  }, [handleError])

  const handleMCPError = useCallback((
    error: Error,
    toolName?: string
  ) => {
    const context = toolName ? `MCP Tool: ${toolName}` : 'MCP Server'
    
    // Check for specific MCP error types
    if (error.message.includes('timeout')) {
      return handleError(
        'The operation timed out. Please try again.',
        context,
        { fallbackMessage: 'Request timeout' }
      )
    }

    if (error.message.includes('unauthorized') || error.message.includes('403')) {
      return handleError(
        'Access denied. Please check your permissions.',
        context,
        { fallbackMessage: 'Authorization error' }
      )
    }

    if (error.message.includes('rate limit')) {
      return handleError(
        'Too many requests. Please wait a moment and try again.',
        context,
        { fallbackMessage: 'Rate limit exceeded' }
      )
    }

    return handleNetworkError(error, context)
  }, [handleNetworkError])

  const handleValidationError = useCallback((
    errors: Record<string, string[]> | string,
    context = 'Validation Error'
  ) => {
    if (typeof errors === 'string') {
      showWarningToast(context, errors)
      return
    }

    // Handle multiple validation errors
    const errorMessages = Object.entries(errors)
      .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
      .join('\n')

    showWarningToast(context, errorMessages)
  }, [showWarningToast])

  const withErrorHandling = useCallback(<T extends any[], R>(
    fn: (...args: T) => Promise<R>,
    context?: string,
    options?: ErrorHandlerOptions
  ) => {
    return async (...args: T): Promise<R | null> => {
      try {
        return await fn(...args)
      } catch (error) {
        handleError(error as Error, context, options)
        return null
      }
    }
  }, [handleError])

  return {
    handleError,
    handleNetworkError,
    handleMCPError,
    handleValidationError,
    withErrorHandling,
  }
}
