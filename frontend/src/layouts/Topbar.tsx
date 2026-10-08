import { useState } from 'react';
import { Bell, User, LogOut, Menu } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/AuthContext';
import { GlobalSearch } from '@/components/ui/GlobalSearch';
import { ThemeToggle } from '@/components/ui/ThemeToggle';

export function Topbar({ onMenuClick }: { onMenuClick?: () => void }) {
  const { user, logout } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    await logout();
    // No need to set isLoggingOut to false, we redirect
  };

  return (
    <header className="flex items-center justify-between h-16 px-4 md:px-6 border-b border-border bg-background-base/50 backdrop-blur-md sticky top-0 z-40">
      <div className="flex items-center gap-4 flex-1">
        {onMenuClick && (
          <Button variant="ghost" size="icon" className="md:hidden" onClick={onMenuClick}>
            <Menu className="h-5 w-5" />
          </Button>
        )}
        <div className="hidden md:block flex-1 max-w-lg">
          <GlobalSearch />
        </div>
      </div>
      <div className="flex items-center space-x-2 md:space-x-4">
        <div className="hidden lg:flex items-center text-sm text-text-secondary mr-2">
          <span className="w-2 h-2 rounded-full bg-status-success mr-2 animate-pulse"></span>
          Production
        </div>
        
        <ThemeToggle />

        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-status-danger border-2 border-background-base"></span>
        </Button>
        <div className="flex items-center space-x-2">
          <div className="flex flex-col text-right mr-2 hidden md:block">
            <span className="text-sm font-medium text-text-primary">{user?.full_name || user?.email}</span>
            {user?.role && <span className="text-xs text-text-muted">{user?.role}</span>}
          </div>
          <Button variant="ghost" size="icon" className="rounded-full bg-surface" title={user?.email}>
            <User className="h-5 w-5" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleLogout} disabled={isLoggingOut} className="ml-2">
            <LogOut className="h-4 w-4 mr-2" />
            {isLoggingOut ? 'Logging out...' : 'Logout'}
          </Button>
        </div>
      </div>
    </header>
  );
}
