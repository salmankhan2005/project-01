import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChefHat } from 'lucide-react';

export const Splash = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/onboarding');
    }, 2000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-primary to-primary-hover">
      <div className="animate-scale-in">
        <div className="bg-white/20 backdrop-blur-lg rounded-full p-8 mb-6">
          <ChefHat className="w-24 h-24 text-white" strokeWidth={1.5} />
        </div>
        <h1 className="text-4xl font-heading font-bold text-white text-center mb-2">
          FreshPlate
        </h1>
        <p className="text-white/80 text-center">Your kitchen companion</p>
      </div>
    </div>
  );
};
