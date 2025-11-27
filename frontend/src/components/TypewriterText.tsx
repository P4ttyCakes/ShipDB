import { useEffect, useState, useRef } from 'react';

interface TypewriterTextProps {
  text: string;
  speed?: number; // milliseconds per character
  onComplete?: () => void;
  className?: string;
  messageKey?: string | number; // Unique key to prevent re-animation
}

export const TypewriterText = ({ 
  text, 
  speed = 20, 
  onComplete,
  className = '',
  messageKey
}: TypewriterTextProps) => {
  const [displayedText, setDisplayedText] = useState('');
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastTextRef = useRef<string>('');
  const lastKeyRef = useRef<string | number | undefined>(messageKey);
  const stableKey = messageKey !== undefined ? String(messageKey) : 'default';

  useEffect(() => {
    // Check if message key changed (new message)
    const isNewMessage = messageKey !== lastKeyRef.current;
    
    // Check if text actually changed
    const textChanged = text !== lastTextRef.current;
    
    // If nothing changed, don't restart animation
    if (!isNewMessage && !textChanged && displayedText === text) {
      return;
    }

    // If message key changed, reset everything
    if (isNewMessage) {
      lastKeyRef.current = messageKey;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      setDisplayedText('');
      lastTextRef.current = '';
    }

    // Update last text
    const previousText = lastTextRef.current;
    lastTextRef.current = text;

    // If text is empty, complete immediately
    if (!text || text.length === 0) {
      setDisplayedText('');
      if (onComplete) {
        onComplete();
      }
      return;
    }

    // If text decreased (shouldn't happen, but handle it)
    if (text.length < previousText.length || (isNewMessage && !textChanged)) {
      setDisplayedText('');
    }

    // Clear any existing animation
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Determine starting index - continue from current displayed length if text grew
    const startIndex = !isNewMessage && text.startsWith(displayedText) ? displayedText.length : 0;

    let currentIndex = startIndex;

    // Start typing animation
    intervalRef.current = setInterval(() => {
      currentIndex += 1;
      
      if (currentIndex > text.length) {
        // Animation complete
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        if (onComplete) {
          onComplete();
        }
        return;
      }
      
      setDisplayedText(text.slice(0, currentIndex));
    }, speed);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [text, speed, stableKey, messageKey]);

  return (
    <span className={className}>
      {displayedText}
      {displayedText.length < text.length && (
        <span className="inline-block w-0.5 h-4 bg-current opacity-75 ml-0.5 animate-pulse align-middle" />
      )}
    </span>
  );
};
