# Track 1 replication: every number the papers compute is re-derived, tested and sealed. No model calls.
Output assets/demo/replicate.gif
Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 500
Set Padding 24
Set Theme "Builtin Light"
Set TypingSpeed 35ms
Env PS1 "$ "
Env PYTHONDONTWRITEBYTECODE "1"
Hide
Type "clear" Enter
Show
Type "# Re-derive the papers' computed numbers and run both test suites (offline)" Enter
Sleep 600ms
Type ".venv/bin/python run_all.py" Enter
Sleep 14s
Type "# The seal also verifies on its own, stdlib only:" Enter
Type "python3 make_provenance.py --verify" Enter
Sleep 3s
