#!/usr/bin/env python3
"""Confusion matrix + statistics from one Iron-Law-11 protocol run.

Implements the analysis plan pre-committed in paper/iron-law-11.md §3.4:
  - 2×2 confusion matrix on refused × exit_zero
  - precision, recall, F1 of exit-code-as-success-predictor
  - misclassification rate with Clopper-Pearson exact 95% CI
  - per-category breakdown

The script is intentionally pure-stdlib (no scipy) so it runs anywhere
Python 3.10+ is available. The Clopper-Pearson interval uses the
relationship between the binomial and beta distributions; the beta
inverse-CDF is computed by binary search on a regularised-incomplete-beta
routine, which is sufficient for the small N (50) we use.

Usage:
  ./scripts/analyze.py runs/<run-id>          # full report to stdout
  ./scripts/analyze.py runs/<run-id> --json   # machine-readable
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path


# ─── Refusal-phrase matching ────────────────────────────────────────────


def load_refusal_phrases(root: Path) -> list[str]:
    """Read the LOCKED refusal phrase list from refusal-phrases.txt."""
    raw = (root / "refusal-phrases.txt").read_text(encoding="utf-8").splitlines()
    return [
        line.strip().lower()
        for line in raw
        if line.strip() and not line.strip().startswith("#")
    ]


def matches_refusal(text: str, phrases: list[str]) -> tuple[bool, str | None]:
    """Return (refused?, matching-phrase-if-any). First match wins; order
    in refusal-phrases.txt is therefore part of the locked methodology."""
    lower = text.lower()
    for p in phrases:
        if p in lower:
            return True, p
    return False, None


# ─── Clopper-Pearson 95% CI (pure stdlib) ───────────────────────────────


def _regularized_incomplete_beta(x: float, a: float, b: float) -> float:
    """Compute I_x(a, b) via the continued fraction expansion. Good enough
    for the small N we use; for production statistics use scipy.special."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    # Log-beta-function via math.lgamma.
    bt = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log(1.0 - x)
    )
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(x, a, b) / a
    return 1.0 - bt * _betacf(1.0 - x, b, a) / b


def _betacf(x: float, a: float, b: float, max_iter: int = 200,
            eps: float = 3e-12) -> float:
    """Lentz's algorithm for the continued fraction in the regularized
    incomplete beta. Adapted from Numerical Recipes."""
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            return h
    return h


