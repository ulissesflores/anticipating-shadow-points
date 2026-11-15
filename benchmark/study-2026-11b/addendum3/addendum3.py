"""Score the three reruns of study 2 (2026-11b) with the judge model through a paid API.

Exploratory, post hoc and a deviation from addendum 2; see ``ADDENDUM-3.md``, sealed before any
call below was made. Every output is written under this folder.

* ``judge`` scores the three reruns on both yardsticks and for relevance through OpenRouter.
* ``check`` scores a fixed sample of 30 sealed trials on the second yardstick the same way.
* ``results`` writes ``results4.json``.

Usage::

    OPENROUTER_API_KEY=<key> python addendum3.py judge
    OPENROUTER_API_KEY=<key> python addendum3.py check [--workers 4]
    python addendum3.py results
"""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
A2 = STUDY / "addendum2"
sys.path.insert(0, str(STUDY))
sys.path.insert(0, str(A2))

import judge  # noqa: E402
from addendum2 import (  # noqa: E402
    YARDSTICKS,
    cells_of,
    kappa,
    rerun_trials,
    sealed_trials,
    share,
    summary,
    tasks,
    valid,
)
from analyze import A, B, delta  # noqa: E402
from score import table_rows  # noqa: E402

URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-3.8-flash"
OUT = HERE / "openrouter"
SEED, SAMPLE = 20261115, 30


def call(prompt: str) -> dict:
    """Send one prompt and return the full API reply; an HTTP or API error is never a reply.

    Parameters
    ----------
    prompt : str
        The full prompt, sent as the only message.

    Returns
    -------
    dict
        The parsed API reply.
    """
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "reasoning": {"effort": "high"},
            "provider": {"only": ["google-ai-studio"], "allow_fallbacks": False},
        }
    ).encode()
    req = urllib.request.Request(
        URL,
        data=body,
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
        },
    )
    last = ""
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                reply = json.loads(resp.read())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = repr(exc)[:200]
        else:
            if not reply.get("error") and reply.get("choices"):
                content = reply["choices"][0]["message"].get("content")
                if isinstance(content, str) and content.strip():
                    return reply
            last = json.dumps(reply.get("error") or "empty reply")[:200]
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"openrouter: no answer: {last}")


def ask(prompt: str, n: int) -> tuple[dict, dict]:
    """Ask until the reply answers every item, at most three times; never edit a reply.

    Parameters
    ----------
    prompt : str
        The full prompt.
    n : int
        Number of items asked about.

    Returns
    -------
    tuple
        ``(verdict, full API reply)``.
    """
    for _ in range(3):
        reply = call(prompt)
        try:
            verdict = judge.first_json(reply["choices"][0]["message"]["content"])
        except ValueError:
            continue
        if valid(verdict, n):
            return verdict, reply
    raise RuntimeError("openrouter: no complete verdict")


def write(dest: Path, trial: str, prompt: str, hits: int, n: int) -> None:
    """Score one prompt and write the verdict unless it exists.

    Parameters
    ----------
    dest : Path
        Verdict file.
    trial : str
        Trial id.
    prompt : str
        The full prompt.
    hits : int
        Redactions the prompt builder made.
    n : int
        Number of items asked about.
    """
    if dest.exists():
        return
    verdict, reply = ask(prompt, n) if n else ({}, {})
    dest.parent.mkdir(parents=True, exist_ok=True)
    message = reply["choices"][0]["message"]["content"] if reply else ""
    envelope = {k: reply.get(k) for k in ("id", "model", "provider", "usage")} if reply else {}
    dest.write_text(
        json.dumps(
            {
                "trial": trial,
                "covered": sorted(int(k) for k, v in verdict.items() if v),
                "n": n,
                "redactions": hits,
                "prompt": prompt,
                "raw": message,
                "channel": "openrouter",
                "reasoning_effort": "high",
                "api": envelope,
            },
            indent=1,
        )
        + "\n"
    )
    print(dest.parent.name, trial, len(verdict and [v for v in verdict.values() if v]), "/", n)


def coverage_job(tr: dict, answer: str, yardstick: str, dest: Path) -> None:
    """Score one answer against one yardstick.

    Parameters
    ----------
    tr : dict
        Trial record.
    answer : str
        The trial's final reply.
    yardstick : str
        Key of ``YARDSTICKS``.
    dest : Path
        Verdict file.
    """
    merged = json.loads(YARDSTICKS[yardstick].read_text())
    reference = [r["item"] for r in merged[tr["task"]]["reference"]]
    prompt, hits = judge.trial_prompt(tasks()[tr["task"]]["request"], reference, table_rows(answer))
    write(dest, tr["trial"], prompt, hits, len(reference))


def do_judge() -> None:
    """Score the three reruns: both yardsticks, then relevance."""
    for tr in rerun_trials():
        answer = (A2 / "rerun" / "answers" / f"{tr['trial']}.md").read_text(encoding="utf-8")
        for y in YARDSTICKS:
            coverage_job(tr, answer, y, OUT / "rerun" / y / f"{tr['trial']}.json")
        rows = table_rows(answer)
        prompt, hits = judge.relevance_prompt(tasks()[tr["task"]]["request"], rows)
        dest = OUT / "rerun" / "relevance" / f"{tr['trial']}.json"
        write(dest, tr["trial"], prompt, hits, len(rows))


