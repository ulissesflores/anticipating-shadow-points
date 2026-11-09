# Native Execution Kernel — Phase 9 Default

> The default Phase 9 path: an in-session worker/evaluator pattern the user can watch step by step.
>
> The `claude -p /goal` child session (see `claude-p-goal-runner.md`) runs only when the user passes `--goal`.

## 1. Worker loop (pseudocode)

```
T_START = bash:date +%s
turn = 0
fal_consecutive = 0

while TaskList.has_pending_unblocked():
    task = TaskList.next_unblocked()
    TaskUpdate(task, status="in_progress")
    turn += 1

    # Hard stops
    if turn > HARD_STOP.turn_cap: halt("turn cap reached")
    if (date +%s) - T_START > HARD_STOP.time_cap: halt("time cap reached")
    if fal_consecutive >= 3: halt("3 consecutive falsifications, no progress")

    # Verify PRECONDITION
    if not eval(task.PRECONDITION): halt(f"PRECONDITION failed: {task}")

    # Execute ACTION (Write/Edit/Bash/Agent dispatch — whatever the task requires)
    execute(task.ACTION)

    # Verify POSTCONDITION via ACCEPTANCE-TEST
    acc_result = bash(task.ACCEPTANCE_TEST)
    if acc_result matches expected:
        write_evidence(task, acc_result)   # tests/evidence/<slug>.md
        TaskUpdate(task, status="completed")
        fal_consecutive = 0
    else:
        fal_result = bash(task.FALSIFICATION_TEST)
        if fal_result matches failure_pattern:
            halt(f"FALSIFICATION fired on {task}")
        fal_consecutive += 1
        # task stays in_progress; re-enter ASP at appropriate phase if persistent

    # Checkpoint logic — when to dispatch evaluator
    if should_checkpoint(turn, task):
        verdict = dispatch_evaluator()
        if verdict == HALT:
            halt(verdict.reason)
```

## 2. Evaluator subagent prompt template

Dispatched via `Agent` tool with `subagent_type: general-purpose` and a fresh prompt (no transcript from worker). Template:

```
You are an INDEPENDENT EVALUATOR for an ASP-driven execution. You have NO context from the worker — only the artifacts below. Decide CONTINUE or HALT.

ARTIFACTS:
- Deliverables Register state: <paste current table>
- Recent TaskList transitions (last N): <paste>
- Iron Laws (must not be violated): <paste 12 laws from SKILL.md>
- Project Charter (for context only): <paste>

YOUR JOB:
1. Check each Iron Law against TaskList state. Any violation -> HALT.
2. Check Deliverables Register: any deliverable marked `aceito` without evidence path -> HALT.
3. Check for hidden FALSIFICATION patterns the worker may have rationalized past.
4. Output: CONTINUE / HALT (with specific reason).

Return STRICTLY one of:
{ "verdict": "CONTINUE" }
OR
{ "verdict": "HALT", "reason": "<specific Iron Law violated or anomaly>" }
```

## 3. Checkpoint cadence rules (by depth flag)

| Flag | Trigger | Cost |
|---|---|---|
| `--quick` | No evaluator dispatched. Worker self-checks Iron Laws heuristically. | 1× |
| `--standard` (default) | Evaluator at every Deliverable boundary (status `entregue` transition) | 3× |
| `--paranoid` | Evaluator every N=3 tasks + `advisor()` at every Deliverable boundary | 6×+ |

## 4. Evidence file format

Each ACCEPTANCE-TEST capture writes a markdown file at `tests/evidence/<task-subject-slug>.md`:

```markdown
# Evidence — <Task Subject>

- Task ID: <#>
- Deliverable: <D-ID>
- ACTION timestamp: <ISO 8601>
- POSTCONDITION verified at: <ISO 8601>
- ACCEPTANCE-TEST command: `<cmd>`
- ACCEPTANCE-TEST output:
  ```
  <captured stdout/stderr>
  ```
- Pass/Fail: PASS
- Falsification check: <result of FALSIFICATION-TEST, if run>
```

These files are durable evidence the project-close audit can inspect.

## 5. When to use this kernel vs the `claude -p /goal` runner

| Situation | Use this kernel? |
|---|---|
| No `--goal` flag | Yes — the default |
| User passed `--goal` | No — use `claude-p-goal-runner.md` (subprocess) |
| `claude` binary missing | Yes — graceful degradation |
| Inside `ASP_IN_GOAL=1` child | NEITHER — refuse via Iron Law 9 |

## Why this kernel exists at all

The `claude -p /goal` runner depends on:
- `claude` CLI in `$PATH`
- Claude Code 2.1.139+
- jq for JSON parsing
- A writable runtime root (see Runtime directory in `SKILL.md`)
- Background process support (run_in_background)

When any of these fails, this in-session native kernel provides a graceful fallback that does the same worker/evaluator separation, just inside the same Claude session instead of a child subprocess. Iron Law 8 (no Phase 9 without evaluator checkpoints) is enforced in both paths.
