"""
Agent 4: Planner Agent

This agent synthesizes all information from previous agents to create
a comprehensive capacity plan that requires human approval.

FOUNDRY V1 PATTERN:
- Uses AzureAIAgentClient from agent_framework.azure
- No additional tools - focuses on synthesis and planning
- Generates structured output for human review
"""
import asyncio
from typing import Dict, Any
import time

from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

from ..config import get_settings
from ..models import AgentMetrics


class PlannerAgent:
    """
    Agent 4: Planner

    This agent takes outputs from all previous agents and synthesizes
    them into a comprehensive, actionable capacity plan. The plan
    includes specific recommendations for:

    - Aircraft assignments
    - Crew scheduling
    - Route optimization
    - Risk mitigation

    The plan requires human approval before execution.

    FOUNDRY V1 IMPLEMENTATION:
    - Uses AzureAIAgentClient for agent creation
    - No additional tools - pure reasoning and synthesis
    - Generates structured plan output
    """

    INSTRUCTIONS = """You are a Capacity Planning Manager for Zava Global Logistics.

Your role is to synthesize all available data into a comprehensive, actionable
capacity plan for the Seattle hub operations. You will receive:

1. Shipment data and volume analysis from the Data Analyst
2. Capacity calculations from the Capacity Calculator
3. Policy and regulatory constraints from the Document Researcher

Create a FINAL CAPACITY PLAN that includes:

## EXECUTIVE SUMMARY
- Brief overview of the planning period
- Key metrics and recommendations
- Risk assessment (Low/Medium/High)

## AIRCRAFT ASSIGNMENTS
- Specific aircraft-to-route assignments
- Departure times and frequencies
- Load factors and utilization rates

## CREW SCHEDULE
- Pilot assignments for each flight
- Duty time compliance verification
- Backup crew arrangements

## OPERATIONAL COSTS
- Detailed cost breakdown
- Comparison to budget/targets
- Cost optimization opportunities

## RISK MITIGATION
- Identified constraints and risks
- Mitigation strategies
- Contingency plans

## ACTIONS REQUIRING APPROVAL
- List specific actions that need human authorization
- Include booking confirmations, crew assignments, fuel orders

Format the plan clearly with headers and tables. Be specific with numbers,
names, and times. This plan will be reviewed by a human manager before execution."""

    def __init__(self):
        self.settings = get_settings()
        self._agent = None
        self._credential = None
        self._client = None

    async def __aenter__(self):
        """Initialize the agent."""
        self._credential = DefaultAzureCredential()
        await self._credential.__aenter__()

        self._client = AzureAIAgentClient(
            project_endpoint=self.settings.azure_ai_project_endpoint,
            model_deployment_name=self.settings.azure_ai_model_deployment_name,
            async_credential=self._credential,
        )

        # Create the agent (no additional tools - synthesis only)
        self._agent = await self._client.create_agent(
            name="CapacityPlanner",
            instructions=self.INSTRUCTIONS
        ).__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup agent resources."""
        if self._agent:
            await self._agent.__aexit__(exc_type, exc_val, exc_tb)
        if self._credential:
            await self._credential.__aexit__(exc_type, exc_val, exc_tb)

    async def create_plan(
        self,
        shipment_data: str,
        capacity_calculations: str,
        policy_research: str
    ) -> Dict[str, Any]:
        """
        Create a comprehensive capacity plan from all agent outputs.

        Args:
            shipment_data: Output from Data Analyst
            capacity_calculations: Output from Capacity Calculator
            policy_research: Output from Document Researcher

        Returns:
            Dictionary containing the plan and metrics
        """
        start_time = time.time()

        prompt = f"""Create a comprehensive capacity plan based on the following inputs:

## SHIPMENT DATA (from Data Analyst)
{shipment_data}

## CAPACITY CALCULATIONS (from Capacity Calculator)
{capacity_calculations}

## POLICY & REGULATORY RESEARCH (from Document Researcher)
{policy_research}

---

Now create the FINAL CAPACITY PLAN following the structure in your instructions.
Include all specific details and ensure the plan is actionable.
List all actions that require human approval at the end."""

        # Execute the agent
        result = await self._agent.run(prompt)

        duration_ms = int((time.time() - start_time) * 1000)

        # Calculate metrics
        input_tokens = len(prompt.split()) * 2
        output_tokens = len(result.text.split()) * 2

        metrics = AgentMetrics(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            cost_usd=self._calculate_cost(input_tokens, output_tokens),
            tool_calls=0  # No tools used
        )

        return {
            "output": result.text,
            "metrics": metrics,
            "tools_used": [],
            "requires_approval": True,
            "approval_actions": self._extract_approval_actions(result.text)
        }

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost based on GPT-5-mini pricing."""
        input_cost = (input_tokens / 1_000_000) * self.settings.gpt5_mini_input_cost_per_million
        output_cost = (output_tokens / 1_000_000) * self.settings.gpt5_mini_output_cost_per_million
        return round(input_cost + output_cost, 6)

    def _extract_approval_actions(self, plan_text: str) -> list:
        """Extract actions requiring approval from the plan."""
        # In a real implementation, this would parse the plan
        # For demo, return standard approval actions
        return [
            {
                "action_id": "aircraft_booking",
                "action": "Confirm Aircraft Assignments",
                "description": "Book 5 aircraft for the planned routes",
                "estimated_cost": 45000.00
            },
            {
                "action_id": "crew_assignment",
                "action": "Assign Flight Crew",
                "description": "Assign 11 crew members to scheduled flights",
                "estimated_cost": 12500.00
            },
            {
                "action_id": "fuel_order",
                "action": "Order Fuel",
                "description": "Pre-order 37,023 liters of jet fuel",
                "estimated_cost": 31470.00
            },
            {
                "action_id": "notify_partners",
                "action": "Notify Ground Handling Partners",
                "description": "Send schedule to all destination handlers",
                "estimated_cost": 0.00
            }
        ]


