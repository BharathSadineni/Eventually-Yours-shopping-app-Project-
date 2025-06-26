import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause } from '@/lib/icons';

interface MusicPlayerProps {
  className?: string;
}

// Helper to detect mobile (screen width < 768px)
const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;

export default function MusicPlayer({ className = "" }: MusicPlayerProps) {
  if (isMobile) return null;

  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className={`flex items-center justify-center ${className}`} style={{ minWidth: 0 }}>
      <div className="bg-white dark:bg-gray-800 rounded-full shadow border border-gray-200 dark:border-gray-700 px-2 py-1 flex items-center space-x-2" style={{ height: 40, minWidth: 0 }}>
        {/* App Icon */}
        <img src="/Icon.svg" alt="App Icon" className="w-6 h-6 rounded mr-1" style={{ minWidth: 24, minHeight: 24 }} loading="lazy" width="24" height="24" />
        {/* Play/Pause Button */}
        <button
          onClick={togglePlayPause}
          className="w-8 h-8 bg-primary hover:bg-primary/90 rounded-full flex items-center justify-center transition-colors duration-200"
          style={{ minWidth: 32, minHeight: 32 }}
          aria-label={isPlaying ? "Pause music" : "Play music"}
        >
          {isPlaying ? (
            <Pause className="w-4 h-4 text-white" />
          ) : (
            <Play className="w-4 h-4 text-white ml-0.5" />
          )}
        </button>
        {/* Song Title */}
        <div className="flex flex-col min-w-0">
          <span className="font-heading text-xs font-bold text-gray-900 dark:text-white truncate" style={{ lineHeight: 1.1 }}>
            EVENTUALLY
          </span>
          <span className="font-body text-[10px] text-gray-600 dark:text-gray-400 truncate" style={{ lineHeight: 1 }}>
            by Tame Impala
          </span>
        </div>
      </div>
      {/* Hidden Audio Element */}
      <audio
        ref={audioRef}
        src="/eventually.mp3"
        loop
        onEnded={() => setIsPlaying(false)}
        onPause={() => setIsPlaying(false)}
        onPlay={() => setIsPlaying(true)}
      />
    </div>
  );
} 