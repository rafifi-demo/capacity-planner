"""
OpenTelemetry Configuration for Zava Capacity Planner

This module configures OpenTelemetry for comprehensive observability:
- Tracing: Track request flow through agents
- Metrics: Token usage, costs, latency
- Export to Azure Application Insights

TELEMETRY ARCHITECTURE:
FastAPI -> OpenTelemetry SDK -> Azure Monitor Exporter -> Application Insights
"""
import os
from typing import Optional, Dict, Any
from contextlib import contextmanager
import time

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

# Metrics
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Azure Monitor exporter
try:
    from azure.monitor.opentelemetry.exporter import (
        AzureMonitorTraceExporter,
        AzureMonitorMetricExporter
    )
    AZURE_MONITOR_AVAILABLE = True
except ImportError:
    AZURE_MONITOR_AVAILABLE = False


# Global tracer and meter instances
_tracer: Optional[trace.Tracer] = None
_meter: Optional[metrics.Meter] = None

# Metrics instruments
_token_counter: Optional[metrics.Counter] = None
_cost_counter: Optional[metrics.Counter] = None
_duration_histogram: Optional[metrics.Histogram] = None


def configure_telemetry(
    connection_string: Optional[str] = None,
    service_name: str = "zava-capacity-planner"
) -> trace.Tracer:
    """
    Configure OpenTelemetry with Azure Application Insights.

    Args:
        connection_string: Application Insights connection string
        service_name: Name of the service for tracing

    Returns:
        Configured tracer instance
    """
    global _tracer, _meter, _token_counter, _cost_counter, _duration_histogram

    # Create resource with service information
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.environ.get("ENVIRONMENT", "development")
    })

    # ========================================================================
    # TRACING CONFIGURATION
    # ========================================================================
    tracer_provider = TracerProvider(resource=resource)

    if connection_string and AZURE_MONITOR_AVAILABLE:
        # Production: Export to Azure Application Insights
        azure_exporter = AzureMonitorTraceExporter(
            connection_string=connection_string
        )
        tracer_provider.add_span_processor(
            BatchSpanProcessor(azure_exporter)
        )
    else:
        # Development: Console output (or no-op)
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        tracer_provider.add_span_processor(
            SimpleSpanProcessor(ConsoleSpanExporter())
        )

    trace.set_tracer_provider(tracer_provider)
    _tracer = trace.get_tracer(service_name)

    # ========================================================================
    # METRICS CONFIGURATION
    # ========================================================================
    if connection_string and AZURE_MONITOR_AVAILABLE:
        metric_exporter = AzureMonitorMetricExporter(
            connection_string=connection_string
        )
        metric_reader = PeriodicExportingMetricReader(
            metric_exporter,
            export_interval_millis=60000  # Export every minute
        )
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader]
        )
    else:
        meter_provider = MeterProvider(resource=resource)

    metrics.set_meter_provider(meter_provider)
    _meter = metrics.get_meter(service_name)

    # Create metrics instruments
    _token_counter = _meter.create_counter(
        name="agent.tokens",
        description="Number of tokens used by agents",
        unit="tokens"
    )

    _cost_counter = _meter.create_counter(
        name="agent.cost",
        description="Cost of agent operations in USD",
        unit="USD"
    )

    _duration_histogram = _meter.create_histogram(
        name="agent.duration",
        description="Duration of agent operations",
        unit="ms"
    )

    return _tracer


def get_tracer() -> trace.Tracer:
    """Get the configured tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("zava-capacity-planner")
    return _tracer


@contextmanager
def create_agent_span(
    agent_name: str,
    operation: str = "run",
    attributes: Optional[Dict[str, Any]] = None
):
    """
    Create a span for agent operations.

    Usage:
        with create_agent_span("DataAnalyst", "analyze") as span:
            result = await agent.analyze(...)
            span.set_attribute("tokens.output", 500)

    Args:
        agent_name: Name of the agent
        operation: Operation being performed
        attributes: Additional span attributes
    """
    tracer = get_tracer()
    span_name = f"{agent_name}.{operation}"

    with tracer.start_as_current_span(span_name) as span:
        # Set default attributes
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("agent.operation", operation)

        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        start_time = time.time()

        try:
            yield span
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            span.set_attribute("duration.ms", duration_ms)


def record_agent_metrics(
    agent_name: str,
    input_tokens: int,
    output_tokens: int,
    duration_ms: int,
    cost_usd: float
):
    """
    Record metrics for an agent operation.

    Args:
        agent_name: Name of the agent
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        duration_ms: Duration in milliseconds
        cost_usd: Cost in USD
    """
    global _token_counter, _cost_counter, _duration_histogram

    labels = {"agent": agent_name}

    if _token_counter:
        _token_counter.add(input_tokens, {"agent": agent_name, "type": "input"})
        _token_counter.add(output_tokens, {"agent": agent_name, "type": "output"})

    if _cost_counter:
        _cost_counter.add(cost_usd, labels)

    if _duration_histogram:
        _duration_histogram.record(duration_ms, labels)


class TelemetryCollector:
    """
    Collects and aggregates telemetry data for the workflow.

    This class provides real-time telemetry that can be streamed
    to the frontend via WebSocket.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = time.time()
        self.agent_data: Dict[str, Dict[str, Any]] = {}
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0

    def record_agent(
        self,
        agent_name: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: int,
        cost_usd: float,
        tool_calls: int = 0
    ):
        """Record metrics for an agent."""
        self.agent_data[agent_name] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "duration_ms": duration_ms,
            "cost_usd": cost_usd,
            "tool_calls": tool_calls
        }

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += cost_usd

        # Also record to OpenTelemetry
        record_agent_metrics(agent_name, input_tokens, output_tokens, duration_ms, cost_usd)

    def get_summary(self) -> Dict[str, Any]:
        """Get telemetry summary for display."""
        elapsed_ms = int((time.time() - self.start_time) * 1000)

        return {
            "session_id": self.session_id,
            "elapsed_ms": elapsed_ms,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "agents_completed": len(self.agent_data),
            "agents_total": 4,
            "agent_breakdown": self.agent_data
        }
