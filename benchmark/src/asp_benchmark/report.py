"""Human-readable Markdown report for one run.

The report is a courtesy artifact: anything load-bearing lives in
manifest.json and the per-eval adjudication JSON. The report exists so
a reader can scan a run without parsing JSON.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .adjudicator import Coverage
from .env_fingerprint import EnvFingerprint
from .eval_parser import EvalSpec


def render_report(
    *,
    run_dir: Path,
    started_at: datetime,
    finished_at: datetime,
    mode: str,
    model: str,
    env: EnvFingerprint,
    specs: list[EvalSpec],
    coverages: list[Coverage],
    manifest_hash: str,
) -> str:
    """Build the report.md content for this run."""
    cov_by_key: dict[tuple[str, str], Coverage] = {
        (c.eval_id, c.candidate_label): c for c in coverages
    }

    lines: list[str] = []
    lines.append(f"# ASP Benchmark — Run {run_dir.name}\n")
    lines.append(f"- **Mode**: `{mode}`")
    lines.append(f"- **Model**: `{model}`")
    lines.append(f"- **Started**: `{started_at.isoformat()}`")
    lines.append(f"- **Finished**: `{finished_at.isoformat()}`")
    lines.append(f"- **Manifest hash**: `{manifest_hash}`")
    lines.append(f"- **Python**: `{env.python_version} ({env.python_implementation})`")
    lines.append(f"- **OS**: `{env.platform_system} {env.platform_release} / {env.platform_machine}`")
    lines.append(f"- **Claude CLI**: `{env.claude_cli_version}` at `{env.claude_cli_path}`\n")

    # Headline table — RED vs GREEN coverage per eval.
    lines.append("## Coverage by eval")
    lines.append("")
    lines.append("| Eval | RED coverage | GREEN coverage | Δ | RED matched / total | GREEN matched / total |")
    lines.append("|---|---|---|---|---|---|")
    red_avg_num = 0.0
    green_avg_num = 0.0
    counted = 0
    for spec in specs:
        red = cov_by_key.get((spec.eval_id, "RED"))
        green = cov_by_key.get((spec.eval_id, "GREEN"))
        if red is None or green is None:
            continue
        red_pct = f"{red.coverage * 100:.1f}%"
        green_pct = f"{green.coverage * 100:.1f}%"
        delta_pp = (green.coverage - red.coverage) * 100
        delta_str = f"{delta_pp:+.1f} pp"
        red_frac = f"{len(red.matched)} / {len(red.matched) + len(red.unmatched)}"
        green_frac = f"{len(green.matched)} / {len(green.matched) + len(green.unmatched)}"
        lines.append(
            f"| {spec.eval_id} — {spec.title} | {red_pct} | {green_pct} | "
            f"{delta_str} | {red_frac} | {green_frac} |"
        )
        red_avg_num += red.coverage
        green_avg_num += green.coverage
        counted += 1

    if counted:
        lines.append(
            f"| **Mean** | **{red_avg_num / counted * 100:.1f}%** | "
            f"**{green_avg_num / counted * 100:.1f}%** | "
            f"**{(green_avg_num - red_avg_num) / counted * 100:+.1f} pp** | | |"
        )

    # Per-eval detail.
    lines.append("\n## Per-eval detail\n")
    for spec in specs:
        lines.append(f"### {spec.eval_id} — {spec.title}\n")
        lines.append(f"Source: `{spec.source_path}`")
        lines.append(f"Acceptance threshold: `{spec.acceptance_threshold:.0%}`")
        lines.append(f"Expected shadow points: {len(spec.expected)}")
        for condition in ("RED", "GREEN"):
            cov = cov_by_key.get((spec.eval_id, condition))
            if cov is None:
                continue
            lines.append(f"\n**{condition}** — coverage {cov.coverage:.1%} "
                         f"(threshold {spec.acceptance_threshold:.0%}; "
                         f"{'PASS' if cov.coverage >= spec.acceptance_threshold else 'FAIL'})")
            lines.append(f"- text sha256: `{cov.candidate_text_sha256}`")
            lines.append(f"- Jaccard threshold: `{cov.jaccard_threshold}`")
            lines.append(f"- Matched ({len(cov.matched)}):")
            for m in cov.matched:
                via = m.matched_via
                score = f" (J={m.jaccard_score})" if via == "jaccard" else ""
                lines.append(f"  - {m.index}. {m.name} — via `{via}`{score}")
            lines.append(f"- Unmatched ({len(cov.unmatched)}):")
            for u in cov.unmatched:
                lines.append(f"  - {u.index}. {u.name} — best Jaccard `{u.best_jaccard}`")
        lines.append("")

    lines.append("## Provenance\n")
    lines.append(
        "Every adjudication call is deterministic: same `candidate_text_sha256` "
        "always yields the same matched/unmatched partition. Tampering with any "
        "file under this run directory will be detected by re-running:"
    )
    lines.append("")
    lines.append("```bash")
    lines.append(f"asp-benchmark verify {run_dir.name}")
    lines.append("```\n")
    lines.append(
        "The manifest hash above is derived from the env fingerprint, the "
        "code inventory (every `.py` file under `benchmark/src/`), the "
        "input prompts, the candidate outputs, and the per-eval "
        "adjudication. Reordering files, renaming files, or editing any "
        "byte will invalidate the manifest hash.\n"
    )
    return "\n".join(lines) + "\n"
