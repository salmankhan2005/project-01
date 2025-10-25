import React from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { SavedRecipesProvider } from "@/contexts/SavedRecipesContext";
import { ReviewsProvider } from "@/contexts/ReviewsContext";
import { NotificationProvider } from "@/contexts/NotificationContext";
import { RecipeProvider } from "@/contexts/RecipeContext";
import { MealPlanProvider } from "@/contexts/MealPlanContext";
import { UserDataProvider } from "@/contexts/UserDataContext";
import { TourProvider } from "@/contexts/TourContext";
import { ThemeProvider } from "next-themes";
import { StatusBar, Style } from '@capacitor/status-bar';
import { Capacitor } from '@capacitor/core';
import { App as CapacitorApp } from '@capacitor/app';

// Pages
import { Splash } from "./pages/Splash";
import { Onboarding } from "./pages/Onboarding";
import { Auth } from "./pages/Auth";
import { Home } from "./pages/Home";
import { Recipes } from "./pages/Recipes";
import { Discover } from "./pages/Discover";
import { RecipeDetail } from "./pages/RecipeDetail";
import { RecipeBuilder } from "./pages/RecipeBuilder";
import { Shopping } from "./pages/Shopping";
import { More } from "./pages/More";
import { Profile } from "./pages/Profile";
import { Settings } from "./pages/Settings";
import { Premium } from "./pages/Premium";
import { Notifications } from "./pages/Notifications";
import { Help } from "./pages/Help";
import { MealSharing } from "./pages/MealSharing";
import { ClientView } from "./pages/ClientView";
import { Billing } from "./pages/Billing";
import { Analytics } from "./pages/Analytics";
import { Support } from "./pages/Support";
import { EmailSettings } from "./pages/EmailSettings";
import { AdminNotifications } from "./pages/AdminNotifications";
import MealPlanTemplates from "./pages/MealPlanTemplates";

import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

// Protected route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isGuest, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (!isAuthenticated && !isGuest) {
    return <Navigate to="/auth" replace />;
  }
  
  return <>{children}</>;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Splash />} />
      <Route path="/onboarding" element={<Onboarding />} />
      <Route path="/auth" element={<Auth />} />
      
      {/* Protected Routes */}
      <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
      <Route path="/recipes" element={<ProtectedRoute><Recipes /></ProtectedRoute>} />
      <Route path="/discover" element={<ProtectedRoute><Discover /></ProtectedRoute>} />
      <Route path="/recipe/:id" element={<ProtectedRoute><RecipeDetail /></ProtectedRoute>} />
      <Route path="/recipe-builder" element={<ProtectedRoute><RecipeBuilder /></ProtectedRoute>} />
      <Route path="/shopping" element={<ProtectedRoute><Shopping /></ProtectedRoute>} />
      <Route path="/more" element={<ProtectedRoute><More /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      <Route path="/premium" element={<ProtectedRoute><Premium /></ProtectedRoute>} />
      <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
      <Route path="/help" element={<ProtectedRoute><Help /></ProtectedRoute>} />
      <Route path="/support" element={<ProtectedRoute><Support /></ProtectedRoute>} />
      <Route path="/billing" element={<ProtectedRoute><Billing /></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
      <Route path="/email-settings" element={<ProtectedRoute><EmailSettings /></ProtectedRoute>} />
      <Route path="/admin-notifications" element={<ProtectedRoute><AdminNotifications /></ProtectedRoute>} />
      <Route path="/meal-sharing" element={<ProtectedRoute><MealSharing /></ProtectedRoute>} />
      <Route path="/client-view" element={<ProtectedRoute><ClientView /></ProtectedRoute>} />
      <Route path="/meal-plan-templates" element={<ProtectedRoute><MealPlanTemplates /></ProtectedRoute>} />

      
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

const App = () => {
  // Set viewport meta tag for proper mobile rendering and handle back button
  React.useEffect(() => {
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {
      viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes, viewport-fit=cover');
    } else {
      const meta = document.createElement('meta');
      meta.name = 'viewport';
      meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes, viewport-fit=cover';
      document.head.appendChild(meta);
    }

    // Configure status bar and back button for Capacitor
    if (Capacitor.isNativePlatform()) {
      StatusBar.setStyle({ style: Style.Dark });
      StatusBar.setBackgroundColor({ color: '#000000' });
      StatusBar.setOverlaysWebView({ overlay: false });
      
      // Handle hardware back button
      const handleBackButton = () => {
        const currentPath = window.location.pathname;
        
        // Define routes where back button should navigate within app
        const navigableRoutes = [
          '/recipe/', '/recipe-builder', '/profile', '/settings', 
          '/notifications', '/help', '/support', '/premium',
          '/billing', '/analytics', '/meal-sharing', '/client-view'
        ];
        
        const isNavigableRoute = navigableRoutes.some(route => 
          currentPath.includes(route)
        );
        
        if (isNavigableRoute) {
          // Navigate back within the app
          window.history.back();
        } else if (currentPath === '/home' || currentPath === '/recipes' || 
                   currentPath === '/discover' || currentPath === '/shopping' || 
                   currentPath === '/more') {
          // On main tabs, minimize app instead of closing
          CapacitorApp.minimizeApp();
        } else {
          // Default navigation back
          window.history.back();
        }
      };
      
      // Listen for back button
      CapacitorApp.addListener('backButton', handleBackButton);
      
      return () => {
        CapacitorApp.removeAllListeners();
      };
    }
  }, []);

  // Notification system for 2-hour inactivity
  React.useEffect(() => {
    let notificationTimeout: NodeJS.Timeout;
    let lastActivity = Date.now();

    const scheduleNotification = () => {
      clearTimeout(notificationTimeout);
      notificationTimeout = setTimeout(() => {
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification('Meal Plan Reminder', {
            body: "Don't forget to plan your meals for next week!",
            icon: '/favicon.ico',
            badge: '/favicon.ico'
          });
        }
      }, 2 * 60 * 60 * 1000); // 2 hours
    };

    const resetTimer = () => {
      lastActivity = Date.now();
      scheduleNotification();
    };

    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }

    // Track user activity
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    events.forEach(event => {
      document.addEventListener(event, resetTimer, true);
    });

    // Initial schedule
    scheduleNotification();

    return () => {
      clearTimeout(notificationTimeout);
      events.forEach(event => {
        document.removeEventListener(event, resetTimer, true);
      });
    };
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider 
        attribute="class" 
        defaultTheme="light" 
        storageKey="meal-planner-theme"
        enableSystem={false}
        themes={[
          'light', 
          'dark', 
          'comic', 
          'comic-dark', 
          'clean-minimalist', 
          'clean-minimalist-dark',
          'cozy-rustic',
          'cozy-rustic-dark',
          'vibrant-healthy',
          'vibrant-healthy-dark',
          'gourmet-elegant',
          'gourmet-elegant-dark',
          'playful-fun',
          'playful-fun-dark',
          'morning-dew'
        ]}
      >
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <AuthProvider>
              <TourProvider>
                <UserDataProvider>
                  <RecipeProvider>
                    <SavedRecipesProvider>
                      <ReviewsProvider>
                        <NotificationProvider>
                          <MealPlanProvider>
                          <div className="min-h-screen bg-background text-foreground antialiased">
                            <div className="animate-fade-in">
                              <AppRoutes />
                            </div>
                          </div>
                          </MealPlanProvider>
                        </NotificationProvider>
                      </ReviewsProvider>
                    </SavedRecipesProvider>
                  </RecipeProvider>
                </UserDataProvider>
              </TourProvider>
            </AuthProvider>
          </BrowserRouter>
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
