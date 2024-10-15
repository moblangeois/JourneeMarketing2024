import { useState, useEffect, ReactNode } from 'react';
import { Sparkles, Camera, Eye } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { useNavigate } from 'react-router-dom';


// Définir une interface pour les props du composant Modal
interface ModalProps {
  children: ReactNode;
  isVisible: boolean;
  onClose: () => void;
}

// Composant pour afficher la modale
const Modal = ({ children, isVisible, onClose }: ModalProps) => {
  if (!isVisible) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white rounded-lg w-11/12 max-w-3xl p-4">
        <button className="text-gray-500 hover:text-gray-700 float-right" onClick={onClose}>X</button>
        {children}
      </div>
    </div>
  );
};

const BrandCreationPage = () => {
  const [brand, setBrand] = useState({ name: '', slogan: '' });
  const [ad, setAd] = useState({ title: '', description: '' });
  const [logo, setLogo] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [entityType] = useState<string>('association a but non lucratif pour le developpement durable');
  const navigate = useNavigate();
  
  // Ajout de l'état pour la modale
  const [isModalVisible, setIsModalVisible] = useState(false);

  useEffect(() => {
    const storedKeywords = localStorage.getItem('keywords');
    const keywords = storedKeywords ? JSON.parse(storedKeywords) : [];
    console.log('Keywords:', keywords);
  }, []);

  const generateBrandAndAd = async () => {
    setIsLoading(true);
    setError(null);
  
    try {
      const storedKeywords = localStorage.getItem('keywords');
      const keywords = storedKeywords ? JSON.parse(storedKeywords) : [];
  
      if (keywords.length === 0) {
        throw new Error('No keywords found. Please generate keywords first.');
      }
  
      const brandResponse = await fetch('http://localhost:5000/generate-brand', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keywords, entityType }), // Passer entityType à l'API
      });
  
      if (!brandResponse.ok) {
        throw new Error(`HTTP error! status: ${brandResponse.status}`);
      }
  
      const brandData = await brandResponse.json();
      setBrand(brandData);

      const adResponse = await fetch('http://localhost:5000/generate-ad', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keywords, brand: brandData, entityType }), // Passer entityType à l'API
      });
  
      if (!adResponse.ok) {
        throw new Error(`HTTP error! status: ${adResponse.status}`);
      }
  
      const adData = await adResponse.json();
      setAd(adData);
    } catch (error) {
      console.error('Error:', error);
      setError('Une erreur est survenue lors de la génération de la marque et de la publicité.');
    } finally {
      setIsLoading(false);
    }
  };

  const generateLogo = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/generate-logo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brand }),
      });
      const data = await response.json();
      setLogo(data.logo_url);
    } catch (error) {
      setError('Une erreur est survenue lors de la génération du logo.');
    } finally {
      setIsLoading(false);
    }
  };

  // Contenu de la publicité en contexte avec d'autres posts
  const renderInContext = () => {
    const dummyPosts = [
      { user: 'Alexis Lambert', content: 'J’ai testé un nouveau parcours de randonnée, magnifique vue ! 🏞️', avatar: 'Avatar1.png' },
      { user: 'Samira Belhaj', content: 'Nouveau livre terminé, une lecture passionnante sur l’innovation durable 📚🌍', avatar: 'Avatar2.png' },
      { user: 'Léo Nguyen', content: "Découvrez cette plateforme d'apprentissage que j’utilise pour élargir mes compétences en ligne 🎓💻", avatar: 'Avatar3.png' },
    ];

    return (
      <div className="space-y-4">
        {dummyPosts.map((post, index) => (
          <div key={index} className="border p-4 rounded-lg bg-white shadow-md flex items-center">
  <img src={post.avatar} alt="avatar" className="w-10 h-10 rounded-full mr-4 object-cover" />
  <div className="flex flex-col justify-start items-start">
    <p className="font-bold text-gray-900">{post.user}</p>
    <p className="text-gray-700">{post.content}</p>
  </div>
</div>

        ))}
        {/* Ajout de la publicité de la marque au centre */}
        <div className="border p-4 rounded-lg bg-white shadow-md">
          <div className="flex items-center mb-2">
            {logo ? (
              <img src={logo} alt="Logo de la marque" className="w-10 h-10 rounded-full mr-3 object-cover" />
            ) : (
              <div className="w-10 h-10 bg-gray-300 rounded-full mr-3 flex items-center justify-center">
                <Camera className="text-gray-400" size={24} />
              </div>
            )}
            <div>
              <p className="font-bold">{brand.name || "Nom de la marque"}</p>
              <p className="text-sm text-gray-500">Sponsorisé</p>
            </div>
          </div>
          <p className="font-semibold mb-2 text-left">{ad.title || "Titre de la publicité"}</p>
          <p className="text-sm mb-4 text-left">{ad.description || "Description de la publicité"}</p>
          <Button variant="outline" className="w-full">En savoir plus</Button>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-cover bg-center bg-fixed text-center" style={{backgroundImage: "url('/low-poly-grid-haikei.svg')"}}>
      <div className="container mx-auto p-4 max-w-9xl">
        <h1 className="text-3xl font-bold mb-6 text-center text-white">Création de marque et publicité</h1>

        {error && <div className="text-red-500 mb-4">{error}</div>}

        {/* Section de la marque et du logo */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Marque */}
          <Card className="flex flex-col">
            <CardHeader>
              <CardTitle>Génération de marque</CardTitle>
            
            </CardHeader>
            <CardContent className="flex-grow">
              <div className="flex flex-col h-full">
                <div className="flex-grow">
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold mb-2">Nom de la marque</h3>
                    <div className="bg-gray-100 p-3 rounded-md">{brand.name || "Pas encore généré"}</div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Slogan</h3>
                    <div className="bg-gray-100 p-3 rounded-md">{brand.slogan || "Pas encore généré"}</div>
                  </div>
                </div>
                <div className="mt-auto">
                  <Button onClick={() => generateBrandAndAd()} className="w-full" disabled={isLoading}>
                    <Sparkles className="mr-2" />
                    {isLoading ? 'Génération...' : 'Générer la marque'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Logo */}
          <Card>
            <CardHeader>
              <CardTitle>Logo de la marque</CardTitle>
            </CardHeader>
            <CardContent>
              {logo ? (
                <img src={logo} alt="Logo généré" className="w-full h-48 object-contain mb-4" />
              ) : (
                <div className="flex flex-col items-center justify-center h-48 bg-gray-100 rounded-lg mb-4">
                  <Camera className="text-gray-400 mb-2" size={48} />
                  <p className="text-gray-500">Le logo généré apparaîtra ici</p>
                </div>
              )}
              <Button onClick={generateLogo} className="w-full" disabled={isLoading || !brand.name}>
                <Camera className="mr-2" />
                {isLoading ? 'Génération...' : 'Générer le logo'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Aperçu de la publicité sur le réseau social */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Aperçu de la publicité sur réseau social</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="border p-4 rounded-lg bg-white shadow-md">
              <div className="flex items-center mb-2">
                {logo ? (
                  <img src={logo} alt="Logo de la marque" className="w-10 h-10 rounded-full mr-3 object-cover" />
                ) : (
                  <div className="w-10 h-10 bg-gray-300 rounded-full mr-3 flex items-center justify-center">
                    <Camera className="text-gray-400" size={24} />
                  </div>
                )}
                <div>
                  <p className="font-bold">{brand.name || "Nom de la marque"}</p>
                  <p className="text-sm text-gray-500">Sponsorisé</p>
                </div>
              </div>
              <p className="font-semibold mb-2 text-left">{ad.title || "Titre de la publicité"}</p>
              <p className="text-sm mb-4 text-left">{ad.description || "Description de la publicité"}</p>
              <Button variant="outline" className="w-full" onClick={() => setIsModalVisible(true)}>
                <Eye className="mr-2" /> Voir en contexte
              </Button>
            </div>
<Button variant="outline" className="w-full mt-4" onClick={() => navigate('/questionnaire')}>
  Continuer vers le questionnaire
</Button>
          </CardContent>
        </Card>

        {/* Modale avec l'aperçu en contexte */}
        <Modal isVisible={isModalVisible} onClose={() => setIsModalVisible(false)}>
          <h2 className="text-2xl font-bold mb-4 text-center">Publicité en contexte</h2>
          {renderInContext()}
        </Modal>
      </div>
    </div>
  );
};

export default BrandCreationPage;