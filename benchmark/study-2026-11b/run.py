"""Run study 2 (2026-11b): two conditions, two models, twelve pinned repositories, seeded order.

Each trial clones the task's repository at its pinned commit into a fresh folder, runs one
``claude -p`` session in plan mode, keeps the full ``stream-json`` envelope, and records the final
reply. The two conditions differ only by one sentence in the prompt; turn cap, permission mode,
output contract and configuration folder are the same, and no plugin is enabled in any trial.
Every task x condition cell runs on both models.

Usage::

    python run.py plan --replicates 5    # print the seeded trial order
    python run.py go --replicates 5 --workers 2 [--only t001,t002] [--pilot]
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import gzip
import hashlib
import json
import os
import random
import re
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRATCH = Path(os.environ.get("ASP_STUDY_SCRATCH", HERE / ".scratch"))
CONFIG = Path(os.environ.get("ASP_STUDY_CONFIG", ""))
MODELS = ["claude-opus-5-5", "claude-sonnet-5-5"]
MAX_TURNS = 60
SEED = "asp-study2-2026-11b"
PLUGIN_ID = "anticipating-shadow-points@anticipating-shadow-points"
SYNCED_OFF = [
    "pdf-viewer@synced",
    "engineering@synced",
    "productivity@synced",
    "sales@synced",
    "data@synced",
]

CONTRACT = (
    "Non-interactive run: state your assumptions instead of asking. Do not edit any file. "
    "Answer in English. End your answer with the main risks of this change as one markdown table "
    "with columns #, Risk, Why it bites here, Mitigation (at most 10 rows, short cells), then one "
    'line starting "Riskiest:" naming the riskiest one.'
)
CONDITIONS = {
    "RED-plain": "{request}\n\nPlan this change.\n\n" + CONTRACT,
    "RED-risk": "{request}\n\nBefore planning, list the ways this change could go wrong.\n\n"
    + CONTRACT,
}
# Exploratory only, run only if the confirmatory trials finish and usage remains (PROTOCOL.md).
EXPLORATORY = {
    "RED-klein": "{request}\n\nImagine it is a month from now and this change has failed. "
    "Before planning, list why it failed.\n\n" + CONTRACT,
}


def trials(replicates: int, conditions: dict | None = None) -> list[dict]:
    """Return every trial in the seeded order.

    Parameters
    ----------
    replicates : int
        Replicates per task, model and condition.
    conditions : dict, optional
        Conditions to run; the confirmatory two by default.

    Returns
    -------
    list of dict
        Trials with ids ``t001``... in run order.
    """
    tasks = json.loads((HERE / "tasks.json").read_text())["tasks"]
    conditions = conditions or CONDITIONS
    cells = [
        {"task": t["id"], "model": m, "condition": c, "rep": r}
        for t in tasks
        for m in MODELS
        for c in conditions
        for r in range(1, replicates + 1)
    ]
    random.Random(SEED).shuffle(cells)
    return [{"trial": f"t{i:03d}", **cell} for i, cell in enumerate(cells, 1)]


def settings_file(condition: str) -> Path:
    """Write and return the settings file that turns plugins on or off for a condition.

    Parameters
    ----------
    condition : str
        Condition name.

    Returns
    -------
    Path
        A JSON settings file passed with ``--settings``.
    """
    enabled = {p: False for p in SYNCED_OFF}
    enabled[PLUGIN_ID] = False  # no plugin in study 2
    path = SCRATCH / f"settings-{condition}.json"
    path.write_text(json.dumps({"enabledPlugins": enabled}))
    return path


def redact(text: str, work: Path) -> str:
    """Replace machine-specific paths in a raw envelope.

    Parameters
    ----------
    text : str
        Raw stream-json text.
    work : Path
        The trial's working folder.

    Returns
    -------
    str
        Text with the working folder, scratch and configuration paths replaced by markers.
    """
    for path, mark in ((work, "<repo>"), (SCRATCH, "<scratch>"), (CONFIG, "<config>")):
        text = text.replace(str(path), mark)
    text = re.sub(r"/private/tmp/claude-\d+/[^\"\s\\]*", "<tmp>", text)
    text = re.sub(r"-?Users-[A-Za-z0-9._]+[^\"\s/\\]*", "<home>", text)
    return re.sub(r"/Users/[A-Za-z0-9._-]+", "<home>", text)


def run_trial(trial: dict, task: dict, out: Path) -> dict:
    """Run one trial and return its record.

    Parameters
    ----------
    trial : dict
        Trial id, task, condition and replicate.
    task : dict
        The task entry of ``tasks.json``.
    out : Path
        Folder for envelopes and answers.

    Returns
    -------
    dict
        The trial record (also appended to ``trials.jsonl``).
    """
    work = SCRATCH / "work" / trial["trial"]
    mirror = SCRATCH / "repos" / task["repo"].rsplit("/", 1)[1]
    subprocess.run(["git", "clone", "-q", str(mirror), str(work)], check=True)
    subprocess.run(["git", "-C", str(work), "checkout", "-q", task["commit"]], check=True)
    prompt = {**CONDITIONS, **EXPLORATORY}[trial["condition"]].format(request=task["request"])
    cmd = [
        "claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
        "--model", trial["model"], "--permission-mode", "plan", "--max-turns", str(MAX_TURNS),
        "--settings", str(settings_file(trial["condition"])),
    ]  # fmt: skip
    # a clean room: drop every CLAUDE*/ANTHROPIC* variable inherited from the calling session,
    # so effort, subagent model and session links are Claude Code defaults
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC"))}
    env["CLAUDE_CONFIG_DIR"] = str(CONFIG)
    start = time.time()
    proc = subprocess.run(
        cmd, cwd=work, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL
    )
    seconds = round(time.time() - start, 1)
    events = []
    for line in proc.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    results = [e for e in events if e.get("type") == "result"]
    last = results[-1] if results else {}
    answer = last.get("result") or ""
    raw = redact(proc.stdout, work)
    (out / "envelopes").mkdir(parents=True, exist_ok=True)
    (out / "answers").mkdir(parents=True, exist_ok=True)
    env_path = out / "envelopes" / f"{trial['trial']}.jsonl.gz"
    env_path.write_bytes(gzip.compress(raw.encode(), mtime=0))
    (out / "answers" / f"{trial['trial']}.md").write_text(answer, encoding="utf-8")
    changed = subprocess.run(
        ["git", "-C", str(work), "status", "--porcelain"], capture_output=True, text=True
    ).stdout.strip()
    usage = last.get("usage") or {}
    record = {
        **trial,
        "exit_code": proc.returncode,
        "is_error": last.get("is_error"),
        "subtype": last.get("subtype"),
        "result_events": len(results),
        "num_turns": last.get("num_turns"),
        "seconds": seconds,
        "models": sorted((last.get("modelUsage") or {}).keys()),
        "init_model": init.get("model"),
        "asp_loaded": any("shadow" in s for s in init.get("slash_commands", [])),
        "plugins": sorted(p.get("name", "") for p in init.get("plugins", [])),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "cache_read_tokens": usage.get("cache_read_input_tokens"),
        "project_files_changed": len(changed.splitlines()) if changed else 0,
        "answer_sha256": hashlib.sha256(answer.encode()).hexdigest(),
        "envelope_sha256": hashlib.sha256(env_path.read_bytes()).hexdigest(),
        "stderr_tail": proc.stderr[-300:],
    }
    with (out / "trials.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def main() -> None:
    """Parse arguments and run the chosen command."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["plan", "go"])
    ap.add_argument("--exploratory", action="store_true")
    ap.add_argument("--replicates", type=int, default=5)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--only", default="")
    ap.add_argument("--pilot", action="store_true")
    args = ap.parse_args()
    order = trials(args.replicates, EXPLORATORY if args.exploratory else None)
    if args.exploratory:  # PROTOCOL.md: Opus 5.5 only, replicates as passed (2)
        order = [t for t in order if t["model"] == "claude-opus-5-5"]
    if args.command == "plan":
        print("\n".join(json.dumps(t) for t in order))
        return
    tasks = {t["id"]: t for t in json.loads((HERE / "tasks.json").read_text())["tasks"]}
    out = HERE / ("pilot" if args.pilot else "exploratory" if args.exploratory else "runs")
    done = set()
    if (out / "trials.jsonl").exists():
        done = {json.loads(ln)["trial"] for ln in (out / "trials.jsonl").read_text().splitlines()}
    todo = [t for t in order if t["trial"] not in done]
    if args.only:
        todo = [t for t in todo if t["trial"] in args.only.split(",")]
    with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_trial, t, tasks[t["task"]], out): t for t in todo}
        for fut in cf.as_completed(futures):
            rec = fut.result()
            print(
                rec["trial"], rec["task"], rec["model"], rec["condition"], rec["subtype"],
                rec["num_turns"], rec["seconds"], "s", flush=True,
            )  # fmt: skip
            if rec["is_error"] and "limit" in json.dumps(rec).lower():
                print("usage limit reached: stopping", flush=True)
                pool.shutdown(cancel_futures=True)
                break


if __name__ == "__main__":
    main()
