import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { useRecipeContext } from '@/contexts/RecipeContext';
import { apiService } from '@/services/api';

interface Recipe {
  id: number | string;
  name: string;
  time: string;
  servings: number;
  image: string;
  ingredients?: string[];
  instructions?: string[];
}

const mockRecipes: Recipe[] = [
  { id: 3, name: 'Grilled Chicken Salad', time: '25 min', servings: 2, image: '🥗' },
  { id: 6, name: 'Spaghetti Carbonara', time: '30 min', servings: 4, image: '🍝' },
  { id: 1, name: 'Avocado Toast', time: '10 min', servings: 1, image: '🥑' },
  { id: 2, name: 'Greek Yogurt Bowl', time: '3 min', servings: 1, image: '🥣' },
  { id: 5, name: 'Salmon with Vegetables', time: '30 min', servings: 2, image: '🐟' },
  { id: 4, name: 'Quinoa Buddha Bowl', time: '25 min', servings: 2, image: '🍲' },
];

const mealSuggestions = {
  'Breakfast': ['Tea', 'Coffee', 'Sandwich', 'Milk', 'Toast', 'Cereal'],
  'Lunch': ['Briyani', 'Rice', 'Onion raita', 'Curry', 'Salad', 'Soup'],
  'Dinner': ['Chapati', 'Dal kuruma', 'Vegetable curry', 'Rice', 'Roti'],
  'Snack': ['Biscuits', 'Fruits', 'Nuts', 'Juice', 'Chips']
};

const allMealSuggestions = Object.values(mealSuggestions).flat().map((meal, index) => ({
  id: `meal-${index}`,
  name: meal,
  time: '15 min',
  servings: 1,
  image: '🍽️'
}));

export const useDiscoverRecipes = () => {
  const { isAuthenticated } = useAuth();
  const { recipes: userCreatedRecipes } = useRecipeContext();

  const { data: discoverRecipes = [], isLoading } = useQuery({
    queryKey: ['discoverRecipes', isAuthenticated],
    queryFn: async () => {
      if (isAuthenticated) {
        const response = await apiService.getDiscoverRecipes();
        return response.recipes;
      } else {
        const savedRecipes = localStorage.getItem('guest_discover_recipes');
        let recipes = savedRecipes ? JSON.parse(savedRecipes) : [];
        
        try {
          const adminResponse = await apiService.getAdminRecipes();
          if (adminResponse.recipes?.length > 0) {
            recipes = [...recipes, ...adminResponse.recipes];
            localStorage.setItem('guest_discover_recipes', JSON.stringify(recipes));
          }
        } catch {}
        
        return recipes;
      }
    },
    staleTime: 5 * 60 * 1000,
    cacheTime: 10 * 60 * 1000,
  });

  const allRecipes = useMemo(() => {
    const userRecipes = userCreatedRecipes.map(recipe => ({
      id: recipe.id,
      name: recipe.title || recipe.name,
      time: recipe.cook_time ? `${recipe.cook_time} min` : '30 min',
      servings: recipe.servings || 1,
      image: '🍽️',
      ingredients: recipe.ingredients,
      instructions: recipe.instructions
    }));

    return [
      ...discoverRecipes,
      ...userRecipes,
      ...mockRecipes,
      ...allMealSuggestions
    ].filter((recipe, index, self) => 
      recipe?.name && 
      typeof recipe.name === 'string' &&
      index === self.findIndex(r => r.id === recipe.id)
    );
  }, [discoverRecipes, userCreatedRecipes]);

  return { allRecipes, loading: isLoading };
};