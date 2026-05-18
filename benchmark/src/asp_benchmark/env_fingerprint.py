"""Capture an environment fingerprint for the benchmark run.

The fingerprint is the smallest set of fields that, together, reproduce the
behavior of `claude -p` in this run. Fields the adjudicator must agree on:

  - Python version
  - OS + arch
  - claude CLI version
  - The exact model flag passed (caller's choice; recorded for audit)

Fields we explicitly do NOT capture (would harm reproducibility):
  - Wall-clock timestamps (other than the run start, recorded once)
  - Hostnames (PII, not reproducibility-relevant)
  - Process IDs
"""

from __future__ import annotations

import platform
import subprocess
import sys
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EnvFingerprint:
    """Reproducibility-relevant environment state."""

    python_version: str
    python_implementation: str
    platform_system: str  # "Darwin", "Linux", "Windows"
    platform_release: str  # e.g. "24.5.0"
    platform_machine: str  # "arm64", "x86_64"
    claude_cli_version: str  # "claude-code 2.1.143" or "unavailable"
    claude_cli_path: str  # absolute path to the claude binary, or "unavailable"

    def as_dict(self) -> dict:
        return asdict(self)


def capture() -> EnvFingerprint:
    """Build a fingerprint from the running interpreter and environment."""
    return EnvFingerprint(
        python_version=sys.version.split()[0],
        python_implementation=platform.python_implementation(),
        platform_system=platform.system(),
        platform_release=platform.release(),
        platform_machine=platform.machine(),
        claude_cli_version=_claude_cli_version(),
        claude_cli_path=_claude_cli_path(),
    )


def _claude_cli_version() -> str:
    try:
        out = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "unavailable"


def _claude_cli_path() -> str:
    try:
        out = subprocess.run(
            ["which", "claude"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "unavailable"
