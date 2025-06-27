import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Profile from '../Profile';
import '@testing-library/jest-dom';

// Mock the API service
jest.mock('../../services/api', () => ({
  getUserProfile: jest.fn().mockResolvedValue({
    data: {
      displayName: 'Test User',
      email: 'test@example.com',
      bio: 'Test bio',
      location: 'Test Location',
      tags: ['Test', 'Jest'],
      dateJoined: '2023-01-01'
    }
  }),
  updateUserProfile: jest.fn().mockResolvedValue({ success: true })
}));

describe('Profile Component', () => {
  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <Profile />
      </BrowserRouter>
    );
  };

  it('renders the profile page title', () => {
    renderComponent();
    expect(screen.getByText('My Profile')).toBeInTheDocument();
  });

  it('displays profile information', () => {
    renderComponent();
    expect(screen.getByText('User Name')).toBeInTheDocument();
    expect(screen.getByText('user@example.com')).toBeInTheDocument();
  });

  it('shows tabs for different profile sections', () => {
    renderComponent();
    expect(screen.getByText('Personal Info')).toBeInTheDocument();
    expect(screen.getByText('Preferences')).toBeInTheDocument();
    expect(screen.getByText('Security')).toBeInTheDocument();
  });

  it('allows editing display name', async () => {
    renderComponent();
    
    // Find the display name input
    const displayNameInput = screen.getByLabelText('Display Name');
    expect(displayNameInput).toBeInTheDocument();
    
    // Change the value
    fireEvent.change(displayNameInput, { target: { value: 'New User Name' } });
    
    // Check if the input value changed
    expect(displayNameInput).toHaveValue('New User Name');
  });

  it('shows success message after saving profile', async () => {
    renderComponent();
    
    // Find and click the save button
    const saveButton = screen.getByText('Save Profile');
    fireEvent.click(saveButton);
    
    // Wait for the success message
    await waitFor(() => {
      expect(screen.getByText('Profile updated successfully')).toBeInTheDocument();
    });
  });

  it('switches between tabs', () => {
    renderComponent();
    
    // Initial tab should be Personal Info
    expect(screen.getByLabelText('Display Name')).toBeInTheDocument();
    
    // Click Preferences tab
    fireEvent.click(screen.getByText('Preferences'));
    expect(screen.getByText('Display Preferences')).toBeInTheDocument();
    
    // Click Security tab
    fireEvent.click(screen.getByText('Security'));
    expect(screen.getByText('Change Password')).toBeInTheDocument();
  });

  it('allows adding and removing tags', () => {
    renderComponent();
    
    // Get the count of initial tags
    const initialTags = screen.getAllByRole('button', { name: /Research|Notes|Organization/ });
    const initialTagCount = initialTags.length;
    
    // Add a new tag
    const tagInput = screen.getByPlaceholderText('Enter tag and press Enter');
    fireEvent.change(tagInput, { target: { value: 'NewTag' } });
    fireEvent.keyDown(tagInput, { key: 'Enter', code: 'Enter' });
    
    // Check if a new tag was added
    const updatedTags = screen.getAllByRole('button', { name: /Research|Notes|Organization|NewTag/ });
    expect(updatedTags.length).toBe(initialTagCount + 1);
    expect(screen.getByText('NewTag')).toBeInTheDocument();
    
    // Remove a tag
    const deleteButtons = screen.getAllByRole('button', { name: /cancel/i });
    fireEvent.click(deleteButtons[0]);
    
    // Check if a tag was removed
    const finalTags = screen.getAllByRole('button', { name: /Research|Notes|Organization|NewTag/ });
    expect(finalTags.length).toBe(initialTagCount);
  });
}); 