import axios from 'axios';
import { ChatResponse, GeneratedImage } from '@/lib/types';
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

// Types for streaming
export interface StreamingMessage {
  type: 'metadata' | 'text' | 'done' | 'error' | 'document' | 'images' | string; // Added 'images'
  content?: string;
  chat_id?: string;
  user_id?: string;
  message?: string;
  // Document fields
  document?: {
    document_id: string;
    pdf_report_link: string;
  };
  // Images fields
  images?: GeneratedImage[]; // Updated to use the proper type
  // Additional fields that might come from the agent
  document_url?: string;
  document_id?: string;
  link?: string;
  url?: string;
  file_path?: string;
  file_name?: string;
  attachment?: any;
  metadata?: any;
  [key: string]: any; // Allow any additional properties
}

export interface StreamingCallbacks {
  onMetadata?: (data: { chat_id: string; user_id: string }) => void;
  onText?: (content: string) => void; // Changed from onChunk to onText
  onDone?: (data: { chat_id: string }) => void;
  onError?: (error: string) => void;
  onDocument?: (data: StreamingMessage) => void;
  onImages?: (data: StreamingMessage) => void;
  onUnknownEvent?: (data: StreamingMessage) => void;
}

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

  /**
   * Send a message with streaming response using Server-Sent Events
   */
  sendMessageStream: async (
    question: string,
    userId: string,
    callbacks: StreamingCallbacks,
    sessionId?: string,
    chatName?: string
  ): Promise<void> => {
    const payload = {
      query: question,
      user_id: userId,
      chat_id: sessionId,
      chat_name: chatName,
    };



    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ROUTES.AGENT.MESSAGE_WITH_BOT_STREAM}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;
          
          // Process complete lines
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.trim() && line.startsWith('data: ')) {
              try {
                const jsonStr = line.slice(6).trim(); // Remove 'data: ' prefix
                if (jsonStr && jsonStr !== '') {
                  const data: StreamingMessage = JSON.parse(jsonStr);
                  
                  switch (data.type) {
                    case 'metadata':
                      console.log('📋 Metadata event:', JSON.stringify(data, null, 2));
                      if (callbacks.onMetadata && data.chat_id && data.user_id) {
                        callbacks.onMetadata({ chat_id: data.chat_id, user_id: data.user_id });
                      }
                      break;
                    case 'text':
                      if (callbacks.onText && data.content) {
                        // Use requestIdleCallback for better performance, fallback to setTimeout
                        if (window.requestIdleCallback) {
                          window.requestIdleCallback(() => {
                            callbacks.onText!(data.content!);
                          });
                        } else {
                          setTimeout(() => {
                            callbacks.onText!(data.content!);
                          }, 0);
                        }
                      }
                      break;
                    case 'done':
                      console.log('✅ Done event:', JSON.stringify(data, null, 2));
                      if (callbacks.onDone && data.chat_id) {
                        callbacks.onDone({ chat_id: data.chat_id });
                      }
                      return; // End the stream
                    case 'error':
                      console.error('❌ Error event:', JSON.stringify(data, null, 2));
                      if (callbacks.onError && data.message) {
                        callbacks.onError(data.message);
                      }
                      return; // End the stream on error
                    case 'document':
                      console.log('📎 Document event:', JSON.stringify(data, null, 2));
                      if (callbacks.onDocument) {
                        callbacks.onDocument(data);
                      }
                      break;
                    case 'images':
                      console.log('🖼️ Images event:', JSON.stringify(data, null, 2));
                      if (callbacks.onImages) {
                        callbacks.onImages(data);
                      }
                      break;
                    default:
                      console.log('❓ Unknown event type:', JSON.stringify(data, null, 2));
                      if (callbacks.onUnknownEvent) {
                        callbacks.onUnknownEvent(data);
                      }
                      break;
                  }
                }
              } catch (parseError) {
                console.warn('⚠️ Failed to parse SSE message:', line, parseError);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      if (callbacks.onError) {
        callbacks.onError(error instanceof Error ? error.message : 'Unknown streaming error');
      }
      throw error;
    }
  },
};