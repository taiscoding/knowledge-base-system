import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import InputAdornment from '@mui/material/InputAdornment';
import IconButton from '@mui/material/IconButton';
import SearchIcon from '@mui/icons-material/Search';
import MicIcon from '@mui/icons-material/Mic';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';

// Components
import ContentCard from '../components/content/ContentCard';
import VoiceInputDialog from '../components/input/VoiceInputDialog';

// API
import api from '../services/api';

// Example queries to help users get started
const EXAMPLE_QUERIES = [
  "Show me notes about project planning",
  "Find all high priority todos",
  "When is my next meeting?",
  "Create a new note about knowledge base",
  "What tasks are due this week?",
  "Show me the most recent content"
];

interface QueryResult {
  query: string;
  response: {
    text: string;
    action: {
      type: string;
      parameters: any;
    };
  };
  analysis: {
    intent: string;
    content_type: string;
    entities: any;
  };
  results?: any[];
}

const NaturalLanguage: React.FC = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [voiceDialogOpen, setVoiceDialogOpen] = useState(false);
  const [queryHistory, setQueryHistory] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await api.queryNaturalLanguage(query);
      setResult(response);
      
      // Add query to history
      setQueryHistory(prev => [query, ...prev].slice(0, 5));
      
      // If the action type is "search", also get search results
      if (response.analysis.intent === "search") {
        const searchQuery = response.response.action.parameters.search_term;
        const contentType = response.response.action.parameters.content_type;
        
        // Try semantic search first
        try {
          const searchResults = await api.semanticSearch(searchQuery, { 
            contentTypes: contentType ? [contentType] : undefined,
            topK: 5
          });
          
          setResult(prev => prev ? {
            ...prev,
            results: searchResults.results
          } : null);
        } catch (error) {
          console.error('Semantic search failed, falling back to regular search', error);
          
          // Fall back to regular search
          const searchResults = await api.searchContent(searchQuery, contentType);
          setResult(prev => prev ? {
            ...prev,
            results: searchResults.results
          } : null);
        }
      }
      
    } catch (error) {
      console.error('Error performing natural language query:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceInput = (text: string) => {
    setQuery(text);
    setVoiceDialogOpen(false);
    // Auto-submit voice input
    setTimeout(() => {
      document.getElementById('nlp-search-form')?.dispatchEvent(
        new Event('submit', { cancelable: true, bubbles: true })
      );
    }, 500);
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
    // Auto-submit example
    setTimeout(() => {
      document.getElementById('nlp-search-form')?.dispatchEvent(
        new Event('submit', { cancelable: true, bubbles: true })
      );
    }, 100);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Natural Language Query
      </Typography>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="body1" gutterBottom>
          Ask questions or give commands in natural language to interact with your knowledge base.
        </Typography>
        
        <form id="nlp-search-form" onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Enter your query"
            variant="outlined"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., 'Show me notes about project planning' or 'What tasks are due this week?'"
            disabled={loading}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="voice input"
                    onClick={() => setVoiceDialogOpen(true)}
                    edge="end"
                  >
                    <MicIcon />
                  </IconButton>
                  <IconButton
                    type="submit"
                    aria-label="search"
                    edge="end"
                    disabled={!query.trim() || loading}
                  >
                    {loading ? <CircularProgress size={24} /> : <SearchIcon />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
            sx={{ mb: 2 }}
          />
        </form>
        
        <Typography variant="subtitle2" sx={{ mb: 1 }}>Try these examples:</Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {EXAMPLE_QUERIES.map((example, index) => (
            <Chip
              key={index}
              label={example}
              onClick={() => handleExampleClick(example)}
              clickable
            />
          ))}
        </Box>
      </Paper>
      
      {/* Recent Queries */}
      {queryHistory.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>Recent queries:</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {queryHistory.map((q, index) => (
              <Chip
                key={index}
                label={q}
                size="small"
                variant="outlined"
                onClick={() => handleExampleClick(q)}
                clickable
              />
            ))}
          </Box>
        </Box>
      )}
      
      {/* Results */}
      {result && (
        <Box sx={{ mt: 3 }}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>Response</Typography>
            <Typography variant="body1">{result.response.text}</Typography>
            
            {result.analysis && (
              <Box sx={{ mt: 2 }}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  I understood this as: {result.analysis.intent === 'search' ? 'a search' : result.analysis.intent === 'create' ? 'a creation request' : 'a listing request'}
                  {result.analysis.content_type && ` for ${result.analysis.content_type}s`}
                </Typography>
              </Box>
            )}
          </Paper>
          
          {/* Search Results */}
          {result.results && result.results.length > 0 && (
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Results</Typography>
              <Grid container spacing={2}>
                {result.results.map((item, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <ContentCard 
                      content={item}
                      onClick={() => navigate(`/content/${item.content_id || item.id}`)}
                    />
                  </Grid>
                ))}
              </Grid>
            </Paper>
          )}
          
          {/* No Results */}
          {result.results && result.results.length === 0 && (
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1" align="center" color="text.secondary">
                No results found for this query.
              </Typography>
            </Paper>
          )}
        </Box>
      )}
      
      {/* Voice Input Dialog */}
      <VoiceInputDialog
        open={voiceDialogOpen}
        onClose={() => setVoiceDialogOpen(false)}
        onTranscription={handleVoiceInput}
      />
    </Box>
  );
};

export default NaturalLanguage; 