"""Second yardstick for study 2 (2026-11b): reference lists elicited with different words.

Exploratory and post hoc; see ``ADDENDUM.md``. The reviewers, the merge, the judge prompt and the
statistic are those of the study. Only the sentence that asks the reviewers for their list
changes, and every output is written under this folder, never over the sealed files.

Usage::

    ASP_STUDY_SCRATCH=<folder with repos/> python yardstick2.py lists [--workers 3]
    python yardstick2.py merge
    python yardstick2.py trials --judge gemini [--workers 6]
    python yardstick2.py results
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY))

import analyze  # noqa: E402
import judge  # noqa: E402
from score import numbered_items  # noqa: E402

AGY = "/Users/ulissesflores/.local/bin/agy"
REVIEWER_COMMANDS = {
    "grok": ["/Users/ulissesflores/.grok/bin/grok", "-p", "{prompt}"],
    "gptoss": [AGY, "-p", "{prompt}", "--model", "gpt-oss-120b-medium"],
    "gemini": [AGY, "-p", "{prompt}", "--model", "gemini-3.8-flash-high"],
}
MIN_ITEMS, MAX_ITEMS = 6, 12


def tasks() -> dict:
    """Return the study's tasks by id.

    Returns
    -------
    dict
        ``{task id: task}`` from the study's ``tasks.json``.
    """
    return {t["id"]: t for t in json.loads((STUDY / "tasks.json").read_text())["tasks"]}


def one_list(reviewer: str, task: dict) -> str:
    """Ask one reviewer for its list on a fresh clone of the pinned commit.

    A reply that does not parse as 6 to 12 numbered items is asked again, up to four times, and
    never edited.

    Parameters
    ----------
    reviewer : str
        Key of ``REVIEWER_COMMANDS``.
    task : dict
        The task entry.

    Returns
    -------
    str
        The reviewer's raw reply.
    """
    out_file = HERE / "lists" / reviewer / f"{task['id']}.md"
    if out_file.exists():
        return out_file.read_text(encoding="utf-8")
    mirror = Path(os.environ["ASP_STUDY_SCRATCH"]) / "repos" / task["repo"].rsplit("/", 1)[1]
    prompt = (HERE / "reference-list-2.txt").read_text().format(request=task["request"])
    cmd = [prompt if part == "{prompt}" else part for part in REVIEWER_COMMANDS[reviewer]]
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC"))}
    for _ in range(4):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / task["id"]
            subprocess.run(["git", "clone", "-q", str(mirror), str(work)], check=True)
            subprocess.run(["git", "-C", str(work), "checkout", "-q", task["commit"]], check=True)
            run = subprocess.run(
                cmd, cwd=work, env=env, capture_output=True, text=True, timeout=1800,
                stdin=subprocess.DEVNULL,
            )  # fmt: skip
        if run.returncode == 0 and MIN_ITEMS <= len(numbered_items(run.stdout)) <= MAX_ITEMS:
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(run.stdout, encoding="utf-8")
            return run.stdout
    raise RuntimeError(f"{reviewer} {task['id']}: no list of 6 to 12 items: {run.stderr[-300:]}")


def do_lists(workers: int) -> None:
    """Collect the 36 reviewer lists.

    Parameters
    ----------
    workers : int
        Reviewer calls in parallel.
    """
    jobs = [(r, t) for t in tasks().values() for r in REVIEWER_COMMANDS]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for (r, t), text in zip(jobs, pool.map(lambda j: one_list(*j), jobs), strict=True):
            print(r, t["id"], len(numbered_items(text)), "items", flush=True)


def do_results() -> dict:
    """Score the 240 answers against the second yardstick and write ``results2.json``.

    Returns
    -------
    dict
        One summary per judge, the size of each list and whose wording each risk carries.
    """
    trials = [json.loads(x) for x in (STUDY / "runs" / "trials.jsonl").read_text().splitlines()]
    merged = json.loads((HERE / "lists" / "merged.json").read_text())
    out: dict = {
        "note": "Exploratory and post hoc (ADDENDUM.md). The confirmatory analysis is "
        "../results.json.",
        "reference_risks_per_task": {k: v["n_reference"] for k, v in merged.items()},
        "wording_origin": {
            r: sum(i["from"] == r for v in merged.values() for i in v["reference"])
            for r in judge.REVIEWERS
        },
    }
    for name in ("gemini", "grok"):
        values: dict = {}
        for tr in sorted(trials, key=lambda r: r["trial"]):
            f = HERE / "judge" / name / f"{tr['trial']}.json"
            if not f.exists():
                break
            j = json.loads(f.read_text())
            v = round(len(j["covered"]) / j["n"], 4) if j["n"] and not tr["is_error"] else 0.0
            cell = values.setdefault((tr["task"], tr["model"]), {analyze.A: [], analyze.B: []})
            cell[tr["condition"]].append(v)
        else:
            summary = analyze.summarise(values, 5)
            summary.pop("decision")  # the decision rule belongs to the fixed analysis only
            out[name] = summary
    (HERE / "results2.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


def main() -> None:
    """Parse arguments and run the chosen command."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["lists", "merge", "trials", "results"])
    ap.add_argument("--judge", default="gemini", choices=sorted(judge.JUDGES))
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()
    if args.command == "lists":
        do_lists(args.workers)
    elif args.command == "results":
        r = do_results()
        for name in ("gemini", "grok"):
            if name in r:
                print(name, r[name]["overall"], r[name]["delta_bar"], r[name]["p"])
    else:
        judge.HERE = HERE  # every path of judge.py now resolves inside this folder
        if args.command == "merge":
            judge.do_merge()
        else:
            judge.do_trials(args.judge, "../runs", args.workers)


if __name__ == "__main__":
    main()
