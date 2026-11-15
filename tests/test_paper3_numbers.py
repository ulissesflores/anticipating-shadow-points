"""Every number ``paper/one-sentence-premortem.md`` prints from study 2, checked against the data.

Each test derives a figure from ``results.json``, ``sensitivity.json`` or ``descriptives.json``
(which ``run_all.py`` computes again from the committed answers and verdicts), formats it the way
the paper does and asserts that the paper holds that exact text.
"""

from __future__ import annotations

import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "benchmark" / "study-2026-11b"
PAPER = " ".join((ROOT / "paper" / "one-sentence-premortem.md").read_text(encoding="utf-8").split())
RESULTS = json.loads((STUDY / "results.json").read_text(encoding="utf-8"))
SENS = json.loads((STUDY / "sensitivity.json").read_text(encoding="utf-8"))
DESC = json.loads((STUDY / "descriptives.json").read_text(encoding="utf-8"))
STUDY1 = json.loads((ROOT / "benchmark" / "study-2026-11" / "results.json").read_text("utf-8"))
OPUS, SONNET = "claude-opus-5-5", "claude-sonnet-5-5"
A, B = "RED-risk", "RED-plain"


sys.path.insert(0, str(ROOT / "paper" / "tools"))
from apa_stats import p_text as P  # noqa: E402  (APA 7: "< .001" or "= .0xx", canon v1.6)


def K(x: float) -> str:
    """Return a kappa with two decimals and no zero before the decimal point, as APA 7 writes it."""
    return f"{x:.2f}".lstrip("0")


def pct(x: float, places: int = 1) -> str:
    """Format a share as a percentage, rounding halves up as the paper does.

    Parameters
    ----------
    x : float
        A share between -1 and 1.
    places : int
        Decimal places.

    Returns
    -------
    str
        For example ``"11.4"``.
    """
    q = Decimal(1).scaleb(-places)
    return str((Decimal(str(x)) * 100).quantize(q, rounding=ROUND_HALF_UP))


def exact_delta(scorer: str) -> float:
    """Return the primary statistic for one scorer, unrounded, from the scored trials.

    ``results.json`` stores it at four places; rounding that again can move the last digit.

    Parameters
    ----------
    scorer : str
        ``gemini``, ``grok`` or ``relevance``.

    Returns
    -------
    float
        Mean over the 24 strata of mean(sentence) minus mean(plain).
    """
    cells: dict = {}
    for t in RESULTS["trials"]:
        cells.setdefault((t["task"], t["model"]), {A: [], B: []})[t["condition"]].append(t[scorer])
    per = [sum(c[A]) / len(c[A]) - sum(c[B]) / len(c[B]) for c in cells.values()]
    assert len(per) == 24
    return sum(per) / len(per)


def test_primary_result():
    """46.1% to 57.5%, +11.4 points, p = 0.0001 pooled and per model, 22 of 24 strata."""
    g = RESULTS["gemini"]
    assert f"from {pct(g['overall'][B])}% to {pct(g['overall'][A])}%" in PAPER
    assert f"is {pct(g['delta_bar'])} percentage points, with p {P(g['p'])}" in PAPER
    assert (
        f"Within Claude Opus 5.5 the difference is {pct(g['by_model'][OPUS])} points and within "
        f"Claude Sonnet 5.5 it is {pct(g['by_model'][SONNET])} points, each with p < .001"
    ) in PAPER
    assert g["p_by_model"] == {OPUS: 0.0001, SONNET: 0.0001}
    assert g["positive_strata"] == 22 and g["complete_strata"] == 24
    assert "positive in 22 of the 24 strata, zero in one and negative in one" in PAPER
    deltas = [v[m]["delta"] for v in DESC["per_task"].values() for m in (OPUS, SONNET)]
    assert sum(d == 0 for d in deltas) == 1 and sum(d < 0 for d in deltas) == 1
    assert g["decision"] == "confirmed"


def test_abstract_matches_results():
    """The abstract repeats the primary numbers, the second judge and the sensitivity check."""
    g, k = RESULTS["gemini"], RESULTS["grok"]
    for text in (
        f"from {pct(g['overall'][B])}% to {pct(g['overall'][A])}%",
        f"a mean difference of {pct(g['delta_bar'])} percentage points over 24",
        f"A second judge gave +{pct(k['delta_bar'])} points",
        f"the difference is {pct(SENS['gemini']['without_strata']['delta_bar'])} points",
        f"κ = {K(DESC['judges']['kappa'])}",
    ):
        assert text in PAPER, text


