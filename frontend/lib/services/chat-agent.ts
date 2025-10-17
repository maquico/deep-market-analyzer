import axios from 'axios';
import { ChatResponse } from '@/lib/types';
import { API_CONFIG, ApiError } from '@/lib/api-config';
import { API_ROUTES } from '@/lib/api-routes';

// Create an axios instance for the chat agent
const chatAgentApi = axios.create({
  baseURL: API_CONFIG.BASE_URL, // Use the same base URL as the rest of the API
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Interceptor to handle response errors
chatAgentApi.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Error sending message';
    throw new ApiError(errorMessage, error.response?.status, error.response?.data);
  }
);

export const chatAgentService = {
  /**
   * Send a message to the chatbot/agent using the /api/v1/agent/message_with_bot endpoint
   */
  sendMessage: async (
    question: string,
    userId: string,
    sessionId?: string,
    chatName?: string
  ): Promise<ChatResponse> => {
    const payload = {
      query: question,
      user_id: userId,
      chat_id: sessionId,
      chat_name: chatName,
    };

    const response = await chatAgentApi.post(API_ROUTES.AGENT.MESSAGE_WITH_BOT, payload);
    

    
    // Transform the backend response to the format expected by the frontend
    return {
      answer: response.data.message,
      session_id: response.data.chat_id,
      user_id: response.data.user_id,
      metadata: {
        has_document: false, // Add logic if you need to detect documents
      },
    };
  },
};