# Track 1 replication: every number the papers compute is re-derived, tested and sealed. No model calls.
Output assets/demo/replicate.gif
Source assets/demo/_common.tape
Set Height 800
Hide
Type "clear" Enter
Show
Type "# Re-derive the papers' computed numbers and run both test suites (offline)" Enter
Sleep 600ms
Type ".venv/bin/python run_all.py" Enter
Sleep 9s
Type "# The seal also verifies on its own, stdlib only:" Enter
Type "python3 make_provenance.py --verify" Enter
Sleep 3s
