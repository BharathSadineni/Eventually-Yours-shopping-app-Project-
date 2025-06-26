import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import TypewriterText, { TypewriterProvider } from "@/components/typewriter-text";
import MusicPlayer from "@/components/music-player";
import { useUser } from "@/context/UserContext";
import { createSessionId, setupSessionCleanup } from "@/lib/utils";
import { apiRequest } from "@/lib/queryClient";
import { 
  ShoppingCart, 
  Brain, 
  Rocket, 
  Zap,
  Shield,
  Gauge,
  User,
  DollarSign,
  FileText,
  Linkedin,
  Github,
  Globe,
  Clock,
  CheckCircle,
  Target
} from "lucide-react";

const actionTexts = [
  'Kick Off',
  'Get Started',
  'Begin Journey',
  'Start Shopping',
  'Launch Assistant'
];

const animatedTexts = [
  "Experience",
  "Discover", 
  "Explore",
  "Transform"
];

const buttonTexts = [
  "Get Started",
  "Start Shopping",
  "Begin Journey",
  "Launch App"
];

const features = [
  {
    icon: <Brain className="h-8 w-8 text-primary" />,
    title: "Smart AI Engine",
    description: "Advanced AI that learns your style and predicts what you'll love, making every recommendation feel personal and intentional."
  },
  {
    icon: <Target className="h-8 w-8 text-primary" />,
    title: "Tailored Recommendations Engine",
    description: "Precision-targeted suggestions that match your exact taste. Our AI fine-tunes every pick to align with what truly matters to you."
  },
  {
    icon: <Zap className="h-8 w-8 text-primary" />,
    title: "Instant Results",
    description: "Lightning-fast analysis and instant recommendations — no waiting, no delays, just seamless discovery of your next favorite items."
  }
];

export default function Landing() {
  const [, setLocation] = useLocation();
  const [actionIndex, setActionIndex] = useState(0);
  const { sessionId, setSessionId } = useUser();

  useEffect(() => {
    if (!sessionId) {
      const newSessionId = createSessionId();
      setSessionId(newSessionId);
      apiRequest('POST', '/api/init-session', { session_id: newSessionId })
        .then(response => {
          return response.json();
        }).then(data => {
        }).catch(error => {
        });
    }
    const cleanup = setupSessionCleanup();
    return cleanup;
  }, [sessionId, setSessionId]);

  useEffect(() => {
    const interval = setInterval(() => {
      setActionIndex(prev => (prev + 1) % actionTexts.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleGetStarted = () => {
    setLocation('/user-info');
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-gold py-20 dark:bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="animate-fade-in">
              <TypewriterProvider>
                <h1 className="text-5xl font-heading text-gray-900 dark:text-foreground mb-2 leading-tight">
                  Eventually Yours (shopping app)
                </h1>
                <div className="text-4xl font-bold text-primary mb-6">
                <TypewriterText 
                    texts={animatedTexts}
                  className="text-primary"
                />
                </div>
                <p className="text-xl text-gray-600 dark:text-muted-foreground mb-8 leading-relaxed font-body">
                  Discover products that will eventually be yours.<br/>
                  Get AI-powered recommendations tailored to your unique style and preferences.
              </p>
                <div className="mb-8">
                  <button
                    onClick={() => setLocation("/user-info")}
                    className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-4 px-8 rounded-lg text-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                  >
                    <TypewriterText 
                      texts={buttonTexts}
                      className="text-primary-foreground"
                    />
                  </button>
                </div>
              </TypewriterProvider>
                <div className="flex items-center space-x-6 text-sm text-gray-500 dark:text-muted-foreground">
                  <span className="flex items-center">
                  <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                  Smart AI Engine
                </span>
                <span className="flex items-center">
                  <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                  Tailored Recommendations
                  </span>
                  <span className="flex items-center">
                  <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                  Instant Results
                  </span>
              </div>
            </div>
            <div className="animate-slide-up">
              {/* Professional dashboard preview mockup */}
              <div className="bg-white dark:bg-card rounded-xl shadow-2xl p-6 border border-gray-100 dark:border-border">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex space-x-2">
                    <div className="w-3 h-3 rounded-full bg-red-400"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                    <div className="w-3 h-3 rounded-full bg-green-400"></div>
                  </div>
                  <span className="text-xs text-gray-500 dark:text-muted-foreground">
                    Eventually Yours Dashboard
                  </span>
                </div>
                <div className="space-y-3">
                  <div className="h-4 bg-gradient-to-r from-primary/20 to-primary/10 rounded"></div>
                  <div className="h-3 bg-gray-200 dark:bg-muted rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 dark:bg-muted rounded w-1/2"></div>
                  <div className="grid grid-cols-2 gap-3 mt-4">
                    <div className="h-20 bg-gradient-to-br from-primary/20 to-primary/10 rounded-lg"></div>
                    <div className="h-20 bg-gradient-to-br from-primary/30 to-primary/20 rounded-lg"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose Section */}
      <section className="py-20 bg-white dark:bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-heading text-gray-900 dark:text-foreground mb-4">Why Choose Eventually Yours?</h2>
            <p className="text-xl text-gray-600 dark:text-muted-foreground font-body">
              Professional-grade features for the modern shopper.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="feature-card bg-white dark:bg-card p-8 rounded-xl shadow-lg border border-gray-100 dark:border-border">
              <div className="w-12 h-12 bg-primary/10 dark:bg-primary/20 rounded-lg flex items-center justify-center mb-6">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-foreground mb-4">{feature.title}</h3>
                <p className="text-gray-600 dark:text-muted-foreground leading-relaxed font-body">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="pt-4 pb-16 bg-background dark:bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-heading text-gray-900 dark:text-foreground mb-4">Eventually Yours Features</h2>
          </div>
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div className="flex flex-col items-center">
              <Rocket className="text-primary h-8 w-8 mb-3" />
              <span className="font-semibold">AI-Powered Recommendations</span>
            </div>
            <div className="flex flex-col items-center">
              <User className="text-primary h-8 w-8 mb-3" />
              <span className="font-semibold">Personal Preference Tracking</span>
              </div>
            <div className="flex flex-col items-center">
              <DollarSign className="text-primary h-8 w-8 mb-3" />
              <span className="font-semibold">Budget-Smart Shopping</span>
            </div>
            <div className="flex flex-col items-center">
              <FileText className="text-primary h-8 w-8 mb-3" />
              <span className="font-semibold">Data Export & Import</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
