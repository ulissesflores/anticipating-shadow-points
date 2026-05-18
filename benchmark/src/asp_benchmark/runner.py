"""Dispatch RED and GREEN conditions and collect candidate plans.

Two modes:

  - "real": spawn `claude -p --output-format json` with the eval's prompt
    wrapped as either RED (senior-engineer roleplay, no ASP) or GREEN
    (ASP discipline injected). Parses JSON per Iron Law 11/12.

  - "mock": load canned candidate plans from a fixtures directory.
    The fixtures pretend to be what claude returned. Used by unit tests
    and by users who want to exercise the adjudicator end-to-end without
    paying for inference. Mock outputs are committed to the repository
    so the unit-test path is deterministic and CI-runnable.

Both modes return a `Candidate` for each (eval, condition) pair. The
caller hashes the candidate text and uses it for adjudication and
provenance.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .eval_parser import EvalSpec


Condition = Literal["RED", "GREEN"]


# The RED prompt is intentionally minimal — it asks for a senior-engineer
# plan with no methodology, framework, or taxonomy hint. Changing this
# wording changes RED scores; the wording is therefore committed and any
# revision must be a deliberate version bump.
RED_TEMPLATE = """\
You are a senior software engineer. A colleague asks you to plan the
following task. Respond with the plan a senior engineer would draft,
without invoking any external framework, methodology, or shadow-point
taxonomy. Be specific.

Task:
{task}
"""

# The GREEN prompt injects the ASP discipline: pre-mortem framing, the
# MAST 14-mode forced enumeration, and an explicit mitigation requirement.
# It does NOT pass the expected list — that would be data leakage.
GREEN_TEMPLATE = """\
You are a senior software engineer using the ASP (Anticipating Shadow
Points) protocol. For the task below, do all of the following before any
code suggestion:

  (1) Pre-mortem: imagine it is 30 days in the future and the task has
      failed catastrophically. List 10+ concrete causes.

  (2) Iterate the MAST 14-mode failure taxonomy (Cemri et al. 2025):
      FC1 Specification & System Design — FM-1.1 disobey task spec,
        FM-1.2 disobey role spec, FM-1.3 step repetition,
        FM-1.4 loss of conversation history,
        FM-1.5 unaware of termination conditions.
      FC2 Inter-Agent Misalignment — FM-2.1 conversation reset,
        FM-2.2 fail to ask for clarification, FM-2.3 task derailment,
        FM-2.4 information withholding, FM-2.5 ignored other agent's input,
        FM-2.6 reasoning-action mismatch.
      FC3 Task Verification — FM-3.1 premature termination,
        FM-3.2 no/incomplete verification, FM-3.3 incorrect verification.
      For each mode, briefly state whether it applies.

  (3) Synthesize a single categorized list of shadow points with a
      one-line mitigation per item. Be specific about technical
      categories: data, integration, concurrency, time/timezone,
      observability, op-ex, contract drift, security, cost.

