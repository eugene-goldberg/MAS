import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  LinearProgress,
  Chip,
  Stack
} from '@mui/material';
import { Speed, Functions } from '@mui/icons-material';
import { getAgentColor, getAgentIcon } from '../../utils/formatters';

interface MetricCardProps {
  agent: string;
  avgResponseTime: number;
  totalCalls: number;
  toolUsage: Record<string, number>;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  agent,
  avgResponseTime,
  totalCalls,
  toolUsage
}) => {
  const totalToolCalls = Object.values(toolUsage).reduce((sum, count) => sum + count, 0);
  
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" sx={{ mr: 1 }}>
            {getAgentIcon(agent)}
          </Typography>
          <Typography variant="h6">{agent}</Typography>
        </Box>
        
        <Stack spacing={2}>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
              <Speed sx={{ fontSize: 16, mr: 0.5 }} />
              <Typography variant="body2" color="textSecondary">
                Avg Response Time
              </Typography>
            </Box>
            <Typography variant="h4">
              {avgResponseTime}ms
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Box>
              <Typography variant="body2" color="textSecondary">
                Total Calls
              </Typography>
              <Typography variant="h6">{totalCalls}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="textSecondary">
                Tool Calls
              </Typography>
              <Typography variant="h6">{totalToolCalls}</Typography>
            </Box>
          </Box>
          
          {Object.keys(toolUsage).length > 0 && (
            <Box>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Tool Usage
              </Typography>
              <Stack direction="row" spacing={0.5} flexWrap="wrap">
                {Object.entries(toolUsage).map(([tool, count]) => (
                  <Chip 
                    key={tool}
                    label={`${tool} (${count})`}
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Stack>
            </Box>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
};