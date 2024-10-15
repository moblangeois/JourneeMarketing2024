import { useState, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Smartphone, Calendar, Image } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Textarea } from '../components/ui/textarea';


interface Persona {
  name: string;
  age: string;
  favoriteApps: string;
  socialNetworks: string[];
  personalHistory: string;
}


const PersonaCreationPage = () => {
  const navigate = useNavigate();
  const [persona, setPersona] = useState<Persona>({
    name: '',
    age: '',
    favoriteApps: '',
    socialNetworks: [],
    personalHistory: '',
  });

  const [isLoading, setIsLoading] = useState(false);

  const socialNetworkOptions = ['facebook', 'twitter', 'instagram', 'linkedin', 'tiktok'];

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setPersona(prev => ({ ...prev, [name]: value }));
  };

  const handleSocialNetworkClick = (network: string) => {
    setPersona(prev => ({
      ...prev,
      socialNetworks: prev.socialNetworks.includes(network)
        ? prev.socialNetworks.filter(n => n !== network)
        : [...prev.socialNetworks, network],
    }));
  };

  const handleGenerateImage = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/generate-persona-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ persona }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (data.image_url) {
        setGeneratedImageUrl(data.image_url);
      } else {
        throw new Error('No image URL received');
      }
    } catch (error: any) {
      console.error('Error generating image:', error);
      // Afficher un message d'erreur à l'utilisateur
      alert(`Erreur lors de la génération de l'image: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSavePersona = () => {
    const personaWithImage = {
      ...persona,
      imageUrl: generatedImageUrl, // Ajoutez l'URL de l'image générée à l'objet persona
    };
    localStorage.setItem('persona', JSON.stringify(personaWithImage));
    navigate('/keyword-generation');
  };

  const [generatedImageUrl, setGeneratedImageUrl] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-cover bg-center bg-fixed text-center" style={{ backgroundImage: "url('/low-poly-grid-haikei.svg')" }}>
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6 text-center text-white">Création de persona</h1>
        <Button className="w-full mb-6" onClick={handleSavePersona}>
          Continuer vers la génération de mots-clés
        </Button>
        <div className="flex flex-col lg:flex-row gap-6">
          <Card className="relative flex-1 lg:w-3/5">
            <CardHeader className="flex items-center justify-between">
              <div className="flex items-center">
                <CardTitle>Détails du persona</CardTitle>
              </div>
              <div className="flex space-x-2">
                {socialNetworkOptions.map((network) => (
                  <img
                    key={network}
                    src={`/icons/${network}.png`}
                    alt={network}
                    className={`w-10 h-10 cursor-pointer ${persona.socialNetworks.includes(network) ? 'opacity-100' : 'opacity-50'}`}
                    onClick={() => handleSocialNetworkClick(network)}
                  />
                ))}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <User className="text-gray-500" />
                  <Input
                    name="name"
                    placeholder="Nom"
                    value={persona.name}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Calendar className="text-gray-500" />
                  <Input
                    name="age"
                    type="number"
                    placeholder="Âge"
                    value={persona.age}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Smartphone className="text-gray-500" />
                  <Input
                    name="favoriteApps"
                    placeholder="Applications préférées"
                    value={persona.favoriteApps}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="flex items-start space-x-2">
                  <User className="text-gray-500 mt-2" />
                  <Textarea
                    name="personalHistory"
                    placeholder="Histoire personnelle"
                    value={persona.personalHistory}
                    onChange={handleInputChange}
                    rows={8}
                    className="w-full"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="flex-1 lg:w-2/5">
            <CardHeader>
            <div className="flex items-center">
              <CardTitle>Image du persona</CardTitle>
            </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center h-96 bg-gray-100 rounded-lg">
                {generatedImageUrl ? (
                  <img src={generatedImageUrl} alt="Generated Persona" className="max-h-full max-w-full object-contain" />
                ) : (
                  <>
                    <Image className="text-gray-400 mb-2" size={64} />
                    <p className="text-gray-500">L'image générée apparaîtra ici</p>
                  </>
                )}
              </div>
              <Button
                className="w-full mt-4"
                onClick={handleGenerateImage}
                disabled={isLoading}
              >
                {isLoading ? 'Génération...' : 'Générer l\'image'}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PersonaCreationPage;