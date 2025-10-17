import { Bell, User, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useDeviceType } from '@/hooks/use-mobile';

interface HeaderProps {
  title: string;
  showNotifications?: boolean;
  showProfile?: boolean;
  showBackButton?: boolean;
  onBackClick?: () => void;
}

export const Header = ({ title, showNotifications = true, showProfile = true, showBackButton = false, onBackClick }: HeaderProps) => {
  const { isMobile, isTablet } = useDeviceType();
  
  return (
    <header className="sticky top-0 z-40 bg-background/80 backdrop-blur-lg border-b border-border safe-area-top">
      <div className="container-responsive flex items-center justify-between h-12 xs:h-14 sm:h-16 lg:h-18">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
          {showBackButton && (
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={onBackClick}
              className="h-8 w-8 xs:h-9 xs:w-9 sm:h-10 sm:w-10 shrink-0 touch-manipulation"
            >
              <ArrowLeft className="w-4 h-4 xs:w-5 xs:h-5 sm:w-6 sm:h-6" />
            </Button>
          )}
          <h1 className="heading-sm lg:heading-lg text-foreground truncate">
            {title}
          </h1>
        </div>
        
        <div className="flex items-center gap-1 xs:gap-2 sm:gap-3 shrink-0">
          {showNotifications && (
            <Link to="/notifications">
              <Button 
                variant="ghost" 
                size="icon" 
                className="relative h-8 w-8 xs:h-9 xs:w-9 sm:h-10 sm:w-10 lg:h-11 lg:w-11 touch-manipulation"
              >
                <Bell className="w-4 h-4 xs:w-5 xs:h-5 sm:w-5 sm:h-5 lg:w-6 lg:h-6" />
                <span className="absolute top-1 right-1 xs:top-1.5 xs:right-1.5 w-2 h-2 xs:w-2.5 xs:h-2.5 bg-secondary rounded-full" />
              </Button>
            </Link>
          )}
          
          {showProfile && (
            <Link to="/profile">
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-8 w-8 xs:h-9 xs:w-9 sm:h-10 sm:w-10 lg:h-11 lg:w-11 touch-manipulation"
              >
                <User className="w-4 h-4 xs:w-5 xs:h-5 sm:w-5 sm:h-5 lg:w-6 lg:h-6" />
              </Button>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};
