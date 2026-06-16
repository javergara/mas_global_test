from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Query:
    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    id: str
    content: str
    score: float


@dataclass
class Response:
    query_id: str
    answer: str
    sources: list[Document]
    generated_at: float
