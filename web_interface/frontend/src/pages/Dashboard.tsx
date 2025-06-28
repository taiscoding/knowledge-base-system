import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardActions,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  IconButton
} from '@mui/material';
import NoteIcon from '@mui/icons-material/Note';
import TaskIcon from '@mui/icons-material/Task';
import EventIcon from '@mui/icons-material/Event';
import FolderIcon from '@mui/icons-material/Folder';
import SearchIcon from '@mui/icons-material/Search';
import BarChartIcon from '@mui/icons-material/BarChart';
import {
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

// API
import api from '../services/api';

// Types
import { ContentStats } from '../types';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<ContentStats>({
    notes: 0,
    todos: 0,
    events: 0,
    folders: 0,
    total: 0
  });
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  
  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Fetch stats
        const statsData = await api.getDashboardStats();
        setStats(statsData.data || {
          notes: 0,
          todos: 0,
          events: 0,
          folders: 0,
          total: 0
        });
        
        // Fetch recent activity
        const activityData = await api.getRecentActivity(5);
        setRecentActivity(activityData.data || []);
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);
  
  // Colors for charts
  const chartColors = {
    notes: '#2196f3',
    todos: '#673ab7',
    events: '#ff9800',
    folders: '#4caf50'
  };
  
  // Data for pie chart
  const pieChartData = [
    { name: 'Notes', value: stats.notes, color: chartColors.notes },
    { name: 'Todos', value: stats.todos, color: chartColors.todos },
    { name: 'Calendar Events', value: stats.events, color: chartColors.events },
    { name: 'Folders', value: stats.folders, color: chartColors.folders }
  ].filter(item => item.value > 0);
  
  // Activity icon mapping based on type
  const getActivityIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'note':
        return <NoteIcon color="primary" />;
      case 'todo':
        return <TaskIcon color="secondary" />;
      case 'event':
      case 'calendar':
        return <EventIcon color="warning" />;
      case 'folder':
        return <FolderIcon color="success" />;
      default:
        return <SearchIcon />;
    }
  };
  
  // Format activity timestamp
  const formatActivityTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffSeconds < 60) {
      return 'Just now';
    } else if (diffSeconds < 3600) {
      const minutes = Math.floor(diffSeconds / 60);
      return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    } else if (diffSeconds < 86400) {
      const hours = Math.floor(diffSeconds / 3600);
      return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    } else if (diffSeconds < 604800) {
      const days = Math.floor(diffSeconds / 86400);
      return `${days} day${days !== 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString();
    }
  };
  
  // Handle card click
  const handleCardClick = (path: string) => {
    navigate(path);
  };
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {error && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'error.light', color: 'error.contrastText' }}>
          <Typography>{error}</Typography>
        </Paper>
      )}
      
      {/* Content Type Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ 
              bgcolor: '#e3f2fd', 
              cursor: 'pointer',
              '&:hover': { boxShadow: 3 }
            }}
            onClick={() => handleCardClick('/notes')}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="h5" component="div">
                  {stats.notes}
                </Typography>
                <NoteIcon sx={{ fontSize: 40, color: chartColors.notes }} />
              </Box>
              <Typography color="text.secondary">
                Notes
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ 
              bgcolor: '#ede7f6', 
              cursor: 'pointer',
              '&:hover': { boxShadow: 3 }
            }}
            onClick={() => handleCardClick('/todos')}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="h5" component="div">
                  {stats.todos}
                </Typography>
                <TaskIcon sx={{ fontSize: 40, color: chartColors.todos }} />
              </Box>
              <Typography color="text.secondary">
                Todos
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ 
              bgcolor: '#fff3e0', 
              cursor: 'pointer',
              '&:hover': { boxShadow: 3 }
            }}
            onClick={() => handleCardClick('/calendar')}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="h5" component="div">
                  {stats.events}
                </Typography>
                <EventIcon sx={{ fontSize: 40, color: chartColors.events }} />
              </Box>
              <Typography color="text.secondary">
                Calendar Events
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ 
              bgcolor: '#e8f5e9', 
              cursor: 'pointer',
              '&:hover': { boxShadow: 3 }
            }}
            onClick={() => handleCardClick('/folders')}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="h5" component="div">
                  {stats.folders}
                </Typography>
                <FolderIcon sx={{ fontSize: 40, color: chartColors.folders }} />
              </Box>
              <Typography color="text.secondary">
                Folders
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Grid container spacing={3}>
        {/* Chart: Content Distribution */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 350 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">
                Content Distribution
              </Typography>
              <IconButton size="small">
                <BarChartIcon />
              </IconButton>
            </Box>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ height: 250 }}>
              {pieChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                    >
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => [`${value} items`, 'Count']} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                  <Typography variant="body2" color="text.secondary">
                    No data available
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>
        
        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 350 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Divider sx={{ mb: 1 }} />
            
            {recentActivity.length > 0 ? (
              <List>
                {recentActivity.map((activity: any, index: number) => (
                  <ListItem 
                    key={index}
                    button
                    onClick={() => navigate(`/content/${activity.id}`)}
                    secondaryAction={
                      <Typography variant="caption" color="text.secondary">
                        {formatActivityTime(activity.timestamp)}
                      </Typography>
                    }
                  >
                    <ListItemIcon>
                      {getActivityIcon(activity.type)}
                    </ListItemIcon>
                    <ListItemText 
                      primary={activity.title}
                      secondary={`${activity.action} ${activity.type}`}
                      primaryTypographyProps={{ noWrap: true }}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '80%' }}>
                <Typography variant="body2" color="text.secondary">
                  No recent activity
                </Typography>
              </Box>
            )}
            
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
              <Button size="small" onClick={() => navigate('/search')}>
                View All Activity
              </Button>
            </Box>
          </Paper>
        </Grid>
        
        {/* Suggestions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Suggested Actions
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Organize Your Notes
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      You have {stats.notes} notes. Consider organizing them into folders or adding tags.
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small" onClick={() => navigate('/notes')}>Manage Notes</Button>
                  </CardActions>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Review Pending Tasks
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      You have active todos that might need your attention.
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small" onClick={() => navigate('/todos')}>View Todos</Button>
                  </CardActions>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Explore Knowledge Graph
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Visualize connections between your content items.
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small" onClick={() => navigate('/graph')}>View Graph</Button>
                  </CardActions>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 