import { useState, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import { BottomNav } from '@/components/layout/BottomNav';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LoadingButton } from '@/components/LoadingButton';
import { GlowCard } from '@/components/GlowCard';
import { Checkbox } from '@/components/ui/checkbox';
import { Plus, Trash2, Check } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { useNavigate } from 'react-router-dom';
import { InventoryAnimation } from '@/components/InventoryAnimation';
import { apiService } from '@/services/api';

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
  const [activeTab, setActiveTab] = useState('recent');
  const [allItems, setAllItems] = useState<typeof mockItems>([]);
  const [pastItems, setPastItems] = useState<typeof mockItems>([]);
  const [recentItems, setRecentItems] = useState<any[]>([]);
  const [addItemLoading, setAddItemLoading] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated) {
      loadShoppingData();
    }
  }, [isAuthenticated]);

  const loadShoppingData = async () => {
    try {
      const [shoppingResponse, recentResponse] = await Promise.all([
        apiService.getShoppingItems(),
        apiService.getRecentItems()
      ]);
      
      setItems(shoppingResponse.items.map(item => ({
        id: item.id,
        name: item.item_name,
        category: item.category,
        checked: item.is_completed
      })));
      
      setRecentItems(recentResponse.recent_items);
    } catch (error) {
      console.error('Failed to load shopping data:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleItem = async (id: number | string) => {
    const item = items.find(item => item.id === id);
    if (!item) return;
    
    try {
      if (isAuthenticated) {
        await apiService.updateShoppingItem(String(id), {
          is_completed: !item.checked
        });
      }
      
      setItems(items.map(item => 
        item.id === id ? { ...item, checked: !item.checked } : item
      ));
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update item. Please try again.",
        variant: "destructive",
      });
    }
  };

  const deleteItem = async (id: number | string) => {
    try {
      if (isAuthenticated) {
        await apiService.deleteShoppingItem(String(id));
      }
      
      setItems(items.filter(item => item.id !== id));
      toast({
        title: "Item removed",
        description: "Item has been deleted from your list",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete item. Please try again.",
        variant: "destructive",
      });
    }
  };

  const addItem = async () => {
    if (!newItemName.trim() || !newItemCategory) {
      toast({
        title: "Missing information",
        description: "Please enter item name and category",
        variant: "destructive",
      });
      return;
    }

    setAddItemLoading(true);
    
    try {
      if (isAuthenticated) {
        const response = await apiService.addShoppingItem({
          item_name: newItemName.trim(),
          category: newItemCategory,
          quantity: 1,
          unit: 'pcs'
        });
        
        const newItem = {
          id: response.item.id,
          name: response.item.item_name,
          category: response.item.category,
          checked: response.item.is_completed
        };
        
        setItems([newItem, ...items]);
        
        // Refresh recent items
        const recentResponse = await apiService.getRecentItems();
        setRecentItems(recentResponse.recent_items);
      } else {
        // Fallback for non-authenticated users
        const newItem = {
          id: Math.max(...items.map(i => i.id), 0) + 1,
          name: newItemName.trim(),
          category: newItemCategory,
          checked: false,
        };
        setItems([...items, newItem]);
      }
      
      setNewItemName('');
      setNewItemCategory('');
      setIsDialogOpen(false);
      
      toast({
        title: "Item added",
        description: `${newItemName} has been added to your list`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add item. Please try again.",
        variant: "destructive",
      });
    } finally {
      setAddItemLoading(false);
    }
  };

  const addRecentItem = async (recentItem: any) => {
    try {
      if (isAuthenticated) {
        const response = await apiService.addShoppingItem({
          item_name: recentItem.item_name,
          category: recentItem.category,
          quantity: 1,
          unit: 'pcs'
        });
        
        const newItem = {
          id: response.item.id,
          name: response.item.item_name,
          category: response.item.category,
          checked: response.item.is_completed
        };
        
        setItems([newItem, ...items]);
        
        toast({
          title: "Item added",
          description: `${recentItem.item_name} has been added to your list`,
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add item. Please try again.",
        variant: "destructive",
      });
    }
  };
  
  const handleDone = () => {
    // Move current items to past (push current past to history)
    if (pastItems.length > 0) {
      // Keep only the most recent past list
      setPastItems(items);
    } else {
      setPastItems(items);
    }
    
    // Move current items to all items
    setAllItems(prev => [...items, ...prev]);
    
    // Clear current items
    setItems([]);
    
    toast({
      title: "Shopping completed!",
      description: "List moved to completed items",
    });
  };

  const ShoppingList = () => (
    <div className="space-y-3">
      {items.map((item, idx) => (
        <GlowCard key={item.id} className="p-4 animate-fade-up bg-gradient-to-r from-card to-card/80 hover:shadow-md" 
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
        </GlowCard>
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
        {/* Inventory Animation */}
        <div className="mb-8 flex justify-center">
          <InventoryAnimation className="w-48 h-32" />
        </div>

        {/* Custom Tab Navigation */}
        <div className="mb-8">
          <div className="bg-muted/30 rounded-full p-2 flex">
            <button
              onClick={() => setActiveTab('recent')}
              className={`flex-1 py-3 px-6 rounded-full text-center font-medium transition-all ${
                activeTab === 'recent'
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-foreground hover:bg-muted/50'
              }`}
            >
              Recent
            </button>
            <button
              onClick={() => setActiveTab('all')}
              className={`flex-1 py-3 px-6 rounded-full text-center font-medium transition-all ${
                activeTab === 'all'
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-foreground hover:bg-muted/50'
              }`}
            >
              All items
            </button>
            <button
              onClick={() => setActiveTab('past')}
              className={`flex-1 py-3 px-6 rounded-full text-center font-medium transition-all ${
                activeTab === 'past'
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-foreground hover:bg-muted/50'
              }`}
            >
              Past
            </button>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'recent' && (
          <div className="space-y-6">
            <ShoppingList />
            
            {/* Recent Items Section */}
            {recentItems.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4">Recent Items</h3>
                <div className="space-y-2">
                  {recentItems.map((item, idx) => (
                    <GlowCard key={item.id} className="p-3 animate-fade-up bg-gradient-to-r from-muted/50 to-muted/30 hover:shadow-md" 
                          style={{ animationDelay: `${idx * 0.05}s` }}>
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-sm">{item.item_name}</p>
                          <p className="text-xs text-muted-foreground">{item.category}</p>
                        </div>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => addRecentItem(item)}
                          className="h-8 px-3"
                        >
                          <Plus className="w-3 h-3 mr-1" />
                          Add
                        </Button>
                      </div>
                    </GlowCard>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        {activeTab === 'all' && (
          <div className="space-y-6">
            <div className="space-y-3">
              <Card className="p-4 animate-fade-up">
                <div className="flex items-center gap-3">
                  <Checkbox checked={false} disabled className="data-[state=checked]:bg-primary" />
                  <div className="flex-1">
                    <p className="font-medium">Apples</p>
                    <p className="text-xs text-muted-foreground">Fruits</p>
                  </div>
                </div>
              </Card>
              <Card className="p-4 animate-fade-up">
                <div className="flex items-center gap-3">
                  <Checkbox checked={false} disabled className="data-[state=checked]:bg-primary" />
                  <div className="flex-1">
                    <p className="font-medium">Milk</p>
                    <p className="text-xs text-muted-foreground">Dairy</p>
                  </div>
                </div>
              </Card>
              <Card className="p-4 animate-fade-up">
                <div className="flex items-center gap-3">
                  <Checkbox checked={false} disabled className="data-[state=checked]:bg-primary" />
                  <div className="flex-1">
                    <p className="font-medium">Bread</p>
                    <p className="text-xs text-muted-foreground">Pantry</p>
                  </div>
                </div>
              </Card>
              <Card className="p-4 animate-fade-up">
                <div className="flex items-center gap-3">
                  <Checkbox checked={false} disabled className="data-[state=checked]:bg-primary" />
                  <div className="flex-1">
                    <p className="font-medium">Tomatoes</p>
                    <p className="text-xs text-muted-foreground">Vegetables</p>
                  </div>
                </div>
              </Card>
              <Card className="p-4 animate-fade-up">
                <div className="flex items-center gap-3">
                  <Checkbox checked={false} disabled className="data-[state=checked]:bg-primary" />
                  <div className="flex-1">
                    <p className="font-medium">Rice</p>
                    <p className="text-xs text-muted-foreground">Pantry</p>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        )}
        {activeTab === 'past' && (
          <div className="space-y-3">
            {pastItems.length > 0 ? (
              pastItems.map((item, idx) => (
                <Card key={item.id} className="p-4 animate-fade-up" 
                      style={{ animationDelay: `${idx * 0.05}s` }}>
                  <div className="flex items-center gap-3">
                    <Checkbox
                      checked={item.checked}
                      disabled
                      className="data-[state=checked]:bg-primary"
                    />
                    <div className="flex-1">
                      <p className={`font-medium ${item.checked ? 'line-through text-muted-foreground' : ''}`}>
                        {item.name}
                      </p>
                      <p className="text-xs text-muted-foreground">{item.category}</p>
                    </div>
                  </div>
                </Card>
              ))
            ) : (
              <Card className="p-8 text-center">
                <p className="text-muted-foreground">No past shopping lists</p>
              </Card>
            )}
          </div>
        )}

        {/* Stats - Only show when not in 'all' tab */}
        {activeTab !== 'all' && (
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
        )}

        {/* Action Buttons - Only show in recent tab */}
        {activeTab === 'recent' && (
          <div className="space-y-3 mt-6">
            <Button 
              className={`w-full h-12 gap-2 ${
                items.filter(i => !i.checked).length === 0 && items.length > 0
                  ? 'bg-green-600 hover:bg-green-700 text-white'
                  : 'bg-muted text-muted-foreground cursor-not-allowed'
              }`}
              onClick={handleDone}
              disabled={items.filter(i => !i.checked).length > 0 || items.length === 0}
            >
              <Check className="w-5 h-5" />
              Done
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
                  <LoadingButton 
                    className="w-full bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-md hover:shadow-lg transition-all duration-300" 
                    onClick={addItem}
                    loading={addItemLoading}
                    loadingText="Adding..."
                  >
                    Add to List
                  </LoadingButton>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        )}
      </main>

      <BottomNav />
    </div>
  );
};
