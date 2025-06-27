import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  TextField,
  Box,
  Grid,
  Button,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Autocomplete,
  Divider,
  CircularProgress,
  Pagination,
  ToggleButtonGroup,
  ToggleButton,
  Slider,
  FormGroup,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import TuneIcon from '@mui/icons-material/Tune';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewModuleIcon from '@mui/icons-material/ViewModule';
import ClearIcon from '@mui/icons-material/Clear';

import ContentCard from '../components/content/ContentCard';
import ContentList from '../components/content/ContentList';
import { Content, SearchOptions, ContentType, TagData } from '../types';
import api from '../services/api';

const Search: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [results, setResults] = useState<Content[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
  const [showFilters, setShowFilters] = useState<boolean>(false);
  const [page, setPage] = useState<number>(1);
  const [totalResults, setTotalResults] = useState<number>(0);
  const resultsPerPage = 12;
  
  // Filter state
  const [selectedContentTypes, setSelectedContentTypes] = useState<ContentType[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [dateRange, setDateRange] = useState<[Date | null, Date | null]>([null, null]);
  const [minSimilarity, setMinSimilarity] = useState<number>(0.7);
  const [popularCategories, setPopularCategories] = useState<string[]>([]);
  const [popularTags, setPopularTags] = useState<TagData[]>([]);
  const [semanticSearch, setSemanticSearch] = useState<boolean>(true);
  
  // Parse search params from URL on component mount
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const query = params.get('q');
    
    if (query) {
      setSearchQuery(query);
      performSearch(query);
    }
    
    // Load popular categories and tags
    loadFilterOptions();
  }, [location.search]);
  
  const loadFilterOptions = async () => {
    try {
      // This would be replaced with actual API calls
      const categoriesResponse = await api.request('/organization/categories/popular?limit=15');
      const tagsResponse = await api.getPopularTags();
      
      if (categoriesResponse.data) {
        setPopularCategories(categoriesResponse.data);
      }
      
      if (tagsResponse.tags) {
        const tagData = tagsResponse.tags.map((tag: string) => ({
          label: tag,
          value: tag
        }));
        setPopularTags(tagData);
      }
    } catch (err) {
      console.error('Error loading filter options:', err);
    }
  };
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (searchQuery.trim()) {
      // Update URL with search query
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      performSearch(searchQuery);
    }
  };
  
  const performSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // Prepare search options
      const searchOptions: SearchOptions = {
        contentTypes: selectedContentTypes.length > 0 ? selectedContentTypes : undefined,
        categories: selectedCategories.length > 0 ? selectedCategories : undefined,
        tags: selectedTags.length > 0 ? selectedTags : undefined,
        minSimilarity: semanticSearch ? minSimilarity : undefined
      };
      
      // Choose search method based on semanticSearch flag
      const response = semanticSearch 
        ? await api.semanticSearch(query, searchOptions)
        : await api.searchContent(query);
      
      if (response.data) {
        setResults(response.data.results || []);
        setTotalResults(response.data.total || response.data.results.length || 0);
      } else {
        setResults([]);
        setTotalResults(0);
      }
    } catch (err) {
      console.error('Error performing search:', err);
      setError('An error occurred while searching. Please try again.');
      setResults([]);
      setTotalResults(0);
    } finally {
      setLoading(false);
    }
  };
  
  const handleViewModeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newViewMode: 'list' | 'grid' | null,
  ) => {
    if (newViewMode !== null) {
      setViewMode(newViewMode);
    }
  };
  
  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
    window.scrollTo(0, 0);
  };
  
  const handleContentClick = (id: string) => {
    navigate(`/content/${id}`);
  };
  
  const handleClearSearch = () => {
    setSearchQuery('');
    setResults([]);
    setTotalResults(0);
    navigate('/search');
  };
  
  const handleClearFilters = () => {
    setSelectedContentTypes([]);
    setSelectedCategories([]);
    setSelectedTags([]);
    setDateRange([null, null]);
    setMinSimilarity(0.7);
  };
  
  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };
  
  // Display pagination if needed
  const paginationElement = totalResults > resultsPerPage && (
    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
      <Pagination 
        count={Math.ceil(totalResults / resultsPerPage)} 
        page={page} 
        onChange={handlePageChange}
        color="primary"
        size="large"
        showFirstButton
        showLastButton
      />
    </Box>
  );
  
  // Calculate results to show based on current page
  const paginatedResults = results.slice(
    (page - 1) * resultsPerPage,
    page * resultsPerPage
  );
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Search header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Search
        </Typography>
        
        <Paper component="form" onSubmit={handleSearch} sx={{ p: 1, display: 'flex', alignItems: 'center' }}>
          <IconButton aria-label="search" onClick={handleSearch}>
            <SearchIcon />
          </IconButton>
          <TextField
            fullWidth
            placeholder="Search for notes, todos, events..."
            variant="standard"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{ disableUnderline: true }}
          />
          {searchQuery && (
            <IconButton aria-label="clear search" onClick={handleClearSearch}>
              <ClearIcon />
            </IconButton>
          )}
          <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
          <Button 
            variant={showFilters ? "contained" : "outlined"}
            startIcon={<TuneIcon />}
            onClick={toggleFilters}
          >
            Filters
          </Button>
        </Paper>
      </Box>
      
      {/* Filters section */}
      {showFilters && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Search Filters</Typography>
            <Button size="small" onClick={handleClearFilters}>Clear All</Button>
          </Box>
          
          <Grid container spacing={3}>
            {/* Content type filter */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth size="small">
                <InputLabel id="content-type-label">Content Types</InputLabel>
                <Select
                  labelId="content-type-label"
                  multiple
                  value={selectedContentTypes}
                  onChange={(e) => setSelectedContentTypes(e.target.value as ContentType[])}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                  label="Content Types"
                >
                  <MenuItem value="note">Notes</MenuItem>
                  <MenuItem value="todo">Todos</MenuItem>
                  <MenuItem value="calendar">Events</MenuItem>
                  <MenuItem value="folder">Folders</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            {/* Category filter */}
            <Grid item xs={12} md={6}>
              <Autocomplete
                multiple
                options={popularCategories}
                value={selectedCategories}
                onChange={(_event, newValue) => setSelectedCategories(newValue)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Categories"
                    size="small"
                  />
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      label={option}
                      size="small"
                      {...getTagProps({ index })}
                    />
                  ))
                }
              />
            </Grid>
            
            {/* Tags filter */}
            <Grid item xs={12}>
              <Autocomplete
                multiple
                options={popularTags}
                getOptionLabel={(option) => option.label}
                value={selectedTags.map(tag => ({ label: tag, value: tag }))}
                onChange={(_event, newValue) => {
                  setSelectedTags(newValue.map(item => item.value));
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Tags"
                    size="small"
                  />
                )}
              />
            </Grid>
            
            {/* Semantic search toggle */}
            <Grid item xs={12} md={6}>
              <FormGroup>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={semanticSearch}
                      onChange={(e) => setSemanticSearch(e.target.checked)}
                    />
                  }
                  label="Use semantic search"
                />
              </FormGroup>
            </Grid>
            
            {/* Semantic search threshold */}
            {semanticSearch && (
              <Grid item xs={12} md={6}>
                <Typography id="similarity-slider" gutterBottom>
                  Minimum similarity: {Math.round(minSimilarity * 100)}%
                </Typography>
                <Slider
                  value={minSimilarity}
                  onChange={(_e, newValue) => setMinSimilarity(newValue as number)}
                  aria-labelledby="similarity-slider"
                  step={0.05}
                  marks
                  min={0.5}
                  max={1}
                />
              </Grid>
            )}
          </Grid>
        </Paper>
      )}
      
      {/* Results summary */}
      {searchQuery && !loading && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1" color="text.secondary">
            {totalResults > 0 
              ? `Found ${totalResults} result${totalResults !== 1 ? 's' : ''} for "${searchQuery}"`
              : `No results found for "${searchQuery}"`
            }
          </Typography>
        </Box>
      )}
      
      {/* View mode toggle */}
      {results.length > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={handleViewModeChange}
            aria-label="view mode"
            size="small"
          >
            <ToggleButton value="list" aria-label="list view">
              <ViewListIcon />
            </ToggleButton>
            <ToggleButton value="grid" aria-label="grid view">
              <ViewModuleIcon />
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>
      )}
      
      {/* Loading state */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      )}
      
      {/* Error message */}
      {error && !loading && (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="error">{error}</Typography>
          <Button sx={{ mt: 2 }} onClick={() => performSearch(searchQuery)}>
            Try Again
          </Button>
        </Paper>
      )}
      
      {/* Results - List view */}
      {!loading && viewMode === 'list' && results.length > 0 && (
        <ContentList
          items={paginatedResults.map(result => ({
            id: result.id,
            title: result.title,
            type: result.type,
            description: result.description,
            tags: result.tags,
            date: result.created,
            status: result.status,
            priority: result.priority
          }))}
          onItemClick={handleContentClick}
          emptyMessage="No search results found"
        />
      )}
      
      {/* Results - Grid view */}
      {!loading && viewMode === 'grid' && results.length > 0 && (
        <Grid container spacing={3}>
          {paginatedResults.map((result) => (
            <Grid item xs={12} sm={6} md={4} key={result.id}>
              <ContentCard
                content={result}
                onClick={() => handleContentClick(result.id)}
              />
            </Grid>
          ))}
        </Grid>
      )}
      
      {/* Empty state */}
      {!loading && results.length === 0 && searchQuery && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            No results found
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Try adjusting your search query or filters to find what you're looking for.
          </Typography>
          
          {showFilters && (
            <Button 
              sx={{ mt: 2 }}
              onClick={handleClearFilters}
            >
              Clear Filters
            </Button>
          )}
        </Paper>
      )}
      
      {/* Pagination */}
      {paginationElement}
    </Container>
  );
};

export default Search;
