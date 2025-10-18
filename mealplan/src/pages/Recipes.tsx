import { useState, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import { BottomNav } from '@/components/layout/BottomNav';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus, Search, Clock, Users, BookmarkX, CalendarPlus } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useSavedRecipes } from '@/contexts/SavedRecipesContext';
import { useToast } from '@/hooks/use-toast';
import { LottieAnimation } from '@/components/LottieAnimation';
import { GlowCard } from '@/components/GlowCard';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';

const relevantRecipes = [
  { id: 1, name: 'Avocado Toast', image: '🥑', time: '5 min', servings: 1, category: 'Breakfast' },
  { id: 2, name: 'Greek Yogurt Bowl', image: '🥣', time: '3 min', servings: 1, category: 'Breakfast' },
  { id: 3, name: 'Grilled Chicken Salad', image: '🥗', time: '20 min', servings: 2, category: 'Lunch' },
  { id: 4, name: 'Quinoa Buddha Bowl', image: '🍲', time: '25 min', servings: 2, category: 'Lunch' },
  { id: 5, name: 'Salmon with Vegetables', image: '🐟', time: '30 min', servings: 2, category: 'Dinner' },
  { id: 6, name: 'Pasta Primavera', image: '🍝', time: '25 min', servings: 3, category: 'Dinner' },
];

