// Types para la API del backend
export interface ChatMessage {
  message_id: string;
  chat_id: string;
  created_at: string;
  sender: 'USER' | 'ASSISTANT'; // Coincide con el backend que usa mayúsculas
  content: string;
}

export interface Chat {
  chat_id: string;
  chat_name: string;
  user_id: string;
  messages?: ChatMessage[];
  created_at?: string;
  updated_at?: string;
}

export interface User {
  user_id: string;
  created_at: string;
  username: string;
}

export interface Document {
  document_id: string;
  chat_id: string;
  user_id: string;
  name: string;
  s3_path: string;
  uploaded_at: string;
}

// Types para el chat agent - Basado en el endpoint /api/v1/agent/message_with_bot
export interface MessageRequest {
  query: string;
  user_id: string;
  chat_id?: string;
  chat_name?: string;
}

export interface MessageResponse {
  message: string;
  chat_id: string;
  success: boolean;
  user_id: string;
  message_id: string;
}

export interface ChatRequest {
  question: string;
  user_id: string;
  session_id?: string;
}

export interface ChatResponse {
  answer: string;
  session_id: string;
  user_id: string;
  sources?: string[];
  metadata?: Record<string, any>;
}

// Types para el UI local
export interface UIMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  hasDownload?: boolean;
  timestamp?: string;
}

export interface UIChat {
  id: string;
  name: string;
  lastMessage: string;
  timestamp: string;
}