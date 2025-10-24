import Lottie from 'lottie-react';
import genieAnimation from '../../Aladdin genie.json';

interface GenieAnimationProps {
  className?: string;
}

export const GenieAnimation = ({ className = "w-16 h-16" }: GenieAnimationProps) => {
  return (
    <div className={className}>
      <Lottie 
        animationData={genieAnimation}
        loop
        autoplay
      />
    </div>
  );
};