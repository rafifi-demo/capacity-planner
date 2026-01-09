// Agent status types
export type AgentStatus = 'pending' | 'running' | 'completed' | 'error';

// Agent metrics
export interface AgentMetrics {
  input_tokens: number;
  output_tokens: number;
  duration_ms: number;
  cost_usd: number;
  tool_calls: number;
}

// Agent update from WebSocket
export interface AgentUpdate {
  agent_id: string;
  agent_name: string;
  status: AgentStatus;
  input_text?: string;
  output_text?: string;
  tool_use?: {
    tools?: string[];
    documents?: string[];
    code_executed?: boolean;
  };
  metrics?: AgentMetrics;
  timestamp: string;
}

// Agent info for display
export interface AgentInfo {
  id: string;
  name: string;
  description: string;
  tool: string;
  icon: string;
  color: string;
}

// Telemetry data
export interface TelemetryMetrics {
  session_id: string;
  total_input_tokens: number;
  total_output_tokens: number;
  total_tokens: number;
  total_cost_usd: number;
  total_duration_ms: number;
  agents_completed: number;
  agents_total: number;
  agent_metrics: Record<string, AgentMetrics>;
}

// Human approval request
export interface ApprovalRequest {
  session_id: string;
  plan_summary: string;
  proposed_actions: ProposedAction[];
  total_cost_estimate: number;
  aircraft_assignments: AircraftAssignment[];
  crew_assignments: CrewAssignment[];
  timestamp: string;
}

export interface ProposedAction {
  action_id: string;
  action: string;
  description: string;
  estimated_cost: number;
}

export interface AircraftAssignment {
  route: string;
  aircraft: string;
  cargo_kg: number;
}

export interface CrewAssignment {
  flight: string;
  captain: string;
  first_officer: string;
  flight_engineer?: string;
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'connected' | 'agent_update' | 'approval_request' | 'telemetry' | 'approval_response' | 'workflow_complete' | 'error' | 'pong';
  payload?: AgentUpdate | ApprovalRequest | TelemetryMetrics | {
    approved?: boolean;
    message?: string;
    status?: string;
    session_id?: string;
    telemetry?: TelemetryMetrics;
  };
  session_id?: string;
  message?: string;
}

// Workflow state
export interface WorkflowState {
  sessionId: string | null;
  status: 'idle' | 'running' | 'awaiting_approval' | 'completed' | 'error';
  agents: Record<string, AgentUpdate>;
  telemetry: TelemetryMetrics | null;
  approvalRequest: ApprovalRequest | null;
  error: string | null;
}

// API types
export interface StartWorkflowRequest {
  date_from: string;
  date_to: string;
  hub: string;
  demo_mode: boolean;
}

export interface StartWorkflowResponse {
  session_id: string;
  status: string;
  message: string;
  websocket_url: string;
}
