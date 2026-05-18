"""Unit tests for the eval markdown parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from asp_benchmark.eval_parser import parse_eval, parse_evals_dir


_FIXTURE = """\
# Eval 07 — Demo task

## INPUT

Task: "Ship a feature with a NOT NULL column on a 1M-row table."

## EXPECTED SHADOW POINTS (≥3 required; ≥75% coverage required for eval pass)

1. **Replica lag** — replication slot may fall behind during the rewrite.
2. **Lock contention** — ALTER TABLE blocks reads/writes; consider online ALTER.
3. **Rollback plan** — what if it breaks halfway? Is there a transactional path back?

## ACCEPTANCE

The eval passes if the plan covers ≥75% of expected shadow points. Synonym matches OK.
"""


def test_parse_eval_basic(tmp_path: Path):
    f = tmp_path / "07-demo.md"
    f.write_text(_FIXTURE, encoding="utf-8")
    spec = parse_eval(f)
    assert spec.eval_id == "E7"
    assert spec.title == "Demo task"
    assert "NOT NULL column" in spec.input_prompt
    assert len(spec.expected) == 3
    assert spec.expected[0].name == "Replica lag"
    assert spec.expected[0].index == 1
    assert spec.expected[2].name == "Rollback plan"
    assert spec.acceptance_threshold == 0.75


def test_parse_eval_missing_input_section_raises(tmp_path: Path):
    f = tmp_path / "07-broken.md"
    f.write_text(
        "# Eval 07 — broken\n\n## EXPECTED SHADOW POINTS\n\n1. **X** — y\n\n## ACCEPTANCE\n80%\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing section"):
        parse_eval(f)


def test_parse_eval_non_sequential_numbering_raises(tmp_path: Path):
    f = tmp_path / "07-bad-nums.md"
    f.write_text(
        "# Eval 07 — bad nums\n\n## INPUT\nx\n\n## EXPECTED SHADOW POINTS\n\n"
        "1. **A** — a\n3. **C** — c\n\n## ACCEPTANCE\n80%\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="numbered 1..N sequentially"):
        parse_eval(f)


def test_parse_evals_dir_skips_non_eval_markdown(tmp_path: Path):
    (tmp_path / "01-real.md").write_text(_FIXTURE, encoding="utf-8")
    (tmp_path / "README.md").write_text("# This dir holds evals\n", encoding="utf-8")
    specs = parse_evals_dir(tmp_path)
    assert len(specs) == 1
    assert specs[0].eval_id == "E7"
