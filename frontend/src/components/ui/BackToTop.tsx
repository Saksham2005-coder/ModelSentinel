import { useState, useEffect } from 'react';
import { ArrowUp } from 'lucide-react';
import { Button } from './Button';

export function BackToTop() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const mainContent = document.getElementById('main-content');
    
    const toggleVisibility = () => {
      // If we're scrolling the main content area
      if (mainContent) {
        if (mainContent.scrollTop > 300) {
          setIsVisible(true);
        } else {
          setIsVisible(false);
        }
      } else {
        // Fallback to window scrolling
        if (window.scrollY > 300) {
          setIsVisible(true);
        } else {
          setIsVisible(false);
        }
      }
    };

    if (mainContent) {
      mainContent.addEventListener('scroll', toggleVisibility);
      return () => mainContent.removeEventListener('scroll', toggleVisibility);
    } else {
      window.addEventListener('scroll', toggleVisibility);
      return () => window.removeEventListener('scroll', toggleVisibility);
    }
  }, []);

  const scrollToTop = () => {
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      mainContent.scrollTo({
        top: 0,
        behavior: 'smooth',
      });
    } else {
      window.scrollTo({
        top: 0,
        behavior: 'smooth',
      });
    }
  };

  if (!isVisible) return null;

  return (
    <Button
      variant="outline"
      size="icon"
      className="fixed bottom-6 right-6 z-40 rounded-full shadow-lg bg-surface/80 backdrop-blur-sm border-border-strong text-text-primary hover:bg-surface-hover transition-all print:hidden"
      onClick={scrollToTop}
      aria-label="Back to top"
    >
      <ArrowUp className="h-5 w-5" />
    </Button>
  );
}
