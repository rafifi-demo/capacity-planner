"""
Custom MCP Server for PostgreSQL

This MCP (Model Context Protocol) server exposes PostgreSQL database
operations as tools that can be called by AI agents. It connects to
the Zava logistics database and provides structured access to:

- Shipment data
- Aircraft fleet information
- Route information
- Crew availability
- Historical volumes

In production, this server runs behind Azure API Management (APIM)
for security, rate limiting, and monitoring.

AUTHENTICATION:
- Supports Managed Identity (Azure AD) for passwordless authentication
- Falls back to password-based auth when USE_MANAGED_IDENTITY=false
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import date, datetime
import asyncpg
import os

# Azure Identity for Managed Identity support
try:
    from azure.identity import DefaultAzureCredential
    AZURE_IDENTITY_AVAILABLE = True
except ImportError:
    AZURE_IDENTITY_AVAILABLE = False

# MCP SDK imports (when available)
# from mcp import Server, Tool, Resource

logger = logging.getLogger(__name__)


class PostgresMCPServer:
    """
    MCP Server that exposes PostgreSQL data as tools for AI agents.

    This server implements the Model Context Protocol to allow
    Foundry agents to query the database through structured tools.

    ARCHITECTURE:
    Agent -> APIM Gateway -> MCP Server -> PostgreSQL

    The APIM layer provides:
    - Authentication and authorization
    - Rate limiting
    - Request/response logging
    - DDoS protection

    AUTHENTICATION MODES:
    1. Managed Identity (recommended for production):
       - Set USE_MANAGED_IDENTITY=true
       - Uses DefaultAzureCredential to get Azure AD tokens
       - Token is used as password for PostgreSQL connection

    2. Password-based (fallback/local development):
       - Set USE_MANAGED_IDENTITY=false
       - Uses traditional connection string with password
    """

    def __init__(
        self,
        host: Optional[str] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        connection_string: Optional[str] = None,
        use_managed_identity: bool = False
    ):
        """
        Initialize the MCP server.

        Args:
            host: PostgreSQL server hostname
            database: Database name
            user: Username (managed identity name when using MI)
            password: Password (not used when using MI)
            connection_string: Full connection string (legacy support)
            use_managed_identity: Whether to use Azure AD authentication
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection_string = connection_string
        self.use_managed_identity = use_managed_identity
        self._pool: Optional[asyncpg.Pool] = None
        self._credential: Optional[DefaultAzureCredential] = None

    async def _get_access_token(self) -> str:
        """
        Get Azure AD access token for PostgreSQL.

        Returns:
            Access token string to use as password

        Raises:
            RuntimeError: If azure-identity is not installed
        """
        if not AZURE_IDENTITY_AVAILABLE:
            raise RuntimeError(
                "azure-identity package required for Managed Identity. "
                "Install with: pip install azure-identity"
            )

        if self._credential is None:
            self._credential = DefaultAzureCredential()

        # Get token for PostgreSQL resource
        token = self._credential.get_token(
            "https://ossrdbms-aad.database.windows.net/.default"
        )
        logger.info("Successfully acquired Azure AD token for PostgreSQL")
        return token.token

    async def start(self):
        """Start the MCP server and initialize database connection pool."""
        if self.use_managed_identity:
            # Use Managed Identity (Azure AD) authentication
            logger.info("Connecting to PostgreSQL with Managed Identity...")
            access_token = await self._get_access_token()

            self._pool = await asyncpg.create_pool(
                host=self.host,
                database=self.database,
                user=self.user,
                password=access_token,  # Token as password
                ssl='require',  # SSL required for Azure AD auth
                min_size=2,
                max_size=10
            )
            logger.info("Connected to PostgreSQL using Managed Identity")
        elif self.connection_string:
            # Legacy: Use connection string
            logger.info("Connecting to PostgreSQL with connection string...")
            self._pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=2,
                max_size=10
            )
        else:
            # Use individual parameters with password
            logger.info("Connecting to PostgreSQL with password...")
            self._pool = await asyncpg.create_pool(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                ssl='prefer',
                min_size=2,
                max_size=10
            )

    async def stop(self):
        """Stop the server and close connections."""
        if self._pool:
            await self._pool.close()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    # ========================================================================
    # MCP TOOL IMPLEMENTATIONS
    # ========================================================================

    async def get_shipments(
        self,
        date_from: str,
        date_to: str,
        hub: str
    ) -> Dict[str, Any]:
        """
        Query shipments from the database.

        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            hub: Origin hub location

        Returns:
            Dictionary with shipment data and statistics
        """
        async with self._pool.acquire() as conn:
            # Get shipment summary
            summary = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_shipments,
                    SUM(weight_kg) as total_weight,
                    SUM((dimensions_cm->>'volume')::numeric) as total_volume,
                    AVG(weight_kg) as avg_weight
                FROM shipments
                WHERE ship_date BETWEEN $1 AND $2
                AND origin_hub = $3
            """, date_from, date_to, hub)

            # Get destination breakdown
            destinations = await conn.fetch("""
                SELECT
                    destination,
                    COUNT(*) as shipment_count,
                    SUM(weight_kg) as total_weight
                FROM shipments
                WHERE ship_date BETWEEN $1 AND $2
                AND origin_hub = $3
                GROUP BY destination
                ORDER BY shipment_count DESC
                LIMIT 10
            """, date_from, date_to, hub)

            # Get priority breakdown
            priorities = await conn.fetch("""
                SELECT
                    priority,
                    COUNT(*) as count,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
                FROM shipments
                WHERE ship_date BETWEEN $1 AND $2
                AND origin_hub = $3
                GROUP BY priority
            """, date_from, date_to, hub)

            return {
                "summary": dict(summary) if summary else {},
                "destinations": [dict(d) for d in destinations],
                "priorities": [dict(p) for p in priorities],
                "query_params": {
                    "date_from": date_from,
                    "date_to": date_to,
                    "hub": hub
                }
            }

    async def get_aircraft_fleet(self) -> Dict[str, Any]:
        """
        Get available aircraft and specifications.

        Returns:
            Dictionary with fleet information
        """
        async with self._pool.acquire() as conn:
            aircraft = await conn.fetch("""
                SELECT
                    tail_number,
                    model,
                    max_cargo_kg,
                    max_volume_m3,
                    fuel_efficiency_km_per_l,
                    crew_required,
                    status
                FROM aircraft
                WHERE status != 'Retired'
                ORDER BY max_cargo_kg DESC
            """)

            # Calculate totals for available aircraft
            available = [a for a in aircraft if dict(a)['status'] == 'Available']

            return {
                "aircraft": [dict(a) for a in aircraft],
                "total_count": len(aircraft),
                "available_count": len(available),
                "total_available_capacity_kg": sum(a['max_cargo_kg'] for a in available),
                "total_available_volume_m3": sum(a['max_volume_m3'] for a in available)
            }

    async def get_routes(self, hub: str) -> Dict[str, Any]:
        """
        Get available routes from a hub.

        Args:
            hub: Origin hub (e.g., "Seattle")

        Returns:
            Dictionary with route information
        """
        async with self._pool.acquire() as conn:
            routes = await conn.fetch("""
                SELECT
                    origin,
                    destination,
                    distance_km,
                    typical_flight_hours
                FROM routes
                WHERE origin = $1
                ORDER BY distance_km
            """, hub)

            domestic = [r for r in routes if not self._is_international(dict(r)['destination'])]
            international = [r for r in routes if self._is_international(dict(r)['destination'])]

            return {
                "routes": [dict(r) for r in routes],
                "domestic_count": len(domestic),
                "international_count": len(international),
                "hub": hub
            }

    async def get_crew_availability(self) -> Dict[str, Any]:
        """
        Get current crew availability.

        Returns:
            Dictionary with crew availability information
        """
        async with self._pool.acquire() as conn:
            crew = await conn.fetch("""
                SELECT
                    name,
                    role,
                    certifications,
                    available
                FROM crew_members
                WHERE available = true
                ORDER BY role, name
            """)

            captains = [c for c in crew if dict(c)['role'] == 'Captain']
            first_officers = [c for c in crew if dict(c)['role'] == 'First Officer']
            flight_engineers = [c for c in crew if dict(c)['role'] == 'Flight Engineer']

            return {
                "crew": [dict(c) for c in crew],
                "captains_available": len(captains),
                "first_officers_available": len(first_officers),
                "flight_engineers_available": len(flight_engineers),
                "total_available": len(crew)
            }

    async def get_historical_volumes(
        self,
        hub: str,
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Get historical shipment volumes for trend analysis.

        Args:
            hub: Hub location
            months: Number of months of history

        Returns:
            Dictionary with historical volume data
        """
        async with self._pool.acquire() as conn:
            # Monthly volumes
            monthly = await conn.fetch("""
                SELECT
                    DATE_TRUNC('month', ship_date) as month,
                    COUNT(*) as shipment_count,
                    SUM(weight_kg) as total_weight
                FROM shipments
                WHERE origin_hub = $1
                AND ship_date >= CURRENT_DATE - INTERVAL '%s months'
                GROUP BY DATE_TRUNC('month', ship_date)
                ORDER BY month
            """ % months, hub)

            # Calculate YoY growth if we have enough data
            yoy_growth = None
            if len(monthly) >= 12:
                recent = sum(m['shipment_count'] for m in monthly[-6:])
                previous = sum(m['shipment_count'] for m in monthly[-12:-6])
                if previous > 0:
                    yoy_growth = round((recent - previous) / previous * 100, 1)

            return {
                "monthly_data": [
                    {
                        "month": m['month'].isoformat() if m['month'] else None,
                        "shipments": m['shipment_count'],
                        "weight_kg": float(m['total_weight']) if m['total_weight'] else 0
                    }
                    for m in monthly
                ],
                "hub": hub,
                "months_analyzed": months,
                "yoy_growth_percent": yoy_growth
            }

    def _is_international(self, destination: str) -> bool:
        """Check if a destination is international."""
        international_codes = ['NRT', 'LHR', 'FRA', 'HKG', 'SYD', 'CDG', 'AMS', 'SIN']
        return any(code in destination for code in international_codes)


