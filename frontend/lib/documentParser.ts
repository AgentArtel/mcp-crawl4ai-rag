import { supabase } from './supabase';
import { toast } from 'react-hot-toast';

export interface Course {
  course_code: string;
  course_title: string;
  credits: number;
  grade: string;
  grade_points: number;
  semester: string;
  year: number;
  institution: string;
  transfer_credit: boolean;
  status: 'completed' | 'in_progress' | 'withdrawn' | 'failed' | 'transfer';
  category?: string;
  notes?: string;
}

export interface StudentInfo {
  name: string;
  student_id: string;
  institution: string;
  program: string;
  major: string;
  concentrations: string[];
  college: string;
  classification: string;
  overall_gpa: number;
  total_credits_earned: number;
  total_credits_required: number;
  upper_division_earned: number;
  upper_division_required: number;
}

export interface DegreeInfo {
  degree_type: string;
  major: string;
  catalog_year: string;
  graduation_date?: string;
}

export interface GeneralEducationCategory {
  required: number;
  completed: number;
  status: 'COMPLETE' | 'NEEDED' | 'IN_PROGRESS';
  options?: string[];
}

export interface GeneralEducation {
  overall_gpa: number;
  status: 'COMPLETE' | 'INCOMPLETE';
  categories: {
    [key: string]: GeneralEducationCategory;
  };
}

export interface CoreCourse {
  title: string;
  credits: number;
  status: 'completed' | 'in_progress' | 'needed';
}

export interface Competency {
  status: 'completed' | 'needed';
  options: string[];
}

export interface MajorRequirements {
  status: 'COMPLETE' | 'INCOMPLETE';
  core_courses: {
    [courseCode: string]: CoreCourse;
  };
  competencies: {
    [competencyName: string]: Competency;
  };
}

export interface ParsedTranscript {
  student_info: StudentInfo;
  courses: Course[];
  degree_info: DegreeInfo;
  general_education: GeneralEducation;
  major_requirements: MajorRequirements;
  parsing_confidence: number;
  parsing_notes: string[];
}

export class DocumentParser {
  private static readonly OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';
  
  /**
   * Parse a PDF transcript using AI
   */
  static async parseTranscript(
    documentId: string,
    fileUrl: string,
    apiKey?: string
  ): Promise<ParsedTranscript> {
    try {
      // Update parsing status
      await supabase
        .from('student_documents')
        .update({ 
          parsing_status: 'processing',
          processed_at: new Date().toISOString()
        })
        .eq('id', documentId);

      // Extract text from PDF (simplified - in production, use proper PDF parsing)
      const pdfText = await this.extractTextFromPDF(fileUrl);
      
      // Use AI to parse the transcript
      const parsedData = await this.parseWithAI(pdfText, apiKey);
      
      // Save parsed data to database
      await supabase
        .from('student_documents')
        .update({
          parsed_data: parsedData,
          parsing_status: 'completed',
          processed_at: new Date().toISOString()
        })
        .eq('id', documentId);

      // Save individual courses to course history
      if (parsedData.courses.length > 0) {
        const { data: profile } = await supabase
          .from('student_profiles')
          .select('id')
          .eq('auth_user_id', (await supabase.auth.getUser()).data.user?.id)
          .single();

        if (profile) {
          const courseRecords = parsedData.courses.map(course => ({
            student_id: profile.id,
            ...course
          }));

          await supabase
            .from('student_course_history')
            .insert(courseRecords);
        }
      }

      return parsedData;
    } catch (error) {
      console.error('Transcript parsing error:', error);
      
      // Update parsing status to failed
      await supabase
        .from('student_documents')
        .update({
          parsing_status: 'failed',
          parsing_errors: [error instanceof Error ? error.message : 'Unknown error'],
          processed_at: new Date().toISOString()
        })
        .eq('id', documentId);

      throw error;
    }
  }