def test_bootstrap_interval():
    """The unplanned bootstrap intervals: 8.9 to 14.0 pooled, 6.8 to 14.1 and 8.8 to 16.2."""
    lo, hi = DESC["bootstrap_95"]
    assert f"95% interval of {pct(lo)} to {pct(hi)} points for the pooled difference" in PAPER
    o, s = DESC["bootstrap_95_by_model"][OPUS], DESC["bootstrap_95_by_model"][SONNET]
    assert f"{pct(o[0])} to {pct(o[1])} for Opus 5.5 and {pct(s[0])} to {pct(s[1])} for" in PAPER


def test_table_by_model_and_judge():
    """Table 3: coverage by model and judge, in whole per cent."""
    rows = []
    for label, model in (("Claude Opus 5.5", OPUS), ("Claude Sonnet 5.5", SONNET), ("Both", None)):
        cells = []
        for judge in ("gemini", "grok"):
            for cond in (B, A):
                xs = [
                    t[judge]
                    for t in RESULTS["trials"]
                    if t["condition"] == cond and model in (None, t["model"])
                ]
                cells.append(pct(sum(xs) / len(xs), 0) + "%")
        rows.append(f"| {label} | " + " | ".join(cells) + " |")
    for row in rows:
        assert row in PAPER, row


def test_table_per_task():
    """Table 4: reference risks and coverage per task and model."""
    for task, v in DESC["per_task"].items():
        row = (
            f"| {task} | {DESC['reference_risks_per_task'][task]} | {pct(v[OPUS][B], 0)} | "
            f"{pct(v[OPUS][A], 0)} | {pct(v[SONNET][B], 0)} | {pct(v[SONNET][A], 0)} |"
        )
        assert row in PAPER, row
    assert sum(DESC["reference_risks_per_task"].values()) == 100
    assert "This left 100 reference risks, between 6 and 10 per task" in PAPER
    assert min(DESC["reference_risks_per_task"].values()) == 6
    assert max(DESC["reference_risks_per_task"].values()) == 10


def test_reviewer_items():
    """The three reviewers wrote 369 items in all."""
    merged = json.loads((STUDY / "lists" / "merged.json").read_text(encoding="utf-8"))
    assert sum(sum(v["n_by_reviewer"].values()) for v in merged.values()) == 369
    assert "They produced 369 items" in PAPER


def test_second_judge_and_agreement():
    """Second judge: 50.0% to 60.8%, +10.7; 93.2% of 2,000 decisions; kappa 0.86; matcher."""
    k, j, m = RESULTS["grok"], DESC["judges"], RESULTS["matcher"]
    assert f"gave {pct(k['overall'][B])}% without the sentence and {pct(k['overall'][A])}%" in PAPER
    assert f"a mean difference of {pct(k['delta_bar'])} points over the strata" in PAPER
    assert (
        f"{pct(k['by_model'][OPUS])} points within Opus 5.5 and {pct(k['by_model'][SONNET])}"
        in PAPER
    )
    assert k["positive_strata"] == 22 and k["decision"] == "confirmed"
    assert j["items"] == 2000 and pct(j["agreement"]) == "93.2"
    assert f"(Cohen, 1960), is {K(j['kappa'])}" in PAPER
    assert f"scored {pct(m['overall'][B])}% and {pct(m['overall'][A])}%" in PAPER
    w = DESC["judges_where_a_table_exists"]
    assert w["items"] == 1971 and j["items"] - w["items"] == 29
    assert (
        f"over the other 1,971 the agreement is {pct(w['agreement'])}% and κ is {K(w['kappa'])}"
        in PAPER
    )


def test_relevance():
    """Relevance: 71.1% to 73.9% where a table exists; 69.4% under the fixed rule; +4.5, p 0.011."""
    r = RESULTS["relevance"]
    w = DESC["relevance_where_a_table_exists"]
    assert w[B]["trials"] == 117 and w[A]["trials"] == 120
    assert (
        f"was {pct(w[B]['relevance'])}% without the sentence and {pct(w[A]['relevance'])}% with"
        in PAPER
    )
    assert f"the plain figure is {pct(r['overall'][B])}%" in PAPER
    assert round(exact_delta("relevance"), 4) == r["delta_bar"]
    assert f"difference of {pct(exact_delta('relevance'))} points has p {P(r['p'])}" in PAPER
    by = [P(r["p_by_model"][m]).removeprefix("= ") for m in (OPUS, SONNET)]
    assert f"({by[0]} and {by[1]})" in PAPER


