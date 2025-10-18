import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';

interface MealPlanItem {
  id: string;
  recipeId: string | number;
  recipeName: string;
  day: string;
  mealTime: string;
  servings?: number;
  image?: string;
  time?: string;
}

interface MealPlanContextType {
  mealPlan: Record<string, MealPlanItem[]>;
  addToMealPlan: (item: Omit<MealPlanItem, 'id'>) => Promise<void>;
  removeFromMealPlan: (id: string) => Promise<void>;
  getMealsForDay: (day: string) => MealPlanItem[];
  loading: boolean;
}

const MealPlanContext = createContext<MealPlanContextType | undefined>(undefined);

export const useMealPlan = () => {
  const context = useContext(MealPlanContext);
  if (!context) {
    throw new Error('useMealPlan must be used within a MealPlanProvider');
  }
  return context;
};

export const MealPlanProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [mealPlan, setMealPlan] = useState<Record<string, MealPlanItem[]>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      loadMealPlan();
    }
  }, [isAuthenticated]);

  const loadMealPlan = async () => {
    try {
      setLoading(true);
      const response = await apiService.getMealPlan();
      const planByDay: Record<string, MealPlanItem[]> = {};
      
      response.meal_plan.forEach((item: any) => {
        const mealItem: MealPlanItem = {
          id: item.id,
          recipeId: item.recipe_id,
          recipeName: item.recipe_name,
          day: item.day,
          mealTime: item.meal_time,
          servings: item.servings,
          image: item.image,
          time: item.time
        };
        
        if (!planByDay[item.day]) {
          planByDay[item.day] = [];
        }
        planByDay[item.day].push(mealItem);
      });
      
      setMealPlan(planByDay);
    } catch (error) {
      console.error('Failed to load meal plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToMealPlan = async (item: Omit<MealPlanItem, 'id'>) => {
    try {
      if (isAuthenticated) {
        await apiService.addToMealPlan({
          recipe_id: item.recipeId,
          recipe_name: item.recipeName,
          day: item.day,
          meal_time: item.mealTime,
          servings: item.servings,
          image: item.image,
          time: item.time
        });
        await loadMealPlan();
      } else {
        // Fallback to localStorage for guest users
        const newItem: MealPlanItem = {
          ...item,
          id: `${item.day}-${item.mealTime}-${Date.now()}`
        };
        setMealPlan(prev => ({
          ...prev,
          [item.day]: [
            ...(prev[item.day] || []).filter(meal => meal.mealTime !== item.mealTime),
            newItem
          ]
        }));
      }
    } catch (error) {
      console.error('Failed to add to meal plan:', error);
      throw error;
    }
  };

  const removeFromMealPlan = async (id: string) => {
    try {
      if (isAuthenticated) {
        await apiService.removeFromMealPlan(id);
        await loadMealPlan();
      } else {
        setMealPlan(prev => {
          const newPlan = { ...prev };
          Object.keys(newPlan).forEach(day => {
            newPlan[day] = newPlan[day].filter(meal => meal.id !== id);
          });
          return newPlan;
        });
      }
    } catch (error) {
      console.error('Failed to remove from meal plan:', error);
      throw error;
    }
  };

  const getMealsForDay = (day: string) => {
    return mealPlan[day] || [];
  };

  return (
    <MealPlanContext.Provider value={{
      mealPlan,
      addToMealPlan,
      removeFromMealPlan,
      getMealsForDay,
      loading
    }}>
      {children}
    </MealPlanContext.Provider>
  );
};