# ============================================================================
# MCP SERVER RUNNER (for standalone operation)
# ============================================================================

def create_mcp_server_from_env() -> PostgresMCPServer:
    """
    Create MCP server instance from environment variables.

    Environment variables:
    - USE_MANAGED_IDENTITY: Set to 'true' for Azure AD auth (default: false)
    - POSTGRES_HOST: Database server hostname
    - POSTGRES_DATABASE: Database name
    - POSTGRES_USER: Username (managed identity name when using MI)
    - POSTGRES_PASSWORD: Password (not used when USE_MANAGED_IDENTITY=true)
    - POSTGRES_CONNECTION_STRING: Full connection string (legacy support)

    Returns:
        Configured PostgresMCPServer instance
    """
    use_managed_identity = os.environ.get("USE_MANAGED_IDENTITY", "false").lower() == "true"

    if use_managed_identity:
        logger.info("Initializing MCP server with Managed Identity authentication")
        return PostgresMCPServer(
            host=os.environ.get("POSTGRES_HOST"),
            database=os.environ.get("POSTGRES_DATABASE"),
            user=os.environ.get("POSTGRES_USER"),
            use_managed_identity=True
        )
    elif os.environ.get("POSTGRES_CONNECTION_STRING"):
        logger.info("Initializing MCP server with connection string")
        return PostgresMCPServer(
            connection_string=os.environ.get("POSTGRES_CONNECTION_STRING")
        )
    else:
        logger.info("Initializing MCP server with password authentication")
        return PostgresMCPServer(
            host=os.environ.get("POSTGRES_HOST"),
            database=os.environ.get("POSTGRES_DATABASE"),
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD")
        )


