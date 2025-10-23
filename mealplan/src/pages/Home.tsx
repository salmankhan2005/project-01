import { Header } from '@/components/layout/Header';
import { BottomNav } from '@/components/layout/BottomNav';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LoadingButton } from '@/components/LoadingButton';
import { GlowCard } from '@/components/GlowCard';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Calendar } from '@/components/ui/calendar';
import { Textarea } from '@/components/ui/textarea';
import { ChevronDown, ChevronUp, Trash2, Edit, Coffee, UtensilsCrossed, Apple, ChefHat, Calendar as CalendarIcon, Grid, List, Star, Clock, Lock, Edit2, Sparkles, Crown } from 'lucide-react';

import { useAuth } from '@/contexts/AuthContext';
import { useMealPlan } from '@/contexts/MealPlanContext';
import { useUserData } from '@/contexts/UserDataContext';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { sanitizeInput, generateSecureId } from '@/utils/security';
import { apiService } from '@/services/api';

const mealTimes = [
  { name: 'Breakfast', icon: Coffee },
  { name: 'Lunch', icon: UtensilsCrossed },
  { name: 'Snack', icon: Apple },
  { name: 'Dinner', icon: ChefHat }
];

const weeks = ['Week - 1', 'Week - 2', 'Week - 3', 'Week - 4'];
const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

interface Person {
  id: number;
  name: string;
  preferences?: string;
  allergies?: string;
}

interface Meal {
  time: string;
  name: string;
  description?: string;
  ingredients?: string[];
  instructions?: string[];
  servings?: number;
  cookTime?: string;
  assignedTo?: number;
  week?: string;
}

const initialMeals: Record<string, Meal[]> = {
  Monday: [],
  Tuesday: [],
  Wednesday: [],
  Thursday: [],
  Friday: [],
  Saturday: [],
  Sunday: []
};

