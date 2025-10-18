import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { CreditCard, Plus, Edit, Trash2, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const SubscriptionPlans = () => {
  const { toast } = useToast();
  const [plans, setPlans] = useState([
    { 
      id: 1, 
      name: "Free", 
      price: 0, 
      interval: "month", 
      features: ["Basic meal planning", "5 recipes", "Limited support"], 
      status: "Active",
      subscribers: 1250
    },
    { 
      id: 2, 
      name: "Basic", 
      price: 9.99, 
      interval: "month", 
      features: ["Advanced meal planning", "50 recipes", "Email support", "Shopping lists"], 
      status: "Active",
      subscribers: 450
    },
    { 
      id: 3, 
      name: "Premium", 
      price: 19.99, 
      interval: "month", 
      features: ["Unlimited meal planning", "Unlimited recipes", "Priority support", "AI recommendations", "Custom themes"], 
      status: "Active",
      subscribers: 180
    },
  ]);

  const [formData, setFormData] = useState({
    name: "",
    price: "",
    interval: "month",
    features: ""
  });

  const [openDialog, setOpenDialog] = useState(false);

  const handleCreatePlan = (e: React.FormEvent) => {
    e.preventDefault();
    
    const newPlan = {
      id: Date.now(),
      name: formData.name,
      price: parseFloat(formData.price),
      interval: formData.interval,
      features: formData.features.split('\n').filter(f => f.trim()),
      status: "Active",
      subscribers: 0
    };

    setPlans([...plans, newPlan]);
    setFormData({ name: "", price: "", interval: "month", features: "" });
    setOpenDialog(false);
    toast({ title: "Success", description: "Subscription plan created successfully" });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-heading font-bold">Subscription Plans</h1>
          <p className="text-muted-foreground mt-1">Manage subscription plans and pricing</p>
        </div>
        <Dialog open={openDialog} onOpenChange={setOpenDialog}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Create Plan
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Plan</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreatePlan} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Plan Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="price">Price ($)</Label>
                <Input
                  id="price"
                  type="number"
                  step="0.01"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="features">Features (one per line)</Label>
                <Textarea
                  id="features"
                  value={formData.features}
                  onChange={(e) => setFormData({ ...formData, features: e.target.value })}
                  placeholder="Feature 1&#10;Feature 2&#10;Feature 3"
                  rows={4}
                  required
                />
              </div>
              
              <Button type="submit" className="w-full">
                Create Plan
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <Card key={plan.id} className={`relative ${plan.name === "Premium" ? "border-primary" : ""}`}>
            {plan.name === "Premium" && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-primary text-primary-foreground">Most Popular</Badge>
              </div>
            )}
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">{plan.name}</CardTitle>
              <div className="text-3xl font-bold">
                ${plan.price}
                <span className="text-sm font-normal text-muted-foreground">/{plan.interval}</span>
              </div>
              <p className="text-sm text-muted-foreground">{plan.subscribers} subscribers</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                {plan.features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-green-500" />
                    <span className="text-sm">{feature}</span>
                  </div>
                ))}
              </div>
              
              <div className="flex gap-2 pt-4">
                <Button size="sm" variant="outline" className="flex-1">
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </Button>
                <Button size="sm" variant="outline">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Plan Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Plan Statistics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <p className="text-2xl font-bold">{plans.reduce((sum, p) => sum + p.subscribers, 0)}</p>
              <p className="text-sm text-muted-foreground">Total Subscribers</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <p className="text-2xl font-bold">${plans.reduce((sum, p) => sum + (p.price * p.subscribers), 0).toFixed(2)}</p>
              <p className="text-sm text-muted-foreground">Monthly Revenue</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <p className="text-2xl font-bold">{plans.length}</p>
              <p className="text-sm text-muted-foreground">Active Plans</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SubscriptionPlans;