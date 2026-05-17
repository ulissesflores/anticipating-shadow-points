# Micro-TODO Template — single task

> ASP Phase 8 output. Each `TaskCreate` call emits one task whose `description` field uses this exact schema. This IS the non-violation contract — labels are mandatory.

## Schema

```
PRECONDITION: <invariant that must be true before this step runs>
ACTION: <exact command or literal edit — copy-paste-ready>
POSTCONDITION: <what changed; how the system state differs>
ACCEPTANCE-TEST: <command + expected output; the test that proves POSTCONDITION>
FALSIFICATION-TEST: <command or observation that would prove this step failed>
DEPENDS-ON: <comma-separated task subjects that must be `completed` before this can start>
DELIVERABLE-ID: <D01..Dn from Deliverables Register, or `-` for internal-only step>
```

## Example — concrete instance

```
Subject: Write user-auth handler in /api/auth.ts

Description:
PRECONDITION: file /api/auth.ts does not exist; package.json includes "zod"
ACTION: Write /api/auth.ts with handler exporting POST function that validates email+password via zod schema and returns 401 on invalid, 200 + JWT on valid
POSTCONDITION: /api/auth.ts exists, exports POST, returns expected status codes for two test inputs
ACCEPTANCE-TEST:
  curl -s -X POST localhost:3000/api/auth -d '{"email":"a@b","password":"x"}' -o /dev/null -w "%{http_code}"
  Expected output: 401
FALSIFICATION-TEST:
  ls /api/auth.ts || echo MISSING
  Or: tsc --noEmit /api/auth.ts | grep error
FALSIFICATION trigger: file missing OR typecheck errors
DEPENDS-ON: Install zod dependency, Configure /api routing
DELIVERABLE-ID: D03
```

## Rules

1. **Every field must be present.** Empty field = task rejected at Phase 8 emission.
2. **ACCEPTANCE-TEST must include the expected output**, not just the command. "Run tests" is invalid; "npm test; expected '15 passed, 0 failed'" is valid.
3. **FALSIFICATION-TEST must be different from negation of ACCEPTANCE-TEST.** They probe different failure modes (false-positive vs missed-postcondition).
4. **DEPENDS-ON uses task subjects, not IDs**, so it survives re-numbering. Keep subjects unique.
5. **DELIVERABLE-ID** ties the step to the register — every deliverable should have ≥1 task contributing to it.

## Aggregate gate (Phase 9 entry)

Before invoking `/goal` in Phase 9, confirm:
- All emitted tasks have all 7 fields populated.
- Every `DELIVERABLE-ID` referenced exists in `deliverables-register.md`.
- DEPENDS-ON forms a DAG (no cycles).
- User explicitly accepted the `acceptance-contract.md` text.
