// Setup Supabase storage bucket for student documents
const { createClient } = require('@supabase/supabase-js')

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://localhost:8000'
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'

const supabase = createClient(supabaseUrl, supabaseKey)

async function setupStorage() {
  console.log('Setting up Supabase storage bucket for student documents...')
  
  try {
    // Create the bucket
    const { data, error } = await supabase.storage.createBucket('student-documents', {
      public: false,
      allowedMimeTypes: ['application/pdf'],
      fileSizeLimit: 10485760 // 10MB
    })

    if (error) {
      if (error.message.includes('already exists')) {
        console.log('✅ Storage bucket "student-documents" already exists')
      } else {
        console.error('❌ Error creating storage bucket:', error)
        return
      }
    } else {
      console.log('✅ Storage bucket "student-documents" created successfully')
    }

    // Test bucket access
    const { data: buckets, error: listError } = await supabase.storage.listBuckets()
    
    if (listError) {
      console.error('❌ Error listing buckets:', listError)
      return
    }

    const studentDocsBucket = buckets.find(bucket => bucket.name === 'student-documents')
    if (studentDocsBucket) {
      console.log('✅ Storage bucket verified:', studentDocsBucket.name)
      console.log('📁 Bucket details:', {
        id: studentDocsBucket.id,
        name: studentDocsBucket.name,
        public: studentDocsBucket.public,
        created_at: studentDocsBucket.created_at
      })
    } else {
      console.log('❌ Storage bucket not found in list')
    }

  } catch (error) {
    console.error('❌ Setup failed:', error)
  }
}

setupStorage()
