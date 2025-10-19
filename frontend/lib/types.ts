// Types for the backend API
export interface ChatMessage {
  message_id: string;
  chat_id: string;
  created_at: string;
  sender: 'USER' | 'ASSISTANT'; // Matches the backend that uses uppercase
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
  name?: string;
  s3_path?: string;
  s3_key?: string;
  pdf_report_link?: string;
  pdf_presigned_url?: string;
  url?: string;
  uploaded_at?: string;
  created_at?: string;
}

export interface Image {
  image_id: string;
  chat_id: string;
  user_id: string;
  description: string;
  s3_bucket: string;
  s3_key: string;
  image_presigned_url: string; // Campo correcto del backend
  created_at?: string;
  updated_at?: string;
}

// Types for the chat agent - Based on the /api/v1/agent/message_with_bot endpoint
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
  metadata?: Record<string, unknown>;
}

export interface GeneratedImage {
  image_id: string;
  description: string;
  s3_bucket: string;
  s3_key: string;
  presigned_url: string; // Para el streaming mantiene este nombre
}

// Types for the local UI
export interface UIMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  hasDownload?: boolean;
  downloadLink?: string;
  documentId?: string;
  images?: GeneratedImage[];
  timestamp?: string;
}

export interface UIChat {
  id: string;
  name: string;
  lastMessage: string;
  timestamp: string;
}