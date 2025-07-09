'use client'

import { Bot, User, CheckCircle, AlertCircle, BarChart3, BookOpen } from 'lucide-react'
import { Message } from '../types'
import { format } from 'date-fns'

interface MessageBubbleProps {
  message: Message
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.type === 'user'

  return (
    <div className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`p-2 rounded-full ${isUser ? 'bg-blue-500' : 'bg-utah-red'}`}>
        {isUser ? (
          <User className="h-4 w-4 text-white" />
        ) : (
          <Bot className="h-4 w-4 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={`max-w-xs lg:max-w-md ${isUser ? 'text-right' : ''}`}>
        <div
          className={`rounded-lg px-4 py-2 ${
            isUser
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Tool Results */}
        {message.toolResults && message.toolResults.length > 0 && (
          <div className="mt-2 space-y-2">
            {message.toolResults.map((result, index) => (
              <div
                key={index}
                className="bg-white border border-gray-200 rounded-lg p-3 text-sm"
              >
                <div className="flex items-center space-x-2 mb-2">
                  {result.success ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-red-500" />
                  )}
                  <span className="font-medium text-gray-700">
                    {getToolDisplayName(result.toolName)}
                  </span>
                </div>
                
                {renderToolResult(result)}
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <p className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : ''}`}>
          {format(message.timestamp, 'h:mm a')}
        </p>
      </div>
    </div>
  )
}

function getToolDisplayName(toolName: string): string {
  const displayNames: { [key: string]: string } = {
    'search_courses': 'Course Search',
    'calculate_credits': 'Credit Analysis',
    'conduct_market_research': 'Market Research',
    'validate_iap_requirements': 'IAP Validation',
    'generate_iap_suggestions': 'AI Suggestions',
    'analyze_disciplines': 'Discipline Analysis',
    'check_prerequisites': 'Prerequisites Check',
  }
  return displayNames[toolName] || toolName
}

function renderToolResult(result: any) {
  if (!result.success) {
    return (
      <p className="text-red-600 text-xs">
        Error: {result.result?.error || 'Tool execution failed'}
      </p>
    )
  }

  const data = result.result

  // Handle different tool result types
  if (result.toolName === 'search_courses' && data.courses) {
    return (
      <div className="space-y-2">
        <p className="font-medium text-gray-700">Found {data.courses.length} courses:</p>
        {data.courses.slice(0, 3).map((course: any, idx: number) => (
          <div key={idx} className="bg-gray-50 p-2 rounded text-xs">
            <p className="font-medium">{course.course_code}: {course.title}</p>
            <p className="text-gray-600">{course.credits} credits • {course.level}</p>
          </div>
        ))}
      </div>
    )
  }

  if (result.toolName === 'conduct_market_research' && data.market_data) {
    return (
      <div className="space-y-2">
        <div className="flex items-center space-x-2">
          <BarChart3 className="h-4 w-4 text-green-500" />
          <p className="font-medium text-gray-700">
            Viability Score: {data.viability_score}/100
          </p>
        </div>
        <p className="text-xs text-gray-600">
          Salary Range: {data.market_data.salary_data.entry_level_range} - {data.market_data.salary_data.senior_level_range}
        </p>
        <p className="text-xs text-gray-600">
          Job Growth: {data.market_data.job_market_data.employment_growth_rate}
        </p>
      </div>
    )
  }

  if (result.toolName === 'calculate_credits' && data.analysis) {
    return (
      <div className="space-y-1">
        <p className="text-xs">
          <span className="font-medium">Total Credits:</span> {data.analysis.total_credits}
        </p>
        <p className="text-xs">
          <span className="font-medium">Upper Division:</span> {data.analysis.upper_division_credits}
        </p>
        <p className="text-xs">
          <span className="font-medium">Lower Division:</span> {data.analysis.lower_division_credits}
        </p>
      </div>
    )
  }

  // Default rendering for other tools
  return (
    <div className="text-xs text-gray-600">
      <BookOpen className="h-4 w-4 inline mr-1" />
      Tool executed successfully
    </div>
  )
}
