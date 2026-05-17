# Goal Spec Template — completion condition

> ASP Phase 8 output (paired with micro-TODO). The rendered output is consumed by **one of three execution paths** in Phase 9:
>
> 1. **Primary (v5)**: `claude -p /goal` child via stdin pipe — see `claude-p-goal-runner.md`. This is the default.
> 2. **Fallback**: evaluator subagent of the native in-session kernel — see `execution-kernel.md`. Used when `--no-claude-p` OR task <5 steps.
> 3. **Alternative**: user typing `/goal "..."` manually in their terminal — opt-in interactive autonomous mode.
>
> Regardless of consumer, the schema below is the same. Focus on completion-condition clarity — the text must be readable enough that ANY evaluator (Anthropic's built-in, our subagent, or the user themselves) can decide done/not-done unambiguously.

## Schema

```
GOAL: <one-line statement: what must be true for this work to be considered done>

EVALUATOR CRITERIA:
  - All TaskList items completed with ACCEPTANCE-TEST evidence
  - All Deliverables in deliverables-register marked `aceito`
  - All Iron Laws respected:
      1. NO IMPLEMENTATION WITHOUT SHADOW-POINT PASS FIRST
      2. NO PLAN APPROVAL WITHOUT INDEPENDENT VALIDATOR PASS
      3. NO MICRO-TODO WITHOUT MACRO PLAN + CHARTER + DELIVERABLES APPROVED
      4. NO STEP COMPLETION WITHOUT FRESH ACCEPTANCE-TEST EVIDENCE
      5. NO DELIVERABLE `aceito` WITHOUT EVIDENCE MATCHED
      6. NO PROJECT CLOSE WITHOUT EXECUTION REPORT + MEMORY WRITE-BACK
      7. NO LOOP WITHOUT CAP

HARD STOP CONDITIONS:
  - turn count > <N>
  - elapsed > <HH:MM>
  - cost > <$X>  (if cost tracking active)
  - 3 consecutive FALSIFICATION-TEST failures with no progress
  - any Iron Law violation detected by evaluator
```

## Example — concrete instance (this very ASP build)

```
GOAL: ASP skill at ~/.claude/skills/anticipating-shadow-points/ exists, loads via Skill tool in fresh session, scripts/verify.sh exits 0 with 16/16 criteria PASS, and advisor() final call returns ship verdict.

EVALUATOR CRITERIA:
  - All 63 emitted TaskCreate items completed with ACCEPTANCE-TEST evidence in tests/
  - All 13 Deliverables (D01-D13) marked `aceito` (D13 may stay pending pending user inspection)
  - 7 Iron Laws respected per task
  - tests/criteria-final-checklist.md shows 16 OK
  - tests/advisor-final.md shows positive verdict

HARD STOP CONDITIONS:
  - turn count > 200
  - elapsed > 06:00
  - 3 consecutive FALSIFICATION-TEST failures with no progress
  - Any task marked `completed` without ACCEPTANCE-TEST evidence path -> halt
```

## Writing rules

1. **GOAL must be one line and testable.** "Make it good" is invalid; "verify.sh exits 0" is valid.
2. **EVALUATOR CRITERIA bullets** are machine-checkable predicates, not opinions.
3. **HARD STOP CONDITIONS** must include at least: turn cap, time cap, and Iron-Law-violation halt.
4. **Cost cap is optional** but recommended for tasks that may run unattended.
5. **The Goal Spec is showed to the user at the same time as the acceptance-contract**, so they know exactly what /goal is going to enforce.