def test_sensitivity_table():
    """Table 5 and the per-model figures of the most conservative row."""
    g, k, r = RESULTS["gemini"], RESULTS["grok"], RESULTS["relevance"]
    rows = [
        f"| As pre-registered (errors count zero) | 24 | +{pct(g['delta_bar'])} (p {P(g['p'])}) | "
        f"+{pct(k['delta_bar'])} (p {P(k['p'])}) | "
        f"+{pct(exact_delta('relevance'))} (p {P(r['p'])}) |"
    ]
    for label, key in (
        ("Without the three strata that hold an error", "without_strata"),
        ("Without the three trials only", "without_trials"),
    ):
        sg, sk, sr = SENS["gemini"][key], SENS["grok"][key], SENS["relevance"][key]
        rows.append(
            f"| {label} | {sg['strata']} | +{pct(sg['delta_bar'])} (p {P(sg['p'])}) | "
            f"+{pct(sk['delta_bar'])} (p {P(sk['p'])}) | "
            f"+{pct(sr['delta_bar'])} (p {P(sr['p'])}) |"
        )
    for row in rows:
        assert row in PAPER, row
    sg, sk = SENS["gemini"]["without_strata"], SENS["grok"]["without_strata"]
    assert (
        f"{pct(sg['by_model'][OPUS])} points for Opus 5.5 (p {P(sg['p_by_model'][OPUS])}) and "
        f"{pct(sg['by_model'][SONNET])} for Sonnet 5.5 (p {P(sg['p_by_model'][SONNET])}) by the "
        f"primary judge, and {pct(sk['by_model'][OPUS])} (p {P(sk['p_by_model'][OPUS])}) and "
        f"{pct(sk['by_model'][SONNET])} (p {P(sk['p_by_model'][SONNET])}) by the second"
    ) in PAPER


def test_cost_table():
    """Table 6: seconds, turns, output tokens and rows per model and condition."""
    names = {OPUS: "Claude Opus 5.5", SONNET: "Claude Sonnet 5.5", "all": "Both"}
    for model, name in names.items():
        for cond, label in ((B, "Plain"), (A, "Sentence")):
            c = DESC["costs"][cond][model]
            turns = Decimal(str(c["turns"])).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            rows = Decimal(str(c["rows"])).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            row = (
                f"| {name} | {label} | {c['seconds']} | {turns} | {c['output_tokens']:,} | {rows} |"
            )
            assert row in PAPER, row
    assert DESC["costs"][B]["all"]["trials"] == 117 and DESC["costs"][A]["all"]["trials"] == 120
    assert "117 plain trials and 120 trials with the sentence" in PAPER


def test_item_level_description():
    """Section 5.7: 52 gain, 34 tie, 14 lose; 45 and 9 at ten points; 41 to 56; 12 and 13 never."""
    s = DESC["by_item"]["summary"]
    assert (
        f"{s['gain']} reference risks were covered more often with the sentence, {s['tie']} "
        f"equally often and {s['loss']} less often"
    ) in PAPER
    assert f"{s['gain_10_points_or_more']} gained and {s['loss_10_points_or_more']} lost" in PAPER
    assert f"rose from {s['covered_in_most_plain']} to {s['covered_in_most_risk']}" in PAPER
    assert (
        f"{s['never_covered_either']} reference risks were covered by no trial in either "
        f"condition, and {s['never_covered_risk']} by no trial with the sentence"
    ) in PAPER
    items = DESC["by_item"]["items"]
    assert items["U01#1"] == {B: 0.3, A: 1.0} and "(U01, from 30% to 100% of trials)" in PAPER
    assert items["U07#4"] == {B: 0.3, A: 0.9} and "(U07, from 30% to 90%)" in PAPER
    assert items["U09#6"] == {B: 0.2, A: 0.9} and "(U09, from 20% to 90%)" in PAPER