Task:
{task}
"""


@dataclass(frozen=True)
class Candidate:
    """One agent response, plus provenance fields needed by adjudication
    and manifest building."""

    eval_id: str
    condition: Condition
    prompt_sha256: str  # hash of the exact bytes sent to claude
    text: str           # the candidate plan, free-form prose
    text_sha256: str    # hash of `text` (UTF-8 bytes)
    raw_response: dict  # the JSON object returned by claude -p, or {} in mock
    refusal_detected: bool  # Iron Law 11: textual refusal heuristic
    terminal_reason: str    # from claude -p JSON, or "mock" in mock mode

    def as_dict(self) -> dict:
        return {
            "eval_id": self.eval_id,
            "condition": self.condition,
            "prompt_sha256": self.prompt_sha256,
            "text_sha256": self.text_sha256,
            "refusal_detected": self.refusal_detected,
            "terminal_reason": self.terminal_reason,
            # `text` is large and is also stored as its own file in the run
            # directory; we keep only the hash in manifest summaries.
        }


def build_prompt(spec: EvalSpec, condition: Condition) -> str:
    template = RED_TEMPLATE if condition == "RED" else GREEN_TEMPLATE
    return template.format(task=spec.input_prompt)


def dispatch_real(
    spec: EvalSpec,
    condition: Condition,
    *,
    model: str,
    max_turns: int = 1,
    timeout_seconds: int = 600,
) -> Candidate:
    """Spawn `claude -p` for one (eval, condition) pair.

    Iron Law 11/12 are honored: we always pass --output-format json and
    we never trust the exit code. We parse `is_error`, `terminal_reason`,
    `stop_reason`, and the textual `result`; refusal heuristics flag
    candidates that completed normally but refused semantically.
    """
    from .hasher import hash_bytes

    prompt = build_prompt(spec, condition)
    prompt_bytes = prompt.encode("utf-8")
    prompt_sha = hash_bytes(prompt_bytes)

    cmd = [
        "claude",
        "-p",
        "--output-format", "json",
        "--model", model,
        "--max-turns", str(max_turns),
    ]
    try:
        completed = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as e:
        raise RuntimeError(
            "claude CLI not found on PATH. Install Claude Code or run "
            "the benchmark in mock mode (--mode mock)."
        ) from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"{spec.eval_id}/{condition}: claude -p timed out after "
            f"{timeout_seconds}s"
        ) from e

    # Iron Law 11/12: never trust completed.returncode for semantic success.
    # Parse the JSON envelope.
    if not completed.stdout.strip():
        raise RuntimeError(
            f"{spec.eval_id}/{condition}: claude -p returned empty stdout. "
            f"stderr: {completed.stderr[:500]!r}"
        )
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"{spec.eval_id}/{condition}: claude -p stdout was not valid "
            f"JSON. First 500 chars: {completed.stdout[:500]!r}"
        ) from e

    text = response.get("result", "") or ""
    terminal_reason = (
        response.get("terminal_reason")
        or response.get("stop_reason")
        or "unknown"
    )
    refusal_detected = _detect_refusal(text)

    return Candidate(
        eval_id=spec.eval_id,
        condition=condition,
        prompt_sha256=prompt_sha,
        text=text,
        text_sha256=hash_bytes(text.encode("utf-8")),
        raw_response=response,
        refusal_detected=refusal_detected,
        terminal_reason=terminal_reason,
    )


def dispatch_mock(
    spec: EvalSpec,
    condition: Condition,
    *,
    fixtures_root: Path,
) -> Candidate:
    """Load a canned candidate from `fixtures_root/<eval_id>/<condition>.md`.

    The mock path is what unit tests and CI use; it lets us validate the
    adjudicator + manifest builder without paying for inference. Fixtures
    are committed to the repository as part of the auditable codebase.
    """
    from .hasher import hash_bytes

    prompt = build_prompt(spec, condition)
    prompt_bytes = prompt.encode("utf-8")
    prompt_sha = hash_bytes(prompt_bytes)

    path = fixtures_root / spec.eval_id / f"{condition}.md"
    if not path.exists():
        raise FileNotFoundError(
            f"mock fixture missing: {path}. Mock mode requires a fixture "
            f"per (eval_id, condition) pair."
        )
    text = path.read_text(encoding="utf-8")
    return Candidate(
        eval_id=spec.eval_id,
        condition=condition,
        prompt_sha256=prompt_sha,
        text=text,
        text_sha256=hash_bytes(text.encode("utf-8")),
        raw_response={"mode": "mock", "fixture": str(path)},
        refusal_detected=_detect_refusal(text),
        terminal_reason="mock",
    )


# Refusal heuristic: substrings that, if present in a completed response,
# indicate the agent semantically refused. This list is short on purpose;
# false negatives are preferable to false positives (a false positive would
# silently zero an honest plan's coverage). Maintenance burden goes up if
# the list grows beyond ~10 items.
_REFUSAL_PHRASES: tuple[str, ...] = (
    "i can't help with that",
    "i can't do that",
    "i won't",
    "i'm not able to",
    "i am unable to",
    "i cannot complete",
    "this request violates",
    "i cannot provide",
)


def _detect_refusal(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in _REFUSAL_PHRASES)
