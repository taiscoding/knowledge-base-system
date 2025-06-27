import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Typography,
  Grid,
  Paper,
  Box,
  IconButton,
  Divider,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

import { getAllShortcuts, useGlobalKeyboardShortcuts } from '../../utils/keyboardShortcuts';

interface ShortcutHelpProps {
  shortcut: string;
  description: string;
}

const ShortcutHelp: React.FC<ShortcutHelpProps> = ({ shortcut, description }) => {
  return (
    <Grid container spacing={2} sx={{ my: 1 }}>
      <Grid item xs={4} sm={3}>
        <Paper 
          elevation={0} 
          sx={{ 
            p: 1, 
            textAlign: 'center', 
            backgroundColor: 'action.hover',
            borderRadius: 1,
            fontFamily: 'monospace'
          }}
        >
          {shortcut}
        </Paper>
      </Grid>
      <Grid item xs={8} sm={9}>
        <Typography variant="body2" sx={{ pt: 1 }}>
          {description}
        </Typography>
      </Grid>
    </Grid>
  );
};

/**
 * Keyboard Shortcuts Help Dialog
 * Displays a modal with all available keyboard shortcuts
 */
const KeyboardShortcutsHelp: React.FC = () => {
  const [open, setOpen] = useState(false);
  const { shortcuts } = useGlobalKeyboardShortcuts();
  
  useEffect(() => {
    const handleShowShortcutsHelp = () => {
      setOpen(true);
    };
    
    window.addEventListener('show-shortcuts-help', handleShowShortcutsHelp);
    
    return () => {
      window.removeEventListener('show-shortcuts-help', handleShowShortcutsHelp);
    };
  }, []);
  
  const handleClose = () => {
    setOpen(false);
  };
  
  const shortcutGroups = [
    {
      title: 'Navigation',
      shortcuts: [
        { shortcut: 'Ctrl+D', description: 'Go to dashboard' },
        { shortcut: 'Ctrl+G', description: 'Open knowledge graph' },
        { shortcut: 'Ctrl+K', description: 'Open search' },
        { shortcut: 'Ctrl+P', description: 'Open profile' },
        { shortcut: 'Ctrl+,', description: 'Open settings' },
      ]
    },
    {
      title: 'Content',
      shortcuts: [
        { shortcut: 'Ctrl+Alt+N', description: 'Create new note' },
        { shortcut: 'Ctrl+Alt+T', description: 'Create new todo' },
        { shortcut: 'Ctrl+S', description: 'Save content (when editing)' },
      ]
    },
    {
      title: 'Help',
      shortcuts: [
        { shortcut: 'Ctrl+?', description: 'Show keyboard shortcuts help' },
      ]
    }
  ];
  
  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      fullWidth
      maxWidth="md"
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h5">Keyboard Shortcuts</Typography>
          <IconButton 
            edge="end" 
            color="inherit" 
            onClick={handleClose}
            aria-label="close"
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <Divider />
      <DialogContent>
        <Grid container spacing={4}>
          {shortcutGroups.map((group) => (
            <Grid item xs={12} md={6} key={group.title}>
              <Typography variant="h6" gutterBottom>
                {group.title}
              </Typography>
              <Box mb={2}>
                {group.shortcuts.map((shortcut) => (
                  <ShortcutHelp
                    key={shortcut.shortcut}
                    shortcut={shortcut.shortcut}
                    description={shortcut.description}
                  />
                ))}
              </Box>
            </Grid>
          ))}
        </Grid>
      </DialogContent>
    </Dialog>
  );
};

export default KeyboardShortcutsHelp; 