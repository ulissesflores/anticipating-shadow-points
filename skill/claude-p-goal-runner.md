# `claude -p /goal` Runner — Primary Phase 9 Execution

> v5 primary execution kernel. Spawns a child Claude Code session via `claude -p`, pipes `/goal "..."` as first input, captures structured JSON output, reconciles state with parent TaskList.
>
> Empirical validation: 2026-05-17 battery (Claude Code 2.1.143) — see `tests/claude-p-goal-runner-probe.md`.

## 1. Spawn pattern (Bash)

The parent skill (Phase 9 step 1) emits this script template, substituting `$SESSION_ID`, `$GOAL_SPEC_PATH`, `$BUDGET`, `$MAX_TURNS`:

```bash
#!/usr/bin/env bash
set -uo pipefail

# Inputs from parent Phase 8 emission
SESSION_ID="${SESSION_ID:-$(date +%s)-$$}"
RUNTIME_DIR="$HOME/Developer/ASP/runtime/$SESSION_ID"
GOAL_SPEC_PATH="$RUNTIME_DIR/goal-spec.md"
BUDGET="${BUDGET:-2.00}"
MAX_TURNS="${MAX_TURNS:-50}"
OUTPUT_FORMAT="${OUTPUT_FORMAT:-json}"   # json | stream-json

mkdir -p "$RUNTIME_DIR"

# Initial state.json (parent + child share)
cat > "$RUNTIME_DIR/state.json" <<EOF
{
  "session": "$SESSION_ID",
  "status": "spawned",
  "spawned_at": "$(date -Iseconds)",
  "cost_usd_acc": 0.0,
  "current_task_id": null
}
EOF

# Spawn child — Iron Law 9: ASP_IN_GOAL=1 prevents recursive spawn
# IMPORTANT: env var must be on the CLAUDE invocation, not on echo.
# `VAR=1 echo "x" | claude` exports VAR only to echo. The pipe child (claude)
# inherits from the parent shell, not from echo. Confirmed in advisor review.
cd "$RUNTIME_DIR"

# Build the input safely (heredoc avoids shell-escaping pitfalls when
# goal-spec.md contains backticks, $, !, or quotes).
INPUT_FILE="$RUNTIME_DIR/.stdin"
{
  printf '/goal "'
  cat "$GOAL_SPEC_PATH"
  printf '"\n'
} > "$INPUT_FILE"

ASP_IN_GOAL=1 claude -p \
    --permission-mode bypassPermissions \
    --output-format "$OUTPUT_FORMAT" \
    --max-budget-usd "$BUDGET" \
    --max-turns "$MAX_TURNS" \
    < "$INPUT_FILE" \
    > exec.json 2> err.log &

CHILD_PID=$!
echo "$CHILD_PID" > child.pid
echo "[runner] child spawned pid=$CHILD_PID, runtime=$RUNTIME_DIR"
```

Parent uses `run_in_background: true` when invoking this script via Bash, then `Monitor` tool to be notified on exit.

## 2. File-based contract (state.json — parent-side only)

> **Honest correction (post-advisor review)**: the child Claude session only receives `/goal "..."` as its input. It does NOT automatically know about `state.json` and won't write to it unless the Goal Spec text explicitly instructs it to. The simpler, empirically-grounded model is:
>
> - **Parent writes `state.json` once at spawn time** (initial state).
> - **Child writes its work to `exec.json` (stdout JSON) and any task-produced files**.
> - **Parent reconstructs final state from `exec.json` at child exit time**.

`$RUNTIME_DIR/state.json` schema (parent-side bookkeeping, NOT a shared bus):

```json
{
  "session": "<uuid-or-timestamp>",
  "status": "spawned | completed | halted | failed",
  "spawned_at": "<ISO 8601>",
  "completed_at": "<ISO 8601 | null>",
  "cost_usd_acc": <float>,
  "num_turns": <int>,
  "terminal_reason": "<end_turn | max_turns_exceeded | max_budget_exceeded | refused | error | null>",
  "is_error": <bool>,
  "final_text": "<string>"
}
```

Initial state at spawn:

```json
{ "session": "<id>", "status": "spawned", "spawned_at": "<ts>", "cost_usd_acc": 0.0 }
```

Final state is reconstructed by parent from `exec.json` post-exit (see Section 4 reconciliation recipe). If the user wants mid-flight progress, they should use `--paranoid` mode (`stream-json --verbose`) and have parent tail `exec.json` directly — not via `state.json`.

## 3. Monitor integration

Parent flow:

