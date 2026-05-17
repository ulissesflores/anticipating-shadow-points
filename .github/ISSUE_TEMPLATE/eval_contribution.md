---
name: Eval contribution
about: Propose a new eval from your domain (e.g., frontend, ML, infra, mobile)
title: "[eval] "
labels: eval
assignees: ulissesflores
---

## Domain

<!-- e.g., "Frontend React migration", "ML pipeline data drift", "Kubernetes operator upgrade", "Mobile app store submission". -->

## Eval input (the task statement)

> <!-- The task that an LLM agent would be asked to plan. Keep it realistic and non-trivial — something that takes >5 micro-steps and has real failure modes. -->

## Expected shadow points (≥8)

<!-- List the failure modes a competent senior engineer would flag during pre-mortem. ≥8 required for the eval to be useful as a baseline. -->

1.
2.
3.
4.
5.
6.
7.
8.

## Acceptance criterion

> The eval passes if `/asp <INPUT>` produces a shadow-point list covering **≥80%** of the expected items above. Synonym/paraphrase matches OK.

## Why this eval matters

<!-- What category of failure does this stress-test? Is it well-covered by existing evals or a gap? -->

## File location

If accepted, this eval would live at:
`skills/anticipating-shadow-points/evals/0X-<short-slug>.md`

(numbered after the existing 5 evals; see `evals/01-supabase-migration.md` for format reference.)

## Verification baseline (optional but valuable)

<!-- If you've already run an agent against this eval input WITHOUT ASP loaded, paste a coverage estimate. This becomes the RED baseline for the GREEN measurement. -->

- Baseline coverage (no skill): ___ / ___ expected items (___%)
- Predicted coverage with ASP: ≥80%

## I'm willing to

- [ ] Submit the eval as a PR (recommended).
- [ ] File this as an issue for someone else to implement.
- [ ] Run the RED/GREEN baseline subagent dispatches and attach results.
