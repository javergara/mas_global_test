import pytest

from mas_global.tracer import memory_exporter


@pytest.fixture(autouse=True)
def clear_spans():
    """Reset the in-memory span exporter before each test."""
    memory_exporter.clear()
    yield