export const Recipes = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [dbSavedRecipes, setDbSavedRecipes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { savedRecipes, unsaveRecipe } = useSavedRecipes();
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      loadSavedRecipes();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const loadSavedRecipes = async () => {
    try {
      const response = await apiService.getSavedRecipesNew();
      setDbSavedRecipes(response.saved_recipes.map(item => ({
        id: item.recipe_id,
        name: item.recipe_data?.name || item.recipe_data?.title || item.recipe_name || 'Untitled Recipe',
        image: item.recipe_data?.image || '🍽️',
        time: item.recipe_data?.time || '30 min',
        servings: item.recipe_data?.servings || 1,
        category: item.recipe_data?.category || 'Other'
      })));
    } catch (error) {
      console.error('Failed to load saved recipes:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredRelevantRecipes = relevantRecipes.filter(recipe => {
    const matchesSearch = recipe.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || recipe.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Combine database saved recipes with local saved recipes
  const allSavedRecipes = [...dbSavedRecipes, ...savedRecipes];
  
  // Remove duplicates based on ID
  const uniqueSavedRecipes = allSavedRecipes.filter((recipe, index, self) => 
    index === self.findIndex(r => r.id === recipe.id)
  );
  
  // Filter saved recipes by search and selected category
  const filteredSavedRecipes = uniqueSavedRecipes.filter((recipe) => {
    const matchesSearch = recipe.name.toLowerCase().includes(searchQuery.toLowerCase());
    const recipeCategory = recipe.category;
    const matchesCategory = selectedCategory === 'All' || recipeCategory === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleUnsave = async (recipeId: number | string, recipeName: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    try {
      if (isAuthenticated) {
        await apiService.unsaveRecipeNew(String(recipeId));
        // Remove from database saved recipes
        setDbSavedRecipes(prev => prev.filter(recipe => recipe.id !== recipeId));
      }
      
      // Also remove from local saved recipes
      unsaveRecipe(recipeId);
      
      toast({
        title: "Recipe removed",
        description: `${recipeName} removed from your recipes`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to remove recipe. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleAddToMeal = (recipe: typeof relevantRecipes[0], e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    toast({
      title: "Added to meal plan",
      description: `${recipe.name} added to your meal plan`,
    });
  };

  return (
    <div className="min-h-screen bg-background pb-20 sm:pb-24">
      <Header 
        title="Recipes" 
        showBackButton={true}
        onBackClick={() => navigate(-1)}
      />
      
      <main className="px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 md:py-8 max-w-7xl mx-auto">
        {/* Search Bar */}
        <div className="relative mb-4 sm:mb-6 animate-fade-in">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-muted-foreground pointer-events-none" />
          <Input
            placeholder="Search recipes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 sm:pl-10 h-10 sm:h-12 text-sm sm:text-base"
          />
        </div>



        {/* Action Buttons */}
        <div className="mb-6 sm:mb-8">
          <Link to="/recipe-builder">
            <Button variant="outline" className="w-full h-20 sm:h-24 md:h-28 flex flex-col gap-2 hover:bg-primary/5 transition-colors">
              <Plus className="w-5 h-5 sm:w-6 sm:h-6 md:w-7 md:h-7" />
              <span className="text-xs sm:text-sm md:text-base font-semibold">Create Recipe</span>
            </Button>
          </Link>
        </div>

        {/* Lottie Animation Display */}
        <div className="mb-8 sm:mb-10 flex justify-center">
          <LottieAnimation className="w-48 h-32" />
        </div>

        {/* Saved Items */}
        <div className="mb-6 mt-8">
          <h3 className="text-base sm:text-lg md:text-xl font-heading font-semibold mb-3 sm:mb-4">
            Saved ({filteredSavedRecipes.length})
          </h3>
          {loading ? (
            <div className="grid gap-3 sm:gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(3)].map((_, idx) => (
                <Card key={idx} className="p-3 sm:p-4 animate-pulse">
                  <div className="flex gap-3 sm:gap-4">
                    <div className="w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 bg-muted rounded-xl sm:rounded-2xl shrink-0"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-muted rounded"></div>
                      <div className="h-3 bg-muted rounded w-3/4"></div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : filteredSavedRecipes && filteredSavedRecipes.length > 0 ? (
            <div className="grid gap-3 sm:gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredSavedRecipes.map((recipe, idx) => (
                <GlowCard
                  key={`saved-${recipe.id}-${idx}`}
                  className="p-3 sm:p-4 hover:shadow-xl hover:-translate-y-2 animate-fade-up bg-gradient-to-br from-card to-card/80"
                  style={{ animationDelay: `${idx * 0.05}s` }}
                >
                  <Link to={`/recipe/${recipe.id}`} className="block">
                    <div className="flex gap-3 sm:gap-4">
                      <div className="w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 bg-muted rounded-xl sm:rounded-2xl flex items-center justify-center text-3xl sm:text-4xl shrink-0">
                        {recipe.image}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-sm sm:text-base text-foreground mb-1 sm:mb-2 line-clamp-2">{recipe.name}</h4>
                        <div className="flex flex-col sm:flex-row gap-1 sm:gap-4 text-xs text-muted-foreground mb-2">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {recipe.time}
                          </span>
                          <span className="flex items-center gap-1">
                            <Users className="w-3 h-3" />
                            {recipe.servings} servings
                          </span>
                        </div>
                        <span className="inline-block bg-primary text-primary-foreground text-xs px-2 py-1 rounded-md">
                          Saved
                        </span>
                      </div>
                      <div className="flex items-start flex-col gap-2">
                        <Button
                          variant="outline"
                          size="icon"
                          className="shrink-0 h-8 w-8 sm:h-9 sm:w-9"
                          onClick={(e) => handleUnsave(recipe.id, recipe.name, e)}
                        >
                          <BookmarkX className="w-3 h-3 sm:w-4 sm:h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          className="shrink-0 h-8 w-8 sm:h-9 sm:w-9"
                          onClick={(e) => handleAddToMeal(recipe, e)}
                        >
                          <CalendarPlus className="w-3 h-3 sm:w-4 sm:h-4" />
                        </Button>
                      </div>
                    </div>
                  </Link>
                </GlowCard>
              ))}
            </div>
          ) : (
            <Card className="p-4 text-sm text-muted-foreground flex items-center gap-3">
              <LottieAnimation className="w-12 h-12" />
              <span>You don't have any saved recipes yet. Tap the bookmark icon on a recipe to save it here.</span>
            </Card>
          )}
        </div>

        {/* Relevant Recipes */}
        <div className="mb-6">
          <h3 className="text-base sm:text-lg md:text-xl font-heading font-semibold mb-3 sm:mb-4">
            Recommended Recipes
          </h3>
          {/* Category Filter - moved below Recommended Recipes heading */}
          <div className="mb-4">
            <div className="flex gap-2 overflow-x-auto pb-2">
              {['All', 'Breakfast', 'Lunch', 'Dinner'].map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(category)}
                  className="whitespace-nowrap"
                >
                  {category}
                </Button>
              ))}
            </div>
          </div>

          <div className="grid gap-3 sm:gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredRelevantRecipes.map((recipe, idx) => (
              <GlowCard 
                key={`relevant-${recipe.id}-${idx}`}
                className="p-3 sm:p-4 hover:shadow-xl hover:-translate-y-2 animate-fade-up bg-gradient-to-br from-card to-card/80" 
                style={{ animationDelay: `${idx * 0.05}s` }}
              >
                <Link to={`/recipe/${recipe.id}`} className="block">
                  <div className="flex gap-3 sm:gap-4">
                    <div className="w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 bg-muted rounded-xl sm:rounded-2xl flex items-center justify-center text-3xl sm:text-4xl shrink-0">
                      {recipe.image}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-sm sm:text-base text-foreground mb-1 sm:mb-2 line-clamp-2">{recipe.name}</h4>
                      <div className="flex flex-col sm:flex-row gap-1 sm:gap-4 text-xs text-muted-foreground mb-2">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {recipe.time}
                        </span>
                        <span className="flex items-center gap-1">
                          <Users className="w-3 h-3" />
                          {recipe.servings} servings
                        </span>
                      </div>
                      <span className="inline-block bg-primary text-primary-foreground text-xs px-2 py-1 rounded-md">
                        {recipe.category}
                      </span>
                    </div>
                    <Button
                      variant="outline"
                      size="icon"
                      className="shrink-0 h-8 w-8 sm:h-9 sm:w-9"
                      onClick={(e) => handleAddToMeal(recipe, e)}
                    >
                      <CalendarPlus className="w-3 h-3 sm:w-4 sm:h-4" />
                    </Button>
                  </div>
                </Link>
              </GlowCard>
            ))}
          </div>
          
        </div>
      </main>

      <BottomNav />
    </div>
  );
};
