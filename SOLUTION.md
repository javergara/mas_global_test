# Solution

## 1. What was the bug and where?

`src/mas_global/pipeline.py`: `RAGPipeline.run` started the span with `start_span()` but only called `set_status(OK)`/`end()` on the success path. When `_retrieve` or `_generate` raised, the exception unwound before `end()` ran, so `SimpleSpanProcessor` (which exports `on_end`) never received the span — the failed run's trace silently vanished. Fix: `start_as_current_span()` guarantees `end()` on every exit path; the `except` branch records the exception and sets ERROR before re-raising.

## 2. Retry span structure, and why?

One span per call, `retriever.with_retry`, with `retry.max_attempts`, `retry.attempts` (actual), and `retry.outcome` (ok/exhausted/aborted). A single low-cardinality span answers the PM's questions directly from attributes — how many attempts, and whether the result came from a retry — without per-attempt span noise or event parsing.

## 3. Next 20 minutes?

Extract a tracing port (Protocol) with an OTel adapter so the pipeline depends on an abstraction, not the SDK global — restoring hexagonal purity and enabling fast, SDK-free unit tests.
