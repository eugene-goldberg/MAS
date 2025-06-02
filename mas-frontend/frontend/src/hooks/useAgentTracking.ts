import { useState, useEffect, useCallback } from 'react';
import { useWebSocketContext } from '../contexts/WebSocketContext';
import { AgentResponse, ExecutionTrace } from '../types/agent';

export const useAgentTracking = () => {
  const [currentExecution, setCurrentExecution] = useState<ExecutionTrace | null>(null);
  const [agentResponses, setAgentResponses] = useState<AgentResponse[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionProgress, setExecutionProgress] = useState(0);
  
  const { registerHandler } = useWebSocketContext();

  useEffect(() => {
    // Register handler for agent responses
    const unregisterAgentResponse = registerHandler('agent_response', (data) => {
      console.log('Agent response received:', data);
      
      // The backend sends agent_responses as an array
      if (data.agent_responses && Array.isArray(data.agent_responses)) {
        const responses: AgentResponse[] = data.agent_responses.map((resp: any) => ({
          agent_name: resp.agent_name || 'Unknown Agent',
          agent_type: resp.agent_type || 'unknown',
          response: resp.response || '',
          tools_used: resp.tools_used || [],
          processing_time_ms: resp.processing_time_ms || 0,
          timestamp: new Date(resp.timestamp || Date.now())
        }));
        
        setAgentResponses(responses);
        setIsExecuting(false);
        setExecutionProgress(100);
      }
    });
    
    // Register handler for execution updates
    const unregisterExecution = registerHandler('execution_update', (data) => {
      console.log('Execution update:', data);
      
      if (data.agent_name) {
        // This is a single agent update during execution
        const response: AgentResponse = {
          agent_name: data.agent_name,
          agent_type: data.agent_type || 'unknown',
          response: data.response || 'Processing...',
          tools_used: data.tools_used || [],
          processing_time_ms: data.processing_time_ms || 0,
          timestamp: new Date(data.timestamp || Date.now())
        };
        
        setAgentResponses(prev => [...prev, response]);
        setIsExecuting(true);
        
        // Update progress
        if (data.agent_sequence && data.current_agent_index !== undefined) {
          const progress = ((data.current_agent_index + 1) / data.agent_sequence.length) * 100;
          setExecutionProgress(progress);
        }
      }
    });

    return () => {
      unregisterAgentResponse();
      unregisterExecution();
    };
  }, [registerHandler]);

  const startTracking = useCallback(() => {
    setIsExecuting(true);
    setExecutionProgress(0);
    // Don't clear agent responses here - let them accumulate
    // setAgentResponses([]);
    setCurrentExecution(null);
  }, []);

  const stopTracking = useCallback(() => {
    setIsExecuting(false);
    setExecutionProgress(100);
  }, []);

  const updateProgress = useCallback((progress: number) => {
    setExecutionProgress(progress);
  }, []);

  return {
    currentExecution,
    agentResponses,
    isExecuting,
    executionProgress,
    startTracking,
    stopTracking,
    updateProgress,
  };
};