import { useState, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Search, Trash2 } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useMealPlan } from '@/contexts/MealPlanContext';
import { toast } from 'sonner';
import { sanitizeHtml } from '@/utils/security';

export const EditMeal = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { addToMealPlan } = useMealPlan();
  
  const day = searchParams.get('day') || '';
  const mealTime = searchParams.get('mealTime') || '';
  const currentMeal = searchParams.get('currentMeal') || '';
  const week = searchParams.get('week') || 'Week - 1';
  
  const [mealName, setMealName] = useState(currentMeal);
  const [searchQuery, setSearchQuery] = useState('');
  
  const mealSuggestions = {
    'Breakfast': ['Tea', 'Coffee', 'Sandwich', 'Milk', 'Toast', 'Cereal'],
    'Lunch': ['Briyani', 'Rice', 'Onion raita', 'Curry', 'Salad', 'Soup'],
    'Dinner': ['Chapati', 'Dal kuruma', 'Vegetable curry', 'Rice', 'Roti'],
    'Snack': ['Biscuits', 'Fruits', 'Nuts', 'Juice', 'Chips']
  };
  
  const [availableSuggestions, setAvailableSuggestions] = useState(() => {
    const deletedItems = JSON.parse(localStorage.getItem('deletedMealSuggestions') || '[]');
    const allSuggestions = mealSuggestions[mealTime as keyof typeof mealSuggestions] || [];
    return allSuggestions.filter(item => !deletedItems.includes(item));
  });
  
  const filteredSuggestions = availableSuggestions.filter(meal => 
    meal.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAdd = async () => {
    if (!mealName.trim()) {
      toast.error('Please enter a meal name');
      return;
    }

    try {
      await addToMealPlan({
        recipeId: `meal-${Date.now()}`,
        recipeName: sanitizeHtml(mealName.trim()),
        day: day,
        mealTime: mealTime,
        servings: 1,
        image: '🍽️',
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        week: week
      });

      toast.success('Meal updated successfully');
      navigate('/home');
    } catch (error) {
      toast.error('Failed to update meal');
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (mealName.trim()) {
      setMealName(prev => prev + ', ' + suggestion);
    } else {
      setMealName(suggestion);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header 
        title={`${day} / ${mealTime}`}
        showBackButton={true}
        onBackClick={() => navigate('/home')}
      />
      
      <main className="container-responsive py-6 space-y-6">
        <div>
          <Label htmlFor="meal-name">Meal Name</Label>
          <div className="flex gap-2 mt-2">
            <Input
              id="meal-name"
              placeholder="e.g., Coffee with toasts"
              value={mealName}
              onChange={(e) => setMealName(e.target.value)}
              className="flex-1"
            />
            <Button onClick={handleAdd} className="bg-green-500 hover:bg-green-600 px-6">
              Add
            </Button>
          </div>
        </div>
        
        <div className="border-2 border-green-500 rounded-lg p-4">
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search meals..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {filteredSuggestions.map((meal, idx) => (
              <div 
                key={idx} 
                className="flex items-center justify-between p-3 hover:bg-muted/50 rounded cursor-pointer"
                onClick={() => handleSuggestionClick(meal)}
              >
                <span className="text-green-600 font-medium">{meal}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 text-red-500 hover:text-red-600"
                  onClick={(e) => {
                    e.stopPropagation();
                    const deletedItems = JSON.parse(localStorage.getItem('deletedMealSuggestions') || '[]');
                    const updatedDeleted = [...deletedItems, meal];
                    localStorage.setItem('deletedMealSuggestions', JSON.stringify(updatedDeleted));
                    setAvailableSuggestions(prev => prev.filter(item => item !== meal));
                  }}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};