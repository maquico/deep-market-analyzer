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
   * Limpiar mensajes temporales
   */
  const clearTemporaryMessages = useCallback(() => {
    setMessages(prev => prev.filter(msg => !msg.id.startsWith('temp-')));
  }, []);

  /**
   * Cargar todos los chats del usuario
   */
  const loadChats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const apiChats = await chatsService.getChatsByUser(userId);
      const uiChats = apiChats.map(apiChatToUIChat);
      
      setChats(uiChats);
      
      // Si no hay chat activo y hay chats disponibles, seleccionar el primero
      if (!activeChat && uiChats.length > 0) {
        setActiveChat(uiChats[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Error al cargar los chats');
      console.error('Error loading chats:', err);
    } finally {
      setLoading(false);
    }
  }, [userId, activeChat]);

  /**
   * Cargar mensajes de un chat específico
   */
  const loadMessages = useCallback(async (chatId: string) => {
    try {
      setLoading(true);
      setError(null);

      const apiMessages = await messagesService.getMessagesByChat(chatId);
      
      // Ordenar por fecha de creación
      const sortedMessages = apiMessages.sort((a, b) => 
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
      
      const uiMessages = sortedMessages.map(apiMessageToUIMessage);
      
      // Reemplazar TODOS los mensajes
      setMessages(uiMessages);
    } catch (err: any) {
      setError(err.message || 'Error al cargar los mensajes');
      console.error('❌ Error loading messages:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Crear un nuevo chat
   */
  const createNewChat = useCallback(async (chatName?: string) => {
    try {
      setLoading(true);
      setError(null);

      const finalChatName = chatName || 'Nuevo análisis';
      const newChat = await chatsService.createChat(finalChatName, userId);
      const uiChat = apiChatToUIChat(newChat);

      
      setChats(prev => [uiChat, ...prev]);
      setActiveChat(newChat.chat_id);
      setMessages([]);
      
      return newChat.chat_id;
    } catch (err: any) {
      setError(err.message || 'Error al crear el chat');
      console.error('Error creating chat:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  /**
   * Enviar un mensaje - SIN mensajes temporales para evitar duplicaciones
   */
  const sendMessage = useCallback(async (content: string, chatId: string) => {
    try {
      setSending(true);
      setError(null);



      // Usar el servicio de chat-agent que maneja todo el flujo
      const agentResponse = await chatAgentService.sendMessage(
        content, 
        userId, 
        chatId,
        chats.find(chat => chat.id === chatId)?.name || 'Análisis'
      );



      // Recargar mensajes directamente desde el backend
      await loadMessages(chatId);
      
      // Recargar la lista de chats para actualizar el último mensaje
      await loadChats();



    } catch (err: any) {
      setError(err.message || 'Error al enviar el mensaje');
      console.error('❌ Error sending message:', err);
      throw err;
    } finally {
      setSending(false);
    }
  }, [userId, chats, loadChats, loadMessages]);

  /**
   * Eliminar un chat
   */
  const deleteChat = useCallback(async (chatId: string) => {
    try {
      setLoading(true);
      setError(null);

      await chatsService.deleteChat(chatId);
      
      setChats(prev => prev.filter(chat => chat.id !== chatId));
      
      // Si era el chat activo, seleccionar otro
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
      setError(err.message || 'Error al eliminar el chat');
      console.error('Error deleting chat:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [activeChat, chats]);

  /**
   * Cambiar el chat activo
   */
  const switchToChat = useCallback((chatId: string) => {
    setActiveChat(chatId);
    loadMessages(chatId);
  }, [loadMessages]);

  // Cargar chats al montar el componente
  useEffect(() => {
    loadChats();
  }, [loadChats]);

  // Cargar mensajes cuando cambia el chat activo
  useEffect(() => {
    if (activeChat) {
      loadMessages(activeChat);
    }
  }, [activeChat, loadMessages]);

  return {
    // Estado
    chats,
    activeChat,
    messages,
    loading,
    sending,
    error,
    
    // Acciones
    createNewChat,
    sendMessage,
    deleteChat,
    switchToChat,
    refreshChats: loadChats,
    clearError: () => setError(null),
  };
};