# What ASP changes: the same migration task planned without (RED) and with (GREEN) the skill.
# Replays the committed May 2026 benchmark transcripts for E1. No model calls.
Output assets/demo/asp-plan.gif
Source assets/demo/_common.tape
Set Height 760
Hide
Type "clear" Enter
Type "B=benchmark/runs/published/2026-05-18T00-27-43Z-b0a1bc7b/outputs/E1" Enter
Type "clear" Enter
Show
Type "# Task E1: add a NOT NULL column to a 1M-row table. Recorded May 2026, Opus 4.7." Enter
Sleep 500ms
Type "# RED: senior-engineer plan, no ASP" Enter
Type "head -12 $B/RED.text.txt" Enter
Sleep 4s
Type "clear" Enter
Type "# GREEN: same model with ASP loaded (pre-mortem + MAST 14-mode pass)" Enter
Type "head -24 $B/GREEN.text.txt" Enter
Sleep 6s
Type `jq -r '.benchmark_2026_05 | "deterministic match E1: RED \(.red_coverage.E1*100)% -> GREEN \(.green_coverage.E1*100)%"' output/results.json` Enter
Sleep 4s
