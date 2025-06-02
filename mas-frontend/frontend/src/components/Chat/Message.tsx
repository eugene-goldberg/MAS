import React from 'react';
import { Box, Paper, Typography, Chip } from '@mui/material';
import { Person, SmartToy } from '@mui/icons-material';
import { format } from 'date-fns';
import { ChatMessage } from '../../types/chat';
import './Message.scss';

interface MessageProps {
  message: ChatMessage;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <Box className={`message ${isUser ? 'user' : 'assistant'}`}>
      <Box className="message-avatar">
        {isUser ? <Person /> : <SmartToy />}
      </Box>
      
      <Paper className="message-content" elevation={0}>
        <Box className="message-header">
          <Typography variant="subtitle2" className="message-role">
            {isUser ? 'You' : 'MAS Assistant'}
          </Typography>
          <Typography variant="caption" className="message-time">
            {format(new Date(message.timestamp), 'HH:mm')}
          </Typography>
        </Box>
        
        <Typography variant="body1" className="message-text">
          {message.content}
        </Typography>
        
        {message.execution_trace && (
          <Box className="message-metadata">
            <Chip 
              size="small" 
              label={`${message.execution_trace.agent_sequence.length} agents`}
              variant="outlined"
            />
            <Chip 
              size="small" 
              label={`${message.execution_trace.total_time_ms}ms`}
              variant="outlined"
            />
          </Box>
        )}
      </Paper>
    </Box>
  );
};