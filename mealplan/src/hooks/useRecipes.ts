import { useState, useEffect } from 'react';
import { recipeService, Recipe } from '@/services/recipeService';

export const useRecipes = () => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecipes = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await recipeService.getRecipes();
      setRecipes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch recipes');
    } finally {
      setLoading(false);
    }
  };

  const createRecipe = async (recipe: Omit<Recipe, 'id' | 'created_at' | 'updated_at'>) => {
    setLoading(true);
    setError(null);
    try {
      const newRecipe = await recipeService.createRecipe(recipe);
      setRecipes(prev => [...prev, newRecipe]);
      return newRecipe;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create recipe');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateRecipe = async (id: string, recipe: Partial<Recipe>) => {
    setLoading(true);
    setError(null);
    try {
      const updatedRecipe = await recipeService.updateRecipe(id, recipe);
      setRecipes(prev => prev.map(r => r.id === id ? updatedRecipe : r));
      return updatedRecipe;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update recipe');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteRecipe = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      await recipeService.deleteRecipe(id);
      setRecipes(prev => prev.filter(r => r.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete recipe');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getRecipe = async (id: string) => {
    try {
      const recipe = await recipeService.getRecipe(id);
      if (recipe) {
        // Track recipe access
        await recipeService.trackRecipeAccess(id);
      }
      return recipe;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get recipe');
      return null;
    }
  };

  const getAccessedRecipes = async () => {
    try {
      return await recipeService.getAccessedRecipes();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get accessed recipes');
      return [];
    }
  };

  useEffect(() => {
    fetchRecipes();
  }, []);

  return {
    recipes,
    loading,
    error,
    fetchRecipes,
    createRecipe,
    updateRecipe,
    deleteRecipe,
    getRecipe,
    getAccessedRecipes
  };
};