"""
Zava Capacity Planner - FastAPI Backend

This is the main entry point for the Zava Capacity Planner API.
It provides REST endpoints and WebSocket connections for the
capacity planning workflow.

ENDPOINTS:
- GET /health - Health check
- POST /api/workflow/start - Start capacity planning workflow
- POST /api/workflow/{session_id}/approve - Approve capacity plan
- POST /api/workflow/{session_id}/reject - Reject capacity plan
- GET /api/telemetry/{session_id} - Get telemetry data
- WS /ws/{session_id} - WebSocket for real-time updates
"""
import asyncio
import os
from contextlib import asynccontextmanager
from datetime import date
from typing import Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import get_settings
from .models import WorkflowRequest, WorkflowResponse, ApprovalResponse, AgentUpdate
from .agents import CapacityPlanningWorkflow
from .websocket.handler import ws_manager
from .telemetry import configure_telemetry


# Store active workflows
active_workflows: Dict[str, CapacityPlanningWorkflow] = {}
# Store workflow requests for re-running
workflow_requests: Dict[str, WorkflowRequest] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    settings = get_settings()

    # Configure OpenTelemetry
    if settings.applicationinsights_connection_string:
        configure_telemetry(settings.applicationinsights_connection_string)
    else:
        configure_telemetry()  # Console output for development

    yield

    # Cleanup
    active_workflows.clear()


