import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  List, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  Collapse,
  Paper,
  Tooltip
} from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import NoteIcon from '@mui/icons-material/Note';
import TaskIcon from '@mui/icons-material/Task';
import EventIcon from '@mui/icons-material/Event';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';

interface FolderItem {
  id: string;
  title: string;
  children?: FolderItem[];
  type: 'folder' | 'note' | 'todo' | 'calendar';
  icon?: string;
}

interface FolderHierarchyProps {
  root: FolderItem;
  onItemClick: (id: string, type: string) => void;
  selectedId?: string;
}

const FolderTreeNode: React.FC<{
  item: FolderItem; 
  level: number;
  onItemClick: (id: string, type: string) => void;
  selectedId?: string;
}> = ({ item, level, onItemClick, selectedId }) => {
  const [open, setOpen] = useState(level < 2); // Auto-expand first two levels
  
  const handleClick = () => {
    if (item.type === 'folder' && item.children && item.children.length > 0) {
      setOpen(!open);
    }
    onItemClick(item.id, item.type);
  };
  
  const getIcon = () => {
    if (item.type === 'folder') {
      return open ? <FolderOpenIcon color="primary" /> : <FolderIcon color="primary" />;
    } else if (item.type === 'note') {
      return <NoteIcon color="info" />;
    } else if (item.type === 'todo') {
      return <TaskIcon color="secondary" />;
    } else if (item.type === 'calendar') {
      return <EventIcon color="success" />;
    }
    return <NoteIcon />;
  };
  
  const hasChildren = item.children && item.children.length > 0;
  
  return (
    <>
      <ListItemButton
        onClick={handleClick}
        sx={{ 
          pl: 2 + level * 2, 
          backgroundColor: selectedId === item.id ? 'action.selected' : 'transparent',
          '&:hover': {
            backgroundColor: selectedId === item.id ? 'action.selected' : 'action.hover',
          }
        }}
      >
        <ListItemIcon>
          {getIcon()}
        </ListItemIcon>
        <ListItemText 
          primary={
            <Tooltip title={item.title} placement="right" arrow>
              <Typography 
                variant="body2" 
                noWrap
                sx={{ maxWidth: 180 }}
              >
                {item.title}
              </Typography>
            </Tooltip>
          } 
        />
        {hasChildren && (open ? <ExpandLess /> : <ExpandMore />)}
      </ListItemButton>
      
      {hasChildren && (
        <Collapse in={open} timeout="auto" unmountOnExit>
          {item.children?.map((child) => (
            <FolderTreeNode 
              key={child.id} 
              item={child} 
              level={level + 1}
              onItemClick={onItemClick}
              selectedId={selectedId}
            />
          ))}
        </Collapse>
      )}
    </>
  );
};

const FolderHierarchy: React.FC<FolderHierarchyProps> = ({ 
  root, 
  onItemClick,
  selectedId 
}) => {
  return (
    <Paper sx={{ maxHeight: '80vh', overflow: 'auto', mb: 2 }}>
      <Box sx={{ p: 2 }}>
        <Typography variant="h6">Folder Structure</Typography>
      </Box>
      <List
        dense
        component="nav"
        aria-labelledby="folder-hierarchy"
        sx={{ width: '100%', bgcolor: 'background.paper' }}
      >
        <FolderTreeNode 
          item={root} 
          level={0} 
          onItemClick={onItemClick}
          selectedId={selectedId}
        />
      </List>
    </Paper>
  );
};

export default FolderHierarchy; 