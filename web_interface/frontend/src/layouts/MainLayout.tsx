import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  Toolbar,
  Typography,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery,
  ListItemButton,
  Avatar,
  Menu,
  MenuItem,
  Tooltip,
  Badge,
  InputBase,
  Paper
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import NoteIcon from '@mui/icons-material/Note';
import TaskIcon from '@mui/icons-material/Task';
import EventIcon from '@mui/icons-material/Event';
import FolderIcon from '@mui/icons-material/Folder';
import SearchIcon from '@mui/icons-material/Search';
import SettingsIcon from '@mui/icons-material/Settings';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import NotificationsIcon from '@mui/icons-material/Notifications';
import HelpIcon from '@mui/icons-material/Help';
import LogoutIcon from '@mui/icons-material/Logout';
import ChatIcon from '@mui/icons-material/Chat';
import ShareIcon from '@mui/icons-material/Share';
import PrivacyTipIcon from '@mui/icons-material/PrivacyTip';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import KeyboardIcon from '@mui/icons-material/Keyboard';

// Import keyboard shortcuts
import { useGlobalKeyboardShortcuts } from '../utils/keyboardShortcuts';

// Import keyboard shortcuts help dialog
import KeyboardShortcutsHelp from '../components/ui/KeyboardShortcutsHelp';

// Sidebar width
const drawerWidth = 240;

