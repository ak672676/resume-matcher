import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import PredictPage from './pages/PredictPage';
import RetrainPage from './pages/RetrainPage';
import ResumesPage from './pages/ResumesPage';
import RolesPage from './pages/RolesPage';
import UploadPage from './pages/UploadPage';
import './index.css';
import Home from './components/Home';


ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/predict" element={<PredictPage />} />
      <Route path="/retrain" element={<RetrainPage />} />
      <Route path="/upload" element={<UploadPage />} />
      <Route path="/resumes" element={<ResumesPage />} />
      <Route path="/roles" element={<RolesPage />} />
    </Routes>
  </BrowserRouter>
);
