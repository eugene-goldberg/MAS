import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { SmartToy } from '@mui/icons-material';
import './Message.scss';

export const LoadingMessage: React.FC = () => {
  return (
    <Box className="message assistant">
      <Box className="message-avatar">
        <SmartToy />
      </Box>
      
      <Box className="message-content loading">
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CircularProgress size={16} />
          <Typography variant="body2" color="textSecondary">
            MAS is processing your request...
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};