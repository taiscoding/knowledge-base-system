import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Button,
  TextField,
  InputAdornment,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  Divider,
  Stack,
  ListItemIcon
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewModuleIcon from '@mui/icons-material/ViewModule';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import SortIcon from '@mui/icons-material/Sort';

// Components
import ContentCard from '../components/content/ContentCard';
import ContentList from '../components/content/ContentList';
import LoadingSpinner from '../components/ui/LoadingSpinner';

// API
import api from '../services/api';

// Types
import { NoteContent as NoteItem, BaseContent } from '../types';

interface NoteFilters {
  category?: string;
  tags?: string[];
  sortBy: 'created' | 'modified' | 'title';
  sortDirection: 'asc' | 'desc';
}

const NotesPage: React.FC = () => {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<NoteItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('grid');
  const [filters, setFilters] = useState<NoteFilters>({
    sortBy: 'modified',
    sortDirection: 'desc'
  });
  
  // UI state
  const [filterMenuAnchor, setFilterMenuAnchor] = useState<null | HTMLElement>(null);
  const [sortMenuAnchor, setSortMenuAnchor] = useState<null | HTMLElement>(null);
  const [actionMenuAnchor, setActionMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newNoteData, setNewNoteData] = useState({
    title: '',
    content: '',
    category: 'personal',
    tags: [] as string[]
  });
  
  const fetchNotes = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Get all notes
      const response = await api.getContentByType('note');
      
      let filteredNotes = response.items || [];
      
      // Apply filters
      if (filters.category) {
        filteredNotes = filteredNotes.filter((note: NoteItem) => 
          note.category?.toLowerCase() === filters.category?.toLowerCase()
        );
      }
      
      if (filters.tags && filters.tags.length > 0) {
        filteredNotes = filteredNotes.filter((note: NoteItem) => 
          filters.tags?.some(tag => note.tags?.includes(tag))
        );
      }
      
      // Apply sorting
      filteredNotes.sort((a: NoteItem, b: NoteItem) => {
        const aValue = a[filters.sortBy];
        const bValue = b[filters.sortBy];
        
        if (typeof aValue === 'string' && typeof bValue === 'string') {
          return filters.sortDirection === 'asc' 
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
        }
        
        return 0;
      });
      
      setNotes(filteredNotes);
    } catch (error) {
      console.error('Error fetching notes:', error);
      setError('Failed to load notes. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [filters]);
  
  // Load notes on component mount
  useEffect(() => {
    fetchNotes();
  }, [fetchNotes]);
  
  const handleSearch = () => {
    if (!searchQuery.trim()) {
      fetchNotes();
      return;
    }
    
    // Filter notes client-side for quick searches
    const filtered = notes.filter(note => 
      note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (note.content && note.content.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (note.tags && note.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())))
    );
    
    setNotes(filtered);
  };
  
  const handleCreateNote = async () => {
    try {
      const result = await api.createContent({
        ...newNoteData,
        type: 'note'
      });
      
      // Add new note to the list
      setNotes([result, ...notes]);
      
      // Close dialog and reset form
      setCreateDialogOpen(false);
      setNewNoteData({
        title: '',
        content: '',
        category: 'personal',
        tags: []
      });
      
      // Navigate to the new note
      navigate(`/content/${result.id}`);
      
    } catch (error) {
      console.error('Error creating note:', error);
      setError('Failed to create note. Please try again.');
    }
  };
  
  const handleDeleteNote = async () => {
    if (!selectedNoteId) return;
    
    try {
      await api.deleteContent(selectedNoteId);
      
      // Remove from list
      setNotes(notes.filter(note => note.id !== selectedNoteId));
      
      // Close menu
      setActionMenuAnchor(null);
      setSelectedNoteId(null);
      
    } catch (error) {
      console.error('Error deleting note:', error);
      setError('Failed to delete note. Please try again.');
    }
  };
  
  const handleNoteClick = (id: string) => {
    navigate(`/content/${id}`);
  };
  
  const handleActionClick = (event: React.MouseEvent<HTMLButtonElement>, id: string) => {
    setActionMenuAnchor(event.currentTarget);
    setSelectedNoteId(id);
  };
  
  const filteredNotes = searchQuery
    ? notes.filter(note => 
        note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (note.content && note.content.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (note.tags && note.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())))
      )
    : notes;
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Notes
      </Typography>
      
      {/* Actions Bar */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              placeholder="Search notes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              size="small"
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={8}>
            <Box sx={{ display: 'flex', gap: 1, justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
              {/* Create Button */}
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={() => setCreateDialogOpen(true)}
              >
                New Note
              </Button>
              
              {/* View Mode Toggle */}
              <IconButton 
                color={viewMode === 'list' ? 'primary' : 'default'} 
                onClick={() => setViewMode('list')}
              >
                <ViewListIcon />
              </IconButton>
              <IconButton 
                color={viewMode === 'grid' ? 'primary' : 'default'} 
                onClick={() => setViewMode('grid')}
              >
                <ViewModuleIcon />
              </IconButton>
              
              {/* Sort Button */}
              <Button
                startIcon={<SortIcon />}
                onClick={(e) => setSortMenuAnchor(e.currentTarget)}
                size="small"
              >
                Sort
              </Button>
              
              {/* Filter Button */}
              <Button
                startIcon={<FilterListIcon />}
                onClick={(e) => setFilterMenuAnchor(e.currentTarget)}
                size="small"
              >
                Filter
              </Button>
            </Box>
          </Grid>
        </Grid>
        
        {/* Active Filters */}
        {(filters.category || (filters.tags && filters.tags.length > 0)) && (
          <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            <Typography variant="body2" sx={{ mr: 1 }}>
              Active filters:
            </Typography>
            
            {filters.category && (
              <Chip
                label={`Category: ${filters.category}`}
                size="small"
                onDelete={() => setFilters({ ...filters, category: undefined })}
              />
            )}
            
            {filters.tags && filters.tags.map(tag => (
              <Chip
                key={tag}
                label={`Tag: ${tag}`}
                size="small"
                onDelete={() => setFilters({
                  ...filters,
                  tags: filters.tags?.filter(t => t !== tag)
                })}
              />
            ))}
            
            <Chip
              label="Clear all"
              size="small"
              variant="outlined"
              onClick={() => setFilters({
                sortBy: filters.sortBy,
                sortDirection: filters.sortDirection
              })}
            />
          </Box>
        )}
      </Paper>
      
      {/* Content */}
      {loading ? (
        <LoadingSpinner />
      ) : error ? (
        <Typography color="error">{error}</Typography>
      ) : filteredNotes.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>No notes found</Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Create a new note or change your search filters
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{ mt: 2 }}
          >
            Create New Note
          </Button>
        </Paper>
      ) : viewMode === 'grid' ? (
        <Grid container spacing={2}>
          {filteredNotes.map(note => (
            <Grid item xs={12} sm={6} md={4} key={note.id}>
              <ContentCard 
                content={note as unknown as BaseContent}
                onClick={() => handleNoteClick(note.id)}
                onActionClick={(e) => handleActionClick(e, note.id)}
              />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Paper>
          <ContentList
            items={filteredNotes.map(note => ({
              id: note.id,
              title: note.title,
              type: 'note',
              description: note.content || '',
              date: note.modified ? new Date(note.modified).toLocaleDateString() : '',
              tags: note.tags || []
            }))}
            onItemClick={handleNoteClick}
            onActionClick={(e, id) => handleActionClick(e, id)}
          />
        </Paper>
      )}
      
      {/* Filter Menu */}
      <Menu
        anchorEl={filterMenuAnchor}
        open={Boolean(filterMenuAnchor)}
        onClose={() => setFilterMenuAnchor(null)}
      >
        <MenuItem onClick={() => {
          setFilters({ ...filters, category: 'personal' });
          setFilterMenuAnchor(null);
        }}>
          Personal Notes
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, category: 'work' });
          setFilterMenuAnchor(null);
        }}>
          Work Notes
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, category: 'research' });
          setFilterMenuAnchor(null);
        }}>
          Research Notes
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => {
          setFilters({
            sortBy: filters.sortBy,
            sortDirection: filters.sortDirection
          });
          setFilterMenuAnchor(null);
        }}>
          Clear Filters
        </MenuItem>
      </Menu>
      
      {/* Sort Menu */}
      <Menu
        anchorEl={sortMenuAnchor}
        open={Boolean(sortMenuAnchor)}
        onClose={() => setSortMenuAnchor(null)}
      >
        <MenuItem onClick={() => {
          setFilters({ ...filters, sortBy: 'modified', sortDirection: 'desc' });
          setSortMenuAnchor(null);
        }}>
          Newest First
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, sortBy: 'modified', sortDirection: 'asc' });
          setSortMenuAnchor(null);
        }}>
          Oldest First
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, sortBy: 'title', sortDirection: 'asc' });
          setSortMenuAnchor(null);
        }}>
          Title (A-Z)
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, sortBy: 'title', sortDirection: 'desc' });
          setSortMenuAnchor(null);
        }}>
          Title (Z-A)
        </MenuItem>
      </Menu>
      
      {/* Action Menu */}
      <Menu
        anchorEl={actionMenuAnchor}
        open={Boolean(actionMenuAnchor)}
        onClose={() => {
          setActionMenuAnchor(null);
          setSelectedNoteId(null);
        }}
      >
        <MenuItem onClick={() => {
          setActionMenuAnchor(null);
          if (selectedNoteId) {
            navigate(`/content/${selectedNoteId}/edit`);
          }
        }}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          Edit
        </MenuItem>
        <MenuItem onClick={handleDeleteNote}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          Delete
        </MenuItem>
      </Menu>
      
      {/* Create Note Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>Create New Note</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Title"
              fullWidth
              value={newNoteData.title}
              onChange={(e) => setNewNoteData({ ...newNoteData, title: e.target.value })}
              autoFocus
            />
            
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={newNoteData.category}
                label="Category"
                onChange={(e) => setNewNoteData({ 
                  ...newNoteData, 
                  category: e.target.value as string 
                })}
              >
                <MenuItem value="personal">Personal</MenuItem>
                <MenuItem value="work">Work</MenuItem>
                <MenuItem value="research">Research</MenuItem>
                <MenuItem value="reference">Reference</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              label="Tags (comma separated)"
              fullWidth
              value={newNoteData.tags.join(', ')}
              onChange={(e) => setNewNoteData({ 
                ...newNoteData, 
                tags: e.target.value.split(',').map(tag => tag.trim()).filter(Boolean)
              })}
            />
            
            <TextField
              label="Content"
              multiline
              rows={10}
              fullWidth
              value={newNoteData.content}
              onChange={(e) => setNewNoteData({ ...newNoteData, content: e.target.value })}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateNote} 
            variant="contained" 
            color="primary"
            disabled={!newNoteData.title.trim()}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default NotesPage; 