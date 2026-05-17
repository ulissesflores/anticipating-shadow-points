# `claude -p /goal` Runner — Empirical Probe Report

> Pre-flight probe for Phase 9 v5 primary execution kernel. Documents empirical evidence that `/goal` is invocable via `claude -p` subprocess, including critical findings that shape the runner design.

## Probe metadata

- **Date**: 2026-05-17
- **Operator**: ulissesflores
- **Claude Code version**: 2.1.143
- **Host**: macOS (Ulissess-MacBook-Pro.local)
- **Working dirs tested**: `~/sandbox/`, `~/sandbox/claude_cli_tests/<TS>/`

---

## 1. Initial smoke tests (2 quick)

### Test 1 — Basic /goal invocation

```bash
~/sandbox ❯ echo '/goal "test"' | claude -p
Test successful — `test` echoed back. Goal condition met.    (11s)
```

**Result**: ✅ `/goal` is parsed as first piped input. Child exited with success.

### Test 2 — bypassPermissions + autonomous file ops

```bash
~/sandbox ❯ echo '/goal "test"' | claude -p --permission-mode bypassPermissions
Goal "test" satisfied: created `test.py` with three assertions on an `add` function and ran it — output `OK: all tests passed`.    (31s)
```

**Result**: ✅ Child created file + ran tests autonomously. No interactive prompts. Output is a structured summary.

---

## 2. Full battery 2026-05-17 (4 tests A/B/C/D)

Ran `test_claude_cli.sh` with `--max-budget-usd 0.50 --max-turns 5`. Total cost: ~$0.46. Total time: 2m35s.

### Test A — Background + tail (compatibility with `run_in_background` + Monitor)

```
PID: 20443  |  Duração: 110s  |  Exit: 0
Resultado: ✅ compatível com run_in_background + Monitor
```

Verbatim final JSON had `total_cost_usd: 0.33983575`, `num_turns: 7`, `terminal_reason: completed`.

**Implication**: Parent can spawn `claude -p` with `&` and use Monitor to watch for completion. JSON output is rich and parseable.

### Test B — Write outside CWD

```
CWD: ~/sandbox  |  Target: /tmp/claude_outside_<TS>.txt
Exit: 0  |  Criado: sim  |  Conteúdo: sentinel_test_OK
Resultado: ✅ child escreve fora do CWD — bus file-based viável
```

**Implication**: File-based contract via `~/Developer/ASP/runtime/<session>/` works WITHOUT `--add-dir`. No special flags needed.

### Test C — Exit code on impossible goal (🚨 CRITICAL FINDING)

**Prompt given to child**: "Implemente, teste e faça deploy de sistema PCI-DSS completo em UMA turn sem usar tools."

**Child's response** (refused gracefully):

> "Não vou fazer isso. Algumas razões concretas:
> - **Impossibilidade técnica.** 'Sem usar tools' significa não escrever arquivo, não rodar teste, não fazer deploy...
> - **PCI-DSS não cabe em uma turn.** É um framework com 12 requisitos, ~300 controles...
> - **Conflito com instruções globais.** Seu `CLAUDE.md` exige `recall.py` antes de ações não-triviais..."

**Exit code**: `0` ✅
**`is_error`**: `false`
**`terminal_reason`**: `end_turn` (NOT a failure marker)
**`stop_reason`**: `end_turn`

**Resultado**: ⚠️ `$? = 0` mesmo quando o child REFUSED the task.

**Critical finding** — This is the most important discovery from the battery: **Claude returns exit code 0 even when it gracefully refuses to do the goal**. The exit code only signals process-level success of the CLI binary, NOT semantic success of the agent's task.

**Consequence for the runner**: ALL error/success routing decisions MUST parse the JSON output (`is_error`, `terminal_reason`, `stop_reason`, content of `result`). `$?` is NOT a reliable signal.

This drives Iron Laws 11 and 12 in SKILL.md.

### Test D — stream-json output

```
Exit: 0  |  Eventos NDJSON: 13
Tipos: assistant, direct, message, rate_limit_event, result, system, text, thinking, tool_result, tool_use, user
Resultado: ✅ streaming funcional
```

**Implication**: `--output-format stream-json --verbose` emits rich turn-by-turn events. Suitable for Monitor in `--paranoid` mode to surface progress as the child runs.

