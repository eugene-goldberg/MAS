import axios from 'axios';
import { ChatRequest, ChatResponse } from '../types/chat';
import { AgentInfo } from '../types/agent';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Chat endpoints
export const chatApi = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post('/api/chat/send', request);
    return response.data;
  },
  
  getHistory: async (sessionId: string, limit: number = 50) => {
    const response = await apiClient.get(`/api/chat/history/${sessionId}`, {
      params: { limit }
    });
    return response.data;
  },
  
  clearHistory: async (sessionId: string) => {
    const response = await apiClient.delete(`/api/chat/history/${sessionId}`);
    return response.data;
  }
};

// Agent endpoints
export const agentApi = {
  getInfo: async (): Promise<{ coordinator: any; agents: AgentInfo[] }> => {
    const response = await apiClient.get('/api/agents/info');
    return response.data;
  },
  
  getMetrics: async () => {
    const response = await apiClient.get('/api/agents/metrics');
    return response.data;
  },
  
  getToolUsage: async () => {
    const response = await apiClient.get('/api/agents/tools');
    return response.data;
  }
};

// Session endpoints
export const sessionApi = {
  create: async () => {
    const response = await apiClient.post('/api/sessions/create');
    return response.data;
  },
  
  get: async (sessionId: string) => {
    const response = await apiClient.get(`/api/sessions/${sessionId}`);
    return response.data;
  },
  
  listActive: async () => {
    const response = await apiClient.get('/api/sessions/active');
    return response.data;
  }
};