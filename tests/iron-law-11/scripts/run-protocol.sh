#!/usr/bin/env bash
# Iron Law 11 — protocol runner.
#
# Iterates over every scenarios/*.txt, invokes `claude -p` per the locked
# parameters in preregistration.json, captures exit code + structured JSON
# envelope + textual result, and writes one trial record per scenario.
#
# Iron Law 12: --output-format json is mandatory (the entire point of the
# protocol is that we never trust $? alone).
#
# Iron Law 9: ASP_IN_GOAL=1 prevents the child from re-entering ASP if any
# scenario accidentally invokes /asp (it should not, but defense-in-depth).
#
# Usage:
#   ./scripts/run-protocol.sh                 # full N=50 formal run
#   ./scripts/run-protocol.sh smoke           # 3 non-formal smoke scenarios
#
# Output:
#   runs/<timestamp>-<seed>/
#     trials/<scenario_id>/
#       prompt.txt          (copy of the input)
#       exit_code.txt       (numeric exit status of claude -p)
#       result.json         (the --output-format json envelope)
#       result.text.txt     (the .result field extracted)
#       wall_clock.json     (start/end utc, elapsed seconds)
#     run-summary.json      (aggregate metadata, written at end)

set -euo pipefail

# Resolve script dir, then iron-law-11 root.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT"

# Locked parameters per preregistration.json.
MODEL="${MODEL:-claude-opus-4-7}"
MAX_TURNS="${MAX_TURNS:-1}"
TIMEOUT_S="${TIMEOUT_S:-300}"

# Choose scenario set.
MODE="${1:-formal}"
case "$MODE" in
  formal)
    SCENARIO_DIR="$ROOT/scenarios"
    RUN_ROOT="$ROOT/runs"
    ;;
  smoke)
    SCENARIO_DIR="$ROOT/smoke/scenarios"
    RUN_ROOT="$ROOT/smoke/runs"
    if [[ ! -d "$SCENARIO_DIR" ]]; then
      echo "smoke scenarios not found at $SCENARIO_DIR" >&2
      exit 1
    fi
    ;;
  *)
    echo "usage: $0 [formal|smoke]" >&2
    exit 2
    ;;
esac

# Reentrancy guard (Iron Law 9).
if [[ "${ASP_IN_GOAL:-}" == "1" ]]; then
  echo "Refusing to run inside an ASP_IN_GOAL=1 child session." >&2
  exit 3
fi
export ASP_IN_GOAL=1

# Verify claude is on PATH.
if ! command -v claude >/dev/null 2>&1; then
  echo "claude CLI not found on PATH; install Claude Code first." >&2
  exit 4
fi

# Run id: utc timestamp + short hash of locked seed.
SEED="$(cat "$ROOT/random_seed.txt" | tr -d '[:space:]')"
TS="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
RUN_ID="${TS}-${SEED}"
RUN_DIR="$RUN_ROOT/$RUN_ID"
mkdir -p "$RUN_DIR/trials"
echo "run_id: $RUN_ID"
echo "model:  $MODEL"
echo "scen:   $SCENARIO_DIR"
echo "run:    $RUN_DIR"
echo

# Enumerate scenarios in sorted lexical order — deterministic on macOS/Linux.
# Avoid mapfile (bash 4+); macOS ships with bash 3.2.
scenarios=()
while IFS= read -r line; do
  scenarios+=("$line")
