"""
Pydantic schemas for Zava Capacity Planner API.
Defines request/response models and WebSocket message types.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, date


class AgentStatus(str, Enum):
    """Status of an agent in the workflow."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class WorkflowRequest(BaseModel):
    """Request to start a capacity planning workflow."""
    date_from: date = Field(..., description="Start date for shipment analysis")
    date_to: date = Field(..., description="End date for shipment analysis")
    hub: str = Field(default="Seattle", description="Hub location to analyze")

    class Config:
        json_schema_extra = {
            "example": {
                "date_from": "2026-01-01",
                "date_to": "2026-01-31",
                "hub": "Seattle"
            }
        }


class AgentMetrics(BaseModel):
    """Metrics for a single agent execution."""
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0
    cost_usd: float = 0.0
    tool_calls: int = 0


class AgentUpdate(BaseModel):
    """WebSocket message for agent status updates."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    agent_name: str = Field(..., description="Display name of the agent")
    status: AgentStatus = Field(..., description="Current status")
    input_text: Optional[str] = Field(None, description="Input provided to agent")
    output_text: Optional[str] = Field(None, description="Output from agent")
    tool_use: Optional[Dict[str, Any]] = Field(None, description="Tool usage details")
    metrics: Optional[AgentMetrics] = Field(None, description="Execution metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "data_analyst",
                "agent_name": "Data Analyst",
                "status": "completed",
                "input_text": "Query shipments for January 2026 from Seattle hub",
                "output_text": "Found 487 shipments totaling 125,000 kg...",
                "tool_use": {"tool": "get_shipments", "params": {"date_from": "2026-01-01"}},
                "metrics": {"input_tokens": 150, "output_tokens": 500, "duration_ms": 2500}
            }
        }


class HumanApprovalRequest(BaseModel):
    """Request for human approval before executing the capacity plan."""
    session_id: str = Field(..., description="Workflow session identifier")
    plan_summary: str = Field(..., description="Summary of the proposed capacity plan")
    proposed_actions: List[Dict[str, Any]] = Field(..., description="Actions requiring approval")
    total_cost_estimate: float = Field(..., description="Estimated cost of the plan")
    aircraft_assignments: List[Dict[str, Any]] = Field(..., description="Proposed aircraft assignments")
    crew_assignments: List[Dict[str, Any]] = Field(..., description="Proposed crew assignments")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ApprovalResponse(BaseModel):
    """Response for approval/rejection of capacity plan."""
    session_id: str = Field(..., description="Workflow session identifier")
    approved: bool = Field(..., description="Whether the plan was approved")
    comments: Optional[str] = Field(None, description="Optional comments from approver")


class TelemetryMetrics(BaseModel):
    """Aggregated telemetry metrics for the workflow."""
    session_id: str
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_duration_ms: int = 0
    agents_completed: int = 0
    agents_total: int = 4
    agent_metrics: Dict[str, AgentMetrics] = Field(default_factory=dict)

    def add_agent_metrics(self, agent_id: str, metrics: AgentMetrics):
        """Add metrics from an agent execution."""
        self.agent_metrics[agent_id] = metrics
        self.total_input_tokens += metrics.input_tokens
        self.total_output_tokens += metrics.output_tokens
        self.total_tokens = self.total_input_tokens + self.total_output_tokens
        self.total_cost_usd += metrics.cost_usd
        self.total_duration_ms += metrics.duration_ms
        self.agents_completed += 1


class WorkflowResponse(BaseModel):
    """Response after workflow completion."""
    session_id: str
    status: str
    message: str
    telemetry: Optional[TelemetryMetrics] = None


class WebSocketMessage(BaseModel):
    """Generic WebSocket message wrapper."""
    type: str = Field(..., description="Message type: agent_update, approval_request, telemetry, error")
    payload: Dict[str, Any] = Field(..., description="Message payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
