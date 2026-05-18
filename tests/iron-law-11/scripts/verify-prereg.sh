#!/usr/bin/env bash
# Verify pre-registration integrity.
#
# Re-hashes refusal-phrases.txt and every scenarios/*.txt and compares
# against the values committed in preregistration.json. Any drift means
# the pre-registration has been violated (someone edited a scenario or
# the phrase list after registration); analyze.py output produced after
# such a violation is no longer pre-registered.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT"

PREREG="$ROOT/preregistration.json"
if [[ ! -f "$PREREG" ]]; then
  echo "preregistration.json missing at $PREREG" >&2
  exit 1
fi

python3 - <<'PY'
import hashlib
import json
import sys
from pathlib import Path

prereg = json.loads(Path("preregistration.json").read_text(encoding="utf-8"))

issues = []

# 1. refusal phrases.
expected = prereg["refusal_phrases_sha256"]
actual = hashlib.sha256(Path("refusal-phrases.txt").read_bytes()).hexdigest()
if actual != expected:
    issues.append(f"refusal-phrases.txt sha256 drift: expected {expected[:16]} got {actual[:16]}")

# 2. random seed.
expected_seed = prereg["random_seed"]
actual_seed = Path("random_seed.txt").read_text().strip()
if actual_seed != expected_seed:
    issues.append(f"random_seed.txt drift: expected {expected_seed} got {actual_seed}")

# 3. every scenario file.
for sid, expected_rec in prereg["scenarios"].items():
    p = Path("scenarios") / f"{sid}.txt"
    if not p.exists():
        issues.append(f"scenarios/{sid}.txt: missing")
        continue
    actual_sha = hashlib.sha256(p.read_bytes()).hexdigest()
    expected_sha = expected_rec["sha256"]
    if actual_sha != expected_sha:
        issues.append(f"scenarios/{sid}.txt sha256 drift: expected "
                      f"{expected_sha[:16]} got {actual_sha[:16]}")

if issues:
    print("PRE-REGISTRATION VIOLATION:", file=sys.stderr)
    for it in issues:
        print(f"  - {it}", file=sys.stderr)
    sys.exit(2)

n_scenarios = len(prereg["scenarios"])
print(f"OK: pre-registration intact ({n_scenarios} scenarios hashed)")
PY