done < <(find "$SCENARIO_DIR" -maxdepth 1 -name '*.txt' | sort)
total=${#scenarios[@]}
if [[ $total -eq 0 ]]; then
  echo "no scenarios found in $SCENARIO_DIR" >&2
  exit 5
fi
echo "running $total scenarios..."
echo

# Per-trial loop.
i=0
for spath in "${scenarios[@]}"; do
  i=$((i + 1))
  sid="$(basename "$spath" .txt)"
  tdir="$RUN_DIR/trials/$sid"
  mkdir -p "$tdir"

  # Copy prompt for provenance.
  cp "$spath" "$tdir/prompt.txt"

  printf "[%2d/%d] %s ... " "$i" "$total" "$sid"
  start_utc="$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)"
  start_epoch="$(date +%s)"

  # The actual call. Iron Law 12: --output-format json. Iron Law 11: we
  # capture $? but immediately fall through to JSON parsing without
  # routing on it.
  #
  # Per-trial timeout: use `timeout` if available (Linux), otherwise
  # gtimeout (macOS + coreutils), otherwise run without wrapper. This is
  # acceptable because each call has --max-turns 1 which is itself an
  # in-CLI bound.
  if command -v timeout >/dev/null 2>&1; then
    TIMEOUT_BIN=(timeout "${TIMEOUT_S}s")
  elif command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_BIN=(gtimeout "${TIMEOUT_S}s")
  else
    TIMEOUT_BIN=()
  fi

  set +e
  if [[ ${#TIMEOUT_BIN[@]} -gt 0 ]]; then
    "${TIMEOUT_BIN[@]}" claude -p \
      --output-format json \
      --model "$MODEL" \
      --max-turns "$MAX_TURNS" \
      < "$spath" \
      > "$tdir/result.json" \
      2> "$tdir/stderr.txt"
  else
    claude -p \
      --output-format json \
      --model "$MODEL" \
      --max-turns "$MAX_TURNS" \
      < "$spath" \
      > "$tdir/result.json" \
      2> "$tdir/stderr.txt"
  fi
  exit_code=$?
  set -e

  end_utc="$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)"
  end_epoch="$(date +%s)"
  elapsed=$((end_epoch - start_epoch))

  echo "$exit_code" > "$tdir/exit_code.txt"

  # claude -p --output-format json returns an ARRAY of events, not a
  # single object. The final event has type=="result" and carries the
  # summary fields (.result, .is_error, .terminal_reason, .stop_reason,
  # .total_cost_usd, .num_turns). We extract from there.
  #
  # This is an important refinement of the safe-parsing recipe in
  # paper/iron-law-11.md §4 (which originally said "parse .is_error from
  # the envelope"). The envelope is a JSON array; the field lives on
  # the last event of type "result".
  if jq -e . "$tdir/result.json" >/dev/null 2>&1; then
    # Try array-of-events shape first.
    if jq -e 'type == "array"' "$tdir/result.json" >/dev/null 2>&1; then
      RESULT_EVT='[.[] | select(.type == "result")] | last'
    else
      # Some versions may return a single object; fall back to identity.
      RESULT_EVT='.'
    fi
    jq -r "$RESULT_EVT | .result // \"\"" "$tdir/result.json" > "$tdir/result.text.txt"
    terminal="$(jq -r "$RESULT_EVT | .terminal_reason // .stop_reason // \"unknown\"" "$tdir/result.json")"
    is_error="$(jq -r "$RESULT_EVT | .is_error // false" "$tdir/result.json")"
  else
    printf '__INVALID_JSON__\n' > "$tdir/result.text.txt"
    terminal="invalid_json"
    is_error="true"
  fi

  # Per-trial wall-clock record.
  cat > "$tdir/wall_clock.json" <<EOF
{
  "started_at_utc": "$start_utc",
  "finished_at_utc": "$end_utc",
  "elapsed_seconds": $elapsed,
  "exit_code": $exit_code,
  "terminal_reason": "$terminal",
  "is_error": $is_error,
  "result_bytes": $(wc -c < "$tdir/result.text.txt" | tr -d ' ')
}
EOF

  printf "exit=%d elapsed=%ds terminal=%s\n" "$exit_code" "$elapsed" "$terminal"
done

# Aggregate run summary.
python3 "$HERE/_summarize-run.py" "$RUN_DIR" "$MODE" "$MODEL" "$MAX_TURNS"

echo
echo "run complete: $RUN_DIR"
echo "next: ./scripts/analyze.py $RUN_DIR"