  /**
   * Extract text from PDF (simplified implementation)
   * In production, use a proper PDF parsing library like pdf-parse or PDF.js
   */
  private static async extractTextFromPDF(fileUrl: string): Promise<string> {
    try {
      // For now, return a mock response
      // In production, implement actual PDF text extraction
      return `
        UTAH TECH UNIVERSITY
        OFFICIAL TRANSCRIPT
        
        Student: John Doe
        Student ID: 00123456
        
        FALL 2022
        PSYC 1010    General Psychology         3.0    A    4.0
        MATH 1050    College Algebra           4.0    B+   3.3
        ENGL 1010    Introduction to Writing   3.0    A-   3.7
        
        SPRING 2023
        PSYC 2000    Research Methods          3.0    B    3.0
        BIOL 1610    Biology I                 4.0    A    4.0
        HIST 1700    American History          3.0    B+   3.3
        
        Cumulative GPA: 3.55
        Total Credits: 20.0
      `;
    } catch (error) {
      console.error('PDF text extraction error:', error);
      throw new Error('Failed to extract text from PDF');
    }
  }

  /**
   * Parse Utah Tech degree audit/transcript using AI
   */
  private static async parseWithAI(
    transcriptText: string,
    apiKey?: string
  ): Promise<ParsedTranscript> {
    const prompt = `
You are an expert Utah Tech University degree audit parser. Parse the following degree audit and extract structured academic data.

UTAH TECH DEGREE AUDIT:
${transcriptText}

Extract and return a JSON object with this exact structure:
{
  "student_info": {
    "name": "Last, First Middle",
    "student_id": "string",
    "institution": "Utah Tech University",
    "program": "BIS - Individualized Studies",
    "major": "Individualized Studies",
    "concentrations": ["Art", "Computer Science", "Philosophy"],
    "college": "College of Education",
    "classification": "Junior/Senior/etc",
    "overall_gpa": 2.56,
    "total_credits_earned": 92,
    "total_credits_required": 120,
    "upper_division_earned": 37,
    "upper_division_required": 40
  },
  "courses": [
    {
      "course_code": "ENGL 1010",
      "course_title": "Intro to Writing",
      "credits": 3.0,
      "grade": "TB",
      "grade_points": 3.0,
      "semester": "Spring 2017",
      "year": 2017,
      "institution": "Utah Tech University",
      "transfer_credit": true,
      "status": "completed",
      "category": "General Education - Writing",
      "notes": "Transfer credit from UVU"
    }
  ],
  "general_education": {
    "overall_gpa": 2.90,
    "status": "INCOMPLETE",
    "categories": {
      "writing": { "required": 6, "completed": 6, "status": "COMPLETE" },
      "mathematics": { "required": 3, "completed": 0, "status": "NEEDED", "options": ["MATH 1030", "MATH 1040", "MATH 1050"] },
      "american_institutions": { "required": 3, "completed": 0, "status": "NEEDED", "options": ["ECON 1740", "HIST 1700", "POLS 1100"] }
    }
  },
  "major_requirements": {
    "status": "INCOMPLETE",
    "core_courses": {
      "INDS 3800": { "title": "Individualized Studies Seminar", "credits": 3, "status": "in_progress" },
      "INDS 3805": { "title": "Individualized Studies Lab", "credits": 1, "status": "in_progress" },
      "INDS 4700": { "title": "Portfolio Requirement", "credits": 3, "status": "needed" }
    },
    "competencies": {
      "statistical": { "status": "needed", "options": ["MATH 1040", "SOC 3112", "STAT 2040"] },
      "written": { "status": "needed", "options": ["ENGL 3010", "ENGL 3030", "PSY 2000"] }
    }
  },
  "degree_info": {
    "degree_type": "Bachelor of Individualized Studies",
    "major": "Individualized Studies",
    "catalog_year": "2023-2024",
    "graduation_date": null
  },
  "parsing_confidence": 95,
  "parsing_notes": [
    "Parsed Utah Tech degree audit format",
    "Identified BIS program with multiple concentrations",
    "Transfer credits from Utah Valley University detected",
    "In-progress and withdrawn courses properly categorized"
  ]
}

UTAH TECH SPECIFIC PARSING RULES:
1. Course codes: Standard format (ENGL 1010, ART 3270, PHIL 4800R)
2. Grades: A, A-, B+, B, B-, C+, C, C-, D+, D, F, W (withdrawn)
3. Transfer grades: TB=Transfer B (3.0), TC=Transfer C (2.0), TD=Transfer D (1.0), TC+=Transfer C+ (2.3)
4. Course status: completed, in_progress, withdrawn, failed, transfer
5. Categories: General Education, Major Requirements, Concentration Courses, Transfer Credit, General Electives
6. BIS Program: INDS courses are core requirements, multiple concentrations allowed
7. Credit format: Use decimal notation (3.0, 4.0, 1.0)
8. Upper-division: Courses numbered 3000+ are upper-division
9. Repeat indicator: (R) suffix means repeated course
10. Extract ALL course attempts including withdrawn/failed for complete academic history

IMPORTANT: Return ONLY the JSON object, no markdown formatting or additional text.
`;

    try {
      if (!apiKey) {
        // Fallback: Return mock parsed data for development
        return this.getMockParsedData(transcriptText);
      }

      const response = await fetch(this.OPENAI_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          model: 'gpt-4',
          messages: [
            {
              role: 'system',
              content: 'You are an expert academic transcript parser. Return only valid JSON.'
            },
            {
              role: 'user',
              content: prompt
            }
          ],
          temperature: 0.1,
          max_tokens: 2000
        })
      });

      if (!response.ok) {
        throw new Error(`OpenAI API error: ${response.statusText}`);
      }

      const data = await response.json();
      const parsedContent = data.choices[0]?.message?.content;

      if (!parsedContent) {
        throw new Error('No response from AI parser');
      }

      // Parse the JSON response
      const parsedData = JSON.parse(parsedContent);
      
      // Validate the structure
      this.validateParsedData(parsedData);
      
      return parsedData;
    } catch (error) {
      console.error('AI parsing error:', error);
      
      // Fallback to mock data if AI parsing fails
      toast.error('AI parsing failed, using fallback parser');
      return this.getMockParsedData(transcriptText);
    }
  }

  /**
   * Mock parsed data for development/fallback
   */
  private static getMockParsedData(transcriptText: string): ParsedTranscript {
    return {
      student_info: {
        name: 'John Doe',
        student_id: '00123456',
        institution: 'Utah Tech University',
        program: 'BIS - Individualized Studies',
        major: 'Individualized Studies',
        concentrations: ['Psychology', 'Computer Science'],
        college: 'College of Education',
        classification: 'Junior',
        overall_gpa: 3.55,
        total_credits_earned: 92,
        total_credits_required: 120,
        upper_division_earned: 37,
        upper_division_required: 40
      },
      courses: [
        {
          course_code: 'PSYC 1010',
          course_title: 'General Psychology',
          credits: 3,
          grade: 'A',
          grade_points: 4.0,
          semester: 'Fall 2022',
          year: 2022,
          institution: 'Utah Tech University',
          transfer_credit: false,
          status: 'completed'
        },
        {
          course_code: 'MATH 1050',
          course_title: 'College Algebra',
          credits: 4,
          grade: 'B+',
          grade_points: 3.3,
          semester: 'Fall 2022',
          year: 2022,
          institution: 'Utah Tech University',
          transfer_credit: false,
          status: 'completed'
        },
        {
          course_code: 'ENGL 1010',
          course_title: 'Introduction to Writing',
          credits: 3,
          grade: 'A-',
          grade_points: 3.7,
          semester: 'Fall 2022',
          year: 2022,
          institution: 'Utah Tech University',
          transfer_credit: false,
          status: 'completed'
        },
        {
          course_code: 'PSYC 2000',
          course_title: 'Research Methods',
          credits: 3,
          grade: 'B',
          grade_points: 3.0,
          semester: 'Spring 2023',
          year: 2023,
          institution: 'Utah Tech University',
          transfer_credit: false,
          status: 'completed'
        },
        {
          course_code: 'BIOL 1610',
          course_title: 'Biology I',
          credits: 4,
          grade: 'A',
          grade_points: 4.0,
          semester: 'Spring 2023',
          year: 2023,
          institution: 'Utah Tech University',
          transfer_credit: false,
          status: 'completed'
        },
        {
          course_code: 'HIST 1700',
          course_title: 'American History',
          credits: 3,
          grade: 'B+',
          grade_points: 3.3,
          semester: 'Spring 2023',
          year: 2023,
          institution: 'Utah Tech University',
          transfer_credit: false,
          status: 'completed'
        }
      ],
      general_education: {
        overall_gpa: 2.90,
        status: 'INCOMPLETE',
        categories: {
          writing: { required: 6, completed: 6, status: 'COMPLETE' },
          mathematics: { required: 3, completed: 0, status: 'NEEDED', options: ['MATH 1030', 'MATH 1040'] },
          american_institutions: { required: 3, completed: 3, status: 'COMPLETE' }
        }
      },
      major_requirements: {
        status: 'INCOMPLETE',
        core_courses: {
          'INDS 3800': { title: 'Individualized Studies Seminar', credits: 3, status: 'needed' },
          'INDS 3805': { title: 'Individualized Studies Lab', credits: 1, status: 'needed' },
          'INDS 4700': { title: 'Portfolio Requirement', credits: 3, status: 'needed' }
        },
        competencies: {
          statistical: { status: 'needed', options: ['MATH 1040', 'SOC 3112', 'STAT 2040'] },
          written: { status: 'needed', options: ['ENGL 3010', 'ENGL 3030', 'PSY 2000'] }
        }
      },
      degree_info: {
        degree_type: 'Bachelor of Individualized Studies',
        major: 'Individualized Studies',
        catalog_year: '2023-2024',
        graduation_date: undefined
      },
      parsing_confidence: 85,
      parsing_notes: [
        'Mock data used for development',
        'Actual transcript parsing requires OpenAI API key',
        'All courses marked as completed from Utah Tech University'
      ]
    };
  }

  /**
   * Validate parsed data structure
   */
  private static validateParsedData(data: any): void {
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid parsed data structure');
    }

    if (!data.courses || !Array.isArray(data.courses)) {
      throw new Error('Courses array is required');
    }

    // Validate each course
    for (const course of data.courses) {
      if (!course.course_code || !course.credits) {
        throw new Error('Course code and credits are required for all courses');
      }
    }

    if (typeof data.parsing_confidence !== 'number') {
      data.parsing_confidence = 50; // Default confidence
    }

    if (!Array.isArray(data.parsing_notes)) {
      data.parsing_notes = [];
    }
  }

  /**
   * Get parsing status for a document
   */
  static async getParsingStatus(documentId: string) {
    const { data, error } = await supabase
      .from('student_documents')
      .select('parsing_status, parsed_data, parsing_errors, processed_at')
      .eq('id', documentId)
      .single();

    if (error) {
      throw error;
    }

    return data;
  }

  /**
   * Retry parsing for a failed document
   */
  static async retryParsing(documentId: string, apiKey?: string) {
    const { data: document } = await supabase
      .from('student_documents')
      .select('file_url')
      .eq('id', documentId)
      .single();

    if (!document) {
      throw new Error('Document not found');
    }

    return this.parseTranscript(documentId, document.file_url, apiKey);
  }

  /**
   * Get all parsed courses for a student
   */
  static async getStudentCourseHistory(studentId: string) {
    const { data, error } = await supabase
      .from('student_course_history')
      .select('*')
      .eq('student_id', studentId)
      .order('year', { ascending: false })
      .order('semester');

    if (error) {
      throw error;
    }

    return data;
  }

  /**
   * Update course information manually
   */
  static async updateCourse(courseId: string, updates: Partial<Course>) {
    const { data, error } = await supabase
      .from('student_course_history')
      .update(updates)
      .eq('id', courseId)
      .select()
      .single();

    if (error) {
      throw error;
    }

    return data;
  }

  /**
   * Delete a course from history
   */
  static async deleteCourse(courseId: string) {
    const { error } = await supabase
      .from('student_course_history')
      .delete()
      .eq('id', courseId);

    if (error) {
      throw error;
    }
  }

  /**
   * Add a course manually
   */
  static async addCourse(studentId: string, course: Omit<Course, 'id'>) {
    const { data, error } = await supabase
      .from('student_course_history')
      .insert({
        student_id: studentId,
        ...course
      })
      .select()
      .single();

    if (error) {
      throw error;
    }

    return data;
  }
}

export default DocumentParser;
