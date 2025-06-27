import React from 'react';
import { Box, Typography, List, ListItem, ListItemText, ListItemIcon, Chip, IconButton } from '@mui/material';
import NoteIcon from '@mui/icons-material/Note';
import TaskIcon from '@mui/icons-material/Task';
import EventIcon from '@mui/icons-material/Event';
import FolderIcon from '@mui/icons-material/Folder';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { BaseContent, ContentType } from '../../types';

interface ContentItemProps extends BaseContent {
  onClick?: (id: string) => void;
  onActionClick?: (event: React.MouseEvent<HTMLButtonElement>, id: string) => void;
}

interface ContentListProps {
  items: ContentItemProps[];
  emptyMessage?: string;
  onItemClick?: (id: string) => void;
  onActionClick?: (event: React.MouseEvent<HTMLButtonElement>, id: string) => void;
}

const ContentList: React.FC<ContentListProps> = ({ 
  items, 
  emptyMessage = "No content items to display", 
  onItemClick,
  onActionClick
}) => {
  const getIcon = (type: ContentType) => {
    switch (type) {
      case 'note':
        return <NoteIcon />;
      case 'todo':
        return <TaskIcon />;
      case 'calendar':
        return <EventIcon />;
      case 'folder':
        return <FolderIcon />;
      default:
        return <NoteIcon />;
    }
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority?.toLowerCase()) {
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

  const getStatusColor = (status?: string) => {
    switch (status?.toLowerCase()) {
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

  const handleItemClick = (id: string) => {
    if (onItemClick) {
      onItemClick(id);
    }
  };

  if (!items || items.length === 0) {
    return (
      <Box sx={{ py: 4, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          {emptyMessage}
        </Typography>
      </Box>
    );
  }

  return (
    <List sx={{ width: '100%' }}>
      {items.map((item) => (
        <ListItem
          key={item.id}
          alignItems="flex-start"
          sx={{
            mb: 1,
            borderRadius: 1,
            '&:hover': {
              bgcolor: 'action.hover',
              cursor: 'pointer'
            }
          }}
          onClick={() => handleItemClick(item.id)}
          secondaryAction={
            onActionClick && (
              <IconButton edge="end" onClick={(e) => {
                e.stopPropagation();
                onActionClick(e, item.id);
              }}>
                <MoreVertIcon />
              </IconButton>
            )
          }
        >
          <ListItemIcon>{getIcon(item.type)}</ListItemIcon>
          <ListItemText
            primary={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="subtitle1" component="span">
                  {item.title}
                </Typography>
                {item.priority && (
                  <Chip 
                    label={item.priority} 
                    size="small" 
                    color={getPriorityColor(item.priority) as any} 
                    variant="outlined" 
                  />
                )}
                {item.status && (
                  <Chip 
                    label={item.status} 
                    size="small" 
                    color={getStatusColor(item.status) as any} 
                    variant="outlined" 
                  />
                )}
              </Box>
            }
            secondary={
              <React.Fragment>
                {item.description && (
                  <Typography
                    variant="body2"
                    color="text.primary"
                    component="span"
                    sx={{ display: 'block', mb: 0.5 }}
                  >
                    {item.description.length > 100 
                      ? `${item.description.substring(0, 100)}...` 
                      : item.description}
                  </Typography>
                )}
                <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                  {item.created && (
                    <Typography variant="caption" color="text.secondary" component="span">
                      {item.created}
                    </Typography>
                  )}
                  {item.tags && item.tags.length > 0 && (
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {item.tags.map((tag, index) => (
                        <Chip
                          key={index}
                          label={tag}
                          size="small"
                          variant="outlined"
                          onClick={(e) => {
                            e.stopPropagation();
                            // Tag click handler could go here
                          }}
                          sx={{ height: 20, fontSize: '0.7rem' }}
                        />
                      ))}
                    </Box>
                  )}
                </Box>
              </React.Fragment>
            }
          />
        </ListItem>
      ))}
    </List>
  );
};

export default ContentList; 