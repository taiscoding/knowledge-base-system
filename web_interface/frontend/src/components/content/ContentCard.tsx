import React from 'react';
import { Card, CardContent, CardActions, Typography, Box, Chip, IconButton } from '@mui/material';
import NoteIcon from '@mui/icons-material/Note';
import TaskIcon from '@mui/icons-material/Task';
import EventIcon from '@mui/icons-material/Event';
import FolderIcon from '@mui/icons-material/Folder';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { BaseContent } from '../../types';

/**
 * Props interface for the ContentCard component
 */
interface ContentCardProps {
  /** Content object containing all the necessary data */
  content: BaseContent;
  /** Optional click handler for the entire card */
  onClick?: () => void;
  /** Optional click handler for the action button (three dots) */
  onActionClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

/**
 * ContentCard Component
 * 
 * A reusable component for displaying content items in a card format.
 * This component can be used in grid layouts to show notes, todos, calendar events,
 * or folders with consistent styling and interaction patterns.
 * 
 * @component
 * @example
 * ```tsx
 * <ContentCard
 *   content={noteItem}
 *   onClick={() => navigate(`/content/${noteItem.id}`)}
 *   onActionClick={(e) => handleMenuOpen(e, noteItem.id)}
 * />
 * ```
 */
const ContentCard: React.FC<ContentCardProps> = ({ content, onClick, onActionClick }) => {
  const contentType = content._content_type || content.type || 'note';
  
  /**
   * Returns the appropriate icon based on content type
   * @returns React element with the icon component
   */
  const getIcon = () => {
    switch (contentType.toLowerCase()) {
      case 'note':
      case 'notes':
        return <NoteIcon color="primary" />;
      case 'todo':
      case 'todos':
      case 'task':
      case 'tasks':
        return <TaskIcon color="secondary" />;
      case 'calendar':
      case 'event':
      case 'events':
        return <EventIcon color="info" />;
      case 'folder':
        return <FolderIcon color="action" />;
      default:
        return <NoteIcon />;
    }
  };

  /**
   * Returns the appropriate color for priority badge
   * @returns Material UI color name for the chip
   */
  const getPriorityColor = () => {
    switch (content.priority?.toLowerCase()) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  /**
   * Returns the appropriate color for status badge
   * @returns Material UI color name for the chip
   */
  const getStatusColor = () => {
    switch (content.status?.toLowerCase()) {
      case 'completed':
        return 'success';
      case 'in progress':
      case 'active':
        return 'info';
      case 'canceled':
        return 'error';
      default:
        return 'default';
    }
  };
  
  /**
   * Truncates and returns a preview of the content
   * @returns Truncated content string
   */
  const getContentPreview = () => {
    const text = content.content || content.description || '';
    if (text.length > 80) {
      return text.substring(0, 80) + '...';
    }
    return text;
  };
  
  /**
   * Formats date strings for display
   * @param dateString - ISO date string
   * @returns Formatted date string
   */
  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      }).format(date);
    } catch (e) {
      return dateString;
    }
  };

  return (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        cursor: onClick ? 'pointer' : 'default',
        '&:hover': onClick ? { boxShadow: 3 } : {}
      }}
      onClick={onClick}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Box sx={{ mr: 1 }}>{getIcon()}</Box>
          <Typography variant="subtitle1" component="div" noWrap>
            {content.title}
          </Typography>
          {onActionClick && (
            <Box sx={{ ml: 'auto' }}>
              <IconButton 
                size="small" 
                onClick={(e) => {
                  e.stopPropagation();
                  onActionClick(e);
                }}
              >
                <MoreVertIcon />
              </IconButton>
            </Box>
          )}
        </Box>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {getContentPreview()}
        </Typography>
        
        {/* Metadata */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
          {content.category && (
            <Chip label={content.category} size="small" variant="outlined" />
          )}
          
          {content.status && (
            <Chip 
              label={content.status} 
              size="small" 
              color={getStatusColor() as any}
              variant="outlined" 
            />
          )}
          
          {content.priority && (
            <Chip 
              label={content.priority} 
              size="small" 
              color={getPriorityColor() as any}
              variant="outlined" 
            />
          )}
        </Box>
      </CardContent>
      
      <CardActions sx={{ pt: 0, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', pb: 2, px: 2 }}>
        <Box sx={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Date info */}
          <Typography variant="caption" color="text.secondary">
            {content.due_date && `Due: ${formatDate(content.due_date)}`}
            {content.datetime && `Date: ${formatDate(content.datetime)}`}
            {!content.due_date && !content.datetime && content.created && `Created: ${formatDate(content.created)}`}
          </Typography>
          
          {/* Similarity score if available */}
          {content.similarity !== undefined && (
            <Chip
              label={`${Math.round(content.similarity * 100)}% match`}
              size="small"
              color="primary"
              variant="outlined"
            />
          )}
        </Box>
        
        {/* Tags */}
        {content.tags && content.tags.length > 0 && (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5, width: '100%' }}>
            {content.tags.slice(0, 3).map((tag, i) => (
              <Chip
                key={i}
                label={tag}
                size="small"
                variant="outlined"
                onClick={(e) => e.stopPropagation()}
                sx={{ height: 20, fontSize: '0.7rem' }}
              />
            ))}
            {content.tags.length > 3 && (
              <Chip
                label={`+${content.tags.length - 3}`}
                size="small"
                variant="outlined"
                sx={{ height: 20, fontSize: '0.7rem' }}
              />
            )}
          </Box>
        )}
      </CardActions>
    </Card>
  );
};

export default ContentCard; 