"""
Agent 2: Capacity Calculator Agent

This agent uses the Code Interpreter tool to perform Python calculations
for logistics capacity planning. It analyzes shipment data and calculates
aircraft requirements, fuel estimates, and crew needs.

FOUNDRY V1 PATTERN:
- Uses AzureAIAgentClient from agent_framework.azure
- Uses HostedCodeInterpreterTool for Python execution
- Agent can write and execute code to perform precise calculations
"""
import asyncio
from typing import Dict, Any
import time

from agent_framework.azure import AzureAIAgentClient
from agent_framework import HostedCodeInterpreterTool
from azure.identity.aio import DefaultAzureCredential

from ..config import get_settings
from ..models import AgentMetrics


class CapacityCalculatorAgent:
    """
    Agent 2: Capacity Calculator

    This agent uses the Code Interpreter tool to perform precise calculations
    for capacity planning. It can write and execute Python code to:

    - Calculate optimal aircraft assignments
    - Estimate fuel requirements per route
    - Determine crew scheduling needs
    - Optimize load distribution

    FOUNDRY V1 IMPLEMENTATION:
    - Uses HostedCodeInterpreterTool for code execution
    - Agent has access to Python runtime in Azure
    - Can perform complex mathematical calculations
    """

    INSTRUCTIONS = """You are a Capacity Calculator for Zava Global Logistics.

Your role is to perform precise calculations for capacity planning using Python code.
You have access to a Python code interpreter to run calculations.

Given shipment data and fleet information, calculate:

1. AIRCRAFT REQUIREMENTS
   - Determine which aircraft types are needed
   - Calculate number of flights per route
   - Optimize aircraft utilization

2. FUEL ESTIMATES
   - Calculate fuel needed per route based on distance and aircraft type
   - Account for cargo weight impact on fuel consumption
   - Include reserve fuel (10% buffer)

3. CREW REQUIREMENTS
   - Calculate total crew needed based on flights
   - Account for duty time regulations (max 10 hours)
   - Ensure proper rest periods between flights

4. LOAD OPTIMIZATION
   - Distribute cargo across available aircraft
   - Maximize load factor while respecting weight limits
   - Consider volume constraints

Always use Python code for precise calculations. Show your work with code
and provide clear numerical results. Round costs to 2 decimal places."""

    def __init__(self):
        self.settings = get_settings()
        self._agent = None
        self._credential = None
        self._client = None

    async def __aenter__(self):
        """Initialize the agent with Code Interpreter tool."""
        self._credential = DefaultAzureCredential()
        await self._credential.__aenter__()

        self._client = AzureAIAgentClient(
            project_endpoint=self.settings.azure_ai_project_endpoint,
            model_deployment_name=self.settings.azure_ai_model_deployment_name,
            async_credential=self._credential,
        )

        # Create the agent with Code Interpreter tool
        self._agent = await self._client.create_agent(
            name="CapacityCalculator",
            instructions=self.INSTRUCTIONS,
            tools=HostedCodeInterpreterTool()  # Key V1 feature: Code Interpreter
        ).__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup agent resources."""
        if self._agent:
            await self._agent.__aexit__(exc_type, exc_val, exc_tb)
        if self._credential:
            await self._credential.__aexit__(exc_type, exc_val, exc_tb)

    async def calculate(self, shipment_data: str) -> Dict[str, Any]:
        """
        Perform capacity calculations based on shipment data.

        Args:
            shipment_data: Output from the Data Analyst agent

        Returns:
            Dictionary containing calculation results and metrics
        """
        start_time = time.time()

        prompt = f"""Based on the following shipment data, perform capacity calculations:

{shipment_data}

Please use Python code to calculate:

1. Aircraft assignments - which planes should fly which routes
2. Fuel requirements - total fuel needed with 10% reserve
3. Crew scheduling - pilot and crew assignments
4. Cost estimates - operational costs breakdown

Write and execute Python code to perform these calculations precisely.
Provide a detailed breakdown of all calculations."""

        # Execute the agent with Code Interpreter
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
            tool_calls=1  # Code Interpreter
        )

        return {
            "output": result.text,
            "metrics": metrics,
            "tools_used": ["HostedCodeInterpreter"],
            "code_executed": True
        }

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost based on GPT-5-mini pricing."""
        input_cost = (input_tokens / 1_000_000) * self.settings.gpt5_mini_input_cost_per_million
        output_cost = (output_tokens / 1_000_000) * self.settings.gpt5_mini_output_cost_per_million
        return round(input_cost + output_cost, 6)


