# Interview Guide — Senior Advanced Python Developer (AI-Assisted Development)

> **The one thing to internalize:** this interview does **not** score how clever your prompts are.
> It scores whether you can **detect an error, correct it, and direct the AI to a correct result** —
> your engineering judgment, your verification discipline, and how you steer the model. The AI is
> the typist. You are the senior engineer accountable for the outcome.

---

## 1. What is actually being evaluated

| They are watching for… | Not for… |
|---|---|
| Do you **notice** when the AI's output is wrong, subtly buggy, or over-engineered? | A perfectly worded one-shot prompt. |
| Can you **diagnose and correct** an error methodically (not by guessing)? | Memorizing syntax. |
| Do you **verify** — run tests, types, linters — before saying "done"? | Trusting generated code on sight. |
| Do you **own the architecture** and impose constraints (SOLID, hexagonal, TDD)? | Letting the model decide everything. |
| Do you keep changes **small and reviewable** and explain your reasoning? | Big-bang dumps of code. |

If you remember nothing else: **read everything the AI produces, run it, and prove it works.**

---

## 2. Mindset: you are the tech lead, the AI is a fast junior

- A junior who types fast and knows the stdlib but has **no taste, no accountability, and will
  confidently produce plausible-wrong code**. Your value is judgment: framing, constraints, review.
- Talk out loud. The interviewer is scoring your *thinking*, so narrate: "I'll define the port first
  so the domain stays testable," "that mypy error means a `None` is leaking — let me handle it at the
  source, not cast it away."
- Slow is smooth, smooth is fast. One verified slice beats three unverified features.

---

## 3. The live loop (use the harness)

This repo ships specialist agents and skills (see `CLAUDE.md`). Drive them in this order:

```
requirement
  └─ architect      → thin hexagonal design: domain, ports, first TDD slice, what NOT to build
       └─ python-pro / tdd-feature   → red → green → refactor on one slice
            └─ run the gate          → uv run ruff check . && uv run mypy src && uv run pytest
                 └─ something broke?  → debug-fix / debugger  (reproduce → root-cause → fix → verify)
                      └─ code-reviewer / /code-review  → correctness, SOLID, coverage, over-engineering
                           └─ iterate on the next slice
```

Don't plan ten steps up front. Get **one slice fully green**, then re-plan. The `orchestrator` agent
can produce the delegation plan if the sequence isn't obvious.

---

## 4. Error-detection & correction playbook (the heart of the score)

When anything breaks — a traceback, a failing test, a mypy/ruff error, wrong output — **do not guess
and patch.** Run the loop (this is what `debug-fix` / the `debugger` agent encode):

1. **Capture** the full error. Read it aloud. mypy gives you an error *code* (`[arg-type]`,
   `[union-attr]`, `[return-value]`); ruff gives you a *rule* (`B006`, `SIM…`). Those name the
   category before you read a line of code.
2. **Reproduce** with the smallest failing command. If there's no test, **write a failing test that
   reproduces the bug** — it's both your repro and your regression guard.
3. **Hypothesize** one cause and say it out loud: "I think X because Y." Confirm or kill it by
   inspecting, not editing.
4. **Root-cause** it. The bottom of a traceback is usually where the bug *surfaced*, not where the
   bad value was *born*. Trace upward.
5. **Minimal fix** — change the least code that addresses the cause; don't refactor in the same pass.
6. **Verify green** — repro test passes, full gate passes, nothing regressed.
7. **Leave the test in** so it can't silently come back.

> Interview gold: catching a bug the AI *introduced* and walking through this loop is exactly the
> behavior being tested. Make it visible.

**Tells that AI output is wrong** — scan for these every time:
- Swallowed exceptions (`except: pass`), broad `except Exception`.
- Mutable default arguments, off-by-one in ranges/slices, `==` vs `is`.
- A `cast(...)` or `# type: ignore` hiding a real `None`/type problem.
- Tests that assert implementation details, or that would pass even if the code were wrong.
- Domain code importing a framework or doing I/O (broken hexagonal boundary).
- Generic machinery (a "repository base class", config flags) for a single caller — over-engineering.

---

## 5. How to direct the AI well

- **State acceptance criteria up front.** "Implement `reserve_stock`; it must reject quantities over
  available stock with a domain error, be covered by a test that fails first, and pass mypy strict."
- **Constrain scope.** "One slice only. No persistence yet — use an in-memory adapter behind the
  `StockRepository` port."
- **Demand the design before the code** for anything non-trivial — ask the `architect` for ports and
  trade-offs first.
- **Ask for alternatives + trade-offs** when there's a real decision: "give me two approaches and
  why you'd pick one." Then *you* choose and justify.
- **Reject over-engineering explicitly.** "That's premature — delete the abstraction, inline it."
- **Always require verification.** "Run ruff, mypy, and pytest and show me the output." Never accept
  "this should work."
- **Correct, don't restart.** When output is wrong, point at the specific defect and the fix
  direction — that's the steering they want to see, not a fresh mega-prompt.

---

## 6. Seniority talking points (drop these naturally)

- **SOLID, applied** — "I'll depend on a port here so the use case doesn't know about HTTP/DB"
  (DIP + ISP), "single responsibility — parsing and persistence are different reasons to change."
- **Deep modules (Ousterhout)** — "narrow interface, complexity hidden behind it; I'd rather one
  clear function than five shallow helpers."
- **Hexagonal** — domain pure at the center, ports define needs, adapters at the edges depend inward.
- **TDD** — "test first so the design stays testable and I have a regression guard."
- **Microservice concerns** (if relevant) — idempotency, explicit error contracts, observability
  (structured logging/metrics), timeouts/retries at adapters, no shared mutable state.

---

## 7. Do / Don't

**Do**
- Read every diff before accepting it. Run the gate after every slice.
- Keep changes small; commit-sized increments.
- Narrate your reasoning and your verification.
- Write the failing test first; keep it after the fix.
- Say "I don't know yet — let me reproduce it" instead of guessing.

**Don't**
- Trust generated code on sight or paste it without reading.
- Silence type errors with `cast`/`# type: ignore` to move on.
- Fix a symptom without finding the cause.
- Let the model expand scope or add speculative abstraction.
- Claim "done" without a green `ruff` + `mypy` + `pytest`.

---

## 8. Dry-run script (rehearse the day before)

In a fresh session in this repo, do a full rep end-to-end:

1. Invent a small microservice requirement, e.g. *"a stock-reservation use case: reserve N units of
   a SKU; reject if insufficient; expose it behind a port."*
2. Ask the **architect** for the design (domain, `StockRepository` port, first slice, what to skip).
3. Use **`tdd-feature`** / **python-pro** to implement the first slice test-first.
4. Run `uv run ruff check . && uv run mypy src && uv run pytest`.
5. **Deliberately introduce a bug** (e.g. flip a comparison, drop a `None` check), watch it fail,
   then run **`debug-fix`** / the **debugger** to find the root cause and fix it.
6. Ask **code-reviewer** (or `/code-review`) to review the diff; address the top finding.
7. Time yourself. Practice narrating. The smoothness of this loop is the interview.

You've got this — own the architecture, verify everything, and make your error-correction loop
visible.
