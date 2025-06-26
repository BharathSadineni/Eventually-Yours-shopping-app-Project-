import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { UserProvider } from "./context/UserContext";

// Barrel roll effect on double 'r' key press (not Ctrl+R)
let lastRPress = 0;
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', (e) => {
    if (e.key.toLowerCase() === 'r' && !e.ctrlKey && !e.metaKey && !e.altKey && !e.repeat) {
      const now = Date.now();
      if (now - lastRPress < 400) {
        const root = document.getElementById('root');
        if (root && !root.classList.contains('barrel-roll')) {
          root.classList.add('barrel-roll');
          setTimeout(() => root.classList.remove('barrel-roll'), 1000);
        }
        lastRPress = 0;
      } else {
        lastRPress = now;
      }
    }
  });
}

// Register service worker for caching
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
      })
      .catch((registrationError) => {
      });
  });
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <UserProvider>
    <App />
  </UserProvider>
);
