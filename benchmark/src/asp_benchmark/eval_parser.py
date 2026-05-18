"""Parser for the eval markdown files in skills/anticipating-shadow-points/evals/.

Each eval file has three sections we extract:

    # Eval NN — <title>
    ## INPUT
        <prompt text>
    ## EXPECTED SHADOW POINTS (>=8 required; >=80% coverage required for eval pass)
        1. **<name>** - <description>
        2. ...
    ## ACCEPTANCE
        <threshold prose>

The parser is intentionally permissive on prose but strict on the
numbered shadow-points list — the list is what adjudication operates on,
so a malformed entry must fail loudly rather than silently degrade coverage.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ShadowPoint:
    """One expected shadow point.

    `index` is the 1-based ordinal from the source markdown.
    `name` is the short label (bolded in the source).
    `description` is the explanation that follows the dash.
    """

    index: int
    name: str
    description: str

    @property
    def text_for_matching(self) -> str:
        """The text the adjudicator sees. Combines name and description so
        paraphrase matches can hit either part."""
        return f"{self.name}. {self.description}"


@dataclass(frozen=True)
class EvalSpec:
    """A single benchmark evaluation.

    `eval_id` is the canonical short identifier (e.g. "E1").
    `title` is the human-readable title from the markdown H1.
    `source_path` is the absolute path on disk; used for provenance hashing.
    """

    eval_id: str
    title: str
    input_prompt: str
    expected: tuple[ShadowPoint, ...]
    acceptance_threshold: float  # e.g. 0.80 for "80% coverage"
    source_path: Path


# Header detection. The eval markdown convention is:
#   # Eval 01 — <title>
# We accept "—" (em dash) or "-" between number and title.
_H1_PATTERN = re.compile(
    r"^#\s+Eval\s+(\d+)\s*[—\-]\s*(.+?)\s*$",
    re.MULTILINE,
)

# Section headers are ## with one of three labels.
_INPUT_HEADER = re.compile(r"^##\s+INPUT\s*$", re.MULTILINE)
_EXPECTED_HEADER = re.compile(r"^##\s+EXPECTED SHADOW POINTS.*$", re.MULTILINE)
_ACCEPTANCE_HEADER = re.compile(r"^##\s+ACCEPTANCE\s*$", re.MULTILINE)

# Each shadow point is a numbered list item with a bolded label.
#   1. **RLS policy update** — the new column ...
# We accept "—" or "-" between label and description.
_SHADOW_POINT_PATTERN = re.compile(
    r"^(\d+)\.\s+\*\*([^*]+)\*\*\s*[—\-]\s*(.+?)(?=^\d+\.\s+\*\*|\Z)",
    re.MULTILINE | re.DOTALL,
)

# Acceptance threshold: extract the "XX%" or "0.XX" mentioned in the
# acceptance section; default to 0.80 if not parseable.
_THRESHOLD_PERCENT = re.compile(r"(\d{1,3})\s*%")


def parse_eval(path: Path) -> EvalSpec:
    """Parse one eval markdown file. Raises ValueError on malformed input."""
    text = path.read_text(encoding="utf-8")

    h1_match = _H1_PATTERN.search(text)
    if not h1_match:
        raise ValueError(
            f"{path}: no '# Eval NN — title' header found. "
            "First line must match: # Eval 01 — Some Title"
        )
    eval_num = int(h1_match.group(1))
    eval_id = f"E{eval_num}"
    title = h1_match.group(2).strip()

    input_prompt = _extract_section(text, _INPUT_HEADER, _EXPECTED_HEADER, path)
    expected_block = _extract_section(text, _EXPECTED_HEADER, _ACCEPTANCE_HEADER, path)
    acceptance_block = _extract_section(text, _ACCEPTANCE_HEADER, None, path)

    expected = _parse_shadow_points(expected_block, path)
    if len(expected) < 1:
        raise ValueError(
            f"{path}: EXPECTED SHADOW POINTS section parsed zero entries. "
            f"Each entry must look like: 1. **Label** — description"
        )

    threshold = _parse_threshold(acceptance_block)

    return EvalSpec(
        eval_id=eval_id,
        title=title,
        input_prompt=input_prompt.strip(),
        expected=expected,
        acceptance_threshold=threshold,
        source_path=path.resolve(),
    )


def parse_evals_dir(root: Path) -> list[EvalSpec]:
    """Parse every .md eval under `root`, sorted by eval_id."""
    specs: list[EvalSpec] = []
    for p in sorted(root.glob("*.md")):
        # Skip non-eval markdown like README.md.
        if not _H1_PATTERN.search(p.read_text(encoding="utf-8")):
            continue
        specs.append(parse_eval(p))
    return sorted(specs, key=lambda s: s.eval_id)


def _extract_section(
    text: str,
    start_pattern: re.Pattern[str],
    end_pattern: re.Pattern[str] | None,
    path: Path,
) -> str:
    start = start_pattern.search(text)
    if start is None:
        raise ValueError(f"{path}: missing section {start_pattern.pattern}")
    start_idx = start.end()
    if end_pattern is None:
        return text[start_idx:]
    end = end_pattern.search(text, start_idx)
    end_idx = end.start() if end else len(text)
    return text[start_idx:end_idx]


def _parse_shadow_points(block: str, path: Path) -> tuple[ShadowPoint, ...]:
    points: list[ShadowPoint] = []
    for m in _SHADOW_POINT_PATTERN.finditer(block):
        idx = int(m.group(1))
        name = m.group(2).strip()
        description = m.group(3).strip()
        # Trim trailing blank lines and stray whitespace.
        description = re.sub(r"\s+", " ", description)
        points.append(ShadowPoint(index=idx, name=name, description=description))
    if not points:
        raise ValueError(
            f"{path}: EXPECTED block contained no parseable shadow points. "
            "Required format per line: 1. **Label** — description"
        )
    # Verify indices are sequential and start at 1 — guards against author
    # typos that would silently shift adjudication.
    expected_indices = list(range(1, len(points) + 1))
    actual_indices = [p.index for p in points]
    if actual_indices != expected_indices:
        raise ValueError(
            f"{path}: shadow points must be numbered 1..N sequentially; "
            f"got {actual_indices}"
        )
    return tuple(points)


def _parse_threshold(acceptance_block: str) -> float:
    m = _THRESHOLD_PERCENT.search(acceptance_block)
    if m:
        return int(m.group(1)) / 100.0
    return 0.80
