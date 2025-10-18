import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, UserPlus, Edit, Trash2, Download, Trash, Ban } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/hooks/use-toast";

const Users = () => {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [editingUser, setEditingUser] = useState<any>(null);
  const [selectedUsers, setSelectedUsers] = useState<number[]>([]);

  const [users, setUsers] = useState([
    { id: 1, name: "John Doe", email: "john@example.com", role: "User", subscription: "Premium", status: "Active", joinDate: "2024-01-15" },
    { id: 2, name: "Jane Smith", email: "jane@example.com", role: "Professional", subscription: "Basic", status: "Active", joinDate: "2024-02-20" },
    { id: 3, name: "Mike Johnson", email: "mike@example.com", role: "User", subscription: "Free", status: "Active", joinDate: "2024-03-10" },
    { id: 4, name: "Sarah Williams", email: "sarah@example.com", role: "User", subscription: "Premium", status: "Inactive", joinDate: "2024-01-05" },
    { id: 5, name: "Tom Brown", email: "tom@example.com", role: "Professional", subscription: "Premium", status: "Active", joinDate: "2024-02-28" },
  ]);

  const handleSaveUser = (formData: any) => {
    if (editingUser) {
      setUsers(users.map(u => u.id === editingUser.id ? { ...u, ...formData } : u));
      toast({ title: "User Updated", description: "User details updated successfully" });
    } else {
      setUsers([...users, { id: Date.now(), ...formData, joinDate: new Date().toISOString().split('T')[0] }]);
      toast({ title: "User Created", description: "New user added successfully" });
    }
    setOpenEditDialog(false);
    setOpenAddDialog(false);
    setEditingUser(null);
  };

  const handleDeleteUser = (id: number) => {
    setUsers(users.filter(u => u.id !== id));
    setSelectedUsers(selectedUsers.filter(uid => uid !== id));
    toast({ title: "User Deleted", description: "User removed successfully" });
  };

  const handleBulkDelete = () => {
    setUsers(users.filter(u => !selectedUsers.includes(u.id)));
    setSelectedUsers([]);
    toast({ title: "Users Deleted", description: `${selectedUsers.length} users removed successfully` });
  };

  const handleBulkStatusChange = (status: string) => {
    setUsers(users.map(u => selectedUsers.includes(u.id) ? { ...u, status } : u));
    setSelectedUsers([]);
    toast({ title: "Status Updated", description: `${selectedUsers.length} users updated to ${status}` });
  };

  const handleExportUsers = () => {
    const csv = [
      ["Name", "Email", "Role", "Subscription", "Status", "Join Date"],
      ...users.map(u => [u.name, u.email, u.role, u.subscription, u.status, u.joinDate])
    ].map(row => row.join(",")).join("\n");
    
    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `users-${new Date().toISOString()}.csv`;
    a.click();
    
    toast({ title: "Export Successful", description: "Users exported to CSV file" });
  };

  const toggleSelectAll = () => {
    if (selectedUsers.length === filteredUsers.length) {
      setSelectedUsers([]);
    } else {
      setSelectedUsers(filteredUsers.map(u => u.id));
    }
  };

  const toggleSelectUser = (id: number) => {
    setSelectedUsers(prev => 
      prev.includes(id) ? prev.filter(uid => uid !== id) : [...prev, id]
    );
  };

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-heading font-bold">User Management</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage all users and professionals</p>
        </div>
        <Dialog open={openAddDialog} onOpenChange={setOpenAddDialog}>
          <DialogTrigger asChild>
            <Button className="gap-2 w-full sm:w-auto" onClick={() => setEditingUser(null)}>
              <UserPlus className="h-4 w-4" />
              Add User
            </Button>
          </DialogTrigger>
          <DialogContent>
            <UserForm user={editingUser} onSave={handleSaveUser} />
          </DialogContent>
        </Dialog>
      </div>

      <Card className="shadow-lg">
        <CardHeader>
          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search users..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button variant="outline" size="sm" onClick={handleExportUsers} className="gap-2">
                <Download className="h-4 w-4" />
                Export CSV
              </Button>
            </div>
            {selectedUsers.length > 0 && (
              <div className="flex flex-wrap gap-2 p-3 bg-muted/50 rounded-lg">
                <Badge variant="secondary">{selectedUsers.length} selected</Badge>
                <Button size="sm" variant="outline" onClick={() => handleBulkStatusChange("Active")} className="gap-1">
                  Activate
                </Button>
                <Button size="sm" variant="outline" onClick={() => handleBulkStatusChange("Inactive")} className="gap-1">
                  <Ban className="h-3 w-3" />
                  Deactivate
                </Button>
                <Button size="sm" variant="destructive" onClick={handleBulkDelete} className="gap-1">
                  <Trash className="h-3 w-3" />
                  Delete
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {/* Mobile Card View */}
          <div className="md:hidden space-y-4">
            {filteredUsers.map((user) => (
              <Card key={user.id}>
                <CardContent className="p-4 space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium">{user.name}</p>
                      <p className="text-sm text-muted-foreground">{user.email}</p>
                    </div>
                    <Badge variant={user.status === "Active" ? "default" : "destructive"} className="text-xs">
                      {user.status}
                    </Badge>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant={user.role === "Professional" ? "default" : "secondary"} className="text-xs">
                      {user.role}
                    </Badge>
                    <Badge
                      variant={
                        user.subscription === "Premium"
                          ? "default"
                          : user.subscription === "Basic"
                          ? "secondary"
                          : "outline"
                      }
                      className="text-xs"
                    >
                      {user.subscription}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">Joined: {user.joinDate}</p>
                  <div className="flex gap-2 pt-2">
                    <Dialog open={openEditDialog && editingUser?.id === user.id} onOpenChange={setOpenEditDialog}>
                      <DialogTrigger asChild>
                        <Button size="sm" variant="outline" className="flex-1" onClick={() => setEditingUser(user)}>
                          <Edit className="h-3 w-3 mr-1" /> Edit
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <UserForm user={user} onSave={handleSaveUser} />
                      </DialogContent>
                    </Dialog>
                    <Button size="sm" variant="outline" onClick={() => handleDeleteUser(user.id)}>
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Desktop Table View */}
          <div className="hidden md:block overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <Checkbox 
                      checked={selectedUsers.length === filteredUsers.length && filteredUsers.length > 0}
                      onCheckedChange={toggleSelectAll}
                    />
                  </TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Subscription</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Join Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <Checkbox 
                        checked={selectedUsers.includes(user.id)}
                        onCheckedChange={() => toggleSelectUser(user.id)}
                      />
                    </TableCell>
                    <TableCell className="font-medium">{user.name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Badge variant={user.role === "Professional" ? "default" : "secondary"}>
                        {user.role}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          user.subscription === "Premium"
                            ? "default"
                            : user.subscription === "Basic"
                            ? "secondary"
                            : "outline"
                        }
                      >
                        {user.subscription}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={user.status === "Active" ? "default" : "destructive"}>
                        {user.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{user.joinDate}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Dialog open={openEditDialog && editingUser?.id === user.id} onOpenChange={setOpenEditDialog}>
                          <DialogTrigger asChild>
                            <Button size="icon" variant="ghost" className="h-8 w-8" onClick={() => setEditingUser(user)}>
                              <Edit className="h-4 w-4" />
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <UserForm user={user} onSave={handleSaveUser} />
                          </DialogContent>
                        </Dialog>
                        <Button size="icon" variant="ghost" className="h-8 w-8" onClick={() => handleDeleteUser(user.id)}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const UserForm = ({ user, onSave }: { user: any; onSave: (data: any) => void }) => {
  const [formData, setFormData] = useState(user || {
    name: "",
    email: "",
    role: "sub_admin",
    subscription: "Free",
    status: "Active"
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <DialogHeader>
        <DialogTitle>{user ? "Edit User" : "Add User"}</DialogTitle>
        <DialogDescription>
          {user ? "Update user details and subscription" : "Create a new user account"}
        </DialogDescription>
      </DialogHeader>
      <div className="space-y-4 py-4">
        <div className="space-y-2">
          <Label htmlFor="name">Full Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="role">Role</Label>
          <Select value={formData.role} onValueChange={(value) => setFormData({ ...formData, role: value })}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="super_admin">Super Admin</SelectItem>
              <SelectItem value="sub_admin">Sub Admin</SelectItem>
              <SelectItem value="market_admin">Market Admin</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="subscription">Subscription Plan</Label>
          <Select value={formData.subscription} onValueChange={(value) => setFormData({ ...formData, subscription: value })}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Free">Free</SelectItem>
              <SelectItem value="Basic">Basic</SelectItem>
              <SelectItem value="Premium">Premium</SelectItem>
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
              <SelectItem value="Active">Active</SelectItem>
              <SelectItem value="Inactive">Inactive</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <DialogFooter>
        <Button type="submit">{user ? "Update" : "Create"} User</Button>
      </DialogFooter>
    </form>
  );
};

export default Users;
