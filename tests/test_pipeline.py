from __future__ import annotations

import pytest
from opentelemetry.trace import StatusCode

from mas_global.pipeline import RAGPipeline
from mas_global.tracer import memory_exporter
from mas_global.types import Document, Query


def make_query() -> Query:
    return Query(id="q-001", text="What is retrieval-augmented generation?")


STUB_DOCS = [Document(id="d-1", content="RAG combines retrieval with generation.", score=0.95)]


async def stub_retrieve(query: Query) -> list[Document]:
    return STUB_DOCS


async def stub_generate(query: Query, docs: list[Document]) -> str:
    return "RAG is retrieval-augmented generation."


class TestRAGPipeline:
    async def test_returns_response_on_success(self):
        pipeline = RAGPipeline(retrieve=stub_retrieve, generate=stub_generate)
        response = await pipeline.run(make_query())
        assert response.query_id == "q-001"
        assert response.answer == "RAG is retrieval-augmented generation."
        assert response.sources == STUB_DOCS

    async def test_emits_finished_span_on_success(self):
        pipeline = RAGPipeline(retrieve=stub_retrieve, generate=stub_generate)
        await pipeline.run(make_query())

        spans = memory_exporter.get_finished_spans()
        assert len(spans) == 1
        assert spans[0].name == "rag.pipeline.run"
        assert spans[0].attributes["query.id"] == "q-001"

    async def test_closes_span_with_error_status_when_retrieve_raises(self):
        async def failing_retrieve(query: Query) -> list[Document]:
            raise RuntimeError("vector store unavailable")

        pipeline = RAGPipeline(retrieve=failing_retrieve, generate=stub_generate)

        with pytest.raises(RuntimeError, match="vector store unavailable"):
            await pipeline.run(make_query())

        spans = memory_exporter.get_finished_spans()
        assert len(spans) == 1
        assert spans[0].status.status_code == StatusCode.ERROR
