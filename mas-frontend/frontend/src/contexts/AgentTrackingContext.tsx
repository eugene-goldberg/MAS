import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { ExecutionTrace, AgentResponse } from '../types/agent';

interface AgentTrackingContextType {
  currentExecution: ExecutionTrace | null;
  agentResponses: AgentResponse[];
  isExecuting: boolean;
  executionProgress: number;
  updateExecution: (execution: ExecutionTrace) => void;
  addToolCall: (toolCall: any) => void;
  updateProgress: (progress: number) => void;
  clearTracking: () => void;
}

const AgentTrackingContext = createContext<AgentTrackingContextType | undefined>(undefined);

export const AgentTrackingProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentExecution, setCurrentExecution] = useState<ExecutionTrace | null>(null);
  const [agentResponses, setAgentResponses] = useState<AgentResponse[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionProgress, setExecutionProgress] = useState(0);

  const updateExecution = useCallback((execution: ExecutionTrace) => {
    setCurrentExecution(execution);
    setAgentResponses(execution.agent_responses);
    setIsExecuting(false);
    setExecutionProgress(100);
  }, []);

  const addToolCall = useCallback((toolCall: any) => {
    // This would be used for real-time updates
    // For now, we'll just track the state
    setIsExecuting(true);
  }, []);

  const updateProgress = useCallback((progress: number) => {
    setExecutionProgress(progress);
  }, []);

  const clearTracking = useCallback(() => {
    setCurrentExecution(null);
    setAgentResponses([]);
    setIsExecuting(false);
    setExecutionProgress(0);
  }, []);

  return (
    <AgentTrackingContext.Provider value={{
      currentExecution,
      agentResponses,
      isExecuting,
      executionProgress,
      updateExecution,
      addToolCall,
      updateProgress,
      clearTracking
    }}>
      {children}
    </AgentTrackingContext.Provider>
  );
};

export const useAgentTracking = () => {
  const context = useContext(AgentTrackingContext);
  if (!context) {
    throw new Error('useAgentTracking must be used within AgentTrackingProvider');
  }
  return context;
};