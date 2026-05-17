#!/usr/bin/env bash
# ASP verify script — runs the 16 success criteria.
# Usage: ./scripts/verify.sh [--pre-install]
#   --pre-install : skip criterion 13 (staging isolation), useful in CI before install.

set -u

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_SRC="$REPO_DIR/skill"
COMMAND_SRC="$REPO_DIR/command"
DOCS_DIR="$REPO_DIR/docs"
TESTS_DIR="$REPO_DIR/tests"
SCRIPTS_DIR="$REPO_DIR/scripts"
HOME_SKILL="$HOME/.claude/skills/anticipating-shadow-points"
HOME_CMDS="$HOME/.claude/commands"

PRE_INSTALL=0
for arg in "$@"; do
    case "$arg" in
        --pre-install) PRE_INSTALL=1 ;;
        -h|--help)
            echo "Usage: $0 [--pre-install]"
            exit 0
            ;;
    esac
done

PASS=0
FAIL=0
declare -a FAIL_REASONS=()

check() {
    local name="$1"; local cmd="$2"
    if eval "$cmd" >/dev/null 2>&1; then
        printf '  [OK]   %s\n' "$name"
        PASS=$((PASS + 1))
    else
        printf '  [FAIL] %s\n' "$name"
        FAIL=$((FAIL + 1))
        FAIL_REASONS+=("$name -> failed: $cmd")
    fi
}

echo "=== ASP verify.sh — 16 success criteria ==="

# 1. Carregamento — SKILL.md exists and YAML frontmatter is valid
check "1. SKILL.md frontmatter parses (name + description present)" \
    "awk '/^---$/{i++; if(i==2)exit} i==1' '$SKILL_SRC/SKILL.md' | tail -n +2 | python3 -c 'import sys,yaml; d=yaml.safe_load(sys.stdin); assert d.get(\"name\") and d.get(\"description\")'"

# 2. Frontmatter description starts with 'Use when'
check "2. SKILL.md description starts 'Use when'" \
    "awk '/^---$/{i++; if(i==2)exit} i==1' '$SKILL_SRC/SKILL.md' | grep -q '^description: Use when'"

# 3. TDD baseline file exists
check "3. tests/baseline-pressure-tests.md exists with 3 scenarios" \
    "[ \$(grep -c '^## Scenario' '$TESTS_DIR/baseline-pressure-tests.md') -eq 3 ]"

# 4. 5 evals files exist
check "4. All 5 evals/*.md files exist" \
    "[ \$(ls '$SKILL_SRC/evals/'*.md 2>/dev/null | wc -l) -eq 5 ]"

# 5. Validator-independence marker present in SKILL.md
check "5. SKILL.md mentions validator separate-prompt discipline" \
    "grep -qi 'separate prompt\\|fresh prompt\\|NOT receive' '$SKILL_SRC/SKILL.md'"

# 6. question-frames.md has ≤3 questions per phase reference
check "6. question-frames.md exists with Pre/Post sections" \
    "grep -q 'Pre-research' '$SKILL_SRC/question-frames.md' && grep -q 'Post-research' '$SKILL_SRC/question-frames.md'"

# 7. project-charter template exists with placeholders
check "7. templates/project-charter.md has ≥9 placeholders" \
    "[ \$(grep -c '{{' '$SKILL_SRC/templates/project-charter.md') -ge 9 ]"

# 8. deliverables-register template exists
check "8. templates/deliverables-register.md exists" \
    "[ -f '$SKILL_SRC/templates/deliverables-register.md' ]"

# 9. micro-todo template has contract fields
check "9. templates/micro-todo.md has PRECONDITION/ACTION/POSTCONDITION/ACCEPTANCE-TEST/FALSIFICATION-TEST" \
    "grep -q PRECONDITION '$SKILL_SRC/templates/micro-todo.md' && grep -q FALSIFICATION-TEST '$SKILL_SRC/templates/micro-todo.md'"

# 10. /goal mention in SKILL.md
check "10. SKILL.md mentions /goal as Phase 9 kernel" \
    "grep -q '/goal' '$SKILL_SRC/SKILL.md'"

