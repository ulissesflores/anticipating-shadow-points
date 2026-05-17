#!/usr/bin/env bash
# ASP uninstall script — fully reverse install.sh.
# Usage: ./scripts/uninstall.sh [--dry-run] [--yes]

set -euo pipefail

SKILL_DIR="$HOME/.claude/skills/anticipating-shadow-points"
COMMANDS_DIR="$HOME/.claude/commands"

DRY_RUN=0
ASSUME_YES=0
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        --yes|-y)  ASSUME_YES=1 ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--yes]"
            echo "  --dry-run  Show what would be removed without modifying."
            echo "  --yes      Skip interactive confirmation."
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
        printf '[uninstall] %s\n' "$*"
    fi
}

do_run() {
    if [[ $DRY_RUN -eq 1 ]]; then
        printf '[DRY-RUN] $ %s\n' "$*"
    else
        "$@"
    fi
}

confirm() {
    if [[ $ASSUME_YES -eq 1 || $DRY_RUN -eq 1 ]]; then
        return 0
    fi
    read -rp "Proceed with uninstall? [y/N] " ans
    case "$ans" in
        y|Y|yes|YES) return 0 ;;
        *) echo "Aborted."; exit 1 ;;
    esac
}

log "Will remove:"
log "  $SKILL_DIR"
log "  $COMMANDS_DIR/asp.md"
log "  $COMMANDS_DIR/ASP.md"

confirm

if [[ -d "$SKILL_DIR" ]]; then
    log "Removing $SKILL_DIR"
    do_run rm -rf "$SKILL_DIR"
else
    log "Already absent: $SKILL_DIR"
fi

for cmd in asp.md ASP.md; do
    dst="$COMMANDS_DIR/$cmd"
    if [[ -f "$dst" ]]; then
        log "Removing $dst"
        do_run rm -f "$dst"
    else
        log "Already absent: $dst"
    fi
done

log "Uninstall complete."
if [[ $DRY_RUN -eq 1 ]]; then
    log "This was a DRY RUN. Re-run without --dry-run to apply."
fi
