from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable


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
    for attempt in range(1, max_attempts + 1):
        try:
            return await fn()
        except Exception as exc:
            if attempt == max_attempts:
                raise
            if should_retry is not None and not should_retry(exc):
                raise
            await asyncio.sleep(delay_s)

    raise RuntimeError("unreachable")
