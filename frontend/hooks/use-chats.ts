import { useState, useEffect, useCallback, startTransition } from 'react';
import { 
  chatsService, 
  messagesService,
  chatAgentService, 
  API_CONFIG,
  Chat, 
  UIChat, 
  UIMessage 
} from '@/lib/services';
import type { StreamingCallbacks } from '@/lib/services/chat-agent';
import { 
  apiChatToUIChat,
  apiMessageToUIMessage,
  generateChatName 
} from '@/lib/utils/api-transforms';
import { useStreaming } from './use-streaming';

export const useChats = () => {
  const [chats, setChats] = useState<UIChat[]>([]);
  const [activeChat, setActiveChat] = useState<string | null>(null);
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const userId = API_CONFIG.DEFAULT_USER_ID;
  const { updateStreamingContent, resetStreamingContent } = useStreaming();

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
      
      // Sort chats by creation date (newest first)
      const sortedChats = apiChats.sort((a, b) => {
        const dateA = new Date(a.created_at || '').getTime();
        const dateB = new Date(b.created_at || '').getTime();
        return dateB - dateA; // Newest first
      });
      
      const uiChats = sortedChats.map(apiChatToUIChat);
      
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
   * Send a message with streaming response
   */
  const sendMessage = useCallback(async (content: string, chatId: string) => {
    try {
      setSending(true);
      setError(null);

      // Reset streaming content
      resetStreamingContent();

      // Add user message immediately
      const userMessage: UIMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, userMessage]);

      // Create a temporary assistant message for streaming
      const tempAssistantId = `assistant-${Date.now()}`;
      const assistantMessage: UIMessage = {
        id: tempAssistantId,
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, assistantMessage]);

      let finalChatId = chatId;

      // Use streaming service
      await chatAgentService.sendMessageStream(
        content,
        userId,
        {
          onMetadata: (data) => {
            if (data.chat_id) {
              finalChatId = data.chat_id;
              // Update active chat if it's a new chat
              if (finalChatId !== chatId) {
                setActiveChat(finalChatId);
              }
            }
          },
          onText: (chunk) => {
            // Use the streaming hook to update content
            updateStreamingContent(chunk, (newContent) => {
              setMessages(prevMessages => 
                prevMessages.map(msg => 
                  msg.id === tempAssistantId 
                    ? { ...msg, content: newContent } 
                    : msg
                )
              );
            });
          },
          onDone: async (data) => {
            console.log('✅ Stream completed:', data);
            setSending(false);
            
            // TODO: Temporalmente comentado para no perder las imágenes
            // El problema es que loadMessages() reemplaza el estado local con datos de la API
            // que no incluyen las imágenes generadas durante el streaming
            /*
            if (finalChatId) {
              await loadMessages(finalChatId);
            }
            */
            
            // Update chat list in a transition to avoid blocking
            startTransition(() => {
              loadChats();
            });
          },
          onError: (errorMsg) => {
            console.error('❌ Stream error:', errorMsg);
            setError(errorMsg);
            setSending(false);
            // Remove the temporary assistant message on error
            setMessages(prev => prev.filter(msg => msg.id !== tempAssistantId));
          },
          onDocument: (data) => {
            console.log('📎 Document event received in useChats:', data);
            
            // Add the document information to the current assistant message
            setMessages(prevMessages => 
              prevMessages.map(msg => 
                msg.id === tempAssistantId 
                  ? { 
                      ...msg, 
                      hasDownload: true,
                      downloadLink: data.document?.pdf_report_link,
                      documentId: data.document?.document_id
                    } 
                  : msg
              )
            );
          },
          onImages: (data) => {
            console.log('🖼️ Images event received - adding', data.images?.length, 'images to message');
            
            // Add the images to the current assistant message
            if (data.images && data.images.length > 0) {
              setMessages(prevMessages => {
                const updatedMessages = prevMessages.map(msg => 
                  msg.id === tempAssistantId 
                    ? { 
                        ...msg, 
                        images: data.images
                      } 
                    : msg
                );
                return updatedMessages;
              });
            } else {
              console.log('🖼️ No images in data or empty array');
            }
          },
          onUnknownEvent: (data) => {
            console.log('❓ Unknown event received in useChats:', data);
          },
        },
        chatId,
        chats.find(chat => chat.id === chatId)?.name || 'Analysis'
      );
    } catch (err: any) {
      setError(err.message || 'Error sending message');
      console.error('❌ Error sending message:', err);
      setSending(false);
      throw err;
    }
  }, [userId, chats, updateStreamingContent, resetStreamingContent, loadChats]);

  /**
   * Update chat name
   */
  const updateChatName = useCallback(async (chatId: string, newName: string) => {
    try {
      setLoading(true);
      setError(null);

      await chatsService.updateChatName(chatId, newName);
      
      // Update the chat name in the local state
      setChats(prev => prev.map(chat => 
        chat.id === chatId 
          ? { ...chat, name: newName }
          : chat
      ));
    } catch (err: any) {
      setError(err.message || 'Error updating chat name');
      console.error('Error updating chat name:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

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
  }, []);

  // Load messages when active chat changes (but not when sending)
  useEffect(() => {
    if (activeChat && !sending) {
      loadMessages(activeChat);
    }
  }, [activeChat]); // Only depend on activeChat

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
    updateChatName,
    switchToChat,
    refreshChats: loadChats,
    clearError: () => setError(null),
  };
};