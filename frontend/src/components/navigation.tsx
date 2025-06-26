import { useLocation } from "wouter";
import { ShoppingCart } from "@/lib/icons";
import { lazy, Suspense, useEffect, useState } from "react";

const MusicPlayer = lazy(() => import("@/components/music-player"));

// SSR-safe mobile detection
function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);
  return isMobile;
}

export default function Navigation() {
  const [location, setLocation] = useLocation();
  const isMobile = useIsMobile();

  const getStepStatus = (step: number) => {
    const stepPaths = ['/', '/user-info', '/shopping'];
    const currentStepIndex = stepPaths.findIndex(path => 
      location === path || (path === '/shopping' && location.startsWith('/shopping'))
    );
    if (currentStepIndex === -1) return 'bg-gray-300 dark:bg-gray-600';
    return step <= currentStepIndex + 1 ? 'bg-primary' : 'bg-gray-300 dark:bg-gray-600';
  };

  return (
    <nav className="bg-white dark:bg-card shadow-sm border-b border-gray-200 dark:border-border sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div className="flex items-center h-16 relative">
          {/* Left: Logo */}
          <div className="flex items-center space-x-4 min-w-0">
            <button
              className="flex items-center focus:outline-none group"
              onClick={() => setLocation("/")}
              aria-label="Go to landing page"
              type="button"
            >
              <img 
                src="/Icon.svg" 
                alt="Eventually Yours" 
                className="mr-3 h-8 w-8 group-hover:scale-110 transition-transform"
                loading="lazy"
                width="32"
                height="32"
              />
              <span className={`font-display text-gray-900 dark:text-foreground whitespace-nowrap ${
                isMobile ? 'text-sm' : 'text-xl'
              }`}>
                {isMobile ? 'Eventually Yours' : 'Eventually Yours Shopping App'}
              </span>
            </button>
          </div>

          {/* Center: Music Player (desktop only) */}
          {!isMobile && (
            <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <Suspense fallback={<div>Loading music player...</div>}>
                <MusicPlayer />
              </Suspense>
            </div>
          )}

          {/* Right: Music Player (mobile) and Progress dots + barrel roll message (desktop) */}
          <div className="flex items-center space-x-4 ml-auto">
            {/* Music Player on mobile */}
            {isMobile && (
              <Suspense fallback={<div>Loading...</div>}>
                <MusicPlayer />
              </Suspense>
            )}
            
            {/* Progress dots and barrel roll message (desktop only) */}
            {!isMobile && (
              <>
                <div className="flex space-x-2">
                  <div className={`w-2 h-2 rounded-full ${getStepStatus(1)}`}></div>
                  <div className={`w-2 h-2 rounded-full ${getStepStatus(2)}`}></div>
                  <div className={`w-2 h-2 rounded-full ${getStepStatus(3)}`}></div>
                </div>
                <span className="ml-6 text-xs font-mono text-gray-500 dark:text-gray-400 opacity-80 select-none">
                  Press <span className="font-bold text-primary">R</span> twice for barrel roll
                </span>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
