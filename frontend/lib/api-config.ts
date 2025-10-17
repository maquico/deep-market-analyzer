import axios from 'axios';

// Configuración de la API
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || '',
  CHAT_AGENT_URL: process.env.NEXT_PUBLIC_CHAT_AGENT_URL || process.env.NEXT_PUBLIC_API_BASE_URL || '',
  DEFAULT_USER_ID: process.env.NEXT_PUBLIC_DEFAULT_USER_ID || '',
  TIMEOUT: 30000,
};

// Instancia de axios para la API principal
export const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Función para manejar errores de la API
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = `HTTP Error: ${error.response?.status || 'Unknown'}`;
    
    try {
      const errorData = error.response?.data;
      errorMessage = errorData?.detail || errorData?.message || errorMessage;
    } catch {
      // Si no se puede parsear el error, usar el mensaje por defecto
    }
    
    throw new ApiError(errorMessage, error.response?.status, error.response?.data);
  }
);

// Headers por defecto (mantenido para compatibilidad)
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

// Función para crear URLs de la API (mantenida para compatibilidad)
export const createApiUrl = (endpoint: string): string => {
  const baseUrl = API_CONFIG.BASE_URL.replace(/\/$/, '');
  const cleanEndpoint = endpoint.replace(/^\//, '');
  return `${baseUrl}/api/v1/${cleanEndpoint}`;
};

// Función helper para hacer requests (deprecated - usar axios directamente)
export const makeRequest = async <T>(
  url: string,
  options: RequestInit = {}
): Promise<T> => {
  const config: RequestInit = {
    headers: DEFAULT_HEADERS,
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      let errorMessage = `HTTP Error: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // Si no se puede parsear el error, usar el mensaje por defecto
      }
      throw new ApiError(errorMessage, response.status);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Network error or server unavailable');
  }
};