import React, { useState } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Collapse, 
  IconButton,
  Chip,
  Stack
} from '@mui/material';
import { 
  ExpandMore, 
  ExpandLess, 
  AccessTime,
  Build
} from '@mui/icons-material';
import { AgentResponse } from '../../types/agent';
import { ToolCallDetail } from './ToolCallDetail';
import { getAgentColor, getAgentIcon } from '../../utils/formatters';
import './AgentCard.scss';

interface AgentCardProps {
  response: AgentResponse;
}

export const AgentCard: React.FC<AgentCardProps> = ({ response }) => {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <Card className={`agent-card ${response.agent_type}`}>
      <CardContent>
        <Box 
          className="agent-header" 
          onClick={() => setExpanded(!expanded)}
          sx={{ cursor: 'pointer' }}
        >
          <Box className="agent-info">
            <Typography variant="h5" className="agent-icon">
              {getAgentIcon(response.agent_name)}
            </Typography>
            <Box>
              <Typography variant="h6">{response.agent_name}</Typography>
              <Typography variant="body2" color="textSecondary">
                {response.agent_type}
              </Typography>
            </Box>
          </Box>
          
          <Box className="agent-stats">
            <Stack direction="row" spacing={1}>
              <Chip 
                icon={<Build sx={{ fontSize: 16 }} />}
                label={`${response.tools_used.length} tools`} 
                size="small"
                variant="outlined"
              />
              <Chip 
                icon={<AccessTime sx={{ fontSize: 16 }} />}
                label={`${response.processing_time_ms}ms`} 
                size="small"
                variant="outlined"
              />
            </Stack>
            <IconButton size="small">
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
        </Box>
        
        <Collapse in={expanded}>
          <Box className="agent-details">
            <Box className="response-section">
              <Typography variant="subtitle2" gutterBottom>
                Response
              </Typography>
              <Typography variant="body2" className="response-text">
                {response.response}
              </Typography>
            </Box>
            
            {response.tools_used.length > 0 && (
              <Box className="tools-section">
                <Typography variant="subtitle2" gutterBottom>
                  Tools Used
                </Typography>
                <Stack spacing={1}>
                  {response.tools_used.map((tool, idx) => (
                    <ToolCallDetail key={idx} toolCall={tool} />
                  ))}
                </Stack>
              </Box>
            )}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};