import { Chat, ChatMessage, UIChat, UIMessage } from '@/lib/types';

/**
 * Converts an API ChatMessage to UIMessage for the interface
 */
export const apiMessageToUIMessage = (apiMessage: ChatMessage): UIMessage => {
  return {
    id: apiMessage.message_id,
    role: apiMessage.sender.toLowerCase() as 'user' | 'assistant', // Convert from UPPERCASE to lowercase
    content: apiMessage.content,
    timestamp: apiMessage.created_at,
  };
};

/**
 * Converts a UIMessage to ChatMessage to send to the API
 */
export const uiMessageToApiMessage = (
  uiMessage: Omit<UIMessage, 'id' | 'timestamp'>,
  chatId: string
): Omit<ChatMessage, 'message_id' | 'created_at'> => {
  return {
    chat_id: chatId,
    sender: uiMessage.role.toUpperCase() as 'USER' | 'ASSISTANT', // Convert to UPPERCASE for the API
    content: uiMessage.content,
  };
};

/**
 * Converts an API Chat to UIChat for the interface
 */
export const apiChatToUIChat = (apiChat: Chat): UIChat => {
  let lastMessage = 'New chat created';
  
  if (apiChat.messages && apiChat.messages.length > 0) {
    // Sort messages by date and take the last one
    const sortedMessages = apiChat.messages.sort((a, b) => 
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );
    const lastMsg = sortedMessages[sortedMessages.length - 1];
    
    // Show a more descriptive preview
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
 * Truncates text to a specific length
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Formats timestamp for UI display
 */
export const formatTimestamp = (timestamp: string): string => {
  if (!timestamp) return 'Now';

  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) return 'Now';
    if (diffInMinutes < 60) return `${diffInMinutes} min ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
  } catch {
    return 'Invalid date';
  }
};

/**
 * Generates an automatic name for a chat based on the first message
 */
export const generateChatName = (firstMessage: string): string => {
  const maxLength = 40;
  let name = firstMessage.trim();
  
  // If the message is too short, add descriptive prefix
  if (name.length < 10) {
    name = `Analysis: ${name}`;
  }
  
  // Remove special characters but keep spaces and dots
  name = name.replace(/[^\w\s.,-]/gi, '');
  
  // Truncate if too long
  if (name.length > maxLength) {
    name = name.substring(0, maxLength);
    // Cut at the last complete word
    const lastSpace = name.lastIndexOf(' ');
    if (lastSpace > 15) {
      name = name.substring(0, lastSpace);
    }
    name += '...';
  }
  
  // Capitalize first letter
  name = name.charAt(0).toUpperCase() + name.slice(1);
  
  return name || 'New analysis';
};