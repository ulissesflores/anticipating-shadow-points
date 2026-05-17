#!/usr/bin/env bash
# ASP install script — idempotent staging -> ~/.claude/ deployment.
# Usage: ./scripts/install.sh [--dry-run] [--force]

set -euo pipefail

# Resolve paths
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$HOME/.claude/skills/anticipating-shadow-points"
COMMANDS_DIR="$HOME/.claude/commands"

DRY_RUN=0
FORCE=0
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        --force)   FORCE=1   ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--force]"
            echo "  --dry-run  Show what would be done without modifying anything."
            echo "  --force    Overwrite existing files without backup."
            exit 0
            ;;
        *)
            echo "Unknown arg: $arg" >&2
            exit 2
            ;;
    esac
done

log() {
    if [[ $DRY_RUN -eq 1 ]]; then
        printf '[DRY-RUN] %s\n' "$*"
    else
        printf '[install] %s\n' "$*"
    fi
}

do_run() {
    if [[ $DRY_RUN -eq 1 ]]; then
        printf '[DRY-RUN] $ %s\n' "$*"
    else
        "$@"
    fi
}

# Sanity check
if [[ ! -d "$REPO_DIR/skill" || ! -d "$REPO_DIR/command" ]]; then
    echo "ERROR: $REPO_DIR is not a valid ASP repo (missing skill/ or command/)" >&2
    exit 1
fi

log "Repo:     $REPO_DIR"
log "Target:   $SKILL_DIR"
log "Commands: $COMMANDS_DIR"

# Backup existing skill if present and content differs
if [[ -d "$SKILL_DIR" && $FORCE -eq 0 ]]; then
    if diff -rq "$REPO_DIR/skill" "$SKILL_DIR" >/dev/null 2>&1; then
        log "Skill already installed and identical — skipping skill copy."
        SKIP_SKILL=1
    else
        BACKUP="$SKILL_DIR.bak.$(date +%Y%m%d-%H%M%S)"
        log "Existing skill differs; backing up to $BACKUP"
        do_run mv "$SKILL_DIR" "$BACKUP"
        SKIP_SKILL=0
    fi
else
    SKIP_SKILL=0
fi

# Install skill
if [[ ${SKIP_SKILL:-0} -ne 1 ]]; then
    log "Creating $SKILL_DIR"
    do_run mkdir -p "$SKILL_DIR"
    log "Copying skill/ -> $SKILL_DIR"
    do_run cp -R "$REPO_DIR/skill/." "$SKILL_DIR/"
fi

# Install slash commands
log "Ensuring $COMMANDS_DIR exists"
do_run mkdir -p "$COMMANDS_DIR"

for cmd in asp.md ASP.md; do
    src="$REPO_DIR/command/$cmd"
    dst="$COMMANDS_DIR/$cmd"
    if [[ ! -f "$src" ]]; then
        log "Source missing: $src (skipping)"
        continue
    fi
    if [[ -f "$dst" && $FORCE -eq 0 ]]; then
        if diff -q "$src" "$dst" >/dev/null 2>&1; then
            log "Identical, skipping: $dst"
            continue
        else
            log "Backing up $dst -> $dst.bak"
            do_run cp "$dst" "$dst.bak"
        fi
    fi
    log "Installing $dst"
    do_run cp "$src" "$dst"
done

log ""
log "Install complete."
if [[ $DRY_RUN -eq 1 ]]; then
    log "This was a DRY RUN. Re-run without --dry-run to apply."
else
    log "Verify with: ls $SKILL_DIR && ls $COMMANDS_DIR/asp.md"
fi