```
spawn script in Bash with run_in_background: true
  → captures PID via stdout
  → Monitor tool watches exec.json size or PID liveness
  → parent goes idle until notification
```

For long-running goals (>10 min), parent can opt to `tail -f exec.json` via Monitor stream mode to surface progress events (only meaningful when `OUTPUT_FORMAT=stream-json`).

## 4. JSON parsing recipe (post-exit reconciliation)

```bash
# Pre-condition: exec.json exists and child has exited (verified via Monitor)
RESULT="$(cat "$RUNTIME_DIR/exec.json")"

# CRITICAL: do NOT use $? to determine semantic success.
# Iron Law 11 — see tests/claude-p-goal-runner-probe.md test C.
IS_ERR="$(echo "$RESULT" | jq -r '.is_error // false')"
STOP="$(echo "$RESULT" | jq -r '.terminal_reason // .stop_reason // "unknown"')"
COST="$(echo "$RESULT" | jq -r '.total_cost_usd // 0')"
NUM_TURNS="$(echo "$RESULT" | jq -r '.num_turns // 0')"
FINAL_TEXT="$(echo "$RESULT" | jq -r '.result // ""')"

# Persist back to state.json
jq --arg s "$STOP" \
   --arg c "$COST" \
   --arg t "$NUM_TURNS" \
   --arg f "$FINAL_TEXT" \
   --argjson e "$IS_ERR" \
   '.status = "completed" |
    .terminal_reason = $s |
    .cost_usd_acc = ($c | tonumber) |
    .num_turns = ($t | tonumber) |
    .final_text = $f |
    .is_error = $e |
    .completed_at = (now | todate)' \
   "$RUNTIME_DIR/state.json" > "$RUNTIME_DIR/state.json.tmp" \
   && mv "$RUNTIME_DIR/state.json.tmp" "$RUNTIME_DIR/state.json"
```

## 5. Reconciliation (parent → TaskList sync)

After parsing `exec.json`, the parent:

1. Inspects `final_text` (the child's narrative summary).
2. Inspects task-produced artifacts: which files were created/modified per the parent's TaskList expectations? This is the source of truth, NOT a child-emitted state.json.
3. For each task whose POSTCONDITION can be verified via filesystem inspection, invokes `TaskUpdate(task, status=completed)` if evidence matches.
4. For tasks where evidence is missing or `final_text` indicates trouble, marks `in_progress` and surfaces to the user.
5. Updates Deliverables Register based on which tasks are now `completed`.
6. Logs `total_cost_usd` and `num_turns` in the Execution Report metrics.

Reconciliation is **filesystem-grounded** (parent verifies artifacts directly), not message-grounded (parent does not trust the child's narrative as the source of task status). This respects Iron Law 4: NO STEP COMPLETION WITHOUT FRESH ACCEPTANCE-TEST EVIDENCE.

## 6. Iron Law 9 enforcement (ASP_IN_GOAL detection)

The skill (when invoked via `/asp` or `Skill` tool) checks at Phase 0a:

```bash
if [[ -n "${ASP_IN_GOAL:-}" ]]; then
  echo "REFUSE: ASP cannot re-enter itself inside a /goal child session."
  echo "Iron Law 9 violation prevented."
  exit 1
fi
```

This prevents infinite recursive Claude session spawn (MAST mode 10).

## 7. `--paranoid` mode: stream-json + Monitor

When the depth flag is `--paranoid`:

- Use `OUTPUT_FORMAT=stream-json` in the spawn script.
- Parent uses Monitor in streaming mode to read each NDJSON line as the child emits.
- For each `type:tool_use` event, parent can opt to dispatch a "checkpoint evaluator" subagent (separate prompt, only the recent events) to audit Iron Laws turn-by-turn.
- `type:result` event marks the final summary.

Cost trade-off: ~2x more IO but real-time visibility into the child's reasoning. Worth it for high-stakes runs.

## Decision matrix (when to use this runner vs native kernel)

| Situation | Runner | Rationale |
|---|---|---|
| Task has ≥5 micro-steps | `claude -p /goal` (this runner) | Spawn overhead amortized; native /goal evaluator handles complex flow |
| Task has <5 micro-steps | Native kernel (`execution-kernel.md`) | Spawn overhead not justified for small work |
| User passed `--no-claude-p` | Native kernel | Explicit user choice |
| User passed `--no-kernel` | Vanilla `executing-plans` skill | Manual step-by-step, no autonomy |
| Inside a child session (ASP_IN_GOAL=1) | NEITHER — refuse with Iron Law 9 | Prevent recursion |
| `claude` binary not in PATH | Native kernel + warn | Graceful degradation |
