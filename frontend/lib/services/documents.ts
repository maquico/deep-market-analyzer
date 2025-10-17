import { Document } from '@/lib/types';
import { apiClient } from '@/lib/api-client';
import { API_ROUTES } from '@/lib/api-routes';

export const documentsService = {
  /**
   * Obtener documentos por chat
   */
  getDocumentsByChat: async (chatId: string): Promise<Document[]> => {
    const response = await apiClient.get<Document[]>(API_ROUTES.DOCUMENTS.GET_BY_CHAT(chatId));
    return response.data;
  },

  /**
   * Obtener documentos por usuario
   */
  getDocumentsByUser: async (userId: string): Promise<Document[]> => {
    const response = await apiClient.get<Document[]>(API_ROUTES.DOCUMENTS.GET_BY_USER(userId));
    return response.data;
  },
};