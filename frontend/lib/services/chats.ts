import { Chat } from '@/lib/types';
import { apiClient } from '@/lib/api-client';
import { API_ROUTES } from '@/lib/api-routes';

export const chatsService = {
  /**
   * Get all chats from a user
   */
  getChatsByUser: async (userId: string): Promise<Chat[]> => {
    const response = await apiClient.get<Chat[]>(API_ROUTES.CHATS.GET_BY_USER(userId));
    return response.data;
  },

  /**
   * Get a specific chat by ID (includes messages)
   */
  getChatById: async (chatId: string): Promise<Chat> => {
    const response = await apiClient.get<Chat>(API_ROUTES.CHATS.GET_BY_ID(chatId));
    return response.data;
  },

  /**
   * Create a new chat
   */
  createChat: async (chatName: string, userId: string): Promise<Chat> => {
    console.log('Creating chat with:', { chatName, userId });
    console.log('URL will be:', API_ROUTES.CHATS.CREATE);
    
    const response = await apiClient.post<Chat>(API_ROUTES.CHATS.CREATE, null, {
      params: { 
        chat_name: chatName, 
        user_id: userId 
      }
    });
    
    console.log('Create chat response:', response.data);
    return response.data;
  },

  /**
   * Delete a chat
   */
  deleteChat: async (chatId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(API_ROUTES.CHATS.DELETE(chatId));
    return response.data;
  },

  /**
   * Update chat name
   */
  updateChatName: async (chatId: string, chatName: string): Promise<Chat> => {
    const response = await apiClient.patch<Chat>(API_ROUTES.CHATS.UPDATE(chatId), null, {
      params: { 
        chat_name: chatName 
      }
    });
    return response.data;
  },
};