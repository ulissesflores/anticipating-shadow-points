"""Live viewer for a ``claude -p --output-format stream-json --verbose`` run, sized for a demo GIF.

It reads the event stream on stdin while the run happens and prints one short line per action
(each file read, search, subagent, task), with a running clock, then the reply's shadow points
in large type. It changes nothing in the run: every event is also written untouched to the
file named by ``ASP_VIEW_LOG``, the full reply to ``ASP_VIEW_RESULT``, and the start and end
times of the run to ``ASP_VIEW_TIMES``.

Usage::

    claude -p "$(cat task.txt)" --output-format stream-json --verbose | python3 asp_view.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

WIDTH = 78
DIM, BOLD, AMBER, CYAN, GREEN, RESET = (
    "\033[2m",
    "\033[1m",
    "\033[38;5;214m",
    "\033[36m",
    "\033[32m",
    "\033[0m",
)
START = time.time()


def clock() -> str:
    """Return the time since the run started, as ``[mm:ss]``.

    Returns
    -------
    str
        The dimmed clock.
    """
    m, s = divmod(int(time.time() - START), 60)
    return f"{DIM}[{m:02d}:{s:02d}]{RESET}"


def short(text: str, room: int) -> str:
    """Return ``text`` on one line, cut to ``room`` characters.

    Parameters
    ----------
    text : str
        Any text.
    room : int
        Maximum length.

    Returns
    -------
    str
        The shortened text.
    """
    text = " ".join(str(text).split())
    return text if len(text) <= room else text[: room - 1] + "…"


def describe(name: str, args: dict) -> tuple[str, str]:
    """Return a verb and a target for one tool call.

    Parameters
    ----------
    name : str
        Tool name.
    args : dict
        Tool input.

    Returns
    -------
    tuple of str
        ``(verb, target)``.
    """
    path = args.get("file_path") or args.get("path") or ""
    inside = str(args.get("file_path", "")).startswith(os.getcwd())
    path = re.sub(r"^.*?full-stack-fastapi-template/", "", path)
    table = {
        "Read": ("read", path),
        "Grep": ("search", f"{args.get('pattern', '')}  {path}".strip()),
        "Glob": ("list", args.get("pattern", "")),
        "Task": ("subagent", args.get("description") or args.get("subagent_type", "")),
        "Agent": ("subagent", args.get("description") or args.get("subagent_type", "")),
        "Bash": ("shell", args.get("command", "")),
        "Skill": ("skill", args.get("skill") or args.get("command", "")),
        "Write": ("write", path if inside else "plan file (plan mode)"),
        "Edit": ("edit", path if inside else "plan file (plan mode)"),
        "TaskCreate": ("task", args.get("subject", "")),
        "TodoWrite": ("plan", f"{len(args.get('todos', []))} tasks"),
        "WebSearch": ("web", args.get("query", "")),
        "WebFetch": ("fetch", args.get("url", "")),
    }
    verb, target = table.get(name, (name.lower(), short(json.dumps(args), 40)))
    return verb, tidy(str(target))


def tidy(text: str) -> str:
    """Drop the absolute path of the demo folder from ``text``.

    Parameters
    ----------
    text : str
        A command or a path.

    Returns
    -------
    str
        The text with paths relative to the project.
    """
    text = re.sub(r"\S*full-stack-fastapi-template/?", "", text).replace(os.getcwd(), ".")
    if home := os.environ.get("CLAUDE_CONFIG_DIR"):
        text = text.replace(home, "$CLAUDE_CONFIG_DIR")
    return re.sub(r"\s*2>\s*/dev/null", "", text)


def shell_steps(command: str) -> list[tuple[str, str]]:
    """Split a shell command into the reads, searches and listings it performs.

    Parameters
    ----------
    command : str
        The command the agent ran.

    Returns
    -------
    list of tuple of str
        ``(verb, target)`` pairs, in order; other steps are left out.
    """
    steps = []
    for part in re.split(r"\s*(?:;|&&|\|\||\|)\s*", tidy(command)):
        words = part.split()
        if not words:
            continue
        head, rest = words[0], [w for w in words[1:] if not w.startswith("-")]
        if head in ("cat", "head", "tail") and rest:
            steps += [("read", w) for w in rest if "/" in w or "." in w]
        elif head == "sed" and len(rest) > 1:
            steps.append(("read", rest[-1]))
        elif head in ("grep", "rg") and rest:
            steps.append(("search", " ".join(rest)[:60]))
        elif head in ("ls", "find") and rest:
            steps.append(("list", " ".join(rest)))
    return steps


def show_result(text: str) -> None:
    """Print the shadow points, the validator verdict and the riskiest point of the reply.

    Parameters
    ----------
    text : str
        The final reply.
    """
    rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in text.splitlines()
        if re.match(r"^\|\s*\d+\s*\|", line)
    ]
    print(f"\n{BOLD}{AMBER}━━ ASP result ━━  {len(rows)} shadow points, before any code{RESET}\n")
    for row in rows[:10]:
        print(f"  {AMBER}{BOLD}{row[0]:>2}{RESET}  {short(row[1].replace('`', ''), WIDTH - 6)}")
    if len(rows) > 10:
        print(f"  {DIM}… {len(rows) - 10} more in the full reply{RESET}")
    for label in ("Validator", "Riskiest"):
        line = next((ln for ln in text.splitlines() if ln.lstrip("*").startswith(label)), "")
        if line:
            body = re.sub(r"[*`#]", "", line).strip()
            print(
                f"\n{BOLD}{GREEN if label == 'Validator' else AMBER}{short(body, WIDTH * 2)}{RESET}"
            )


def main() -> None:
    """Read the event stream from stdin and print the live view."""
    log = Path(os.environ.get("ASP_VIEW_LOG", os.devnull)).open("w", encoding="utf-8")
    result_path = os.environ.get("ASP_VIEW_RESULT")
    seen = edits = 0
    agents: set[str] = set()
    for raw in sys.stdin:
        log.write(raw)
        log.flush()
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        if kind == "system" and event.get("subtype") == "init":
            print(
                f"{clock()} {CYAN}session{RESET}  {event.get('model', '')}  ·  plan mode, read-only"
            )
        elif kind == "assistant":
            nested = event.get("parent_tool_use_id") is not None
            lead = f"{DIM}  ↳{RESET} " if nested else f"{AMBER}▸{RESET} "
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "text" and not nested and block.get("text", "").strip():
                    first = block["text"].strip().splitlines()[0]
                    print(
                        f"{clock()} {DIM}“{short(re.sub(r'[*#`]', '', first), WIDTH - 12)}”{RESET}"
                    )
                if block.get("type") != "tool_use":
                    continue
                name, args = block.get("name", ""), block.get("input") or {}
                seen += 1
                target_file = str(args.get("file_path", ""))
                edits += name in ("Write", "Edit", "NotebookEdit") and target_file.startswith(
                    os.getcwd()
                )
                if name in ("Agent", "Task"):
                    agents.add(block.get("id"))
                steps = shell_steps(args.get("command", "")) if name == "Bash" else []
                for verb, target in steps or [describe(name, args)]:
                    colour = CYAN if verb in ("subagent", "skill") else ""
                    print(f"{clock()} {lead}{colour}{verb:<9}{RESET}{short(target, WIDTH - 22)}")
                    sys.stdout.flush()
                    time.sleep(0.15)  # one line at a time, so a burst stays readable
        elif kind == "user":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_result" and block.get("tool_use_id") in agents:
                    body = json.dumps(block.get("content"))
                    verdict = next((v for v in ("REVISE", "APPROVE") if v in body), "returned")
                    print(f"{clock()} {GREEN}{BOLD}validator → {verdict}{RESET}", flush=True)
        elif kind == "result":
            text = event.get("result") or ""
            if result_path:
                Path(result_path).write_text(text, encoding="utf-8")
            if times := os.environ.get(
                "ASP_VIEW_TIMES"
            ):  # lets the GIF edit find the wait to speed up
                Path(times).write_text(json.dumps({"start": START, "result": time.time()}))
            m, s = divmod(int(time.time() - START), 60)
            print(
                f"\n{clock()} {GREEN}done{RESET}  {seen} actions in {m} min {s:02d} s"
                f" · project files edited: {edits}"
            )
            show_result(text)
            sys.stdout.flush()


if __name__ == "__main__":
    main()
