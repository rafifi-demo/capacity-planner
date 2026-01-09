"""
Agent 1: Data Analyst Agent

This agent uses MCP (Model Context Protocol) tools to query the PostgreSQL database
for shipment data. It retrieves volumes, destinations, weights, and historical trends.

FOUNDRY V1 PATTERN:
- Uses AzureAIAgentClient from agent_framework.azure
- Custom function tools for MCP database queries
- Async context manager pattern for agent lifecycle
"""
import os
import asyncio
from typing import Annotated, Dict, Any, Optional
from datetime import date
from pydantic import Field

from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

from ..config import get_settings
from ..models import AgentMetrics


# =============================================================================
# MCP TOOL FUNCTIONS
# =============================================================================
# These functions are exposed to the agent as callable tools.
# In production, these would call the actual MCP server via APIM.
# For the demo, they can query the database directly or through MCP.

async def get_shipments(
    date_from: Annotated[str, Field(description="Start date (YYYY-MM-DD)")],
    date_to: Annotated[str, Field(description="End date (YYYY-MM-DD)")],
    hub: Annotated[str, Field(description="Hub location (e.g., 'Seattle')")]
) -> str:
    """
    Query shipments from the database for a given date range and hub.
    Returns summary of shipment volumes, weights, and destinations.
    """
    # In production, this calls the MCP server through APIM
    # For demo, we return realistic sample data
    return f"""
    SHIPMENT DATA QUERY RESULTS
    ===========================
    Date Range: {date_from} to {date_to}
    Hub: {hub}

    Summary Statistics:
    - Total Shipments: 487
    - Total Weight: 125,450 kg
    - Total Volume: 892 cubic meters
    - Average Weight per Shipment: 257.6 kg

    Top Destinations:
    1. Los Angeles (LAX): 89 shipments, 22,340 kg
    2. New York (JFK): 76 shipments, 19,850 kg
    3. Chicago (ORD): 64 shipments, 15,200 kg
    4. Dallas (DFW): 52 shipments, 12,800 kg
    5. Miami (MIA): 48 shipments, 11,500 kg
    6. Tokyo (NRT): 42 shipments, 18,200 kg (International)
    7. London (LHR): 38 shipments, 15,800 kg (International)
    8. Frankfurt (FRA): 35 shipments, 14,200 kg (International)
    9. Other Domestic: 28 shipments, 8,560 kg
    10. Other International: 15 shipments, 7,000 kg

    Priority Breakdown:
    - Express (Same Day): 45 shipments (9.2%)
    - Priority (Next Day): 156 shipments (32.0%)
    - Standard (2-5 Days): 286 shipments (58.8%)

    Weight Distribution:
    - Light (<50 kg): 198 shipments
    - Medium (50-200 kg): 187 shipments
    - Heavy (200-500 kg): 78 shipments
    - Extra Heavy (>500 kg): 24 shipments
    """


async def get_aircraft_fleet() -> str:
    """
    Get available aircraft and their specifications from the database.
    Returns fleet composition and capacity details.
    """
    return """
    ZAVA AIRCRAFT FLEET - SEATTLE HUB
    ==================================

    Available Aircraft:

    1. Boeing 747-400F (N747ZV)
       - Max Cargo: 120,000 kg
       - Max Volume: 858 cubic meters
       - Range: 8,240 km
       - Fuel Efficiency: 12.5 km/liter
       - Crew Required: 3 (2 pilots + 1 flight engineer)
       - Status: Available

    2. Boeing 777F (N777ZV)
       - Max Cargo: 102,000 kg
       - Max Volume: 653 cubic meters
       - Range: 9,070 km
       - Fuel Efficiency: 14.2 km/liter
       - Crew Required: 2
       - Status: Available

    3. Boeing 767-300F (N767ZV)
       - Max Cargo: 54,000 kg
       - Max Volume: 438 cubic meters
       - Range: 6,025 km
       - Fuel Efficiency: 16.8 km/liter
       - Crew Required: 2
       - Status: Available

    4. Boeing 767-300F (N768ZV)
       - Max Cargo: 54,000 kg
       - Max Volume: 438 cubic meters
       - Range: 6,025 km
       - Fuel Efficiency: 16.8 km/liter
       - Crew Required: 2
       - Status: In Maintenance (Returns Jan 15)

    5. Airbus A330-200F (N330ZV)
       - Max Cargo: 70,000 kg
       - Max Volume: 475 cubic meters
       - Range: 7,400 km
       - Fuel Efficiency: 15.1 km/liter
       - Crew Required: 2
       - Status: Available

    Total Available Capacity: 346,000 kg / 2,424 cubic meters
    """


