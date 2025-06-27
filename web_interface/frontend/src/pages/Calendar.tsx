import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Button,
  IconButton,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Stack,
  Chip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import TodayIcon from '@mui/icons-material/Today';
import EventIcon from '@mui/icons-material/Event';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import ViewAgendaIcon from '@mui/icons-material/ViewAgenda';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import CalendarViewWeekIcon from '@mui/icons-material/CalendarViewWeek';
import CalendarViewDayIcon from '@mui/icons-material/CalendarViewDay';

import { format, addMonths, addWeeks, addDays, startOfMonth, endOfMonth, 
         startOfWeek, endOfWeek, eachDayOfInterval, isSameMonth, isSameDay,
         differenceInMinutes, parse, parseISO } from 'date-fns';

// Components
import LoadingSpinner from '../components/ui/LoadingSpinner';

// API
import api from '../services/api';

// Types
interface CalendarEvent {
  id: string;
  title: string;
  description: string;
  datetime: string;
  duration: string;
  tags: string[];
  created: string;
  modified: string;
  type: string;
  _content_type: string;
}

interface EventDialogData {
  title: string;
  description: string;
  date: string;
  time: string;
  duration: string;
  tags: string[];
}

const CalendarPage: React.FC = () => {
  const navigate = useNavigate();
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // View state
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewType, setViewType] = useState<'month' | 'week' | 'day' | 'agenda'>('month');
  
  // Dialog state
  const [eventDialogOpen, setEventDialogOpen] = useState(false);
  const [eventDialogData, setEventDialogData] = useState<EventDialogData>({
    title: '',
    description: '',
    date: format(new Date(), 'yyyy-MM-dd'),
    time: format(new Date(), 'HH:mm'),
    duration: '60',
    tags: []
  });
  
  // Load events on component mount
  useEffect(() => {
    fetchEvents();
  }, []);
  
  const fetchEvents = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.getContentByType('calendar');
      setEvents(response.items || []);
    } catch (error) {
      console.error('Error fetching events:', error);
      setError('Failed to load events. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreateEvent = async () => {
    try {
      // Combine date and time for datetime
      const datetimeStr = `${eventDialogData.date}T${eventDialogData.time}`;
      
      const result = await api.createContent({
        title: eventDialogData.title,
        description: eventDialogData.description,
        datetime: datetimeStr,
        duration: `${eventDialogData.duration}min`,
        tags: eventDialogData.tags,
        type: 'calendar'
      });
      
      // Add new event to the list
      setEvents([...events, result]);
      
      // Close dialog and reset form
      setEventDialogOpen(false);
      setEventDialogData({
        title: '',
        description: '',
        date: format(new Date(), 'yyyy-MM-dd'),
        time: format(new Date(), 'HH:mm'),
        duration: '60',
        tags: []
      });
      
    } catch (error) {
      console.error('Error creating event:', error);
      setError('Failed to create event. Please try again.');
    }
  };
  
  const handleDeleteEvent = async (id: string) => {
    try {
      await api.deleteContent(id);
      
      // Remove from list
      setEvents(events.filter(event => event.id !== id));
      
    } catch (error) {
      console.error('Error deleting event:', error);
      setError('Failed to delete event. Please try again.');
    }
  };
  
  const handleEventClick = (id: string) => {
    navigate(`/content/${id}`);
  };
  
  // Renders a single day cell in the month view
  const renderDayCell = (day: Date) => {
    const dayEvents = events.filter(event => {
      const eventDate = parseISO(event.datetime);
      return isSameDay(eventDate, day);
    });
    
    const isCurrentMonth = isSameMonth(day, currentDate);
    const isToday = isSameDay(day, new Date());
    
    return (
      <Box
        sx={{
          height: 120,
          border: '1px solid',
          borderColor: 'divider',
          backgroundColor: isCurrentMonth ? 'background.paper' : 'action.hover',
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        <Box 
          sx={{ 
            p: 0.5, 
            backgroundColor: isToday ? 'primary.main' : isCurrentMonth ? 'transparent' : 'action.hover',
            color: isToday ? 'primary.contrastText' : isCurrentMonth ? 'text.primary' : 'text.secondary',
            fontWeight: isToday ? 'bold' : 'normal',
            textAlign: 'right',
            borderBottom: '1px solid',
            borderColor: 'divider'
          }}
        >
          {format(day, 'd')}
        </Box>
        
        <Box sx={{ p: 0.5, overflowY: 'auto', maxHeight: 90 }}>
          {dayEvents.slice(0, 3).map(event => (
            <Box 
              key={event.id} 
              sx={{ 
                backgroundColor: 'primary.light', 
                color: 'primary.contrastText',
                p: 0.5,
                mb: 0.5,
                borderRadius: 1,
                fontSize: '0.75rem',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                cursor: 'pointer'
              }}
              onClick={() => handleEventClick(event.id)}
            >
              {format(parseISO(event.datetime), 'HH:mm')} {event.title}
            </Box>
          ))}
          {dayEvents.length > 3 && (
            <Typography variant="caption" color="text.secondary">
              +{dayEvents.length - 3} more
            </Typography>
          )}
        </Box>
      </Box>
    );
  };
  
  // Render month view
  const renderMonthView = () => {
    const monthStart = startOfMonth(currentDate);
    const monthEnd = endOfMonth(currentDate);
    const startDate = startOfWeek(monthStart);
    const endDate = endOfWeek(monthEnd);
    
    const days = eachDayOfInterval({ start: startDate, end: endDate });
    
    // Create rows of 7 days
    const rows = [];
    let cells = [];
    
    days.forEach((day, i) => {
      cells.push(
        <Grid item xs key={day.toString()}>
          {renderDayCell(day)}
        </Grid>
      );
      
      if (cells.length === 7 || i === days.length - 1) {
        rows.push(
          <Grid container spacing={0} key={day.toString()}>
            {cells}
          </Grid>
        );
        cells = [];
      }
    });
    
    return (
      <Box sx={{ mt: 2 }}>
        {/* Day headers */}
        <Grid container spacing={0}>
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <Grid item xs key={day}>
              <Box 
                sx={{ 
                  textAlign: 'center',
                  p: 1,
                  fontWeight: 'bold',
                  backgroundColor: 'grey.100',
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                {day}
              </Box>
            </Grid>
          ))}
        </Grid>
        
        {/* Calendar grid */}
        {rows}
      </Box>
    );
  };
  
  // Render week view
  const renderWeekView = () => {
    const weekStart = startOfWeek(currentDate);
    const weekEnd = endOfWeek(currentDate);
    const days = eachDayOfInterval({ start: weekStart, end: weekEnd });
    
    return (
      <Box sx={{ mt: 2 }}>
        <Grid container spacing={2}>
          {days.map((day) => {
            const dayEvents = events.filter(event => {
              const eventDate = parseISO(event.datetime);
              return isSameDay(eventDate, day);
            });
            
            const isToday = isSameDay(day, new Date());
            
            return (
              <Grid item xs={12} key={day.toString()}>
                <Paper 
                  sx={{ 
                    p: 2,
                    backgroundColor: isToday ? 'primary.light' : 'background.paper',
                  }}
                >
                  <Typography 
                    variant="subtitle1" 
                    sx={{ 
                      fontWeight: isToday ? 'bold' : 'normal',
                      color: isToday ? 'primary.contrastText' : 'text.primary' 
                    }}
                  >
                    {format(day, 'EEEE, MMMM d')}
                  </Typography>
                  
                  <Divider sx={{ my: 1 }} />
                  
                  {dayEvents.length > 0 ? (
                    <Stack spacing={1}>
                      {dayEvents.map(event => (
                        <Paper
                          key={event.id}
                          sx={{ 
                            p: 1, 
                            display: 'flex',
                            alignItems: 'flex-start',
                            cursor: 'pointer',
                            '&:hover': { bgcolor: 'action.hover' }
                          }}
                          onClick={() => handleEventClick(event.id)}
                        >
                          <Box sx={{ mr: 1 }}>
                            <AccessTimeIcon color="action" fontSize="small" />
                          </Box>
                          <Box sx={{ flexGrow: 1 }}>
                            <Typography variant="subtitle2">
                              {format(parseISO(event.datetime), 'h:mm a')}
                              {event.duration && ` · ${event.duration}`}
                            </Typography>
                            <Typography variant="body2">{event.title}</Typography>
                            {event.description && (
                              <Typography variant="body2" color="text.secondary" noWrap>
                                {event.description}
                              </Typography>
                            )}
                          </Box>
                        </Paper>
                      ))}
                    </Stack>
                  ) : (
                    <Typography color="text.secondary">No events scheduled</Typography>
                  )}
                </Paper>
              </Grid>
            );
          })}
        </Grid>
      </Box>
    );
  };
  
  // Render day view
  const renderDayView = () => {
    const dayEvents = events.filter(event => {
      const eventDate = parseISO(event.datetime);
      return isSameDay(eventDate, currentDate);
    });
    
    // Sort by time
    dayEvents.sort((a, b) => {
      const timeA = parseISO(a.datetime);
      const timeB = parseISO(b.datetime);
      return timeA.getTime() - timeB.getTime();
    });
    
    const isToday = isSameDay(currentDate, new Date());
    
    return (
      <Box sx={{ mt: 2 }}>
        <Paper sx={{ p: 2 }}>
          <Typography 
            variant="h5" 
            gutterBottom
            sx={{ 
              color: isToday ? 'primary.main' : 'text.primary',
              fontWeight: isToday ? 'bold' : 'normal'
            }}
          >
            {isToday ? 'Today, ' : ''}{format(currentDate, 'EEEE, MMMM d, yyyy')}
          </Typography>
          
          <Divider sx={{ my: 2 }} />
          
          {dayEvents.length > 0 ? (
            <Stack spacing={2}>
              {dayEvents.map(event => {
                // Parse duration to display end time
                let durationMinutes = 60; // default 1 hour
                if (event.duration) {
                  const durationMatch = event.duration.match(/(\d+)/);
                  if (durationMatch) {
                    durationMinutes = parseInt(durationMatch[1]);
                  }
                }
                
                const startTime = parseISO(event.datetime);
                const endTime = new Date(startTime.getTime() + durationMinutes * 60000);
                
                return (
                  <Paper
                    key={event.id}
                    elevation={2}
                    sx={{ 
                      p: 2, 
                      borderLeft: '4px solid',
                      borderColor: 'primary.main',
                      cursor: 'pointer',
                      '&:hover': { bgcolor: 'action.hover' }
                    }}
                    onClick={() => handleEventClick(event.id)}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle1">
                        {event.title}
                      </Typography>
                      <Box>
                        <IconButton 
                          size="small" 
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/content/${event.id}/edit`);
                          }}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteEvent(event.id);
                          }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <AccessTimeIcon fontSize="small" sx={{ mr: 1 }} />
                      <Typography variant="body2">
                        {format(startTime, 'h:mm a')} - {format(endTime, 'h:mm a')}
                        {event.duration && ` (${event.duration})`}
                      </Typography>
                    </Box>
                    
                    {event.description && (
                      <Typography variant="body2" color="text.secondary">
                        {event.description}
                      </Typography>
                    )}
                    
                    {event.tags && event.tags.length > 0 && (
                      <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {event.tags.map((tag, i) => (
                          <Chip
                            key={i}
                            label={tag}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    )}
                  </Paper>
                );
              })}
            </Stack>
          ) : (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography color="text.secondary" gutterBottom>No events scheduled for this day</Typography>
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={() => {
                  setEventDialogData({
                    ...eventDialogData,
                    date: format(currentDate, 'yyyy-MM-dd')
                  });
                  setEventDialogOpen(true);
                }}
                sx={{ mt: 2 }}
              >
                Add Event
              </Button>
            </Box>
          )}
        </Paper>
      </Box>
    );
  };
  
  // Render agenda view (list of upcoming events)
  const renderAgendaView = () => {
    // Sort by date
    const sortedEvents = [...events].sort((a, b) => {
      const dateA = parseISO(a.datetime);
      const dateB = parseISO(b.datetime);
      return dateA.getTime() - dateB.getTime();
    });
    
    // Group by date
    const groupedEvents: {[key: string]: CalendarEvent[]} = {};
    
    sortedEvents.forEach(event => {
      const eventDate = parseISO(event.datetime);
      const dateKey = format(eventDate, 'yyyy-MM-dd');
      
      if (!groupedEvents[dateKey]) {
        groupedEvents[dateKey] = [];
      }
      
      groupedEvents[dateKey].push(event);
    });
    
    return (
      <Box sx={{ mt: 2 }}>
        {Object.keys(groupedEvents).length > 0 ? (
          Object.keys(groupedEvents).map(dateKey => {
            const date = parseISO(dateKey);
            const isToday = isSameDay(date, new Date());
            
            return (
              <Paper key={dateKey} sx={{ mb: 2, overflow: 'hidden' }}>
                <Box 
                  sx={{ 
                    p: 2, 
                    backgroundColor: isToday ? 'primary.main' : 'grey.100',
                    color: isToday ? 'primary.contrastText' : 'text.primary',
                  }}
                >
                  <Typography variant="subtitle1" fontWeight="bold">
                    {isToday ? 'Today, ' : ''}{format(date, 'EEEE, MMMM d, yyyy')}
                  </Typography>
                </Box>
                
                <Stack divider={<Divider />}>
                  {groupedEvents[dateKey].map(event => {
                    const startTime = parseISO(event.datetime);
                    
                    return (
                      <Box
                        key={event.id}
                        sx={{ 
                          p: 2,
                          cursor: 'pointer',
                          '&:hover': { bgcolor: 'action.hover' }
                        }}
                        onClick={() => handleEventClick(event.id)}
                      >
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={3} md={2}>
                            <Typography variant="body2" fontWeight="medium">
                              {format(startTime, 'h:mm a')}
                            </Typography>
                            {event.duration && (
                              <Typography variant="caption" color="text.secondary">
                                {event.duration}
                              </Typography>
                            )}
                          </Grid>
                          
                          <Grid item xs={12} sm={9} md={10}>
                            <Typography variant="subtitle2">{event.title}</Typography>
                            {event.description && (
                              <Typography variant="body2" color="text.secondary">
                                {event.description}
                              </Typography>
                            )}
                            
                            {event.tags && event.tags.length > 0 && (
                              <Box sx={{ mt: 0.5, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                {event.tags.map((tag, i) => (
                                  <Chip
                                    key={i}
                                    label={tag}
                                    size="small"
                                    variant="outlined"
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                  />
                                ))}
                              </Box>
                            )}
                          </Grid>
                        </Grid>
                      </Box>
                    );
                  })}
                </Stack>
              </Paper>
            );
          })
        ) : (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>No events scheduled</Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Create a new event to get started
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={() => setEventDialogOpen(true)}
              sx={{ mt: 2 }}
            >
              Add Event
            </Button>
          </Paper>
        )}
      </Box>
    );
  };
  
  const renderCalendarHeader = () => {
    let title = '';
    let navigatePrevious;
    let navigateNext;
    
    switch (viewType) {
      case 'month':
        title = format(currentDate, 'MMMM yyyy');
        navigatePrevious = () => setCurrentDate(addMonths(currentDate, -1));
        navigateNext = () => setCurrentDate(addMonths(currentDate, 1));
        break;
      case 'week':
        const weekStart = startOfWeek(currentDate);
        const weekEnd = endOfWeek(currentDate);
        title = `${format(weekStart, 'MMM d')} - ${format(weekEnd, 'MMM d, yyyy')}`;
        navigatePrevious = () => setCurrentDate(addWeeks(currentDate, -1));
        navigateNext = () => setCurrentDate(addWeeks(currentDate, 1));
        break;
      case 'day':
        title = format(currentDate, 'EEEE, MMMM d, yyyy');
        navigatePrevious = () => setCurrentDate(addDays(currentDate, -1));
        navigateNext = () => setCurrentDate(addDays(currentDate, 1));
        break;
      case 'agenda':
        title = 'Upcoming Events';
        navigatePrevious = () => {}; // Not used in agenda view
        navigateNext = () => {}; // Not used in agenda view
        break;
    }
    
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography variant="h5" component="h1" sx={{ mr: 2 }}>
            {title}
          </Typography>
          
          {viewType !== 'agenda' && (
            <>
              <IconButton onClick={navigatePrevious}>
                <ChevronLeftIcon />
              </IconButton>
              <IconButton onClick={navigateNext}>
                <ChevronRightIcon />
              </IconButton>
              <Button 
                startIcon={<TodayIcon />} 
                variant="outlined" 
                sx={{ ml: 1 }}
                onClick={() => setCurrentDate(new Date())}
              >
                Today
              </Button>
            </>
          )}
        </Box>
        
        <Box>
          <Tabs 
            value={viewType} 
            onChange={(_, newValue) => setViewType(newValue)}
            aria-label="calendar view type"
          >
            <Tab 
              icon={<CalendarMonthIcon />} 
              label="Month" 
              value="month" 
              aria-label="month view"
            />
            <Tab 
              icon={<CalendarViewWeekIcon />} 
              label="Week" 
              value="week" 
              aria-label="week view"
            />
            <Tab 
              icon={<CalendarViewDayIcon />} 
              label="Day" 
              value="day" 
              aria-label="day view"
            />
            <Tab 
              icon={<ViewAgendaIcon />} 
              label="Agenda" 
              value="agenda" 
              aria-label="agenda view"
            />
          </Tabs>
        </Box>
      </Box>
    );
  };
  
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">Calendar</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setEventDialogOpen(true)}
        >
          New Event
        </Button>
      </Box>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        {renderCalendarHeader()}
      </Paper>
      
      {loading ? (
        <LoadingSpinner />
      ) : error ? (
        <Typography color="error">{error}</Typography>
      ) : (
        <>
          {viewType === 'month' && renderMonthView()}
          {viewType === 'week' && renderWeekView()}
          {viewType === 'day' && renderDayView()}
          {viewType === 'agenda' && renderAgendaView()}
        </>
      )}
      
      {/* Create Event Dialog */}
      <Dialog 
        open={eventDialogOpen} 
        onClose={() => setEventDialogOpen(false)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>Create New Event</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Title"
              fullWidth
              value={eventDialogData.title}
              onChange={(e) => setEventDialogData({ ...eventDialogData, title: e.target.value })}
              autoFocus
            />
            
            <TextField
              label="Description"
              multiline
              rows={4}
              fullWidth
              value={eventDialogData.description}
              onChange={(e) => setEventDialogData({ ...eventDialogData, description: e.target.value })}
            />
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <TextField
                  label="Date"
                  type="date"
                  fullWidth
                  value={eventDialogData.date}
                  onChange={(e) => setEventDialogData({ ...eventDialogData, date: e.target.value })}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  label="Time"
                  type="time"
                  fullWidth
                  value={eventDialogData.time}
                  onChange={(e) => setEventDialogData({ ...eventDialogData, time: e.target.value })}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  label="Duration (minutes)"
                  type="number"
                  fullWidth
                  value={eventDialogData.duration}
                  onChange={(e) => setEventDialogData({ ...eventDialogData, duration: e.target.value })}
                  InputProps={{
                    inputProps: { min: 0 }
                  }}
                />
              </Grid>
            </Grid>
            
            <TextField
              label="Tags (comma separated)"
              fullWidth
              value={eventDialogData.tags.join(', ')}
              onChange={(e) => setEventDialogData({ 
                ...eventDialogData, 
                tags: e.target.value.split(',').map(tag => tag.trim()).filter(Boolean)
              })}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEventDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateEvent} 
            variant="contained" 
            color="primary"
            disabled={!eventDialogData.title.trim()}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CalendarPage; 