# =============================================================================
# SAMPLE CALCULATION OUTPUT (for demo mode)
# =============================================================================
# This is the type of output the Code Interpreter would produce:

SAMPLE_CALCULATION_OUTPUT = """
CAPACITY CALCULATION RESULTS
============================

## Python Code Executed:

```python
import pandas as pd
import numpy as np

# Shipment data summary
total_shipments = 487
total_weight_kg = 125450
total_volume_m3 = 892

# Aircraft specifications
aircraft = {
    '747-400F': {'capacity_kg': 120000, 'volume_m3': 858, 'fuel_rate': 12.5, 'crew': 3},
    '777F': {'capacity_kg': 102000, 'volume_m3': 653, 'fuel_rate': 14.2, 'crew': 2},
    '767-300F': {'capacity_kg': 54000, 'volume_m3': 438, 'fuel_rate': 16.8, 'crew': 2},
    'A330-200F': {'capacity_kg': 70000, 'volume_m3': 475, 'fuel_rate': 15.1, 'crew': 2},
}

# Route distances (km)
routes = {
    'SEA-LAX': 1540, 'SEA-JFK': 3900, 'SEA-ORD': 2800,
    'SEA-NRT': 7700, 'SEA-LHR': 7800, 'SEA-FRA': 8200
}

# Calculate optimal aircraft assignment
def calculate_assignments():
    assignments = []

    # Domestic routes - use 767 and A330
    domestic_weight = 81700  # kg
    assignments.append({
        'route': 'SEA-LAX', 'aircraft': '767-300F',
        'cargo_kg': 22340, 'flights': 1
    })
    assignments.append({
        'route': 'SEA-JFK', 'aircraft': 'A330-200F',
        'cargo_kg': 19850, 'flights': 1
    })

    # International routes - use 777F and 747F
    assignments.append({
        'route': 'SEA-NRT', 'aircraft': '777F',
        'cargo_kg': 18200, 'flights': 1
    })
    assignments.append({
        'route': 'SEA-LHR', 'aircraft': '747-400F',
        'cargo_kg': 30000, 'flights': 1  # Combined EU cargo
    })

    return assignments

assignments = calculate_assignments()
print("Aircraft Assignments:", assignments)
```

## CALCULATION RESULTS:

### 1. Aircraft Assignments
| Route | Aircraft | Cargo (kg) | Load Factor |
|-------|----------|------------|-------------|
| SEA → LAX | 767-300F | 22,340 | 41.4% |
| SEA → JFK | A330-200F | 19,850 | 28.4% |
| SEA → ORD | 767-300F | 15,200 | 28.1% |
| SEA → NRT | 777F | 18,200 | 17.8% |
| SEA → LHR/FRA | 747-400F | 30,000 | 25.0% |

### 2. Fuel Requirements
| Route | Distance | Aircraft | Fuel (L) | Reserve | Total |
|-------|----------|----------|----------|---------|-------|
| SEA → LAX | 1,540 km | 767-300F | 1,833 | 183 | 2,016 |
| SEA → JFK | 3,900 km | A330-200F | 5,166 | 517 | 5,683 |
| SEA → ORD | 2,800 km | 767-300F | 3,333 | 333 | 3,666 |
| SEA → NRT | 7,700 km | 777F | 10,845 | 1,085 | 11,930 |
| SEA → LHR | 7,800 km | 747-400F | 12,480 | 1,248 | 13,728 |

**Total Fuel Required: 37,023 liters** (with 10% reserve)

### 3. Crew Requirements
| Flight | Aircraft | Crew Needed | Duty Hours |
|--------|----------|-------------|------------|
| SEA-LAX | 767-300F | 2 (Capt + FO) | 4.5 hrs |
| SEA-JFK | A330-200F | 2 (Capt + FO) | 7.0 hrs |
| SEA-ORD | 767-300F | 2 (Capt + FO) | 5.8 hrs |
| SEA-NRT | 777F | 2 (Capt + FO) | 12.5 hrs* |
| SEA-LHR | 747-400F | 3 (Capt + FO + FE) | 11.5 hrs* |

*Long-haul flights require augmented crew for rest compliance.

**Total Crew Required: 11 crew members**

### 4. Cost Estimates
| Category | Cost (USD) |
|----------|------------|
| Fuel (37,023 L @ $0.85/L) | $31,470 |
| Crew (flight pay) | $12,500 |
| Landing Fees | $8,200 |
| Handling Fees | $4,500 |
| Insurance | $2,800 |
| **TOTAL OPERATIONAL COST** | **$59,470** |

Cost per kg shipped: $0.47
Cost per shipment: $122.11
"""
