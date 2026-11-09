# ASP at work: the pre-mortem of a production migration on a 4-file sample repo.
# Replays the reply recorded on 2026-11-09 (assets/demo/asp-plan/result.md). No model calls.
# Settings are inline: vhs ignores size settings that come after a Source line.
Output assets/demo/asp-plan.gif
Set Shell "bash"
Set FontSize 14
Set Width 1400
Set Height 1000
Set Padding 24
Set Theme "Builtin Light"
Set TypingSpeed 30ms
Env PS1 "$ "
Hide
Type "cd assets/demo/asp-plan/shop-api && claude() { sleep 3; glow -s light -w 150 ../result.md; } && clear" Enter
Show
Type "# Replay of a recorded run: 2026-11-09, Claude Code 2.1.319, claude-opus-5-5. Files: assets/demo/asp-plan/" Enter
Sleep 400ms
Type "tail -2 deploy.sh" Enter
Sleep 1500ms
Type `claude -p "/anticipating-shadow-points:asp --quick Add a NOT NULL email_verified column to users and backfill it, shipped by deploy.sh"` Enter
Sleep 14s
