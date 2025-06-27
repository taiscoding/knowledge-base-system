import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Chip,
  TextField,
  Button,
  Autocomplete,
  Paper,
  Stack,
  IconButton,
  Collapse,
  Alert
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import SyncIcon from '@mui/icons-material/Sync';

import api from '../../services/api';
import { TagData } from '../../types';

interface ContentTaggingProps {
  contentId: string;
  tags: string[];
  onChange?: (newTags: string[]) => void;
  onTagsUpdated?: (success: boolean) => void;
  allowAutoTagging?: boolean;
}

interface AlertMessage {
  type: 'success' | 'error' | 'info';
  message: string;
}

const ContentTagging: React.FC<ContentTaggingProps> = ({
  contentId,
  tags,
  onChange,
  onTagsUpdated,
  allowAutoTagging = false
}) => {
  const [currentTags, setCurrentTags] = useState<string[]>(tags || []);
  const [inputValue, setInputValue] = useState<string>('');
  const [suggestedTags, setSuggestedTags] = useState<string[]>([]);
  const [popularTags, setPopularTags] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [alertMessage, setAlertMessage] = useState<AlertMessage | null>(null);

  // Load popular tags on component mount
  useEffect(() => {
    const loadPopularTags = async () => {
      try {
        const response = await api.getPopularTags();
        setPopularTags(response.tags || []);
      } catch (error) {
        console.error('Error loading popular tags:', error);
      }
    };
    
    loadPopularTags();
  }, []);

  // Update local state when props change
  useEffect(() => {
    setCurrentTags(tags || []);
  }, [tags]);

  const handleTagAdd = () => {
    if (inputValue && !currentTags.includes(inputValue)) {
      const newTags = [...currentTags, inputValue];
      setCurrentTags(newTags);
      setInputValue('');
      
      if (onChange) {
        onChange(newTags);
      }
      
      // Save tags to API
      updateContentTags(newTags);
    }
  };

  const handleTagDelete = (tagToDelete: string) => {
    const newTags = currentTags.filter(tag => tag !== tagToDelete);
    setCurrentTags(newTags);
    
    if (onChange) {
      onChange(newTags);
    }
    
    // Save tags to API
    updateContentTags(newTags);
  };

  const handleTagClick = (tag: string) => {
    if (!currentTags.includes(tag)) {
      const newTags = [...currentTags, tag];
      setCurrentTags(newTags);
      
      if (onChange) {
        onChange(newTags);
      }
      
      // Save tags to API
      updateContentTags(newTags);
    }
  };
  
  const autoGenerateTags = async () => {
    setLoading(true);
    setAlertMessage(null);
    
    try {
      const result = await api.autoGenerateTags(contentId);
      
      if (result.combined_tags) {
        setCurrentTags(result.combined_tags);
        
        if (onChange) {
          onChange(result.combined_tags);
        }
        
        setAlertMessage({
          type: 'success',
          message: `Successfully generated ${result.new_tags?.length || 0} new tags`
        });
        
        if (onTagsUpdated) {
          onTagsUpdated(true);
        }
      }
    } catch (error) {
      console.error('Error generating tags:', error);
      setAlertMessage({
        type: 'error',
        message: 'Failed to generate tags'
      });
      
      if (onTagsUpdated) {
        onTagsUpdated(false);
      }
    } finally {
      setLoading(false);
    }
  };
  
  const updateContentTags = async (newTags: string[]) => {
    try {
      await api.updateContent(contentId, { tags: newTags });
      
      if (onTagsUpdated) {
        onTagsUpdated(true);
      }
    } catch (error) {
      console.error('Error updating tags:', error);
      
      if (onTagsUpdated) {
        onTagsUpdated(false);
      }
    }
  };
  
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="subtitle1" gutterBottom>
        Tags
      </Typography>
      
      {/* Current tags */}
      <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
        {currentTags.length > 0 ? (
          currentTags.map(tag => (
            <Chip
              key={tag}
              label={tag}
              onDelete={() => handleTagDelete(tag)}
              color="primary"
              variant="outlined"
              size="small"
            />
          ))
        ) : (
          <Typography variant="body2" color="text.secondary">
            No tags yet
          </Typography>
        )}
      </Box>
      
      {/* Add new tags */}
      <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
        <Autocomplete
          freeSolo
          options={suggestedTags}
          inputValue={inputValue}
          onInputChange={(event, newValue) => {
            setInputValue(newValue);
          }}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Add tag"
              variant="outlined"
              size="small"
              fullWidth
            />
          )}
          sx={{ flexGrow: 1 }}
        />
        <Button 
          variant="contained" 
          color="primary"
          onClick={handleTagAdd}
          startIcon={<AddIcon />}
          disabled={!inputValue}
        >
          Add
        </Button>
        
        {allowAutoTagging && (
          <Button
            variant="outlined"
            color="secondary"
            onClick={autoGenerateTags}
            startIcon={<SyncIcon />}
            disabled={loading}
          >
            Auto-Tag
          </Button>
        )}
      </Stack>
      
      {/* Alert message */}
      <Collapse in={!!alertMessage}>
        {alertMessage && (
          <Alert
            severity={alertMessage.type}
            action={
              <IconButton
                aria-label="close"
                color="inherit"
                size="small"
                onClick={() => setAlertMessage(null)}
              >
                <CloseIcon fontSize="inherit" />
              </IconButton>
            }
            sx={{ mb: 2 }}
          >
            {alertMessage.message}
          </Alert>
        )}
      </Collapse>
      
      {/* Popular tags */}
      {popularTags.length > 0 && (
        <>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Popular tags:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {popularTags.map(tag => (
              <Chip
                key={tag}
                label={tag}
                size="small"
                variant="outlined"
                onClick={() => handleTagClick(tag)}
                sx={{ 
                  cursor: 'pointer',
                  opacity: currentTags.includes(tag) ? 0.5 : 1
                }}
              />
            ))}
          </Box>
        </>
      )}
    </Paper>
  );
};

export default ContentTagging; 