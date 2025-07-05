import React, { useState } from 'react';

export default function PredictPage() {
  const [skills, setSkills] = useState('');
  const [prediction, setPrediction] = useState('');
  const [loading, setLoading] = useState(false);

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

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Predict Role</h2>
      <input
        type="text"
        className="border rounded p-2 w-full mb-4"
        placeholder="Enter comma-separated skills"
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
  );
}
