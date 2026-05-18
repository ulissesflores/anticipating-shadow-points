"""Deterministic adjudication of shadow-point coverage.

Given an EvalSpec (expected shadow points) and an agent's free-text plan
(the candidate text), return a Coverage object enumerating which expected
points were matched and which were not. The function is pure: same inputs
always produce the same output.

The matcher uses a layered strategy, applied in order. The first layer
that fires for a given expected point wins, and the layer index is
recorded for audit:

  Layer 1 — exact normalized substring of the expected name in candidate.
  Layer 2 — exact normalized substring of any synonym (per-eval list).
  Layer 3 — Jaccard token overlap of expected.text vs sliding windows
            of candidate.text >= JACCARD_THRESHOLD.
  Layer 4 — no match.

Synonyms are loaded from an optional sidecar JSON file alongside the eval
markdown. The sidecar is not required; absent synonyms means layer 2 is
skipped for that eval. The sidecar schema is:

    {
      "synonyms": {
        "RLS policy update": ["row-level security", "row level security",
                              "RLS"],
        ...
      }
    }

JACCARD_THRESHOLD is exposed as a constant so the chosen value is auditable
in the source. Lowering it raises recall and lowers precision; the chosen
value (0.30) is tuned to be permissive enough for paraphrase but strict
enough that an unrelated sentence does not accidentally match.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .eval_parser import EvalSpec, ShadowPoint


JACCARD_THRESHOLD = 0.30  # tunable; changing it changes outputs deterministically
WINDOW_TOKENS = 40        # candidate is scanned in 40-token sliding windows
WINDOW_STRIDE = 10        # 10-token stride


# Words that contribute no semantic signal and are stripped before matching.
# This list is small on purpose — over-aggressive stop-word removal can
# silently change scores; aggressive lists should be added with care and
# accompanied by adjudicator tests.
_STOPWORDS: frozenset[str] = frozenset(
    """a an the of for to in on at by with from as is are was were be been
    being and or but if not no this that these those it its their there
    here will would shall should can could may might must do does did
    have has had we you i they he she him her us them my your our""".split()
)


def _normalize(text: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation except hyphens.

    Hyphens are preserved because they carry meaning in this domain
    ("row-level", "rate-limit").
    """
    text = text.lower()
    # Replace any non-alphanumeric (excluding hyphen) with a space.
    text = re.sub(r"[^a-z0-9\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _tokenize(text: str) -> list[str]:
    """Split normalized text into tokens, dropping stopwords."""
    return [t for t in _normalize(text).split() if t and t not in _STOPWORDS]


def _jaccard(a: set[str], b: set[str]) -> float:
    """Jaccard similarity of two token sets."""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union


def _sliding_windows(tokens: list[str], size: int, stride: int) -> list[set[str]]:
    """Build all windows of `size` tokens at `stride` steps. Each window is a
    set (for Jaccard); duplicate tokens within a window collapse."""
    if len(tokens) <= size:
        return [set(tokens)]
    return [
        set(tokens[i : i + size])
        for i in range(0, len(tokens) - size + 1, stride)
    ]


@dataclass(frozen=True)
class MatchedPoint:
    """One expected point that was successfully matched."""

    index: int
    name: str
    matched_via: str  # "exact_name" | "synonym" | "jaccard"
    jaccard_score: float  # 0.0 if matched non-Jaccard; >= threshold otherwise


@dataclass(frozen=True)
class UnmatchedPoint:
    """One expected point that was NOT matched."""

    index: int
    name: str
    best_jaccard: float  # the highest window-jaccard we saw; helps tune threshold


@dataclass
class Coverage:
    """Adjudication result for one eval + one candidate."""

    eval_id: str
    candidate_label: str  # "RED" or "GREEN"
    candidate_text_sha256: str
    matched: list[MatchedPoint] = field(default_factory=list)
    unmatched: list[UnmatchedPoint] = field(default_factory=list)
    jaccard_threshold: float = JACCARD_THRESHOLD

    @property
    def coverage(self) -> float:
        total = len(self.matched) + len(self.unmatched)
        if total == 0:
            return 0.0
        return len(self.matched) / total

    @property
    def passed_acceptance(self) -> bool:
        # Recomputed by caller against EvalSpec.acceptance_threshold.
        # Kept here for self-contained reporting only.
        return self.coverage >= 0.80

    def as_dict(self) -> dict:
        return {
            "eval_id": self.eval_id,
            "candidate_label": self.candidate_label,
            "candidate_text_sha256": self.candidate_text_sha256,
            "coverage": round(self.coverage, 4),
            "jaccard_threshold": self.jaccard_threshold,
            "matched": [asdict(m) for m in self.matched],
            "unmatched": [asdict(u) for u in self.unmatched],
        }


def load_synonyms(eval_source_path: Path) -> dict[str, list[str]]:
    """Load synonyms from <eval-file>.synonyms.json if present.

    The sidecar lives next to the eval markdown, named identically with
    .synonyms.json appended (after the .md is stripped). Absent file
    returns {}.
    """
    sidecar = eval_source_path.with_suffix(".synonyms.json")
    if not sidecar.exists():
        return {}
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"{sidecar}: invalid JSON: {e}") from e
    syns = data.get("synonyms", {})
    if not isinstance(syns, dict):
        raise ValueError(f"{sidecar}: 'synonyms' must be an object")
    return syns


