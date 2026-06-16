from __future__ import annotations

import pytest

from mas_global.retriever import with_retry
from mas_global.tracer import memory_exporter


class TestWithRetry:
    async def test_returns_on_first_success(self):
        calls = 0

        async def fn():
            nonlocal calls
            calls += 1
            return "ok"

        result = await with_retry(fn, max_attempts=3, delay_s=0)
        assert result == "ok"
        assert calls == 1

    async def test_retries_and_succeeds_on_later_attempt(self):
        calls = 0

        async def fn():
            nonlocal calls
            calls += 1
            if calls < 3:
                raise ConnectionError("timeout")
            return "recovered"

        result = await with_retry(fn, max_attempts=3, delay_s=0)
        assert result == "recovered"
        assert calls == 3

    async def test_raises_after_exhausting_all_attempts(self):
        async def fn():
            raise ConnectionError("always fails")

        with pytest.raises(ConnectionError, match="always fails"):
            await with_retry(fn, max_attempts=3, delay_s=0)

    async def test_stops_early_when_should_retry_returns_false(self):
        calls = 0

        async def fn():
            nonlocal calls
            calls += 1
            raise ValueError("non-retryable")

        with pytest.raises(ValueError):
            await with_retry(fn, max_attempts=5, delay_s=0, should_retry=lambda e: False)

        assert calls == 1

    # TODO: with_retry currently emits no spans.
    #
    # The PM needs visibility into retry behavior when the vector store is degraded:
    # how many attempts were made, and what was the final outcome.
    #
    # Add OTel tracing to with_retry in retriever.py so this test passes.
    # Span name, attribute names, and structure are your call.
    # Document your decisions in a short comment in the code.
    #
    # Remove the @pytest.mark.skip when the test passes.
    @pytest.mark.skip(reason="with_retry has no tracing yet — implement and remove this skip")
    async def test_emits_span_capturing_retry_attempts(self):
        calls = 0

        async def flaky():
            nonlocal calls
            calls += 1
            if calls < 2:
                raise ConnectionError("vector store timeout")
            return "result"

        await with_retry(flaky, max_attempts=3, delay_s=0)

        spans = memory_exporter.get_finished_spans()
        assert len(spans) > 0, "Expected at least one span from with_retry"

        retry_span = next((s for s in spans if "retry" in s.name.lower()), None)
        assert retry_span is not None, "Expected a span with 'retry' in the name"

        # Attribute names are your call — document them in retriever.py
        assert len(retry_span.attributes) > 0, "Expected the span to carry attributes"
