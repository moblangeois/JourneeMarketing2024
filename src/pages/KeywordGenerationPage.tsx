import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Tag } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';

interface Keyword {
  word: string;
  importance: number; // Entre 1 et 10
  explanation: string;
  currentBid?: number;
}

interface Persona {
  name: string;
  age: string;
  favoriteApps: string; // Peut-être une chaîne de texte séparée par des virgules
  socialNetworks: string; // Peut-être une chaîne de texte séparée par des virgules
  personalHistory: string;
  imageUrl?: string; // Ajout d'un champ pour l'URL de l'image
}

const KeywordGenerationPage = () => {
  const navigate = useNavigate();
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [selectedKeyword, setSelectedKeyword] = useState<Keyword | null>(null);
  const [showAllExplanations, setShowAllExplanations] = useState(false);
  const [persona, setPersona] = useState<Persona | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [, setError] = useState<string | null>(null);

  useEffect(() => {
    const storedPersona = localStorage.getItem('persona');
    if (storedPersona) {
      const parsedPersona = JSON.parse(storedPersona);
      console.log("Données du persona récupérées :", parsedPersona);
      setPersona(parsedPersona);
    }
  }, []);

  const handleContinue = () => {
    navigate('/brand-creation');
  };

  const generateKeywords = async () => {
    if (!persona) {
      console.error('No persona data available');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/generate-keywords', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ persona }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setKeywords(data.keywords);
      localStorage.setItem('keywords', JSON.stringify(data.keywords));
      setIsLoading(false);
    } catch (error) {
      console.error('Error generating keywords:', error);
      setError('Une erreur est survenue lors de la génération des mots-clés.');
      setIsLoading(false);
    }
  };

  const handleKeywordClick = (keyword: Keyword) => {
    setSelectedKeyword(keyword);
    setShowAllExplanations(false);
  };

  const toggleAllExplanations = () => {
    setShowAllExplanations(!showAllExplanations);
    setSelectedKeyword(null);
  };

  return (
<div className="min-h-screen bg-cover bg-center bg-fixed bg-no-repeat text-center" style={{ backgroundImage: "url('/low-poly-grid-haikei.svg')" }}>
  <div className="container mx-auto p-4 max-w-9xl pb-8">
    <h1 className="text-3xl font-bold mb-6 text-center text-white">Génération de mots-clés</h1>
    <Button className="w-full mt-6 mb-6" onClick={handleContinue}>
      Continuer vers la création de marque
    </Button>
    
    {/* Grid layout */}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      {/* Encart des détails du persona */}
{/* Encart des détails du persona */}
{persona && (
  <Card className="flex flex-col h-full mb-4 items-center justify-center text-center p-4">
    <CardHeader>
      <CardTitle>Détails du persona</CardTitle>
    </CardHeader>
    <CardContent className="flex-grow">
      {/* Affichage de l'image du persona */}
      {persona.imageUrl && (
        <img
          src={persona.imageUrl}
          alt={`${persona.name}`}
          className="w-32 h-32 rounded-full mb-4 mx-auto object-cover"
        />
      )}
      
      {/* Affichage du nom et de l'âge */}
      <p className="text-lg font-semibold">
        {persona.name} <span className="text-gray-500">- {persona.age} ans</span>
      </p>
      
      {/* Applications préférées sur une ligne */}
      <p className="text-lg font-semibold mt-4">Applications préférées :</p>
      <p className="text-sm">
        {persona.favoriteApps.split(',').map(app => app.trim()).join(', ')}
      </p>

      {/* Réseaux sociaux avec des icônes */}
      <p className="text-lg font-semibold mt-4">Réseaux sociaux :</p>
      <div className="flex space-x-2 justify-center">
        {(Array.isArray(persona.socialNetworks)
          ? persona.socialNetworks
          : persona.socialNetworks.split(',')
        ).map((network, index) => (
          <img
            key={index}
            src={`/icons/${network.trim()}.png`}
            alt={network.trim()}
            className="w-10 h-10"
          />
        ))}
      </div>
    </CardContent>
  </Card>
)}




      {/* Encart des mots-clés générés */}
      <Card className="flex flex-col h-full"> {/* Ajout de h-full */}
        <CardHeader>
          <CardTitle>Mots-clés générés</CardTitle>
        </CardHeader>
        <CardContent className="flex-grow">
          <div className="flex flex-wrap gap-2 mb-4">
            {keywords.map((keyword, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold cursor-pointer hover:bg-blue-200"
                onClick={() => handleKeywordClick(keyword)}
              >
                {keyword.word}
              </span>
            ))}
          </div>
          <Button onClick={toggleAllExplanations} className="w-full mt-4">
            {showAllExplanations ? "Masquer les explications" : "Afficher toutes les explications"}
          </Button>
        </CardContent>
        <div className="p-4 mt-auto">
          <Button onClick={generateKeywords} className="w-full" disabled={isLoading}>
            <Tag className="mr-2" />
            {isLoading ? 'Génération en cours...' : 'Générer les mots-clés'}
          </Button>
        </div>
      </Card>
    </div>

    {/* Encart d'explication étendu sur deux colonnes */}
    <Card className="col-span-1 md:col-span-2"> {/* Ajout de col-span-2 pour occuper la largeur des deux colonnes */}
      <CardHeader>
        <CardTitle>Explication</CardTitle>
      </CardHeader>
      <CardContent>
      <div className="sm:col-span-6 mt-4">
              <div className="mt-2 max-h-60 overflow-y-auto">
                {selectedKeyword ? (
                  <div className="p-2 border-b border-gray-300">
                    <h3 className="font-semibold">{selectedKeyword.word}</h3>
                    <p className="text-sm">{selectedKeyword.explanation}</p>
                  </div>
                ) : showAllExplanations ? (
                  keywords.map((keyword, index) => (
                    <div key={index} className="p-2 border-b border-gray-300">
                      <h3 className="font-semibold">{keyword.word}</h3>
                      <p className="text-sm">{keyword.explanation}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm">Cliquez sur un mot-clé pour voir son explication ou utilisez le bouton ci-dessus pour tout afficher.</p>
                )}
              </div>
          </div>
      </CardContent>
    </Card>
  </div>
</div>
  );
};

export default KeywordGenerationPage;
