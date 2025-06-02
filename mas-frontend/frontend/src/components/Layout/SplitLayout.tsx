import React from 'react';
import { Box } from '@mui/material';

interface SplitLayoutProps {
  left: React.ReactNode;
  right: React.ReactNode;
}

export const SplitLayout: React.FC<SplitLayoutProps> = ({ left, right }) => {
  return (
    <Box className="split-layout">
      <Box className="split-panel left">
        {left}
      </Box>
      <Box className="split-panel right">
        {right}
      </Box>
    </Box>
  );
};