def adjudicate(
    spec: EvalSpec,
    candidate_text: str,
    candidate_label: str,
    candidate_text_sha256: str,
) -> Coverage:
    """Score `candidate_text` against `spec.expected` deterministically."""
    synonyms = load_synonyms(spec.source_path)
    cand_norm = _normalize(candidate_text)
    cand_tokens = _tokenize(candidate_text)
    cand_windows = _sliding_windows(cand_tokens, WINDOW_TOKENS, WINDOW_STRIDE)

    matched: list[MatchedPoint] = []
    unmatched: list[UnmatchedPoint] = []

    for point in spec.expected:
        m = _match_point(point, cand_norm, cand_windows, synonyms)
        if isinstance(m, MatchedPoint):
            matched.append(m)
        else:
            unmatched.append(m)

    return Coverage(
        eval_id=spec.eval_id,
        candidate_label=candidate_label,
        candidate_text_sha256=candidate_text_sha256,
        matched=matched,
        unmatched=unmatched,
    )


def _match_point(
    point: ShadowPoint,
    cand_norm: str,
    cand_windows: list[set[str]],
    synonyms: dict[str, list[str]],
) -> MatchedPoint | UnmatchedPoint:
    """Run the four-layer match for one expected point."""
    name_norm = _normalize(point.name)

    # Layer 1: exact substring of the expected name in the candidate.
    if name_norm and name_norm in cand_norm:
        return MatchedPoint(
            index=point.index,
            name=point.name,
            matched_via="exact_name",
            jaccard_score=0.0,
        )

    # Layer 2: any provided synonym as a substring of the candidate.
    for syn in synonyms.get(point.name, []):
        syn_norm = _normalize(syn)
        if syn_norm and syn_norm in cand_norm:
            return MatchedPoint(
                index=point.index,
                name=point.name,
                matched_via="synonym",
                jaccard_score=0.0,
            )

    # Layer 3: best Jaccard over candidate windows.
    expected_tokens = set(_tokenize(point.text_for_matching))
    best = 0.0
    for window in cand_windows:
        j = _jaccard(expected_tokens, window)
        if j > best:
            best = j
    if best >= JACCARD_THRESHOLD:
        return MatchedPoint(
            index=point.index,
            name=point.name,
            matched_via="jaccard",
            jaccard_score=round(best, 4),
        )

    return UnmatchedPoint(
        index=point.index,
        name=point.name,
        best_jaccard=round(best, 4),
    )
