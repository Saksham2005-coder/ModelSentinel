import { Moon, Sun, Monitor } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { Button } from './Button';
import { useState, useRef, useEffect } from 'react';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="w-9 h-9 p-0 flex items-center justify-center text-text-secondary hover:text-text-primary"
        aria-label="Toggle theme"
        title="Toggle theme"
      >
        {theme === 'dark' && <Moon className="h-4 w-4" />}
        {theme === 'light' && <Sun className="h-4 w-4" />}
        {theme === 'system' && <Monitor className="h-4 w-4" />}
      </Button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-36 rounded-md shadow-lg bg-background-elevated border border-border py-1 z-50">
          <button
            className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 hover:bg-surface ${theme === 'light' ? 'text-brand bg-brand-soft' : 'text-text-primary'}`}
            onClick={() => { setTheme('light'); setIsOpen(false); }}
          >
            <Sun className="h-4 w-4" /> Light
          </button>
          <button
            className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 hover:bg-surface ${theme === 'dark' ? 'text-brand bg-brand-soft' : 'text-text-primary'}`}
            onClick={() => { setTheme('dark'); setIsOpen(false); }}
          >
            <Moon className="h-4 w-4" /> Dark
          </button>
          <button
            className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 hover:bg-surface ${theme === 'system' ? 'text-brand bg-brand-soft' : 'text-text-primary'}`}
            onClick={() => { setTheme('system'); setIsOpen(false); }}
          >
            <Monitor className="h-4 w-4" /> System
          </button>
        </div>
      )}
    </div>
  );
}
