import React from 'react';
import { Box, Typography, Grid, Paper } from '@mui/material';
import { MetricCard } from './MetricCard';
import { LoadingSpinner } from '../Common/LoadingSpinner';

interface AgentStats {
  avgResponseTime: number;
  totalCalls: number;
  toolUsage: Record<string, number>;
}

export const MetricsPanel: React.FC = () => {
  // Initialize with empty metrics
  const agentStats: Record<string, AgentStats> = {};
  const isLoading = false;
  
  if (isLoading) {
    return <LoadingSpinner message="Loading metrics..." />;
  }
  
  return (
    <Box className="metrics-panel">
      <Typography variant="h6" gutterBottom>
        Performance Metrics
      </Typography>
      
      <Grid container spacing={2}>
        {Object.entries(agentStats).map(([agent, stats]) => (
          <Grid item xs={12} md={6} key={agent}>
            <MetricCard
              agent={agent}
              avgResponseTime={stats.avgResponseTime}
              totalCalls={stats.totalCalls}
              toolUsage={stats.toolUsage}
            />
          </Grid>
        ))}
      </Grid>
      
      <Paper sx={{ mt: 3, p: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          System Overview
        </Typography>
        <Box sx={{ display: 'flex', gap: 3, mt: 1 }}>
          <Box>
            <Typography variant="body2" color="textSecondary">
              Total Requests
            </Typography>
            <Typography variant="h6">
              {Object.values(agentStats).reduce((sum, stats) => sum + stats.totalCalls, 0)}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="textSecondary">
              Avg Response Time
            </Typography>
            <Typography variant="h6">
              {Math.round(
                Object.values(agentStats).reduce((sum, stats) => sum + stats.avgResponseTime, 0) / 
                Object.keys(agentStats).length
              )}ms
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="textSecondary">
              Active Agents
            </Typography>
            <Typography variant="h6">
              {Object.keys(agentStats).length}
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};