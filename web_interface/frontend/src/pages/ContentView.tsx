import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Chip,
  Button,
  Grid,
  Breadcrumbs,
  Link,
  IconButton,
  Divider,
  CircularProgress
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ContentTagging from '../components/content/ContentTagging';
import { Content } from '../types';
import api from '../services/api';

const ContentView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [content, setContent] = useState<Content | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadContent(id);
    }
  }, [id]);

  const loadContent = async (contentId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.getContent(contentId);
      
      if (response.data) {
        setContent(response.data);
      } else {
        throw new Error("Content not found");
      }
    } catch (err) {
      console.error("Error loading content:", err);
      setError("Failed to load content. It may have been moved or deleted.");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    navigate(`/content/${id}/edit`);
  };

  const handleDelete = async () => {
    if (!id || !window.confirm("Are you sure you want to delete this content?")) {
      return;
    }
    
    try {
      await api.deleteContent(id);
      // Redirect back to the appropriate page based on content type
      navigate(`/${content?.type || 'notes'}`);
    } catch (err) {
      console.error("Error deleting content:", err);
      alert("Failed to delete content. Please try again.");
    }
  };

  const handleBack = () => {
    // Navigate back or to the content type listing page
    navigate(-1);
  };

  const handleTagsUpdated = (success: boolean) => {
    if (success && id) {
      // Refresh content to get updated tags
      loadContent(id);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: 'numeric'
      }).format(date);
    } catch (e) {
      return dateString;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !content) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="error" variant="h6">
            {error || "Content not found"}
          </Typography>
          <Button 
            startIcon={<ArrowBackIcon />} 
            sx={{ mt: 2 }}
            onClick={handleBack}
          >
            Go Back
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Breadcrumbs navigation */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link 
          color="inherit" 
          component="button"
          underline="hover"
          onClick={() => navigate('/')}
        >
          Home
        </Link>
        <Link 
          color="inherit" 
          component="button"
          underline="hover"
          onClick={() => navigate(`/${content.type}s`)}
        >
          {content.type.charAt(0).toUpperCase() + content.type.slice(1)}s
        </Link>
        <Typography color="text.primary">{content.title}</Typography>
      </Breadcrumbs>

      {/* Content header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center' }}>
        <IconButton 
          sx={{ mr: 1 }}
          onClick={handleBack}
        >
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1">
          {content.title}
        </Typography>
        <Box sx={{ ml: 'auto', display: 'flex', gap: 1 }}>
          <Button 
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={handleEdit}
          >
            Edit
          </Button>
          <Button 
            variant="outlined" 
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleDelete}
          >
            Delete
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          {/* Main content */}
          <Paper sx={{ p: 3, mb: 3 }}>
            {content.category && (
              <Chip 
                label={content.category} 
                color="primary" 
                size="small" 
                sx={{ mb: 2 }} 
              />
            )}

            {content.type === 'todo' && content.status && (
              <Chip 
                label={content.status} 
                color={content.status === 'completed' ? 'success' : 'primary'} 
                variant="outlined"
                size="small" 
                sx={{ mb: 2, ml: 1 }} 
              />
            )}

            {/* Content body */}
            <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-wrap' }}>
              {content.content || content.description || ''}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          {/* Metadata sidebar */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Details
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ mb: 1 }}>
              <Typography variant="body2" color="text.secondary" component="span">
                Type:
              </Typography>{' '}
              <Typography variant="body2" component="span">
                {content.type.charAt(0).toUpperCase() + content.type.slice(1)}
              </Typography>
            </Box>
            
            {content.created && (
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary" component="span">
                  Created:
                </Typography>{' '}
                <Typography variant="body2" component="span">
                  {formatDate(content.created)}
                </Typography>
              </Box>
            )}
            
            {content.modified && (
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary" component="span">
                  Last modified:
                </Typography>{' '}
                <Typography variant="body2" component="span">
                  {formatDate(content.modified)}
                </Typography>
              </Box>
            )}
            
            {content.type === 'todo' && content.due_date && (
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary" component="span">
                  Due date:
                </Typography>{' '}
                <Typography variant="body2" component="span">
                  {formatDate(content.due_date)}
                </Typography>
              </Box>
            )}
            
            {content.type === 'calendar' && content.datetime && (
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary" component="span">
                  Date/time:
                </Typography>{' '}
                <Typography variant="body2" component="span">
                  {formatDate(content.datetime)}
                </Typography>
              </Box>
            )}
          </Paper>

          {/* Tags */}
          {id && (
            <ContentTagging
              contentId={id}
              tags={content.tags || []}
              onTagsUpdated={handleTagsUpdated}
              allowAutoTagging
            />
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default ContentView; 