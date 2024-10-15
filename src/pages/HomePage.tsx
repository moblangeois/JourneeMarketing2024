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
          <Link to="/keyword-generation" className="transform transition-transform duration-300 hover:scale-105">
            <div className="bg-[#1d5f7d] text-white shadow-md rounded-lg p-6">
              <h2 className="text-2xl font-semibold mb-4">Génération de mots-clés</h2>
              <p className="mb-4">Générez des mots-clés pertinents basés sur le persona créé et visualisez-les dans un graphe interactif.</p>
            </div>
          </Link>
          <Link to="/brand-creation" className="transform transition-transform duration-300 hover:scale-105">
            <div className="bg-[#1d5f7d] text-white shadow-md rounded-lg p-6">
              <h2 className="text-2xl font-semibold mb-4">Création de marque</h2>
              <p className="mb-4">Créez une marque ciblée avec un logo, un nom et une publicité adaptée au persona et aux mots-clés générés.</p>
            </div>
          </Link>
          {/* Nouvelle tuile 1 */}
          <Link to="/persona-creation2" className="transform transition-transform duration-300 hover:scale-105">
            <div className="bg-[#1c7c6b] text-white shadow-md rounded-lg p-6">
              <h2 className="text-2xl font-semibold mb-4">Création de persona II</h2>
              <p className="mb-4">Deuxième version de la création de persona.</p>
            </div>
          </Link>
          {/* Nouvelle tuile 2 */}
          <Link to="/keyword-generation2" className="transform transition-transform duration-300 hover:scale-105">
            <div className="bg-[#1c7c6b] text-white shadow-md rounded-lg p-6">
              <h2 className="text-2xl font-semibold mb-4">Création de mots-clés II</h2>
              <p className="mb-4">Deuxième version de la création des mots-clés.</p>
            </div>
          </Link>
          {/* Nouvelle tuile 3 */}
          <Link to="/brand-creation2" className="transform transition-transform duration-300 hover:scale-105">
            <div className="bg-[#1c7c6b] text-white shadow-md rounded-lg p-6">
              <h2 className="text-2xl font-semibold mb-4">Création de marque II</h2>
              <p className="mb-4">Deuxième version de la création de la marque.</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
