import { useState, useCallback, useRef, useEffect } from 'react';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);
  const messageHandlers = useRef<Map<string, Set<(data: any) => void>>>(new Map());
  const isConnecting = useRef(false);

  const connect = useCallback(() => {
    // Prevent multiple simultaneous connections
    if (isConnecting.current || (ws.current && ws.current.readyState === WebSocket.OPEN)) {
      console.log('Already connected or connecting');
      return;
    }

    // Close existing connection if any
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }

    try {
      isConnecting.current = true;
      
      // Generate a unique session ID
      const sessionId = localStorage.getItem('sessionId') || crypto.randomUUID();
      localStorage.setItem('sessionId', sessionId);

      // Connect to backend WebSocket
      const wsUrl = `ws://localhost:8000/ws/chat/${sessionId}`;
      console.log('Connecting to WebSocket:', wsUrl);
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        isConnecting.current = false;
        
        // Clear any reconnect timer
        if (reconnectTimer.current) {
          clearTimeout(reconnectTimer.current);
          reconnectTimer.current = null;
        }
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message received:', data);

          // Handle different message types
          if (data.type === 'connection_established') {
            console.log('Connection established with session:', data.session_id);
          } else if (data.type === 'message_received') {
            console.log('Message acknowledged:', data.message_id);
            const handlers = messageHandlers.current.get('message_received');
            if (handlers) {
              handlers.forEach(handler => handler(data));
            }
          } else if (data.type === 'agent_response') {
            // Forward to chat handler
            console.log('Agent response received:', data);
            const handlers = messageHandlers.current.get('agent_response');
            console.log('Handlers found:', handlers?.size || 0);
            if (handlers) {
              console.log(`Calling ${handlers.size} agent_response handlers`);
              handlers.forEach(handler => handler(data));
            } else {
              console.log('No agent_response handlers registered!');
            }
          } else if (data.type === 'error') {
            console.error('WebSocket error:', data.error);
            const handlers = messageHandlers.current.get('error');
            if (handlers) {
              handlers.forEach(handler => handler(data));
            }
          } else if (data.type === 'heartbeat') {
            // Respond to heartbeat
            if (ws.current?.readyState === WebSocket.OPEN) {
              ws.current.send(JSON.stringify({ type: 'pong' }));
            }
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        console.error('WebSocket readyState:', ws.current?.readyState);
        setIsConnected(false);
        isConnecting.current = false;
      };

      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        isConnecting.current = false;
        ws.current = null;

        // Only reconnect if not a normal closure
        if (event.code !== 1000 && event.code !== 1001) {
          // Attempt to reconnect after 3 seconds
          reconnectTimer.current = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connect();
          }, 3000);
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      setIsConnected(false);
      isConnecting.current = false;
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }

    if (ws.current) {
      ws.current.close(1000, 'User disconnect');
      ws.current = null;
    }
    setIsConnected(false);
    isConnecting.current = false;
  }, []);

  const sendMessage = useCallback(async (message: WebSocketMessage) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected. State:', ws.current?.readyState);
      throw new Error('WebSocket is not connected');
    }

    try {
      ws.current.send(JSON.stringify(message));
      console.log('Message sent:', message);
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }, []);

  const registerHandler = useCallback((type: string, handler: (data: any) => void) => {
    console.log(`[WebSocket] Registering handler for: ${type}`);
    
    if (!messageHandlers.current.has(type)) {
      messageHandlers.current.set(type, new Set());
    }
    
    const handlers = messageHandlers.current.get(type)!;
    handlers.add(handler);
    
    return () => {
      console.log(`[WebSocket] Unregistering handler for: ${type}`);
      const handlers = messageHandlers.current.get(type);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          messageHandlers.current.delete(type);
        }
      }
    };
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    let mounted = true;
    console.log('[useWebSocket] Effect running');
    
    // Delay connection slightly to avoid StrictMode double-mount issues
    const timer = setTimeout(() => {
      if (mounted && !isConnecting.current && !ws.current) {
        console.log('[useWebSocket] Connecting...');
        connect();
      }
    }, 100);
    
    return () => {
      mounted = false;
      clearTimeout(timer);
      console.log('[useWebSocket] Cleanup function called');
      // Don't disconnect here - let the component handle it
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array - connect only once

  return {
    isConnected,
    connect,
    disconnect,
    sendMessage,
    registerHandler
  };
};