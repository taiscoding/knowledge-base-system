import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Grid,
  Divider,
  FormControlLabel,
  Switch,
  Button,
  Tabs,
  Tab,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LockIcon from '@mui/icons-material/Lock';
import NotificationsIcon from '@mui/icons-material/Notifications';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

import { PrivacySettings } from '../types';
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
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const Settings: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Theme settings
  const [darkMode, setDarkMode] = useState(false);
  const [fontSize, setFontSize] = useState('medium');
  
  // Privacy settings
  const [privacySettings, setPrivacySettings] = useState<PrivacySettings>({
    level: 'balanced',
    encryptContent: false,
    anonymizeEntities: true,
    allowAiProcessing: true
  });
  
  // Notification settings
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(true);
  const [reminderNotifications, setReminderNotifications] = useState(true);
  
  // User account settings
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  
  // Load settings on component mount
  useEffect(() => {
    loadSettings();
  }, []);
  
  const loadSettings = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load privacy settings
      const privacyResponse = await api.getPrivacySettings();
      
      if (privacyResponse && privacyResponse.data) {
        setPrivacySettings(privacyResponse.data);
      }
      
      // Load other settings from API or local storage
      const userTheme = localStorage.getItem('userTheme') || 'light';
      setDarkMode(userTheme === 'dark');
      
      const userFontSize = localStorage.getItem('fontSize') || 'medium';
      setFontSize(userFontSize);
      
      // Notification settings would typically come from user preferences API
      // Account settings would come from user profile API
      setDisplayName('User Name');
      setEmail('user@example.com');
      
    } catch (err) {
      console.error('Error loading settings:', err);
      setError('Failed to load settings. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  const saveSettings = async () => {
    setLoading(true);
    setSaveSuccess(false);
    setError(null);
    
    try {
      // Save privacy settings
      await api.updatePrivacySettings(privacySettings);
      
      // Save theme preference to local storage
      localStorage.setItem('userTheme', darkMode ? 'dark' : 'light');
      localStorage.setItem('fontSize', fontSize);
      
      // Save other settings to API
      
      setSaveSuccess(true);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSaveSuccess(false);
      }, 3000);
    } catch (err) {
      console.error('Error saving settings:', err);
      setError('Failed to save settings. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>
      
      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="settings tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab icon={<DarkModeIcon />} label="Appearance" />
            <Tab icon={<LockIcon />} label="Privacy & Security" />
            <Tab icon={<NotificationsIcon />} label="Notifications" />
            <Tab icon={<AccountCircleIcon />} label="Account" />
          </Tabs>
        </Box>
        
        {/* Appearance Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Theme
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
                Text Size
              </Typography>
              <FormControl variant="outlined" size="small" sx={{ minWidth: 200 }}>
                <InputLabel>Font Size</InputLabel>
                <Select
                  value={fontSize}
                  onChange={(e) => setFontSize(e.target.value)}
                  label="Font Size"
                >
                  <MenuItem value="small">Small</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="large">Large</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </TabPanel>
        
        {/* Privacy Tab */}
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Privacy Level
              </Typography>
              <FormControl variant="outlined" size="small" sx={{ minWidth: 200 }}>
                <InputLabel>Privacy Level</InputLabel>
                <Select
                  value={privacySettings.level}
                  onChange={(e) => setPrivacySettings({ 
                    ...privacySettings, 
                    level: e.target.value as 'high' | 'balanced' | 'low' 
                  })}
                  label="Privacy Level"
                >
                  <MenuItem value="high">High - Maximum Privacy</MenuItem>
                  <MenuItem value="balanced">Balanced - Recommended</MenuItem>
                  <MenuItem value="low">Low - Maximum Functionality</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Privacy Options
              </Typography>
              <FormControlLabel
                control={
                  <Switch 
                    checked={privacySettings.encryptContent} 
                    onChange={(e) => setPrivacySettings({ 
                      ...privacySettings, 
                      encryptContent: e.target.checked 
                    })} 
                  />
                }
                label="Encrypt all content"
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={privacySettings.anonymizeEntities} 
                    onChange={(e) => setPrivacySettings({ 
                      ...privacySettings, 
                      anonymizeEntities: e.target.checked 
                    })} 
                  />
                }
                label="Anonymize personal entities (names, places, etc.)"
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={privacySettings.allowAiProcessing} 
                    onChange={(e) => setPrivacySettings({ 
                      ...privacySettings, 
                      allowAiProcessing: e.target.checked 
                    })} 
                  />
                }
                label="Allow AI processing of content"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Privacy Sessions
              </Typography>
              <Button 
                variant="outlined" 
                color="primary"
                onClick={() => api.createPrivacySession()}
                sx={{ mb: 2 }}
              >
                Create New Privacy Session
              </Button>
              
              <List>
                <ListItem>
                  <ListItemText 
                    primary="Current Session" 
                    secondary="Created: Today, 12:34 PM" 
                  />
                  <ListItemSecondaryAction>
                    <IconButton edge="end">
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              </List>
            </Grid>
          </Grid>
        </TabPanel>
        
        {/* Notifications Tab */}
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Notification Preferences
              </Typography>
              <FormControlLabel
                control={
                  <Switch 
                    checked={emailNotifications} 
                    onChange={(e) => setEmailNotifications(e.target.checked)} 
                  />
                }
                label="Email notifications"
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={pushNotifications} 
                    onChange={(e) => setPushNotifications(e.target.checked)} 
                  />
                }
                label="Push notifications"
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={reminderNotifications} 
                    onChange={(e) => setReminderNotifications(e.target.checked)} 
                  />
                }
                label="Reminder notifications"
              />
            </Grid>
          </Grid>
        </TabPanel>
        
        {/* Account Tab */}
        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Display Name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <Button variant="contained" color="secondary">
                Change Password
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
          onClick={saveSettings}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Save Settings'}
        </Button>
      </Box>
    </Container>
  );
};

export default Settings; 