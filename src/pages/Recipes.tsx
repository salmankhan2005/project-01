import { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { BottomNav } from '@/components/layout/BottomNav';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus, Search, Clock, Users, BookmarkX } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useSavedRecipes } from '@/contexts/SavedRecipesContext';
import { useToast } from '@/hooks/use-toast';

export const Recipes = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const { savedRecipes, unsaveRecipe } = useSavedRecipes();
  const { toast } = useToast();
  const navigate = useNavigate();

  // Filter saved recipes based on search query
  const filteredRecipes = savedRecipes.filter(recipe =>
    recipe.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleUnsave = (recipeId: number, recipeName: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    unsaveRecipe(recipeId);
    toast({
      title: "Recipe removed",
      description: `${recipeName} removed from your recipes`,
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

        {/* Recipes Grid */}
        <div className="mb-6">
          <h3 className="text-base sm:text-lg md:text-xl font-heading font-semibold mb-3 sm:mb-4">
            {searchQuery ? `Search Results (${filteredRecipes.length})` : 'Saved Recipes'}
          </h3>
          {filteredRecipes.length === 0 ? (
            <Card className="p-6 sm:p-8 text-center">
              <p className="text-sm sm:text-base text-muted-foreground">
                {searchQuery 
                  ? `No recipes found matching "${searchQuery}"` 
                  : 'No saved recipes yet. Go to Discover to save some recipes!'}
              </p>
            </Card>
          ) : (
            <div className="grid gap-3 sm:gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredRecipes.map((recipe, idx) => (
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
                        variant="outline"
                        size="icon"
                        className="shrink-0 h-8 w-8 sm:h-9 sm:w-9"
                        onClick={(e) => handleUnsave(recipe.id, recipe.name, e)}
                      >
                        <BookmarkX className="w-3 h-3 sm:w-4 sm:h-4" />
                      </Button>
                    </div>
                  </Link>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>

      <BottomNav />
    </div>
  );
};
