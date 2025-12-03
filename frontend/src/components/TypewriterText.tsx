import { useState, useEffect, useRef } from 'react';

interface TypewriterTextProps {
  text: string;
  speed?: number; // milliseconds per character
  onComplete?: () => void;
  onUpdate?: () => void; // Called on each character update for scrolling
}

export const TypewriterText = ({ text, speed = 30, onComplete, onUpdate }: TypewriterTextProps) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const completedRef = useRef(false);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(text.slice(0, currentIndex + 1));
        setCurrentIndex(currentIndex + 1);
        // Call onUpdate for auto-scrolling during typing
        if (onUpdate) {
          onUpdate();
        }
      }, speed);

      return () => clearTimeout(timeout);
    } else if (currentIndex === text.length && !completedRef.current && onComplete) {
      completedRef.current = true;
      onComplete();
    }
  }, [currentIndex, text, speed, onComplete, onUpdate]);

  // Reset when text changes
  useEffect(() => {
    setDisplayedText('');
    setCurrentIndex(0);
    completedRef.current = false;
  }, [text]);

  return (
    <span className="whitespace-pre-wrap">
      {displayedText}
      {currentIndex < text.length && (
        <span className="inline-block w-0.5 h-4 bg-foreground ml-0.5 animate-pulse align-middle">|</span>
      )}
    </span>
  );
};

