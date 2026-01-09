"""
Capacity Planning Workflow Orchestrator

This module orchestrates the sequential execution of all four agents
in the capacity planning workflow. It manages state, emits real-time
updates via WebSocket, and handles the human-in-the-loop approval step.

WORKFLOW PATTERN:
1. Data Analyst Agent (MCP queries)
2. Capacity Calculator Agent (Code Interpreter)
3. Document Researcher Agent (File Search)
4. Planner Agent (Synthesis)
5. Human Approval (WebSocket notification)
6. Execution (if approved)
"""
import asyncio
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional, Callable, Awaitable
from enum import Enum

from ..models import (
    WorkflowRequest,
    AgentUpdate,
    AgentStatus,
    AgentMetrics,
    TelemetryMetrics,
    HumanApprovalRequest,
)
from ..config import get_settings

# Import demo data for offline mode
from .data_analyst import (
    get_shipments,
    get_aircraft_fleet,
    get_historical_volumes,
    get_routes,
    get_crew_availability,
)
from .capacity_calc import SAMPLE_CALCULATION_OUTPUT
from .doc_researcher import SAMPLE_RESEARCH_OUTPUT
from .planner import SAMPLE_PLAN_OUTPUT


class WorkflowState(str, Enum):
    """States of the capacity planning workflow."""
    INITIALIZED = "initialized"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    ERROR = "error"


