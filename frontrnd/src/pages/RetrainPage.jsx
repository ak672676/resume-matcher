import React, { useState } from 'react';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
export default function RetrainPage() {
  const [message, setMessage] = useState('');

  const handleRetrain = async () => {
    setMessage('');
    try {
      const res = await fetch(`${API_BASE_URL}/retrain`, { method: 'POST' });
      const data = await res.json();
      setMessage(data.message);
    } catch (err) {
      console.error('Retrain error:', err);
      setMessage('Retraining failed');
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Retrain Model</h2>
      <button
        onClick={handleRetrain}
        className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
      >
        Retrain
      </button>
      {message && <p className="mt-4 text-sm text-gray-700">{message}</p>}
    </div>
  );
}