export const Home = () => {
  const { isGuest, isSubscribed, isAuthenticated } = useAuth();
  const { getMealsForDay, removeFromMealPlan, addToMealPlan, loading: mealPlanLoading, mealPlan, currentWeek, setCurrentWeek } = useMealPlan();
  const { people, preferences, addPerson, updatePerson, deletePerson, updatePreferences } = useUserData();
  const navigate = useNavigate();
  const [selectedWeek, setSelectedWeek] = useState(preferences.selectedWeek);
  const [selectedFood, setSelectedFood] = useState<string>('');
  const [weekDropdownOpen, setWeekDropdownOpen] = useState(false);
  const [foodDropdownOpen, setFoodDropdownOpen] = useState(false);
  const [meals, setMeals] = useState<Record<string, Meal[]>>(initialMeals);


  const [viewMode, setViewMode] = useState<'list' | 'calendar'>(preferences.viewMode);
  const [addMealOpen, setAddMealOpen] = useState(false);
  const [editMealOpen, setEditMealOpen] = useState(false);
  const [selectedMealTime, setSelectedMealTime] = useState('');
  const [selectedDay, setSelectedDay] = useState('');
  const [mealName, setMealName] = useState('');
  const [mealDescription, setMealDescription] = useState('');
  const [mealIngredients, setMealIngredients] = useState('');
  const [mealInstructions, setMealInstructions] = useState('');
  const [mealServings, setMealServings] = useState(1);
  const [mealCookTime, setMealCookTime] = useState('');
  const [selectedAssignedTo, setSelectedAssignedTo] = useState<string | null>(null);
  const [editingMeal, setEditingMeal] = useState<Meal | null>(null);
  const [craftMealOpen, setCraftMealOpen] = useState(false);
  const [planMonthOpen, setPlanMonthOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());
  const [craftMealName, setCraftMealName] = useState('');
  const [craftMealIngredients, setCraftMealIngredients] = useState('');
  const [craftMealInstructions, setCraftMealInstructions] = useState('');

  const [selectedCalendarDate, setSelectedCalendarDate] = useState<Date | undefined>(new Date());
  const [quickAddOpen, setQuickAddOpen] = useState(false);

  const [addPersonOpen, setAddPersonOpen] = useState(false);
  const [newPersonName, setNewPersonName] = useState('');
  const [newPersonPreferences, setNewPersonPreferences] = useState('');
  const [newPersonAllergies, setNewPersonAllergies] = useState('');
  const [editPersonOpen, setEditPersonOpen] = useState(false);
  const [editingPerson, setEditingPerson] = useState<Person | null>(null);
  const [editPersonName, setEditPersonName] = useState('');
  const [planMonthLoading, setPlanMonthLoading] = useState(false);
  const [craftMealLoading, setCraftMealLoading] = useState(false);
  const [editMealPlanOpen, setEditMealPlanOpen] = useState(false);
  const [editingMealPlan, setEditingMealPlan] = useState<any>(null);
  const [editMealPlanName, setEditMealPlanName] = useState('');
  const [quickAddLoading, setQuickAddLoading] = useState(false);
  const [backendAvailable, setBackendAvailable] = useState(true);
  const [showSignInNotification, setShowSignInNotification] = useState(false);
  const [showSubscriptionNotification, setShowSubscriptionNotification] = useState(false);

  // Sync preferences when they change
  useEffect(() => {
    setSelectedWeek(preferences.selectedWeek);
    setViewMode(preferences.viewMode);
    setCurrentWeek(preferences.selectedWeek);
  }, [preferences, setCurrentWeek]);

  const savePreferences = async (week?: string, mode?: 'list' | 'calendar') => {
    await updatePreferences({
      selectedWeek: week || selectedWeek,
      viewMode: mode || viewMode
    });
  };



  const handleAddMeal = async () => {
    if (!mealName || !selectedMealTime || !selectedDay) {
      toast.error('Please fill all fields');
      return;
    }
    if (!selectedWeek) {
      toast.error('Please select a week first');
      return;
    }
    
    try {
      if (isAuthenticated) {
        // Save to backend
        await addToMealPlan({
          recipeId: `meal-${Date.now()}`,
          recipeName: sanitizeInput(mealName),
          day: selectedDay,
          mealTime: selectedMealTime,
          servings: 1,
          image: '🍽️',
          time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          week: selectedWeek
        });
      } else {
        // Use MealPlanContext for guests (now with localStorage)
        await addToMealPlan({
          recipeId: `meal-${Date.now()}`,
          recipeName: sanitizeInput(mealName),
          day: selectedDay,
          mealTime: selectedMealTime,
          servings: 1,
          image: '🍽️',
          time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          week: selectedWeek
        });
      }
      
      toast.success('Meal added successfully');
      setMealName('');
      setMealDescription('');
      setAddMealOpen(false);
    } catch (error) {
      toast.error('Failed to add meal');
    }
  };

  const handleEditMeal = (meal: Meal, day: string) => {
    setEditingMeal(meal);
    setSelectedDay(day);
    setMealName(meal.name);
    setMealDescription(meal.description || '');
    setMealIngredients(meal.ingredients?.join('\n') || '');
    setMealInstructions(meal.instructions?.join('\n') || '');
    setMealServings(meal.servings || 1);
    setMealCookTime(meal.cookTime || '');
    setSelectedMealTime(meal.time);
    setSelectedAssignedTo(meal.assignedTo ?? null);
    setEditMealOpen(true);
  };

  const handleUpdateMeal = async () => {
    if (!mealName || !editingMeal || !selectedDay) return;
    
    try {
      if (isAuthenticated) {
        // Update via backend - remove old and add new
        await addToMealPlan({
          recipeId: `meal-${Date.now()}`,
          recipeName: sanitizeInput(mealName),
          day: selectedDay,
          mealTime: editingMeal.time,
          servings: mealServings,
          image: '🍽️',
          time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          week: selectedWeek
        });
      } else {
        // Use MealPlanContext for guests
        await addToMealPlan({
          recipeId: `meal-${Date.now()}`,
          recipeName: sanitizeInput(mealName),
          day: selectedDay,
          mealTime: editingMeal.time,
          servings: mealServings,
          image: '🍽️',
          time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          week: selectedWeek
        });
      }
      
      toast.success('Meal updated successfully');
      setEditMealOpen(false);
      setEditingMeal(null);
      setMealName('');
      setMealDescription('');
      setMealIngredients('');
      setMealInstructions('');
      setMealServings(1);
      setMealCookTime('');
      setSelectedAssignedTo(null);
    } catch (error) {
      toast.error('Failed to update meal');
    }
  };

  const handleDeleteMeal = async (mealTime: string, day: string) => {
    try {
      if (isAuthenticated) {
        // Find and delete from backend
        const mealPlanItems = getMealsForDay(day);
        const mealToDelete = mealPlanItems.find(item => item.mealTime === mealTime);
        if (mealToDelete) {
          await removeFromMealPlan(mealToDelete.id);
        }
      } else {
        // Use MealPlanContext for guests
        const mealPlanItems = getMealsForDay(day);
        const mealToDelete = mealPlanItems.find(item => item.mealTime === mealTime);
        if (mealToDelete) {
          await removeFromMealPlan(mealToDelete.id);
        }
      }
      
      toast.success('Meal deleted successfully');
    } catch (error) {
      toast.error('Failed to delete meal');
    }
  };

  const handleCraftMeal = async () => {
    if (!craftMealName) {
      toast.error('Please enter meal name');
      return;
    }
    
    setCraftMealLoading(true);
    try {
      if (isAuthenticated) {
        await apiService.createRecipe({
          name: craftMealName,
          ingredients: craftMealIngredients.split('\n').filter(i => i.trim()),
          instructions: craftMealInstructions.split('\n').filter(i => i.trim()),
          servings: 1,
          difficulty: 'medium'
        });
      }
      
      toast.success(`Recipe "${craftMealName}" crafted successfully!`);
      setCraftMealName('');
      setCraftMealIngredients('');
      setCraftMealInstructions('');
      setCraftMealOpen(false);
    } catch (error) {
      toast.error('Failed to create recipe');
    } finally {
      setCraftMealLoading(false);
    }
  };

  const handlePlanMonth = async () => {
    if (!selectedDate) {
      toast.error('Please select a date');
      return;
    }
    
    setPlanMonthLoading(true);
    try {
      if (isAuthenticated) {
        await apiService.createMonthPlan(selectedDate.getMonth() + 1, selectedDate.getFullYear());
      }
      
      const monthName = selectedDate.toLocaleString('default', { month: 'long', year: 'numeric' });
      toast.success(`Meal plan created for ${monthName}!`);
      setPlanMonthOpen(false);
    } catch (error) {
      toast.error('Failed to create meal plan');
    } finally {
      setPlanMonthLoading(false);
    }
  };

  const handleCalendarMealAdd = (date: Date, mealTime: string) => {
    const dateKey = date.toDateString();
    setSelectedCalendarDate(date);
    setSelectedMealTime(mealTime);
    setSelectedDay(date.toLocaleDateString('en-US', { weekday: 'long' }));
    setAddMealOpen(true);
  };

  const getMealsForDate = (date: Date) => {
    const dateKey = date.toDateString();
    return [];
  };

  const handleQuickAdd = async () => {
    if (!mealName || !selectedMealTime) {
      toast.error('Please fill all fields');
      return;
    }
    
    setQuickAddLoading(true);
    try {
      const today = new Date();
      const dayName = today.toLocaleDateString('en-US', { weekday: 'long' });
      

      
      // Use MealPlanContext to add to backend
      await addToMealPlan({
        recipeId: `quick-${Date.now()}`, // Generate unique ID for quick add
        recipeName: sanitizeInput(mealName),
        day: dayName,
        mealTime: selectedMealTime,
        servings: 1,
        image: '🍽️',
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        week: selectedWeek
      });
      
      toast.success(`Quick meal "${mealName}" added for ${dayName} ${selectedMealTime}!`);
      setMealName('');
      setMealDescription('');
      setSelectedMealTime('');
      setSelectedAssignedTo(null);
      setQuickAddOpen(false);
    } catch (error) {
      console.error('Failed to add quick meal:', error);
      toast.error('Failed to add meal. Please try again.');
    } finally {
      setQuickAddLoading(false);
    }
  };

  const handleAddPerson = async () => {
    if (!newPersonName.trim()) {
      toast.error('Please enter person name');
      return;
    }
    
    try {
      await addPerson({
        name: sanitizeInput(newPersonName.trim()),
        preferences: sanitizeInput(newPersonPreferences.trim()),
        allergies: sanitizeInput(newPersonAllergies.trim())
      });
      
      toast.success(`${newPersonName} added successfully!`);
      setNewPersonName('');
      setNewPersonPreferences('');
      setNewPersonAllergies('');
      setAddPersonOpen(false);
    } catch (error) {
      toast.error('Failed to add person');
    }
  };

  const handleRemovePerson = async (personId: string | number) => {
    const person = people.find(p => p.id === personId);
    
    try {
      await deletePerson(personId);
      toast.success(`${person?.name} removed successfully`);
    } catch (error) {
      toast.error('Failed to remove person');
    }
  };

  const handleEditPerson = (person: Person) => {
    setEditingPerson(person);
    setEditPersonName(person.name);
    setEditPersonOpen(true);
  };

  const handleUpdatePerson = async () => {
    if (!editPersonName.trim() || !editingPerson) {
      toast.error('Please enter person name');
      return;
    }
    
    try {
      await updatePerson(editingPerson.id, {
        name: sanitizeInput(editPersonName.trim())
      });
      
      toast.success('Person updated successfully!');
      setEditPersonName('');
      setEditingPerson(null);
      setEditPersonOpen(false);
    } catch (error) {
      toast.error('Failed to update person');
    }
  };

  const handleDeleteMealPlan = async (mealId: string) => {
    try {
      await removeFromMealPlan(mealId);
      toast.success('Meal removed from plan');
    } catch (error) {
      toast.error('Failed to remove meal');
    }
  };

  const handleEditMealPlan = (mealPlanItem: any, day: string) => {
    setEditingMealPlan(mealPlanItem);
    setEditMealPlanName(mealPlanItem.recipeName);
    setSelectedDay(day);
    setEditMealPlanOpen(true);
  };

  const handleUpdateMealPlan = async () => {
    if (!editMealPlanName.trim() || !editingMealPlan) {
      toast.error('Please enter meal name');
      return;
    }
    
    try {
      // Update meal using addToMealPlan (it will replace existing meal with same mealTime)
      await addToMealPlan({
        recipeId: editingMealPlan.recipeId,
        recipeName: sanitizeInput(editMealPlanName.trim()),
        day: selectedDay,
        mealTime: editingMealPlan.mealTime,
        servings: editingMealPlan.servings || 1,
        image: editingMealPlan.image || '🍽️',
        time: editingMealPlan.time,
        week: editingMealPlan.week || selectedWeek
      });
      
      toast.success('Meal updated successfully!');
      setEditMealPlanOpen(false);
      setEditingMealPlan(null);
      setEditMealPlanName('');
    } catch (error) {
      toast.error('Failed to update meal');
    }
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      <Header 
        title="Meal plan pro"
        showBackButton={true}
        onBackClick={() => navigate(-1)}
      />
      
      <main className="container-responsive py-6 space-y-6">

        
        {/* Action buttons */}
        <div className="grid grid-cols-1 gap-4">
          <Button 
            className="w-full bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 text-primary-foreground rounded-full py-4 text-lg font-medium flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02]"
            onClick={() => setPlanMonthOpen(true)}
          >
            Plan your month
          </Button>
        </div>

        {/* View Toggle */}
        <div className="flex gap-2 bg-muted/50 rounded-full p-1">
          <Button
            variant={viewMode === 'list' ? 'default' : 'ghost'}
            size="sm"
            className="flex-1 rounded-full"
            onClick={() => {
              setViewMode('list');
              savePreferences(undefined, 'list');
            }}
          >
            <List className="w-4 h-4 mr-2" />
            List View
          </Button>
          <Button
            variant={viewMode === 'calendar' ? 'default' : 'ghost'}
            size="sm"
            className="flex-1 rounded-full"
            onClick={() => {
              setViewMode('calendar');
              savePreferences(undefined, 'calendar');
            }}
          >
            <Grid className="w-4 h-4 mr-2" />
            Calendar
          </Button>
        </div>

        {/* Horizontal Row: Week, Food for, Quick Add */}
        <div className="grid grid-cols-3 gap-4">
          {/* Week Dropdown */}
          <div className="relative">
            <Button
              variant="outline"
              className="w-full justify-between bg-muted/50 border-border rounded-full py-4 text-muted-foreground"
              onClick={() => {
                setWeekDropdownOpen(!weekDropdownOpen);
                setFoodDropdownOpen(false);
              }}
            >
              {selectedWeek || 'Week'}
              {weekDropdownOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </Button>
            {weekDropdownOpen && (
              <Card className="absolute top-full left-0 right-0 mt-2 z-10 bg-card border-border">
                <div className="p-2 space-y-1">
                  {weeks.map((week) => {
                    const isLocked = isGuest && (week === 'Week - 2' || week === 'Week - 3' || week === 'Week - 4');
                    return (
                      <Button
                        key={week}
                        variant="ghost"
                        className={`w-full justify-between text-foreground border-b border-border rounded-none py-3 ${
                          isLocked 
                            ? 'opacity-50 cursor-not-allowed hover:bg-muted/20' 
                            : 'hover:bg-muted/50'
                        }`}
                        onClick={() => {
                          if (!isLocked) {
                            setSelectedWeek(week);
                            setCurrentWeek(week);
                            setWeekDropdownOpen(false);
                            savePreferences(week);
                          } else {
                            setWeekDropdownOpen(false);
                            setShowSignInNotification(true);
                            setTimeout(() => setShowSignInNotification(false), 3000);
                          }
                        }}

                      >
                        <span>{week}</span>
                        {isLocked && <Lock className="w-4 h-4 text-muted-foreground" />}
                      </Button>
                    );
                  })}

                </div>
              </Card>
            )}
          </div>

          {/* Food for Dropdown */}
          <div className="relative">
            <Button
              variant="outline"
              className="w-full justify-between bg-muted/50 border-border rounded-full py-4 text-muted-foreground"
              onClick={() => {
                setFoodDropdownOpen(!foodDropdownOpen);
                setWeekDropdownOpen(false);
              }}
            >
              {selectedFood ? people.find(p => p.id.toString() === selectedFood)?.name || 'Food for' : 'Food for'}
              {foodDropdownOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </Button>
            {foodDropdownOpen && (
              <Card className="absolute top-full left-0 right-0 mt-2 z-10 bg-card border-border">
                <div className="p-2 space-y-1">
                  {people.map((person) => {
                    const isLocked = !isSubscribed && person.name === 'Person B';
                    return (
                      <div
                        key={person.id}
                        role="button"
                        tabIndex={0}
                        onClick={() => { 
                          if (!isLocked) {
                            setSelectedFood(person.id.toString()); 
                            setFoodDropdownOpen(false);
                          } else {
                            setFoodDropdownOpen(false);
                            setShowSubscriptionNotification(true);
                            setTimeout(() => setShowSubscriptionNotification(false), 3000);
                          }
                        }}
                        onKeyDown={(e) => { 
                          if (!isLocked && (e.key === 'Enter' || e.key === ' ')) { 
                            e.preventDefault(); 
                            setSelectedFood(person.name); 
                            setFoodDropdownOpen(false); 
                          } 
                        }}
                        className={`flex items-center justify-between p-3 border-b border-border last:border-b-0 ${
                          isLocked 
                            ? 'opacity-50 cursor-not-allowed' 
                            : 'cursor-pointer hover:bg-muted/50'
                        } ${selectedFood === person.id.toString() ? 'bg-muted/20' : ''}`}
                      >
                        <div className="flex-1 flex items-center gap-2">
                          <span className="text-foreground font-medium">{person.name}</span>
                          {isLocked && <Lock className="w-4 h-4 text-muted-foreground" />}
                          <div>
                            {person.preferences && (
                              <p className="text-xs text-muted-foreground">Likes: {person.preferences}</p>
                            )}
                            {person.allergies && (
                              <p className="text-xs text-destructive">Allergies: {person.allergies}</p>
                            )}
                          </div>
                        </div>
                        {!isLocked && (
                          <div className="flex items-center gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 w-6 p-0 hover:bg-primary/20"
                              onClick={(e) => { e.stopPropagation(); handleEditPerson(person); }}
                            >
                              <Edit2 className="w-3 h-3 text-primary" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 w-6 p-0 hover:bg-red-600"
                              onClick={(e) => { e.stopPropagation(); handleRemovePerson(person.id.toString()); }}
                            >
                              <Trash2 className="w-4 h-4 text-red-400" />
                            </Button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                  <Button
                    className={`w-full mt-2 rounded-full ${
                      !isSubscribed 
                        ? 'bg-muted text-muted-foreground cursor-not-allowed opacity-50' 
                        : 'bg-primary text-primary-foreground hover:bg-primary/90'
                    }`}
                    onClick={() => isSubscribed && setAddPersonOpen(true)}
                    disabled={!isSubscribed}
                  >
                    {!isSubscribed ? (
                      <div className="flex items-center gap-2">
                        <Lock className="w-4 h-4" />
                        Add Person
                      </div>
                    ) : (
                      'Add Person'
                    )}
                  </Button>

                </div>
              </Card>
            )}
          </div>

          {/* Quick Add Button */}
          <Button 
            variant="outline"
            className="w-full border-dashed border-2 py-4 text-muted-foreground hover:text-foreground hover:border-primary rounded-full"
            onClick={() => setQuickAddOpen(true)}
          >
            <Star className="w-4 h-4 mr-2" />
            Quick Add
          </Button>
        </div>

        {/* Main Content Area */}
        {viewMode === 'list' ? (
          /* List View - Scrollable Day Cards */
          <div className="space-y-6 max-h-[60vh] overflow-y-auto scrollbar-hide">
            {daysOfWeek.map((day) => {
              
              return (
                <GlowCard key={day} className="bg-gradient-to-br from-muted/20 to-muted/40 border-border rounded-3xl p-6">
                  <h2 className="text-2xl font-bold text-foreground mb-6">{day}</h2>
                  
                  <div className="space-y-4">
                    {mealTimes.map(({ name, icon: Icon }) => {
                      // Check meal plan context (includes localStorage for guests)
                      const mealPlanItems = getMealsForDay(day);
                      const mealPlanItem = mealPlanItems.find(item => item.mealTime === name);
                      
                      // Use meal plan item (which now includes localStorage data for guests)
                      const displayMeal = mealPlanItem;
                      

                      return (
                        <div key={name} className="bg-card rounded-2xl p-4 flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center">
                              <Icon className="w-5 h-5 text-muted-foreground" />
                            </div>
                            <div>
                              <p className="font-medium text-foreground">{name}</p>
                              <p className="text-sm text-muted-foreground">{displayMeal?.recipeName || displayMeal?.name || 'No meal planned'}</p>
                              {displayMeal && 'assignedTo' in displayMeal && displayMeal.assignedTo && (
                                <p className="text-xs text-primary">
                                  {people.find(p => p.id.toString() === displayMeal.assignedTo?.toString())?.name}
                                </p>
                              )}
                              {mealPlanItem && (
                                <p className="text-xs text-green-600">
                                  Added via meal plan
                                </p>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0 hover:bg-destructive/20"
                              onClick={() => {
                                if (displayMeal) {
                                  handleDeleteMealPlan(displayMeal.id);
                                }
                              }}
                            >
                              <Trash2 className="w-4 h-4 text-destructive" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0 hover:bg-primary/20"
                              onClick={() => {
                                if (displayMeal) {
                                  handleEditMealPlan(displayMeal, day);
                                } else {
                                  setSelectedMealTime(name);
                                  setSelectedDay(day);
                                  setAddMealOpen(true);
                                }
                              }}
                            >
                              <Edit className="w-4 h-4 text-primary" />
                            </Button>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <Button 
                    className="w-full mt-6 bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 text-primary-foreground rounded-full py-4 text-lg font-medium flex items-center justify-center gap-2 shadow-md hover:shadow-lg transition-all duration-300 hover:scale-[1.02]"
                    onClick={() => setCraftMealOpen(true)}
                  >
                    Craft Your Meal
                  </Button>
                </GlowCard>
              );
            })}

          </div>
        ) : (
          /* Calendar View */
          <Card className="p-6">
            <div className="mb-6">
              <h3 className="text-xl font-bold text-foreground mb-4">Meal Calendar</h3>
              <Calendar
                mode="single"
                selected={selectedCalendarDate}
                onSelect={setSelectedCalendarDate}
                className="rounded-md border mx-auto"
              />
            </div>
            
            {selectedCalendarDate && (
              <div className="space-y-4">
                <h4 className="text-lg font-semibold text-foreground">
                  {selectedCalendarDate.toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </h4>
                
                <div className="grid grid-cols-2 gap-3">
                  {mealTimes.map(({ name, icon: Icon }) => {
                    const dayMeals = getMealsForDate(selectedCalendarDate);
                    // Filter meals based on selected week and person
                    const filteredMeals = dayMeals.filter(m => {
                      const weekMatch = !selectedWeek || m.week === selectedWeek;
                      const selectedPersonId = typeof selectedFood === 'string' ? people.find(p => p.name === selectedFood)?.id : selectedFood;
                      const personMatch = !selectedFood || selectedFood === '' || m.assignedTo === selectedPersonId;
                      return weekMatch && personMatch;
                    });
                    const meal = filteredMeals.find(m => m.time === name);
                    return (
                      <Card 
                        key={name} 
                        className="p-4 cursor-pointer hover:bg-muted/50 transition-colors"
                        onClick={() => handleCalendarMealAdd(selectedCalendarDate, name)}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <Icon className="w-4 h-4 text-muted-foreground" />
                          <span className="font-medium text-sm">{name}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {meal?.name || 'Click to add meal'}
                        </p>
                        {meal && meal.assignedTo && (
                          <p className="text-xs text-primary mt-1">
                            {people.find(p => p.id === meal.assignedTo)?.name}
                          </p>
                        )}
                      </Card>
                    );
                  })}
                </div>
                
                <Button 
                  className="w-full bg-primary hover:bg-primary/90 text-primary-foreground rounded-full py-3 flex items-center justify-center gap-2"
                  onClick={() => setCraftMealOpen(true)}
                >
                  Craft Your Meal
                </Button>
              </div>
            )}
          </Card>
        )}
      </main>

      {/* Add Meal Dialog */}
      <Dialog open={addMealOpen} onOpenChange={setAddMealOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Meal</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="meal-name">Meal Name</Label>
              <Input
                id="meal-name"
                placeholder="e.g., Coffee with toasts"
                value={mealName}
                onChange={(e) => setMealName(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="meal-assigned">Assign to</Label>
              <select
                id="meal-assigned"
                className="w-full p-2 border rounded-md"
                value={selectedAssignedTo ?? ''}
                onChange={(e) => setSelectedAssignedTo(e.target.value || null)}
              >
                <option value="">Unassigned</option>
                {people.map(p => (
                  <option key={p.id} value={p.id.toString()}>{p.name}</option>
                ))}
              </select>
            </div>
            <div>
              <Label htmlFor="meal-description">Description (Optional)</Label>
              <Input
                id="meal-description"
                placeholder="e.g., Whole grain bread with butter"
                value={mealDescription}
                onChange={(e) => setMealDescription(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Day</Label>
                <p className="text-sm text-muted-foreground mt-1">{selectedDay}</p>
              </div>
              <div>
                <Label>Meal Time</Label>
                <p className="text-sm text-muted-foreground mt-1">{selectedMealTime}</p>
              </div>
            </div>
            <Button onClick={handleAddMeal} className="w-full">
              Add Meal
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Meal Dialog */}
      <Dialog open={editMealOpen} onOpenChange={setEditMealOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Meal</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="edit-meal-name">Meal Name</Label>
              <Input
                id="edit-meal-name"
                value={mealName}
                onChange={(e) => setMealName(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-meal-servings">Servings</Label>
                <Input
                  id="edit-meal-servings"
                  type="number"
                  min="1"
                  value={mealServings}
                  onChange={(e) => setMealServings(parseInt(e.target.value) || 1)}
                />
              </div>
              <div>
                <Label htmlFor="edit-meal-cook-time">Cook Time</Label>
                <Input
                  id="edit-meal-cook-time"
                  placeholder="e.g., 30 min"
                  value={mealCookTime}
                  onChange={(e) => setMealCookTime(e.target.value)}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="edit-meal-assigned">Assign to</Label>
              <select
                id="edit-meal-assigned"
                className="w-full p-2 border rounded-md"
                value={selectedAssignedTo ?? ''}
                onChange={(e) => setSelectedAssignedTo(e.target.value || null)}
              >
                <option value="">Unassigned</option>
                {people.map(p => (
                  <option key={p.id} value={p.id.toString()}>{p.name}</option>
                ))}
              </select>
            </div>
            <div>
              <Label htmlFor="edit-meal-description">Description (Optional)</Label>
              <Input
                id="edit-meal-description"
                value={mealDescription}
                onChange={(e) => setMealDescription(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="edit-meal-ingredients">Ingredients</Label>
              <Textarea
                id="edit-meal-ingredients"
                placeholder="List ingredients (one per line)"
                value={mealIngredients}
                onChange={(e) => setMealIngredients(e.target.value)}
                rows={4}
              />
            </div>
            <div>
              <Label htmlFor="edit-meal-instructions">Instructions</Label>
              <Textarea
                id="edit-meal-instructions"
                placeholder="Step by step instructions"
                value={mealInstructions}
                onChange={(e) => setMealInstructions(e.target.value)}
                rows={4}
              />
            </div>
            <Button onClick={handleUpdateMeal} className="w-full">
              Update Meal
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Plan Month Dialog */}
      <Dialog open={planMonthOpen} onOpenChange={setPlanMonthOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Plan Your Month</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Select Month</Label>
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={setSelectedDate}
                className="rounded-md border mx-auto"
              />
            </div>
            {selectedDate && (
              <div className="text-center p-3 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground">Selected Month:</p>
                <p className="font-semibold">
                  {selectedDate.toLocaleString('default', { month: 'long', year: 'numeric' })}
                </p>
              </div>
            )}
            <LoadingButton 
              onClick={handlePlanMonth} 
              className="w-full bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-md hover:shadow-lg transition-all duration-300"
              loading={planMonthLoading}
              loadingText="Planning..."
            >
              Start Planning
            </LoadingButton>
          </div>
        </DialogContent>
      </Dialog>

      {/* Craft Meal Dialog */}
      <Dialog open={craftMealOpen} onOpenChange={setCraftMealOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Craft Your Meal</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="craft-meal-name">Recipe Name</Label>
              <Input
                id="craft-meal-name"
                placeholder="e.g., Grilled Chicken Salad"
                value={craftMealName}
                onChange={(e) => setCraftMealName(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="craft-ingredients">Ingredients</Label>
              <Textarea
                id="craft-ingredients"
                placeholder="List your ingredients here..."
                value={craftMealIngredients}
                onChange={(e) => setCraftMealIngredients(e.target.value)}
                rows={4}
              />
            </div>
            <div>
              <Label htmlFor="craft-instructions">Cooking Instructions</Label>
              <Textarea
                id="craft-instructions"
                placeholder="Step by step cooking instructions..."
                value={craftMealInstructions}
                onChange={(e) => setCraftMealInstructions(e.target.value)}
                rows={4}
              />
            </div>
            <LoadingButton 
              onClick={handleCraftMeal} 
              className="w-full bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-md hover:shadow-lg transition-all duration-300"
              loading={craftMealLoading}
              loadingText="Crafting..."
            >
              Save Recipe
            </LoadingButton>
          </div>
        </DialogContent>
      </Dialog>

      {/* Quick Add Dialog */}
      <Dialog open={quickAddOpen} onOpenChange={setQuickAddOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Quick Add - Today's Meal</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="quick-meal-time">Meal Time</Label>
              <select 
                id="quick-meal-time"
                className="w-full p-2 border border-border rounded-md bg-background text-foreground"
                value={selectedMealTime}
                onChange={(e) => setSelectedMealTime(e.target.value)}
              >
                <option value="">Select meal time</option>
                {mealTimes.map(({ name }) => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
            </div>
            <div>
              <Label htmlFor="quick-meal-name">Meal Name</Label>
              <Input
                id="quick-meal-name"
                placeholder="e.g., Grilled Chicken Salad"
                value={mealName}
                onChange={(e) => setMealName(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="quick-meal-description">Description (Optional)</Label>
              <Input
                id="quick-meal-description"
                placeholder="Brief description"
                value={mealDescription}
                onChange={(e) => setMealDescription(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                Adding for: {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
              </span>
            </div>
            <div>
              <Label htmlFor="quick-meal-assigned">Assign to</Label>
              <select
                id="quick-meal-assigned"
                className="w-full p-2 border border-border rounded-md bg-background text-foreground"
                value={selectedAssignedTo ?? ''}
                onChange={(e) => setSelectedAssignedTo(e.target.value || null)}
              >
                <option value="">Unassigned</option>
                {people.map(p => (
                  <option key={p.id} value={p.id.toString()}>{p.name}</option>
                ))}
              </select>
            </div>
            <LoadingButton 
              onClick={handleQuickAdd} 
              className="w-full"
              loading={quickAddLoading}
              loadingText="Adding..."
            >
              Add to Today
            </LoadingButton>
          </div>
        </DialogContent>
      </Dialog>

      {/* Add Person Dialog */}
      <Dialog open={addPersonOpen} onOpenChange={setAddPersonOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New Person</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="person-name">Name *</Label>
              <Input
                id="person-name"
                placeholder="e.g., John Doe"
                value={newPersonName}
                onChange={(e) => setNewPersonName(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="person-preferences">Food Preferences (Optional)</Label>
              <Input
                id="person-preferences"
                placeholder="e.g., Vegetarian, Spicy food, Italian cuisine"
                value={newPersonPreferences}
                onChange={(e) => setNewPersonPreferences(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="person-allergies">Allergies (Optional)</Label>
              <Input
                id="person-allergies"
                placeholder="e.g., Nuts, Dairy, Gluten"
                value={newPersonAllergies}
                onChange={(e) => setNewPersonAllergies(e.target.value)}
              />
            </div>
            <div className="bg-muted/50 p-3 rounded-lg">
              <p className="text-sm text-muted-foreground">
                💡 Adding preferences and allergies helps create personalized meal plans
              </p>
            </div>
            <Button onClick={handleAddPerson} className="w-full">
              Add Person
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Person Dialog */}
      <Dialog open={editPersonOpen} onOpenChange={setEditPersonOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Person</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="edit-person-name">Name *</Label>
              <Input
                id="edit-person-name"
                placeholder="e.g., Salman"
                value={editPersonName}
                onChange={(e) => setEditPersonName(e.target.value)}
              />
            </div>
            <Button onClick={handleUpdatePerson} className="w-full">
              Update Person
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Meal Plan Dialog */}
      <Dialog open={editMealPlanOpen} onOpenChange={setEditMealPlanOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Meal Plan</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="edit-meal-plan-name">Meal Name</Label>
              <Input
                id="edit-meal-plan-name"
                value={editMealPlanName}
                onChange={(e) => setEditMealPlanName(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Day</Label>
                <p className="text-sm text-muted-foreground mt-1">{selectedDay}</p>
              </div>
              <div>
                <Label>Meal Time</Label>
                <p className="text-sm text-muted-foreground mt-1">{editingMealPlan?.mealTime}</p>
              </div>
            </div>
            <Button onClick={handleUpdateMealPlan} className="w-full">
              Update Meal
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <BottomNav />
      
      {/* Custom Sign In Notification */}
      {showSignInNotification && (
        <div className="fixed inset-0 z-50 flex items-center justify-center animate-fade-up">
          <div className="bg-card border border-border rounded-lg p-4 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                  <Lock className="w-4 h-4 text-primary" />
                </div>
                <span className="text-sm font-medium">Sign in for more features</span>
              </div>
              <Button
                size="sm"
                className="h-7 px-3 text-xs"
                onClick={() => {
                  setShowSignInNotification(false);
                  navigate('/auth');
                }}
              >
                Sign In
              </Button>
            </div>
          </div>
        </div>
      )}
      
      {/* Custom Subscription Notification */}
      {showSubscriptionNotification && (
        <div className="fixed inset-0 z-50 flex items-center justify-center animate-fade-up">
          <div className="bg-card border border-border rounded-lg p-4 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                  <Crown className="w-4 h-4 text-primary" />
                </div>
                <span className="text-sm font-medium">Subscribe for more features</span>
              </div>
              <Button
                size="sm"
                className="h-7 px-3 text-xs"
                onClick={() => {
                  setShowSubscriptionNotification(false);
                  navigate('/billing');
                }}
              >
                Subscribe
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};