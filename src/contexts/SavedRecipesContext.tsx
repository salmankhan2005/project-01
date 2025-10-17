import { createContext, useContext, useState, ReactNode, useEffect } from 'react';

interface Recipe {
  id: number;
  name: string;
  time: string;
  servings: number;
  image: string;
}

interface SavedRecipesContextType {
  savedRecipes: Recipe[];
  createdRecipes: Recipe[];
  saveRecipe: (recipe: Recipe) => void;
  unsaveRecipe: (recipeId: number) => void;
  isRecipeSaved: (recipeId: number) => boolean;
  createRecipe: (recipe: Recipe) => void;
  deleteCreatedRecipe: (recipeId: number) => void;
}

const SavedRecipesContext = createContext<SavedRecipesContextType | undefined>(undefined);

export const SavedRecipesProvider = ({ children }: { children: ReactNode }) => {
  const [savedRecipes, setSavedRecipes] = useState<Recipe[]>(() => {
    // Load from localStorage on initial load
    const saved = localStorage.getItem('savedRecipes');
    return saved ? JSON.parse(saved) : [];
  });

  const [createdRecipes, setCreatedRecipes] = useState<Recipe[]>(() => {
    // Load created recipes from localStorage
    const created = localStorage.getItem('createdRecipes');
    return created ? JSON.parse(created) : [];
  });

  // Save to localStorage whenever savedRecipes changes
  useEffect(() => {
    localStorage.setItem('savedRecipes', JSON.stringify(savedRecipes));
  }, [savedRecipes]);

  // Save to localStorage whenever createdRecipes changes
  useEffect(() => {
    localStorage.setItem('createdRecipes', JSON.stringify(createdRecipes));
  }, [createdRecipes]);

  const saveRecipe = (recipe: Recipe) => {
    setSavedRecipes(prev => {
      if (prev.find(r => r.id === recipe.id)) {
        return prev;
      }
      return [...prev, recipe];
    });
  };

  const unsaveRecipe = (recipeId: number) => {
    setSavedRecipes(prev => prev.filter(r => r.id !== recipeId));
  };

  const isRecipeSaved = (recipeId: number) => {
    return savedRecipes.some(r => r.id === recipeId);
  };

  const createRecipe = (recipe: Recipe) => {
    setCreatedRecipes(prev => [...prev, recipe]);
  };

  const deleteCreatedRecipe = (recipeId: number) => {
    setCreatedRecipes(prev => prev.filter(r => r.id !== recipeId));
  };

  return (
    <SavedRecipesContext.Provider value={{ 
      savedRecipes, 
      createdRecipes,
      saveRecipe, 
      unsaveRecipe, 
      isRecipeSaved,
      createRecipe,
      deleteCreatedRecipe
    }}>
      {children}
    </SavedRecipesContext.Provider>
  );
};

export const useSavedRecipes = () => {
  const context = useContext(SavedRecipesContext);
  if (context === undefined) {
    throw new Error('useSavedRecipes must be used within a SavedRecipesProvider');
  }
  return context;
};
