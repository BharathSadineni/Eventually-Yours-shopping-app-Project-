import { useState, useEffect, createContext, useContext } from "react";
import { Switch, Route, useLocation } from "wouter";
import { queryClient } from "@/lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/components/theme-provider";
import { DarkModeToggle } from "@/components/dark-mode-toggle";
import Landing from "@/pages/landing";
import UserInfo from "@/pages/user-info";
import Shopping from "@/pages/shopping";
import Navigation from "@/components/navigation";
import Footer from "@/components/footer";

// Navigation context for transition
const NavigationTransitionContext = createContext({
  navigate: (to: string) => {},
});

export function useNavigateWithTransition() {
  return useContext(NavigationTransitionContext).navigate;
}

function Router() {
  return (
    <div className="min-h-screen bg-background dark:bg-background">
      <DarkModeToggle />
      <Navigation />
      <Switch>
        <Route path="/" component={Landing} />
        <Route path="/user-info" component={UserInfo} />
        <Route path="/shopping" component={Shopping} />
        <Route>
          <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-foreground dark:text-foreground mb-4">Page Not Found</h1>
              <p className="text-muted-foreground dark:text-muted-foreground">The page you're looking for doesn't exist.</p>
            </div>
          </div>
        </Route>
      </Switch>
      <Footer />
    </div>
  );
}

function App() {
  const [location] = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  }, [location]);
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