class CapacityPlanningWorkflow:
    """
    Orchestrates the capacity planning workflow with four sequential agents.

    This class manages:
    - Sequential agent execution
    - State management and persistence
    - Real-time updates via callback
    - Telemetry collection
    - Human-in-the-loop approval

    USAGE:
        workflow = CapacityPlanningWorkflow()
        async for update in workflow.run(request):
            # Handle updates (send to WebSocket)
            pass
    """

    AGENTS = [
        {
            "id": "data_analyst",
            "name": "Data Analyst",
            "description": "Queries shipment data via MCP",
            "tool": "MCP (PostgreSQL)"
        },
        {
            "id": "capacity_calc",
            "name": "Capacity Calculator",
            "description": "Calculates logistics requirements",
            "tool": "Code Interpreter"
        },
        {
            "id": "doc_researcher",
            "name": "Document Researcher",
            "description": "Searches policy documents",
            "tool": "File Search"
        },
        {
            "id": "planner",
            "name": "Planner",
            "description": "Creates comprehensive capacity plan",
            "tool": "Synthesis"
        }
    ]

    def __init__(self, demo_mode: bool = True, session_id: Optional[str] = None):
        """
        Initialize the workflow.

        Args:
            demo_mode: If True, use sample data instead of real agents.
                      Set to False for production with real Azure credentials.
            session_id: Optional session ID for re-running workflows.
                       If not provided, a new UUID will be generated.
        """
        self.settings = get_settings()
        self.demo_mode = demo_mode
        self.session_id = session_id or str(uuid.uuid4())
        self.state = WorkflowState.INITIALIZED
        self.telemetry = TelemetryMetrics(session_id=self.session_id)

        # Store outputs from each agent for context passing
        self._agent_outputs = {}

        # Approval state
        self._approval_event = asyncio.Event()
        self._approved = False
        self._approval_comments = ""

    async def run(
        self,
        request: WorkflowRequest
    ) -> AsyncGenerator[AgentUpdate | HumanApprovalRequest | dict, None]:
        """
        Execute the capacity planning workflow.

        This is the main entry point that runs all agents sequentially
        and yields updates for real-time streaming.

        Args:
            request: The workflow request with date range and hub

        Yields:
            AgentUpdate: Status updates for each agent
            HumanApprovalRequest: Request for human approval
            dict: Final result or error
        """
        self.state = WorkflowState.RUNNING

        try:
            # ================================================================
            # AGENT 1: Data Analyst
            # ================================================================
            yield self._create_update("data_analyst", AgentStatus.RUNNING,
                input_text=f"Analyzing shipments from {request.hub} hub ({request.date_from} to {request.date_to})")

            data_result = await self._run_data_analyst(request)
            self._agent_outputs["data_analyst"] = data_result["output"]
            self.telemetry.add_agent_metrics("data_analyst", data_result["metrics"])

            yield self._create_update("data_analyst", AgentStatus.COMPLETED,
                output_text=data_result["output"],
                tool_use={"tools": data_result.get("tools_used", [])},
                metrics=data_result["metrics"])

            # Small delay for visual effect
            await asyncio.sleep(0.5)

            # ================================================================
            # AGENT 2: Capacity Calculator
            # ================================================================
            yield self._create_update("capacity_calc", AgentStatus.RUNNING,
                input_text="Calculating capacity requirements based on shipment data...")

            calc_result = await self._run_capacity_calculator(data_result["output"])
            self._agent_outputs["capacity_calc"] = calc_result["output"]
            self.telemetry.add_agent_metrics("capacity_calc", calc_result["metrics"])

            yield self._create_update("capacity_calc", AgentStatus.COMPLETED,
                output_text=calc_result["output"],
                tool_use={"tools": calc_result.get("tools_used", []), "code_executed": True},
                metrics=calc_result["metrics"])

            await asyncio.sleep(0.5)

            # ================================================================
            # AGENT 3: Document Researcher
            # ================================================================
            yield self._create_update("doc_researcher", AgentStatus.RUNNING,
                input_text="Searching policy documents and regulations...")

            research_result = await self._run_doc_researcher(calc_result["output"])
            self._agent_outputs["doc_researcher"] = research_result["output"]
            self.telemetry.add_agent_metrics("doc_researcher", research_result["metrics"])

            yield self._create_update("doc_researcher", AgentStatus.COMPLETED,
                output_text=research_result["output"],
                tool_use={
                    "tools": research_result.get("tools_used", []),
                    "documents": research_result.get("documents_searched", [])
                },
                metrics=research_result["metrics"])

            await asyncio.sleep(0.5)

            # ================================================================
            # AGENT 4: Planner
            # ================================================================
            yield self._create_update("planner", AgentStatus.RUNNING,
                input_text="Synthesizing capacity plan from all data...")

            plan_result = await self._run_planner(
                self._agent_outputs["data_analyst"],
                self._agent_outputs["capacity_calc"],
                self._agent_outputs["doc_researcher"]
            )
            self._agent_outputs["planner"] = plan_result["output"]
            self.telemetry.add_agent_metrics("planner", plan_result["metrics"])

            yield self._create_update("planner", AgentStatus.COMPLETED,
                output_text=plan_result["output"],
                tool_use={"tools": []},
                metrics=plan_result["metrics"])

            # ================================================================
            # HUMAN APPROVAL REQUEST
            # ================================================================
            self.state = WorkflowState.AWAITING_APPROVAL

            approval_request = HumanApprovalRequest(
                session_id=self.session_id,
                plan_summary=self._extract_summary(plan_result["output"]),
                proposed_actions=plan_result.get("approval_actions", []),
                total_cost_estimate=self.telemetry.total_cost_usd + 71617.00,  # Plan operational cost
                aircraft_assignments=[
                    {"route": "SEA-LAX", "aircraft": "767-300F", "cargo_kg": 22340},
                    {"route": "SEA-JFK", "aircraft": "A330-200F", "cargo_kg": 19850},
                    {"route": "SEA-NRT", "aircraft": "777F", "cargo_kg": 18200},
                    {"route": "SEA-LHR", "aircraft": "747-400F", "cargo_kg": 30000},
                ],
                crew_assignments=[
                    {"flight": "ZV101", "captain": "Chen", "first_officer": "Liu"},
                    {"flight": "ZV201", "captain": "Park", "first_officer": "Foster"},
                    {"flight": "ZV401", "captain": "Wilson", "first_officer": "Martinez"},
                    {"flight": "ZV501", "captain": "Johnson", "first_officer": "Anderson", "flight_engineer": "Wright"},
                ]
            )

            yield approval_request

            # ================================================================
            # WAIT FOR APPROVAL (or timeout)
            # ================================================================
            # In production, this waits for the approval endpoint to be called
            # For demo, we auto-approve after the user clicks

            try:
                await asyncio.wait_for(self._approval_event.wait(), timeout=300)  # 5 min timeout
            except asyncio.TimeoutError:
                self.state = WorkflowState.ERROR
                yield {"type": "error", "message": "Approval timeout - plan expired"}
                return

            if self._approved:
                self.state = WorkflowState.APPROVED
                yield {
                    "type": "workflow_complete",
                    "status": "approved",
                    "session_id": self.session_id,
                    "message": "Capacity plan approved and ready for execution",
                    "telemetry": self.telemetry.model_dump()
                }
            else:
                self.state = WorkflowState.REJECTED
                yield {
                    "type": "workflow_complete",
                    "status": "rejected",
                    "session_id": self.session_id,
                    "message": f"Capacity plan rejected: {self._approval_comments}",
                    "telemetry": self.telemetry.model_dump()
                }

            self.state = WorkflowState.COMPLETED

        except Exception as e:
            self.state = WorkflowState.ERROR
            yield {
                "type": "error",
                "session_id": self.session_id,
                "message": str(e),
                "telemetry": self.telemetry.model_dump()
            }

    def approve(self, approved: bool, comments: str = ""):
        """
        Set the approval status for the plan.

        Called when user clicks Approve or Reject in the UI.
        """
        self._approved = approved
        self._approval_comments = comments
        self._approval_event.set()

    def _create_update(
        self,
        agent_id: str,
        status: AgentStatus,
        input_text: Optional[str] = None,
        output_text: Optional[str] = None,
        tool_use: Optional[dict] = None,
        metrics: Optional[AgentMetrics] = None
    ) -> AgentUpdate:
        """Create an AgentUpdate message."""
        agent_info = next((a for a in self.AGENTS if a["id"] == agent_id), {})
        return AgentUpdate(
            agent_id=agent_id,
            agent_name=agent_info.get("name", agent_id),
            status=status,
            input_text=input_text,
            output_text=output_text,
            tool_use=tool_use,
            metrics=metrics
        )

    def _extract_summary(self, plan_text: str) -> str:
        """Extract executive summary from the plan."""
        # Simple extraction - in production, use more sophisticated parsing
        if "EXECUTIVE SUMMARY" in plan_text:
            start = plan_text.find("EXECUTIVE SUMMARY")
            end = plan_text.find("##", start + 20)
            if end > start:
                return plan_text[start:end].strip()
        return plan_text[:500] + "..."

    # ========================================================================
    # AGENT EXECUTION METHODS
    # ========================================================================
    # In demo mode, these return sample data.
    # In production mode, they instantiate and run real Foundry agents.

    async def _run_data_analyst(self, request: WorkflowRequest) -> dict:
        """Run the Data Analyst agent."""
        import time
        start = time.time()

        if self.demo_mode:
            # Simulate agent execution with sample data
            await asyncio.sleep(2)  # Simulate processing time

            shipments = await get_shipments(
                request.date_from.isoformat(),
                request.date_to.isoformat(),
                request.hub
            )
            fleet = await get_aircraft_fleet()
            history = await get_historical_volumes(request.hub, 12)
            routes = await get_routes(request.hub)
            crew = await get_crew_availability()

            output = f"""
DATA ANALYSIS COMPLETE
======================

{shipments}

{fleet}

{history}

{routes}

{crew}
"""
            return {
                "output": output,
                "metrics": AgentMetrics(
                    input_tokens=245,
                    output_tokens=1850,
                    duration_ms=int((time.time() - start) * 1000),
                    cost_usd=0.0205,
                    tool_calls=5
                ),
                "tools_used": ["get_shipments", "get_aircraft_fleet", "get_historical_volumes", "get_routes", "get_crew_availability"]
            }
        else:
            # Production mode: use real agent
            from .data_analyst import DataAnalystAgent
            async with DataAnalystAgent() as agent:
                return await agent.analyze(request.date_from, request.date_to, request.hub)

    async def _run_capacity_calculator(self, shipment_data: str) -> dict:
        """Run the Capacity Calculator agent."""
        import time
        start = time.time()

        if self.demo_mode:
            await asyncio.sleep(3)  # Code interpreter takes longer
            return {
                "output": SAMPLE_CALCULATION_OUTPUT,
                "metrics": AgentMetrics(
                    input_tokens=1900,
                    output_tokens=2200,
                    duration_ms=int((time.time() - start) * 1000),
                    cost_usd=0.0245,
                    tool_calls=1
                ),
                "tools_used": ["HostedCodeInterpreter"],
                "code_executed": True
            }
        else:
            from .capacity_calc import CapacityCalculatorAgent
            async with CapacityCalculatorAgent() as agent:
                return await agent.calculate(shipment_data)

    async def _run_doc_researcher(self, capacity_context: str) -> dict:
        """Run the Document Researcher agent."""
        import time
        start = time.time()

        if self.demo_mode:
            await asyncio.sleep(2)
            return {
                "output": SAMPLE_RESEARCH_OUTPUT,
                "metrics": AgentMetrics(
                    input_tokens=2300,
                    output_tokens=1800,
                    duration_ms=int((time.time() - start) * 1000),
                    cost_usd=0.0210,
                    tool_calls=1
                ),
                "tools_used": ["FileSearchTool"],
                "documents_searched": ["aircraft_specs.md", "faa_regulations.md", "crew_policies.md", "historical_reports.md"]
            }
        else:
            from .doc_researcher import DocumentResearcherAgent
            async with DocumentResearcherAgent() as agent:
                return await agent.research(capacity_context)

    async def _run_planner(self, shipment_data: str, calculations: str, research: str) -> dict:
        """Run the Planner agent."""
        import time
        start = time.time()

        if self.demo_mode:
            await asyncio.sleep(2.5)
            return {
                "output": SAMPLE_PLAN_OUTPUT,
                "metrics": AgentMetrics(
                    input_tokens=5500,
                    output_tokens=3200,
                    duration_ms=int((time.time() - start) * 1000),
                    cost_usd=0.0390,
                    tool_calls=0
                ),
                "tools_used": [],
                "requires_approval": True,
                "approval_actions": [
                    {"action_id": "aircraft_booking", "action": "Confirm Aircraft Assignments", "description": "Book 5 aircraft for planned routes", "estimated_cost": 45000.00},
                    {"action_id": "crew_assignment", "action": "Assign Flight Crew", "description": "Assign 11 crew members to flights", "estimated_cost": 12500.00},
                    {"action_id": "fuel_order", "action": "Order Fuel", "description": "Pre-order 37,023 liters of jet fuel", "estimated_cost": 31470.00},
                    {"action_id": "notify_partners", "action": "Notify Partners", "description": "Send schedule to ground handlers", "estimated_cost": 0.00}
                ]
            }
        else:
            from .planner import PlannerAgent
            async with PlannerAgent() as agent:
                return await agent.create_plan(shipment_data, calculations, research)
