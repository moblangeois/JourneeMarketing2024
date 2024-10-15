import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-cover bg-center bg-fixed text-center" style={{ backgroundImage: "url('/low-poly-grid-haikei.svg')" }}>
      <div className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-center mb-8 text-white">Bienvenue aux Ateliers IA/Marketing</h1>
        <div className="grid md:grid-cols-3 gap-6">
          <Link to="/persona-creation" className="transform transition-transform duration-300 hover:scale-105">
            <div className="bg-[#1d5f7d] text-white shadow-md rounded-lg p-6">
              <h2 className="text-2xl font-semibold mb-4">Création de persona</h2>
              <p className="mb-4">Créez un persona détaillé avec une histoire, des préférences et une image générée par IA.</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
