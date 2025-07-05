import React, { useState } from 'react';

export default function App() {
  const [skills, setSkills] = useState('');
  const [prediction, setPrediction] = useState('');
  const [loading, setLoading] = useState(false);
  const [retrainMessage, setRetrainMessage] = useState('');

  const handlePredict = async () => {
    setLoading(true);
    setPrediction('');
    try {
      const res = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills: skills.split(',').map(s => s.trim()) }),
      });
      const data = await res.json();
      setPrediction(data.predicted_role);
    } catch (err) {
      console.error('Prediction error:', err);
      setPrediction('Error predicting role');
    } finally {
      setLoading(false);
    }
  };

  const handleRetrain = async () => {
    setRetrainMessage('');
    try {
      const res = await fetch('http://127.0.0.1:8000/retrain', {
        method: 'POST',
      });
      const data = await res.json();
      setRetrainMessage(data.message);
    } catch (err) {
      console.error('Retrain error:', err);
      setRetrainMessage('Failed to retrain model');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6 flex flex-col gap-6 items-center">
      <h1 className="text-3xl font-bold">Resume Skill Matcher</h1>

      <div className="bg-white p-6 rounded-xl shadow-md w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">Predict Role</h2>
        <input
          type="text"
          className="border rounded p-2 w-full mb-4"
          placeholder="Enter comma-separated skills (e.g., Python, React)"
          value={skills}
          onChange={e => setSkills(e.target.value)}
        />
        <button
          onClick={handlePredict}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {loading ? 'Predicting...' : 'Predict'}
        </button>
        {prediction && (
          <div className="mt-4 text-green-600 font-semibold">
            Predicted Role: {prediction}
          </div>
        )}
      </div>

      <div className="bg-white p-6 rounded-xl shadow-md w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">Retrain Model</h2>
        <button
          onClick={handleRetrain}
          className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
        >
          Retrain
        </button>
        {retrainMessage && (
          <p className="mt-4 text-sm text-gray-700">{retrainMessage}</p>
        )}
      </div>
    </div>
  );
}
