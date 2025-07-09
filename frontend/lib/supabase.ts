import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database Types
export interface StudentProfile {
  id: string
  student_name: string
  student_id: string
  student_email: string
  degree_emphasis: string
  transcript_uploaded: boolean
  transcript_file_url?: string
  transcript_parsed_data?: any
  onboarding_completed: boolean
  onboarding_step: number
  degree_audit_data?: any
  transfer_credits?: any
  academic_standing?: string
  expected_graduation?: string
  created_at: string
  updated_at: string
}

export interface StudentDocument {
  id: string
  student_id: string
  document_type: 'transcript' | 'degree_audit' | 'transfer_credit' | 'other'
  file_name: string
  file_url: string
  file_size?: number
  mime_type?: string
  parsed_data?: any
  parsing_status: 'pending' | 'processing' | 'completed' | 'failed'
  parsing_errors?: string[]
  uploaded_at: string
  processed_at?: string
  created_at: string
  updated_at: string
}

export interface StudentCourseHistory {
  id: string
  student_id: string
  course_code: string
  course_title?: string
  credits?: number
  grade?: string
  grade_points?: number
  semester?: string
  year?: number
  institution: string
  transfer_credit: boolean
  status: 'completed' | 'in_progress' | 'planned' | 'dropped' | 'withdrawn'
  notes?: string
  created_at: string
  updated_at: string
}

export interface StudentGraphPreferences {
  id: string
  student_id: string
  layout_type: 'force-directed' | 'hierarchical' | 'circular' | 'tree'
  show_prerequisites: boolean
  show_corequisites: boolean
  highlight_completed: boolean
  highlight_in_progress: boolean
  color_scheme: 'default' | 'colorblind' | 'high-contrast' | 'dark'
  zoom_level: number
  center_node?: string
  hidden_nodes?: string[]
  custom_positions?: any
  filter_by_discipline?: string[]
  show_credit_hours: boolean
  created_at: string
  updated_at: string
}

export interface AcademicCourse {
  id: string
  course_code: string
  course_title: string
  course_description?: string
  credits: number
  department: string
  level: string
  prerequisites?: string[]
  corequisites?: string[]
  offered_semesters?: string[]
  source_id: string
  created_at: string
  updated_at: string
}

// Student Profile Operations
export const studentProfileService = {
  async getProfile(studentId: string): Promise<StudentProfile | null> {
    const { data, error } = await supabase
      .from('student_profiles')
      .select('*')
      .eq('id', studentId)
      .single()
    
    if (error) {
      console.error('Error fetching student profile:', error)
      return null
    }
    
    return data
  },

  async updateProfile(studentId: string, updates: Partial<StudentProfile>): Promise<boolean> {
    const { error } = await supabase
      .from('student_profiles')
      .update(updates)
      .eq('id', studentId)
    
    if (error) {
      console.error('Error updating student profile:', error)
      return false
    }
    
    return true
  },

  async createProfile(profile: Omit<StudentProfile, 'id' | 'created_at' | 'updated_at'>): Promise<StudentProfile | null> {
    const { data, error } = await supabase
      .from('student_profiles')
      .insert(profile)
      .select()
      .single()
    
    if (error) {
      console.error('Error creating student profile:', error)
      return null
    }
    
    return data
  }
}

// Document Operations
export const documentService = {
  async uploadDocument(file: File, studentId: string, documentType: StudentDocument['document_type']): Promise<string | null> {
    const fileName = `${studentId}/${documentType}/${Date.now()}_${file.name}`
    
    const { data, error } = await supabase.storage
      .from('student-documents')
      .upload(fileName, file)
    
    if (error) {
      console.error('Error uploading document:', error)
      return null
    }
    
    return data.path
  },

  async createDocumentRecord(document: Omit<StudentDocument, 'id' | 'created_at' | 'updated_at'>): Promise<StudentDocument | null> {
    const { data, error } = await supabase
      .from('student_documents')
      .insert(document)
      .select()
      .single()
    
    if (error) {
      console.error('Error creating document record:', error)
      return null
    }
    
    return data
  },

  async getStudentDocuments(studentId: string): Promise<StudentDocument[]> {
    const { data, error } = await supabase
      .from('student_documents')
      .select('*')
      .eq('student_id', studentId)
      .order('uploaded_at', { ascending: false })
    
    if (error) {
      console.error('Error fetching student documents:', error)
      return []
    }
    
    return data || []
  },

  async updateDocumentStatus(documentId: string, status: StudentDocument['parsing_status'], parsedData?: any, errors?: string[]): Promise<boolean> {
    const updates: any = { 
      parsing_status: status,
      processed_at: new Date().toISOString()
    }
    
    if (parsedData) updates.parsed_data = parsedData
    if (errors) updates.parsing_errors = errors
    
    const { error } = await supabase
      .from('student_documents')
      .update(updates)
      .eq('id', documentId)
    
    if (error) {
      console.error('Error updating document status:', error)
      return false
    }
    
    return true
  }
}

