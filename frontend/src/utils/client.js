/**
 * API Client - Unified client for all API calls
 * Handles authentication, token management, and API requests
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const TOKEN_KEY = 'dev-impact-auth-token';
const REFRESH_TOKEN_KEY = 'dev-impact-refresh-token';

/**
 * Storage utilities
 */
const storage = {
  getToken: () => localStorage.getItem(TOKEN_KEY),
  setToken: (token) => localStorage.setItem(TOKEN_KEY, token),
  removeToken: () => localStorage.removeItem(TOKEN_KEY),
  
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  setRefreshToken: (token) => localStorage.setItem(REFRESH_TOKEN_KEY, token),
  removeRefreshToken: () => localStorage.removeItem(REFRESH_TOKEN_KEY),
  
  clear: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
};

/**
 * Make API request with automatic token refresh
 */
async function fetchWithAuth(url, options = {}) {
  const token = storage.getToken();
  
  // Add authorization header if token exists
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_URL}${url}`, {
    ...options,
    headers,
  });
  
  // If unauthorized, try to refresh token
  if (response.status === 401 && token) {
    const refreshToken = storage.getRefreshToken();
    
    if (refreshToken) {
      try {
        const refreshResponse = await fetch(`${API_URL}/api/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
        
        if (refreshResponse.ok) {
          const data = await refreshResponse.json();
          storage.setToken(data.session.access_token);
          if (data.session.refresh_token) {
            storage.setRefreshToken(data.session.refresh_token);
          }
          
          // Retry original request with new token
          headers['Authorization'] = `Bearer ${data.session.access_token}`;
          return fetch(`${API_URL}${url}`, {
            ...options,
            headers,
          });
        }
      } catch (err) {
        console.error('Token refresh failed:', err);
        storage.clear();
      }
    }
  }
  
  return response;
}

/**
 * Auth API
 */
export const auth = {
  /**
   * Sign up a new user
   */
  signUp: async (email, password) => {
    const response = await fetch(`${API_URL}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to sign up');
    }
    
    const data = await response.json();
    
    // Store tokens if session exists
    if (data.session) {
      storage.setToken(data.session.access_token);
      if (data.session.refresh_token) {
        storage.setRefreshToken(data.session.refresh_token);
      }
    }
    
    return data;
  },
  
  /**
   * Sign in an existing user
   */
  signIn: async (email, password) => {
    const response = await fetch(`${API_URL}/api/auth/signin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Invalid email or password');
    }
    
    const data = await response.json();
    
    // Store tokens
    storage.setToken(data.session.access_token);
    if (data.session.refresh_token) {
      storage.setRefreshToken(data.session.refresh_token);
    }
    
    return data;
  },
  
  /**
   * Sign out current user
   */
  signOut: async () => {
    try {
      await fetchWithAuth('/api/auth/signout', {
        method: 'POST',
      });
    } catch (err) {
      console.error('Sign out error:', err);
    } finally {
      storage.clear();
    }
  },
  
  /**
   * Get current session
   */
  getSession: async () => {
    const token = storage.getToken();
    
    if (!token) {
      return { user: null, session: null };
    }
    
    try {
      const response = await fetchWithAuth('/api/auth/session');
      
      if (!response.ok) {
        storage.clear();
        return { user: null, session: null };
      }
      
      const data = await response.json();
      return data;
    } catch (err) {
      console.error('Get session error:', err);
      storage.clear();
      return { user: null, session: null };
    }
  },
  
  /**
   * Reset password (send email)
   */
  resetPassword: async (email) => {
    const response = await fetch(`${API_URL}/api/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send reset email');
    }
    
    return response.json();
  },
  
  /**
   * Update password
   */
  updatePassword: async (newPassword, recoveryToken) => {
    const response = await fetch(`${API_URL}/api/auth/update-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${recoveryToken}`
      },
      body: JSON.stringify({ new_password: newPassword }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update password');
    }
    
    return response.json();
  },
};

/**
 * User API
 */
export const user = {
  /**
   * Get current user's profile
   */
  getProfile: async () => {
    const response = await fetchWithAuth('/api/user/profile');
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch profile');
    }
    
    return response.json();
  },
  
  /**
   * Update current user's profile
   */
  updateProfile: async (profileData) => {
    const response = await fetchWithAuth('/api/user/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update profile');
    }
    
    return response.json();
  },
  
  /**
   * Complete onboarding
   */
  completeOnboarding: async (data) => {
    const response = await fetchWithAuth('/api/user/onboarding', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to complete onboarding');
    }
    
    return response.json();
  },
};

/**
 * Projects API
 */
export const projects = {
  /**
   * List all projects
   */
  list: async () => {
    const response = await fetchWithAuth('/api/projects');
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch projects');
    }
    
    return response.json();
  },
  
  /**
   * Get a single project
   */
  get: async (projectId) => {
    const response = await fetchWithAuth(`/api/projects/${projectId}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch project');
    }
    
    return response.json();
  },
  
  /**
   * Create a new project
   */
  create: async (projectData) => {
    const response = await fetchWithAuth('/api/projects', {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create project');
    }
    
    return response.json();
  },
  
  /**
   * Update a project
   */
  update: async (projectId, projectData) => {
    const response = await fetchWithAuth(`/api/projects/${projectId}`, {
      method: 'PUT',
      body: JSON.stringify(projectData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update project');
    }
    
    return response.json();
  },
  
  /**
   * Delete a project
   */
  delete: async (projectId) => {
    const response = await fetchWithAuth(`/api/projects/${projectId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete project');
    }
    
    return response.json();
  },
};

/**
 * Profiles API (published profiles)
 */
export const profiles = {
  /**
   * Publish profile
   */
  publish: async (profileData) => {
    const response = await fetchWithAuth('/api/profiles', {
      method: 'POST',
      body: JSON.stringify(profileData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to publish profile');
    }
    
    return response.json();
  },
  
  /**
   * Get published profile
   */
  get: async (username) => {
    const response = await fetch(`${API_URL}/api/profiles/${username}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Profile not found');
    }
    
    return response.json();
  },
  
  /**
   * Unpublish profile
   */
  unpublish: async (username) => {
    const response = await fetchWithAuth(`/api/profiles/${username}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to unpublish profile');
    }
    
    return response.json();
  },

  /**
   * Check if username is available
   */
  checkUsername: async (username) => {
    const response = await fetch(`${API_URL}/api/profiles/check/${username}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to check username');
    }
    
    return response.json();
  },
};

/**
 * GitHub Auth API
 */
export const github = {
  /**
   * Initiate GitHub device flow
   */
  initiateDeviceFlow: async () => {
    const response = await fetch(`${API_URL}/api/auth/github/device/code`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to initiate GitHub auth');
    }
    
    return response.json();
  },
  
  /**
   * Poll for GitHub token
   */
  pollDeviceToken: async (deviceCode) => {
    const response = await fetch(`${API_URL}/api/auth/github/device/poll`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_code: deviceCode }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to poll GitHub auth');
    }
    
    return response.json();
  },
  
  /**
   * Get GitHub user profile
   */
  getUserProfile: async (accessToken) => {
    const response = await fetch(`${API_URL}/api/auth/github/user`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ access_token: accessToken }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch GitHub profile');
    }
    
    return response.json();
  },
};

// Export storage utilities for cases where direct access is needed
export { storage };

// Default export for convenience
export default {
  auth,
  user,
  projects,
  profiles,
  github,
  storage,
};

