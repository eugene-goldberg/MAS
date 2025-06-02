export interface ToolCall {
  tool_name: string;
  tool_type: string;
  parameters: Record<string, any>;
  result: Record<string, any>;
  duration_ms: number;
  timestamp: Date;
  success: boolean;
}

export interface AgentResponse {
  agent_name: string;
  agent_type: string;
  response: string;
  tools_used: ToolCall[];
  processing_time_ms: number;
  timestamp: Date;
}

export interface ExecutionTrace {
  session_id: string;
  request_id: string;
  user_message: string;
  coordinator_response: string;
  agent_sequence: string[];
  total_time_ms: number;
  agent_responses: AgentResponse[];
  timestamp: Date;
}

export interface AgentInfo {
  name: string;
  type: string;
  description: string;
  tools: string[];
  color: string;
  icon: string;
}