---

## 3. Critical finding C — detailed analysis

The graceful-refusal-with-exit-0 behavior breaks the naive intuition that "$? = 0 means it worked". It does NOT.

**Wrong** (will misroute in production):

```bash
claude -p "do something" || handle_error
```

**Right** (parse JSON):

```bash
RESULT="$(claude -p "do something" --output-format json)"
IS_ERR="$(echo "$RESULT" | jq -r '.is_error // false')"
STOP="$(echo "$RESULT" | jq -r '.terminal_reason // .stop_reason')"

if [[ "$IS_ERR" == "true" ]]; then
    handle_actual_error
elif [[ "$STOP" != "end_turn" && "$STOP" != "completed" ]]; then
    handle_partial_or_capped
fi
```

---

## 4. jq-based status parsing — canonical recipe

Use this exact pattern in the runner:

```bash
RESULT="$(cat "$RUNTIME_DIR/exec.json")"
IS_ERR="$(echo "$RESULT" | jq -r '.is_error // false')"
STOP="$(echo "$RESULT" | jq -r '.terminal_reason // .stop_reason // "unknown"')"
COST="$(echo "$RESULT" | jq -r '.total_cost_usd // 0')"
NUM_TURNS="$(echo "$RESULT" | jq -r '.num_turns // 0')"
FINAL_TEXT="$(echo "$RESULT" | jq -r '.result // ""')"
```

## 5. Decision matrix per `terminal_reason`

| `terminal_reason` value | Meaning | Parent action |
|---|---|---|
| `end_turn` | Child finished and emitted final result | Reconcile state, proceed normally |
| `completed` | Same as end_turn (some versions emit this label) | Same as above |
| `max_turns_exceeded` | Hit `--max-turns` cap before completing goal | Inspect `final_text`; decide to re-spawn with more turns OR escalate |
| `max_budget_exceeded` | Hit `--max-budget-usd` cap | Escalate to user — budget decision required |
| `error` | Process-level error (network, API, etc.) | Inspect `err.log`; retry with backoff |
| (unknown / null) | Unexpected | Surface to user; do not auto-proceed |

Plus: if the child's `final_text` is a polite refusal (heuristic: contains "won't do", "não vou", "I can't" + reasoning), treat as `refused` even if `terminal_reason: end_turn`. Parent should route to user for clarification, not assume success.

## 6. Bonus observation (meta-cognitive output quality)

Test A's prompt was a generic "deep analysis of current directory". The child produced a 1500-word structured report with Mermaid diagram that included a meta-cognitive observation: *"this report is itself the product of TEST A"*. This is a side-finding worth noting:

- `claude -p` for "analysis" tasks is high-quality and structured.
- Output can be captured as project documentation directly.
- Meta-cognition is preserved across the subprocess boundary.

For ASP: consider using `claude -p` as a way to generate auto-documentation of an ASP run as a separate artifact.

---

## 7. Conclusions

| Question | Answer | Source |
|---|---|---|
| Can the skill invoke `/goal` via `claude -p`? | YES, empirically confirmed | Test 1, Test 2, Test A |
| Does autonomous mode work with `bypassPermissions`? | YES | Test 2, Test A |
| Does file-based coordination work (write outside CWD)? | YES, without `--add-dir` | Test B |
| Is `$?` reliable for error routing? | NO — must parse JSON | Test C |
| Are stream-json events useful for progress monitoring? | YES, 13 event types | Test D |
| Is the runner viable as primary Phase 9 kernel? | YES | All tests |

**Verdict**: `claude -p /goal` is the right Phase 9 primary kernel. Iron Laws 11 and 12 are mandatory to use it safely.

## 8. Files generated by this probe

- `~/sandbox/claude_cli_tests/20260517_003729/REPORT.md` — full battery output
- `~/sandbox/claude_cli_tests/20260517_003729/A_background.log` — JSON output from Test A
- `~/sandbox/claude_cli_tests/20260517_003729/B_outside.log`
- `~/sandbox/claude_cli_tests/20260517_003729/C_impossible.log`
- `~/sandbox/claude_cli_tests/20260517_003729/D_stream.log`

These are the durable empirical evidence backing the v5 architecture.
