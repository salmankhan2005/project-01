import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Clock, Users, Heart, Share, Plus } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import { useSavedRecipes } from '@/contexts/SavedRecipesContext';
import { useState } from 'react';
import { toast } from 'sonner';

const recipeData = {
  1: {
    id: 1, name: 'Avocado Toast', image: '🥑', time: '5 min', servings: 1, category: 'Breakfast',
    ingredients: ['2 slices whole grain bread', '1 ripe avocado', 'Salt and pepper', 'Lemon juice', 'Red pepper flakes'],
    instructions: ['Toast bread slices', 'Mash avocado with salt, pepper, and lemon juice', 'Spread avocado on toast', 'Sprinkle with red pepper flakes']
  },
  2: {
    id: 2, name: 'Greek Yogurt Bowl', image: '🥣', time: '3 min', servings: 1, category: 'Breakfast',
    ingredients: ['1 cup Greek yogurt', '1/4 cup granola', '1/2 cup mixed berries', '1 tbsp honey', 'Chia seeds'],
    instructions: ['Add yogurt to bowl', 'Top with granola and berries', 'Drizzle with honey', 'Sprinkle chia seeds on top']
  },
  3: {
    id: 3, name: 'Grilled Chicken Salad', image: '🥗', time: '20 min', servings: 2, category: 'Lunch',
    ingredients: ['2 chicken breasts', 'Mixed salad greens', 'Cherry tomatoes', 'Cucumber', 'Olive oil & lemon juice'],
    instructions: ['Season chicken with salt and pepper', 'Grill chicken for 6-7 minutes per side', 'Prepare salad with greens, tomatoes, and cucumber', 'Slice chicken and serve over salad with dressing']
  },
  4: {
    id: 4, name: 'Quinoa Buddha Bowl', image: '🍲', time: '25 min', servings: 2, category: 'Lunch',
    ingredients: ['1 cup quinoa', 'Roasted vegetables', 'Chickpeas', 'Avocado', 'Tahini dressing'],
    instructions: ['Cook quinoa according to package directions', 'Roast vegetables in oven', 'Arrange quinoa, vegetables, and chickpeas in bowl', 'Top with avocado and tahini dressing']
  },
  5: {
    id: 5, name: 'Salmon with Vegetables', image: '🐟', time: '30 min', servings: 2, category: 'Dinner',
    ingredients: ['2 salmon fillets', 'Broccoli', 'Carrots', 'Olive oil', 'Garlic and herbs'],
    instructions: ['Preheat oven to 400°F', 'Season salmon with herbs', 'Toss vegetables with olive oil and garlic', 'Bake salmon and vegetables for 20 minutes']
  },
  6: {
    id: 6, name: 'Pasta Primavera', image: '🍝', time: '25 min', servings: 3, category: 'Dinner',
    ingredients: ['12 oz pasta', 'Mixed vegetables', 'Garlic', 'Olive oil', 'Parmesan cheese'],
    instructions: ['Cook pasta according to package directions', 'Sauté vegetables with garlic in olive oil', 'Toss pasta with vegetables', 'Serve with Parmesan cheese']
  }
};

