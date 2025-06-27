import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, 
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  FormHelperText,
  CircularProgress,
  Breadcrumbs,
  Link,
  Stack,
  Divider,
  Alert
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ContentTagging from '../components/content/ContentTagging';
import { Content, TodoContent, CalendarContent, Priority, TodoStatus } from '../types';
import api from '../services/api';

const ContentEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [content, setContent] = useState<Content | null>(null);
  const [title, setTitle] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [contentBody, setContentBody] = useState<string>('');
  const [category, setCategory] = useState<string>('');
  const [priority, setPriority] = useState<Priority | ''>('');
  const [status, setStatus] = useState<TodoStatus | ''>('');
  const [dueDate, setDueDate] = useState<Date | null>(null);
  const [eventDate, setEventDate] = useState<Date | null>(null);
  const [tags, setTags] = useState<string[]>([]);
  
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
  
  // Load content on component mount
  useEffect(() => {
    if (id) {
      loadContent(id);
    } else {
      // New content case
      setLoading(false);
      const contentType = new URLSearchParams(window.location.search).get('type') || 'note';
      setContent({
        id: '',
        title: '',
        type: contentType as any,
        created: new Date().toISOString()
      });
    }
  }, [id]);
  
  // Update form fields when content changes
  useEffect(() => {
    if (content) {
      setTitle(content.title);
      setDescription(content.description || '');
      setContentBody(content.content || '');
      setCategory(content.category || '');
      setTags(content.tags || []);
      
      // Type-specific fields
      if (content.type === 'todo') {
        const todoContent = content as TodoContent;
        setPriority(todoContent.priority || '');
        setStatus(todoContent.status || '');
        setDueDate(todoContent.due_date ? new Date(todoContent.due_date) : null);
      } else if (content.type === 'calendar') {
        const calendarContent = content as CalendarContent;
        setEventDate(calendarContent.datetime ? new Date(calendarContent.datetime) : null);
      }
    }
  }, [content]);
  
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
  
  const handleSave = async () => {
    if (!content) return;
    
    if (!title.trim()) {
      setError("Title is required");
      return;
    }
    
    setSaving(true);
    setError(null);
    setSaveSuccess(false);
    
    try {
      const contentData: any = {
        title,
        description,
        content: contentBody,
        category,
        tags
      };
      
      // Add type-specific fields
      if (content.type === 'todo') {
        contentData.priority = priority;
        contentData.status = status;
        contentData.due_date = dueDate ? dueDate.toISOString() : null;
      } else if (content.type === 'calendar') {
        contentData.datetime = eventDate ? eventDate.toISOString() : null;
      }
      
      let response;
      if (id) {
        // Update existing content
        response = await api.updateContent(id, contentData);
      } else {
        // Create new content
        contentData.type = content.type;
        response = await api.createContent(contentData);
      }
      
      if (response.success) {
        setSaveSuccess(true);
        
        // If this was a new content creation, navigate to the new content view
        if (!id && response.data?.id) {
          setTimeout(() => {
            navigate(`/content/${response.data.id}`);
          }, 1000);
        }
      } else {
        throw new Error(response.error || "Failed to save content");
      }
    } catch (err) {
      console.error("Error saving content:", err);
      setError("Failed to save content. Please try again.");
    } finally {
      setSaving(false);
    }
  };
  
  const handleTagsChange = (newTags: string[]) => {
    setTags(newTags);
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
      setError("Failed to delete content. Please try again.");
    }
  };
  
  const handleCancel = () => {
    if (id) {
      // For existing content, navigate to view page
      navigate(`/content/${id}`);
    } else {
      // For new content, navigate back to content type list
      const contentType = content?.type || 'notes';
      navigate(`/${contentType}`);
    }
  };
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error && !content) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="error" variant="h6">
            {error || "Content not found"}
          </Typography>
          <Button 
            startIcon={<ArrowBackIcon />} 
            sx={{ mt: 2 }}
            onClick={() => navigate(-1)}
          >
            Go Back
          </Button>
        </Paper>
      </Container>
    );
  }
  
  const isNewContent = !id;
  const contentTypeLabel = content?.type.charAt(0).toUpperCase() + content?.type.slice(1);
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Breadcrumbs */}
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
          onClick={() => navigate(`/${content?.type}s`)}
        >
          {contentTypeLabel}s
        </Link>
        {!isNewContent && (
          <Link
            color="inherit"
            component="button"
            underline="hover"
            onClick={() => navigate(`/content/${id}`)}
          >
            {content?.title}
          </Link>
        )}
        <Typography color="text.primary">
          {isNewContent ? `New ${contentTypeLabel}` : `Edit ${contentTypeLabel}`}
        </Typography>
      </Breadcrumbs>

      {/* Page header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1">
          {isNewContent ? `Create New ${contentTypeLabel}` : `Edit ${contentTypeLabel}`}
        </Typography>
      </Box>

      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {isNewContent ? "Content created successfully!" : "Changes saved successfully!"}
          {isNewContent && " Redirecting to content view..."}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          {/* Main content form */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Stack spacing={3}>
              <TextField
                label="Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                fullWidth
                required
                error={title.trim() === ''}
                helperText={title.trim() === '' ? 'Title is required' : ''}
              />

              {(content?.type === 'note' || content?.type === 'todo' || content?.type === 'calendar') && (
                <TextField
                  label="Description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  fullWidth
                  multiline
                  rows={2}
                />
              )}

              {content?.type === 'note' && (
                <TextField
                  label="Content"
                  value={contentBody}
                  onChange={(e) => setContentBody(e.target.value)}
                  fullWidth
                  multiline
                  rows={10}
                />
              )}

              <TextField
                label="Category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                fullWidth
              />

              {/* Todo specific fields */}
              {content?.type === 'todo' && (
                <>
                  <Divider textAlign="left">Todo Details</Divider>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel id="priority-label">Priority</InputLabel>
                        <Select
                          labelId="priority-label"
                          value={priority}
                          label="Priority"
                          onChange={(e) => setPriority(e.target.value as Priority)}
                        >
                          <MenuItem value="">None</MenuItem>
                          <MenuItem value="high">High</MenuItem>
                          <MenuItem value="medium">Medium</MenuItem>
                          <MenuItem value="low">Low</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel id="status-label">Status</InputLabel>
                        <Select
                          labelId="status-label"
                          value={status}
                          label="Status"
                          onChange={(e) => setStatus(e.target.value as TodoStatus)}
                        >
                          <MenuItem value="active">Active</MenuItem>
                          <MenuItem value="in progress">In Progress</MenuItem>
                          <MenuItem value="completed">Completed</MenuItem>
                          <MenuItem value="canceled">Canceled</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12}>
                      <LocalizationProvider dateAdapter={AdapterDateFns}>
                        <DateTimePicker
                          label="Due Date"
                          value={dueDate}
                          onChange={(newValue) => setDueDate(newValue)}
                          slotProps={{ textField: { fullWidth: true } }}
                        />
                      </LocalizationProvider>
                    </Grid>
                  </Grid>
                </>
              )}

              {/* Calendar specific fields */}
              {content?.type === 'calendar' && (
                <>
                  <Divider textAlign="left">Event Details</Divider>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DateTimePicker
                      label="Event Date & Time"
                      value={eventDate}
                      onChange={(newValue) => setEventDate(newValue)}
                      slotProps={{ 
                        textField: { 
                          fullWidth: true,
                          required: true,
                          error: !eventDate,
                          helperText: !eventDate ? 'Event date is required' : ''
                        } 
                      }}
                    />
                  </LocalizationProvider>
                </>
              )}
            </Stack>
          </Paper>

          {/* Action buttons */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'space-between' }}>
            <Button
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              onClick={handleCancel}
            >
              Cancel
            </Button>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              {!isNewContent && (
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={handleDelete}
                >
                  Delete
                </Button>
              )}
              
              <Button
                variant="contained"
                color="primary"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={saving || title.trim() === '' || (content?.type === 'calendar' && !eventDate)}
              >
                {saving ? "Saving..." : "Save"}
              </Button>
            </Box>
          </Box>
        </Grid>

        <Grid item xs={12} md={4}>
          {/* Tagging sidebar */}
          <ContentTagging
            contentId={id || ''}
            tags={tags}
            onChange={handleTagsChange}
            allowAutoTagging={!!id} // Only allow auto-tagging for existing content
          />
          
          {/* Edit Tips */}
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Tips
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Typography variant="body2" paragraph>
              {content?.type === 'note' && (
                "Add detailed content to your note. You can organize notes by adding categories and tags."
              )}
              {content?.type === 'todo' && (
                "Set a priority, status, and due date to help organize your tasks. High priority items will be highlighted."
              )}
              {content?.type === 'calendar' && (
                "Make sure to set the date and time for your event. Add a clear description to remind yourself of event details."
              )}
            </Typography>
            
            <Typography variant="body2">
              Tags help you find related content easily. Use specific, consistent tags for better organization.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ContentEdit; 