async def get_historical_volumes(
    hub: Annotated[str, Field(description="Hub location")],
    months: Annotated[int, Field(description="Number of months of history")]
) -> str:
    """
    Get historical shipment volumes for trend analysis.
    Returns monthly averages and seasonal patterns.
    """
    return f"""
    HISTORICAL VOLUME ANALYSIS - {hub.upper()} HUB
    =============================================
    Period: Last {months} months

    Monthly Averages:
    - January: 425 shipments (102,500 kg) - Post-holiday lull
    - February: 398 shipments (95,200 kg)
    - March: 445 shipments (112,300 kg) - Spring uptick
    - April: 462 shipments (118,400 kg)
    - May: 478 shipments (122,100 kg)
    - June: 495 shipments (128,900 kg) - Summer peak begins
    - July: 512 shipments (135,200 kg)
    - August: 498 shipments (130,400 kg)
    - September: 485 shipments (125,600 kg)
    - October: 520 shipments (138,500 kg) - Pre-holiday surge
    - November: 589 shipments (165,200 kg) - Holiday peak
    - December: 625 shipments (178,400 kg) - Peak season

    Seasonal Patterns:
    - Q1 Average: 423 shipments/month
    - Q2 Average: 478 shipments/month
    - Q3 Average: 498 shipments/month
    - Q4 Average: 578 shipments/month

    Year-over-Year Growth: +8.5%

    Trend Forecast for Next Month:
    - Expected Shipments: 490-510
    - Expected Weight: 128,000-135,000 kg
    - Confidence: 85%
    """


async def get_routes(hub: Annotated[str, Field(description="Origin hub")]) -> str:
    """
    Get available routes from the specified hub.
    Returns destinations, distances, and typical flight times.
    """
    return f"""
    ROUTES FROM {hub.upper()} HUB
    =============================

    Domestic Routes:
    1. SEA -> LAX: 1,540 km, 2.5 hrs
    2. SEA -> JFK: 3,900 km, 5.0 hrs
    3. SEA -> ORD: 2,800 km, 3.8 hrs
    4. SEA -> DFW: 2,700 km, 3.5 hrs
    5. SEA -> MIA: 4,400 km, 5.5 hrs
    6. SEA -> ATL: 3,500 km, 4.5 hrs
    7. SEA -> DEN: 1,650 km, 2.3 hrs
    8. SEA -> PHX: 1,850 km, 2.5 hrs

    International Routes:
    1. SEA -> NRT (Tokyo): 7,700 km, 10.5 hrs
    2. SEA -> LHR (London): 7,800 km, 9.5 hrs
    3. SEA -> FRA (Frankfurt): 8,200 km, 10.0 hrs
    4. SEA -> HKG (Hong Kong): 10,100 km, 13.5 hrs
    5. SEA -> SYD (Sydney): 12,500 km, 16.0 hrs

    Note: Flight times include typical taxi and approach times.
    """


async def get_crew_availability() -> str:
    """
    Get current crew availability and certifications.
    Returns available pilots and their qualifications.
    """
    return """
    CREW AVAILABILITY - SEATTLE BASE
    =================================

    Pilots Available (Next 7 Days):

    Captain-Qualified:
    1. Capt. Sarah Chen - 747/777 rated - Available all week
    2. Capt. Michael Torres - 747/777/767 rated - Available Mon-Fri
    3. Capt. Jennifer Park - 777/767/A330 rated - Available Tue-Sun
    4. Capt. David Wilson - 747/777 rated - Available Wed-Sun
    5. Capt. Emily Johnson - All types rated - Available Mon-Thu

    First Officers:
    1. F/O James Liu - 777/767 rated - Available all week
    2. F/O Amanda Foster - 747/777 rated - Available Mon-Sat
    3. F/O Robert Kim - 767/A330 rated - Available all week
    4. F/O Lisa Martinez - 777/767/A330 rated - Available Tue-Sun
    5. F/O Chris Anderson - All types rated - Available Mon-Fri
    6. F/O Nicole Brown - 747/777 rated - Available Wed-Sun

    Flight Engineers (747 only):
    1. F/E Thomas Wright - Available Mon-Fri
    2. F/E Maria Garcia - Available Tue-Sat

    Crew Summary:
    - Total Captains Available: 5
    - Total First Officers Available: 6
    - Total Flight Engineers Available: 2
    - Max Simultaneous 747 Operations: 2
    - Max Simultaneous Other Operations: 5
    """