async def run_mcp_server(host: str = "0.0.0.0", port: int = 8001):
    """
    Run the MCP server as a standalone service.

    In production, this would implement the full MCP protocol.
    For the demo, we expose it as a simple HTTP API that the
    agents can call through APIM.

    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to listen on (default: 8001)
    """
    from fastapi import FastAPI
    import uvicorn

    app = FastAPI(
        title="Zava MCP Server",
        version="1.1.0",
        description="MCP Server with Managed Identity support for PostgreSQL"
    )
    server = create_mcp_server_from_env()

    @app.on_event("startup")
    async def startup():
        await server.start()

    @app.on_event("shutdown")
    async def shutdown():
        await server.stop()

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "managed_identity": server.use_managed_identity}

    @app.post("/tools/get_shipments")
    async def get_shipments(date_from: str, date_to: str, hub: str):
        return await server.get_shipments(date_from, date_to, hub)

    @app.get("/tools/get_aircraft_fleet")
    async def get_aircraft_fleet():
        return await server.get_aircraft_fleet()

    @app.get("/tools/get_routes")
    async def get_routes(hub: str):
        return await server.get_routes(hub)

    @app.get("/tools/get_crew_availability")
    async def get_crew_availability():
        return await server.get_crew_availability()

    @app.get("/tools/get_historical_volumes")
    async def get_historical_volumes(hub: str, months: int = 12):
        return await server.get_historical_volumes(hub, months)

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server_instance = uvicorn.Server(config)
    await server_instance.serve()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_mcp_server())
