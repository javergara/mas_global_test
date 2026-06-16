from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# memory_exporter is exported so tests can read finished spans.
# Call memory_exporter.clear() in a fixture to isolate test cases.
memory_exporter = InMemorySpanExporter()

_provider = TracerProvider()
_provider.add_span_processor(SimpleSpanProcessor(memory_exporter))
trace.set_tracer_provider(_provider)


def get_tracer() -> trace.Tracer:
    return trace.get_tracer("rag-pipeline", "0.1.0")
