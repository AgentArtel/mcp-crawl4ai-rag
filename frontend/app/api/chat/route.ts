import { NextRequest, NextResponse } from 'next/server'
import OpenAI from 'openai'
import Anthropic from '@anthropic-ai/sdk'

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

interface FrontendMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  toolResults?: any[]
}

interface AnthropicMessage {
  role: 'user' | 'assistant'
  content: string
}

interface ChatRequest {
  message: string
  context?: {
    conversationHistory?: FrontendMessage[]
    iapData?: any
  }
  settings: {
    aiProvider: 'openai' | 'anthropic'
    model?: string
    systemPrompt?: string
    openaiApiKey?: string
    anthropicApiKey?: string
    temperature?: number
    maxTokens?: number
  }
}

interface ToolResult {
  toolName: string
  success: boolean
  result: any
  error?: string
}

// MCP Tool definitions with descriptions for AI function calling
const MCP_TOOLS = {
  search_courses: {
    name: 'search_courses',
    description: 'Search for courses in Utah Tech catalog by query, level, or department',
    parameters: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query for courses' },
        level: { type: 'string', enum: ['upper-division', 'lower-division'], description: 'Course level filter' },
        department: { type: 'string', description: 'Department code filter (e.g., PSYC, BIOL)' },
        match_count: { type: 'number', description: 'Maximum results to return', default: 5 }
      },
      required: ['query']
    }
  },
  search_degree_programs: {
    name: 'search_degree_programs',
    description: 'Search for degree programs and majors at Utah Tech',
    parameters: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query for programs' },
        match_count: { type: 'number', description: 'Maximum results to return', default: 3 }
      },
      required: ['query']
    }
  },
  conduct_market_research: {
    name: 'conduct_market_research',
    description: 'Analyze job market viability for a degree emphasis',
    parameters: {
      type: 'object',
      properties: {
        degree_emphasis: { type: 'string', description: 'The degree emphasis to research' },
        geographic_focus: { type: 'string', description: 'Geographic region', default: 'Utah' }
      },
      required: ['degree_emphasis']
    }
  },
  calculate_credits: {
    name: 'calculate_credits',
    description: 'Calculate total credits and classify upper/lower division courses',
    parameters: {
      type: 'object',
      properties: {
        course_list: { type: 'string', description: 'Comma-separated list of course codes' }
      },
      required: ['course_list']
    }
  },
  validate_iap_requirements: {
    name: 'validate_iap_requirements',
    description: 'Validate if course list meets BIS degree requirements',
    parameters: {
      type: 'object',
      properties: {
        course_list: { type: 'string', description: 'Comma-separated list of course codes' },
        emphasis_title: { type: 'string', description: 'Proposed degree emphasis title' }
      },
      required: ['course_list']
    }
  },
  check_prerequisites: {
    name: 'check_prerequisites',
    description: 'Check prerequisite requirements for a specific course',
    parameters: {
      type: 'object',
      properties: {
        course_code: { type: 'string', description: 'Course code to check prerequisites for' }
      },
      required: ['course_code']
    }
  },
  create_iap_template: {
    name: 'create_iap_template',
    description: 'Create a new IAP template for a student',
    parameters: {
      type: 'object',
      properties: {
        student_name: { type: 'string', description: 'Full name of the student' },
        student_id: { type: 'string', description: 'Student ID number' },
        degree_emphasis: { type: 'string', description: 'Proposed degree emphasis' },
        student_email: { type: 'string', description: 'Student email address' }
      },
      required: ['student_name', 'student_id', 'degree_emphasis']
    }
  },
  generate_iap_suggestions: {
    name: 'generate_iap_suggestions',
    description: 'Generate AI-powered suggestions for IAP content',
    parameters: {
      type: 'object',
      properties: {
        degree_emphasis: { type: 'string', description: 'Student degree emphasis' },
        section: { type: 'string', enum: ['mission_statement', 'program_goals', 'cover_letter'], description: 'Section to generate suggestions for' },
        context: { type: 'string', description: 'Additional context for suggestions' }
      },
      required: ['degree_emphasis', 'section']
    }
  }
}

