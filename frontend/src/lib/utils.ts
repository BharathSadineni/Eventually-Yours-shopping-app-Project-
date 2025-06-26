import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combines class names and merges Tailwind classes intelligently.
 * @param inputs - class values
 * @returns merged class string
 */
export function cn(...inputs: any[]) {
  return twMerge(clsx(inputs));
}

/**
 * Generates a random session ID (UUID v4-like)
 */
export function createSessionId(): string {
  // Simple UUID v4 generator
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Sets up a cleanup function for session (removes sessionId from localStorage on unload)
 * Returns a cleanup function to remove the event listener.
 */
export function setupSessionCleanup() {
  const cleanup = () => {
    // Optionally, remove sessionId or perform other cleanup
    // localStorage.removeItem('sessionId');
  };
  window.addEventListener('beforeunload', cleanup);
  return () => window.removeEventListener('beforeunload', cleanup);
} 