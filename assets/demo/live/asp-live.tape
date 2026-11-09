# ASP, live: installed from its marketplace into a fresh Claude Code config, then run on the
# official FastAPI full-stack template. Nothing here is replayed: the real run is recorded at real
# speed, and assets/demo/live/make_gif.py then speeds up the wait, with the speed shown on screen.
# The three Env paths below are placeholders; the recording used local ones (edit to rerun): DEMO is a clone of fastapi/full-stack-fastapi-template plus task.txt,
# outside any folder with a CLAUDE.md; CLAUDE_CONFIG_DIR is a fresh config where only /login was run.
Output assets/demo/live/raw.mp4
Set Shell "bash"
Set FontSize 24
Set Width 1280
Set Height 820
Set Padding 30
Set Theme "GitHub Dark"
Set TypingSpeed 14ms
Set WindowBar Colorful
Env PS1 "demo $ "
Env CLAUDE_CONFIG_DIR "/path/to/fresh-claude-config"
Env DEMO "/path/to/full-stack-fastapi-template"
Env ASP_VIEW "/path/to/ASP/assets/demo/live/asp_view.py"
Hide
Type `cd "$DEMO" && export ASP_VIEW_LOG=../run.jsonl ASP_VIEW_RESULT=../result.md ASP_VIEW_TIMES=../times.json && alias asp-view='python3 "$ASP_VIEW"' && python3 -c 'import time; print(time.time())' > ../t_show && clear` Enter
Sleep 1s
Show
Type "# Fresh Claude Code config: no settings, no CLAUDE.md, no ASP" Enter
Sleep 1s
Type "claude plugin marketplace add ulissesflores/anticipating-shadow-points" Enter
Wait+Line@3m /demo \$$/
Type "claude plugin install anticipating-shadow-points@anticipating-shadow-points" Enter
Wait+Line@3m /demo \$$/
Sleep 1500ms
Type "clear" Enter
Type "# A real project: the official FastAPI full-stack template." Enter
Type "ls" Enter
Sleep 2s
Type "cat task.txt | fold -s -w 78 | head -3" Enter
Sleep 4s
Type "clear" Enter
Type `claude -p "$(cat task.txt)" --permission-mode plan --output-format stream-json --verbose | asp-view` Enter
Wait+Line@40m /demo \$$/
Sleep 16s
