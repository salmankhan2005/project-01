import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Edit, Trash2, Tag } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Categories = () => {
  const { toast } = useToast();
  const [openDialog, setOpenDialog] = useState(false);
  const [editingCategory, setEditingCategory] = useState<any>(null);

  const [categories, setCategories] = useState([
    { id: 1, name: "Breakfast", description: "Morning meals and brunch ideas", recipeCount: 45, color: "#F59E0B" },
    { id: 2, name: "Lunch", description: "Midday meals and light dishes", recipeCount: 67, color: "#10B981" },
    { id: 3, name: "Dinner", description: "Evening meals and main courses", recipeCount: 89, color: "#3B82F6" },
    { id: 4, name: "Desserts", description: "Sweet treats and desserts", recipeCount: 34, color: "#EC4899" },
    { id: 5, name: "Snacks", description: "Quick bites and appetizers", recipeCount: 52, color: "#8B5CF6" },
    { id: 6, name: "Beverages", description: "Drinks and smoothies", recipeCount: 28, color: "#06B6D4" },
  ]);

  const [tags, setTags] = useState([
    { id: 1, name: "Quick", usage: 123 },
    { id: 2, name: "Healthy", usage: 234 },
    { id: 3, name: "Low-Carb", usage: 156 },
    { id: 4, name: "Gluten-Free", usage: 89 },
    { id: 5, name: "Dairy-Free", usage: 67 },
    { id: 6, name: "High-Protein", usage: 145 },
  ]);

  const handleSaveCategory = (formData: any) => {
    if (editingCategory) {
      setCategories(categories.map(c => c.id === editingCategory.id ? { ...c, ...formData } : c));
      toast({ title: "Category Updated", description: "Category updated successfully" });
    } else {
      setCategories([...categories, { id: Date.now(), ...formData, recipeCount: 0 }]);
      toast({ title: "Category Created", description: "New category created successfully" });
    }
    setOpenDialog(false);
    setEditingCategory(null);
  };

  const handleDeleteCategory = (id: number) => {
    setCategories(categories.filter(c => c.id !== id));
    toast({ title: "Category Deleted", description: "Category removed successfully" });
  };

  const handleDeleteTag = (id: number) => {
    setTags(tags.filter(t => t.id !== id));
    toast({ title: "Tag Deleted", description: "Tag removed successfully" });
  };

  return (
    <div className="space-y-4 md:space-y-6">
      <div>
        <h1 className="text-3xl md:text-4xl font-heading font-bold">Categories & Tags</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Organize recipes with categories and tags</p>
      </div>

      {/* Categories */}
      <Card className="shadow-lg">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <CardTitle className="font-heading text-lg md:text-xl">Recipe Categories</CardTitle>
            <Dialog open={openDialog} onOpenChange={setOpenDialog}>
              <DialogTrigger asChild>
                <Button className="gap-2 w-full sm:w-auto" size="sm" onClick={() => setEditingCategory(null)}>
                  <Plus className="h-4 w-4" />
                  Add Category
                </Button>
              </DialogTrigger>
              <DialogContent>
                <CategoryForm category={editingCategory} onSave={handleSaveCategory} />
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categories.map((category) => (
              <Card key={category.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: category.color }}
                      />
                      <h3 className="font-heading font-bold">{category.name}</h3>
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      {category.recipeCount} recipes
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{category.description}</p>
                  <div className="flex gap-2">
                    <Dialog open={openDialog && editingCategory?.id === category.id} onOpenChange={setOpenDialog}>
                      <DialogTrigger asChild>
                        <Button size="sm" variant="outline" className="flex-1" onClick={() => setEditingCategory(category)}>
                          <Edit className="h-3 w-3 mr-1" /> Edit
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <CategoryForm category={category} onSave={handleSaveCategory} />
                      </DialogContent>
                    </Dialog>
                    <Button size="sm" variant="outline" onClick={() => handleDeleteCategory(category.id)}>
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Tags */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="font-heading text-lg md:text-xl flex items-center gap-2">
            <Tag className="h-5 w-5" />
            Recipe Tags
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            {tags.map((tag) => (
              <div key={tag.id} className="flex items-center gap-2 px-3 py-2 border rounded-lg bg-muted/30">
                <Badge variant="outline" className="font-normal">
                  {tag.name}
                </Badge>
                <span className="text-xs text-muted-foreground">{tag.usage}</span>
                <Button 
                  size="icon" 
                  variant="ghost" 
                  className="h-5 w-5" 
                  onClick={() => handleDeleteTag(tag.id)}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const CategoryForm = ({ category, onSave }: { category: any; onSave: (data: any) => void }) => {
  const [formData, setFormData] = useState({
    name: category?.name || "",
    description: category?.description || "",
    color: category?.color || "#3B82F6"
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <DialogHeader>
        <DialogTitle>{category ? "Edit Category" : "Create Category"}</DialogTitle>
        <DialogDescription>
          {category ? "Update category details" : "Add a new recipe category"}
        </DialogDescription>
      </DialogHeader>
      <div className="space-y-4 py-4">
        <div className="space-y-2">
          <Label htmlFor="name">Category Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Breakfast"
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Morning meals and brunch ideas"
            rows={3}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="color">Color</Label>
          <div className="flex gap-2">
            <Input
              id="color"
              type="color"
              value={formData.color}
              onChange={(e) => setFormData({ ...formData, color: e.target.value })}
              className="w-20 h-10"
            />
            <Input
              value={formData.color}
              onChange={(e) => setFormData({ ...formData, color: e.target.value })}
              placeholder="#3B82F6"
              className="flex-1"
            />
          </div>
        </div>
      </div>
      <DialogFooter>
        <Button type="submit">{category ? "Update" : "Create"} Category</Button>
      </DialogFooter>
    </form>
  );
};

export default Categories;
