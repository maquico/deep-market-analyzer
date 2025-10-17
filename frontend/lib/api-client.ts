import axios from 'axios';
import { API_CONFIG, DEFAULT_HEADERS, ApiError } from './api-config';

// Create axios instance for the main API
export const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: DEFAULT_HEADERS,
});

// Create axios instance for the chat agent
export const chatAgentClient = axios.create({
  baseURL: API_CONFIG.CHAT_AGENT_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: DEFAULT_HEADERS,
});

// Interceptor para manejar errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || 
                   error.response?.data?.message || 
                   error.message || 
                   'Network error or server unavailable';
    throw new ApiError(message, error.response?.status, error.response?.data);
  }
);

chatAgentClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || 
                   error.response?.data?.message || 
                   error.message || 
                   'Network error or server unavailable';
    throw new ApiError(message, error.response?.status, error.response?.data);
  }
);