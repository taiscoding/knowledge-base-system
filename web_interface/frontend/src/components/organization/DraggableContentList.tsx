import React, { useState } from 'react';
import { 
  Box, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  Typography, 
  Paper, 
  Divider,
  IconButton
} from '@mui/material';
import NoteIcon from '@mui/icons-material/Note';
import TaskIcon from '@mui/icons-material/Task';
import EventIcon from '@mui/icons-material/Event';
import FolderIcon from '@mui/icons-material/Folder';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

interface ContentItem {
  id: string;
  title: string;
  type: 'note' | 'todo' | 'calendar' | 'folder';
  description?: string;
  parentId?: string | null;
}

interface DraggableContentListProps {
  items: ContentItem[];
  onDragEnd: (result: any) => void;
  onItemClick?: (id: string) => void;
  currentFolder?: string | null;
}

const DraggableContentList: React.FC<DraggableContentListProps> = ({ 
  items, 
  onDragEnd, 
  onItemClick,
  currentFolder = null
}) => {
  // Group items by whether they are folders or content items
  const folders = items.filter(item => item.type === 'folder');
  const contentItems = items.filter(item => item.type !== 'folder');

  const getIcon = (type: string) => {
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

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ p: 2 }}>
          <Typography variant="h6">
            {currentFolder ? 'Folder Contents' : 'Root Items'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Drag items to rearrange or move between folders
          </Typography>
        </Box>
        
        {/* Folders section */}
        {folders.length > 0 && (
          <>
            <Divider />
            <Box sx={{ p: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Folders
              </Typography>
              <Droppable droppableId="folders">
                {(provided) => (
                  <List
                    {...provided.droppableProps}
                    ref={provided.innerRef}
                    dense
                  >
                    {folders.map((folder, index) => (
                      <Draggable key={folder.id} draggableId={folder.id} index={index}>
                        {(provided) => (
                          <ListItem
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            sx={{ 
                              '&:hover': { bgcolor: 'action.hover' },
                              cursor: 'pointer'
                            }}
                            onClick={() => onItemClick && onItemClick(folder.id)}
                          >
                            <ListItemIcon {...provided.dragHandleProps}>
                              <DragIndicatorIcon />
                            </ListItemIcon>
                            <ListItemIcon>
                              {getIcon(folder.type)}
                            </ListItemIcon>
                            <ListItemText 
                              primary={folder.title} 
                              secondary={folder.description || 'Folder'}
                            />
                          </ListItem>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </List>
                )}
              </Droppable>
            </Box>
          </>
        )}
        
        {/* Content items section */}
        {contentItems.length > 0 && (
          <>
            <Divider />
            <Box sx={{ p: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Content Items
              </Typography>
              <Droppable droppableId="content-items">
                {(provided) => (
                  <List
                    {...provided.droppableProps}
                    ref={provided.innerRef}
                    dense
                  >
                    {contentItems.map((item, index) => (
                      <Draggable key={item.id} draggableId={item.id} index={index}>
                        {(provided) => (
                          <ListItem
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            sx={{ 
                              '&:hover': { bgcolor: 'action.hover' },
                              cursor: 'pointer'
                            }}
                            onClick={() => onItemClick && onItemClick(item.id)}
                          >
                            <ListItemIcon {...provided.dragHandleProps}>
                              <DragIndicatorIcon />
                            </ListItemIcon>
                            <ListItemIcon>
                              {getIcon(item.type)}
                            </ListItemIcon>
                            <ListItemText 
                              primary={item.title} 
                              secondary={item.description || item.type}
                            />
                          </ListItem>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </List>
                )}
              </Droppable>
            </Box>
          </>
        )}
        
        {/* Empty state */}
        {items.length === 0 && (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography color="text.secondary">
              No items in this location
            </Typography>
          </Box>
        )}
      </Paper>
    </DragDropContext>
  );
};

export default DraggableContentList; 