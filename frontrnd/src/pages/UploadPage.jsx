import React, { useState, useEffect } from 'react';
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
  const [availableRoles, setAvailableRoles] = useState([]);
  const [newRole, setNewRole] = useState('');
  const [showAddRole, setShowAddRole] = useState(false);
  const [addingRole, setAddingRole] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [confirmationMessage, setConfirmationMessage] = useState('');
  
  const navigate = useNavigate();

  // Load available roles on component mount
  useEffect(() => {
    fetchAvailableRoles();
  }, []);

  const fetchAvailableRoles = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/roles`);
      const data = await res.json();
      setAvailableRoles(data.roles?.map(role => role.name) || []);
    } catch (err) {
      console.error('Failed to fetch roles:', err);
    }
  };

  const handleAddRole = async () => {
    if (!newRole.trim()) return;
    
    setAddingRole(true);
    try {
      const res = await fetch(`${API_BASE_URL}/roles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newRole.trim() }),
      });
      const data = await res.json();
      
      if (res.ok) {
        setNewRole('');
        setShowAddRole(false);
        fetchAvailableRoles(); // Refresh roles list
        setConfirmationMessage(`Role "${newRole.trim()}" added successfully!`);
      } else {
        setConfirmationMessage(data.detail || 'Failed to add role');
      }
    } catch (err) {
      console.error('Add role error:', err);
      setConfirmationMessage('Failed to add role');
    } finally {
      setAddingRole(false);
    }
  };

  const handleConfirmRole = async (resumeId, confirmedRole) => {
    setConfirming(true);
    setConfirmationMessage('');
    try {
      const res = await fetch(`${API_BASE_URL}/confirm-role`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          resume_id: resumeId, 
          confirmed_role: confirmedRole 
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setConfirmationMessage('Role confirmed successfully!');
        // Update the result to show confirmed role
        setResult(prev => ({
          ...prev,
          analysis_result: {
            ...prev.analysis_result,
            confirmed_role: confirmedRole
          }
        }));
      } else {
        setConfirmationMessage(data.detail || 'Failed to confirm role');
      }
    } catch (err) {
      console.error('Confirm role error:', err);
      setConfirmationMessage('Failed to confirm role');
    } finally {
      setConfirming(false);
    }
  };

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
            
            {/* Debug: Show raw result */}
            <details className="mb-3">
              <summary className="text-xs text-gray-500 cursor-pointer">Debug: Raw Response</summary>
              <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-auto">
                {JSON.stringify(result, null, 2)}
              </pre>
            </details>
          
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

          {/* Analysis Results - Handle both direct results and nested analysis_result */}
          {(result.analysis_result || result.predicted_role) && (
            <div className="border-t border-green-200 pt-4">
              {/* Get the actual result data */}
              {(() => {
                const analysisData = result.analysis_result || result;
                return (
                  <>
                    {/* Main Analysis Results */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      {/* Prediction Card */}
                      <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                        <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                          🎯 Prediction Results
                        </h4>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">Predicted Role:</span>
                            <span className="font-medium text-blue-600">{analysisData.predicted_role}</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">Confidence:</span>
                            <span className={`font-medium ${
                              analysisData.match_score >= 0.8 ? 'text-green-600' :
                              analysisData.match_score >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                            }`}>
                              {(analysisData.match_score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">Resume ID:</span>
                            <span className="text-xs text-gray-500 font-mono">{analysisData.id}</span>
                          </div>
                        </div>
                      </div>

                      {/* Skills Card */}
                      <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                        <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                          🛠️ Extracted Skills
                        </h4>
                        <div className="flex flex-wrap gap-1">
                          {analysisData.skills?.map((skill, index) => (
                            <span key={index} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* AI Insights Section */}
                    {analysisData.ai_enhanced && (
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-200 mb-4">
                        <h4 className="font-semibold text-blue-800 mb-3 flex items-center">
                          🤖 AI-Powered Insights
                        </h4>
                        
                        {/* Alternative Role Suggestions */}
                        {analysisData.ai_suggestions && Object.keys(analysisData.ai_suggestions).length > 0 && (
                          <div className="mb-4">
                            <p className="text-sm font-medium text-blue-700 mb-2">Alternative Role Suggestions:</p>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                              {Object.entries(analysisData.ai_suggestions).map(([role, confidence]) => (
                                <div key={role} className="bg-white p-2 rounded border border-blue-200">
                                  <div className="text-sm font-medium text-blue-800">{role}</div>
                                  <div className="text-xs text-blue-600">
                                    Confidence: {(confidence * 100).toFixed(0)}%
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Resume Feedback */}
                        {analysisData.ai_feedback && (
                          <div>
                            <p className="text-sm font-medium text-blue-700 mb-2">Resume Feedback:</p>
                            <div className="bg-white p-4 rounded border border-blue-200">
                              <div className="prose prose-sm max-w-none">
                                {(() => {
                                  const feedback = analysisData.ai_feedback;
                                  
                                  // Split feedback into sections based on numbered points
                                  const sections = feedback.split(/(?=\*\*[0-9]+\.)/);
                                  
                                  return (
                                    <div className="space-y-4">
                                      {/* Main summary */}
                                      {sections[0] && (
                                        <div className="mb-4">
                                          <p className="text-sm text-blue-700 leading-relaxed">
                                            {sections[0].trim()}
                                          </p>
                                        </div>
                                      )}
                                      
                                      {/* Numbered suggestions */}
                                      {sections.slice(1).map((section, index) => {
                                        const lines = section.trim().split('\n').filter(line => line.trim());
                                        const title = lines[0];
                                        const content = lines.slice(1);
                                        
                                        return (
                                          <div key={index} className="border-l-4 border-blue-300 pl-4">
                                            <h5 className="font-semibold text-blue-800 mb-2 text-sm">
                                              {title.replace(/\*\*/g, '')}
                                            </h5>
                                            <div className="space-y-2">
                                              {content.map((line, lineIndex) => {
                                                const trimmedLine = line.trim();
                                                if (trimmedLine.startsWith('* **Actionable Step:**')) {
                                                  return (
                                                    <div key={lineIndex} className="bg-blue-50 p-3 rounded border border-blue-200">
                                                      <p className="text-sm font-medium text-blue-800 mb-1">
                                                        Actionable Step:
                                                      </p>
                                                      <p className="text-sm text-blue-700">
                                                        {trimmedLine.replace('* **Actionable Step:**', '').trim()}
                                                      </p>
                                                    </div>
                                                  );
                                                } else if (trimmedLine.startsWith('* **Example')) {
                                                  return (
                                                    <div key={lineIndex} className="bg-green-50 p-3 rounded border border-green-200">
                                                      <p className="text-sm font-medium text-green-800 mb-1">
                                                        Example:
                                                      </p>
                                                      <p className="text-sm text-green-700">
                                                        {trimmedLine.replace(/^\* \*\*Example[^:]*:\*\*/, '').trim()}
                                                      </p>
                                                    </div>
                                                  );
                                                } else if (trimmedLine.startsWith('* ')) {
                                                  return (
                                                    <p key={lineIndex} className="text-sm text-blue-700 ml-4">
                                                      • {trimmedLine.replace('* ', '').trim()}
                                                    </p>
                                                  );
                                                } else if (trimmedLine) {
                                                  return (
                                                    <p key={lineIndex} className="text-sm text-blue-700">
                                                      {trimmedLine}
                                                    </p>
                                                  );
                                                }
                                                return null;
                                              })}
                                            </div>
                                          </div>
                                        );
                                      })}
                                    </div>
                                  );
                                })()}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Role Confirmation Section */}
                    <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                      {analysisData.confirmed_role ? (
                        <div className="text-center">
                          <h4 className="font-semibold text-green-800 mb-2 flex items-center justify-center">
                            ✅ Role Confirmed
                          </h4>
                          <div className="bg-green-50 p-3 rounded border border-green-200">
                            <span className="text-lg font-medium text-green-700">{analysisData.confirmed_role}</span>
                          </div>
                        </div>
                      ) : (
                        <div>
                          <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                            📋 Confirm Your Role
                          </h4>
                          <p className="text-sm text-gray-600 mb-3">
                            Help improve our predictions by confirming the correct role for this resume:
                          </p>
                          
                          {/* Available Roles */}
                          <div className="mb-4">
                            <p className="text-sm font-medium text-gray-700 mb-2">Select from existing roles:</p>
                            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                              {availableRoles.map((role) => (
                                <button
                                  key={role}
                                  onClick={() => handleConfirmRole(analysisData.id, role)}
                                  disabled={confirming}
                                  className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                                    confirming 
                                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                                      : 'bg-blue-500 hover:bg-blue-600 text-white shadow-sm'
                                  }`}
                                >
                                  {role}
                                </button>
                              ))}
                            </div>
                          </div>
                          
                          {/* Add New Role */}
                          <div className="border-t pt-4">
                            <p className="text-sm font-medium text-gray-700 mb-2">Or add a new role:</p>
                            <div className="flex gap-2">
                              <button
                                onClick={() => setShowAddRole(true)}
                                disabled={confirming}
                                className={`px-4 py-2 rounded text-sm font-medium border-2 border-dashed transition-colors ${
                                  confirming 
                                    ? 'border-gray-300 text-gray-400 cursor-not-allowed' 
                                    : 'border-blue-500 text-blue-600 hover:bg-blue-50'
                                }`}
                              >
                                + Add New Role
                              </button>
                            </div>
                            
                            {/* Add New Role Form */}
                            {showAddRole && (
                              <div className="mt-3 p-4 bg-gray-50 rounded-lg border">
                                <div className="flex gap-2">
                                  <input
                                    type="text"
                                    placeholder="Enter new role name..."
                                    value={newRole}
                                    onChange={(e) => setNewRole(e.target.value)}
                                    className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    onKeyPress={(e) => e.key === 'Enter' && handleAddRole()}
                                  />
                                  <button
                                    onClick={handleAddRole}
                                    disabled={addingRole || !newRole.trim()}
                                    className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
                                      addingRole || !newRole.trim()
                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                        : 'bg-green-500 hover:bg-green-600 text-white'
                                    }`}
                                  >
                                    {addingRole ? 'Adding...' : 'Add'}
                                  </button>
                                  <button
                                    onClick={() => {
                                      setShowAddRole(false);
                                      setNewRole('');
                                    }}
                                    className="px-4 py-2 text-sm font-medium bg-gray-500 hover:bg-gray-600 text-white rounded transition-colors"
                                  >
                                    Cancel
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                      
                      {/* Confirmation Message */}
                      {confirmationMessage && (
                        <div className={`mt-3 p-3 rounded ${
                          confirmationMessage.includes('successfully') 
                            ? 'bg-green-100 border border-green-200 text-green-700' 
                            : 'bg-red-100 border border-red-200 text-red-700'
                        }`}>
                          <p className="text-sm font-medium">{confirmationMessage}</p>
                        </div>
                      )}
                    </div>
                  </>
                );
              })()}
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