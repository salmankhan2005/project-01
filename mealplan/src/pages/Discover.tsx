import { useState } from 'react';
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
  { id: 1, name: 'Grilled Chicken Salad', time: '25 min', servings: 2, image: '🥗' },
  { id: 2, name: 'Spaghetti Carbonara', time: '30 min', servings: 4, image: '🍝' },
  { id: 3, name: 'Avocado Toast', time: '10 min', servings: 1, image: '🥑' },
  { id: 4, name: 'Veggie Stir Fry', time: '20 min', servings: 3, image: '🥘' },
  { id: 5, name: 'Margherita Pizza', time: '45 min', servings: 4, image: '🍕' },
  { id: 6, name: 'Caesar Salad', time: '15 min', servings: 2, image: '🥗' },
  { id: 7, name: 'Beef Tacos', time: '35 min', servings: 4, image: '🌮' },
  { id: 8, name: 'Chocolate Cake', time: '60 min', servings: 8, image: '🍰' },
];

export const Discover = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const { saveRecipe, unsaveRecipe, isRecipeSaved, createdRecipes } = useSavedRecipes();
  const { isGuest } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  // Combine mock recipes with user-created recipes, filtering out invalid ones
  const allRecipes = [...(createdRecipes || []), ...mockRecipes].filter(recipe => 
    recipe && recipe.name && typeof recipe.name === 'string'
  );

  const filteredRecipes = allRecipes.filter(recipe =>
    recipe.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSaveToggle = (recipe: Recipe, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isRecipeSaved(recipe.id)) {
      unsaveRecipe(recipe.id);
      toast({
        title: "Recipe removed",
        description: `${recipe.name || 'Recipe'} removed from your recipes`,
      });
    } else {
      saveRecipe(recipe);
      toast({
        title: "Recipe saved!",
        description: `${recipe.name || 'Recipe'} added to your recipes`,
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
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 sm:pl-10 h-10 sm:h-12 text-sm sm:text-base"
          />
        </div>

        {/* Recipes Grid */}
        <div className="mb-6">
          <h3 className="text-base sm:text-lg md:text-xl font-heading font-semibold mb-3 sm:mb-4">
            All Recipes ({filteredRecipes.length})
          </h3>
          <div className="grid gap-3 sm:gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredRecipes.map((recipe, idx) => {
              const isSaved = isRecipeSaved(recipe.id);
              return (
                <Card 
                  key={recipe.id}
                  className="p-3 sm:p-4 hover:shadow-lg transition-all hover:-translate-y-1 animate-fade-up" 
                  style={{ animationDelay: `${idx * 0.05}s` }}
                >
                  <Link to={`/recipe/${recipe.id}`} className="block">
                    <div className="flex gap-3 sm:gap-4">
                      <div className="w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 bg-muted rounded-xl sm:rounded-2xl flex items-center justify-center text-3xl sm:text-4xl shrink-0">
                        {recipe.image}
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
        </div>
      </main>

      <BottomNav />
    </div>
  );
};
