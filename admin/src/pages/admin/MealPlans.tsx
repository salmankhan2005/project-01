import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, Plus, Edit, Trash2, Calendar as CalendarIcon, Users } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const MealPlans = () => {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [openDialog, setOpenDialog] = useState(false);
  const [editingPlan, setEditingPlan] = useState<any>(null);

  const [mealPlans, setMealPlans] = useState([
    { id: 1, name: "7-Day Keto Plan", duration: "7 days", type: "Keto", users: 234, status: "Active", createdBy: "Chef John" },
    { id: 2, name: "Mediterranean Weekly", duration: "7 days", type: "Mediterranean", users: 456, status: "Active", createdBy: "Chef Maria" },
    { id: 3, name: "Vegan 14-Day", duration: "14 days", type: "Vegan", users: 189, status: "Active", createdBy: "Chef Sarah" },
    { id: 4, name: "Low-Carb Month", duration: "30 days", type: "Low-Carb", users: 78, status: "Draft", createdBy: "Chef Mike" },
  ]);

  const handleSavePlan = (formData: any) => {
    if (editingPlan) {
      setMealPlans(mealPlans.map(p => p.id === editingPlan.id ? { ...p, ...formData } : p));
      toast({ title: "Meal Plan Updated", description: "Meal plan updated successfully" });
    } else {
      setMealPlans([...mealPlans, { id: Date.now(), ...formData, users: 0, createdBy: "Admin" }]);
      toast({ title: "Meal Plan Created", description: "New meal plan created successfully" });
    }
    setOpenDialog(false);
    setEditingPlan(null);
  };

  const handleDeletePlan = (id: number) => {
    setMealPlans(mealPlans.filter(p => p.id !== id));
    toast({ title: "Meal Plan Deleted", description: "Meal plan removed successfully" });
  };

  const filteredPlans = mealPlans.filter((plan) =>
    plan.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-heading font-bold">Meal Plans</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">Create and manage meal plan templates</p>
        </div>
        <Dialog open={openDialog} onOpenChange={setOpenDialog}>
          <DialogTrigger asChild>
            <Button className="gap-2 w-full sm:w-auto" onClick={() => setEditingPlan(null)}>
              <Plus className="h-4 w-4" />
              Create Meal Plan
            </Button>
          </DialogTrigger>
          <DialogContent>
            <MealPlanForm plan={editingPlan} onSave={handleSavePlan} />
          </DialogContent>
        </Dialog>
      </div>

      <Card className="shadow-lg">
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search meal plans..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredPlans.map((plan) => (
              <Card key={plan.id} className="">
                <CardContent className="p-4 space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-heading font-bold text-lg">{plan.name}</h3>
                      <p className="text-sm text-muted-foreground">by {plan.createdBy}</p>
                    </div>
                    <Badge variant={plan.status === "Active" ? "default" : "secondary"}>
                      {plan.status}
                    </Badge>
                  </div>
                  
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline" className="text-xs">{plan.type}</Badge>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <CalendarIcon className="h-4 w-4" />
                      {plan.duration}
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4" />
                      {plan.users} users
                    </div>
                  </div>

                  <div className="flex gap-2 pt-2">
                    <Dialog open={openDialog && editingPlan?.id === plan.id} onOpenChange={setOpenDialog}>
                      <DialogTrigger asChild>
                        <Button size="sm" variant="outline" className="flex-1" onClick={() => setEditingPlan(plan)}>
                          <Edit className="h-3 w-3 mr-1" /> Edit
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <MealPlanForm plan={plan} onSave={handleSavePlan} />
                      </DialogContent>
                    </Dialog>
                    <Button size="sm" variant="outline" onClick={() => handleDeletePlan(plan.id)}>
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const MealPlanForm = ({ plan, onSave }: { plan: any; onSave: (data: any) => void }) => {
  const [formData, setFormData] = useState({
    name: plan?.name || "",
    duration: plan?.duration || "",
    type: plan?.type || "Balanced",
    status: plan?.status || "Draft"
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <DialogHeader>
        <DialogTitle>{plan ? "Edit Meal Plan" : "Create Meal Plan"}</DialogTitle>
        <DialogDescription>
          {plan ? "Update meal plan details" : "Create a new meal plan template"}
        </DialogDescription>
      </DialogHeader>
      <div className="space-y-4 py-4">
        <div className="space-y-2">
          <Label htmlFor="name">Plan Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="7-Day Keto Plan"
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="duration">Duration</Label>
          <Input
            id="duration"
            value={formData.duration}
            onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
            placeholder="7 days"
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="type">Plan Type</Label>
          <Select value={formData.type} onValueChange={(value) => setFormData({ ...formData, type: value })}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Balanced">Balanced</SelectItem>
              <SelectItem value="Keto">Keto</SelectItem>
              <SelectItem value="Vegan">Vegan</SelectItem>
              <SelectItem value="Vegetarian">Vegetarian</SelectItem>
              <SelectItem value="Mediterranean">Mediterranean</SelectItem>
              <SelectItem value="Low-Carb">Low-Carb</SelectItem>
              <SelectItem value="High-Protein">High-Protein</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="status">Status</Label>
          <Select value={formData.status} onValueChange={(value) => setFormData({ ...formData, status: value })}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Draft">Draft</SelectItem>
              <SelectItem value="Active">Active</SelectItem>
              <SelectItem value="Archived">Archived</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <DialogFooter>
        <Button type="submit">{plan ? "Update" : "Create"} Plan</Button>
      </DialogFooter>
    </form>
  );
};

export default MealPlans;
