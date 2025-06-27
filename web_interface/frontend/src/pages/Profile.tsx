import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Grid,
  TextField,
  Button,
  Avatar,
  Card,
  CardContent,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Chip
} from '@mui/material';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import SecurityIcon from '@mui/icons-material/Security';
import HistoryIcon from '@mui/icons-material/History';
import NotificationsIcon from '@mui/icons-material/Notifications';
import FolderIcon from '@mui/icons-material/Folder';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import PersonIcon from '@mui/icons-material/Person';
import SaveIcon from '@mui/icons-material/Save';

import api from '../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface UserProfile {
  displayName: string;
  email: string;
  bio: string;
  location: string;
  tags: string[];
  avatar?: string;
  dateJoined: string;
}

const Profile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile>({
    displayName: 'User Name',
    email: 'user@example.com',
    bio: 'Knowledge management enthusiast',
    location: 'San Francisco, CA',
    tags: ['Research', 'Notes', 'Organization'],
    dateJoined: '2023-04-15'
  });
  
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Preferences
  const [autoTagging, setAutoTagging] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [keyboardShortcuts, setKeyboardShortcuts] = useState(true);
  const [defaultView, setDefaultView] = useState('cards');
  
  useEffect(() => {
    // Load profile data
    loadProfile();
  }, []);
  
  const loadProfile = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // This would be replaced with an actual API call in production
      // const response = await api.getUserProfile();
      // if (response && response.data) {
      //   setProfile(response.data);
      // }
      
      // For demo purposes, use the default profile data
      setTimeout(() => {
        setLoading(false);
      }, 500);
    } catch (err) {
      console.error('Error loading profile:', err);
      setError('Failed to load profile data. Please try again.');
      setLoading(false);
    }
  };
  
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  const saveProfile = async () => {
    setLoading(true);
    setSaveSuccess(false);
    setError(null);
    
    try {
      // This would be replaced with an actual API call in production
      // await api.updateUserProfile(profile);
      
      // For demo purposes, simulate an API call
      setTimeout(() => {
        setSaveSuccess(true);
        setLoading(false);
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          setSaveSuccess(false);
        }, 3000);
      }, 1000);
    } catch (err) {
      console.error('Error saving profile:', err);
      setError('Failed to save profile. Please try again.');
      setLoading(false);
    }
  };
  
  const handleAddTag = (tag: string) => {
    if (!profile.tags.includes(tag)) {
      setProfile({
        ...profile,
        tags: [...profile.tags, tag]
      });
    }
  };
  
  const handleRemoveTag = (tag: string) => {
    setProfile({
      ...profile,
      tags: profile.tags.filter(t => t !== tag)
    });
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        My Profile
      </Typography>
      
      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Profile updated successfully
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        {/* Profile Overview Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Box sx={{ position: 'relative', display: 'inline-block' }}>
                <Avatar
                  sx={{ width: 120, height: 120, mx: 'auto', mb: 2, bgcolor: 'primary.main', fontSize: 48 }}
                >
                  {profile.displayName.charAt(0)}
                </Avatar>
                <IconButton
                  sx={{
                    position: 'absolute',
                    bottom: 0,
                    right: 0,
                    bgcolor: 'background.paper',
                    borderRadius: '50%',
                    border: '2px solid white',
                    padding: '4px',
                  }}
                >
                  <CameraAltIcon fontSize="small" />
                </IconButton>
              </Box>
              
              <Typography variant="h5" gutterBottom>
                {profile.displayName}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {profile.email}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {profile.location}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block">
                Member since {new Date(profile.dateJoined).toLocaleDateString()}
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                {profile.tags.map((tag) => (
                  <Chip
                    key={tag}
                    label={tag}
                    size="small"
                    sx={{ m: 0.5 }}
                    onDelete={() => handleRemoveTag(tag)}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Storage Overview
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <FolderIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Notes"
                    secondary="35 items"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <BookmarkIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Bookmarks"
                    secondary="12 items"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <HistoryIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Recent Activity"
                    secondary="Last activity: Today"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Profile Edit Area */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ width: '100%' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs
                value={tabValue}
                onChange={handleTabChange}
                aria-label="profile tabs"
                variant="scrollable"
                scrollButtons="auto"
              >
                <Tab icon={<PersonIcon />} label="Personal Info" />
                <Tab icon={<NotificationsIcon />} label="Preferences" />
                <Tab icon={<SecurityIcon />} label="Security" />
              </Tabs>
            </Box>
            
            {/* Personal Info Tab */}
            <TabPanel value={tabValue} index={0}>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Display Name"
                    value={profile.displayName}
                    onChange={(e) => setProfile({ ...profile, displayName: e.target.value })}
                    fullWidth
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Email"
                    value={profile.email}
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    fullWidth
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    label="Bio"
                    value={profile.bio}
                    onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                    multiline
                    rows={3}
                    fullWidth
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Location"
                    value={profile.location}
                    onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                    fullWidth
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Tags & Interests
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    {profile.tags.map((tag) => (
                      <Chip
                        key={tag}
                        label={tag}
                        sx={{ m: 0.5 }}
                        onDelete={() => handleRemoveTag(tag)}
                      />
                    ))}
                  </Box>
                  <TextField
                    label="Add tag"
                    placeholder="Enter tag and press Enter"
                    size="small"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.currentTarget.value) {
                        handleAddTag(e.currentTarget.value);
                        e.currentTarget.value = '';
                      }
                    }}
                  />
                </Grid>
              </Grid>
            </TabPanel>
            
            {/* Preferences Tab */}
            <TabPanel value={tabValue} index={1}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Display Preferences
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={darkMode}
                        onChange={(e) => setDarkMode(e.target.checked)}
                      />
                    }
                    label="Dark Mode"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Interface Preferences
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={keyboardShortcuts}
                        onChange={(e) => setKeyboardShortcuts(e.target.checked)}
                      />
                    }
                    label="Enable keyboard shortcuts"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Content Preferences
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={autoTagging}
                        onChange={(e) => setAutoTagging(e.target.checked)}
                      />
                    }
                    label="Auto-tagging for new content"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Keyboard Shortcuts
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText
                        primary="Create new note"
                        secondary="Ctrl+Alt+N"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Open search"
                        secondary="Ctrl+K"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Save content"
                        secondary="Ctrl+S"
                      />
                    </ListItem>
                  </List>
                </Grid>
              </Grid>
            </TabPanel>
            
            {/* Security Tab */}
            <TabPanel value={tabValue} index={2}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Change Password
                  </Typography>
                  <TextField
                    label="Current Password"
                    type="password"
                    fullWidth
                    sx={{ mb: 2 }}
                  />
                  <TextField
                    label="New Password"
                    type="password"
                    fullWidth
                    sx={{ mb: 2 }}
                  />
                  <TextField
                    label="Confirm New Password"
                    type="password"
                    fullWidth
                    sx={{ mb: 2 }}
                  />
                  <Button 
                    variant="contained" 
                    color="primary"
                  >
                    Update Password
                  </Button>
                </Grid>
                
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle1" gutterBottom>
                    Two-Factor Authentication
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch />
                    }
                    label="Enable two-factor authentication"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle1" gutterBottom>
                    Sessions
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    You are currently logged in from 1 location.
                  </Typography>
                  <Button 
                    variant="outlined" 
                    color="secondary"
                    sx={{ mt: 1 }}
                  >
                    Log out all other sessions
                  </Button>
                </Grid>
              </Grid>
            </TabPanel>
          </Paper>
          
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<SaveIcon />}
              onClick={saveProfile}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Save Profile'}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Profile; 