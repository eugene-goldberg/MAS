export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  execution_trace?: ExecutionTrace;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  execution_trace: ExecutionTrace;
  session_id: string;
}

import { ExecutionTrace } from './agent';