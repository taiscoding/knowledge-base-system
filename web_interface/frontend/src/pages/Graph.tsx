import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Grid,
  Slider,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Card,
  CardContent,
  IconButton,
  Tooltip
} from '@mui/material';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import CenterFocusStrongIcon from '@mui/icons-material/CenterFocusStrong';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit';

import KnowledgeGraph from '../components/visualization/KnowledgeGraph';
import { GraphNode, Content } from '../types';
import api from '../services/api';

const Graph: React.FC = () => {
  const [recentContent, setRecentContent] = useState<Content[]>([]);
  const [maxDepth, setMaxDepth] = useState<number>(2);
  const [selectedRootIds, setSelectedRootIds] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [fullscreen, setFullscreen] = useState<boolean>(false);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  
  useEffect(() => {
    loadRecentContent();
  }, []);
  
  const loadRecentContent = async () => {
    setLoading(true);
    
    try {
      // Load recent content from API
      const response = await api.request('/dashboard/activity?limit=10');
      
      if (response && response.data) {
        setRecentContent(response.data);
      } else {
        throw new Error("Failed to load recent content");
      }
    } catch (err) {
      console.error('Error loading recent content:', err);
      setError('Failed to load content data. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleRootSelection = (contentId: string) => {
    if (!contentId) return;
    
    if (selectedRootIds.includes(contentId)) {
      setSelectedRootIds(selectedRootIds.filter(id => id !== contentId));
    } else {
      setSelectedRootIds([...selectedRootIds, contentId]);
    }
  };
  
  const handleDepthChange = (_event: Event, newValue: number | number[]) => {
    setMaxDepth(newValue as number);
  };
  
  const handleNodeClick = async (nodeId: string) => {
    try {
      const response = await api.getContent(nodeId);
      
      if (response && response.data) {
        setSelectedNode(response.data);
      }
    } catch (err) {
      console.error('Error loading node data:', err);
    }
  };
  
  const handleClearSelection = () => {
    setSelectedRootIds([]);
  };
  
  const toggleFullscreen = () => {
    setFullscreen(!fullscreen);
  };
  
  const getGraphHeight = () => {
    return fullscreen ? window.innerHeight - 100 : 600;
  };
  
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Page header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1">
          Knowledge Graph
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Visualize relationships between your knowledge items
        </Typography>
      </Box>
      
      <Grid container spacing={3}>
        {/* Side panel */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Graph Settings
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {/* Depth slider */}
            <Box sx={{ mb: 3 }}>
              <Typography id="depth-slider" gutterBottom>
                Exploration Depth: {maxDepth}
              </Typography>
              <Slider
                value={maxDepth}
                onChange={handleDepthChange}
                aria-labelledby="depth-slider"
                valueLabelDisplay="auto"
                step={1}
                marks
                min={1}
                max={5}
              />
            </Box>
            
            {/* Root selection */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                Selected Root Items ({selectedRootIds.length})
              </Typography>
              {selectedRootIds.length > 0 ? (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selectedRootIds.map(id => {
                    const content = recentContent.find(c => c.id === id);
                    return (
                      <Chip 
                        key={id} 
                        label={content?.title || id.substring(0, 8)} 
                        onDelete={() => handleRootSelection(id)}
                        size="small"
                      />
                    );
                  })}
                  <Button 
                    size="small" 
                    onClick={handleClearSelection}
                    sx={{ mt: 1 }}
                  >
                    Clear All
                  </Button>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No root items selected. Showing full graph.
                </Typography>
              )}
            </Box>
          </Paper>
          
          {/* Recent content for selection */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Recent Content
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                <CircularProgress size={24} />
              </Box>
            ) : recentContent.length > 0 ? (
              <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                {recentContent.map(content => (
                  <Box 
                    key={content.id} 
                    onClick={() => handleRootSelection(content.id)}
                    sx={{ 
                      p: 1, 
                      mb: 1, 
                      borderRadius: 1,
                      cursor: 'pointer', 
                      bgcolor: selectedRootIds.includes(content.id) 
                        ? 'action.selected' 
                        : 'transparent',
                      '&:hover': { bgcolor: 'action.hover' }
                    }}
                  >
                    <Typography variant="body2" noWrap>
                      {content.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {content.type} • {new Date(content.created || '').toLocaleDateString()}
                    </Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No recent content found.
              </Typography>
            )}
          </Paper>
        </Grid>
        
        {/* Main graph area */}
        <Grid item xs={12} md={8}>
          <Box sx={{ position: 'relative' }}>
            {/* Graph toolbar */}
            <Paper 
              sx={{ 
                p: 1, 
                mb: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <Box>
                <Tooltip title="Zoom in">
                  <IconButton size="small">
                    <ZoomInIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Zoom out">
                  <IconButton size="small">
                    <ZoomOutIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Reset zoom">
                  <IconButton size="small">
                    <CenterFocusStrongIcon />
                  </IconButton>
                </Tooltip>
              </Box>
              
              <Box>
                <Tooltip title={fullscreen ? "Exit fullscreen" : "Fullscreen"}>
                  <IconButton onClick={toggleFullscreen} size="small">
                    {fullscreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
                  </IconButton>
                </Tooltip>
              </Box>
            </Paper>
            
            {/* The graph component */}
            <Box sx={{ height: getGraphHeight() }}>
              <KnowledgeGraph 
                rootIds={selectedRootIds}
                maxDepth={maxDepth}
                height={getGraphHeight()}
                onNodeClick={handleNodeClick}
              />
            </Box>
            
            {/* Selected node details */}
            {selectedNode && (
              <Card 
                sx={{ 
                  position: 'absolute', 
                  bottom: 16, 
                  right: 16, 
                  width: 300,
                  boxShadow: 3
                }}
              >
                <CardContent>
                  <Typography variant="subtitle1">{selectedNode.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Type: {selectedNode.type}
                  </Typography>
                  {selectedNode.category && (
                    <Typography variant="body2" color="text.secondary">
                      Category: {selectedNode.category}
                    </Typography>
                  )}
                  <Button 
                    size="small" 
                    href={`/content/${selectedNode.id}`} 
                    sx={{ mt: 1 }}
                  >
                    View Details
                  </Button>
                </CardContent>
              </Card>
            )}
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Graph;
