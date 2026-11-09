# How the demo GIF was recorded

`assets/demo/asp-live.gif` is a real run, recorded live on 2026-11-09. Nothing in it is replayed.

## What was run

| | |
|---|---|
| Claude Code | 2.1.319, model `claude-opus-5-5`, `--permission-mode plan` (read-only) |
| Configuration | A fresh `CLAUDE_CONFIG_DIR` where only `/login` had been run: no settings and no `CLAUDE.md`. Plugins synced from the Claude account were present (pdf-viewer and a few others); ASP was not |
| Install | `claude plugin marketplace add ulissesflores/anticipating-shadow-points`, then `claude plugin install anticipating-shadow-points@anticipating-shadow-points`, on screen |
| Project | [`fastapi/full-stack-fastapi-template`](https://github.com/fastapi/full-stack-fastapi-template) at commit `aabb901` (248 files), cloned outside any folder with a `CLAUDE.md` |
| Task | [`run/task.txt`](run/task.txt): soft delete for users, restorable by an admin for 30 days, `--standard` depth, stop after the validated plan |
| Reply | [`run/result.md`](run/result.md), verbatim. Status fields in [`run/run.json`](run/run.json) |

The project was left unchanged: `git status` after the run lists only `task.txt`. In plan mode,
Claude Code keeps its plan in a file inside the configuration folder; the screen shows those
writes as "plan file (plan mode)".

## How the picture was made

1. [`asp-live.tape`](asp-live.tape) drives a terminal with [vhs](https://github.com/charmbracelet/vhs)
   and records it at real speed. The two local paths in it must be edited to rerun.
2. [`asp_view.py`](asp_view.py) reads the run's event stream as it arrives and prints one line per
   file read, search or subagent, then the shadow points of the reply. It changes nothing in the
   run and saves every event untouched.
3. [`make_gif.py`](make_gif.py) speeds up only the wait for the result, by the factor shown in the
   badge (13x here), and shortens frozen frames in the install by at most 4x. Typing and output
   play at real speed.

The card under the GIF (`assets/brand/plan-card-*.svg`) is drawn from `run/result.md` by
`assets/brand/make_brand.py`, so it cannot drift from the reply.

## What this shows and what it does not

It shows ASP installed by a user and working on a real codebase: it read the code, found ten
shadow points tied to specific files, and an independent subagent sent the plan back once before
approving it. It is one run, judged by no one but the reader. It does not measure whether ASP makes
plans better; that benchmark is specified in [`PREREGISTRATION.md`](../../../PREREGISTRATION.md).
A new run gives a new reply.
