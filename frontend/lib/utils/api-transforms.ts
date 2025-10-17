import { Chat, ChatMessage, UIChat, UIMessage } from '@/lib/types';

/**
 * Convierte un ChatMessage de la API a UIMessage para la interfaz
 */
export const apiMessageToUIMessage = (apiMessage: ChatMessage): UIMessage => {
  return {
    id: apiMessage.message_id,
    role: apiMessage.sender.toLowerCase() as 'user' | 'assistant', // Convertir de MAYÚSCULAS a minúsculas
    content: apiMessage.content,
    timestamp: apiMessage.created_at,
  };
};

/**
 * Convierte un UIMessage a ChatMessage para enviar a la API
 */
export const uiMessageToApiMessage = (
  uiMessage: Omit<UIMessage, 'id' | 'timestamp'>,
  chatId: string
): Omit<ChatMessage, 'message_id' | 'created_at'> => {
  return {
    chat_id: chatId,
    sender: uiMessage.role.toUpperCase() as 'USER' | 'ASSISTANT', // Convertir a MAYÚSCULAS para la API
    content: uiMessage.content,
  };
};

/**
 * Convierte un Chat de la API a UIChat para la interfaz
 */
export const apiChatToUIChat = (apiChat: Chat): UIChat => {
  let lastMessage = 'Nuevo chat creado';
  
  if (apiChat.messages && apiChat.messages.length > 0) {
    // Ordenar mensajes por fecha y tomar el último
    const sortedMessages = apiChat.messages.sort((a, b) => 
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );
    const lastMsg = sortedMessages[sortedMessages.length - 1];
    
    // Mostrar un preview más descriptivo
    if (lastMsg.sender === 'USER') {
      lastMessage = `You: ${lastMsg.content}`;
    } else {
      lastMessage = `AI: ${lastMsg.content}`;
    }
  }

  return {
    id: apiChat.chat_id,
    name: apiChat.chat_name,
    lastMessage: truncateText(lastMessage, 60),
    timestamp: formatTimestamp(apiChat.updated_at || apiChat.created_at || ''),
  };
};

/**
 * Trunca texto a una longitud específica
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Formatea timestamp para mostrar en la UI
 */
export const formatTimestamp = (timestamp: string): string => {
  if (!timestamp) return 'Ahora';

  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) return 'Ahora';
    if (diffInMinutes < 60) return `${diffInMinutes} min ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
  } catch {
    return 'Fecha inválida';
  }
};

/**
 * Genera un nombre automático para un chat basado en el primer mensaje
 */
export const generateChatName = (firstMessage: string): string => {
  const maxLength = 40;
  let name = firstMessage.trim();
  
  // Si el mensaje es muy corto, agregar prefijo descriptivo
  if (name.length < 10) {
    name = `Análisis: ${name}`;
  }
  
  // Remover caracteres especiales pero mantener espacios y puntos
  name = name.replace(/[^\w\s.,-]/gi, '');
  
  // Truncar si es muy largo
  if (name.length > maxLength) {
    name = name.substring(0, maxLength);
    // Cortar en la última palabra completa
    const lastSpace = name.lastIndexOf(' ');
    if (lastSpace > 15) {
      name = name.substring(0, lastSpace);
    }
    name += '...';
  }
  
  // Capitalizar primera letra
  name = name.charAt(0).toUpperCase() + name.slice(1);
  
  return name || 'Nuevo análisis';
};