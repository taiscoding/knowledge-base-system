# Knowledge Base System - Web Interface

This directory contains the web interface for the Knowledge Base System, providing a modern and user-friendly way to interact with the knowledge management platform.

## Architecture

The web interface follows a client-server architecture:

- **Backend**: FastAPI-based API server providing access to all Knowledge Base functionality
- **Frontend**: React application with TypeScript for type safety and better developer experience
- **UI Framework**: Material-UI for consistent and responsive design

## Directory Structure

```
web_interface/
├── backend/           # FastAPI server
│   ├── api/           # API endpoints
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic
│   └── utils/         # Utilities
├── frontend/          # React application
│   ├── public/        # Static assets
│   ├── src/           # Source code
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── layouts/     # Page layouts
│   │   ├── services/    # API client services
│   │   ├── types/       # TypeScript definitions
│   │   └── utils/       # Utility functions
│   └── docs/          # Frontend documentation
└── README.md          # This file
```

## Features

- **Dashboard**: Overview of knowledge base statistics and recent activity
- **Content Management**: Create, edit, and organize all content types (notes, todos, events)
- **Search**: Advanced semantic search with suggestions and filtering
- **Rich Text Editing**: Comprehensive content editor with formatting
- **Knowledge Graph**: Interactive visualization of content relationships
- **Natural Language Interface**: Interact with your knowledge base using natural language
- **User Profile**: Comprehensive profile and preferences management
- **Responsive Design**: Fully adaptive for desktop, tablet, and mobile
- **Keyboard Shortcuts**: Productivity enhancements with keyboard navigation
- **Animations**: Smooth transitions between pages and content changes
- **Privacy Controls**: User-friendly interface for privacy settings

## Getting Started

### Requirements

- Python 3.8+
- Node.js 16+
- npm or yarn

### Setup

1. Install backend dependencies:
   ```bash
   cd web_interface/backend
   pip install -r requirements.txt
   ```

2. Install frontend dependencies:
   ```bash
   cd web_interface/frontend
   npm install
   ```

3. Start the development servers:
   ```bash
   # Start backend server
   cd web_interface/backend
   python main.py

   # Start frontend development server
   cd web_interface/frontend
   npm start
   ```

4. Open your browser at [http://localhost:3000](http://localhost:3000)

## User Guide

The web interface provides several ways to interact with your knowledge base:

- **Navigation Sidebar**: Access different sections of the application
- **Search Bar**: Quick access to content search
- **Keyboard Shortcuts**: Press `Ctrl+?` to view available keyboard shortcuts
- **User Menu**: Access profile and settings via the avatar icon

For detailed documentation on web interface features:
- [User Profile Documentation](frontend/docs/user_profile.md)
- [Keyboard Shortcuts Documentation](frontend/docs/keyboard_shortcuts.md)

## Development Guidelines

- Follow atomic design principles for components
- Maintain type safety with TypeScript
- Write unit tests for critical functionality
- Ensure all components respect privacy levels
- Use responsive design for mobile compatibility
- Add JSDoc comments to components and functions
- Follow existing patterns for new features

## Documentation

For more information about the web interface, see the documentation in the `frontend/docs` directory. 