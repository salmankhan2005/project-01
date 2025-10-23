import { useState, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import { BottomNav } from '@/components/layout/BottomNav';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search, Clock, Users, Bookmark, BookmarkCheck, Info } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useSavedRecipes } from '@/contexts/SavedRecipesContext';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { Alert, AlertDescription } from '@/components/ui/alert';
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

export const Discover = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [discoverRecipes, setDiscoverRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [showSearchSignInNotification, setShowSearchSignInNotification] = useState(false);
  const { saveRecipe, unsaveRecipe, isRecipeSaved, createdRecipes } = useSavedRecipes();
  const { isGuest, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    loadDiscoverRecipes();
    // Set up polling for recipe updates
    const interval = setInterval(loadDiscoverRecipes, 60000); // Poll every minute
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  const loadDiscoverRecipes = async () => {
    try {
      if (isAuthenticated) {
        const response = await apiService.getDiscoverRecipes();
        setDiscoverRecipes(response.recipes);
      } else {
        // Load from localStorage for guest mode
        const savedDiscoverRecipes = localStorage.getItem('guest_discover_recipes');
        if (savedDiscoverRecipes) {
          setDiscoverRecipes(JSON.parse(savedDiscoverRecipes));
        }
        
        // Try to get admin recipes even without authentication
        try {
          const adminResponse = await apiService.getAdminRecipes();
          if (adminResponse.recipes && adminResponse.recipes.length > 0) {
            const combinedRecipes = [...JSON.parse(savedDiscoverRecipes || '[]'), ...adminResponse.recipes];
            setDiscoverRecipes(combinedRecipes);
            localStorage.setItem('guest_discover_recipes', JSON.stringify(combinedRecipes));
          }
        } catch (adminError) {
          console.log('Admin recipes not available');
        }
      }
    } catch (error) {
      console.error('Failed to load discover recipes:', error);
    } finally {
      setLoading(false);
    }
  };

  // Get user created recipes from localStorage for guest mode
  const getUserCreatedRecipes = () => {
    if (isGuest) {
      const guestCreatedRecipes = localStorage.getItem('guest_created_recipes');
      return guestCreatedRecipes ? JSON.parse(guestCreatedRecipes) : [];
    }
    return createdRecipes || [];
  };
  
  // Combine database recipes, user-created recipes, and mock recipes
  const allRecipes = [
    ...discoverRecipes,
    ...getUserCreatedRecipes(), 
    ...mockRecipes
  ].filter((recipe, index, self) => 
    recipe && 
    recipe.name && 
    typeof recipe.name === 'string' &&
    // Remove duplicates based on id
    index === self.findIndex(r => r.id === recipe.id)
  );

  const filteredRecipes = allRecipes.filter(recipe => {
    // Filter out recipes that don't have proper data (would show "Recipe not found")
    const hasValidData = recipe && recipe.name && recipe.id && 
                        (recipe.ingredients || recipe.time || recipe.servings);
    const matchesSearch = recipe.name.toLowerCase().includes(searchQuery.toLowerCase());
    return hasValidData && matchesSearch;
  });

  const handleSaveToggle = async (recipe: Recipe, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    try {
      if (isRecipeSaved(recipe.id)) {
        if (isAuthenticated) {
          await apiService.unsaveRecipeNew(String(recipe.id));
        }
        unsaveRecipe(recipe.id);
        toast({
          title: "Recipe removed",
          description: `${recipe.name || 'Recipe'} removed from your recipes`,
        });
      } else {
        if (isAuthenticated) {
          await apiService.saveRecipeNew(String(recipe.id), recipe);
        }
        saveRecipe(recipe);
        toast({
          title: "Recipe saved!",
          description: `${recipe.name || 'Recipe'} added to your recipes`,
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update recipe. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-background pb-20 sm:pb-24">
      <Header 
        title="Discover" 
        showBackButton={true}
        onBackClick={() => navigate(-1)}
      />
      
      <main className="px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 md:py-8 max-w-7xl mx-auto">
        {isGuest && (
          <Alert className="mb-4 border-amber-500 bg-amber-50 text-amber-800">
            <Info className="h-4 w-4 mr-2" />
            <AlertDescription>
              You're in guest mode. Recipes will be saved locally on this device only. Sign in to save recipes to your account.
            </AlertDescription>
          </Alert>
        )}
        
        {/* Search Bar */}
        <div className="relative mb-4 sm:mb-6 animate-fade-in">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-muted-foreground pointer-events-none" />
          <Input
            placeholder="Search recipes..."
            value={searchQuery}
            onChange={(e) => {
              if (!isGuest) {
                setSearchQuery(e.target.value);
              }
            }}
            onClick={() => {
              if (isGuest) {
                setShowSearchSignInNotification(true);
                setTimeout(() => setShowSearchSignInNotification(false), 3000);
              }
            }}
            className="pl-9 sm:pl-10 h-10 sm:h-12 text-sm sm:text-base"
            readOnly={isGuest}
          />
        </div>

        {/* Recipes Grid */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3 sm:mb-4">
            <h3 className="text-base sm:text-lg md:text-xl font-heading font-semibold">
              All Recipes ({filteredRecipes.length})
            </h3>

          </div>
          {loading ? (
            <div className="grid gap-3 sm:gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(6)].map((_, idx) => (
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
          ) : (
            <div className="grid gap-3 sm:gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredRecipes.map((recipe, idx) => {
                const isSaved = isRecipeSaved(recipe.id);
                const isUserCreated = discoverRecipes.some(r => r.id === recipe.id);
                const isAdminRecipe = recipe.author === 'By Admin' || recipe.is_admin_recipe;
                return (
                  <Card 
                    key={recipe.id}
                    className="p-3 sm:p-4 hover:shadow-lg transition-all hover:-translate-y-1 animate-fade-up" 
                    style={{ animationDelay: `${idx * 0.05}s` }}
                  >
                    <Link to={`/recipe/${recipe.id}`} className="block">
                      <div className="flex gap-3 sm:gap-4">
                        <div className="w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 bg-muted rounded-xl sm:rounded-2xl flex items-center justify-center text-3xl sm:text-4xl shrink-0">
                          {recipe.image || '🍽️'}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-sm sm:text-base text-foreground mb-1 sm:mb-2 line-clamp-2">{recipe.name}</h4>
                          <div className="flex flex-col sm:flex-row gap-1 sm:gap-4 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {recipe.time}
                            </span>
                            <span className="flex items-center gap-1">
                              <Users className="w-3 h-3" />
                              {recipe.servings} servings
                            </span>
                          </div>
                          {(isUserCreated || isAdminRecipe) && (
                            <div className="mt-1">

                            </div>
                          )}
                        </div>
                        <Button
                          variant={isSaved ? "default" : "outline"}
                          size="icon"
                          className="shrink-0 h-8 w-8 sm:h-9 sm:w-9"
                          onClick={(e) => handleSaveToggle(recipe, e)}
                        >
                          {isSaved ? (
                            <BookmarkCheck className="w-3 h-3 sm:w-4 sm:h-4" />
                          ) : (
                            <Bookmark className="w-3 h-3 sm:w-4 sm:h-4" />
                          )}
                        </Button>
                      </div>
                    </Link>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </main>

      <BottomNav />
      
      {/* Search Sign In Notification */}
      {showSearchSignInNotification && (
        <div className="fixed inset-0 z-50 flex items-center justify-center animate-fade-up">
          <div className="bg-card border border-border rounded-lg p-4 shadow-lg mx-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                  <Search className="w-4 h-4 text-primary" />
                </div>
                <span className="text-sm font-medium">Sign in to search recipes</span>
              </div>
              <Button
                size="sm"
                className="h-7 px-3 text-xs ml-4"
                onClick={() => {
                  setShowSearchSignInNotification(false);
                  navigate('/auth');
                }}
              >
                Sign In
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
