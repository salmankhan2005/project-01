import { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { BottomNav } from '@/components/layout/BottomNav';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CreditCard, Calendar, Download, Crown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

const billingHistory = [
  { id: 1, date: '2024-01-15', amount: '$9.99', plan: 'Premium Monthly', status: 'Paid' },
  { id: 2, date: '2023-12-15', amount: '$9.99', plan: 'Premium Monthly', status: 'Paid' },
  { id: 3, date: '2023-11-15', amount: '$9.99', plan: 'Premium Monthly', status: 'Paid' }
];

export const Billing = () => {
  const navigate = useNavigate();
  const { isSubscribed } = useAuth();
  const [currentPlan] = useState('Premium Monthly');

  return (
    <div className="min-h-screen bg-background pb-20">
      <Header 
        title="Billing & Subscription" 
        showBackButton={true}
        onBackClick={() => navigate(-1)}
      />
      
      <main className="container-responsive py-6 space-y-6">
        {/* Current Subscription */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Current Plan</h2>
            <Badge variant={isSubscribed ? 'default' : 'secondary'}>
              {isSubscribed ? 'Active' : 'Free'}
            </Badge>
          </div>
          <div className="flex items-center gap-3 mb-4">
            <Crown className="w-6 h-6 text-yellow-500" />
            <div>
              <p className="font-medium">{isSubscribed ? currentPlan : 'Free Plan'}</p>
              <p className="text-sm text-muted-foreground">
                {isSubscribed ? '$9.99/month' : 'Limited features'}
              </p>
            </div>
          </div>
          {isSubscribed && (
            <p className="text-sm text-muted-foreground mb-4">
              Next billing date: February 15, 2024
            </p>
          )}
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              {isSubscribed ? 'Change Plan' : 'Upgrade to Premium'}
            </Button>
            {isSubscribed && (
              <Button variant="outline" size="sm">Cancel Subscription</Button>
            )}
          </div>
        </Card>

        {/* Payment Method */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Payment Method</h2>
          <div className="flex items-center gap-3 mb-4">
            <CreditCard className="w-6 h-6 text-muted-foreground" />
            <div>
              <p className="font-medium">•••• •••• •••• 4242</p>
              <p className="text-sm text-muted-foreground">Expires 12/25</p>
            </div>
          </div>
          <Button variant="outline" size="sm">Update Payment Method</Button>
        </Card>

        {/* Billing History */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Billing History</h2>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
          <div className="space-y-3">
            {billingHistory.map((bill) => (
              <div key={bill.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <Calendar className="w-4 h-4 text-muted-foreground" />
                  <div>
                    <p className="font-medium">{bill.plan}</p>
                    <p className="text-sm text-muted-foreground">{bill.date}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium">{bill.amount}</p>
                  <Badge variant="secondary" className="text-xs">
                    {bill.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </main>

      <BottomNav />
    </div>
  );
};