def test_originating_study_table():
    """Table 1 repeats the 2026-11 study: 56/66/48 and 57/70/54 per cent."""
    g, k = STUDY1["gemini"]["overall"], STUDY1["grok"]["overall"]
    for cond, label in (
        ("RED-plain", "Plain request"),
        ("RED-risk", "Plain request plus the sentence"),
        ("GREEN", "ASP protocol (13 phases)"),
    ):
        assert f"| {label} | {pct(g[cond], 0)}% | {pct(k[cond], 0)}% |" in PAPER


def test_no_priority_claim():
    """The paper never says "first"; novelty is stated as "to our knowledge"."""
    lowered = PAPER.lower()
    for phrase in ("the first study", "first to ", "we are the first", "for the first time"):
        assert phrase not in lowered
    assert "To our knowledge, no prior study measures" in PAPER


def test_permutation_null_and_full_tables():
    """No shuffle reaches the observed difference; the largest gives 5.9; full tables give 11.3."""
    null = DESC["null"]
    assert null["hits"] == 0 and null["relabellings"] == 10000
    assert null["observed"] == RESULTS["gemini"]["delta_bar"]
    assert f"the largest gave {pct(null['largest_shuffled'])} points" in PAPER
    full = DESC["full_tables_only"]
    assert (
        f"{full['trials'][B]} plain and {full['trials'][A]} with the sentence, leaves the "
        f"difference at {pct(full['delta_bar'])} points over the {full['strata']} strata"
    ) in PAPER


def test_roles_and_redaction():
    """Table 4: whose wording the reference risks carry; 12 words replaced in 10 tables."""
    assert DESC["wording_origin"] == {"gemini": 91, "gptoss": 9, "grok": 0}
    assert "| Gemini 3.8 Flash | yes | yes | primary judge | yes | 91 |" in PAPER
    assert "| GPT-OSS 120B | yes | no | no | no | 9 |" in PAPER
    assert "| Grok | yes | no | second judge | no | 0 |" in PAPER
    hits = [
        json.loads(f.read_text())["redactions"] for f in (STUDY / "judge" / "gemini").glob("*.json")
    ]
    assert sum(hits) == 12 and sum(h > 0 for h in hits) == 10
    assert "it changed 12 words in 10 of the 240 tables here" in PAPER
    runs = [json.loads(x) for x in (STUDY / "runs" / "trials.jsonl").read_text().splitlines()]
    assert {len(r["plugins"]) for r in runs} == {4}
    assert "the four plugins built into Claude Code stayed on in every trial" in PAPER


def test_integrity_record():
    """Table 3 quotes the two stamped ledger heads and the commits of each sealed event."""
    for name in ("pretrial-head.txt", "analysis-head.txt"):
        head = (STUDY / name).read_text().split()[-1]
        assert f"`{head[:8]}…{head[-8:]}`" in PAPER
    for commit in ("eb1a447", "fe18438", "e046f36", "67b52d0", "e8c73c1"):
        assert f"Commit `{commit}`" in PAPER
    # one Bitcoin attestation of each proof, as listed by `ots info <head>.ots`
    for block in ("975226", "975820"):
        assert f"anchored in Bitcoin block {block}" in PAPER


def test_example_list_in_appendix():
    """Table B1: coverage of the six reference risks of U08 per condition."""
    raw = (ROOT / "paper" / "one-sentence-premortem.md").read_text(encoding="utf-8")
    table = raw.split("**Table B1.**")[1]
    rows = [ln for ln in table.splitlines() if ln[:4] in {f"| {i} " for i in "123456"}]
    assert len(rows) == 6
    for i, row in enumerate(rows, 1):
        item = DESC["by_item"]["items"][f"U08#{i}"]
        assert row.rstrip().endswith(f"| {pct(item[B], 0)}% | {pct(item[A], 0)}% |"), row


