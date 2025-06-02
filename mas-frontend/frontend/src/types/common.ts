export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface Session {
  id: string;
  created_at: Date;
  last_activity: Date;
  user_id?: string;
  is_active: boolean;
}