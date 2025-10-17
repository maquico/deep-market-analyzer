import axios from 'axios';
import { ChatRequest, ChatResponse } from '@/lib/types';
import { API_CONFIG, ApiError } from '@/lib/api-config';
import { API_ROUTES } from '@/lib/api-routes';

// Crear una instancia de axios para el chat agent
const chatAgentApi = axios.create({
  baseURL: API_CONFIG.BASE_URL, // Usar la misma URL base que el resto de la API
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Interceptor para manejar errores de respuesta
chatAgentApi.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Error sending message';
    throw new ApiError(errorMessage, error.response?.status, error.response?.data);
  }
);

export const chatAgentService = {
  /**
   * Envía un mensaje al chatbot/agente usando el endpoint /api/v1/agent/message_with_bot
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
    

    
    // Transformar la respuesta del backend al formato esperado por el frontend
    return {
      answer: response.data.message,
      session_id: response.data.chat_id,
      user_id: response.data.user_id,
      metadata: {
        has_document: false, // Agregar lógica si necesitas detectar documentos
      },
    };
  },
};