"""OpenTelemetry configuration and utilities."""
from .otel_config import configure_telemetry, get_tracer, create_agent_span

__all__ = ["configure_telemetry", "get_tracer", "create_agent_span"]
