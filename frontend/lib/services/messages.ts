import { ChatMessage } from '@/lib/types';
import { apiClient } from '@/lib/api-client';
import { API_ROUTES } from '@/lib/api-routes';

export const messagesService = {
  /**
   * Get all messages from a chat
   */
  getMessagesByChat: async (chatId: string): Promise<ChatMessage[]> => {
    const response = await apiClient.get<ChatMessage[]>(API_ROUTES.MESSAGES.GET_BY_CHAT(chatId));
    return response.data;
  },

  /**
   * Create a new message
   */
  addMessage: async (message: Omit<ChatMessage, 'message_id' | 'created_at'>): Promise<ChatMessage> => {
    const response = await apiClient.post<ChatMessage>(API_ROUTES.MESSAGES.CREATE, message);
    return response.data;
  },
};