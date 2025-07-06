import React, { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function AnalyzePage() {
  const [email, setEmail] = useState('');
  const [resumeText, setResumeText] = useState('');
  const [result, setResult] = useState(null);
  const [confirming, setConfirming] = useState(false);
  const [confirmationMessage, setConfirmationMessage] = useState('');

  const handleAnalyze = async () => {
    setResult(null);
    setConfirmationMessage('');
    try {
      const res = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_email: email, resume_text: resumeText }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error('Analyze error:', err);
      setResult({ error: 'Failed to analyze resume' });
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
      <textarea
        placeholder="Paste resume text here..."
        className="border p-2 w-full h-32 mb-4 rounded"
        value={resumeText}
        onChange={(e) => setResumeText(e.target.value)}
      />
      <button
        onClick={handleAnalyze}
        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
      >
        Analyze
      </button>
      {result && (
        <div className="mt-4 text-sm text-gray-700 space-y-2">
          {result.error ? (
            <p className="text-red-600">{result.error}</p>
          ) : (
            <>
              <p><strong>Resume ID:</strong> {result.id}</p>
              <p><strong>Predicted Role:</strong> {result.predicted_role}</p>
              <p><strong>Extracted Skills:</strong> {result.skills.join(', ')}</p>
              
              {result.confirmed_role ? (
                <p className="text-green-600">
                  <strong>Confirmed Role:</strong> {result.confirmed_role}
                </p>
              ) : (
                <div className="mt-4">
                  <p className="mb-2"><strong>Confirm Role:</strong></p>
                  <div className="flex gap-2 flex-wrap">
                    {[
                      'Full Stack Developer', 'Frontend Developer', 'Backend Developer',
                      'Data Scientist', 'Data Analyst', 'DevOps Engineer', 'Mobile Developer',
                      'UI/UX Designer', 'Product Manager', 'QA Engineer', 'Machine Learning Engineer',
                      'Cloud Engineer', 'Security Engineer', 'Database Administrator', 'Network Engineer'
                    ].map((role) => (
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
                  </div>
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
