import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import KeyboardShortcutsHelp from '../KeyboardShortcutsHelp';
import '@testing-library/jest-dom';

// Mock the keyboard shortcuts hook
jest.mock('../../../utils/keyboardShortcuts', () => ({
  useGlobalKeyboardShortcuts: jest.fn(() => ({
    shortcuts: [
      {
        key: 'k',
        ctrlKey: true,
        handler: jest.fn(),
        description: 'Open search',
      },
      {
        key: 'd',
        ctrlKey: true,
        handler: jest.fn(),
        description: 'Go to dashboard',
      }
    ]
  })),
  getAllShortcuts: jest.fn(() => [
    { shortcut: 'Ctrl+K', description: 'Open search' },
    { shortcut: 'Ctrl+D', description: 'Go to dashboard' }
  ]),
  formatShortcut: jest.fn((shortcut) => {
    const parts = [];
    if (shortcut.ctrlKey) parts.push('Ctrl');
    if (shortcut.altKey) parts.push('Alt');
    if (shortcut.shiftKey) parts.push('Shift');
    parts.push(shortcut.key.toUpperCase());
    return parts.join('+');
  })
}));

describe('KeyboardShortcutsHelp Component', () => {
  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <KeyboardShortcutsHelp />
      </BrowserRouter>
    );
  };

  it('is not visible by default', () => {
    renderComponent();
    expect(screen.queryByText('Keyboard Shortcuts')).not.toBeInTheDocument();
  });

  it('becomes visible when triggered by a custom event', async () => {
    renderComponent();
    
    // Dispatch the custom event to open the dialog
    window.dispatchEvent(new CustomEvent('show-shortcuts-help'));
    
    // Check if the dialog is displayed
    await waitFor(() => {
      expect(screen.getByText('Keyboard Shortcuts')).toBeInTheDocument();
    });
  });

  it('displays shortcut groups', async () => {
    renderComponent();
    
    // Open dialog
    window.dispatchEvent(new CustomEvent('show-shortcuts-help'));
    
    // Check if group titles are displayed
    await waitFor(() => {
      expect(screen.getByText('Navigation')).toBeInTheDocument();
      expect(screen.getByText('Content')).toBeInTheDocument();
      expect(screen.getByText('Help')).toBeInTheDocument();
    });
  });

  it('displays individual shortcuts', async () => {
    renderComponent();
    
    // Open dialog
    window.dispatchEvent(new CustomEvent('show-shortcuts-help'));
    
    // Check if shortcuts are displayed
    await waitFor(() => {
      expect(screen.getByText('Ctrl+K')).toBeInTheDocument();
      expect(screen.getByText('Open search')).toBeInTheDocument();
      expect(screen.getByText('Ctrl+D')).toBeInTheDocument();
      expect(screen.getByText('Go to dashboard')).toBeInTheDocument();
    });
  });

  it('closes when the close button is clicked', async () => {
    renderComponent();
    
    // Open dialog
    window.dispatchEvent(new CustomEvent('show-shortcuts-help'));
    
    // Wait for the dialog to appear
    await waitFor(() => {
      expect(screen.getByText('Keyboard Shortcuts')).toBeInTheDocument();
    });
    
    // Click the close button
    const closeButton = screen.getByLabelText('close');
    fireEvent.click(closeButton);
    
    // Check if the dialog is closed
    await waitFor(() => {
      expect(screen.queryByText('Keyboard Shortcuts')).not.toBeInTheDocument();
    });
  });
}); 