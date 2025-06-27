import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AnimatePresence } from 'framer-motion';

// Layouts
import MainLayout from './layouts/MainLayout';

// Pages
import Dashboard from './pages/Dashboard';
import Notes from './pages/Notes';
import Todos from './pages/Todos';
import Calendar from './pages/Calendar';
import NaturalLanguage from './pages/NaturalLanguage';
import ContentView from './pages/ContentView';
import ContentEdit from './pages/ContentEdit';
import Search from './pages/Search';
import Graph from './pages/Graph';
import Settings from './pages/Settings';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';

// Components
import PageTransition from './components/ui/PageTransition';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#673ab7',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: "'Roboto', 'Helvetica', 'Arial', sans-serif",
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.08)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

// Wrap page components with PageTransition
const TransitionPage = ({ Component, transitionType }: { Component: React.ComponentType<any>; transitionType?: 'fade' | 'slide' | 'scale' | 'none' }) => (
  <PageTransition transitionType={transitionType}>
    <Component />
  </PageTransition>
);

const App: React.FC = () => {
  const [mounted, setMounted] = useState(false);

  // Set mounted state on initial render
  // This helps prevent animation on first page load
  useEffect(() => {
    setMounted(true);
  }, []);
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            {/* Redirect root to dashboard */}
            <Route index element={<Navigate to="/dashboard" replace />} />
            
            {/* Main routes */}
            <Route path="dashboard" element={
              mounted ? <TransitionPage Component={Dashboard} transitionType="fade" /> : <Dashboard />
            } />
            <Route path="notes" element={
              mounted ? <TransitionPage Component={Notes} transitionType="slide" /> : <Notes />
            } />
            <Route path="todos" element={
              mounted ? <TransitionPage Component={Todos} transitionType="slide" /> : <Todos />
            } />
            <Route path="calendar" element={
              mounted ? <TransitionPage Component={Calendar} transitionType="slide" /> : <Calendar />
            } />
            <Route path="nlp" element={
              mounted ? <TransitionPage Component={NaturalLanguage} transitionType="slide" /> : <NaturalLanguage />
            } />
            <Route path="graph" element={
              mounted ? <TransitionPage Component={Graph} transitionType="scale" /> : <Graph />
            } />
            <Route path="settings" element={
              mounted ? <TransitionPage Component={Settings} transitionType="fade" /> : <Settings />
            } />
            <Route path="profile" element={
              mounted ? <TransitionPage Component={Profile} transitionType="fade" /> : <Profile />
            } />
            
            {/* Content routes */}
            <Route path="content/:id" element={
              mounted ? <TransitionPage Component={ContentView} transitionType="fade" /> : <ContentView />
            } />
            <Route path="content/:id/edit" element={
              mounted ? <TransitionPage Component={ContentEdit} transitionType="fade" /> : <ContentEdit />
            } />
            
            {/* Search route */}
            <Route path="search" element={
              mounted ? <TransitionPage Component={Search} transitionType="fade" /> : <Search />
            } />
            
            {/* Catch all */}
            <Route path="*" element={
              mounted ? <TransitionPage Component={NotFound} transitionType="fade" /> : <NotFound />
            } />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App; 