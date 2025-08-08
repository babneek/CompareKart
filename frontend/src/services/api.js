import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// API methods
export const apiService = {
  // Compare prices across platforms
  compareProducts: async (product, category = null, platforms = null, maxResults = 5) => {
    try {
      const params = {
        product,
        max_results: maxResults
      };
      
      if (category) {
        params.category = category;
      }
      
      if (platforms && platforms.length > 0) {
        params.platforms = platforms.join(',');
      }
      
      const response = await api.get('/compare', { params });
      return response.data;
    } catch (error) {
      console.error('Error comparing products:', error);
      throw error;
    }
  },

  // Search specific platform
  searchPlatform: async (platform, product, maxResults = 5) => {
    try {
      const response = await api.get(`/search/${platform}`, {
        params: {
          product,
          max_results: maxResults
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error searching ${platform}:`, error);
      throw error;
    }
  },

  // Get available categories
  getCategories: async () => {
    try {
      const response = await api.get('/categories');
      return response.data;
    } catch (error) {
      console.error('Error fetching categories:', error);
      throw error;
    }
  },

  // Get supported platforms
  getPlatforms: async () => {
    try {
      const response = await api.get('/platforms');
      return response.data;
    } catch (error) {
      console.error('Error fetching platforms:', error);
      throw error;
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  },

  // Test scrapers
  testScrapers: async () => {
    try {
      const response = await api.get('/test-scrapers');
      return response.data;
    } catch (error) {
      console.error('Error testing scrapers:', error);
      throw error;
    }
  }
};

export default apiService;
