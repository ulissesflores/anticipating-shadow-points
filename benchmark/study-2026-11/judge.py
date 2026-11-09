"""Blind judge for the 2026-11 study: merge the reference lists, then score each trial's table.

The judge is a model from another vendor, never Claude, because the skill's own methodology
cites the self-enhancement bias of same-family judges. The primary judge is Gemini 3.8 Flash (high)
through Google Antigravity. Grok, through its own CLI, is a second judge whose agreement is
reported. Each call runs from an empty folder with no file access. Every prompt and raw output is
kept under ``judge/`` and recorded in the ledger.

The judge sees the change request, the reference items and **only the rows of the answer's
table**, after a fixed redaction of words that would reveal the condition.

Usage::

    python judge.py merge                     # lists/<reviewer>/<task>.md -> lists/merged.json
    python judge.py trials --judge gemini     # runs/answers -> judge/gemini/<trial>.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from score import MIN_MERGED, numbered_items, table_rows

HERE = Path(__file__).resolve().parent
REVIEWERS = ["gemini", "gptoss", "grok"]
LETTER = {"gemini": "A", "gptoss": "B", "grok": "C"}
JUDGES = {
    "gemini": [
        "/Users/ulissesflores/.local/bin/agy", "-p", "{prompt}", "--model", "gemini-3.8-flash-high",
    ],
    "grok": ["/Users/ulissesflores/.grok/bin/grok", "-p", "{prompt}"],
}  # fmt: skip
REDACT = re.compile(
    r"\b(ASP|anticipating[- ]shadow[- ]points?|shadow[- ]points?|pre-?mortem|MAST|validator|"
    r"validated|Phase \d+|Iron Law \d*|charter|deliverables? register)\b",
    re.IGNORECASE,
)


def call(judge: str, prompt: str) -> str:
    """Run one judge call from an empty folder and return its raw output.

    Parameters
    ----------
    judge : str
        Key of ``JUDGES``.
    prompt : str
        The full prompt.

    Returns
    -------
    str
        Standard output of the CLI.
    """
    cmd = [prompt if part == "{prompt}" else part for part in JUDGES[judge]]
    with tempfile.TemporaryDirectory() as empty:
        for _ in range(
            8
        ):  # server-busy or denied-tool errors are retried; the answer is never edited
            out = subprocess.run(
                cmd,
                cwd=empty,
                capture_output=True,
                text=True,
                timeout=1500,
                stdin=subprocess.DEVNULL,
            )
            if out.returncode == 0 and "{" in out.stdout:
                return out.stdout
    raise RuntimeError(f"{judge}: no answer: {out.stderr[-300:]}")


def first_json(text: str) -> dict | list:
    """Return the first JSON object or array in a reply.

    Parameters
    ----------
    text : str
        Raw judge output.

    Returns
    -------
    dict or list
        The parsed value.
    """
    start = min(i for i in (text.find("{"), text.find("[")) if i >= 0)
    return json.JSONDecoder().raw_decode(text[start:])[0]


def merge_prompt(request: str, lists: dict[str, list[str]]) -> str:
    """Build the prompt that groups the three reviewers' items.

    Parameters
    ----------
    request : str
        The change request.
    lists : dict
        Reviewer name to items.

    Returns
    -------
    str
        The prompt.
    """
    body = "\n".join(
        f"{LETTER[r]}{i}. {item}" for r in REVIEWERS for i, item in enumerate(lists[r], 1)
    )
    return (
        "Three reviewers independently listed ways a software change could go wrong.\n\n"
        f"Change request: {request}\n\nItems (the letter is the reviewer):\n{body}\n\n"
        "Group the items that name the same underlying problem, even when worded differently. "
        "Every item belongs to exactly one group; an item with no match is a group of one. "
        "Answer directly from the text above; do not run commands or use tools. "
        'Answer with JSON only: {"groups": [["A1", "B3"], ["A2"], ...]}'
    )


def do_merge() -> dict:
    """Merge the lists with the primary judge and write ``lists/merged.json``.

    Returns
    -------
    dict
        Per task: reference items, counts and the share of each reviewer's items shared.
    """
    tasks = {t["id"]: t for t in json.loads((HERE / "tasks.json").read_text())["tasks"]}
    out_dir = HERE / "judge" / "merge"
    out_dir.mkdir(parents=True, exist_ok=True)

    def one(tid: str) -> tuple[str, dict]:
        """Merge one task's lists."""
        task = tasks[tid]
        lists = {
            r: numbered_items((HERE / "lists" / r / f"{tid}.md").read_text(encoding="utf-8"))
            for r in REVIEWERS
        }
        prompt = merge_prompt(task["request"], lists)
        cached = out_dir / f"{tid}.raw.txt"
        if (
            cached.exists()
            and (out_dir / f"{tid}.prompt.txt").read_text(encoding="utf-8") == prompt
        ):
            raw = cached.read_text(encoding="utf-8")  # a finished merge is never asked again
        else:
            raw = call("gemini", prompt)
            (out_dir / f"{tid}.prompt.txt").write_text(prompt, encoding="utf-8")
            cached.write_text(raw, encoding="utf-8")
        groups = first_json(raw)["groups"]
        lookup = {
            f"{LETTER[r]}{i}": (r, item) for r in REVIEWERS for i, item in enumerate(lists[r], 1)
        }
        seen = [k for g in groups for k in g]
        assert sorted(seen) == sorted(lookup), f"{tid}: groups do not cover every item once"
        reference = []
        for g in groups:
            owners = {lookup[k][0] for k in g}
            if len(owners) >= 2:
                first = sorted(g, key=lambda k: (k[0], int(k[1:])))[0]
                reference.append({"item": lookup[first][1], "from": lookup[first][0], "group": g})
        if len(reference) < MIN_MERGED:
            reference = [{"item": i, "from": r, "group": []} for r in REVIEWERS for i in lists[r]]
        shared = {
            r: round(
                sum(
                    1 for g in groups for k in g if k[0] == LETTER[r] and len({x[0] for x in g}) > 1
                )
                / len(lists[r]),
                3,
            )
            for r in REVIEWERS
        }
        return tid, {
            "reference": reference,
            "n_reference": len(reference),
            "n_by_reviewer": {r: len(v) for r, v in lists.items()},
            "share_named_by_another": shared,
        }

    with ThreadPoolExecutor(max_workers=len(tasks)) as pool:  # one call per task, in parallel
        merged = dict(sorted(pool.map(one, tasks)))
    (HERE / "lists" / "merged.json").write_text(json.dumps(merged, indent=1) + "\n")
    return merged