def test_every_paragraph_cites_a_source():
    """Each body paragraph names a source: (Author, year), a table, figure, section or appendix."""
    raw = (ROOT / "paper" / "one-sentence-premortem.md").read_text(encoding="utf-8")
    body = raw.split("## 1. Introduction")[1].split("## References")[0]
    source = re.compile(
        r"\(\d{4}[ab]?[,)]|, \d{4}[ab]?[;),]|\bTables? [0-9AB]|\bFigures? \d|\bSection \d"
        r"|Appendix [AB]"
    )
    bare = []
    for block in re.split(r"\n\s*\n", body):
        text = block.strip()
        if not text or text.startswith(
            (
                "#",
                "|",
                "![",
                "---",
                "**Table",
                "*Note.*",
                "**Funding.**",
                "**Author contribution.**",
            )
        ):
            continue
        if len(text.split()) >= 12 and not source.search(text):
            bare.append(text[:90])
    assert not bare, bare


def test_checks_raised_by_the_outside_pre_mortem():
    """Plan-file writing by condition, reviewers per risk, and the opposite bound for errors."""
    plan = DESC["plan_file"]
    wrote = plan["trials_that_wrote_a_plan_file"]
    assert wrote[OPUS] == {B: 59, A: 22} and wrote[SONNET] == {B: 0, A: 0}
    assert "in 59 of the 60 plain trials and in 22 of the 60 trials with the sentence" in PAPER
    assert (
        f"the difference is {pct(plan['among_those']['delta_bar'])} points over the "
        f"{plan['among_those']['strata']} strata where both conditions remain"
    ) in PAPER
    assert DESC["reviewers_per_risk"] == {"3": 31, "2": 69}
    assert "31 were named by all three reviewers and 69 by two" in PAPER
    bound = DESC["errors_as_full_coverage"]
    assert (
        f"the difference is {pct(bound['gemini'])} points by the primary judge and "
        f"{pct(bound['grok'])} by the second"
    ) in PAPER


def test_second_yardstick():
    """Section 5.8 and Table 9: the exploratory check against differently worded lists."""
    y2 = json.loads((STUDY / "yardstick2" / "results2.json").read_text())
    g, sizes = y2["gemini"], y2["reference_risks_per_task"]
    plain, risk = pct(g["overall"][B]), pct(g["overall"][A])
    delta = pct(g["delta_bar"])
    assert "grok" not in y2  # the second judge's verdicts are incomplete and not reported
    assert (
        f"| 111 | {plain}% | {risk}% | +{delta} | {P(g['p'])} | {g['positive_strata']} of 24 |"
        in PAPER
    )
    assert sum(sizes.values()) == 111 and (min(sizes.values()), max(sizes.values())) == (7, 11)
    assert f"{pct(g['by_model'][OPUS])} on Opus (p {P(g['p_by_model'][OPUS])})" in PAPER
    assert f"{pct(g['by_model'][SONNET])} on Sonnet (p {P(g['p_by_model'][SONNET])})" in PAPER
    assert "16 are positive, 2 are zero and 6 are negative" in PAPER
    assert y2["wording_origin"] == {"gemini": 98, "gptoss": 13, "grok": 0}
    assert "98 of the 111 reference risks" in PAPER
    assert delta == "6.7" and PAPER.count("6.7 points") >= 5
    assert len(list((STUDY / "yardstick2" / "judge" / "gemini").glob("t*.json"))) == 240
    # the unplanned checks a blind reviewer asked for (round 2), recomputed by sensitivity2.py
    s2 = json.loads((STUDY / "yardstick2" / "sensitivity2.json").read_text())["gemini"]
    assert s2["fixed_rule"]["delta_bar"] == g["delta_bar"] and s2["fixed_rule"]["p"] == g["p"]
    ws, wt, full = s2["without_strata"], s2["without_trials"], s2["errors_as_full_coverage"]
    assert f"the difference is {pct(ws['delta_bar'])} points (p {P(ws['p'])})" in PAPER
    assert f"without the three trials it is {pct(wt['delta_bar'])} (p {P(wt['p'])})" in PAPER
    assert f"it is {pct(full['delta_bar'])} points (p {P(full['p'])})" in PAPER
    assert (
        f"{pct(full['by_model'][SONNET])} on Sonnet 5.5 (p {P(full['p_by_model'][SONNET])})"
        in PAPER
    )
    assert pct(full["by_model"][OPUS]) == "3.2" and full["p_by_model"][OPUS] == 0.0994
    assert "3.2 on Opus 5.5, where it is no longer significant (p = .099)" in PAPER
    low, high = (pct(v) for v in s2["bootstrap_95"])
    assert f"second difference is {low} to {high} points" in PAPER
    low, high = (pct(v) for v in s2["task_bootstrap_95"])
    assert PAPER.count(f"{low} to {high}") == 2
    first = json.loads((STUDY / "yardstick2" / "sensitivity2.json").read_text())["original"]
    low, high = (pct(v) for v in first["task_bootstrap_95"])
    assert PAPER.count(f"{low} to {high}") == 2
    assert (
        first["bootstrap_95"]
        == json.loads((STUDY / "descriptives.json").read_text())["bootstrap_95"]
    )


