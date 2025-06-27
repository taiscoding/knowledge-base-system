import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ListSubheader from '@mui/material/ListSubheader';
import Divider from '@mui/material/Divider';
import DashboardIcon from '@mui/icons-material/Dashboard';
import NoteIcon from '@mui/icons-material/Note';
import ChecklistIcon from '@mui/icons-material/CheckBoxOutlined';
import CalendarIcon from '@mui/icons-material/CalendarToday';
import SearchIcon from '@mui/icons-material/Search';
import ChatIcon from '@mui/icons-material/Chat';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import MicIcon from '@mui/icons-material/Mic';
import SettingsIcon from '@mui/icons-material/Settings';
import SecurityIcon from '@mui/icons-material/Security';
import CategoryIcon from '@mui/icons-material/Category';

const SidebarNavigation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Primary navigation items
  const mainItems = [
    { name: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { name: 'Notes', icon: <NoteIcon />, path: '/notes' },
    { name: 'Todos', icon: <ChecklistIcon />, path: '/todos' },
    { name: 'Calendar', icon: <CalendarIcon />, path: '/calendar' },
    { name: 'Knowledge Graph', icon: <AccountTreeIcon />, path: '/knowledge-graph' },
  ];
  
  // Secondary navigation items
  const searchItems = [
    { name: 'Search', icon: <SearchIcon />, path: '/search' },
    { name: 'Natural Language', icon: <ChatIcon />, path: '/natural-language' },
    { name: 'Voice Input', icon: <MicIcon />, path: '/voice' },
  ];
  
  // Settings navigation items
  const settingsItems = [
    { name: 'Categories', icon: <CategoryIcon />, path: '/categories' },
    { name: 'Privacy', icon: <SecurityIcon />, path: '/privacy' },
    { name: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];
  
  // Handle navigation
  const handleNavigate = (path: string) => {
    navigate(path);
  };
  
  // Check if a menu item is active
  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') {
      return true;
    }
    return location.pathname.startsWith(path) && path !== '/';
  };
  
  return (
    <React.Fragment>
      <List component="nav">
        {mainItems.map((item) => (
          <ListItemButton
            key={item.name}
            onClick={() => handleNavigate(item.path)}
            selected={isActive(item.path)}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.name} />
          </ListItemButton>
        ))}
        
        <Divider sx={{ my: 1 }} />
        
        <ListSubheader component="div" inset>
          Search & Input
        </ListSubheader>
        
        {searchItems.map((item) => (
          <ListItemButton
            key={item.name}
            onClick={() => handleNavigate(item.path)}
            selected={isActive(item.path)}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.name} />
          </ListItemButton>
        ))}
        
        <Divider sx={{ my: 1 }} />
        
        <ListSubheader component="div" inset>
          System
        </ListSubheader>
        
        {settingsItems.map((item) => (
          <ListItemButton
            key={item.name}
            onClick={() => handleNavigate(item.path)}
            selected={isActive(item.path)}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.name} />
          </ListItemButton>
        ))}
      </List>
    </React.Fragment>
  );
};

export default SidebarNavigation; 