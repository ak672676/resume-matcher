import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import PredictPage from './pages/PredictPage';
import RetrainPage from './pages/RetrainPage';
import AnalyzePage from './pages/AnalyzePage';
import './index.css';
import Home from './components/Home';


ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/predict" element={<PredictPage />} />
      <Route path="/retrain" element={<RetrainPage />} />
      <Route path="/analyze" element={<AnalyzePage />} />
    </Routes>
  </BrowserRouter>
);