export const RecipeDetail = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { savedRecipes, isRecipeSaved, saveRecipe, unsaveRecipe } = useSavedRecipes();
  const [addToMealPlanOpen, setAddToMealPlanOpen] = useState(false);
  const [selectedDay, setSelectedDay] = useState('');
  const [selectedMealTime, setSelectedMealTime] = useState('');
  
  const recipeId = parseInt(id || '0');
  const recipe = recipeData[recipeId as keyof typeof recipeData] || savedRecipes.find(r => r.id === recipeId);
  const isSaved = isRecipeSaved(recipeId);
  
  const handleSaveToggle = () => {
    if (!recipe) return;
    if (isSaved) {
      unsaveRecipe(recipe.id);
      toast.success('Recipe removed from saved');
    } else {
      saveRecipe(recipe);
      toast.success('Recipe saved!');
    }
  };
  
  const handleAddToMealPlan = () => {
    if (!selectedDay || !selectedMealTime) {
      toast.error('Please select day and meal time');
      return;
    }
    toast.success(`Added to ${selectedDay} ${selectedMealTime}`);
    setAddToMealPlanOpen(false);
  };
  
  if (!recipe) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">Recipe not found</h2>
          <Button onClick={() => navigate(-1)}>Go Back</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-6">
      <Header title="Recipe Details" showNotifications={false} />
      
      <main>
        {/* Hero Image */}
        <div className="relative h-48 sm:h-56 md:h-64 lg:h-80 bg-muted mb-4 sm:mb-6">
          <div className="absolute inset-0 flex items-center justify-center text-4xl sm:text-5xl md:text-6xl">
            {recipe.image}
          </div>
          <Button
            onClick={() => navigate(-1)}
            variant="ghost"
            size="icon"
            className="absolute top-3 left-3 sm:top-4 sm:left-4 bg-background/80 backdrop-blur-sm h-9 w-9 sm:h-10 sm:w-10"
          >
            <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5" />
          </Button>
          <div className="absolute bottom-3 right-3 sm:bottom-4 sm:right-4 flex gap-2">
            <Button 
              variant="ghost" 
              size="icon" 
              className="bg-background/80 backdrop-blur-sm h-9 w-9 sm:h-10 sm:w-10"
              onClick={handleSaveToggle}
            >
              <Heart className={`w-4 h-4 sm:w-5 sm:h-5 ${isSaved ? 'fill-red-500 text-red-500' : ''}`} />
            </Button>
            <Button variant="ghost" size="icon" className="bg-background/80 backdrop-blur-sm h-9 w-9 sm:h-10 sm:w-10">
              <Share className="w-4 h-4 sm:w-5 sm:h-5" />
            </Button>
          </div>
        </div>

        <div className="px-3 sm:px-4 md:px-6 lg:px-8 max-w-4xl mx-auto">
          <h1 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-heading font-bold mb-3 sm:mb-4">
            {recipe.name}
          </h1>

          <div className="flex gap-4 sm:gap-6 mb-4 sm:mb-6">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Clock className="w-5 h-5" />
              <span>{recipe.time}</span>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Users className="w-5 h-5" />
              <span>{recipe.servings} servings</span>
            </div>
          </div>

          <Card className="p-6 mb-6">
            <h2 className="text-xl font-heading font-semibold mb-4">Ingredients</h2>
            <ul className="space-y-2">
              {recipe.ingredients?.map((ingredient, index) => (
                <li key={index} className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full" />
                  <span>{ingredient}</span>
                </li>
              ))}
            </ul>
          </Card>

          <Card className="p-6 mb-6">
            <h2 className="text-xl font-heading font-semibold mb-4">Instructions</h2>
            <ol className="space-y-4">
              {recipe.instructions?.map((instruction, index) => (
                <li key={index} className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    {index + 1}
                  </span>
                  <p>{instruction}</p>
                </li>
              ))}
            </ol>
          </Card>

          <Button className="w-full h-12" onClick={() => setAddToMealPlanOpen(true)}>
            <Plus className="w-5 h-5 mr-2" />
            Add to Meal Plan
          </Button>
          
          {/* Add to Meal Plan Dialog */}
          <Dialog open={addToMealPlanOpen} onOpenChange={setAddToMealPlanOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add to Meal Plan</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <label className="text-sm font-medium">Day</label>
                  <Select value={selectedDay} onValueChange={setSelectedDay}>
                    <SelectTrigger className="mt-2">
                      <SelectValue placeholder="Select day" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Monday">Monday</SelectItem>
                      <SelectItem value="Tuesday">Tuesday</SelectItem>
                      <SelectItem value="Wednesday">Wednesday</SelectItem>
                      <SelectItem value="Thursday">Thursday</SelectItem>
                      <SelectItem value="Friday">Friday</SelectItem>
                      <SelectItem value="Saturday">Saturday</SelectItem>
                      <SelectItem value="Sunday">Sunday</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Meal Time</label>
                  <Select value={selectedMealTime} onValueChange={setSelectedMealTime}>
                    <SelectTrigger className="mt-2">
                      <SelectValue placeholder="Select meal time" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Breakfast">Breakfast</SelectItem>
                      <SelectItem value="Lunch">Lunch</SelectItem>
                      <SelectItem value="Snack">Snack</SelectItem>
                      <SelectItem value="Dinner">Dinner</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={handleAddToMealPlan} className="w-full">
                  Add to Plan
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </main>
    </div>
  );
};