# Create FastAPI application
app = FastAPI(
    title="Zava Capacity Planner API",
    description="""
    API for the Zava Capacity Planning Demo Application.

    This API demonstrates Microsoft Foundry V1 Agents working together
    in a sequential workflow for logistics capacity planning.

    ## Features
    - Sequential 4-agent workflow
    - Real-time WebSocket updates
    - Human-in-the-loop approval
    - OpenTelemetry integration
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "service": "zava-capacity-planner",
        "version": "1.0.0",
        "active_workflows": len(active_workflows),
        "active_connections": ws_manager.total_connections
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Zava Capacity Planner API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================================================
# WORKFLOW ENDPOINTS
# ============================================================================

class StartWorkflowRequest(BaseModel):
    """Request to start a new capacity planning workflow."""
    date_from: date
    date_to: date
    hub: str = "Seattle"
    demo_mode: bool = True


class StartWorkflowResponse(BaseModel):
    """Response after starting a workflow."""
    session_id: str
    status: str
    message: str
    websocket_url: str


@app.post("/api/workflow/start", response_model=StartWorkflowResponse)
async def start_workflow(
    request: StartWorkflowRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new capacity planning workflow.

    This endpoint:
    1. Creates a new workflow instance
    2. Returns the session ID immediately
    3. Runs the workflow in the background
    4. Streams updates via WebSocket

    Connect to the WebSocket at /ws/{session_id} to receive real-time updates.
    """
    # Create workflow instance
    workflow = CapacityPlanningWorkflow(demo_mode=request.demo_mode)
    session_id = workflow.session_id

    # Create the workflow request
    workflow_request = WorkflowRequest(
        date_from=request.date_from,
        date_to=request.date_to,
        hub=request.hub
    )

    # Store workflow and request for later access
    active_workflows[session_id] = workflow
    workflow_requests[session_id] = workflow_request

    # Run workflow in background
    background_tasks.add_task(run_workflow_background, workflow, workflow_request)

    return StartWorkflowResponse(
        session_id=session_id,
        status="started",
        message="Workflow started. Connect to WebSocket for real-time updates.",
        websocket_url=f"/ws/{session_id}"
    )


async def run_workflow_background(workflow: CapacityPlanningWorkflow, request: WorkflowRequest):
    """Run the workflow and broadcast updates via WebSocket."""
    try:
        async for update in workflow.run(request):
            # Broadcast update to all clients watching this session
            if isinstance(update, AgentUpdate):
                await ws_manager.send_to_session(
                    workflow.session_id,
                    {
                        "type": "agent_update",
                        "payload": update.model_dump()
                    }
                )
            elif hasattr(update, 'model_dump'):  # HumanApprovalRequest
                await ws_manager.send_to_session(
                    workflow.session_id,
                    {
                        "type": "approval_request",
                        "payload": update.model_dump()
                    }
                )
            elif isinstance(update, dict):
                await ws_manager.send_to_session(
                    workflow.session_id,
                    update
                )

            # Also send telemetry update
            await ws_manager.send_to_session(
                workflow.session_id,
                {
                    "type": "telemetry",
                    "payload": workflow.telemetry.model_dump()
                }
            )

    except Exception as e:
        await ws_manager.send_to_session(
            workflow.session_id,
            {
                "type": "error",
                "message": str(e)
            }
        )


@app.post("/api/workflow/{session_id}/approve")
async def approve_workflow(session_id: str, comments: str = ""):
    """
    Approve the capacity plan.

    This triggers the workflow to proceed with execution.
    """
    workflow = active_workflows.get(session_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.approve(approved=True, comments=comments)

    # Notify clients
    await ws_manager.send_to_session(
        session_id,
        {
            "type": "approval_response",
            "payload": {
                "approved": True,
                "comments": comments,
                "message": "Capacity plan approved for execution"
            }
        }
    )

    return {"status": "approved", "session_id": session_id}


@app.post("/api/workflow/{session_id}/reject")
async def reject_workflow(session_id: str, comments: str = ""):
    """
    Reject the capacity plan.

    This ends the workflow without execution.
    """
    workflow = active_workflows.get(session_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.approve(approved=False, comments=comments)

    # Notify clients
    await ws_manager.send_to_session(
        session_id,
        {
            "type": "approval_response",
            "payload": {
                "approved": False,
                "comments": comments,
                "message": "Capacity plan rejected"
            }
        }
    )

    return {"status": "rejected", "session_id": session_id}


@app.get("/api/workflow/{session_id}")
async def get_workflow_status(session_id: str):
    """Get the current status of a workflow."""
    workflow = active_workflows.get(session_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return {
        "session_id": session_id,
        "state": workflow.state.value,
        "telemetry": workflow.telemetry.model_dump()
    }


# ============================================================================
# TELEMETRY ENDPOINTS
# ============================================================================

@app.get("/api/telemetry/{session_id}")
async def get_telemetry(session_id: str):
    """Get detailed telemetry for a workflow session."""
    workflow = active_workflows.get(session_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow.telemetry.model_dump()


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time workflow updates.

    Connect to this endpoint to receive:
    - Agent status updates
    - Telemetry data
    - Approval requests
    - Workflow completion/error notifications
    """
    await ws_manager.connect(websocket, session_id)

    # Send initial connection confirmation
    await websocket.send_json({
        "type": "connected",
        "session_id": session_id,
        "message": "Connected to workflow updates"
    })

    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()

            message_type = data.get("type")

            if message_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif message_type == "approve":
                # Handle approval from WebSocket
                workflow = active_workflows.get(session_id)
                if workflow:
                    workflow.approve(
                        approved=True,
                        comments=data.get("comments", "")
                    )

            elif message_type == "reject":
                # Handle rejection from WebSocket - re-run workflow
                workflow = active_workflows.get(session_id)
                original_request = workflow_requests.get(session_id)
                if workflow and original_request:
                    # Create new workflow with same session_id for re-run
                    new_workflow = CapacityPlanningWorkflow(
                        demo_mode=workflow.demo_mode,
                        session_id=session_id  # Keep same session
                    )
                    active_workflows[session_id] = new_workflow
                    # Re-run workflow in background
                    asyncio.create_task(
                        run_workflow_background(new_workflow, original_request)
                    )

    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, session_id)


# ============================================================================
# AGENT INFO ENDPOINTS (for UI display)
# ============================================================================

@app.get("/api/agents")
async def get_agents_info():
    """Get information about the agents in the workflow."""
    return {
        "agents": [
            {
                "id": "data_analyst",
                "name": "Data Analyst",
                "description": "Queries shipment data from PostgreSQL via MCP",
                "tool": "MCP (Model Context Protocol)",
                "icon": "database",
                "color": "#3B82F6"
            },
            {
                "id": "capacity_calc",
                "name": "Capacity Calculator",
                "description": "Performs Python calculations for logistics planning",
                "tool": "Code Interpreter",
                "icon": "calculator",
                "color": "#10B981"
            },
            {
                "id": "doc_researcher",
                "name": "Document Researcher",
                "description": "Searches policy documents and regulations",
                "tool": "File Search",
                "icon": "file-search",
                "color": "#8B5CF6"
            },
            {
                "id": "planner",
                "name": "Planner",
                "description": "Synthesizes data into comprehensive capacity plan",
                "tool": "Synthesis",
                "icon": "clipboard-list",
                "color": "#F59E0B"
            }
        ],
        "workflow_type": "sequential",
        "human_in_loop": True
    }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
