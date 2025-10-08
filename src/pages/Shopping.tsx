import { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { BottomNav } from '@/components/layout/BottomNav';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Plus, Trash2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { useNavigate } from 'react-router-dom';

const mockItems = [
  { id: 1, name: 'Chicken Breast', category: 'Meat', checked: false },
  { id: 2, name: 'Mixed Salad', category: 'Vegetables', checked: false },
  { id: 3, name: 'Olive Oil', category: 'Pantry', checked: true },
  { id: 4, name: 'Spaghetti', category: 'Pasta', checked: false },
];

export const Shopping = () => {
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [items, setItems] = useState(mockItems);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newItemName, setNewItemName] = useState('');
  const [newItemCategory, setNewItemCategory] = useState('');

  const toggleItem = (id: number) => {
    setItems(items.map(item => 
      item.id === id ? { ...item, checked: !item.checked } : item
    ));
  };

  const deleteItem = (id: number) => {
    setItems(items.filter(item => item.id !== id));
    toast({
      title: "Item removed",
      description: "Item has been deleted from your list",
    });
  };

  const addItem = () => {
    if (!newItemName.trim() || !newItemCategory) {
      toast({
        title: "Missing information",
        description: "Please enter item name and category",
        variant: "destructive",
      });
      return;
    }

    const newItem = {
      id: Math.max(...items.map(i => i.id), 0) + 1,
      name: newItemName.trim(),
      category: newItemCategory,
      checked: false,
    };

    setItems([...items, newItem]);
    setNewItemName('');
    setNewItemCategory('');
    setIsDialogOpen(false);
    toast({
      title: "Item added",
      description: `${newItem.name} has been added to your list`,
    });
  };
  
  const generateFromMealPlan = () => {
    const mealPlanItems = [
      { id: Date.now() + 1, name: 'Chicken Breast', category: 'Meat', checked: false },
      { id: Date.now() + 2, name: 'Mixed Greens', category: 'Vegetables', checked: false },
      { id: Date.now() + 3, name: 'Cherry Tomatoes', category: 'Vegetables', checked: false },
      { id: Date.now() + 4, name: 'Olive Oil', category: 'Pantry', checked: false },
    ];
    setItems(prev => [...prev, ...mealPlanItems]);
    toast({
      title: "Items generated",
      description: "Shopping list updated from your meal plan",
    });
  };

  const ShoppingList = () => (
    <div className="space-y-3">
      {items.map((item, idx) => (
        <Card key={item.id} className="p-4 animate-fade-up" 
              style={{ animationDelay: `${idx * 0.05}s` }}>
          <div className="flex items-center gap-3">
            <Checkbox
              checked={item.checked}
              onCheckedChange={() => toggleItem(item.id)}
              className="data-[state=checked]:bg-primary"
            />
            <div className="flex-1">
              <p className={`font-medium ${item.checked ? 'line-through text-muted-foreground' : ''}`}>
                {item.name}
              </p>
              <p className="text-xs text-muted-foreground">{item.category}</p>
            </div>
            <Button variant="ghost" size="icon" onClick={() => deleteItem(item.id)}>
              <Trash2 className="w-4 h-4 text-destructive" />
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-background pb-20 sm:pb-24">
      <Header 
        title="Shopping List" 
        showBackButton={true}
        onBackClick={() => navigate(-1)}
      />
      
      <main className="px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 md:py-8 max-w-4xl mx-auto">
        {isAuthenticated ? (
          <Tabs defaultValue="recent" className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-6">
              <TabsTrigger value="recent">Recent</TabsTrigger>
              <TabsTrigger value="all">All Lists</TabsTrigger>
              <TabsTrigger value="past">Past</TabsTrigger>
            </TabsList>
            
            <TabsContent value="recent">
              <ShoppingList />
            </TabsContent>
            
            <TabsContent value="all">
              <Card className="p-8 text-center">
                <p className="text-muted-foreground">View all your shopping lists</p>
              </Card>
            </TabsContent>
            
            <TabsContent value="past">
              <Card className="p-8 text-center">
                <p className="text-muted-foreground">Past shopping lists</p>
              </Card>
            </TabsContent>
          </Tabs>
        ) : (
          <ShoppingList />
        )}

        {/* Stats */}
        <Card className="mt-6 p-4 bg-primary/5 border-primary/20">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-muted-foreground">Items Left</p>
              <p className="text-2xl font-bold text-primary">
                {items.filter(i => !i.checked).length}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Completed</p>
              <p className="text-2xl font-bold text-foreground">
                {items.filter(i => i.checked).length}
              </p>
            </div>
          </div>
        </Card>

        {/* Action Buttons */}
        <div className="space-y-3 mt-6">
          <Button 
            variant="outline" 
            className="w-full h-12 gap-2"
            onClick={generateFromMealPlan}
          >
            <Plus className="w-5 h-5" />
            Generate from Meal Plan
          </Button>
          
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="w-full h-12 gap-2">
                <Plus className="w-5 h-5" />
                Add Item Manually
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Item</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="item-name">Item Name</Label>
                  <Input
                    id="item-name"
                    placeholder="e.g., Chicken Breast"
                    value={newItemName}
                    onChange={(e) => setNewItemName(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="item-category">Category</Label>
                  <Select value={newItemCategory} onValueChange={setNewItemCategory}>
                    <SelectTrigger id="item-category">
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Meat">Meat</SelectItem>
                      <SelectItem value="Vegetables">Vegetables</SelectItem>
                      <SelectItem value="Fruits">Fruits</SelectItem>
                      <SelectItem value="Dairy">Dairy</SelectItem>
                      <SelectItem value="Pantry">Pantry</SelectItem>
                      <SelectItem value="Pasta">Pasta</SelectItem>
                      <SelectItem value="Beverages">Beverages</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button className="w-full" onClick={addItem}>
                  Add to List
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </main>

      <BottomNav />
    </div>
  );
};