# =============================================================================
# DATA ANALYST AGENT CLASS
# =============================================================================

class DataAnalystAgent:
    """
    Agent 1: Data Analyst

    This agent queries the PostgreSQL database via MCP tools to retrieve
    shipment data, aircraft fleet information, historical trends, and more.

    FOUNDRY V1 IMPLEMENTATION:
    - Uses AzureAIAgentClient for agent creation
    - Registers custom function tools for MCP queries
    - Follows async context manager pattern
    """

    # Agent instructions define the agent's role and behavior
    INSTRUCTIONS = """You are a Data Analyst for Zava Global Logistics.

Your role is to query and analyze shipment data from the Seattle hub database.
Use the available tools to gather comprehensive data about:

1. Current shipment volumes and destinations
2. Aircraft fleet availability and specifications
3. Historical volume trends for forecasting
4. Route information and distances
5. Crew availability

When queried, provide a thorough data summary that will be used by other agents
for capacity calculations and planning. Be precise with numbers and include
all relevant statistics.

Always query multiple data sources to provide a complete picture."""

    def __init__(self):
        self.settings = get_settings()
        self._agent = None
        self._credential = None
        self._client = None

    async def __aenter__(self):
        """Initialize the agent with Azure credentials."""
        self._credential = DefaultAzureCredential()
        await self._credential.__aenter__()

        self._client = AzureAIAgentClient(
            project_endpoint=self.settings.azure_ai_project_endpoint,
            model_deployment_name=self.settings.azure_ai_model_deployment_name,
            async_credential=self._credential,
        )

        # Create the agent with MCP function tools
        self._agent = await self._client.create_agent(
            name="DataAnalyst",
            instructions=self.INSTRUCTIONS,
            tools=[
                get_shipments,
                get_aircraft_fleet,
                get_historical_volumes,
                get_routes,
                get_crew_availability,
            ]
        ).__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup agent resources."""
        if self._agent:
            await self._agent.__aexit__(exc_type, exc_val, exc_tb)
        if self._credential:
            await self._credential.__aexit__(exc_type, exc_val, exc_tb)

    async def analyze(self, date_from: date, date_to: date, hub: str = "Seattle") -> Dict[str, Any]:
        """
        Run the data analysis for the specified parameters.

        Args:
            date_from: Start date for analysis
            date_to: End date for analysis
            hub: Hub location (default: Seattle)

        Returns:
            Dictionary containing the analysis results and metrics
        """
        import time
        start_time = time.time()

        prompt = f"""Analyze shipment data for capacity planning:

Date Range: {date_from.isoformat()} to {date_to.isoformat()}
Hub: {hub}

Please query and compile:
1. All shipments for this date range from the {hub} hub
2. Current aircraft fleet availability
3. Historical volume data for the past 12 months
4. Available routes from {hub}
5. Current crew availability

Provide a comprehensive summary of all data gathered."""

        # Execute the agent
        result = await self._agent.run(prompt)

        duration_ms = int((time.time() - start_time) * 1000)

        # Calculate metrics (estimated for demo)
        input_tokens = len(prompt.split()) * 2  # Rough estimate
        output_tokens = len(result.text.split()) * 2

        metrics = AgentMetrics(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            cost_usd=self._calculate_cost(input_tokens, output_tokens),
            tool_calls=5  # We call all 5 MCP tools
        )

        return {
            "output": result.text,
            "metrics": metrics,
            "tools_used": [
                "get_shipments",
                "get_aircraft_fleet",
                "get_historical_volumes",
                "get_routes",
                "get_crew_availability"
            ]
        }

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost based on GPT-5-mini pricing."""
        input_cost = (input_tokens / 1_000_000) * self.settings.gpt5_mini_input_cost_per_million
        output_cost = (output_tokens / 1_000_000) * self.settings.gpt5_mini_output_cost_per_million
        return round(input_cost + output_cost, 6)
