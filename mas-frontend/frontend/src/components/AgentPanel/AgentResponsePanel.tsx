import React, { useState } from 'react';
import { Box, Paper, Typography, Tabs, Tab, Chip } from '@mui/material';
import { AgentCard } from './AgentCard';
import { ToolTimeline } from './ToolTimeline';
import { MetricsPanel } from '../Metrics/MetricsPanel';
import { useAgentTracking } from '../../hooks/useAgentTracking';
import './AgentResponsePanel.scss';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div hidden={value !== index}>
      {value === index && <Box p={2}>{children}</Box>}
    </div>
  );
};

export const AgentResponsePanel: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const { 
    currentExecution, 
    agentResponses, 
    isExecuting,
    executionProgress 
  } = useAgentTracking();
  
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  return (
    <Paper className="agent-response-panel" elevation={0}>
      <Box className="panel-header">
        <Typography variant="h6">Agent Activity</Typography>
        {isExecuting && (
          <Chip 
            label={`Processing... ${executionProgress}%`} 
            color="primary" 
            size="small"
          />
        )}
      </Box>
      
      <Tabs value={tabValue} onChange={handleTabChange}>
        <Tab label="Timeline" />
        <Tab label="Responses" />
        <Tab label="Metrics" />
      </Tabs>
      
      <TabPanel value={tabValue} index={0}>
        <ToolTimeline execution={currentExecution} />
      </TabPanel>
      
      <TabPanel value={tabValue} index={1}>
        <Box className="agents-list">
          {agentResponses.map((response, idx) => (
            <AgentCard key={idx} response={response} />
          ))}
        </Box>
      </TabPanel>
      
      <TabPanel value={tabValue} index={2}>
        <MetricsPanel />
      </TabPanel>
    </Paper>
  );
};