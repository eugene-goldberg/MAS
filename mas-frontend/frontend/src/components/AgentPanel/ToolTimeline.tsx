import React from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';
import Timeline from '@mui/lab/Timeline';
import TimelineItem from '@mui/lab/TimelineItem';
import TimelineSeparator from '@mui/lab/TimelineSeparator';
import TimelineConnector from '@mui/lab/TimelineConnector';
import TimelineContent from '@mui/lab/TimelineContent';
import TimelineDot from '@mui/lab/TimelineDot';
import { ExecutionTrace, ToolCall } from '../../types/agent';
import { getAgentColor, getAgentIcon, formatDuration } from '../../utils/formatters';
import './ToolTimeline.scss';

interface TimelineEvent {
  type: 'agent_start' | 'tool_call' | 'agent_complete';
  agent: string;
  tool?: string;
  timestamp: Date;
  duration?: number;
  status?: 'running' | 'complete' | 'error';
}

export const ToolTimeline: React.FC<{ execution?: ExecutionTrace | null }> = ({ execution }) => {
  if (!execution) {
    return (
      <Box className="timeline-empty">
        <Typography variant="body2" color="textSecondary">
          No execution data yet. Send a message to see the agent activity timeline.
        </Typography>
      </Box>
    );
  }
  
  // Convert execution data to timeline events
  const events: TimelineEvent[] = [];
  
  execution.agent_responses.forEach(agentResponse => {
    // Agent start
    events.push({
      type: 'agent_start',
      agent: agentResponse.agent_name,
      timestamp: new Date(agentResponse.timestamp),
      status: 'complete'
    });
    
    // Tool calls
    agentResponse.tools_used.forEach(tool => {
      events.push({
        type: 'tool_call',
        agent: agentResponse.agent_name,
        tool: tool.tool_name,
        timestamp: new Date(tool.timestamp),
        duration: tool.duration_ms,
        status: 'complete'
      });
    });
    
    // Agent complete
    events.push({
      type: 'agent_complete',
      agent: agentResponse.agent_name,
      timestamp: new Date(agentResponse.timestamp),
      duration: agentResponse.processing_time_ms,
      status: 'complete'
    });
  });
  
  // Sort by timestamp
  events.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  
  return (
    <Box className="tool-timeline">
      <Timeline position="right">
        {events.map((event, index) => (
          <TimelineItem key={index}>
            <TimelineSeparator>
              <TimelineDot 
                sx={{ 
                  bgcolor: getAgentColor(event.agent),
                  width: event.type === 'tool_call' ? 8 : 12,
                  height: event.type === 'tool_call' ? 8 : 12
                }}
              >
                {event.type !== 'tool_call' && getAgentIcon(event.agent)}
              </TimelineDot>
              {index < events.length - 1 && <TimelineConnector />}
            </TimelineSeparator>
            
            <TimelineContent>
              <Box className={`timeline-event ${event.type}`}>
                <Typography variant="subtitle2" className="event-title">
                  {event.type === 'agent_start' && `${event.agent} Started`}
                  {event.type === 'tool_call' && `Tool: ${event.tool}`}
                  {event.type === 'agent_complete' && `${event.agent} Complete`}
                </Typography>
                
                {event.duration && (
                  <Typography variant="caption" color="textSecondary">
                    {formatDuration(event.duration)}
                  </Typography>
                )}
                
                {event.status === 'running' && (
                  <LinearProgress 
                    variant="indeterminate" 
                    sx={{ mt: 0.5, height: 2 }}
                  />
                )}
              </Box>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
      
      <Box className="timeline-summary">
        <Typography variant="caption" color="textSecondary">
          Total execution time: {formatDuration(execution.total_time_ms)}
        </Typography>
      </Box>
    </Box>
  );
};