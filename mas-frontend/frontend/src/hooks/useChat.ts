import { useState, useEffect } from 'react';
import { useWebSocketContext } from '../contexts/WebSocketContext';
import { useChat as useChatContext } from '../contexts/ChatContext';

export const useChat = () => {
  const { messages, addMessage, clearMessages, isLoading, setLoading } = useChatContext();
  const [sessionId] = useState(() => 
    localStorage.getItem('sessionId') || crypto.randomUUID()
  );
  
  const { registerHandler } = useWebSocketContext();
  
  // Register WebSocket message handlers
  useEffect(() => {
    const handlerId = Math.random().toString(36).substring(7);
    console.log(`[useChat] Registering handlers with ID: ${handlerId}`);
    
    // Handle agent responses
    const unregisterAgentResponse = registerHandler('agent_response', (data: any) => {
      console.log(`[useChat ${handlerId}] Received agent response:`, data);
      console.log(`[useChat ${handlerId}] Current loading state before:`, isLoading);
      
      // Add assistant message
      const assistantMessage = {
        id: data.message_id || crypto.randomUUID(),
        role: 'assistant' as const,
        content: data.content,
        timestamp: new Date(),
        agentResponses: data.agent_responses
      };
      
      console.log(`[useChat ${handlerId}] Adding assistant message:`, assistantMessage);
      addMessage(assistantMessage);
      console.log(`[useChat ${handlerId}] Setting loading to false`);
      setLoading(false);
    });
    
    // Handle errors
    const unregisterError = registerHandler('error', (data: any) => {
      console.error('Chat error:', data);
      
      // Add error message as assistant message with error formatting
      const errorMessage = {
        id: crypto.randomUUID(),
        role: 'assistant' as const,
        content: `⚠️ Error: ${data.error}`,
        timestamp: new Date()
      };
      
      addMessage(errorMessage);
      setLoading(false);
    });
    
    // Handle message acknowledgment
    const unregisterAck = registerHandler('message_received', (data: any) => {
      console.log('Message acknowledged:', data.message_id);
      setLoading(true);
    });
    
    return () => {
      console.log(`[useChat] Cleaning up handlers with ID: ${handlerId}`);
      unregisterAgentResponse();
      unregisterError();
      unregisterAck();
    };
  }, [registerHandler, addMessage, setLoading]);
  
  return {
    messages,
    addMessage,
    isLoading,
    clearMessages,
    sessionId
  };
};