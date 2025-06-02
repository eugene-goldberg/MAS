import React, { useState } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Chip, 
  IconButton, 
  Collapse,
  Stack,
  Divider
} from '@mui/material';
import { 
  Code, 
  CheckCircle, 
  Error as ErrorIcon,
  ExpandMore,
  ExpandLess,
  AccessTime
} from '@mui/icons-material';
import { ToolCall } from '../../types/agent';
import { formatDuration } from '../../utils/formatters';

interface ToolCallDetailProps {
  toolCall: ToolCall;
}

export const ToolCallDetail: React.FC<ToolCallDetailProps> = ({ toolCall }) => {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <Paper variant="outlined" sx={{ p: 1.5 }}>
      <Box 
        sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          cursor: 'pointer'
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Code sx={{ fontSize: 20, color: 'primary.main' }} />
          <Typography variant="subtitle2">{toolCall.tool_name}</Typography>
          <Chip 
            icon={toolCall.success ? <CheckCircle /> : <ErrorIcon />}
            label={toolCall.success ? 'Success' : 'Failed'}
            size="small"
            color={toolCall.success ? 'success' : 'error'}
            variant="outlined"
          />
          <Chip 
            icon={<AccessTime sx={{ fontSize: 14 }} />}
            label={formatDuration(toolCall.duration_ms)}
            size="small"
            variant="outlined"
          />
        </Box>
        
        <IconButton size="small">
          {expanded ? <ExpandLess /> : <ExpandMore />}
        </IconButton>
      </Box>
      
      <Collapse in={expanded}>
        <Box sx={{ mt: 2 }}>
          <Stack spacing={2} divider={<Divider />}>
            {Object.keys(toolCall.parameters).length > 0 && (
              <Box>
                <Typography variant="caption" color="textSecondary">
                  Parameters
                </Typography>
                <Box 
                  sx={{ 
                    mt: 0.5, 
                    p: 1, 
                    bgcolor: 'grey.50', 
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    fontSize: '0.875rem'
                  }}
                >
                  <pre style={{ margin: 0, overflow: 'auto' }}>
                    {JSON.stringify(toolCall.parameters, null, 2)}
                  </pre>
                </Box>
              </Box>
            )}
            
            <Box>
              <Typography variant="caption" color="textSecondary">
                Result
              </Typography>
              <Box 
                sx={{ 
                  mt: 0.5, 
                  p: 1, 
                  bgcolor: toolCall.success ? 'success.50' : 'error.50', 
                  borderRadius: 1,
                  fontFamily: 'monospace',
                  fontSize: '0.875rem'
                }}
              >
                <pre style={{ margin: 0, overflow: 'auto' }}>
                  {JSON.stringify(toolCall.result, null, 2)}
                </pre>
              </Box>
            </Box>
          </Stack>
        </Box>
      </Collapse>
    </Paper>
  );
};