const MainLayout: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // State
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState<null | HTMLElement>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Enable keyboard shortcuts
  const { shortcuts } = useGlobalKeyboardShortcuts(true);
  
  // Navigation items
  const navigationItems = [
    { 
      text: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/dashboard'
    },
    { 
      text: 'Notes',
      icon: <NoteIcon />,
      path: '/notes'
    },
    { 
      text: 'Todos',
      icon: <TaskIcon />,
      path: '/todos'
    },
    { 
      text: 'Calendar',
      icon: <EventIcon />,
      path: '/calendar'
    },
    { 
      text: 'Knowledge Graph',
      icon: <AccountTreeIcon />,
      path: '/graph'
    },
    {
      text: 'Folders',
      icon: <FolderIcon />,
      path: '/folders'
    }
  ];
  
  const secondaryNavigationItems = [
    {
      text: 'Natural Language',
      icon: <ChatIcon />,
      path: '/nlp'
    },
    {
      text: 'Privacy Controls',
      icon: <PrivacyTipIcon />,
      path: '/privacy'
    },
    {
      text: 'Share & Export',
      icon: <ShareIcon />,
      path: '/share'
    },
    {
      text: 'Settings',
      icon: <SettingsIcon />,
      path: '/settings'
    }
  ];
  
  // Handle drawer toggle
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };
  
  // Handle navigation
  const handleNavigate = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };
  
  // Handle search submit
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  // Show keyboard shortcuts modal
  const handleOpenShortcutsHelp = () => {
    const event = new CustomEvent('show-shortcuts-help');
    window.dispatchEvent(event);
  };
  
  // Drawer content
  const drawerContent = (
    <>
      <Toolbar>
        <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold' }}>
          Knowledge Base
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {navigationItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton 
              selected={location.pathname === item.path}
              onClick={() => handleNavigate(item.path)}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        {secondaryNavigationItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton 
              selected={location.pathname === item.path}
              onClick={() => handleNavigate(item.path)}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </>
  );
  
  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          {/* Page title - dynamically determined based on current path */}
          <Typography variant="h6" noWrap component="div" sx={{ display: { xs: 'none', sm: 'block' } }}>
            {navigationItems.find(item => item.path === location.pathname)?.text || 
             secondaryNavigationItems.find(item => item.path === location.pathname)?.text ||
             'Knowledge Base'}
          </Typography>
          
          {/* Spacer */}
          <Box sx={{ flexGrow: 1 }} />
          
          {/* Search Bar */}
          <Paper
            component="form"
            sx={{ 
              p: '2px 4px', 
              display: 'flex', 
              alignItems: 'center', 
              width: { xs: 150, sm: 300 },
              mr: 2,
              borderRadius: 4
            }}
            onSubmit={handleSearchSubmit}
          >
            <InputBase
              sx={{ ml: 1, flex: 1 }}
              placeholder="Search Knowledge Base"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <IconButton type="submit" sx={{ p: '10px' }} aria-label="search">
              <SearchIcon />
            </IconButton>
          </Paper>
          
          {/* Keyboard shortcuts help */}
          <Tooltip title="Keyboard Shortcuts">
            <IconButton 
              color="inherit"
              onClick={handleOpenShortcutsHelp}
            >
              <KeyboardIcon />
            </IconButton>
          </Tooltip>
          
          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton 
              color="inherit"
              onClick={(e) => setNotificationsAnchor(e.currentTarget)}
            >
              <Badge badgeContent={3} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>
          
          {/* Help */}
          <Tooltip title="Help">
            <IconButton 
              color="inherit"
              onClick={() => handleNavigate('/help')}
            >
              <HelpIcon />
            </IconButton>
          </Tooltip>
          
          {/* User menu */}
          <Tooltip title="Account">
            <IconButton
              color="inherit"
              onClick={(e) => setUserMenuAnchor(e.currentTarget)}
              sx={{ ml: 1 }}
            >
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>U</Avatar>
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>
      
      {/* Sidebar */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="navigation"
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawerContent}
        </Drawer>
        
        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>
      
      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          marginTop: '64px', // AppBar height
          minHeight: 'calc(100vh - 64px)', // Full height minus AppBar
          backgroundColor: 'background.default'
        }}
      >
        <Outlet />
      </Box>
      
      {/* User Menu */}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={() => setUserMenuAnchor(null)}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={() => {
          handleNavigate('/profile');
          setUserMenuAnchor(null);
        }}>
          <ListItemIcon>
            <AccountCircleIcon fontSize="small" />
          </ListItemIcon>
          Profile
        </MenuItem>
        <MenuItem onClick={() => {
          handleNavigate('/settings');
          setUserMenuAnchor(null);
        }}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          Settings
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => {
          // Handle logout
          setUserMenuAnchor(null);
        }}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>
      
      {/* Notifications Menu */}
      <Menu
        anchorEl={notificationsAnchor}
        open={Boolean(notificationsAnchor)}
        onClose={() => setNotificationsAnchor(null)}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: {
            width: 320,
            maxHeight: 400,
          },
        }}
      >
        <MenuItem>
          <ListItemIcon>
            <TaskIcon fontSize="small" color="primary" />
          </ListItemIcon>
          <Box>
            <Typography variant="body2">Todo item "Design UI" is due today</Typography>
            <Typography variant="caption" color="text.secondary">5 minutes ago</Typography>
          </Box>
        </MenuItem>
        <MenuItem>
          <ListItemIcon>
            <EventIcon fontSize="small" color="primary" />
          </ListItemIcon>
          <Box>
            <Typography variant="body2">Meeting "Project Review" starts in 30 minutes</Typography>
            <Typography variant="caption" color="text.secondary">30 minutes ago</Typography>
          </Box>
        </MenuItem>
        <MenuItem>
          <ListItemIcon>
            <NoteIcon fontSize="small" color="primary" />
          </ListItemIcon>
          <Box>
            <Typography variant="body2">New note added to "Project Ideas" folder</Typography>
            <Typography variant="caption" color="text.secondary">2 hours ago</Typography>
          </Box>
        </MenuItem>
        <Divider />
        <MenuItem
          sx={{ justifyContent: 'center', color: 'primary.main' }}
          onClick={() => {
            handleNavigate('/notifications');
            setNotificationsAnchor(null);
          }}
        >
          View all notifications
        </MenuItem>
      </Menu>

      {/* Keyboard Shortcuts Help Dialog */}
      <KeyboardShortcutsHelp />
    </Box>
  );
};

export default MainLayout; 