// Course History Operations
export const courseHistoryService = {
  async getStudentCourses(studentId: string): Promise<StudentCourseHistory[]> {
    const { data, error } = await supabase
      .from('student_course_history')
      .select('*')
      .eq('student_id', studentId)
      .order('year', { ascending: false })
      .order('semester', { ascending: false })
    
    if (error) {
      console.error('Error fetching course history:', error)
      return []
    }
    
    return data || []
  },

  async addCourse(course: Omit<StudentCourseHistory, 'id' | 'created_at' | 'updated_at'>): Promise<StudentCourseHistory | null> {
    const { data, error } = await supabase
      .from('student_course_history')
      .insert(course)
      .select()
      .single()
    
    if (error) {
      console.error('Error adding course:', error)
      return null
    }
    
    return data
  },

  async updateCourse(courseId: string, updates: Partial<StudentCourseHistory>): Promise<boolean> {
    const { error } = await supabase
      .from('student_course_history')
      .update(updates)
      .eq('id', courseId)
    
    if (error) {
      console.error('Error updating course:', error)
      return false
    }
    
    return true
  },

  async deleteCourse(courseId: string): Promise<boolean> {
    const { error } = await supabase
      .from('student_course_history')
      .delete()
      .eq('id', courseId)
    
    if (error) {
      console.error('Error deleting course:', error)
      return false
    }
    
    return true
  },

  async bulkAddCourses(courses: Omit<StudentCourseHistory, 'id' | 'created_at' | 'updated_at'>[]): Promise<StudentCourseHistory[]> {
    const { data, error } = await supabase
      .from('student_course_history')
      .insert(courses)
      .select()
    
    if (error) {
      console.error('Error bulk adding courses:', error)
      return []
    }
    
    return data || []
  }
}

// Graph Preferences Operations
export const graphPreferencesService = {
  async getPreferences(studentId: string): Promise<StudentGraphPreferences | null> {
    const { data, error } = await supabase
      .from('student_graph_preferences')
      .select('*')
      .eq('student_id', studentId)
      .single()
    
    if (error && error.code !== 'PGRST116') { // PGRST116 = no rows returned
      console.error('Error fetching graph preferences:', error)
      return null
    }
    
    return data
  },

  async updatePreferences(studentId: string, preferences: Partial<StudentGraphPreferences>): Promise<boolean> {
    const { error } = await supabase
      .from('student_graph_preferences')
      .upsert({ student_id: studentId, ...preferences })
    
    if (error) {
      console.error('Error updating graph preferences:', error)
      return false
    }
    
    return true
  }
}

// Academic Course Search
export const academicCourseService = {
  async searchCourses(query: string, limit: number = 10): Promise<AcademicCourse[]> {
    const { data, error } = await supabase
      .from('academic_courses')
      .select('*')
      .or(`course_code.ilike.%${query}%,course_title.ilike.%${query}%,course_description.ilike.%${query}%`)
      .limit(limit)
    
    if (error) {
      console.error('Error searching courses:', error)
      return []
    }
    
    return data || []
  },

  async getCourseByCode(courseCode: string): Promise<AcademicCourse | null> {
    const { data, error } = await supabase
      .from('academic_courses')
      .select('*')
      .eq('course_code', courseCode)
      .single()
    
    if (error) {
      console.error('Error fetching course:', error)
      return null
    }
    
    return data
  },

  async getCoursesByDepartment(department: string): Promise<AcademicCourse[]> {
    const { data, error } = await supabase
      .from('academic_courses')
      .select('*')
      .eq('department', department)
      .order('course_code')
    
    if (error) {
      console.error('Error fetching courses by department:', error)
      return []
    }
    
    return data || []
  }
}

// Real-time subscriptions
export const subscriptions = {
  subscribeToProfile(studentId: string, callback: (profile: StudentProfile) => void) {
    return supabase
      .channel(`profile-${studentId}`)
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: 'student_profiles',
          filter: `id=eq.${studentId}`
        }, 
        (payload: any) => {
          if (payload.new) {
            callback(payload.new as StudentProfile)
          }
        }
      )
      .subscribe()
  },

  subscribeToCourseHistory(studentId: string, callback: (courses: StudentCourseHistory[]) => void) {
    return supabase
      .channel(`courses-${studentId}`)
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: 'student_course_history',
          filter: `student_id=eq.${studentId}`
        }, 
        async () => {
          // Refetch all courses when any change occurs
          const courses = await courseHistoryService.getStudentCourses(studentId)
          callback(courses)
        }
      )
      .subscribe()
  }
}

// Authentication helpers
export const auth = {
  async signUp(email: string, password: string, metadata?: any) {
    return await supabase.auth.signUp({
      email,
      password,
      options: {
        data: metadata
      }
    })
  },

  async signIn(email: string, password: string) {
    return await supabase.auth.signInWithPassword({
      email,
      password
    })
  },

  async signOut() {
    return await supabase.auth.signOut()
  },

  async getCurrentUser() {
    const { data: { user } } = await supabase.auth.getUser()
    return user
  },

  onAuthStateChange(callback: (event: string, session: any) => void) {
    return supabase.auth.onAuthStateChange(callback)
  }
}
