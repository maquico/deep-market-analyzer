import { useState, useEffect, useCallback } from 'react';
import { 
  chatsService, 
  messagesService,
  chatAgentService, 
  API_CONFIG,
  Chat, 
  UIChat, 
  UIMessage 
} from '@/lib/services';
import { 
  apiChatToUIChat,
  apiMessageToUIMessage,
  generateChatName 
} from '@/lib/utils/api-transforms';

export const useChats = () => {
  const [chats, setChats] = useState<UIChat[]>([]);
  const [activeChat, setActiveChat] = useState<string | null>(null);
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const userId = API_CONFIG.DEFAULT_USER_ID;

  /**
   * Clear temporary messages
   */
  const clearTemporaryMessages = useCallback(() => {
    setMessages(prev => prev.filter(msg => !msg.id.startsWith('temp-')));
  }, []);

  /**
   * Load all user chats
   */
  const loadChats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const apiChats = await chatsService.getChatsByUser(userId);
      const uiChats = apiChats.map(apiChatToUIChat);
      
      setChats(uiChats);
      
      // If there's no active chat and chats are available, select the first one
      if (!activeChat && uiChats.length > 0) {
        setActiveChat(uiChats[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Error loading chats');
      console.error('Error loading chats:', err);
    } finally {
      setLoading(false);
    }
  }, [userId, activeChat]);

  /**
   * Load messages from a specific chat
   */
  const loadMessages = useCallback(async (chatId: string) => {
    try {
      setLoading(true);
      setError(null);

      const apiMessages = await messagesService.getMessagesByChat(chatId);
      
      // Sort by creation date
      const sortedMessages = apiMessages.sort((a, b) => 
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
      
      const uiMessages = sortedMessages.map(apiMessageToUIMessage);
      
      // Replace ALL messages
      setMessages(uiMessages);
    } catch (err: any) {
      setError(err.message || 'Error loading messages');
      console.error('❌ Error loading messages:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Create a new chat
   */
  const createNewChat = useCallback(async (chatName?: string) => {
    try {
      setLoading(true);
      setError(null);

      const finalChatName = chatName || 'New analysis';
      const newChat = await chatsService.createChat(finalChatName, userId);
      const uiChat = apiChatToUIChat(newChat);

      
      setChats(prev => [uiChat, ...prev]);
      setActiveChat(newChat.chat_id);
      setMessages([]);
      
      return newChat.chat_id;
    } catch (err: any) {
      setError(err.message || 'Error creating chat');
      console.error('Error creating chat:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  /**
   * Send a message - WITHOUT temporary messages to avoid duplications
   */
  const sendMessage = useCallback(async (content: string, chatId: string) => {
    try {
      setSending(true);
      setError(null);



      // Use the chat-agent service that handles the entire flow
      const agentResponse = await chatAgentService.sendMessage(
        content, 
        userId, 
        chatId,
        chats.find(chat => chat.id === chatId)?.name || 'Analysis'
      );



      // Reload messages directly from the backend
      await loadMessages(chatId);
      
      // Reload the chat list to update the last message
      await loadChats();



    } catch (err: any) {
      setError(err.message || 'Error sending message');
      console.error('❌ Error sending message:', err);
      throw err;
    } finally {
      setSending(false);
    }
  }, [userId, chats, loadChats, loadMessages]);

  /**
   * Delete a chat
   */
  const deleteChat = useCallback(async (chatId: string) => {
    try {
      setLoading(true);
      setError(null);

      await chatsService.deleteChat(chatId);
      
      setChats(prev => prev.filter(chat => chat.id !== chatId));
      
      // If it was the active chat, select another one
      if (activeChat === chatId) {
        const remainingChats = chats.filter(chat => chat.id !== chatId);
        if (remainingChats.length > 0) {
          setActiveChat(remainingChats[0].id);
        } else {
          setActiveChat(null);
          setMessages([]);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Error deleting chat');
      console.error('Error deleting chat:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [activeChat, chats]);

  /**
   * Switch to active chat
   */
  const switchToChat = useCallback((chatId: string) => {
    setActiveChat(chatId);
    loadMessages(chatId);
  }, [loadMessages]);

  // Load chats when component mounts
  useEffect(() => {
    loadChats();
  }, [loadChats]);

  // Load messages when active chat changes
  useEffect(() => {
    if (activeChat) {
      loadMessages(activeChat);
    }
  }, [activeChat, loadMessages]);

  return {
    // State
    chats,
    activeChat,
    messages,
    loading,
    sending,
    error,
    
    // Actions
    createNewChat,
    sendMessage,
    deleteChat,
    switchToChat,
    refreshChats: loadChats,
    clearError: () => setError(null),
  };
};