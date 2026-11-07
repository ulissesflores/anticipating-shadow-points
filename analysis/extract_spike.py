"""Extract a publishable, redacted record of the 2026-07-08 `claude -p` spike.

The raw envelopes of the spike live outside the repository because the CLI's
``system/init`` event records machine-local state (working directory, memory
paths, installed plugins, MCP server names). This one-off script keeps only
the fields the analysis needs and records the SHA-256 of every raw file, so the
published extract can be tied back to the private originals without exposing
them.

It is not part of ``run_all.py``: the raw input is not public. Its output,
``data/spike-2026-07-08/trials.jsonl``, is committed and hash-sealed.

Usage
-----
``python analysis/extract_spike.py <raw-spike-dir>``
where ``<raw-spike-dir>`` holds ``results.tsv`` and ``trials/<sid>.{json,err}``.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "spike-2026-07-08" / "trials.jsonl"
CATEGORY = {"A": "impossible", "B": "capability", "C": "safety", "D": "ambiguity"}
# Personal identifiers that leaked into two replies; replaced, never paraphrased.
REDACTIONS = (
    (re.compile(r"/private/tmp/claude-\d+/[^\s`]+"), "<redacted-local-path>"),
    (re.compile(r"[\w.+-]+@gmail\.com"), "<redacted-email>"),
)


def redact(text: str) -> tuple[str, int]:
    """Replace personal identifiers in a reply.

    Parameters
    ----------
    text : str
        Reply text as returned by the CLI.

    Returns
    -------
    tuple of (str, int)
        Redacted text and the number of replacements made.
    """
    total = 0
    for pattern, token in REDACTIONS:
        text, n = pattern.subn(token, text)
        total += n
    return text, total


def sha256(path: Path) -> str:
    """Return the hex SHA-256 of a file.

    Parameters
    ----------
    path : Path
        File to hash.

    Returns
    -------
    str
        Lower-case hex digest.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(raw: Path) -> list[dict]:
    """Build one redacted record per trial.

    Parameters
    ----------
    raw : Path
        Directory with ``results.tsv`` and ``trials/``.

    Returns
    -------
    list of dict
        Records sorted by scenario id.
    """
    with (raw / "results.tsv").open(encoding="utf-8") as fh:
        exits = {row["sid"]: int(row["exit"]) for row in csv.DictReader(fh, delimiter="\t")}
    records = []
    for sid in sorted(exits):
        env_path = raw / "trials" / f"{sid}.json"
        err_path = raw / "trials" / f"{sid}.err"
        events = json.loads(env_path.read_text(encoding="utf-8"))
        init = next(e for e in events if e.get("type") == "system" and e.get("subtype") == "init")
        result = [e for e in events if e.get("type") == "result"][-1]
        text, n_redacted = redact(result.get("result") or "")
        records.append(
            {
                "scenario_id": sid,
                "category": CATEGORY[sid[0]],
                "exit_code": exits[sid],
                "claude_code_version": init.get("claude_code_version"),
                "session_model": init.get("model"),
                "answering_models": sorted(result.get("modelUsage", {})),
                "permission_mode": init.get("permissionMode"),
                "subtype": result.get("subtype"),
                "is_error": result.get("is_error"),
                "stop_reason": result.get("stop_reason"),
                "terminal_reason": result.get("terminal_reason"),
                "num_turns": result.get("num_turns"),
                "permission_denials": len(result.get("permission_denials") or []),
                "total_cost_usd": result.get("total_cost_usd"),
                "result_text": text,
                "redactions": n_redacted,
                "raw_envelope_sha256": sha256(env_path),
                "raw_stderr_sha256": sha256(err_path),
            }
        )
    return records


def main() -> None:
    """Write the redacted extract to ``data/spike-2026-07-08/trials.jsonl``."""
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    records = extract(Path(sys.argv[1]))
    with OUT.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"wrote {len(records)} records -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
