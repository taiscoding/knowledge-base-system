import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  altKey?: boolean;
  shiftKey?: boolean;
  handler: () => void;
  description: string;
}

/**
 * Global keyboard shortcuts mapping
 * Maps keyboard shortcuts to their respective handlers and descriptions
 */
const useKeyboardShortcuts = (): KeyboardShortcut[] => {
  const navigate = useNavigate();
  
  // Define shortcuts
  const shortcuts: KeyboardShortcut[] = [
    {
      key: 'k',
      ctrlKey: true,
      handler: () => navigate('/search'),
      description: 'Open search',
    },
    {
      key: 'd',
      ctrlKey: true,
      handler: () => navigate('/dashboard'),
      description: 'Go to dashboard',
    },
    {
      key: 'n',
      ctrlKey: true,
      altKey: true,
      handler: () => navigate('/notes?action=new'),
      description: 'Create new note',
    },
    {
      key: 't',
      ctrlKey: true,
      altKey: true,
      handler: () => navigate('/todos?action=new'),
      description: 'Create new todo',
    },
    {
      key: 'g',
      ctrlKey: true,
      handler: () => navigate('/graph'),
      description: 'Open knowledge graph',
    },
    {
      key: ',',
      ctrlKey: true,
      handler: () => navigate('/settings'),
      description: 'Open settings',
    },
    {
      key: 'p',
      ctrlKey: true,
      handler: () => navigate('/profile'),
      description: 'Open profile',
    },
    {
      key: '?',
      ctrlKey: true,
      handler: () => {
        // Show keyboard shortcuts help modal
        const event = new CustomEvent('show-shortcuts-help');
        window.dispatchEvent(event);
      },
      description: 'Show keyboard shortcuts help',
    },
  ];
  
  return shortcuts;
};

/**
 * Keyboard shortcuts hook
 * Manages global keyboard shortcuts for the application
 * 
 * @param enabled - Whether keyboard shortcuts are enabled
 */
export const useGlobalKeyboardShortcuts = (enabled: boolean = true) => {
  const shortcuts = useKeyboardShortcuts();
  
  useEffect(() => {
    if (!enabled) return;
    
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore keyboard shortcuts when typing in input or textarea
      if (
        event.target instanceof HTMLInputElement || 
        event.target instanceof HTMLTextAreaElement ||
        (event.target instanceof HTMLElement && event.target.isContentEditable)
      ) {
        return;
      }
      
      // Check if the key combination matches any of our shortcuts
      const matchedShortcut = shortcuts.find(
        (shortcut) =>
          shortcut.key.toLowerCase() === event.key.toLowerCase() &&
          !!shortcut.ctrlKey === event.ctrlKey &&
          !!shortcut.altKey === event.altKey &&
          !!shortcut.shiftKey === event.shiftKey
      );
      
      if (matchedShortcut) {
        event.preventDefault();
        matchedShortcut.handler();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [enabled, shortcuts]);
  
  return {
    shortcuts,
  };
};

/**
 * Returns a formatted string representation of a keyboard shortcut
 * 
 * @param shortcut - Keyboard shortcut object
 * @returns Formatted shortcut string (e.g., "Ctrl+Alt+N")
 */
export const formatShortcut = (shortcut: KeyboardShortcut): string => {
  const parts: string[] = [];
  
  if (shortcut.ctrlKey) parts.push('Ctrl');
  if (shortcut.altKey) parts.push('Alt');
  if (shortcut.shiftKey) parts.push('Shift');
  
  parts.push(shortcut.key.toUpperCase());
  
  return parts.join('+');
};

/**
 * Returns all available keyboard shortcuts
 */
export const getAllShortcuts = (): { shortcut: string; description: string }[] => {
  const shortcuts = useKeyboardShortcuts();
  
  return shortcuts.map((shortcut) => ({
    shortcut: formatShortcut(shortcut),
    description: shortcut.description,
  }));
}; 