import React, { useState, useEffect } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function ResumesPage() {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState(false);
  const [message, setMessage] = useState('');
  const [availableRoles, setAvailableRoles] = useState([]);
  const [newRole, setNewRole] = useState('');
  const [showAddRole, setShowAddRole] = useState(false);
  const [addingRole, setAddingRole] = useState(false);
  const [activeResumeId, setActiveResumeId] = useState(null);

  useEffect(() => {
    fetchResumes();
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
        setActiveResumeId(null);
        fetchAvailableRoles(); // Refresh roles list
        setMessage(`Role "${newRole.trim()}" added successfully!`);
      } else {
        setMessage(data.detail || 'Failed to add role');
      }
    } catch (err) {
      console.error('Add role error:', err);
      setMessage('Failed to add role');
    } finally {
      setAddingRole(false);
    }
  };

  const fetchResumes = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/resumes`);
      const data = await res.json();
      setResumes(data.resumes || []);
    } catch (err) {
      console.error('Fetch resumes error:', err);
      setMessage('Failed to fetch resumes');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmRole = async (resumeId, confirmedRole) => {
    setConfirming(true);
    setMessage('');
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
        setMessage('Role confirmed successfully!');
        // Update the local state
        setResumes(prev => prev.map(resume => 
          resume.id === resumeId 
            ? { ...resume, confirmed_role: confirmedRole }
            : resume
        ));
      } else {
        setMessage(data.detail || 'Failed to confirm role');
      }
    } catch (err) {
      console.error('Confirm role error:', err);
      setMessage('Failed to confirm role');
    } finally {
      setConfirming(false);
    }
  };



  if (loading) {
    return (
      <div className="p-6">
        <h2 className="text-2xl font-semibold mb-4">Resumes</h2>
        <p>Loading resumes...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Resumes</h2>
        <button
          onClick={fetchResumes}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Refresh
        </button>
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded ${
          message.includes('successfully') 
            ? 'bg-green-100 text-green-700' 
            : 'bg-red-100 text-red-700'
        }`}>
          {message}
        </div>
      )}

      {resumes.length === 0 ? (
        <p className="text-gray-500">No resumes found.</p>
      ) : (
        <div className="space-y-4">
          {resumes.map((resume) => (
            <div key={resume.id} className="border rounded-lg p-4 bg-white shadow-sm">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="font-medium text-gray-900">
                    {resume.user_email || 'No email'}
                  </p>
                  <p className="text-sm text-gray-500">
                    {new Date(resume.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-400">ID: {resume.id.slice(0, 8)}...</p>
                </div>
              </div>

              <div className="space-y-2">
                <div>
                  <span className="font-medium text-gray-700">Predicted Role:</span>
                  <span className="ml-2 text-blue-600">{resume.predicted_role || 'None'}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Match Score:</span>
                  <span className={`ml-2 font-medium ${
                    resume.match_score >= 0.8 ? 'text-green-600' :
                    resume.match_score >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {resume.match_score ? `${(resume.match_score * 100).toFixed(1)}%` : 'N/A'}
                  </span>
                </div>

                {resume.confirmed_role ? (
                  <div>
                    <span className="font-medium text-gray-700">Confirmed Role:</span>
                    <span className="ml-2 text-green-600 font-medium">
                      {resume.confirmed_role}
                    </span>
                  </div>
                ) : (
                  <div>
                    <p className="font-medium text-gray-700 mb-2">Confirm Role:</p>
                    <div className="flex gap-2 flex-wrap">
                      {availableRoles.map((role) => (
                        <button
                          key={role}
                          onClick={() => handleConfirmRole(resume.id, role)}
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
                        onClick={() => {
                          setShowAddRole(true);
                          setActiveResumeId(resume.id);
                        }}
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
                    {showAddRole && activeResumeId === resume.id && (
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
                            onClick={() => handleAddRole()}
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
                              setActiveResumeId(null);
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
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 