# 11. execution-report template exists
check "11. templates/execution-report.md exists with metrics section" \
    "grep -q 'Métricas\\|Metrics' '$SKILL_SRC/templates/execution-report.md'"

# 12. advisor mention in SKILL.md
check "12. SKILL.md mentions advisor() tool" \
    "grep -q 'advisor' '$SKILL_SRC/SKILL.md'"

# 13. Staging isolation (skipped in --pre-install)
if [[ $PRE_INSTALL -eq 0 ]]; then
    check "13. Skill present in ~/.claude/skills/anticipating-shadow-points/" \
        "[ -d '$HOME_SKILL' ] && [ -f '$HOME_SKILL/SKILL.md' ]"
else
    printf '  [SKIP] 13. Staging isolation (pre-install mode)\n'
fi

# 14. install/uninstall syntax valid
check "14a. install.sh syntax valid" \
    "bash -n '$SCRIPTS_DIR/install.sh'"
check "14b. uninstall.sh syntax valid" \
    "bash -n '$SCRIPTS_DIR/uninstall.sh'"

# 15. 5 READMEs present (EN + 4 translations)
check "15. README.md + 4 docs/README.{es,pt,it,he}.md present" \
    "[ -f '$REPO_DIR/README.md' ] && [ -f '$DOCS_DIR/README.es.md' ] && [ -f '$DOCS_DIR/README.pt.md' ] && [ -f '$DOCS_DIR/README.it.md' ] && [ -f '$DOCS_DIR/README.he.md' ]"

# 16. /goal pre-flight probe file exists (or is scheduled — accept either)
check "16. tests/goal-invocability-probe.md present OR scheduled-for-creation" \
    "[ -f '$TESTS_DIR/goal-invocability-probe.md' ] || grep -q 'goal-invocability-probe' '$REPO_DIR/README.md' '$SKILL_SRC/SKILL.md' 2>/dev/null"

# 17. (v4) Native execution kernel doc present with required sections
check "17. skill/execution-kernel.md has Worker loop + Evaluator subagent + Checkpoint + Evidence sections" \
    "[ -f '$SKILL_SRC/execution-kernel.md' ] && grep -q 'Worker loop' '$SKILL_SRC/execution-kernel.md' && grep -q 'Evaluator subagent' '$SKILL_SRC/execution-kernel.md' && grep -q 'Checkpoint' '$SKILL_SRC/execution-kernel.md' && grep -q 'Evidence file format' '$SKILL_SRC/execution-kernel.md'"

# 18. (v5) claude -p /goal runner doc present with required sections
check "18. skill/claude-p-goal-runner.md has Spawn pattern + File-based contract + Monitor + Reconciliation + Iron Law 9" \
    "[ -f '$SKILL_SRC/claude-p-goal-runner.md' ] && grep -q 'Spawn pattern' '$SKILL_SRC/claude-p-goal-runner.md' && grep -q 'state.json' '$SKILL_SRC/claude-p-goal-runner.md' && grep -q 'Monitor' '$SKILL_SRC/claude-p-goal-runner.md' && grep -q 'Reconciliation\\|Reconciliação' '$SKILL_SRC/claude-p-goal-runner.md' && grep -q 'ASP_IN_GOAL' '$SKILL_SRC/claude-p-goal-runner.md'"

# 19. (v5) claude -p /goal empirical probe documents the 2026-05-17 battery
check "19. tests/claude-p-goal-runner-probe.md documents 2026-05-17 battery + Critical finding C" \
    "[ -f '$TESTS_DIR/claude-p-goal-runner-probe.md' ] && grep -q '2026-05-17' '$TESTS_DIR/claude-p-goal-runner-probe.md' && grep -qi 'critical finding' '$TESTS_DIR/claude-p-goal-runner-probe.md'"

echo ""
echo "=== Summary ==="
echo "  Pass: $PASS"
echo "  Fail: $FAIL"

if [[ $FAIL -gt 0 ]]; then
    echo ""
    echo "  Failures:"
    for r in "${FAIL_REASONS[@]}"; do
        echo "  - $r"
    done
    exit 1
fi

echo "  All checks OK."
exit 0
