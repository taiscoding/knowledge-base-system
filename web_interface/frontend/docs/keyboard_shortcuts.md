# Keyboard Shortcuts

This document outlines the keyboard shortcuts available in the Knowledge Base System web interface.

## Available Shortcuts

| Shortcut      | Action                | Description                             |
|---------------|----------------------|------------------------------------------|
| `Ctrl+K`      | Open Search          | Opens the search dialog                  |
| `Ctrl+D`      | Go to Dashboard      | Navigates to the dashboard page          |
| `Ctrl+Alt+N`  | Create New Note      | Opens the note creation interface        |
| `Ctrl+Alt+T`  | Create New Todo      | Opens the todo creation interface        |
| `Ctrl+G`      | Go to Graph          | Navigates to knowledge graph page        |
| `Ctrl+,`      | Open Settings        | Opens the settings page                  |
| `Ctrl+P`      | Open Profile         | Opens the user profile page              |
| `Ctrl+?`      | Show Shortcuts Help  | Displays this keyboard shortcuts dialog  |
| `Ctrl+S`      | Save Content         | Saves the current content (when editing) |

## Accessing Keyboard Shortcuts

There are multiple ways to access the keyboard shortcuts:

1. **Keyboard Shortcuts Dialog**: Press `Ctrl+?` to open the keyboard shortcuts help dialog anytime
2. **Keyboard Icon**: Click the keyboard icon in the top toolbar
3. **Settings**: View and modify keyboard shortcuts in Settings → Preferences

## Customizing Shortcuts

You can enable or disable keyboard shortcuts in the Settings page under the Preferences tab.

## Implementation Details

Keyboard shortcuts are implemented using a global event listener that checks for key combinations. The shortcuts are ignored when typing in text fields or content editors to prevent conflicts with standard editing operations.

### Code Example

```typescript
// Using keyboard shortcuts in custom components
import { useGlobalKeyboardShortcuts } from '../utils/keyboardShortcuts';

const MyComponent = () => {
  // Enable keyboard shortcuts in this component
  const { shortcuts } = useGlobalKeyboardShortcuts(true);
  
  // ...component code
  
  return (
    // ...component JSX
  );
};
```

## Accessibility Considerations

- Keyboard shortcuts can be fully disabled for users who prefer not to use them
- All functionality accessible via keyboard shortcuts is also available through the regular UI
- The keyboard shortcuts help dialog is accessible via both keyboard and mouse

## Future Enhancements

- Customizable keyboard shortcuts
- Context-sensitive shortcuts based on the current view
- Additional shortcuts for power users 