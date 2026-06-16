from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from opentelemetry.trace import Status, StatusCode

from .tracer import get_tracer


async def with_retry[T](
    fn: Callable[[], Awaitable[T]],
    max_attempts: int,
    delay_s: float,
    should_retry: Callable[[Exception], bool] | None = None,
) -> T:
    """
    Retries an async callable up to *max_attempts* times with a fixed
    *delay_s* seconds between attempts. Propagates the last exception
    when all attempts are exhausted or *should_retry* returns False.
    """
    # Tracing: emit a single span per call, named "retriever.with_retry", so the
    # PM has visibility into retry behaviour against a degraded vector store.
    # Attributes use the "retry.*" namespace:
    #   - retry.max_attempts: the configured attempt budget
    #   - retry.attempts:     how many attempts were actually made
    #   - retry.outcome:      "ok" | "exhausted" | "aborted"
    # On terminal failure we record the exception and set ERROR status.
    with get_tracer().start_as_current_span(
        "retriever.with_retry",
        attributes={"retry.max_attempts": max_attempts},
    ) as span:
        for attempt in range(1, max_attempts + 1):
            try:
                result = await fn()
            except Exception as exc:
                exhausted = attempt == max_attempts
                aborted = should_retry is not None and not should_retry(exc)
                if exhausted or aborted:
                    span.set_attribute("retry.attempts", attempt)
                    span.set_attribute("retry.outcome", "exhausted" if exhausted else "aborted")
                    span.record_exception(exc)
                    span.set_status(Status(StatusCode.ERROR))
                    raise
                await asyncio.sleep(delay_s)
            else:
                span.set_attribute("retry.attempts", attempt)
                span.set_attribute("retry.outcome", "ok")
                span.set_status(StatusCode.OK)
                return result

        raise RuntimeError("unreachable")
