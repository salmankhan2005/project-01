import { Header } from '@/components/layout/Header';
import { BottomNav } from '@/components/layout/BottomNav';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { User, Camera } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { apiService, Profile as ProfileType } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';

export const Profile = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [profile, setProfile] = useState<ProfileType>({
    name: '',
    phone: '',
    bio: '',
    dietary_preferences: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const profileData = await apiService.getProfile();
        setProfile(profileData);
      } catch (error) {
        console.error('Failed to load profile:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      loadProfile();
    }
  }, [user]);
  
  const handleSave = async () => {
    try {
      await apiService.updateProfile(profile);
      toast.success('Profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  const handleInputChange = (field: keyof ProfileType, value: string) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return <div className="min-h-screen bg-background flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-background pb-20 sm:pb-24">
      <Header 
        title="Profile" 
        showProfile={false}
        showBackButton={true}
        onBackClick={() => navigate(-1)}
      />
      
      <main className="px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 md:py-8 max-w-4xl mx-auto">
        {/* Profile Picture */}
        <div className="flex justify-center mb-8">
          <div className="relative">
            <div className="w-24 h-24 bg-primary/20 rounded-full flex items-center justify-center">
              <User className="w-12 h-12 text-primary" />
            </div>
            <Button
              size="icon"
              className="absolute bottom-0 right-0 rounded-full h-8 w-8"
            >
              <Camera className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Profile Form */}
        <Card className="p-6 mb-6">
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Full Name</Label>
              <Input 
                id="name" 
                value={profile.name} 
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="mt-1.5" 
              />
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email" 
                type="email" 
                value={user?.email || ''} 
                disabled 
                className="mt-1.5 bg-muted" 
              />
            </div>

            <div>
              <Label htmlFor="phone">Phone Number</Label>
              <Input 
                id="phone" 
                type="tel" 
                value={profile.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                placeholder="+1 (555) 000-0000" 
                className="mt-1.5" 
              />
            </div>

            <div>
              <Label htmlFor="bio">Bio</Label>
              <Input 
                id="bio" 
                value={profile.bio}
                onChange={(e) => handleInputChange('bio', e.target.value)}
                placeholder="Tell us about yourself..." 
                className="mt-1.5" 
              />
            </div>
          </div>
        </Card>

        {/* Dietary Preferences */}
        <Card className="p-6 mb-6">
          <h3 className="font-heading font-semibold mb-4">Dietary Preferences</h3>
          <div className="flex flex-wrap gap-2">
            {['Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 'Keto'].map((pref) => (
              <Button key={pref} variant="outline" size="sm" className="rounded-full">
                {pref}
              </Button>
            ))}
          </div>
        </Card>

        <Button onClick={handleSave} className="w-full h-12">
          Save Changes
        </Button>
      </main>

      <BottomNav />
    </div>
  );
};
