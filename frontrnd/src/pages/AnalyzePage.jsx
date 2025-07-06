import React, { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default function AnalyzePage() {
  const [email, setEmail] = useState('');
  const [resumeText, setResumeText] = useState('');
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    setResult(null);
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
              <p><strong>Predicted Role:</strong> {result.predicted_role}</p>
              <p><strong>Extracted Skills:</strong> {result.skills.join(', ')}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