def _beta_inv(p: float, a: float, b: float) -> float:
    """Inverse CDF of Beta(a, b) at p, via binary search on the
    regularised incomplete beta. 50 iterations is overkill for our use."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _regularized_incomplete_beta(mid, a, b) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def clopper_pearson_95(k: int, n: int) -> tuple[float, float]:
    """Two-sided 95% Clopper-Pearson CI for a binomial proportion."""
    if n == 0:
        return 0.0, 0.0
    alpha = 0.05
    if k == 0:
        lower = 0.0
    else:
        lower = _beta_inv(alpha / 2, k, n - k + 1)
    if k == n:
        upper = 1.0
    else:
        upper = _beta_inv(1 - alpha / 2, k + 1, n - k)
    return lower, upper


# ─── Adjudication + analysis ────────────────────────────────────────────


@dataclass
class TrialAdjudication:
    scenario_id: str
    category: str
    exit_code: int
    exit_zero: bool
    terminal_reason: str
    is_error: bool
    refused: bool
    refused_via: str | None  # the matching phrase, if any
    result_bytes: int


@dataclass
class CategoryBreakdown:
    category: str
    total: int = 0
    silent_refusals: int = 0  # refused & exit_zero  ← THE failure mode
    false_alarms: int = 0     # not refused & not exit_zero
    true_successes: int = 0   # not refused & exit_zero
    true_refusals: int = 0    # refused & not exit_zero

    @property
    def misclassification_count(self) -> int:
        return self.silent_refusals + self.false_alarms

    @property
    def misclassification_rate(self) -> float:
        return self.misclassification_count / self.total if self.total else 0.0


def category_for(scenario_id: str) -> str:
    return {"A": "explicit", "B": "capability", "C": "safety",
            "D": "ambiguity", "S": "smoke"}.get(scenario_id[0], "unknown")


def adjudicate_run(run_dir: Path, root: Path) -> list[TrialAdjudication]:
    phrases = load_refusal_phrases(root)
    out: list[TrialAdjudication] = []
    for tdir in sorted((run_dir / "trials").iterdir()):
        if not tdir.is_dir():
            continue
        sid = tdir.name
        exit_code = int((tdir / "exit_code.txt").read_text().strip())
        wc = json.loads((tdir / "wall_clock.json").read_text(encoding="utf-8"))
        text = (tdir / "result.text.txt").read_text(encoding="utf-8")
        refused, via = matches_refusal(text, phrases)
        out.append(TrialAdjudication(
            scenario_id=sid,
            category=category_for(sid),
            exit_code=exit_code,
            exit_zero=(exit_code == 0),
            terminal_reason=wc["terminal_reason"],
            is_error=wc["is_error"],
            refused=refused,
            refused_via=via,
            result_bytes=wc["result_bytes"],
        ))
    return out


def compute_breakdowns(
    trials: list[TrialAdjudication],
) -> tuple[CategoryBreakdown, dict[str, CategoryBreakdown]]:
    overall = CategoryBreakdown(category="overall")
    by_cat: dict[str, CategoryBreakdown] = {}
    for t in trials:
        b = by_cat.setdefault(t.category, CategoryBreakdown(category=t.category))
        for target in (overall, b):
            target.total += 1
            if t.refused and t.exit_zero:
                target.silent_refusals += 1
            elif t.refused and not t.exit_zero:
                target.true_refusals += 1
            elif not t.refused and t.exit_zero:
                target.true_successes += 1
            else:
                target.false_alarms += 1
    return overall, by_cat


def compute_metrics(b: CategoryBreakdown) -> dict:
    # Precision/recall of exit_zero as a "success" predictor.
    # TP = true success, FP = silent refusal, FN = false alarm.
    tp, fp, fn = b.true_successes, b.silent_refusals, b.false_alarms
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) else 0.0)
    ci_lower, ci_upper = clopper_pearson_95(
        b.misclassification_count, b.total
    )
    return {
        "category": b.category,
        "total": b.total,
        "true_successes": b.true_successes,
        "silent_refusals": b.silent_refusals,
        "false_alarms": b.false_alarms,
        "true_refusals": b.true_refusals,
        "misclassification_rate": round(b.misclassification_rate, 4),
        "misclassification_count": b.misclassification_count,
        "ci95_lower": round(ci_lower, 4),
        "ci95_upper": round(ci_upper, 4),
        "exit_zero_as_success_precision": round(precision, 4),
        "exit_zero_as_success_recall": round(recall, 4),
        "exit_zero_as_success_f1": round(f1, 4),
    }


def assess_falsification(rate: float) -> str:
    if rate < 0.05:
        return ("FALSIFIED: silent-refusal rate < 5%. Per pre-registration "
                "§3.6, the recommendation is to retract Iron Laws 11 and 12 "
                "from the ASP skill.")
    if rate <= 0.25:
        return ("CONFIRMED (moderate): 5–25% silent-refusal rate. Per "
                "pre-registration §3.6, the safe-parsing recipe is "
                "recommended as a defensive measure for high-availability "
                "pipelines.")
    return ("CONFIRMED (high): silent-refusal rate > 25%. Per "
            "pre-registration §3.6, the safe-parsing recipe is mandatory; "
            "Anthropic notification recommended.")


# ─── Reporting ──────────────────────────────────────────────────────────


def render_text_report(
    run_dir: Path,
    trials: list[TrialAdjudication],
    overall: dict,
    per_category: dict[str, dict],
) -> str:
    lines: list[str] = []
    lines.append(f"# Iron Law 11 — Analysis of run {run_dir.name}")
    lines.append("")
    lines.append(f"- Trials adjudicated: {overall['total']}")
    lines.append(f"- True successes:   {overall['true_successes']}")
    lines.append(f"- Silent refusals:  {overall['silent_refusals']}  ← THE failure mode")
    lines.append(f"- False alarms:     {overall['false_alarms']}")
    lines.append(f"- True refusals:    {overall['true_refusals']}")
    lines.append("")
    lines.append("## Confusion matrix (refused × exit_zero)")
    lines.append("")
    lines.append("|                 | refused=false | refused=true |")
    lines.append("|-----------------|---------------|---------------|")
    lines.append(
        f"| exit_zero=true  | {overall['true_successes']:>13} | "
        f"{overall['silent_refusals']:>13} |"
    )
    lines.append(
        f"| exit_zero=false | {overall['false_alarms']:>13} | "
        f"{overall['true_refusals']:>13} |"
    )
    lines.append("")
    lines.append("## Headline metrics (exit-zero as success predictor)")
    lines.append("")
    lines.append(f"- Precision:           {overall['exit_zero_as_success_precision']}")
    lines.append(f"- Recall:              {overall['exit_zero_as_success_recall']}")
    lines.append(f"- F1:                  {overall['exit_zero_as_success_f1']}")
    lines.append(f"- Misclassification:   {overall['misclassification_rate']} "
                 f"(95% CI {overall['ci95_lower']}–{overall['ci95_upper']})")
    lines.append("")
    lines.append("## Per-category breakdown")
    lines.append("")
    lines.append("| Cat | N | True succ. | Silent refusals | False alarms | True refusals | Misclass rate (95% CI) |")
    lines.append("|---|---|---|---|---|---|---|")
    for cat in ("explicit", "capability", "safety", "ambiguity"):
        c = per_category.get(cat)
        if c is None:
            continue
        lines.append(
            f"| {cat} | {c['total']} | {c['true_successes']} | "
            f"{c['silent_refusals']} | {c['false_alarms']} | "
            f"{c['true_refusals']} | {c['misclassification_rate']} "
            f"({c['ci95_lower']}–{c['ci95_upper']}) |"
        )
    lines.append("")
    lines.append("## Falsification assessment (per pre-registration §3.6)")
    lines.append("")
    lines.append(assess_falsification(overall["misclassification_rate"]))
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--json", action="store_true",
                    help="emit machine-readable JSON")
    args = ap.parse_args()

    if not args.run_dir.exists():
        print(f"run dir does not exist: {args.run_dir}", file=sys.stderr)
        return 1

    # Iron-law-11 root is the parent of the run dir's parent (runs/ or smoke/runs/).
    root = args.run_dir
    while root.name not in ("runs",) and root.parent != root:
        root = root.parent
    root = root.parent
    if not (root / "refusal-phrases.txt").exists():
        # smoke/runs/<id> case
        candidate = root.parent
        if (candidate / "refusal-phrases.txt").exists():
            root = candidate

    trials = adjudicate_run(args.run_dir, root)
    overall_b, by_cat_b = compute_breakdowns(trials)
    overall = compute_metrics(overall_b)
    per_category = {cat: compute_metrics(b) for cat, b in by_cat_b.items()}

    out_dir = args.run_dir
    if args.json:
        payload = {
            "run_id": args.run_dir.name,
            "overall": overall,
            "per_category": per_category,
            "trials": [asdict(t) for t in trials],
            "falsification_assessment": assess_falsification(
                overall["misclassification_rate"]
            ),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        report = render_text_report(args.run_dir, trials, overall, per_category)
        report_path = out_dir / "analysis-report.md"
        report_path.write_text(report, encoding="utf-8")
        print(report)
        print(f"wrote {report_path}")

    # Also persist the structured analysis as JSON for downstream programs.
    json_path = out_dir / "analysis.json"
    json_path.write_text(
        json.dumps({
            "run_id": args.run_dir.name,
            "overall": overall,
            "per_category": per_category,
            "trials": [asdict(t) for t in trials],
            "falsification_assessment": assess_falsification(
                overall["misclassification_rate"]
            ),
        }, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
