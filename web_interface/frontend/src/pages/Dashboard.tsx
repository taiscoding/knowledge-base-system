import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import AddIcon from '@mui/icons-material/Add';
import MicIcon from '@mui/icons-material/Mic';
import Stack from '@mui/material/Stack';
import Fab from '@mui/material/Fab';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import LinearProgress from '@mui/material/LinearProgress';

// Components
import ContentCard from '../components/content/ContentCard';
import StatCard from '../components/dashboard/StatCard';
import RecentActivity from '../components/dashboard/RecentActivity';
import QuickInput from '../components/input/QuickInput';
import VoiceInputDialog from '../components/input/VoiceInputDialog';
import KnowledgeGraphPreview from '../components/graph/KnowledgeGraphPreview';

// API
import api from '../services/api';

interface DashboardStats {
  totalNotes: number;
  totalTodos: number;
  totalEvents: number;
  activeTodos: number;
  completedTodos: number;
  upcomingEvents: number;
  privacyScore: number;
}

interface ContentDistribution {
  name: string;
  value: number;
  color: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats>({
    totalNotes: 0,
    totalTodos: 0,
    totalEvents: 0,
    activeTodos: 0,
    completedTodos: 0,
    upcomingEvents: 0,
    privacyScore: 0
  });
  const [voiceDialogOpen, setVoiceDialogOpen] = useState(false);
  const [inputText, setInputText] = useState('');
  const [recentContent, setRecentContent] = useState<any[]>([]);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);

  // Content distribution data for pie chart
  const contentDistribution: ContentDistribution[] = [
    { name: 'Notes', value: stats.totalNotes, color: '#3f51b5' },
    { name: 'Todos', value: stats.totalTodos, color: '#f44336' },
    { name: 'Events', value: stats.totalEvents, color: '#4caf50' },
  ];

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // Fetch dashboard statistics
        const statsResponse = await api.get('/api/dashboard/stats');
        
        // Fetch recent content
        const recentContentResponse = await api.get('/api/dashboard/recent-content');
        
        // Fetch recent activity
        const activityResponse = await api.get('/api/dashboard/activity');
        
        setStats(statsResponse.data);
        setRecentContent(recentContentResponse.data);
        setRecentActivity(activityResponse.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Use mock data for demo purposes
        setStats({
          totalNotes: 12,
          totalTodos: 8,
          totalEvents: 5,
          activeTodos: 4,
          completedTodos: 4,
          upcomingEvents: 3,
          privacyScore: 85
        });
        
        setRecentContent([
          { id: '1', title: 'Project Meeting Notes', type: 'note', created: '2025-06-26T13:35:13Z' },
          { id: '2', title: 'Complete milestone 4', type: 'todo', created: '2025-06-23T14:49:23Z' },
          { id: '3', title: 'Team Sync-up', type: 'calendar', created: '2025-06-23T14:38:16Z' }
        ]);
        
        setRecentActivity([
          { id: '1', action: 'created', content: 'Project Meeting Notes', timestamp: '2025-06-26T13:35:13Z' },
          { id: '2', action: 'updated', content: 'Complete milestone 4', timestamp: '2025-06-24T09:12:45Z' },
          { id: '3', action: 'deleted', content: 'Old draft', timestamp: '2025-06-23T16:22:33Z' }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleInputSubmit = async () => {
    if (!inputText.trim()) return;
    
    setLoading(true);
    try {
      await api.post('/api/process', { content: inputText });
      setInputText('');
      // Refresh data
      // In a real app, you'd refresh only what's needed
      navigate(0); // Refresh the page for simplicity
    } catch (error) {
      console.error('Error processing input:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceInput = (text: string) => {
    setInputText(text);
    setVoiceDialogOpen(false);
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <Typography variant="h4" sx={{ mb: 2 }}>
          Loading Dashboard...
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Quick Input Section */}
      <Paper sx={{ p: 2, mb: 3, display: 'flex', alignItems: 'center' }}>
        <QuickInput
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onSubmit={handleInputSubmit}
          placeholder="Enter stream of consciousness text..."
          fullWidth
        />
        <Fab
          color="primary"
          size="small"
          sx={{ ml: 1 }}
          onClick={() => setVoiceDialogOpen(true)}
        >
          <MicIcon />
        </Fab>
      </Paper>
      
      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Notes"
            value={stats.totalNotes}
            icon="note"
            color="#3f51b5"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Todos"
            value={stats.activeTodos}
            icon="todo"
            color="#f44336"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Upcoming Events"
            value={stats.upcomingEvents}
            icon="calendar"
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Privacy Score"
            value={stats.privacyScore}
            icon="privacy"
            color="#ff9800"
            isPercentage
          />
        </Grid>
      </Grid>
      
      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Content Distribution Chart */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              Content Distribution
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={contentDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label
                >
                  {contentDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`${value} items`, name]} />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        
        {/* Knowledge Graph Preview */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 300 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="h6">Knowledge Graph</Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={() => navigate('/knowledge-graph')}
              >
                View Full Graph
              </Button>
            </Box>
            <KnowledgeGraphPreview />
          </Paper>
        </Grid>
        
        {/* Recent Content */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Recent Content</Typography>
              <Button
                startIcon={<AddIcon />}
                variant="contained"
                size="small"
                onClick={() => navigate('/notes/new')}
              >
                New Note
              </Button>
            </Box>
            <Stack spacing={2}>
              {recentContent.map((content) => (
                <ContentCard
                  key={content.id}
                  content={content}
                  onClick={() => navigate(`/content/${content.id}`)}
                />
              ))}
            </Stack>
          </Paper>
        </Grid>
        
        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <RecentActivity activities={recentActivity} />
          </Paper>
        </Grid>
      </Grid>
      
      {/* Voice Input Dialog */}
      <VoiceInputDialog
        open={voiceDialogOpen}
        onClose={() => setVoiceDialogOpen(false)}
        onTranscription={handleVoiceInput}
      />
    </Box>
  );
};

export default Dashboard; 