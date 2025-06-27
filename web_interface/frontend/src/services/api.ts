/**
 * API Service
 * Provides methods to interact with the Knowledge Base backend API
 */

const API_BASE_URL = '/api';

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

interface SearchOptions {
  contentTypes?: string[];
  categories?: string[];
  tags?: string[];
  minSimilarity?: number;
  topK?: number;
}

interface ContentCreateParams {
  title: string;
  content?: string;
  description?: string;
  category?: string;
  tags?: string[];
  type: string;
  parentId?: string;
  [key: string]: any;
}

interface UserProfile {
  displayName: string;
  email: string;
  bio?: string;
  location?: string;
  tags?: string[];
  avatar?: string;
  dateJoined?: string;
}

interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  fontSize: 'small' | 'medium' | 'large';
  autoTagging: boolean;
  keyboardShortcuts: boolean;
  defaultView: string;
}

class ApiService {
  private async request<T = any>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    const config = {
      ...options,
      headers,
    };
    
    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || response.statusText);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API Request Error: ${error}`);
      throw error;
    }
  }
  
  // Content Management
  
  async getContentByType(type: string) {
    return this.request(`/knowledge/content?type=${type}`);
  }
  
  async getContent(contentId: string) {
    return this.request(`/knowledge/content/${contentId}`);
  }
  
  async createContent(contentData: ContentCreateParams) {
    return this.request('/knowledge/content', {
      method: 'POST',
      body: JSON.stringify(contentData),
    });
  }
  
  async updateContent(contentId: string, updates: any) {
    return this.request(`/knowledge/content/${contentId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }
  
  async deleteContent(contentId: string) {
    return this.request(`/knowledge/content/${contentId}`, {
      method: 'DELETE',
    });
  }
  
  // Search
  
  async searchContent(query: string, contentType?: string) {
    const params = new URLSearchParams();
    params.append('query', query);
    if (contentType) {
      params.append('type', contentType);
    }
    
    return this.request(`/search?${params.toString()}`);
  }
  
  async semanticSearch(query: string, options: SearchOptions = {}) {
    const params = new URLSearchParams();
    params.append('query', query);
    
    if (options.contentTypes?.length) {
      params.append('contentTypes', options.contentTypes.join(','));
    }
    
    if (options.categories?.length) {
      params.append('categories', options.categories.join(','));
    }
    
    if (options.tags?.length) {
      params.append('tags', options.tags.join(','));
    }
    
    if (options.minSimilarity) {
      params.append('minSimilarity', options.minSimilarity.toString());
    }
    
    if (options.topK) {
      params.append('topK', options.topK.toString());
    }
    
    return this.request(`/search/semantic?${params.toString()}`);
  }
  
  // Natural Language Processing
  
  async queryNaturalLanguage(query: string) {
    return this.request(`/nlp/query?query=${encodeURIComponent(query)}`);
  }
  
  async processConversation(message: string, sessionId?: string) {
    const params = new URLSearchParams();
    params.append('message', message);
    if (sessionId) {
      params.append('session_id', sessionId);
    }
    
    return this.request(`/nlp/conversation?${params.toString()}`);
  }
  
  async generateSummary(contentId: string, maxLength: number = 200) {
    return this.request(`/nlp/summarize?content_id=${contentId}&max_length=${maxLength}`);
  }
  
  async extractEntities(text: string) {
    return this.request('/nlp/extract-entities', {
      method: 'POST',
      body: JSON.stringify({ text })
    });
  }
  
  async autoGenerateTags(contentId: string) {
    return this.request(`/nlp/tag-content?content_id=${contentId}`, {
      method: 'POST'
    });
  }
  
  // Dashboard
  
  async getDashboardStats() {
    return this.request('/dashboard/stats');
  }
  
  async getRecentActivity(limit: number = 10) {
    return this.request(`/dashboard/activity?limit=${limit}`);
  }
  
  async getContentDistribution() {
    return this.request('/dashboard/distribution');
  }
  
  // Organization & Tagging
  
  async getFolderStructure(folderId?: string, depth: number = 2) {
    const params = new URLSearchParams();
    if (folderId) {
      params.append('folder_id', folderId);
    }
    params.append('depth', depth.toString());
    
    return this.request(`/organization/folders?${params.toString()}`);
  }
  
  async createFolder(title: string, parentId?: string, description?: string) {
    return this.request('/organization/folders', {
      method: 'POST',
      body: JSON.stringify({
        title,
        parent_id: parentId,
        description
      })
    });
  }
  
  async moveContent(contentId: string, folderId: string) {
    return this.request('/organization/move', {
      method: 'POST',
      body: JSON.stringify({
        content_id: contentId,
        folder_id: folderId
      })
    });
  }
  
  async getPopularTags(limit: number = 20) {
    return this.request(`/organization/tags/popular?limit=${limit}`);
  }
  
  // Knowledge Graph
  
  async getKnowledgeGraph(rootIds?: string[], maxDepth: number = 2) {
    const params = new URLSearchParams();
    if (rootIds?.length) {
      params.append('root_ids', rootIds.join(','));
    }
    params.append('max_depth', maxDepth.toString());
    
    return this.request(`/graph/knowledge?${params.toString()}`);
  }
  
  // Voice
  
  async transcribeAudio(audioBlob: Blob) {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    
    return this.request('/voice/transcribe', {
      method: 'POST',
      headers: {}, // Let browser set content type with boundary
      body: formData
    });
  }
  
  // Privacy
  
  async getPrivacySettings() {
    return this.request('/privacy/settings');
  }
  
  async updatePrivacySettings(settings: any) {
    return this.request('/privacy/settings', {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }
  
  async createPrivacySession(level: string = 'balanced') {
    return this.request('/privacy/session', {
      method: 'POST',
      body: JSON.stringify({ level })
    });
  }

  // User Profile

  /**
   * Get the current user's profile information
   * @returns User profile data
   */
  async getUserProfile() {
    return this.request<ApiResponse<UserProfile>>('/user/profile');
  }

  /**
   * Update the user's profile information
   * @param profile Updated profile data
   * @returns API response
   */
  async updateUserProfile(profile: Partial<UserProfile>) {
    return this.request<ApiResponse<UserProfile>>('/user/profile', {
      method: 'PUT',
      body: JSON.stringify(profile)
    });
  }

  /**
   * Update user avatar
   * @param avatarFile The avatar image file
   * @returns API response with the avatar URL
   */
  async updateAvatar(avatarFile: File) {
    const formData = new FormData();
    formData.append('avatar', avatarFile);
    
    return this.request<ApiResponse<{avatarUrl: string}>>('/user/avatar', {
      method: 'POST',
      headers: {}, // Let browser set content type with boundary
      body: formData
    });
  }

  /**
   * Get user preferences
   * @returns User preferences data
   */
  async getUserPreferences() {
    return this.request<ApiResponse<UserPreferences>>('/user/preferences');
  }

  /**
   * Update user preferences
   * @param preferences Updated preferences data
   * @returns API response
   */
  async updateUserPreferences(preferences: Partial<UserPreferences>) {
    return this.request<ApiResponse<UserPreferences>>('/user/preferences', {
      method: 'PUT',
      body: JSON.stringify(preferences)
    });
  }

  /**
   * Change user password
   * @param currentPassword Current password
   * @param newPassword New password
   * @returns API response
   */
  async changePassword(currentPassword: string, newPassword: string) {
    return this.request<ApiResponse<{success: boolean}>>('/user/password', {
      method: 'PUT',
      body: JSON.stringify({ currentPassword, newPassword })
    });
  }

  /**
   * Get user's active sessions
   * @returns List of active user sessions
   */
  async getUserSessions() {
    return this.request<ApiResponse<any[]>>('/user/sessions');
  }

  /**
   * Terminate all user sessions except the current one
   * @returns API response
   */
  async terminateOtherSessions() {
    return this.request<ApiResponse<{success: boolean}>>('/user/sessions/terminate-others', {
      method: 'POST'
    });
  }
}

// Create and export singleton instance
const api = new ApiService();
export default api; 