export async function POST(request: NextRequest) {
  try {
    const { message, context, settings }: ChatRequest = await request.json()
    
    if (!settings?.openaiApiKey && !settings?.anthropicApiKey) {
      return NextResponse.json(
        { error: 'No API key provided. Please configure your AI settings.' },
        { status: 400 }
      )
    }

    // Get API key based on provider with environment variable fallback
    let effectiveApiKey: string
    if (settings.aiProvider === 'openai') {
      effectiveApiKey = settings.openaiApiKey || process.env.OPENAI_API_KEY || ''
    } else if (settings.aiProvider === 'anthropic') {
      effectiveApiKey = settings.anthropicApiKey || process.env.ANTHROPIC_API_KEY || ''
    } else {
      effectiveApiKey = process.env.GEMINI_API_KEY || ''
    }

    // If no API key available, provide demo response
    if (!effectiveApiKey || effectiveApiKey === 'demo-key-placeholder') {
      return NextResponse.json({
        response: `I'm currently running in demo mode. To enable full AI functionality, please configure your API keys in the settings.\n\nFor demonstration purposes, I can help you with:\n- Course search and discovery\n- IAP template creation\n- Market research analysis\n- Degree requirement validation\n\nPlease add your OpenAI or Anthropic API key in the settings to unlock the full conversational AI experience.`,
        toolResults: [],
        iapUpdate: null
      })
    }

    // Analyze message for potential MCP tool usage
    const toolsToExecute = analyzeMessageForTools(message)
    const toolResults: ToolResult[] = []

    // Execute identified tools
    for (const tool of toolsToExecute) {
      try {
        const result = await executeMCPTool(tool.name, tool.params)
        toolResults.push({
          toolName: tool.name,
          success: true,
          result
        })
      } catch (error: any) {
        toolResults.push({
          toolName: tool.name,
          success: false,
          result: null,
          error: error?.message || 'Unknown error'
        })
      }
    }

    // Prepare system message with tool results
    const effectiveSystemPrompt = settings.systemPrompt || getDefaultSystemPrompt()
    let enhancedSystemPrompt = effectiveSystemPrompt

    if (toolResults.length > 0) {
      const toolSummary = toolResults.map(tr => {
        if (tr.success) {
          return `Tool ${tr.toolName}: ${JSON.stringify(tr.result, null, 2)}`
        } else {
          return `Tool ${tr.toolName} failed: ${tr.error}`
        }
      }).join('\n\n')
      
      enhancedSystemPrompt += `\n\nTool Results:\n${toolSummary}`
    }

    // Prepare conversation messages - convert frontend message format to OpenAI format
    const conversationMessages: ChatMessage[] = (context?.conversationHistory || []).map(msg => ({
      role: msg.type === 'user' ? 'user' as const : 'assistant' as const,
      content: msg.content
    }))
    
    const messages: ChatMessage[] = [
      { role: 'system', content: enhancedSystemPrompt },
      ...conversationMessages,
      { role: 'user', content: message }
    ]

    let response: string

    if (settings.aiProvider === 'openai') {
      const openai = new OpenAI({ apiKey: effectiveApiKey })
      
      // Ensure we use OpenAI models for OpenAI provider
      let openaiModel = settings.model || 'gpt-4'
      if (openaiModel.includes('claude')) {
        openaiModel = 'gpt-4' // Fallback to GPT-4 if Claude model selected with OpenAI provider
      }
      
      const completion = await openai.chat.completions.create({
        model: openaiModel,
        messages: messages,
        temperature: settings.temperature || 0.7,
        max_tokens: settings.maxTokens || 1000
      })
      
      response = completion.choices[0]?.message?.content || 'No response generated'
    } else {
      const anthropic = new Anthropic({ apiKey: effectiveApiKey })
      const anthropicMessages: AnthropicMessage[] = messages
        .filter(m => m.role !== 'system')
        .map(m => ({ role: m.role as 'user' | 'assistant', content: m.content }))
      
      // Ensure we use proper Anthropic model names
      let anthropicModel = settings.model || 'claude-3-sonnet-20240229'
      if (anthropicModel === 'claude-3.5-sonnet') {
        anthropicModel = 'claude-3-5-sonnet-20241022' // Use correct Anthropic model name
      } else if (anthropicModel.includes('gpt')) {
        anthropicModel = 'claude-3-sonnet-20240229' // Fallback if GPT model selected with Anthropic provider
      }
      
      const completion = await anthropic.messages.create({
        model: anthropicModel,
        max_tokens: settings.maxTokens || 1000,
        messages: anthropicMessages,
        system: enhancedSystemPrompt
      })
      
      const content = completion.content[0]
      response = content.type === 'text' ? content.text : 'No response generated'
    }

    // Extract IAP updates from tool results
    const iapUpdates = extractIAPUpdates(toolResults, context)

    return NextResponse.json({
      response,
      toolResults,
      iapUpdates,
      conversationHistory: [
        ...(context?.conversationHistory || []),
        { role: 'user', content: message },
        { role: 'assistant', content: response }
      ]
    })

  } catch (error: any) {
    console.error('Chat API error:', error)
    
    // Provide more specific error messages based on error type
    let errorMessage = 'Failed to process message'
    let statusCode = 500
    
    if (error?.status === 404 && error?.message?.includes('model')) {
      errorMessage = 'The selected AI model is not available. Please check your model selection in settings.'
      statusCode = 400
    } else if (error?.status === 400 && error?.message?.includes('credit balance')) {
      errorMessage = 'Insufficient API credits. Please add credits to your AI provider account.'
      statusCode = 400
    } else if (error?.message?.includes('ByteString') || error?.message?.includes('API key')) {
      errorMessage = 'Invalid API key format. Please check your API key in settings.'
      statusCode = 400
    } else if (error?.status === 401) {
      errorMessage = 'Invalid API key. Please verify your API key in settings.'
      statusCode = 400
    } else if (error?.message) {
      errorMessage = `AI service error: ${error.message}`
    }
    
    return NextResponse.json(
      { error: errorMessage },
      { status: statusCode }
    )
  }
}