def sample() -> list[dict]:
    """Return the fixed sample of sealed trials that have a table.

    Returns
    -------
    list of dict
        ``SAMPLE`` trial records, drawn with ``SEED`` from the trial ids in order.
    """
    good = sorted((t for t in sealed_trials() if not t["is_error"]), key=lambda t: t["trial"])
    return sorted(random.Random(SEED).sample(good, SAMPLE), key=lambda t: t["trial"])


def do_check(workers: int) -> None:
    """Score the fixed sample against the second yardstick through the API.

    Parameters
    ----------
    workers : int
        Calls in parallel.
    """

    def one(tr: dict) -> None:
        """Score one sampled trial, after checking its prompt against the sealed one."""
        answer = (STUDY / "runs" / "answers" / f"{tr['trial']}.md").read_text(encoding="utf-8")
        merged = json.loads(YARDSTICKS["yardstick2"].read_text())
        reference = [r["item"] for r in merged[tr["task"]]["reference"]]
        prompt, _ = judge.trial_prompt(
            tasks()[tr["task"]]["request"], reference, table_rows(answer)
        )
        sealed = json.loads(
            (STUDY / "yardstick2" / "judge" / "gemini" / f"{tr['trial']}.json").read_text()
        )
        assert prompt == sealed["prompt"], tr["trial"]
        coverage_job(tr, answer, "yardstick2", OUT / "check" / "yardstick2" / f"{tr['trial']}.json")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(one, sample()))


def decisions(folder: Path, trials: list[dict]) -> dict:
    """Return every item-level decision in a folder of verdicts.

    Parameters
    ----------
    folder : Path
        Folder of verdict files.
    trials : list of dict
        Trial records.

    Returns
    -------
    dict
        ``{(trial, item number): covered}``.
    """
    out = {}
    for tr in trials:
        j = json.loads((folder / f"{tr['trial']}.json").read_text())
        out.update({(tr["trial"], i): i in j["covered"] for i in range(1, j["n"] + 1)})
    return out


def do_results() -> dict:
    """Write ``results4.json`` from whatever is complete.

    Returns
    -------
    dict
        The rerun rows under the API channel and the channel check.
    """
    sealed = sealed_trials()
    out: dict = {
        "note": "Exploratory, post hoc and a deviation from addendum 2 (ADDENDUM-3.md): the "
        "judge model reached through a paid API. No sealed file or fixed number is changed.",
        "model": MODEL,
        "channel": "openrouter, provider google-ai-studio, reasoning effort high",
    }
    reruns = {t["trial"]: t for t in rerun_trials()}
    rr = OUT / "rerun"
    kinds = (*YARDSTICKS, "relevance")
    if all((rr / k / f"{t}.json").exists() for k in kinds for t in reruns):
        out["rerun_trials"] = {
            tid: {k: 0.0 if tr["is_error"] else share(rr / k / f"{tid}.json") for k in kinds}
            for tid, tr in sorted(reruns.items())
        }
        bases = {
            "yardstick1": STUDY / "judge" / "gemini",
            "yardstick2": STUDY / "yardstick2" / "judge" / "gemini",
            "relevance": STUDY / "judge" / "relevance",
        }
        for k in kinds:

            def value(tr, k=k):
                if tr["trial"] in reruns:
                    return out["rerun_trials"][tr["trial"]][k]
                return 0.0 if tr["is_error"] else share(bases[k] / f"{tr['trial']}.json")

            cells = cells_of(sealed, value)
            if k == "relevance":
                out["relevance_with_reruns"] = {
                    "overall": {
                        c: round(statistics.fmean(v for x in cells.values() for v in x[c]), 4)
                        for c in (A, B)
                    },
                    "delta_bar": round(delta(cells)[0], 4),
                }
            else:
                out[f"{k}_with_reruns"] = summary(cells)
    chk = OUT / "check" / "yardstick2"
    picked = sample()
    if all((chk / f"{t['trial']}.json").exists() for t in picked):
        cli = STUDY / "yardstick2" / "judge" / "gemini"
        agreement = kappa(decisions(cli, picked), decisions(chk, picked))
        agreement["covered_cli"] = agreement.pop("covered_first")
        agreement["covered_api"] = agreement.pop("covered_second")
        out["channel_check"] = {
            "seed": SEED,
            "trials": [t["trial"] for t in picked],
            "items": agreement,
            "mean_coverage_cli": round(
                statistics.fmean(share(cli / f"{t['trial']}.json") for t in picked), 4
            ),
            "mean_coverage_api": round(
                statistics.fmean(share(chk / f"{t['trial']}.json") for t in picked), 4
            ),
            "trials_with_identical_verdict": sum(
                json.loads((cli / f"{t['trial']}.json").read_text())["covered"]
                == json.loads((chk / f"{t['trial']}.json").read_text())["covered"]
                for t in picked
            ),
        }
    (HERE / "results4.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


def main() -> None:
    """Parse arguments and run the chosen command."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["judge", "check", "results"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if args.command == "judge":
        do_judge()
    elif args.command == "check":
        do_check(args.workers)
    else:
        r = do_results()
        if args.quiet:
            parts = [
                f"{k}: delta {r[k]['delta_bar']:+.3f}, p = {r[k]['p']}"
                for k in ("yardstick1_with_reruns", "yardstick2_with_reruns")
                if k in r
            ]
            print("study2 rerun, API channel -> results4.json | " + " | ".join(parts))
        else:
            print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
