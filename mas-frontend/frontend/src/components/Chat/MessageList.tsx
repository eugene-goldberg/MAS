import React from 'react';
import { Box } from '@mui/material';
import { Message } from './Message';
import { LoadingMessage } from './LoadingMessage';
import { ChatMessage } from '../../types/chat';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  console.log('[MessageList] Rendering with:', messages.length, 'messages, loading:', isLoading);
  console.log('[MessageList] Messages:', messages);
  
  return (
    <Box className="message-list">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      {isLoading && <LoadingMessage />}
    </Box>
  );
};