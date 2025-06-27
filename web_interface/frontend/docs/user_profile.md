# User Profile Management

The Knowledge Base System provides comprehensive user profile management features. This document outlines the available profile management capabilities and how to use them.

## Profile Overview

The User Profile page allows users to manage their personal information, preferences, and security settings in a central location. The profile is organized into three main sections:

1. **Personal Information**: Basic user details and preferences
2. **Preferences**: User interface and content preferences
3. **Security**: Password and session management

## Personal Information

The Personal Information tab allows users to manage their basic profile data:

- **Display Name**: The name displayed throughout the application
- **Email**: The primary email address associated with the account
- **Bio**: A short user biography or description
- **Location**: Geographic location information
- **Tags & Interests**: User-specified tags representing interests or expertise areas

### Managing Tags

Users can add and remove tags to represent their interests:

1. To add a tag, type the tag name in the "Add tag" field and press Enter
2. To remove a tag, click the delete (×) icon on any tag

Tags help improve content recommendations and can be used to categorize content.

## Preferences

The Preferences tab provides options to customize the user experience:

- **Display Preferences**: 
  - Dark Mode: Toggle between light and dark interface themes
  
- **Interface Preferences**:
  - Keyboard Shortcuts: Enable or disable keyboard shortcuts
  
- **Content Preferences**:
  - Auto-tagging: Enable automatic tag suggestions for new content

### Keyboard Shortcuts

When keyboard shortcuts are enabled, users can view available shortcuts in the Preferences tab. For detailed information, see the [Keyboard Shortcuts](./keyboard_shortcuts.md) documentation.

## Security

The Security tab provides options for managing account security:

- **Password Management**:
  - Change Password: Update the user account password
  - Password requirements are displayed during the change process
  
- **Two-Factor Authentication**:
  - Enable/disable two-factor authentication for additional security
  
- **Session Management**:
  - View active sessions
  - Log out from other sessions

## Profile Picture

Users can update their profile picture by:

1. Clicking on their current avatar in the profile overview
2. Selecting a new image file from their device
3. Cropping the image if needed
4. Saving the changes

## Responsive Design

The user profile interface is fully responsive and optimized for:

- **Desktop**: Full multi-column layout
- **Tablet**: Adaptive layout with adjusted columns
- **Mobile**: Single column layout with collapsible sections

## API Integration

The user profile integrates with the following API endpoints:

- `GET /user/profile` - Retrieve user profile data
- `PUT /user/profile` - Update user profile information
- `POST /user/avatar` - Upload or update profile picture
- `GET /user/preferences` - Retrieve user preferences
- `PUT /user/preferences` - Update user preferences
- `PUT /user/password` - Change user password
- `GET /user/sessions` - List active user sessions
- `POST /user/sessions/terminate-others` - End other active sessions

## Implementation Components

The user profile functionality is implemented across several components:

- `Profile.tsx`: Main user profile page component
- `ProfileHeader.tsx`: User information display component
- `PreferencesTab.tsx`: User preference management
- `SecurityTab.tsx`: Security settings management
- `api.ts`: API service methods for user profile operations

## Data Privacy

The profile management features are designed with privacy in mind:

- Sensitive information is never exposed in URLs
- Profile updates are done securely via API calls
- Session tokens are securely stored and managed
- Password changes require current password verification 