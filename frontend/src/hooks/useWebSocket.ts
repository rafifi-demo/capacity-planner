import { useState, useEffect, useCallback, useRef } from 'react';
import type { WebSocketMessage, WorkflowState, AgentUpdate, ApprovalRequest, TelemetryMetrics } from '../types';

const API_URL = import.meta.env.VITE_API_URL || '';

export function useWebSocket() {
  const [state, setState] = useState<WorkflowState>({
    sessionId: null,
    status: 'idle',
    agents: {},
    telemetry: null,
    approvalRequest: null,
    error: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  // Connect to WebSocket
  const connect = useCallback((sessionId: string) => {
    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Determine WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = API_URL ? new URL(API_URL).host : window.location.host;
    const wsUrl = `${protocol}//${host}/ws/${sessionId}`;

    console.log('Connecting to WebSocket:', wsUrl);

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setState(prev => ({
        ...prev,
        sessionId,
        status: 'running',
        error: null,
      }));
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        console.log('WebSocket message:', message.type, message);

        switch (message.type) {
          case 'connected':
            console.log('Connected to session:', message.session_id);
            break;

          case 'agent_update':
            const agentUpdate = message.payload as AgentUpdate;
            setState(prev => ({
              ...prev,
              agents: {
                ...prev.agents,
                [agentUpdate.agent_id]: agentUpdate,
              },
            }));
            break;

          case 'telemetry':
            setState(prev => ({
              ...prev,
              telemetry: message.payload as TelemetryMetrics,
            }));
            break;

          case 'approval_request':
            setState(prev => ({
              ...prev,
              status: 'awaiting_approval',
              approvalRequest: message.payload as ApprovalRequest,
            }));
            break;

          case 'approval_response':
            const approvalPayload = message.payload as { approved: boolean; message: string };
            setState(prev => ({
              ...prev,
              status: approvalPayload.approved ? 'running' : 'completed',
            }));
            break;

          case 'workflow_complete':
            const completePayload = message.payload as { status: string; telemetry: TelemetryMetrics };
            setState(prev => ({
              ...prev,
              status: 'completed',
              telemetry: completePayload?.telemetry || prev.telemetry,
            }));
            break;

          case 'error':
            setState(prev => ({
              ...prev,
              status: 'error',
              error: message.message || 'An error occurred',
            }));
            break;

          case 'pong':
            // Heartbeat response
            break;
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setState(prev => ({
        ...prev,
        error: 'Connection error',
      }));
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
      // Only reconnect if we're still in running state
      if (state.status === 'running') {
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect(sessionId);
        }, 3000);
      }
    };

    wsRef.current = ws;
  }, [state.status]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  // Send message via WebSocket
  const sendMessage = useCallback((type: string, data?: Record<string, unknown>) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, ...data }));
    }
  }, []);

  // Approve workflow
  const approve = useCallback((comments?: string) => {
    sendMessage('approve', { comments });
    setState(prev => ({
      ...prev,
      status: 'running',
    }));
  }, [sendMessage]);

  // Reject workflow - resets and re-runs
  const reject = useCallback((comments?: string) => {
    sendMessage('reject', { comments });
    // Reset agents and approval to re-run workflow
    setState(prev => ({
      ...prev,
      status: 'running',
      agents: {},
      approvalRequest: null,
    }));
  }, [sendMessage]);

  // Reset state
  const reset = useCallback(() => {
    disconnect();
    setState({
      sessionId: null,
      status: 'idle',
      agents: {},
      telemetry: null,
      approvalRequest: null,
      error: null,
    });
  }, [disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  // Heartbeat
  useEffect(() => {
    const interval = setInterval(() => {
      sendMessage('ping');
    }, 30000);

    return () => clearInterval(interval);
  }, [sendMessage]);

  return {
    state,
    connect,
    disconnect,
    approve,
    reject,
    reset,
  };
}
