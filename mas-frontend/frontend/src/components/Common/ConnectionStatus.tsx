import React from 'react';
import { Chip } from '@mui/material';
import { Circle } from '@mui/icons-material';

interface ConnectionStatusProps {
  connected: boolean;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ connected }) => {
  return (
    <Chip
      icon={<Circle />}
      label={connected ? 'Connected' : 'Disconnected'}
      size="small"
      color={connected ? 'success' : 'error'}
      variant="outlined"
      sx={{
        '& .MuiChip-icon': {
          fontSize: 12,
        },
      }}
    />
  );
};