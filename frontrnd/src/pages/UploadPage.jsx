import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function UploadPage() {
  const [email, setEmail] = useState('');
  const [resumeText, setResumeText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [useAI, setUseAI] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [uploadMethod, setUploadMethod] = useState('text'); // 'text' or 'file'
  
  const navigate = useNavigate();

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('Please select a PDF file');
        setSelectedFile(null);
        return;
      }
      
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size too large. Maximum size is 10MB.');
        setSelectedFile(null);
        return;
      }
      
      setSelectedFile(file);
      setError('');
    }
  };

  const handleTextUpload = async () => {
    if (!email.trim() || !resumeText.trim()) {
      setError('Please fill in all fields');
      return;
    }

    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('user_email', email);
      formData.append('resume_text', resumeText);
      formData.append('use_ai', useAI);

      const response = await fetch(`${API_BASE_URL}/upload-resume-text`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
        setError('');
      } else {
        setError(data.detail || 'Failed to upload resume');
        setResult(null);
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload resume');
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!email.trim() || !selectedFile) {
      setError('Please fill in all fields and select a file');
      return;
    }

    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('user_email', email);
      formData.append('use_ai', useAI);

      const response = await fetch(`${API_BASE_URL}/upload-resume`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
        setError('');
      } else {
        setError(data.detail || 'Failed to upload resume');
        setResult(null);
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload resume');
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = () => {
    if (uploadMethod === 'text') {
      handleTextUpload();
    } else {
      handleFileUpload();
    }
  };

  const handleViewResumes = () => {
    navigate('/resumes');
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold mb-2">Upload Resume</h2>
        <p className="text-gray-600">Upload your resume as text or PDF file for analysis</p>
      </div>

      {/* Upload Method Toggle */}
      <div className="mb-6">
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setUploadMethod('text')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              uploadMethod === 'text'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            📝 Text Input
          </button>
          <button
            onClick={() => setUploadMethod('file')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              uploadMethod === 'file'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            📄 PDF Upload
          </button>
        </div>
      </div>

      {/* Email Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Email Address *
        </label>
        <input
          type="email"
          placeholder="your.email@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      {/* AI Enhancement Toggle */}
      <div className="mb-4">
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={useAI}
            onChange={(e) => setUseAI(e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">Use AI Enhancement (Google Gemini)</span>
        </label>
      </div>

      {/* Upload Content */}
      {uploadMethod === 'text' ? (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Resume Text *
          </label>
          <textarea
            placeholder="Paste your resume text here..."
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-vertical"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Copy and paste your resume content here. The system will extract skills and predict your role.
          </p>
        </div>
      ) : (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            PDF File *
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-md p-6 text-center">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-50 hover:bg-blue-100"
            >
              📄 Choose PDF File
            </label>
            {selectedFile && (
              <div className="mt-3">
                <p className="text-sm text-gray-600">
                  Selected: <span className="font-medium">{selectedFile.name}</span>
                </p>
                <p className="text-xs text-gray-500">
                  Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Upload a PDF resume (max 10MB). The system will extract text and analyze it.
          </p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Submit Button */}
      <div className="flex gap-3">
        <button
          onClick={handleSubmit}
          disabled={isLoading}
          className={`flex-1 py-2 px-4 rounded-md text-white font-medium ${
            isLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {isLoading ? 'Processing...' : 'Upload & Analyze'}
        </button>
        <button
          onClick={handleViewResumes}
          className="py-2 px-4 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          View Resumes
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
          <h3 className="text-lg font-medium text-green-800 mb-2">
            ✅ Upload Successful!
          </h3>
          
          {uploadMethod === 'file' && (
            <div className="mb-3">
              <p className="text-sm text-green-700">
                <strong>File:</strong> {result.filename}
              </p>
              <p className="text-sm text-green-700">
                <strong>Size:</strong> {(result.file_size / 1024).toFixed(1)} KB
              </p>
              <p className="text-sm text-green-700">
                <strong>Text extracted:</strong> {result.extracted_text_length} characters
              </p>
            </div>
          )}

          {result.analysis_result && (
            <div className="border-t border-green-200 pt-3">
              <h4 className="font-medium text-green-800 mb-2">Analysis Results:</h4>
              <div className="space-y-1 text-sm text-green-700">
                <p><strong>Predicted Role:</strong> {result.analysis_result.predicted_role}</p>
                <p><strong>Match Score:</strong> 
                  <span className={`font-medium ${
                    result.analysis_result.match_score >= 0.8 ? 'text-green-600' :
                    result.analysis_result.match_score >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {(result.analysis_result.match_score * 100).toFixed(1)}%
                  </span>
                </p>
                <p><strong>Skills Found:</strong> {result.analysis_result.skills?.join(', ')}</p>
              </div>
            </div>
          )}

          <div className="mt-4">
            <button
              onClick={() => navigate('/resumes')}
              className="text-sm text-green-600 hover:text-green-800 underline"
            >
              View all resumes →
            </button>
          </div>
        </div>
      )}
    </div>
  );
} 