def test_rerun_and_third_judge():
    """Sections 5.5 and 5.8 and Table 10: the unplanned rerun, the third judge, the API channel."""
    a = json.loads((STUDY / "addendum2" / "results3.json").read_text())["astra"]
    r = json.loads((STUDY / "addendum3" / "results4.json").read_text())
    s2 = json.loads((STUDY / "yardstick2" / "sensitivity2.json").read_text())["gemini"]

    def row(x: dict) -> str:
        p = [x["p"], x["p_by_model"][OPUS], x["p_by_model"][SONNET]]
        d = [x["delta_bar"], x["by_model"][OPUS], x["by_model"][SONNET]]
        return " | ".join(f"+{pct(v)} (p {P(q)})" for v, q in zip(d, p, strict=True))

    full = dict(s2["errors_as_full_coverage"])
    full["p_by_model"] = {OPUS: 0.099, SONNET: full["p_by_model"][SONNET]}
    for label, x in (
        ("Count zero, as fixed in advance | Gemini 3.8 Flash", s2["fixed_rule"]),
        ("Count zero, as fixed in advance | GPT-6 Astra", a["yardstick2_fixed_rule"]),
        ("Scored as full coverage | Gemini 3.8 Flash", full),
        ("Scored as full coverage | GPT-6 Astra", a["yardstick2_errors_as_full_coverage"]),
        ("Run once more | Gemini 3.8 Flash, by API", r["yardstick2_with_reruns"]),
        ("Run once more | GPT-6 Astra", a["yardstick2_with_reruns"]),
    ):
        assert f"| {label} | {row(x)} |" in PAPER, label
    fx = a["yardstick2_fixed_rule"]
    plain, risk = pct(fx["overall"][B]), pct(fx["overall"][A])
    assert f"from {plain}% to {risk}%, with {fx['positive_strata']} of 24" in PAPER
    k = a["agreement_with_gemini"]
    assert (
        f"{pct(k['agreement'])}% of 2,192 single decisions (Cohen's κ = {K(k['kappa'])})" in PAPER
    )
    assert k["items"] == 2192
    assert f"{pct(k['covered_second'])}% against {pct(k['covered_first'])}%" in PAPER
    y1 = r["yardstick1_with_reruns"]
    assert (
        f"is {pct(y1['delta_bar'])} points (p {P(y1['p'])}): "
        f"{pct(y1['by_model'][OPUS])} on Opus 5.5 and {pct(y1['by_model'][SONNET])} on Sonnet 5.5"
    ) in PAPER
    c = r["channel_check"]
    ci = c["items"]
    assert f"{pct(ci['agreement'])}% of {ci['items']} decisions (κ = {K(ci['kappa'])})" in PAPER
    assert f"{pct(c['mean_coverage_api'])}% against {pct(c['mean_coverage_cli'])}%" in PAPER
    assert len(c["trials"]) == 30
    assert (
        len(list((STUDY / "addendum2" / "astra" / "yardstick2" / "astra").glob("t*.json"))) == 240
    )
    assert len(list((STUDY / "addendum3" / "openrouter" / "rerun").glob("*/t*.json"))) == 9


def test_groups_left_out_by_the_merge():
    """Objection 2: how many merged groups only one reviewer named, on each yardstick."""
    import sys

    sys.path.insert(0, str(STUDY))
    from judge import first_json

    for folder, text in (
        (STUDY / "judge" / "merge", "132 of the 232 groups"),
        (STUDY / "yardstick2" / "judge" / "merge", "102 of the 213"),
    ):
        groups = [
            g
            for f in sorted(folder.glob("*.raw.txt"))
            for g in first_json(f.read_text(encoding="utf-8"))["groups"]
        ]
        single = sum(len({k[0] for k in g}) < 2 for g in groups)
        assert f"{single} of the {len(groups)}" in text and text in PAPER
