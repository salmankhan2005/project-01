import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TrendingUp, Users, ChefHat, DollarSign } from "lucide-react";

const Analytics = () => {
  const stats = [
    { label: "Total Users", value: "12,543", change: "+12.5%", icon: Users, trend: "up" },
    { label: "Active Recipes", value: "1,234", change: "+8.2%", icon: ChefHat, trend: "up" },
    { label: "Monthly Revenue", value: "$54,230", change: "+15.3%", icon: DollarSign, trend: "up" },
    { label: "Engagement Rate", value: "68%", change: "+5.1%", icon: TrendingUp, trend: "up" },
  ];

  const userGrowthData = [
    { month: "Jan", users: 4000, active: 2400 },
    { month: "Feb", users: 5200, active: 3200 },
    { month: "Mar", users: 6800, active: 4100 },
    { month: "Apr", users: 8200, active: 5300 },
    { month: "May", users: 10500, active: 6800 },
    { month: "Jun", users: 12543, active: 8500 },
  ];

  const recipeViewsData = [
    { name: "Mon", views: 2400 },
    { name: "Tue", views: 3200 },
    { name: "Wed", views: 2800 },
    { name: "Thu", views: 3800 },
    { name: "Fri", views: 4200 },
    { name: "Sat", views: 5100 },
    { name: "Sun", views: 4800 },
  ];

  const categoryDistribution = [
    { name: "Breakfast", value: 450 },
    { name: "Lunch", value: 670 },
    { name: "Dinner", value: 890 },
    { name: "Desserts", value: 340 },
    { name: "Snacks", value: 520 },
  ];

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"];

  return (
    <div className="space-y-4 sm:space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-heading font-bold">Analytics Dashboard</h1>
        <p className="text-muted-foreground mt-1 text-xs sm:text-sm md:text-base">Monitor platform performance and metrics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3 sm:gap-4">
        {stats.map((stat, idx) => (
          <Card key={idx} className="shadow-lg">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">{stat.label}</p>
                  <p className="text-2xl font-bold font-mono">{stat.value}</p>
                  <p className="text-xs text-primary mt-1 font-mono">{stat.change}</p>
                </div>
                <div className="p-3 rounded-full bg-primary/10 text-primary">
                  <stat.icon className="h-5 w-5" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* User Growth Chart */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="font-heading">User Growth</CardTitle>
        </CardHeader>
        <CardContent className="p-3 sm:p-6">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={userGrowthData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="users" stroke="#3B82F6" strokeWidth={2} name="Total Users" />
              <Line type="monotone" dataKey="active" stroke="#10B981" strokeWidth={2} name="Active Users" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-3 sm:gap-4">
        {/* Recipe Views Chart */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="font-heading">Weekly Recipe Views</CardTitle>
          </CardHeader>
          <CardContent className="p-3 sm:p-6">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={recipeViewsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="views" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Category Distribution */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="font-heading">Recipe Categories</CardTitle>
          </CardHeader>
          <CardContent className="p-3 sm:p-6">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(Number(percent) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Analytics;
