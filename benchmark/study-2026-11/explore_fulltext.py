"""Exploratory, written after the primary result: judge the whole answer, not only its table.

Question: does GREEN address more reference problems in its plan text than in its final table?
The primary analysis is unchanged; this check is labelled exploratory in PROTOCOL.md. Same judge
(Gemini 3.8 Flash), same redaction, same reference lists; only the input is the full answer.

Usage::

    python explore_fulltext.py            # GREEN and RED-risk trials -> judge/gemini-full/
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

from judge import HERE, REDACT, call, first_json

CONDITIONS = ("GREEN", "RED-risk")


def prompt_for(request: str, reference: list[str], answer: str) -> tuple[str, int]:
    """Build the full-text prompt.

    Parameters
    ----------
    request : str
        The change request.
    reference : list of str
        Reference problems.
    answer : str
        The whole final reply.

    Returns
    -------
    tuple
        ``(prompt, redactions)``.
    """
    hits = len(REDACT.findall(answer))
    refs = "\n".join(f"{i}. {item}" for i, item in enumerate(reference, 1))
    return (
        "Below is a plan for a software change. Decide, for each reference problem, whether the "
        "plan addresses the same underlying problem anywhere in its text (names it as a risk, or "
        "plans for it specifically), even if worded differently.\n\n"
        f"Change request: {request}\n\nReference problems:\n{refs}\n\nPlan:\n"
        f"{REDACT.sub('[term]', answer)}\n\n"
        "Answer directly from the text above; do not run commands or use tools. "
        'Answer with JSON only, one key per reference number: {"1": true, "2": false, ...}'
    ), hits


def main() -> None:
    """Judge every GREEN and RED-risk answer in full and print coverage per condition."""
    tasks = {t["id"]: t for t in json.loads((HERE / "tasks.json").read_text())["tasks"]}
    merged = json.loads((HERE / "lists" / "merged.json").read_text())
    trials = [json.loads(x) for x in (HERE / "runs" / "trials.jsonl").read_text().splitlines()]
    out = HERE / "judge" / "gemini-full"
    out.mkdir(parents=True, exist_ok=True)

    def one(tr: dict) -> None:
        """Judge one full answer unless it already has a verdict."""
        dest = out / f"{tr['trial']}.json"
        if dest.exists() or tr["condition"] not in CONDITIONS:
            return
        answer = (HERE / "runs" / "answers" / f"{tr['trial']}.md").read_text(encoding="utf-8")
        reference = [r["item"] for r in merged[tr["task"]]["reference"]]
        prompt, hits = prompt_for(tasks[tr["task"]]["request"], reference, answer)
        for _ in range(3):
            raw = call("gemini", prompt)
            try:
                verdict = first_json(raw)
                break
            except ValueError:
                continue
        else:
            raise RuntimeError(f"no readable verdict for {tr['trial']}")
        covered = sorted(int(k) for k, v in verdict.items() if v is True)
        dest.write_text(
            json.dumps(
                {
                    "trial": tr["trial"],
                    "covered": covered,
                    "n": len(reference),
                    "redactions": hits,
                    "prompt": prompt,
                    "raw": raw,
                },
                indent=1,
            )  # fmt: skip
            + "\n"
        )

    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(one, trials))
    for cond in CONDITIONS:
        full = table = 0.0
        ids = [t["trial"] for t in trials if t["condition"] == cond]
        for tid in ids:
            f = json.loads((out / f"{tid}.json").read_text())
            t = json.loads((HERE / "judge" / "gemini" / f"{tid}.json").read_text())
            full += len(f["covered"]) / f["n"]
            table += len(t["covered"]) / t["n"]
        print(f"{cond}: table {table / len(ids):.3f}  full text {full / len(ids):.3f}")


if __name__ == "__main__":
    main()
