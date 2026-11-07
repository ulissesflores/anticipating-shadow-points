# Iron Law 11, from recorded evidence: a refusal that exits 0 with no envelope flag.
# Replays trial C.05 of the 2026-07-08 run (data/spike-2026-07-08/trials.jsonl). No model calls.
Output assets/demo/exit-code.gif
Source assets/demo/_common.tape
Hide
Type "clear" Enter
Show
Type "# Recorded 2026-07-08, Claude Code 2.1.200, scenario C.05 (safety). Replayed, not live." Enter
Sleep 500ms
Type `jq -r 'select(.scenario_id=="C.05") | "exit_code=\(.exit_code)  stop_reason=\(.stop_reason)  is_error=\(.is_error)"' data/spike-2026-07-08/trials.jsonl` Enter
Sleep 2s
Type `jq -r 'select(.scenario_id=="C.05") | .result_text' data/spike-2026-07-08/trials.jsonl | head -3` Enter
Sleep 3s
Type "# A wrapper that trusts $? reads this refusal as success. Count them:" Enter
Type `jq -s '[.[] | select(.exit_code==0)] | length' data/spike-2026-07-08/trials.jsonl` Enter
Sleep 1500ms
Type `jq -r '.iron_law_11.july_2026 | "author \(.author_silent_refusals.k)/50, codebook \(.codebook_silent_refusals.k)/50, detector \(.detector_silent_refusals.k)/50"' output/results.json` Enter
Sleep 4s
