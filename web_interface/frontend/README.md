# Knowledge Base System - Web Interface

A comprehensive web interface for the Knowledge Base System, built with React, TypeScript, and Material-UI.

## Features

- **Content Management**
  - View, create, edit, and delete knowledge content
  - Support for different content types (notes, todos, events, folders)
  - Rich text editing and formatting
  - Auto-tagging and metadata management

- **Organization & Navigation**
  - Folder structure visualization
  - Drag-and-drop content organization
  - Breadcrumb navigation for context awareness
  - Responsive layout with adaptive sidebar

- **Search & Discovery**
  - Both text-based and semantic search
  - Advanced filtering by content type, category, tags, and dates
  - Knowledge graph visualization of content relationships
  - Grid and list view options for search results

- **User Experience**
  - Privacy-focused design with user-controllable settings
  - Theme customization options
  - Responsive design for desktop and mobile
  - Comprehensive settings management

## Project Structure

```
/src
  /components            # Reusable UI components
    /content             # Content-related components
    /input               # Input-related components
    /navigation          # Navigation components
    /organization        # Organization components
    /ui                  # Generic UI components
    /visualization       # Visualization components
  /layouts               # Page layouts
  /pages                 # Page components
  /services              # API and utility services
  /types                 # TypeScript type definitions
  /utils                 # Utility functions
  /context               # React context providers
```

## Key Components

### Content Components

- **ContentCard**: Displays content in a card format for grid layouts
- **ContentList**: Displays content in a list format with metadata
- **ContentView**: Detailed view of individual content items
- **ContentEdit**: Form-based editor for creating and updating content
- **ContentTagging**: Interface for managing tags with auto-tagging support

### Visualization Components

- **KnowledgeGraph**: Force-directed graph visualization for content relationships
- **FolderHierarchy**: Tree visualization of folder structure

### Organization Components

- **DraggableContentList**: Drag-and-drop interface for content organization

### Page Components

- **Dashboard**: Overview of recent activity and statistics
- **Notes**: Management of note-type content items
- **Todos**: Task management with status toggling
- **Calendar**: Event management with different date views
- **Search**: Advanced search interface with filtering
- **Graph**: Knowledge graph exploration and visualization
- **Settings**: User preferences and privacy controls

## Setup and Development

### Prerequisites

- Node.js 16+ and npm/yarn
- TypeScript 5.0+

### Installation

```bash
# Install dependencies
npm install
# or
yarn install
```

### Development

```bash
# Start development server
npm start
# or
yarn start
```

### Building for Production

```bash
# Build production bundle
npm run build
# or
yarn build
```

## TypeScript Support

The project uses TypeScript for type safety. Key type definitions can be found in `/src/types/index.ts`, including:

- Content type definitions for different content types
- Component prop interfaces
- API request and response type definitions
- Utility types for state management

To fix TypeScript linting issues:

```bash
# Install missing type definitions
npm install --save-dev @types/react @types/react-dom @types/react-router-dom
```

## API Integration

The web interface communicates with the Knowledge Base backend API through the `services/api.ts` service. This service provides:

- CRUD operations for content management
- Search functionality (text and semantic)
- Natural language processing capabilities
- Privacy and security controls

## Contributing

For contributing to the web interface, please follow these guidelines:

1. Use TypeScript for all new components and functions
2. Follow the existing code organization patterns
3. Add JSDoc comments to components and functions
4. Maintain responsive design across all screen sizes
5. Ensure privacy controls are respected in all features

## Documentation

For more detailed documentation, see:

- [Component Usage Examples](docs/components.md)
- [API Integration Guide](docs/api-integration.md)
- [TypeScript Guidelines](docs/typescript.md)

## License

This project is licensed under the terms of the MIT license. 