/**
 * Constants for backend API routes
 * This helps maintain consistency between frontend and backend
 */

export const API_ROUTES = {
  // Chat routes
  CHATS: {
    BASE: '/api/v1/chats',
    GET_ALL: '/api/v1/chats',
    GET_BY_ID: (chatId: string) => `/api/v1/chats/${chatId}`,
    GET_BY_USER: (userId: string) => `/api/v1/chats/user/${userId}`,
    CREATE: '/api/v1/chats',
    DELETE: (chatId: string) => `/api/v1/chats/${chatId}`,
  },

  // Message routes
  MESSAGES: {
    BASE: '/api/v1/messages',
    GET_BY_CHAT: (chatId: string) => `/api/v1/messages/chat/${chatId}`,
    CREATE: '/api/v1/messages',
  },

  // Document routes
  DOCUMENTS: {
    BASE: '/api/v1/documents',
    GET_BY_CHAT: (chatId: string) => `/api/v1/documents/chat/${chatId}`,
    GET_BY_USER: (userId: string) => `/api/v1/documents/user/${userId}`,
    GET_BY_ID: (documentId: string) => `/api/v1/documents/${documentId}`,
  },

  // Agent routes
  AGENT: {
    BASE: '/api/v1/agent',
    MESSAGE_WITH_BOT: '/api/v1/agent/message_with_bot',
  },

  // User routes
  USERS: {
    BASE: '/api/v1/users',
    GET_ALL: '/api/v1/users',
    GET_BY_ID: (userId: string) => `/api/v1/users/${userId}`,
    CREATE: '/api/v1/users/users',
    DELETE: (userId: string) => `/api/v1/users/${userId}`,
  },
} as const;