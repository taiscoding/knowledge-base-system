/**
 * Type definitions for the Knowledge Base System
 * Contains shared interfaces used across components
 */
import React from 'react';

// Content Types
export interface BaseContent {
  id: string;
  content_id?: string; // Alternative ID used in some contexts
  title: string;
  type: ContentType;
  category?: string;
  description?: string;
  content?: string;
  tags?: string[];
  created?: string;
  modified?: string;
  parent_id?: string;
  path?: string;
  _content_type?: string;
}

export type ContentType = 'note' | 'todo' | 'calendar' | 'folder' | 'event' | 'task';

// Note-specific content
export interface NoteContent extends BaseContent {
  type: 'note';
}

// Todo-specific content
export interface TodoContent extends BaseContent {
  type: 'todo';
  status?: TodoStatus;
  priority?: Priority;
  due_date?: string;
}

export type TodoStatus = 'active' | 'completed' | 'canceled' | 'in progress';
export type Priority = 'high' | 'medium' | 'low';

// Calendar-specific content
export interface CalendarContent extends BaseContent {
  type: 'calendar';
  datetime?: string;
  duration?: string;
}

// Folder-specific content
export interface FolderContent extends BaseContent {
  type: 'folder';
  icon?: string;
}

// Union type for all content
export type Content = NoteContent | TodoContent | CalendarContent | FolderContent;

// Search Types
export interface SearchOptions {
  contentTypes?: string[];
  categories?: string[];
  tags?: string[];
  minSimilarity?: number;
  topK?: number;
}

export interface SearchResult {
  id: string;
  title: string;
  type: ContentType;
  description?: string;
  content?: string;
  tags?: string[];
  similarity?: number;
  created?: string;
  modified?: string;
}

// Graph Types
export interface GraphNode {
  id: string;
  name: string;
  type: string;
  val?: number;
  color?: string;
  category?: string;
}

export interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  type?: string;
  value?: number;
  color?: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Component-specific Types
export interface MenuItem {
  id: string;
  title: string;
  path: string;
  icon: React.ReactNode;
}

export interface ContentStats {
  notes: number;
  todos: number;
  events: number;
  folders: number;
  total: number;
}

export interface TagData {
  label: string;
  value: string;
  count?: number;
}

// Privacy Types
export interface PrivacySettings {
  level: 'high' | 'balanced' | 'low';
  encryptContent: boolean;
  anonymizeEntities: boolean;
  allowAiProcessing: boolean;
} 