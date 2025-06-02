import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { ChatMessage } from '../types/chat';

interface ChatContextType {
  messages: ChatMessage[];
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const addMessage = useCallback((message: ChatMessage) => {
    console.log('[ChatContext] Adding message:', message);
    setMessages(prev => {
      console.log('[ChatContext] Previous messages:', prev.length);
      const newMessages = [...prev, message];
      console.log('[ChatContext] New messages:', newMessages.length);
      return newMessages;
    });
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const setLoading = useCallback((loading: boolean) => {
    setIsLoading(loading);
  }, []);

  return (
    <ChatContext.Provider value={{
      messages,
      addMessage,
      clearMessages,
      isLoading,
      setLoading
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within ChatProvider');
  }
  return context;
};