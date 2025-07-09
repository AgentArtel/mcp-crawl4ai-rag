export interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  toolResults?: ToolResult[]
}

export interface ToolResult {
  toolName: string
  result: any
  success: boolean
}

export interface IAPData {
  studentName: string
  studentId: string
  studentEmail?: string
  degreeEmphasis: string
  missionStatement: string
  programGoals: string[]
  concentrationAreas: ConcentrationArea[]
  courseMappings?: { [key: string]: Course[] }
  totalCredits: number
  upperDivisionCredits: number
  completionPercentage: number
}

export interface ConcentrationArea {
  name: string
  courses: Course[]
  credits: number
  upperDivisionCredits: number
}

export interface Course {
  code: string
  title: string
  credits: number
  isUpperDivision: boolean
  prerequisites?: string[]
}

export interface MarketResearch {
  degreeEmphasis: string
  viabilityScore: number
  salaryRange: {
    entry: string
    mid: string
    senior: string
  }
  jobGrowth: string
  keySkills: string[]
}

export interface ChatContextType {
  messages: Message[]
  iapData: IAPData
  isLoading: boolean
  sendMessage: (content: string) => void
}
