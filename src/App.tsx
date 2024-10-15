import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import PersonaCreationPage from './pages/PersonaCreationPage';
import KeywordGenerationPage from './pages/KeywordGenerationPage';
import BrandCreationPage from './pages/BrandCreationPage';
import QuestionnairePage from './pages/QuestionnairePage';
import PersonaCreationPage2 from './pages/PersonaCreationPage2';
import KeywordGenerationPage2 from './pages/KeywordGenerationPage2';
import BrandCreationPage2 from './pages/BrandCreationPage2';


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/persona-creation" element={<PersonaCreationPage />} />
        <Route path="/keyword-generation" element={<KeywordGenerationPage />} />
        <Route path="/brand-creation" element={<BrandCreationPage />} />
        <Route path="/questionnaire" element={<QuestionnairePage />} />
        <Route path="/persona-creation2" element={<PersonaCreationPage2 />} />
        <Route path="/keyword-generation2" element={<KeywordGenerationPage2 />} />
        <Route path="/brand-creation2" element={<BrandCreationPage2 />} />
      </Routes>
    </Router>
  );
}

export default App;