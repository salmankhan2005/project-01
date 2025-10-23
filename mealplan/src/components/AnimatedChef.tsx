import { ChefHat } from 'lucide-react';

interface AnimatedChefProps {
  size?: number;
  className?: string;
}

export const AnimatedChef = ({ size = 24, className = "" }: AnimatedChefProps) => {
  return (
    <div className={`relative ${className}`}>
      <ChefHat 
        size={size} 
        className="animate-bounce text-primary hover:text-primary-hover transition-colors duration-200" 
        style={{ animationDuration: '2s' }}
      />
      <div className="absolute -top-1 -right-1 w-2 h-2 bg-yellow-400 rounded-full animate-ping" />
    </div>
  );
};