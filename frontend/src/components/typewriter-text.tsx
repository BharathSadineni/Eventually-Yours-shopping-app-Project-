import { useState, useEffect, createContext, useContext } from "react";

interface TypewriterContextType {
  currentTextIndex: number;
  isDeleting: boolean;
  setIsDeleting: (deleting: boolean) => void;
  setCurrentTextIndex: (index: number | ((prev: number) => number)) => void;
}

const TypewriterContext = createContext<TypewriterContextType | null>(null);

export function TypewriterProvider({ children }: { children: React.ReactNode }) {
  const [currentTextIndex, setCurrentTextIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  return (
    <TypewriterContext.Provider value={{
      currentTextIndex,
      isDeleting,
      setIsDeleting,
      setCurrentTextIndex,
    }}>
      {children}
    </TypewriterContext.Provider>
  );
}

interface TypewriterTextProps {
  texts: string[];
  className?: string;
  speed?: number;
  pauseDuration?: number;
  syncId?: string;
}

export default function TypewriterText({ 
  texts, 
  className = "", 
  speed = 120, 
  pauseDuration = 2000,
  syncId,
}: TypewriterTextProps) {
  const context = useContext(TypewriterContext);
  
  // Each component maintains its own text state
  const [currentText, setCurrentText] = useState("");
  
  // If no context (standalone mode), use local state
  const [localCurrentTextIndex, setLocalCurrentTextIndex] = useState(0);
  const [localIsDeleting, setLocalIsDeleting] = useState(false);

  const currentTextIndex = context ? context.currentTextIndex : localCurrentTextIndex;
  const isDeleting = context ? context.isDeleting : localIsDeleting;
  const setIsDeleting = context ? context.setIsDeleting : setLocalIsDeleting;
  const setCurrentTextIndex = context ? context.setCurrentTextIndex : setLocalCurrentTextIndex;

  const fullText = texts[currentTextIndex] || "";

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (!fullText) return;
      
      if (isDeleting) {
        setCurrentText(fullText.substring(0, currentText.length - 1));
        
        if (currentText === "") {
          setIsDeleting(false);
          setCurrentTextIndex((prev: number) => (prev + 1) % texts.length);
        }
      } else {
        setCurrentText(fullText.substring(0, currentText.length + 1));
        
        if (currentText === fullText) {
          setTimeout(() => setIsDeleting(true), pauseDuration);
        }
      }
    }, isDeleting ? speed / 2 : speed);

    return () => clearTimeout(timeout);
  }, [currentText, isDeleting, currentTextIndex, texts, speed, pauseDuration, setIsDeleting, setCurrentTextIndex, fullText]);

  return (
    <span className={`strong-typewriter-text ${className}`}>
      {currentText}
      <span className="animate-pulse">|</span>
    </span>
  );
}
