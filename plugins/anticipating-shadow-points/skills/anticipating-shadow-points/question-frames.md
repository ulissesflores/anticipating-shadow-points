# ASP Question Frames — Pre-Research and Post-Research

ASP enforces ≤3 questions in each Q&A phase. Use these frames.

---

## Pre-research Q&A (Phase 0a)

**Goal**: Sharpen scope, success criteria, and constraints BEFORE expensive research. Never ask about solution/implementation — that comes from Phase 1 + Phase 0b.

**Hard limit**: 3 questions in a single AskUserQuestion call. Multi-select OK when choices aren't mutually exclusive.

### Frame 1 — Scope boundaries

```
Question: "What is in-scope and out-of-scope for this work?"
Options:
  - In-scope: <minimal viable interpretation>
  - In-scope: <broader interpretation>
  - In-scope: <broadest interpretation>
```

### Frame 2 — Success criteria (measurable)

```
Question: "How will we know this is done?"
Options:
  - Measurable: <concrete metric or output>
  - Demoable: <user runs X and sees Y>
  - Tested: <test suite or eval passes>
```

### Frame 3 — Constraints

```
Question: "Which constraints apply?" (multi-select)
Options:
  - Deadline: <date or none>
  - Cost cap: <budget or none>
  - Platform: <macOS/linux/web/mobile>
  - Compliance: <none / specific regulation>
  - Backwards-compat: <required / breaking OK>
```

### Frame 4 — Stakeholders / audience

```
Question: "Who will use or review this?"
Options:
  - Only you (personal tool)
  - Team (internal docs needed)
  - Public (full docs + license)
  - Compliance/security review required
```

### Frame 5 — Existing prior work

```
Question: "Is there prior work to build on or replace?"
Options:
  - Greenfield (nothing exists)
  - Replace an existing thing (specify which)
  - Extend an existing thing
  - Don't know — research will find out
```

**Selection rule**: Pick 1-3 frames whose answer would change your research direction. If all are already known, skip Phase 0a entirely.

---

## Post-research Q&A (Phase 0b)

**Goal**: Resolve tradeoffs and priorities that emerged from research. Skip this phase entirely if research didn't surface any ambiguity.

**Hard limit**: 3 questions.

### Frame 1 — Tradeoff resolution

```
Question: "Research surfaced approach A vs B. Which fits your context?"
Options:
  - Approach A (pros: ..., cons: ...)
  - Approach B (pros: ..., cons: ...)
  - Hybrid (specify which parts of each)
  - Need more research on a specific aspect
```

### Frame 2 — Risk acceptance

```
Question: "We found <shadow point X>. How do we handle it?"
Options:
  - Mitigate now (adds <cost/time>)
  - Accept the risk (document and ship)
  - Re-scope to avoid it entirely
```

### Frame 3 — Priority among emergent shadow points

```
Question: "Top-3 shadow points found. Which must we mitigate before ship?" (multi-select)
Options:
  - Shadow point 1: <name>
  - Shadow point 2: <name>
  - Shadow point 3: <name>
  - All three (paranoid mode)
```

### Frame 4 — Scope drift signal

```
Question: "Research suggests the real problem is X, not what we initially scoped. Adjust scope?"
Options:
  - Keep original scope (X handled separately)
  - Pivot to X (re-do Phase 3 charter)
  - Both in parallel (split deliverables)
```

### Frame 5 — Validator stance

```
Question: "How strict should the validator subagent be?"
Options:
  - Standard (1 round)
  - Strict (2 rounds, advisor() if both REVISE)
  - Permissive (validator advises but planner decides)
```

**Selection rule**: If research went smoothly with no surprises, Phase 0b emits zero questions and proceeds to Phase 2.

---

## Anti-patterns (do not ask)

| Anti-pattern question | Why it's wrong |
|---|---|
| "Should I use React or Vue?" | This is implementation. Comes from Phase 1 research + technical analysis, not user input. |
| "Is this plan okay?" | That's what Phase 7 acceptance does formally, not a Q&A frame. |
| "Do you want a test?" | Iron Law 4 mandates acceptance tests. Never optional. |
| "What architecture should we use?" | Phase 4 macro-plan output. Not user input. |
| "How long do you want this to take?" | Time budget = constraint, ask via Frame 3 not separately. |
