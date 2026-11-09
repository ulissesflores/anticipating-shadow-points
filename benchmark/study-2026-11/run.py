"""Run the 2026-11 study: three conditions on six pinned repositories, in a seeded order.

Each trial clones the task's repository at its pinned commit into a fresh folder, runs one
``claude -p`` session in plan mode, keeps the full ``stream-json`` envelope, and records the final
reply. Conditions differ only in the prompt prefix and in whether the ASP plugin is enabled;
model, turn cap, permission mode, output contract and configuration folder are the same.

Usage::

    python run.py check                  # installed plugin bytes vs repository bytes
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
MODEL = "claude-opus-5-5"
MAX_TURNS = 60
SEED = "asp-bench-2026-11"
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
    "GREEN": "/anticipating-shadow-points:asp --standard {request}\n\n"
    "Stop after the validated plan (Phase 6).\n\n" + CONTRACT,
}


def skill_hash(folder: Path) -> str:
    """Return one SHA-256 over the files the skill loads in Phases 0-6.

    Parameters
    ----------
    folder : Path
        A plugin folder (the repository's or an installed copy).

    Returns
    -------
    str
        Hash of the sorted ``path  sha256`` lines of ``skills/`` and ``commands/``.
    """
    lines = []
    for sub in ("skills/anticipating-shadow-points", "commands"):
        for f in sorted((folder / sub).rglob("*")):
            if f.is_file() and f.name != ".DS_Store":
                rel = f.relative_to(folder).as_posix()
                lines.append(f"{rel}  {hashlib.sha256(f.read_bytes()).hexdigest()}")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def installed_folder() -> Path:
    """Return the installed plugin folder inside the study's configuration folder.

    Returns
    -------
    Path
        The ``installPath`` recorded by Claude Code.
    """
    data = json.loads((CONFIG / "plugins" / "installed_plugins.json").read_text())
    return Path(data["plugins"][PLUGIN_ID][0]["installPath"])


def trials(replicates: int) -> list[dict]:
    """Return every trial in the seeded order.

    Parameters
    ----------
    replicates : int
        Replicates per task and condition.

    Returns
    -------
    list of dict
        Trials with ids ``t001``... in run order.
    """
    tasks = json.loads((HERE / "tasks.json").read_text())["tasks"]
    cells = [
        {"task": t["id"], "condition": c, "rep": r}
        for t in tasks
        for c in CONDITIONS
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
    enabled[PLUGIN_ID] = condition == "GREEN"
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
    prompt = CONDITIONS[trial["condition"]].format(request=task["request"])
    cmd = [
        "claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
        "--model", MODEL, "--permission-mode", "plan", "--max-turns", str(MAX_TURNS),
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
    ap.add_argument("command", choices=["check", "plan", "go"])
    ap.add_argument("--replicates", type=int, default=5)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--only", default="")
    ap.add_argument("--pilot", action="store_true")
    args = ap.parse_args()
    if args.command == "check":
        repo = skill_hash(ROOT / "plugins" / "anticipating-shadow-points")
        inst = skill_hash(installed_folder())
        print(json.dumps({"repository": repo, "installed": inst, "equal": repo == inst}))
        raise SystemExit(0 if repo == inst else 1)
    order = trials(args.replicates)
    if args.command == "plan":
        print("\n".join(json.dumps(t) for t in order))
        return
    tasks = {t["id"]: t for t in json.loads((HERE / "tasks.json").read_text())["tasks"]}
    out = HERE / ("pilot" if args.pilot else "runs")
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
                rec["trial"], rec["task"], rec["condition"], rec["subtype"],
                rec["num_turns"], rec["seconds"], "s", flush=True,
            )  # fmt: skip
            if rec["is_error"] and "limit" in json.dumps(rec).lower():
                print("usage limit reached: stopping", flush=True)
                pool.shutdown(cancel_futures=True)
                break


if __name__ == "__main__":
    main()
