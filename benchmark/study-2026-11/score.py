"""Deterministic scoring for the 2026-11 ASP study: reference lists, their merge, and plan coverage.

Everything here is fixed before the reference lists and the trials exist (see ``PROTOCOL.md``).
No model is called. Matching reuses the tokenizer of the shipped matcher
(``benchmark/src/asp_benchmark/adjudicator.py``) and replaces its window Jaccard by token recall:
an expected item matches a unit of text when the unit contains at least ``TAU`` of the item's
distinct tokens and at least ``MIN_SHARED`` of them.

Units are the rows of the answer's markdown table (every condition is asked for the same table).

Run ``python score.py calibrate`` to recompute ``TAU`` from the author-written fixtures of the
earlier mock benchmark (the lowest value at which no fixture line matches another task's
expected list).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from asp_benchmark.adjudicator import _tokenize  # noqa: E402
from asp_benchmark.eval_parser import parse_evals_dir  # noqa: E402

TAU = 0.3  # fixed by ``calibrate`` on 2026-11-09, before any reference list existed
MIN_SHARED = 3
MIN_MERGED = 5  # a merged list shorter than this falls back to the union of the three lists
ROW = re.compile(r"^\s*\|\s*\**\s*(\d+)\s*\**\s*\|(.+)$")


def tokens(text: str) -> set[str]:
    """Return the distinct content tokens of ``text``.

    Parameters
    ----------
    text : str
        Any text.

    Returns
    -------
    set of str
        Tokens after the shipped matcher's normalisation and stop-word removal.
    """
    return set(_tokenize(text))


def matches(item: str, unit: str, tau: float = TAU) -> bool:
    """Say whether ``unit`` covers ``item``.

    Parameters
    ----------
    item : str
        An expected item.
    unit : str
        A unit of candidate text.
    tau : float
        Token-recall threshold.

    Returns
    -------
    bool
        True when the unit holds at least ``tau`` of the item's tokens and ``MIN_SHARED`` of them.
    """
    e, u = tokens(item), tokens(unit)
    shared = len(e & u)
    return bool(e) and shared >= MIN_SHARED and shared / len(e) >= tau


def table_rows(answer: str) -> list[str]:
    """Return the numbered rows of the first markdown table in an answer.

    Parameters
    ----------
    answer : str
        The final reply of a trial.

    Returns
    -------
    list of str
        One string per numbered row, cells joined by spaces.
    """
    return [" ".join(m.group(2).split("|")) for ln in answer.splitlines() if (m := ROW.match(ln))]


def numbered_items(text: str) -> list[str]:
    """Return the items of a numbered list (a reviewer's reference list).

    Parameters
    ----------
    text : str
        Reviewer output.

    Returns
    -------
    list of str
        One string per item, continuation lines joined.
    """
    items: list[str] = []
    for line in text.splitlines():
        if re.match(r"^\s*\d+[.)]\s+", line):
            items.append(re.sub(r"^\s*\d+[.)]\s+", "", line).strip())
        elif items and line.strip():
            items[-1] += " " + line.strip()
    return [re.sub(r"[*_`]", "", i) for i in items]


def merge(lists: dict[str, list[str]]) -> tuple[list[dict], dict]:
    """Merge three reviewers' lists: keep items another reviewer also named.

    Reviewers are visited in sorted order; an item enters when an item of a different reviewer
    matches it in either direction, unless an item already kept matches it.

    Parameters
    ----------
    lists : dict
        Reviewer name to list of items.

    Returns
    -------
    tuple
        ``(reference, agreement)``: the kept items with their source, and the pairwise share of
        each reviewer's items matched by another reviewer.
    """

    def same(a: str, b: str) -> bool:
        """Say whether two items match in either direction."""
        return matches(a, b) or matches(b, a)

    names = sorted(lists)
    agreement = {
        f"{a}->{b}": round(
            sum(any(same(i, j) for j in lists[b]) for i in lists[a]) / len(lists[a]), 3
        )
        for a in names
        for b in names
        if a != b and lists[a]
    }
    kept: list[dict] = []
    for name in names:
        for item in lists[name]:
            others = [o for o in names if o != name]
            if any(same(item, j) for o in others for j in lists[o]) and not any(
                same(item, k["item"]) for k in kept
            ):
                kept.append({"item": item, "from": name})
    if len(kept) < MIN_MERGED:
        kept = [{"item": i, "from": n} for n in names for i in lists[n]]
    return kept, agreement


def coverage(reference: list[str], answer: str) -> dict:
    """Score one answer against one reference list.

    Parameters
    ----------
    reference : list of str
        Expected items.
    answer : str
        The trial's final reply.

    Returns
    -------
    dict
        Matched indices, coverage share, number of rows and number of words.
    """
    rows = table_rows(answer)
    hit = [i for i, item in enumerate(reference) if any(matches(item, r) for r in rows)]
    return {
        "matched": hit,
        "coverage": round(len(hit) / len(reference), 4) if reference else 0.0,
        "rows": len(rows),
        "words": len(answer.split()),
    }


def calibrate() -> float:
    """Return the lowest threshold at which no fixture line matches another task's list.

    Returns
    -------
    float
        The calibrated ``TAU`` (grid of 0.05).
    """
    root = HERE.parent / "tests" / "fixtures" / "mock_runs"
    evals = {
        e.eval_id: e
        for e in parse_evals_dir(
            HERE.parents[1]
            / "plugins/anticipating-shadow-points/skills/anticipating-shadow-points/evals"
        )
    }
    for step in range(1, 20):
        tau = round(step * 0.05, 2)
        cross = 0
        for fixture in sorted(root.glob("E*/GREEN.md")):
            own = fixture.parent.name
            lines = [ln for ln in fixture.read_text(encoding="utf-8").splitlines() if ln.strip()]
            for eid, spec in evals.items():
                if not eid.startswith(own):
                    cross += sum(
                        any(matches(p.text_for_matching, ln, tau) for ln in lines)
                        for p in spec.expected
                    )
        print(f"tau={tau:.2f} cross-task matches={cross}")
        if cross == 0:
            return tau
    return 1.0


if __name__ == "__main__":
    if sys.argv[1:] == ["calibrate"]:
        print("TAU =", calibrate())
    else:
        print(json.dumps({"TAU": TAU, "MIN_SHARED": MIN_SHARED, "MIN_MERGED": MIN_MERGED}))
