from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from opentelemetry.trace import Status, StatusCode

from .tracer import get_tracer
from .types import Document, Query, Response


class RAGPipeline:
    """
    Orchestrates a retrieval-augmented generation run:
      1. Retrieve relevant documents from the vector store.
      2. Generate an answer using the LLM.
    """

    def __init__(
        self,
        retrieve: Callable[[Query], Awaitable[list[Document]]],
        generate: Callable[[Query, list[Document]], Awaitable[str]],
    ) -> None:
        self._retrieve = retrieve
        self._generate = generate

    async def run(self, query: Query) -> Response:
        # Use start_as_current_span so the span's lifecycle is guaranteed on every
        # exit path: the context manager always ends the span (and thus exports it),
        # whether run() returns normally or unwinds on an exception. A downstream
        # failure is recorded and marked ERROR before re-raising, so failed runs
        # still produce a trace instead of silently disappearing.
        with get_tracer().start_as_current_span(
            "rag.pipeline.run",
            attributes={
                "query.id": query.id,
                "query.length": len(query.text),
            },
        ) as span:
            try:
                docs = await self._retrieve(query)
                answer = await self._generate(query, docs)
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR))
                raise

            span.set_status(StatusCode.OK)
            return Response(
                query_id=query.id,
                answer=answer,
                sources=docs,
                generated_at=time.time(),
            )
