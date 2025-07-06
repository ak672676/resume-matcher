import React, { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function AnalyzePage() {
  const [email, setEmail] = useState('');
  const [resumeText, setResumeText] = useState('');
  const [result, setResult] = useState(null);
  const [confirming, setConfirming] = useState(false);
  const [confirmationMessage, setConfirmationMessage] = useState('');
  const [useAI, setUseAI] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [availableRoles, setAvailableRoles] = useState([]);
  const [newRole, setNewRole] = useState('');
  const [showAddRole, setShowAddRole] = useState(false);
  const [addingRole, setAddingRole] = useState(false);

  // Load available roles on component mount
  React.useEffect(() => {
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

  const handleAnalyze = async () => {
    setResult(null);
    setConfirmationMessage('');
    setIsLoading(true);
    try {
      const endpoint = useAI ? '/analyze-ai' : '/analyze';
      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_email: email, resume_text: resumeText }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error('Analyze error:', err);
      setResult({ error: 'Failed to analyze resume' });
    } finally {
      setIsLoading(false);
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
          confirmed_role: confirmedRole
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

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Analyze Resume</h2>
      <input
        type="email"
        placeholder="Your email"
        className="border p-2 w-full mb-4 rounded"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <div className="mb-4">
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={useAI}
            onChange={(e) => setUseAI(e.target.checked)}
            className="rounded"
          />
          <span className="text-sm">Use AI Enhancement (Google Gemini)</span>
        </label>
      </div>
      <textarea
        placeholder="Paste resume text here..."
        className="border p-2 w-full h-32 mb-4 rounded"
        value={resumeText}
        onChange={(e) => setResumeText(e.target.value)}
      />
      <button
        onClick={handleAnalyze}
        disabled={isLoading}
        className={`px-4 py-2 rounded text-white ${
          isLoading 
            ? 'bg-gray-400 cursor-not-allowed' 
            : 'bg-green-600 hover:bg-green-700'
        }`}
      >
        {isLoading ? 'Analyzing...' : 'Analyze'}
      </button>
      {result && (
        <div className="mt-4 text-sm text-gray-700 space-y-2">
          {result.error ? (
            <p className="text-red-600">{result.error}</p>
          ) : (
            <>
              <p><strong>Resume ID:</strong> {result.id}</p>
              <p><strong>Predicted Role:</strong> {result.predicted_role}</p>
              <p><strong>Match Score:</strong> 
                <span className={`font-medium ${
                  result.match_score >= 0.8 ? 'text-green-600' :
                  result.match_score >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {(result.match_score * 100).toFixed(1)}%
                </span>
              </p>
              <p><strong>Extracted Skills:</strong> {result.skills.join(', ')}</p>
              
              {result.ai_enhanced && (
                <div className="mt-4 p-3 bg-blue-50 rounded border-l-4 border-blue-400">
                  <h4 className="font-semibold text-blue-800 mb-2">🤖 AI Insights</h4>
                  {result.ai_suggestions && Object.keys(result.ai_suggestions).length > 0 && (
                    <div className="mb-3">
                      <p className="text-sm font-medium text-blue-700">Alternative Role Suggestions:</p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {Object.entries(result.ai_suggestions).map(([role, confidence]) => (
                          <span key={role} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            {role} ({(confidence * 100).toFixed(0)}%)
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {result.ai_feedback && (
                    <div>
                      <p className="text-sm font-medium text-blue-700">Resume Feedback:</p>
                      <p className="text-sm text-blue-600 mt-1">{result.ai_feedback}</p>
                    </div>
                  )}
                </div>
              )}
              
              {result.confirmed_role ? (
                <p className="text-green-600">
                  <strong>Confirmed Role:</strong> {result.confirmed_role}
                </p>
              ) : (
                <div className="mt-4">
                  <p className="mb-2"><strong>Confirm Role:</strong></p>
                  <div className="flex gap-2 flex-wrap">
                    {availableRoles.map((role) => (
                      <button
                        key={role}
                        onClick={() => handleConfirmRole(result.id, role)}
                        disabled={confirming}
                        className={`px-3 py-1 rounded text-xs ${
                          confirming 
                            ? 'bg-gray-300 cursor-not-allowed' 
                            : 'bg-blue-500 hover:bg-blue-600 text-white'
                        }`}
                      >
                        {role}
                      </button>
                    ))}
                    
                    {/* Add new role button */}
                    <button
                      onClick={() => setShowAddRole(true)}
                      disabled={confirming}
                      className={`px-3 py-1 rounded text-xs border-2 border-dashed ${
                        confirming 
                          ? 'border-gray-300 text-gray-400 cursor-not-allowed' 
                          : 'border-blue-500 text-blue-600 hover:bg-blue-50'
                      }`}
                    >
                      + Add New Role
                    </button>
                  </div>
                  
                  {/* Add new role form */}
                  {showAddRole && (
                    <div className="mt-3 p-3 bg-gray-50 rounded border">
                      <div className="flex gap-2">
                        <input
                          type="text"
                          placeholder="Enter new role name..."
                          value={newRole}
                          onChange={(e) => setNewRole(e.target.value)}
                          className="flex-1 px-2 py-1 text-sm border rounded"
                          onKeyPress={(e) => e.key === 'Enter' && handleAddRole()}
                        />
                        <button
                          onClick={handleAddRole}
                          disabled={addingRole || !newRole.trim()}
                          className={`px-3 py-1 text-xs rounded ${
                            addingRole || !newRole.trim()
                              ? 'bg-gray-300 cursor-not-allowed'
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
                          className="px-3 py-1 text-xs bg-gray-500 hover:bg-gray-600 text-white rounded"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {confirmationMessage && (
                <p className={`mt-2 text-sm ${
                  confirmationMessage.includes('successfully') 
                    ? 'text-green-600' 
                    : 'text-red-600'
                }`}>
                  {confirmationMessage}
                </p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
