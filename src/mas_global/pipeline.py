from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from opentelemetry.trace import StatusCode

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
        span = get_tracer().start_span(
            "rag.pipeline.run",
            attributes={
                "query.id": query.id,
                "query.length": len(query.text),
            },
        )

        docs = await self._retrieve(query)
        answer = await self._generate(query, docs)

        span.set_status(StatusCode.OK)
        span.end()

        return Response(
            query_id=query.id,
            answer=answer,
            sources=docs,
            generated_at=time.time(),
        )