# =============================================================================
# SAMPLE PLAN OUTPUT (for demo mode)
# =============================================================================

SAMPLE_PLAN_OUTPUT = """
# ZAVA CAPACITY PLAN
## Seattle Hub - January 2026

---

## EXECUTIVE SUMMARY

**Planning Period:** January 1-31, 2026
**Total Shipments:** 487 packages
**Total Cargo Weight:** 125,450 kg
**Estimated Revenue:** $485,000

### Key Recommendations:
1. Deploy 5 aircraft across 5 primary routes
2. Assign 11 crew members with rotation schedule
3. Pre-order 37,023 liters of fuel
4. Implement 15% capacity buffer per policy guidelines

### Risk Assessment: **MEDIUM**
- Two crew members approaching monthly duty limits
- One aircraft (N768ZV) in maintenance until Jan 15
- Pacific routes require payload adjustments

---

## AIRCRAFT ASSIGNMENTS

| Flight | Route | Aircraft | Departure | Cargo (kg) | Load % |
|--------|-------|----------|-----------|------------|--------|
| ZV101 | SEA-LAX | N767ZV (767-300F) | 0600 Daily | 22,340 | 41% |
| ZV201 | SEA-JFK | N330ZV (A330-200F) | 0800 Daily | 19,850 | 28% |
| ZV301 | SEA-ORD | N767ZV (767-300F) | 1400 Daily | 15,200 | 28% |
| ZV401 | SEA-NRT | N777ZV (777F) | 2300 Mon/Thu | 18,200 | 18% |
| ZV501 | SEA-LHR | N747ZV (747-400F) | 2100 Tue/Fri | 30,000 | 25% |

**Total Utilization:** 78% of available capacity
**Buffer Maintained:** 22% (exceeds 15% policy requirement)

---

## CREW SCHEDULE

### Week 1 (Jan 1-7)

| Flight | Day | Captain | First Officer | F/E |
|--------|-----|---------|---------------|-----|
| ZV101 | Mon | Chen | Liu | - |
| ZV201 | Mon | Park | Foster | - |
| ZV301 | Mon | Torres | Kim | - |
| ZV401 | Mon | Wilson | Martinez | - |
| ZV501 | Tue | Johnson | Anderson | Wright |

### Duty Time Compliance
- All assignments within 10-hour domestic / 12-hour international limits
- Augmented crew assigned for ZV401 and ZV501 (>8 hour flights)
- Minimum 10-hour rest between assignments verified

### Crew Notes:
- Capt. Chen: 28/30 hours used this month - limit in 2 flights
- F/O Liu: 26/30 hours used - monitor closely
- Backup: Capt. Johnson available for emergency coverage

---

## OPERATIONAL COSTS

| Category | Amount (USD) | % of Total |
|----------|-------------|------------|
| Fuel (37,023 L) | $31,470 | 44% |
| Crew Compensation | $12,500 | 17% |
| Landing Fees | $8,200 | 11% |
| Ground Handling | $4,500 | 6% |
| Insurance | $2,800 | 4% |
| Navigation Fees | $3,200 | 4% |
| Catering/Supplies | $1,800 | 3% |
| Contingency (10%) | $7,147 | 10% |
| **TOTAL** | **$71,617** | 100% |

**Cost per kg:** $0.57
**Cost per shipment:** $147.06
**Budget variance:** -3% (under budget)

---

## RISK MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Crew duty limit exceeded | Medium | High | Pre-assign backup crew |
| Aircraft N768ZV delay | Low | Medium | Use N767ZV double rotation |
| Weather delay SEA | Medium | Medium | 4-hour schedule buffer |
| Fuel price increase | Low | Low | Locked pricing through Jan |
| Customs delay NRT | Low | Medium | Pre-clear documentation |

### Contingency Plans:
1. **Aircraft shortage:** Charter agreement with Atlas Air on standby
2. **Crew shortage:** Cross-trained pilots from Portland hub available
3. **Volume spike:** Activate overflow agreement with FedEx

---

## ACTIONS REQUIRING APPROVAL

The following actions require human authorization before execution:

### 1. Aircraft Booking Confirmation
- **Action:** Confirm assignment of 5 aircraft for January operations
- **Cost Impact:** $45,000 (aircraft positioning and preparation)
- **Deadline:** 48 hours before first flight

### 2. Crew Assignment Publication
- **Action:** Publish crew schedule to 11 assigned crew members
- **Cost Impact:** $12,500 (crew compensation commitment)
- **Deadline:** 72 hours before first assignment

### 3. Fuel Pre-Order
- **Action:** Order 37,023 liters of Jet-A fuel at locked price
- **Cost Impact:** $31,470
- **Deadline:** 24 hours before first flight

### 4. Partner Notification
- **Action:** Send schedule to ground handling partners at all destinations
- **Cost Impact:** None (notification only)
- **Deadline:** 48 hours before first flight

---

**Plan Generated:** 2026-01-08 14:32:00 UTC
**Plan Version:** 1.0
**Status:** AWAITING APPROVAL

⚠️ This plan requires human approval before any actions are executed.
"""
