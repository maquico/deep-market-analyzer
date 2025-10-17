/**
 * Constantes para las rutas de la API del backend
 * Esto ayuda a mantener consistencia entre el frontend y backend
 */

export const API_ROUTES = {
  // Rutas de chats
  CHATS: {
    BASE: '/api/v1/chats',
    GET_ALL: '/api/v1/chats',
    GET_BY_ID: (chatId: string) => `/api/v1/chats/${chatId}`,
    GET_BY_USER: (userId: string) => `/api/v1/chats/user/${userId}`,
    CREATE: '/api/v1/chats',
    DELETE: (chatId: string) => `/api/v1/chats/${chatId}`,
  },

  // Rutas de mensajes
  MESSAGES: {
    BASE: '/api/v1/messages',
    GET_BY_CHAT: (chatId: string) => `/api/v1/messages/chat/${chatId}`,
    CREATE: '/api/v1/messages',
  },

  // Rutas de documentos
  DOCUMENTS: {
    BASE: '/api/v1/documents',
    GET_BY_CHAT: (chatId: string) => `/api/v1/documents/chat/${chatId}`,
    GET_BY_USER: (userId: string) => `/api/v1/documents/user/${userId}`,
    GET_BY_ID: (documentId: string) => `/api/v1/documents/${documentId}`,
  },

  // Rutas del agente
  AGENT: {
    BASE: '/api/v1/agent',
    MESSAGE_WITH_BOT: '/api/v1/agent/message_with_bot',
  },

  // Rutas de usuarios
  USERS: {
    BASE: '/api/v1/users',
    GET_ALL: '/api/v1/users',
    GET_BY_ID: (userId: string) => `/api/v1/users/${userId}`,
    CREATE: '/api/v1/users/users',
    DELETE: (userId: string) => `/api/v1/users/${userId}`,
  },
} as const;