import React, { createContext, useContext, useState, useEffect } from 'react';

interface TourContextType {
  showTour: boolean;
  startTour: () => void;
  completeTour: () => void;
  shouldShowTour: () => boolean;
}

const TourContext = createContext<TourContextType | undefined>(undefined);

export const TourProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [showTour, setShowTour] = useState(false);

  const shouldShowTour = () => {
    // Check if tour has been completed for this session/device
    const tourCompleted = localStorage.getItem('genie-tour-completed');
    return !tourCompleted;
  };

  const startTour = () => {
    if (shouldShowTour()) {
      setShowTour(true);
    }
  };

  const completeTour = () => {
    setShowTour(false);
    localStorage.setItem('genie-tour-completed', 'true');
  };

  useEffect(() => {
    // Auto-start tour for new users/guests after a short delay
    const timer = setTimeout(() => {
      if (shouldShowTour()) {
        startTour();
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <TourContext.Provider value={{ showTour, startTour, completeTour, shouldShowTour }}>
      {children}
    </TourContext.Provider>
  );
};

export const useTour = () => {
  const context = useContext(TourContext);
  if (!context) {
    throw new Error('useTour must be used within a TourProvider');
  }
  return context;
};