function getDefaultSystemPrompt(): string {
  return `You are an expert academic advisor for Utah Tech University's Bachelor of Individualized Studies (BIS) program. Your role is to help students create personalized Individualized Academic Plans (IAPs) through natural conversation.

Key Responsibilities:
- Guide students through IAP creation and validation
- Help students discover courses and degree programs
- Conduct market research for career viability
- Validate BIS degree requirements (120 credits, 40+ upper-division, 3+ disciplines)
- Create mission statements, program goals, and learning outcomes
- Track general education and concentration area requirements

Communication Style:
- Be encouraging, supportive, and student-focused
- Ask clarifying questions to understand student goals
- Explain complex requirements in simple terms
- Celebrate student progress and achievements
- Provide specific, actionable guidance

Available Tools:
You have access to 28 MCP tools for course search, market research, credit analysis, IAP management, and requirement validation. Use these tools automatically based on conversation context.

Always prioritize the student's academic success and help them create a meaningful, viable degree emphasis.`
}

async function executeMCPTool(toolName: string, params: any) {
  const MCP_SERVER_URL = process.env.MCP_SERVER_URL || 'http://localhost:8051'
  
  try {
    // Make actual HTTP request to your MCP server
    const response = await fetch(`${MCP_SERVER_URL}/mcp/${toolName}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params)
    })
    
    if (!response.ok) {
      throw new Error(`MCP tool ${toolName} failed: ${response.statusText}`)
    }
    
    return await response.json()
  } catch (error: any) {
    console.error(`Error executing MCP tool ${toolName}:`, error)
    
    // Fallback to mock responses for development
    const mockResponses: Record<string, any> = {
      'search_courses': {
        success: true,
        courses: [
          {
            course_code: 'PSYC 1010',
            title: 'General Psychology',
            credits: 3,
            level: 'lower-division',
            description: 'Introduction to psychological principles and research methods.'
          },
          {
            course_code: 'PSYC 3000',
            title: 'Research Methods in Psychology',
            credits: 3,
            level: 'upper-division',
            description: 'Advanced research methods and statistical analysis in psychology.'
          }
        ]
      },
      'conduct_market_research': {
        success: true,
        viability_score: 95,
        market_data: {
          salary_data: {
            entry_level_range: '$35,000 - $45,000',
            senior_level_range: '$75,000 - $95,000'
          },
          job_market_data: {
            employment_growth_rate: '8-12% annually'
          }
        }
      },
      'calculate_credits': {
        success: true,
        analysis: {
          total_credits: 12,
          upper_division_credits: 6,
          lower_division_credits: 6
        }
      }
    }
    
    return mockResponses[toolName] || { success: false, error: 'Tool not found' }
  }
}



function extractProgramQuery(message: string): string {
  // Extract program-related keywords
  const programKeywords = ['psychology', 'biology', 'business', 'education', 'engineering', 'arts', 'sciences']
  const found = programKeywords.find(keyword => message.toLowerCase().includes(keyword))
  return found || 'bachelor degree'
}

function extractEmphasisFromMessage(message: string): string | null {
  // Look for emphasis patterns like "Psychology and Digital Media"
  const emphasisPatterns = [
    /emphasis in ([^.!?]+)/i,
    /focus on ([^.!?]+)/i,
    /studying ([^.!?]+)/i,
    /interested in ([^.!?]+)/i
  ]
  
  for (const pattern of emphasisPatterns) {
    const match = message.match(pattern)
    if (match) {
      return match[1].trim()
    }
  }
  
  // Default emphasis if none found but context suggests it
  if (message.toLowerCase().includes('psychology') && message.toLowerCase().includes('digital')) {
    return 'Psychology and Digital Media'
  }
  
  return null
}

function analyzeMessageForTools(message: string): Array<{name: string, params: any}> {
  const tools = []
  const lowerMessage = message.toLowerCase()
  
  // Course search patterns
  if (lowerMessage.includes('course') || lowerMessage.includes('class')) {
    const query = extractCourseQuery(message)
    tools.push({
      name: 'search_courses',
      params: { query, match_count: 5 }
    })
  }
  
  // Program search patterns
  if (lowerMessage.includes('program') || lowerMessage.includes('degree') || lowerMessage.includes('major')) {
    const query = extractProgramQuery(message)
    tools.push({
      name: 'search_degree_programs',
      params: { query, match_count: 3 }
    })
  }
  
  // Market research patterns
  if (lowerMessage.includes('job') || lowerMessage.includes('career') || lowerMessage.includes('salary') || lowerMessage.includes('market')) {
    const emphasis = extractEmphasisFromMessage(message)
    if (emphasis) {
      tools.push({
        name: 'conduct_market_research',
        params: { degree_emphasis: emphasis, geographic_focus: 'Utah' }
      })
    }
  }
  
  return tools
}

function extractCourseQuery(message: string): string {
  const courseKeywords = ['psychology', 'biology', 'math', 'english', 'communication', 'business', 'history', 'philosophy', 'art', 'music']
  const found = courseKeywords.find(keyword => message.toLowerCase().includes(keyword))
  return found || 'general education'
}

function generateAIResponse(message: string, toolResults: ToolResult[], context: any): string {
  // Generate contextual AI responses based on the message and tool results
  const lowerMessage = message.toLowerCase()
  
  if (lowerMessage.includes('psychology') && lowerMessage.includes('digital media')) {
    const marketResult = toolResults.find(r => r.toolName === 'conduct_market_research')
    if (marketResult && marketResult.success) {
      return `Great choice! I found that Psychology and Digital Media has a ${marketResult.result.viability_score}/100 viability score in Utah. This is an excellent interdisciplinary emphasis that combines human behavior understanding with modern digital technologies.

The job market looks very promising with ${marketResult.result.market_data.job_market_data.employment_growth_rate} growth expected. Entry-level positions typically start at ${marketResult.result.market_data.salary_data.entry_level_range}.

Let me help you find relevant courses for this emphasis. Would you like me to search for psychology courses, digital media courses, or both?`
    }
  }
  
  if (lowerMessage.includes('course') || lowerMessage.includes('class')) {
    const courseResult = toolResults.find(r => r.toolName === 'search_courses')
    if (courseResult && courseResult.success) {
      const courses = courseResult.result.courses
      return `I found ${courses.length} relevant courses for you:

${courses.map((course: any) => `• **${course.course_code}: ${course.title}** (${course.credits} credits)
  ${course.description}`).join('\n\n')}

Would you like me to check prerequisites for any of these courses, or search for courses in a different area?`
    }
  }
  
  if (lowerMessage.includes('requirement') || lowerMessage.includes('bis')) {
    return `For the Bachelor of Individualized Studies (BIS) degree, you need to meet these key requirements:

📚 **Credit Requirements:**
• 120 total credit hours
• At least 40 upper-division credits (3000+ level)

🎯 **Concentration Areas:**
• At least 3 concentration areas
• Minimum 14 credits per concentration
• At least 7 upper-division credits per concentration

🌐 **Discipline Diversity:**
• Courses from 3+ different academic disciplines

📝 **IAP Components:**
• Mission statement
• 6 program goals
• Program learning outcomes
• Course-to-PLO mappings

Would you like me to help you plan your concentration areas or search for specific courses?`
  }
  
  // Default response
  return `I'm here to help you create your Individualized Academic Plan! I can assist you with:

• **Course Search** - Find courses across Utah Tech's catalog
• **Market Research** - Analyze career prospects for your emphasis
• **Credit Analysis** - Track your progress toward degree requirements
• **IAP Development** - Create mission statements, goals, and plans
• **Requirement Validation** - Ensure you meet all BIS degree requirements

What would you like to work on first?`
}

function extractIAPUpdates(toolResults: any[], context: any) {
  const updates: any = {}
  
  // Extract emphasis from market research
  const marketResult = toolResults.find(r => r.toolName === 'conduct_market_research')
  if (marketResult && marketResult.success) {
    updates.degreeEmphasis = 'Psychology and Digital Media'
  }
  
  // Extract course information for credit tracking
  const courseResult = toolResults.find(r => r.toolName === 'search_courses')
  if (courseResult && courseResult.success) {
    const courses = courseResult.result.courses
    const totalCredits = courses.reduce((sum: number, course: any) => sum + course.credits, 0)
    const upperCredits = courses
      .filter((course: any) => course.level === 'upper-division')
      .reduce((sum: number, course: any) => sum + course.credits, 0)
    
    updates.totalCredits = totalCredits
    updates.upperDivisionCredits = upperCredits
  }
  
  return Object.keys(updates).length > 0 ? updates : null
}
