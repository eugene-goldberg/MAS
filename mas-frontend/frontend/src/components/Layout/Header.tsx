import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { SmartToy } from '@mui/icons-material';

export const Header: React.FC = () => {
  return (
    <AppBar position="static" elevation={0}>
      <Toolbar>
        <SmartToy sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          MAS Testing Interface
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            Real-time Multi-Agent System Visualization
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};