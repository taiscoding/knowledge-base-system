import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Auth Context
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Layouts
import MainLayout from './layouts/MainLayout';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
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
import OrganizationPage from './pages/Organization';

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

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();
  
  if (isLoading) {
    // You could render a loading spinner here
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    // Redirect to login page but save the current location
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  return <>{children}</>;
};

// Wrap page components with PageTransition
const TransitionPage = ({ Component, transitionType }: { Component: React.ComponentType<any>; transitionType?: 'fade' | 'slide' | 'scale' | 'none' }) => (
  <PageTransition transitionType={transitionType}>
    <Component />
  </PageTransition>
);

const AppRoutes: React.FC = () => {
  const [mounted, setMounted] = useState(false);

  // Set mounted state on initial render
  // This helps prevent animation on first page load
  useEffect(() => {
    setMounted(true);
  }, []);
  
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* Protected routes */}
      <Route path="/" element={
        <ProtectedRoute>
          <MainLayout />
        </ProtectedRoute>
      }>
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
        <Route path="organization" element={
          mounted ? <TransitionPage Component={OrganizationPage} transitionType="slide" /> : <OrganizationPage />
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
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App; 