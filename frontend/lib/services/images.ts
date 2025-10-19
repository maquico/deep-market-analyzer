import axios from 'axios';
import { Image } from '@/lib/types';
import { API_CONFIG, ApiError } from '@/lib/api-config';
import { API_ROUTES } from '@/lib/api-routes';

// Create an axios instance for image operations
const imagesApi = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Interceptor to handle response errors
imagesApi.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Error with images API';
    throw new ApiError(errorMessage, error.response?.status, error.response?.data);
  }
);

export const imagesService = {
  /**
   * Get all images for a specific chat
   */
  getImagesByChat: async (chatId: string): Promise<Image[]> => {
    try {
      console.log('📸 Fetching images for chat:', chatId);
      const response = await imagesApi.get(API_ROUTES.IMAGES.GET_BY_CHAT(chatId));
      console.log('📸 Images API response:', response.data);
      return response.data || [];
    } catch (error) {
      console.error('❌ Error fetching images for chat:', chatId, error);
      throw error;
    }
  },

  /**
   * Get all images for a specific user
   */
  getImagesByUser: async (userId: string): Promise<Image[]> => {
    try {
      const response = await imagesApi.get(API_ROUTES.IMAGES.GET_BY_USER(userId));
      return response.data || [];
    } catch (error) {
      console.error('❌ Error fetching images for user:', userId, error);
      throw error;
    }
  },

  /**
   * Get a specific image by ID
   */
  getImageById: async (imageId: string): Promise<Image> => {
    try {
      console.log('📸 Fetching image by ID:', imageId);
      const response = await imagesApi.get(API_ROUTES.IMAGES.GET_BY_ID(imageId));
      console.log('📸 Image API response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching image by ID:', imageId, error);
      throw error;
    }
  },
};