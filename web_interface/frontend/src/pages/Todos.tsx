import React, { useState, useEffect } from 'react';
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
  Switch,
  FormControlLabel
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewModuleIcon from '@mui/icons-material/ViewModule';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import SortIcon from '@mui/icons-material/Sort';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';

// Components
import ContentCard from '../components/content/ContentCard';
import ContentList from '../components/content/ContentList';
import LoadingSpinner from '../components/ui/LoadingSpinner';

// API
import api from '../services/api';

// Types
interface TodoItem {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  due_date?: string;
  tags: string[];
  created: string;
  modified: string;
  type: string;
  _content_type: string;
}

interface TodoFilters {
  status?: string;
  priority?: string;
  sortBy: 'due_date' | 'created' | 'modified' | 'priority' | 'title';
  sortDirection: 'asc' | 'desc';
}

const TodosPage: React.FC = () => {
  const navigate = useNavigate();
  const [todos, setTodos] = useState<TodoItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
  const [filters, setFilters] = useState<TodoFilters>({
    sortBy: 'due_date',
    sortDirection: 'asc'
  });
  
  // UI state
  const [filterMenuAnchor, setFilterMenuAnchor] = useState<null | HTMLElement>(null);
  const [sortMenuAnchor, setSortMenuAnchor] = useState<null | HTMLElement>(null);
  const [actionMenuAnchor, setActionMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedTodoId, setSelectedTodoId] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newTodoData, setNewTodoData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    status: 'active',
    due_date: '',
    tags: [] as string[]
  });
  
  // Load todos on component mount
  useEffect(() => {
    fetchTodos();
  }, []);
  
  // Re-fetch when filters change
  useEffect(() => {
    if (!loading) {
      fetchTodos();
    }
  }, [filters]);
  
  const fetchTodos = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Get all todos
      const response = await api.getContentByType('todo');
      
      let filteredTodos = response.items || [];
      
      // Apply filters
      if (filters.status) {
        filteredTodos = filteredTodos.filter(todo => 
          todo.status?.toLowerCase() === filters.status?.toLowerCase()
        );
      }
      
      if (filters.priority) {
        filteredTodos = filteredTodos.filter(todo => 
          todo.priority?.toLowerCase() === filters.priority?.toLowerCase()
        );
      }
      
      // Apply sorting
      filteredTodos.sort((a, b) => {
        const aValue = a[filters.sortBy];
        const bValue = b[filters.sortBy];
        
        // Handle due_date sorting specially
        if (filters.sortBy === 'due_date') {
          const dateA = aValue ? new Date(aValue).getTime() : Number.MAX_SAFE_INTEGER;
          const dateB = bValue ? new Date(bValue).getTime() : Number.MAX_SAFE_INTEGER;
          
          return filters.sortDirection === 'asc'
            ? dateA - dateB
            : dateB - dateA;
        }
        
        // Handle priority sorting specially
        if (filters.sortBy === 'priority') {
          const priorityRank = {
            'high': 3,
            'medium': 2,
            'low': 1
          };
          
          const rankA = priorityRank[aValue?.toLowerCase()] || 0;
          const rankB = priorityRank[bValue?.toLowerCase()] || 0;
          
          return filters.sortDirection === 'asc'
            ? rankA - rankB
            : rankB - rankA;
        }
        
        // Default string sorting
        if (typeof aValue === 'string' && typeof bValue === 'string') {
          return filters.sortDirection === 'asc' 
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
        }
        
        return 0;
      });
      
      setTodos(filteredTodos);
    } catch (error) {
      console.error('Error fetching todos:', error);
      setError('Failed to load todos. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleSearch = () => {
    if (!searchQuery.trim()) {
      fetchTodos();
      return;
    }
    
    // Filter todos client-side for quick searches
    const filtered = todos.filter(todo => 
      todo.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      todo.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      todo.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    );
    
    setTodos(filtered);
  };
  
  const handleCreateTodo = async () => {
    try {
      const result = await api.createContent({
        ...newTodoData,
        type: 'todo'
      });
      
      // Add new todo to the list
      setTodos([result, ...todos]);
      
      // Close dialog and reset form
      setCreateDialogOpen(false);
      setNewTodoData({
        title: '',
        description: '',
        priority: 'medium',
        status: 'active',
        due_date: '',
        tags: []
      });
      
      // Navigate to the new todo
      navigate(`/content/${result.id}`);
      
    } catch (error) {
      console.error('Error creating todo:', error);
      setError('Failed to create todo. Please try again.');
    }
  };
  
  const handleDeleteTodo = async () => {
    if (!selectedTodoId) return;
    
    try {
      await api.deleteContent(selectedTodoId);
      
      // Remove from list
      setTodos(todos.filter(todo => todo.id !== selectedTodoId));
      
      // Close menu
      setActionMenuAnchor(null);
      setSelectedTodoId(null);
      
    } catch (error) {
      console.error('Error deleting todo:', error);
      setError('Failed to delete todo. Please try again.');
    }
  };
  
  const handleTodoClick = (id: string) => {
    navigate(`/content/${id}`);
  };
  
  const handleActionClick = (event: React.MouseEvent, id: string) => {
    setActionMenuAnchor(event.currentTarget);
    setSelectedTodoId(id);
  };
  
  const handleToggleStatus = async (id: string) => {
    const todo = todos.find(t => t.id === id);
    if (!todo) return;
    
    const newStatus = todo.status === 'completed' ? 'active' : 'completed';
    
    try {
      await api.updateContent(id, { status: newStatus });
      
      // Update local state
      setTodos(todos.map(t => 
        t.id === id ? { ...t, status: newStatus } : t
      ));
      
    } catch (error) {
      console.error('Error updating todo status:', error);
      setError('Failed to update todo status. Please try again.');
    }
  };
  
  const filteredTodos = searchQuery
    ? todos.filter(todo => 
        todo.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        todo.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        todo.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : todos;
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Todo Items
      </Typography>
      
      {/* Actions Bar */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              placeholder="Search todos..."
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
                New Todo
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
        {(filters.status || filters.priority) && (
          <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            <Typography variant="body2" sx={{ mr: 1 }}>
              Active filters:
            </Typography>
            
            {filters.status && (
              <Chip
                label={`Status: ${filters.status}`}
                size="small"
                onDelete={() => setFilters({ ...filters, status: undefined })}
              />
            )}
            
            {filters.priority && (
              <Chip
                label={`Priority: ${filters.priority}`}
                size="small"
                onDelete={() => setFilters({ ...filters, priority: undefined })}
              />
            )}
            
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
      ) : filteredTodos.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>No todo items found</Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Create a new todo or change your search filters
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{ mt: 2 }}
          >
            Create New Todo
          </Button>
        </Paper>
      ) : viewMode === 'grid' ? (
        <Grid container spacing={2}>
          {filteredTodos.map(todo => (
            <Grid item xs={12} sm={6} md={4} key={todo.id}>
              <ContentCard 
                content={{
                  ...todo,
                  content: todo.description // Map description to content for ContentCard
                }}
                onClick={() => handleTodoClick(todo.id)}
                onActionClick={(e) => handleActionClick(e, todo.id)}
              />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Paper>
          <ContentList
            items={filteredTodos.map(todo => ({
              id: todo.id,
              title: todo.title,
              type: 'todo',
              description: todo.description,
              date: todo.due_date ? `Due: ${new Date(todo.due_date).toLocaleDateString()}` : undefined,
              tags: todo.tags,
              status: todo.status,
              priority: todo.priority,
              onClick: () => handleTodoClick(todo.id)
            }))}
            onItemClick={handleTodoClick}
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
        <MenuItem disabled>
          <Typography variant="subtitle2">Status</Typography>
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, status: 'active' });
          setFilterMenuAnchor(null);
        }}>
          Active Tasks
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, status: 'completed' });
          setFilterMenuAnchor(null);
        }}>
          Completed Tasks
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, status: 'canceled' });
          setFilterMenuAnchor(null);
        }}>
          Canceled Tasks
        </MenuItem>
        <Divider />
        <MenuItem disabled>
          <Typography variant="subtitle2">Priority</Typography>
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, priority: 'high' });
          setFilterMenuAnchor(null);
        }}>
          High Priority
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, priority: 'medium' });
          setFilterMenuAnchor(null);
        }}>
          Medium Priority
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, priority: 'low' });
          setFilterMenuAnchor(null);
        }}>
          Low Priority
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => {
          setFilters({
            sortBy: filters.sortBy,
            sortDirection: filters.sortDirection
          });
          setFilterMenuAnchor(null);
        }}>
          Clear All Filters
        </MenuItem>
      </Menu>
      
      {/* Sort Menu */}
      <Menu
        anchorEl={sortMenuAnchor}
        open={Boolean(sortMenuAnchor)}
        onClose={() => setSortMenuAnchor(null)}
      >
        <MenuItem onClick={() => {
          setFilters({ ...filters, sortBy: 'due_date', sortDirection: 'asc' });
          setSortMenuAnchor(null);
        }}>
          Due Date (Earliest First)
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, sortBy: 'due_date', sortDirection: 'desc' });
          setSortMenuAnchor(null);
        }}>
          Due Date (Latest First)
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => {
          setFilters({ ...filters, sortBy: 'priority', sortDirection: 'desc' });
          setSortMenuAnchor(null);
        }}>
          Priority (High to Low)
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, sortBy: 'priority', sortDirection: 'asc' });
          setSortMenuAnchor(null);
        }}>
          Priority (Low to High)
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => {
          setFilters({ ...filters, sortBy: 'title', sortDirection: 'asc' });
          setSortMenuAnchor(null);
        }}>
          Title (A-Z)
        </MenuItem>
        <MenuItem onClick={() => {
          setFilters({ ...filters, sortBy: 'modified', sortDirection: 'desc' });
          setSortMenuAnchor(null);
        }}>
          Recently Modified
        </MenuItem>
      </Menu>
      
      {/* Action Menu */}
      <Menu
        anchorEl={actionMenuAnchor}
        open={Boolean(actionMenuAnchor)}
        onClose={() => {
          setActionMenuAnchor(null);
          setSelectedTodoId(null);
        }}
      >
        <MenuItem onClick={() => {
          if (!selectedTodoId) return;
          handleToggleStatus(selectedTodoId);
          setActionMenuAnchor(null);
        }}>
          <ListItemIcon>
            <CheckCircleIcon fontSize="small" />
          </ListItemIcon>
          Toggle Completion
        </MenuItem>
        <MenuItem onClick={() => {
          setActionMenuAnchor(null);
          if (selectedTodoId) {
            navigate(`/content/${selectedTodoId}/edit`);
          }
        }}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          Edit
        </MenuItem>
        <MenuItem onClick={handleDeleteTodo}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          Delete
        </MenuItem>
      </Menu>
      
      {/* Create Todo Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>Create New Todo</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Title"
              fullWidth
              value={newTodoData.title}
              onChange={(e) => setNewTodoData({ ...newTodoData, title: e.target.value })}
              autoFocus
            />
            
            <TextField
              label="Description"
              multiline
              rows={4}
              fullWidth
              value={newTodoData.description}
              onChange={(e) => setNewTodoData({ ...newTodoData, description: e.target.value })}
            />
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={newTodoData.priority}
                    label="Priority"
                    onChange={(e) => setNewTodoData({ 
                      ...newTodoData, 
                      priority: e.target.value as string 
                    })}
                  >
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="low">Low</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Due Date"
                  type="date"
                  fullWidth
                  value={newTodoData.due_date}
                  onChange={(e) => setNewTodoData({ ...newTodoData, due_date: e.target.value })}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>
            </Grid>
            
            <TextField
              label="Tags (comma separated)"
              fullWidth
              value={newTodoData.tags.join(', ')}
              onChange={(e) => setNewTodoData({ 
                ...newTodoData, 
                tags: e.target.value.split(',').map(tag => tag.trim()).filter(Boolean)
              })}
            />
            
            <FormControlLabel
              control={
                <Switch 
                  checked={newTodoData.status === 'completed'}
                  onChange={(e) => setNewTodoData({
                    ...newTodoData,
                    status: e.target.checked ? 'completed' : 'active'
                  })}
                  color="primary"
                />
              }
              label="Mark as completed"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateTodo} 
            variant="contained" 
            color="primary"
            disabled={!newTodoData.title.trim()}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TodosPage; 