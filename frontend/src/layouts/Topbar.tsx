import { useState } from 'react';
import { Search, Bell, User, LogOut } from 'lucide-react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/AuthContext';

export function Topbar() {
  const { user, logout } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    await logout();
    // No need to set isLoggingOut to false, we redirect
  };

  return (
    <header className="flex items-center justify-between h-16 px-6 border-b border-border bg-background-base">
      <div className="flex-1 max-w-lg">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-text-muted" />
          <Input 
            type="search" 
            placeholder="Search models, incidents, or PRs..." 
            className="pl-9 bg-surface border-border-strong w-full"
          />
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <div className="flex items-center text-sm text-text-secondary mr-4">
          <span className="w-2 h-2 rounded-full bg-status-success mr-2"></span>
          Production Env
        </div>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-status-danger border-2 border-background-base"></span>
        </Button>
        <div className="flex items-center space-x-2">
          <div className="flex flex-col text-right mr-2 hidden md:block">
            <span className="text-sm font-medium text-text-primary">{user?.full_name}</span>
            <span className="text-xs text-text-muted">{user?.role}</span>
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
