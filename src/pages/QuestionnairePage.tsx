import { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { useNavigate } from 'react-router-dom';

interface Question {
  id: number;
  theme: string;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
}

const QuestionnairePage = () => {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedOptionIndex, setSelectedOptionIndex] = useState<number | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [score, setScore] = useState(0);

  // Charger les questions personnalisées
  useEffect(() => {
    // Vous pouvez personnaliser les questions en fonction des données stockées dans le localStorage
    const storedPersona = localStorage.getItem('persona');
    const storedKeywords = localStorage.getItem('keywords');
    const storedBrand = localStorage.getItem('brand');

    // Exemple de questions personnalisées
    const generatedQuestions: Question[] = [
      {
        id: 1,
        theme: 'Stéréotypes en marketing',
        question: 'Lors de la création de votre persona, quels éléments pourraient renforcer des stéréotypes marketing ?',
        options: [
          'Utiliser des clichés basés sur l’âge ou le genre',
          'Personnaliser les préférences en fonction de données spécifiques',
          'Considérer les motivations profondes du persona',
          'Éviter toute généralisation lors de la création du persona',
        ],
        correctAnswer: 0,
        explanation: 'Utiliser des clichés basés sur l’âge ou le genre peut renforcer des stéréotypes en marketing.',
      },
      {
        id: 2,
        theme: 'Nudge Marketing',
        question: 'Le nudge marketing vise à :',
        options: [
          'Manipuler les consommateurs pour qu’ils achètent plus',
          'Interdire certaines options pour orienter le choix',
          'Influencer subtilement les décisions sans restreindre les choix',
          'Ignorer le comportement des consommateurs',
        ],
        correctAnswer: 2,
        explanation: 'Le nudge marketing influence subtilement les décisions sans restreindre les choix.',
      },
      {
        id: 3,
        theme: 'Intelligence Artificielle',
        question: 'Lors de la génération automatique du logo, quel est un risque potentiel lié à l’IA ?',
        options: [
          'Obtenir un logo totalement unique',
          'Renforcer des biais présents dans les données d’entraînement',
          'Réduire le temps de création',
          'Faciliter la personnalisation selon les préférences',
        ],
        correctAnswer: 1,
        explanation: 'L’IA peut renforcer des biais présents dans les données d’entraînement, affectant la diversité des résultats.',
      },
      // Ajoutez d'autres questions si nécessaire
    ];

    setQuestions(generatedQuestions);
  }, []);

  const handleOptionSelect = (index: number) => {
    setSelectedOptionIndex(index);
  };

  const handleNextQuestion = () => {
    if (selectedOptionIndex === questions[currentQuestionIndex].correctAnswer) {
      setScore(score + 1);
    }
    setShowExplanation(true);
  };

  const handleContinue = () => {
    setShowExplanation(false);
    setSelectedOptionIndex(null);
    if (currentQuestionIndex + 1 < questions.length) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      navigate('/summary'); // Redirige vers une page de résumé ou une autre page
    }
  };

  return (
    <div
      className="min-h-screen bg-cover bg-center bg-fixed text-center"
      style={{ backgroundImage: "url('/low-poly-grid-haikei.svg')" }}
    >
      <div className="container mx-auto p-4 max-w-3xl">
        <h1 className="text-3xl font-bold mb-6 text-center text-white">Questionnaire Réflexion</h1>
        <Card>
          <CardHeader>
            <CardTitle>{questions[currentQuestionIndex]?.theme}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <p className="text-lg font-semibold">
                {questions[currentQuestionIndex]?.question}
              </p>
            </div>
            <div className="space-y-2">
              {questions[currentQuestionIndex]?.options.map((option, index) => (
                <div
                  key={index}
                  className={`p-3 border rounded-md cursor-pointer ${
                    selectedOptionIndex === index ? 'bg-blue-100 border-blue-500' : 'bg-white'
                  }`}
                  onClick={() => handleOptionSelect(index)}
                >
                  {option}
                </div>
              ))}
            </div>
            {!showExplanation ? (
              <Button
                className="w-full mt-4"
                onClick={handleNextQuestion}
                disabled={selectedOptionIndex === null}
              >
                Valider
              </Button>
            ) : (
              <div className="mt-4">
                <p className="text-sm text-left">
                  {questions[currentQuestionIndex]?.explanation}
                </p>
                <Button className="w-full mt-4" onClick={handleContinue}>
                  {currentQuestionIndex + 1 < questions.length ? 'Question Suivante' : 'Terminer'}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
        <p className="text-white mt-4">
          Question {currentQuestionIndex + 1} sur {questions.length}
        </p>
      </div>
    </div>
  );
};

export default QuestionnairePage;
