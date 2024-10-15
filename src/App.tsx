import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import PersonaCreationPage from './pages/PersonaCreationPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/persona-creation" element={<PersonaCreationPage />} />
      </Routes>
    </Router>
  );
}

export default App;