def trial_prompt(request: str, reference: list[str], rows: list[str]) -> tuple[str, int]:
    """Build the per-trial prompt from redacted table rows.

    Parameters
    ----------
    request : str
        The change request.
    reference : list of str
        Reference items.
    rows : list of str
        The answer's table rows.

    Returns
    -------
    tuple
        ``(prompt, redactions)``.
    """
    hits = sum(len(REDACT.findall(r)) for r in rows)
    clean = [REDACT.sub("[term]", r) for r in rows]
    refs = "\n".join(f"{i}. {item}" for i, item in enumerate(reference, 1))
    table = "\n".join(f"- {r}" for r in clean) or "- (no table)"
    prompt = (
        "A plan for a software change ends with a table of risks. Decide, for each reference "
        "problem, whether any row of the table addresses the same underlying problem (names it "
        "as a risk or mitigates it specifically), even if worded differently.\n\n"
        f"Change request: {request}\n\nReference problems:\n{refs}\n\nRows of the risk table:\n"
        f"{table}\n\n"
        "Answer directly from the text above; do not run commands or use tools. "
        'Answer with JSON only, one key per reference number: {"1": true, "2": false, ...}'
    )
    return prompt, hits


def do_trials(judge: str, folder: str) -> None:
    """Judge every answer of a run folder that has no verdict yet.

    Parameters
    ----------
    judge : str
        Key of ``JUDGES``.
    folder : str
        ``runs`` or ``pilot``.
    """
    tasks = {t["id"]: t for t in json.loads((HERE / "tasks.json").read_text())["tasks"]}
    merged = json.loads((HERE / "lists" / "merged.json").read_text())
    out_dir = HERE / "judge" / judge
    out_dir.mkdir(parents=True, exist_ok=True)
    trials = [json.loads(x) for x in (HERE / folder / "trials.jsonl").read_text().splitlines()]
    for tr in trials:
        dest = out_dir / f"{tr['trial']}.json"
        if dest.exists():
            continue
        answer = (HERE / folder / "answers" / f"{tr['trial']}.md").read_text(encoding="utf-8")
        reference = [r["item"] for r in merged[tr["task"]]["reference"]]
        prompt, hits = trial_prompt(tasks[tr["task"]]["request"], reference, table_rows(answer))
        raw = call(judge, prompt)
        verdict = first_json(raw)
        covered = [int(k) for k, v in verdict.items() if v is True]
        dest.write_text(
            json.dumps(
                {
                    "trial": tr["trial"],
                    "covered": sorted(covered),
                    "n": len(reference),
                    "redactions": hits,
                    "prompt": prompt,
                    "raw": raw,
                },
                indent=1,
            )  # fmt: skip
            + "\n"
        )
        print(tr["trial"], len(covered), "/", len(reference), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["merge", "trials"])
    ap.add_argument("--judge", default="gemini", choices=sorted(JUDGES))
    ap.add_argument("--folder", default="runs")
    a = ap.parse_args()
    if a.command == "merge":
        m = do_merge()
        print(
            json.dumps({t: {k: v for k, v in x.items() if k != "reference"} for t, x in m.items()})
        )
    else:
        do_trials(a.judge, a.folder)
