import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { User } from '@supabase/supabase-js';
import authService from '../../lib/auth';
import { toast } from 'react-hot-toast';
import { 
  UserIcon, 
  DocumentTextIcon, 
  AcademicCapIcon, 
  CheckCircleIcon,
  ArrowRightIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';

interface OnboardingStep {
  id: number;
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  component: React.ComponentType<any>;
}

interface OnboardingWizardProps {
  user: User;
  onComplete: () => void;
}

interface StudentProfile {
  student_name: string;
  student_id: string;
  student_email: string;
  student_phone: string;
  degree_emphasis: string;
  academic_standing: string;
  expected_graduation: string;
}

// Step 1: Basic Information
const BasicInfoStep: React.FC<{
  user: User;
  profile: StudentProfile;
  setProfile: (profile: StudentProfile) => void;
  onNext: () => void;
}> = ({ user, profile, setProfile, onNext }) => {
  const [isValid, setIsValid] = useState(false);

  useEffect(() => {
    const required = profile.student_name && profile.student_id && profile.student_email;
    setIsValid(!!required);
  }, [profile]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isValid) {
      onNext();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="student_name" className="block text-sm font-medium text-gray-700 mb-2">
          Full Name *
        </label>
        <input
          type="text"
          id="student_name"
          value={profile.student_name}
          onChange={(e) => setProfile({ ...profile, student_name: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter your full name"
          required
        />
      </div>

      <div>
        <label htmlFor="student_id" className="block text-sm font-medium text-gray-700 mb-2">
          Utah Tech Student ID *
        </label>
        <input
          type="text"
          id="student_id"
          value={profile.student_id}
          onChange={(e) => setProfile({ ...profile, student_id: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., 00123456"
          required
        />
      </div>

      <div>
        <label htmlFor="student_email" className="block text-sm font-medium text-gray-700 mb-2">
          Email Address *
        </label>
        <input
          type="email"
          id="student_email"
          value={profile.student_email}
          onChange={(e) => setProfile({ ...profile, student_email: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="your.email@utahtech.edu"
          required
        />
      </div>

      <div>
        <label htmlFor="student_phone" className="block text-sm font-medium text-gray-700 mb-2">
          Phone Number
        </label>
        <input
          type="tel"
          id="student_phone"
          value={profile.student_phone}
          onChange={(e) => setProfile({ ...profile, student_phone: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="(555) 123-4567"
        />
      </div>

      <div>
        <label htmlFor="degree_emphasis" className="block text-sm font-medium text-gray-700 mb-2">
          Proposed Degree Emphasis
        </label>
        <input
          type="text"
          id="degree_emphasis"
          value={profile.degree_emphasis}
          onChange={(e) => setProfile({ ...profile, degree_emphasis: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., Psychology and Digital Media"
        />
        <p className="text-sm text-gray-500 mt-1">
          This can be changed later as you develop your IAP
        </p>
      </div>

      <button
        type="submit"
        disabled={!isValid}
        className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        Continue
        <ArrowRightIcon className="ml-2 h-4 w-4" />
      </button>
    </form>
  );
};

// Step 2: Document Upload
const DocumentUploadStep: React.FC<{
  user: User;
  onNext: () => void;
  onBack: () => void;
}> = ({ user, onNext, onBack }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadErrors, setUploadErrors] = useState<string[]>([]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files);
    }
  };

  const handleFileUpload = async (files: FileList) => {
    if (!user) {
      toast.error('User not authenticated');
      return;
    }

    // Show selected files immediately for visual feedback
    const fileArray = Array.from(files);
    setSelectedFiles(fileArray);
    console.log('Files selected:', fileArray.map(f => f.name));

    setUploading(true);
    setUploadErrors([]);
    const successfulUploads: string[] = [];
    const errors: string[] = [];
    
    try {
      console.log('Starting file upload process...', files.length, 'files');
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        console.log('Processing file:', file.name, 'Type:', file.type, 'Size:', file.size);
        
        // Validate file type
        if (file.type !== 'application/pdf') {
          console.log('Invalid file type:', file.type);
          toast.error(`${file.name} is not a PDF file`);
          continue;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
          console.log('File too large:', file.size);
          toast.error(`${file.name} is too large (max 10MB)`);
          continue;
        }

        try {
          console.log('Uploading file to Supabase storage:', file.name);
          
          // Generate unique file name
          const timestamp = Date.now();
          const fileName = `${user.id}/${timestamp}_${file.name}`;
          
          // Upload to Supabase Storage
          const { data: storageData, error: storageError } = await authService.supabase.storage
            .from('student-documents')
            .upload(fileName, file, {
              cacheControl: '3600',
              upsert: false
            });

          if (storageError) {
            console.error('Storage upload error:', storageError);
            const errorMsg = `${file.name}: ${storageError.message || 'Upload failed'}`;
            errors.push(errorMsg);
            toast.error(`Failed to upload ${file.name}: ${storageError.message}`);
            continue;
          }

          console.log('File uploaded to storage:', storageData.path);

          // First, get the student profile ID
          console.log('Getting student profile for user:', user.id);
          const { data: profileData, error: profileError } = await authService.supabase
            .from('student_profiles')
            .select('id')
            .eq('user_id', user.id)
            .single();

          if (profileError) {
            console.error('Error getting student profile:', profileError);
            // Try to clean up the uploaded file
            await authService.supabase.storage
              .from('student-documents')
              .remove([storageData.path]);
            toast.error(`Failed to link ${file.name} to your profile. Please complete your profile first.`);
            continue;
          }

          // Save document record to database
          const documentData = {
            student_id: profileData.id,
            document_type: 'transcript', // Default to transcript, can be updated later
            file_name: file.name,
            file_url: storageData.path,
            file_size: file.size,
            mime_type: file.type,
            parsing_status: 'pending'
          };

          console.log('Saving document record to database:', documentData);

          const { data: dbData, error: dbError } = await authService.supabase
            .from('student_documents')
            .insert(documentData)
            .select();

          if (dbError) {
            console.error('Database save error:', dbError);
            // Try to clean up the uploaded file
            await authService.supabase.storage
              .from('student-documents')
              .remove([storageData.path]);
            toast.error(`Failed to save ${file.name} record: ${dbError.message}`);
            continue;
          }

          console.log('Document record saved:', dbData);
          successfulUploads.push(file.name);
          console.log('File processed successfully:', file.name);
          
        } catch (fileError) {
          console.error('Error processing file:', file.name, fileError);
          toast.error(`Failed to process ${file.name}`);
        }
      }
      
      // Update uploaded files state
      if (successfulUploads.length > 0) {
        console.log('Setting uploaded files:', successfulUploads);
        setUploadedFiles(prev => {
          const newFiles = [...prev, ...successfulUploads];
          console.log('Updated uploaded files state:', newFiles);
          return newFiles;
        });
        
        // Show success message
        toast.success(`Successfully uploaded ${successfulUploads.length} file(s)`);
      }
      
      // Update error state
      if (errors.length > 0) {
        setUploadErrors(errors);
        console.log('Upload errors:', errors);
      }
      
    } catch (error) {
      console.error('Upload process error:', error);
      toast.error('Upload failed');
    } finally {
      console.log('Upload process completed');
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Upload Your Academic Documents
        </h3>
        <p className="text-sm text-gray-600">
          Upload your official transcript, degree audit, or transfer credit evaluations.
          These will help us build your personalized academic plan.
        </p>
      </div>

      <div
        className={`relative border-2 border-dashed rounded-lg p-6 transition-colors ${
          dragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple
          accept=".pdf"
          onChange={handleChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={uploading}
        />
        
        <div className="text-center">
          <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
          <div className="mt-4">
            <p className="text-sm text-gray-600">
              <span className="font-medium text-blue-600 hover:text-blue-500">
                Click to upload
              </span>{' '}
              or drag and drop
            </p>
            <p className="text-xs text-gray-500">PDF files only</p>
          </div>
        </div>

        {uploading && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>

      {uploadedFiles.length > 0 && (
        <div className="bg-green-50 border-2 border-green-300 rounded-lg p-4 animate-pulse">
          <div className="flex items-center mb-2">
            <CheckCircleIcon className="h-5 w-5 text-green-600 mr-2" />
            <h4 className="text-sm font-semibold text-green-800">✅ Upload Successful!</h4>
          </div>
          <p className="text-sm text-green-700 mb-2">Your documents have been uploaded and are being processed:</p>
          <ul className="text-sm text-green-700 space-y-2">
            {uploadedFiles.map((fileName, index) => (
              <li key={index} className="flex items-center bg-white rounded px-3 py-2">
                <CheckCircleIcon className="h-4 w-4 mr-2 text-green-600" />
                <span className="font-medium">{fileName}</span>
                <span className="ml-auto text-xs text-green-600">✓ Ready</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Show selected files even if upload failed */}
      {selectedFiles.length > 0 && uploadedFiles.length === 0 && (
        <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <DocumentTextIcon className="h-5 w-5 text-blue-600 mr-2" />
            <h4 className="text-sm font-semibold text-blue-800">📄 Files Selected</h4>
          </div>
          <p className="text-sm text-blue-700 mb-2">Files ready for upload:</p>
          <ul className="text-sm text-blue-700 space-y-2">
            {selectedFiles.map((file, index) => (
              <li key={index} className="flex items-center bg-white rounded px-3 py-2">
                <DocumentTextIcon className="h-4 w-4 mr-2 text-blue-600" />
                <span className="font-medium">{file.name}</span>
                <span className="ml-auto text-xs text-blue-600">{(file.size / 1024).toFixed(1)} KB</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Show upload errors */}
      {uploadErrors.length > 0 && (
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <svg className="h-5 w-5 text-red-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <h4 className="text-sm font-semibold text-red-800">❌ Upload Issues</h4>
          </div>
          <p className="text-sm text-red-700 mb-2">The following files couldn't be uploaded:</p>
          <ul className="text-sm text-red-700 space-y-1">
            {uploadErrors.map((error, index) => (
              <li key={index} className="bg-white rounded px-3 py-2">
                {error}
              </li>
            ))}
          </ul>
          <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-sm text-yellow-800">
              <strong>💡 Note:</strong> You can still continue with your onboarding. 
              File upload is optional and can be completed later from your dashboard.
            </p>
          </div>
        </div>
      )}

      <div className="flex justify-between">
        <button
          onClick={onBack}
          className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
        >
          <ArrowLeftIcon className="mr-2 h-4 w-4" />
          Back
        </button>
        
        <button
          onClick={onNext}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Continue
          <ArrowRightIcon className="ml-2 h-4 w-4" />
        </button>
      </div>

      <div className="text-center">
        <button
          onClick={onNext}
          className="text-sm text-gray-500 hover:text-gray-700 underline"
        >
          Skip for now - I'll upload documents later
        </button>
      </div>
    </div>
  );
};

// Step 3: Academic Information
const AcademicInfoStep: React.FC<{
  user: User;
  profile: StudentProfile;
  setProfile: (profile: StudentProfile) => void;
  onNext: () => void;
  onBack: () => void;
}> = ({ user, profile, setProfile, onNext, onBack }) => {
  const [isCompleting, setIsCompleting] = useState(false);
  
  const handleComplete = async () => {
    console.log('Complete Setup clicked!');
    setIsCompleting(true);
    
    try {
      // Add a small delay to show the loading state
      await new Promise(resolve => setTimeout(resolve, 1000));
      onNext();
    } catch (error) {
      console.error('Setup completion error:', error);
    } finally {
      setIsCompleting(false);
    }
  };
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Academic Information
        </h3>
        <p className="text-sm text-gray-600">
          Help us understand your current academic status and goals.
        </p>
      </div>

      <div>
        <label htmlFor="academic_standing" className="block text-sm font-medium text-gray-700 mb-2">
          Current Academic Standing
        </label>
        <select
          id="academic_standing"
          value={profile.academic_standing}
          onChange={(e) => setProfile({ ...profile, academic_standing: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Select your standing</option>
          <option value="freshman">Freshman (0-29 credits)</option>
          <option value="sophomore">Sophomore (30-59 credits)</option>
          <option value="junior">Junior (60-89 credits)</option>
          <option value="senior">Senior (90+ credits)</option>
          <option value="transfer">Transfer Student</option>
          <option value="returning">Returning Student</option>
        </select>
      </div>

      <div>
        <label htmlFor="expected_graduation" className="block text-sm font-medium text-gray-700 mb-2">
          Expected Graduation
        </label>
        <input
          type="month"
          id="expected_graduation"
          value={profile.expected_graduation}
          onChange={(e) => setProfile({ ...profile, expected_graduation: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <h4 className="text-sm font-medium text-blue-800 mb-2">What's Next?</h4>
        <p className="text-sm text-blue-700">
          After completing this setup, you'll be able to:
        </p>
        <ul className="text-sm text-blue-700 mt-2 space-y-1">
          <li>• Chat with your AI academic advisor</li>
          <li>• Search Utah Tech's course catalog</li>
          <li>• Build your personalized IAP</li>
          <li>• Track your degree progress</li>
          <li>• Get market research for your emphasis</li>
        </ul>
      </div>

      <div className="flex justify-between">
        <button
          onClick={onBack}
          className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
        >
          <ArrowLeftIcon className="mr-2 h-4 w-4" />
          Back
        </button>
        
        <button
          onClick={handleComplete}
          disabled={isCompleting}
          className={`flex items-center px-6 py-3 rounded-md transition-all duration-200 font-medium ${
            isCompleting 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-green-600 hover:bg-green-700 hover:shadow-lg transform hover:scale-105'
          } text-white`}
        >
          {isCompleting ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Setting up...
            </>
          ) : (
            <>
              Complete Setup
              <CheckCircleIcon className="ml-2 h-5 w-5" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};

// Main Onboarding Wizard Component
export const OnboardingWizard: React.FC<OnboardingWizardProps> = ({ user, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [profile, setProfile] = useState<StudentProfile>({
    student_name: '',
    student_id: '',
    student_email: user.email || '',
    student_phone: '',
    degree_emphasis: '',
    academic_standing: '',
    expected_graduation: ''
  });
  const [sessionRefreshed, setSessionRefreshed] = useState(false);

  // Refresh session on component mount to ensure authentication context
  useEffect(() => {
    const refreshSession = async () => {
      console.log('Refreshing Supabase session...');
      try {
        const { data, error } = await authService.supabase.auth.refreshSession();
        console.log('Session refresh result:', { session: data.session, error });
        
        if (error) {
          console.error('Session refresh error:', error);
          toast.error('Authentication session error. Please log in again.');
        } else if (data.session) {
          console.log('Session refreshed successfully:', data.session.user.id);
          setSessionRefreshed(true);
        } else {
          console.warn('No session found after refresh');
          toast.error('Please log in again to continue setup.');
        }
      } catch (err) {
        console.error('Session refresh failed:', err);
        toast.error('Authentication error. Please refresh the page.');
      }
    };
    
    refreshSession();
  }, []);

  const steps: OnboardingStep[] = [
    {
      id: 0,
      title: 'Basic Information',
      description: 'Tell us about yourself',
      icon: UserIcon,
      component: BasicInfoStep
    },
    {
      id: 1,
      title: 'Upload Documents',
      description: 'Share your academic records',
      icon: DocumentTextIcon,
      component: DocumentUploadStep
    },
    {
      id: 2,
      title: 'Academic Details',
      description: 'Complete your profile',
      icon: AcademicCapIcon,
      component: AcademicInfoStep
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    console.log('Starting onboarding completion...');
    console.log('Profile data:', profile);
    console.log('User ID:', user.id);
    console.log('Session refreshed:', sessionRefreshed);
    
    try {
      // Force refresh session before profile creation to ensure valid auth context
      const { data: refreshData, error: refreshError } = await authService.supabase.auth.refreshSession();
      console.log('Fresh session refresh:', { session: refreshData.session, error: refreshError });
      
      if (refreshError || !refreshData.session?.user) {
        console.error('Session refresh failed:', refreshError);
        toast.error('Authentication session expired. Please log in again.');
        // Redirect to login
        window.location.href = '/auth';
        return;
      }
      
      const sessionUser = refreshData.session.user;
      console.log('Using session user ID:', sessionUser.id);
      console.log('Session user email:', sessionUser.email);
      
      // Prepare profile data with required fields matching the database schema
      const profileData = {
        user_id: sessionUser.id, // Use session user ID for RLS consistency
        student_id: profile.student_id || '',
        student_name: profile.student_name || 'Unknown Student', // Fixed: use student_name not full_name
        student_email: profile.student_email || user.email || '', // Fixed: use student_email not email
        phone: profile.student_phone || '',
        major: profile.degree_emphasis || '',
        classification: profile.academic_standing || '',
        expected_graduation: profile.expected_graduation ? new Date(profile.expected_graduation) : null
      };
      
      console.log('Inserting profile data:', profileData);
      
      // Save student profile to database
      const { data, error } = await authService.supabase
        .from('student_profiles')
        .insert(profileData)
        .select();

      if (error) {
        // Handle duplicate student_id gracefully - profile already exists
        if (error.code === '23505' && error.message.includes('student_profiles_student_id_key')) {
          console.log('Profile already exists for this student_id, proceeding with onboarding completion');
          toast.success('Profile found! Completing setup...');
        } else {
          console.error('Database error:', error);
          toast.error(`Failed to save profile: ${error.message}`);
          return;
        }
      } else {
        console.log('Profile saved successfully:', data);
        toast.success('Welcome to Utah Tech IAP Advisor!');
      }
      
      // Small delay to show success message
      setTimeout(() => {
        console.log('Calling onComplete callback');
        onComplete();
      }, 1000);
      
    } catch (error) {
      console.error('Onboarding completion error:', error);
      toast.error('Setup failed. Please try again.');
    }
  };

  const CurrentStepComponent = steps[currentStep].component;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Welcome to Utah Tech</h2>
          <p className="mt-2 text-lg text-gray-600">IAP Advisor Setup</p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {/* Progress Indicator */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              {steps.map((step, index) => {
                const Icon = step.icon;
                const isActive = index === currentStep;
                const isCompleted = index < currentStep;
                
                return (
                  <div key={step.id} className="flex flex-col items-center">
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        isCompleted
                          ? 'bg-green-600 text-white'
                          : isActive
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-200 text-gray-400'
                      }`}
                    >
                      {isCompleted ? (
                        <CheckCircleIcon className="h-6 w-6" />
                      ) : (
                        <Icon className="h-6 w-6" />
                      )}
                    </div>
                    <div className="mt-2 text-center">
                      <p className="text-xs font-medium text-gray-900">{step.title}</p>
                      <p className="text-xs text-gray-500">{step.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Current Step Content */}
          <CurrentStepComponent
            user={user}
            profile={profile}
            setProfile={setProfile}
            onNext={handleNext}
            onBack={handleBack}
          />
        </div>
      </div>
    </div>
  );
};

export default OnboardingWizard;
