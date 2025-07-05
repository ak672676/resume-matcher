import React, { useState } from "react";

const ResumeForm = () => {
  const [email, setEmail] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_email: email, resume_text: resumeText }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      alert("Something went wrong");
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="email"
        placeholder="Your email"
        className="w-full p-2 border rounded"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <textarea
        placeholder="Paste your resume text here..."
        className="w-full p-2 border rounded h-40"
        value={resumeText}
        onChange={(e) => setResumeText(e.target.value)}
        required
      />
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        disabled={loading}
      >
        {loading ? "Analyzing..." : "Analyze Resume"}
      </button>

      {result && (
        <div className="mt-6 p-4 bg-green-50 border border-green-300 rounded">
          <h2 className="text-lg font-semibold">Prediction Result</h2>
          <p><strong>Predicted Role:</strong> {result.predicted_role}</p>
          <p><strong>Skills:</strong> {result.skills.join(", ")}</p>
        </div>
      )}
    </form>
  );
};

export default ResumeForm;
