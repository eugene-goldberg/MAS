import React, { useRef, useEffect } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ConnectionStatus } from '../Common/ConnectionStatus';
import { useChat } from '../../hooks/useChat';
import { useWebSocketContext } from '../../contexts/WebSocketContext';
import { useAgentTracking } from '../../hooks/useAgentTracking';
import './ChatInterface.scss';

export const ChatInterface: React.FC = () => {
  const { messages, addMessage, isLoading } = useChat();
  const { sendMessage, isConnected } = useWebSocketContext();
  const { startTracking } = useAgentTracking();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const handleSendMessage = async (content: string) => {
    if (!content.trim() || !isConnected) return;
    
    // Add user message
    addMessage({
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    });
    
    // Start tracking agent responses
    startTracking();
    
    // Send to backend
    await sendMessage({
      type: 'chat_message',
      content
    });
  };
  
  return (
    <Paper className="chat-interface" elevation={0}>
      <Box className="chat-header">
        <Typography variant="h6">MAS Chat</Typography>
        <ConnectionStatus connected={isConnected} />
      </Box>
      
      <Box className="chat-messages">
        <MessageList messages={messages} isLoading={isLoading} />
        <div ref={messagesEndRef} />
      </Box>
      
      <Box className="chat-input">
        <MessageInput 
          onSend={handleSendMessage} 
          disabled={!isConnected || isLoading}
        />
      </Box>
    </Paper>
  );
};