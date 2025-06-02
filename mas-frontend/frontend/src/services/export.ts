import { ChatMessage } from '../types/chat';
import { AgentResponse, ExecutionTrace } from '../types/agent';
import { downloadBlob } from '../utils/helpers';

interface ExportData {
  timestamp: string;
  sessionId?: string;
  messages: ChatMessage[];
  executionTraces?: ExecutionTrace[];
  agentResponses?: AgentResponse[];
  summary: {
    totalMessages: number;
    totalAgentCalls: number;
    avgResponseTime?: number;
    agentsUsed: string[];
    toolsUsed: string[];
  };
}

export const exportService = {
  exportChatHistory: (
    messages: ChatMessage[], 
    executionTraces?: ExecutionTrace[],
    sessionId?: string
  ) => {
    const agentsUsed = new Set<string>();
    const toolsUsed = new Set<string>();
    let totalResponseTime = 0;
    let totalAgentCalls = 0;
    
    // Analyze execution traces
    executionTraces?.forEach(trace => {
      totalResponseTime += trace.total_time_ms;
      trace.agent_responses.forEach(response => {
        agentsUsed.add(response.agent_name);
        totalAgentCalls++;
        response.tools_used.forEach(tool => {
          toolsUsed.add(tool.tool_name);
        });
      });
    });
    
    const exportData: ExportData = {
      timestamp: new Date().toISOString(),
      sessionId,
      messages,
      executionTraces,
      summary: {
        totalMessages: messages.length,
        totalAgentCalls,
        avgResponseTime: totalAgentCalls > 0 ? totalResponseTime / totalAgentCalls : 0,
        agentsUsed: Array.from(agentsUsed),
        toolsUsed: Array.from(toolsUsed)
      }
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    downloadBlob(blob, `mas-chat-export-${timestamp}.json`);
  },
  
  exportMetrics: (metrics: any) => {
    const exportData = {
      timestamp: new Date().toISOString(),
      metrics,
      generated: 'MAS Testing Interface'
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    downloadBlob(blob, `mas-metrics-export-${timestamp}.json`);
  }
};