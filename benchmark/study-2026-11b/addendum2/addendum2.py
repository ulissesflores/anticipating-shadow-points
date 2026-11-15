"""Two unplanned additions to study 2 (2026-11b): a rerun of the error trials, and a third judge.

Exploratory and post hoc; see ``ADDENDUM-2.md``, sealed before any call below was made. Nothing
here replaces a sealed file or a fixed number: every output is written under this folder.

* ``rerun`` runs the three trials that ended in a network error once more, with ``run.py``'s own
  ``run_trial`` (same prompt, model, pinned commit, turn cap and settings), into ``rerun/``.
* ``judge-rerun`` scores those three answers with the Gemini judge on both yardsticks and for
  relevance, with the prompts of ``judge.py``.
* ``astra`` scores the 240 sealed answers, and the three reruns, against the second yardstick
  with a third judge (GPT-6 Astra through the Codex CLI).
* ``results`` writes ``results3.json``.

Usage::

    ASP_STUDY_SCRATCH=<new folder with repos/> ASP_STUDY_CONFIG=<config> python addendum2.py rerun
    python addendum2.py judge-rerun
    CODEX_HOME=<folder with auth.json only> python addendum2.py astra [--workers 4]
    python addendum2.py results
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
Y2 = STUDY / "yardstick2"
sys.path.insert(0, str(STUDY))

import judge  # noqa: E402
from analyze import MODELS, A, B, delta, permutation_p  # noqa: E402
from score import table_rows  # noqa: E402

ERROR_TRIALS = ["t097", "t099", "t100"]
ASTRA_MODEL = "gpt-6-astra"
ASTRA = [
    "/opt/homebrew/bin/codex", "exec", "--skip-git-repo-check", "--ephemeral", "-s", "read-only",
    "-m", ASTRA_MODEL, "-c", "model_reasoning_effort=high", "{prompt}",
]  # fmt: skip
YARDSTICKS = {
    "yardstick1": STUDY / "lists" / "merged.json",
    "yardstick2": Y2 / "lists" / "merged.json",
}
COMPARED = ["init_model", "models", "plugins", "asp_loaded", "project_files_changed"]


def sealed_trials() -> list[dict]:
    """Return the 240 sealed trial records.

    Returns
    -------
    list of dict
        The lines of ``../runs/trials.jsonl``.
    """
    return [json.loads(x) for x in (STUDY / "runs" / "trials.jsonl").read_text().splitlines()]


def tasks() -> dict:
    """Return the study's tasks by id.

    Returns
    -------
    dict
        ``{task id: task}``.
    """
    return {t["id"]: t for t in json.loads((STUDY / "tasks.json").read_text())["tasks"]}


def do_rerun() -> None:
    """Run each error trial once more into ``rerun/``; a trial already recorded is not run again."""
    import run  # imported here: it reads ASP_STUDY_SCRATCH and ASP_STUDY_CONFIG at import

    out = HERE / "rerun"
    out.mkdir(exist_ok=True)
    done = set()
    if (out / "trials.jsonl").exists():
        done = {json.loads(x)["trial"] for x in (out / "trials.jsonl").read_text().splitlines()}
    order = {t["trial"]: t for t in run.trials(5)}
    sealed = {t["trial"]: t for t in sealed_trials()}
    todo = []
    for tid in ERROR_TRIALS:
        cell = order[tid]
        assert all(sealed[tid][k] == cell[k] for k in ("task", "model", "condition", "rep")), tid
        assert sealed[tid]["is_error"], tid
        if tid not in done:
            todo.append(cell)
    all_tasks = tasks()
    with ThreadPoolExecutor(max_workers=3) as pool:
        for rec in pool.map(lambda t: run.run_trial(t, all_tasks[t["task"]], out), todo):
            print(
                rec["trial"], rec["task"], rec["model"], rec["condition"], rec["subtype"],
                rec["num_turns"], rec["seconds"], "s", flush=True,
            )  # fmt: skip


def rerun_trials() -> list[dict]:
    """Return the rerun records, one per error trial.

    Returns
    -------
    list of dict
        The lines of ``rerun/trials.jsonl``.
    """
    return [json.loads(x) for x in (HERE / "rerun" / "trials.jsonl").read_text().splitlines()]


def valid(verdict: dict, n: int) -> bool:
    """Say whether a verdict has exactly the keys 1..n with true or false values.

    Parameters
    ----------
    verdict : dict
        Parsed judge reply.
    n : int
        Number of items asked about.

    Returns
    -------
    bool
        ``True`` when the reply answers every item once and nothing else.
    """
    return sorted(verdict) == sorted(str(i) for i in range(1, n + 1)) and all(
        isinstance(v, bool) for v in verdict.values()
    )


def ask(judge_name: str, prompt: str, n: int) -> tuple[dict, str]:
    """Ask a judge until its reply answers every item, at most three times; never edit a reply.

    Parameters
    ----------
    judge_name : str
        Key of ``judge.JUDGES``.
    prompt : str
        The full prompt.
    n : int
        Number of items asked about.

    Returns
    -------
    tuple
        ``(verdict, raw reply)``.
    """
    for _ in range(3):
        raw = judge.call(judge_name, prompt)
        try:
            verdict = judge.first_json(raw)
        except ValueError:
            continue
        if valid(verdict, n):
            return verdict, raw
    raise RuntimeError(f"{judge_name}: no complete verdict")


def score_one(judge_name: str, tr: dict, answer: str, reference: list[str], dest: Path) -> None:
    """Write one coverage verdict unless it exists.

    Parameters
    ----------
    judge_name : str
        Key of ``judge.JUDGES``.
    tr : dict
        Trial record.
    answer : str
        The trial's final reply.
    reference : list of str
        Reference risks of the trial's task.
    dest : Path
        Verdict file.
    """
    if dest.exists():
        return
    request = tasks()[tr["task"]]["request"]
    prompt, hits = judge.trial_prompt(request, reference, table_rows(answer))
    verdict, raw = ask(judge_name, prompt, len(reference))
    dest.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "trial": tr["trial"],
        "covered": sorted(int(k) for k, v in verdict.items() if v),
        "n": len(reference),
        "redactions": hits,
        "prompt": prompt,
        "raw": raw,
    }
    if judge_name == "astra":
        record["judge_model"] = ASTRA_MODEL
    dest.write_text(json.dumps(record, indent=1) + "\n")
    print(
        dest.parent.parent.name,
        judge_name,
        tr["trial"],
        len(record["covered"]),
        "/",
        record["n"],
        flush=True,
    )


def do_judge_rerun() -> None:
    """Score the three reruns with the Gemini judge: both yardsticks, then relevance."""
    for tr in rerun_trials():
        answer = (HERE / "rerun" / "answers" / f"{tr['trial']}.md").read_text(encoding="utf-8")
        for name, merged_file in YARDSTICKS.items():
            reference = [
                r["item"] for r in json.loads(merged_file.read_text())[tr["task"]]["reference"]
            ]
            score_one(
                "gemini",
                tr,
                answer,
                reference,
                HERE / "rerun-judge" / name / "gemini" / f"{tr['trial']}.json",
            )
        dest = HERE / "rerun-judge" / "relevance" / "gemini" / f"{tr['trial']}.json"
        rows = table_rows(answer)
        if dest.exists():
            continue
        prompt, hits = judge.relevance_prompt(tasks()[tr["task"]]["request"], rows)
        verdict, raw = ask("gemini", prompt, len(rows)) if rows else ({}, "")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            json.dumps(
                {
                    "trial": tr["trial"],
                    "covered": sorted(int(k) for k, v in verdict.items() if v),
                    "n": len(rows),
                    "redactions": hits,
                    "prompt": prompt,
                    "raw": raw,
                },
                indent=1,
            )
            + "\n"
        )


def do_astra(workers: int) -> None:
    """Score the 240 sealed answers and the reruns against the second yardstick with GPT-6 Astra.

    Parameters
    ----------
    workers : int
        Judge calls in parallel.
    """
    judge.JUDGES["astra"] = ASTRA  # registered here; judge.py is not edited
    merged = json.loads(YARDSTICKS["yardstick2"].read_text())
    jobs = [
        (tr, STUDY / "runs" / "answers", HERE / "astra" / "yardstick2" / "astra")
        for tr in sealed_trials()
    ]
    if (HERE / "rerun" / "trials.jsonl").exists():
        jobs += [
            (tr, HERE / "rerun" / "answers", HERE / "rerun-judge" / "yardstick2" / "astra")
            for tr in rerun_trials()
        ]

    def one(job: tuple) -> None:
        """Score one answer."""
        tr, answers, out = job
        answer = (answers / f"{tr['trial']}.md").read_text(encoding="utf-8")
        reference = [r["item"] for r in merged[tr["task"]]["reference"]]
        score_one("astra", tr, answer, reference, out / f"{tr['trial']}.json")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(one, jobs))


def share(path: Path) -> float:
    """Return the coverage a verdict file gives.

    Parameters
    ----------
    path : Path
        A verdict file.

    Returns
    -------
    float
        Covered items over items, 0 when there is none.
    """
    j = json.loads(path.read_text())
    return round(len(j["covered"]) / j["n"], 4) if j["n"] else 0.0


def summary(cells: dict) -> dict:
    """Return the study's statistic and permutation p, pooled and per model.

    Parameters
    ----------
    cells : dict
        ``{"task|model": {condition: [coverage, ...]}}``.

    Returns
    -------
    dict
        Means per condition, mean difference, p, per-model values and the count of positive strata.
    """
    part = {m: {k: c for k, c in cells.items() if k.endswith(m)} for m in MODELS}
    d, per = delta(cells)
    return {
        "overall": {
            c: round(statistics.fmean(v for x in cells.values() for v in x[c]), 4) for c in (A, B)
        },
        "delta_bar": round(d, 4),
        "p": round(permutation_p(cells), 4),
        "by_model": {m: round(delta(part[m])[0], 4) for m in MODELS},
        "p_by_model": {m: round(permutation_p(part[m]), 4) for m in MODELS},
        "positive_strata": sum(x > 0 for x in per.values()),
        "strata": len(cells),
    }


def cells_of(trials: list[dict], value) -> dict:
    """Group one value per trial into task-by-model cells.

    Parameters
    ----------
    trials : list of dict
        Trial records.
    value : callable
        ``value(trial record) -> float``.

    Returns
    -------
    dict
        ``{"task|model": {condition: [value, ...]}}``.
    """
    cells: dict = {}
    for tr in sorted(trials, key=lambda r: r["trial"]):
        cells.setdefault(f"{tr['task']}|{tr['model']}", {A: [], B: []})[tr["condition"]].append(
            value(tr)
        )
    return cells


def kappa(first: dict, second: dict) -> dict:
    """Return item-level agreement of two judges and Cohen's kappa.

    Parameters
    ----------
    first, second : dict
        ``{(trial, item number): covered}`` per judge.

    Returns
    -------
    dict
        Items compared, share of agreement, each judge's share of "covered", and kappa.
    """
    keys = sorted(set(first) & set(second))
    n = len(keys)
    po = sum(first[x] == second[x] for x in keys) / n
    pa, pb = sum(first[x] for x in keys) / n, sum(second[x] for x in keys) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return {
        "items": n,
        "agreement": round(po, 4),
        "covered_first": round(pa, 4),
        "covered_second": round(pb, 4),
        "kappa": round((po - pe) / (1 - pe), 4),
    }


def items(folder: Path, trials: list[dict]) -> dict:
    """Return every item-level decision of one judge on trials that have a table.

    Parameters
    ----------
    folder : Path
        Folder of verdict files.
    trials : list of dict
        Trial records; error trials are left out.

    Returns
    -------
    dict
        ``{(trial, item number): covered}``.
    """
    out = {}
    for tr in trials:
        if tr["is_error"]:
            continue
        j = json.loads((folder / f"{tr['trial']}.json").read_text())
        out.update({(tr["trial"], i): i in j["covered"] for i in range(1, j["n"] + 1)})
    return out


def do_results() -> dict:
    """Write ``results3.json`` from whatever of the two additions is complete.

    Returns
    -------
    dict
        The rerun rows and the third judge's summary.
    """
    sealed = sealed_trials()
    out: dict = {
        "note": "Exploratory and post hoc (ADDENDUM-2.md). The confirmatory analysis is "
        "../results.json; the planned analysis of the second yardstick is "
        "../yardstick2/results2.json. Neither is changed by this file.",
    }
    rerun_file = HERE / "rerun" / "trials.jsonl"
    reruns = {t["trial"]: t for t in rerun_trials()} if rerun_file.exists() else {}
    judged = HERE / "rerun-judge"
    if len(reruns) == len(ERROR_TRIALS) and all(
        (judged / y / "gemini" / f"{t}.json").exists()
        for y in (*YARDSTICKS, "relevance")
        for t in reruns
    ):
        good = [t for t in sealed if not t["is_error"]]
        out["rerun"] = {"trials": {}, "compared_with_the_237_other_trials": {}}
        for tid, tr in sorted(reruns.items()):
            row = {
                k: tr[k]
                for k in (
                    "task",
                    "model",
                    "condition",
                    "rep",
                    "is_error",
                    "subtype",
                    "num_turns",
                    "seconds",
                )
            }
            row["rows_in_table"] = len(
                table_rows((HERE / "rerun" / "answers" / f"{tid}.md").read_text(encoding="utf-8"))
            )
            for y in (*YARDSTICKS, "relevance"):
                row[y] = 0.0 if tr["is_error"] else share(judged / y / "gemini" / f"{tid}.json")
            out["rerun"]["trials"][tid] = row
        for field in COMPARED:
            same_model = {
                tid: sorted({json.dumps(g[field]) for g in good if g["model"] == tr["model"]})
                for tid, tr in reruns.items()
            }
            out["rerun"]["compared_with_the_237_other_trials"][field] = {
                tid: {
                    "rerun": tr[field],
                    "seen_in_sealed_trials_of_that_model": [json.loads(v) for v in same_model[tid]],
                }
                for tid, tr in sorted(reruns.items())
            }
        for y, base in (
            ("yardstick1", STUDY / "judge" / "gemini"),
            ("yardstick2", Y2 / "judge" / "gemini"),
        ):

            def value(tr, y=y, base=base):
                if tr["trial"] in reruns:
                    return out["rerun"]["trials"][tr["trial"]][y]
                return 0.0 if tr["is_error"] else share(base / f"{tr['trial']}.json")

            out["rerun"][f"{y}_with_reruns"] = summary(cells_of(sealed, value))

        def relevance(tr):
            if tr["trial"] in reruns:
                return out["rerun"]["trials"][tr["trial"]]["relevance"]
            return (
                0.0
                if tr["is_error"]
                else share(STUDY / "judge" / "relevance" / f"{tr['trial']}.json")
            )

        cells = cells_of(sealed, relevance)
        out["rerun"]["relevance_with_reruns"] = {
            "overall": {
                c: round(statistics.fmean(v for x in cells.values() for v in x[c]), 4)
                for c in (A, B)
            },
            "delta_bar": round(delta(cells)[0], 4),
        }
    astra = HERE / "astra" / "yardstick2" / "astra"
    if all((astra / f"{t['trial']}.json").exists() for t in sealed):
        fixed = cells_of(
            sealed, lambda tr: 0.0 if tr["is_error"] else share(astra / f"{tr['trial']}.json")
        )
        out["astra"] = {
            "judge_model": ASTRA_MODEL,
            "yardstick2_fixed_rule": summary(fixed),
            "yardstick2_errors_as_full_coverage": summary(
                cells_of(
                    sealed,
                    lambda tr: 1.0 if tr["is_error"] else share(astra / f"{tr['trial']}.json"),
                )
            ),
            "agreement_with_gemini": kappa(
                items(Y2 / "judge" / "gemini", sealed), items(astra, sealed)
            ),
        }
        rj = judged / "yardstick2" / "astra"
        if reruns and all((rj / f"{t}.json").exists() for t in reruns):
            out["astra"]["yardstick2_with_reruns"] = summary(
                cells_of(
                    sealed,
                    lambda tr: (
                        (
                            0.0
                            if reruns[tr["trial"]]["is_error"]
                            else share(rj / f"{tr['trial']}.json")
                        )
                        if tr["trial"] in reruns
                        else (0.0 if tr["is_error"] else share(astra / f"{tr['trial']}.json"))
                    ),
                )
            )
    (HERE / "results3.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


def main() -> None:
    """Parse arguments and run the chosen command."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["rerun", "judge-rerun", "astra", "results"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if args.command == "rerun":
        do_rerun()
    elif args.command == "judge-rerun":
        do_judge_rerun()
    elif args.command == "astra":
        do_astra(args.workers)
    else:
        r = do_results()
        if args.quiet:
            parts = [
                f"{k}: delta {r['rerun'][k]['delta_bar']:+.3f}, p = {r['rerun'][k]['p']}"
                for k in ("yardstick1_with_reruns", "yardstick2_with_reruns")
                if "rerun" in r
            ]
            if "astra" in r:
                a = r["astra"]["yardstick2_fixed_rule"]
                parts.append(f"third judge: delta {a['delta_bar']:+.3f}, p = {a['p']}")
            print("study2 additions -> results3.json | " + " | ".join(parts))
        else:
            print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
