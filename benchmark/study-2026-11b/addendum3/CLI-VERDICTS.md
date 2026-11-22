# Command-line verdicts on the three reruns

Addendum 3 scored the three rerun trials (t097, t099, t100) with the Gemini judge through a paid API, because the subscription CLI that addendum 2 fixed had reached its usage limit after 4 of 9 verdicts. It promised to report the CLI verdicts next to the API ones when the limit reset. The limit reset, and on 2026-11-21 `python addendum2.py judge-rerun` produced the 5 missing verdicts with the fixed command (`agy --model gemini-3.8-flash-high`). The 4 earlier ones were kept as they were. `python addendum2.py results` then added the `rerun` block to `../addendum2/results3.json`; the 9 verdict files and that file are in the hash ledger.

## Per trial (share of reference risks covered; relevance = share of table rows judged relevant)

| Trial | Yardstick 1, CLI | Yardstick 1, API | Yardstick 2, CLI | Yardstick 2, API | Relevance, CLI | Relevance, API |
|---|---|---|---|---|---|---|
| t097 | 33.3% | 33.3% | 36.4% | 36.4% | 87.5% | 87.5% |
| t099 | 50.0% | 50.0% | 62.5% | 62.5% | 33.3% | 66.7% |
| t100 | 20.0% | 30.0% | 33.3% | 33.3% | 90.0% | 70.0% |

## Effect of the sentence over the 240 trials, with the reruns in place of the three network-error trials

| Measure | CLI | API (addendum 3, `results4.json`) |
|---|---|---|
| Yardstick 1 | +10.5 points (p = .0001) | +10.5 points (p = .0001) |
| Yardstick 2 | +5.6 points (p = .0003) | +5.6 points (p = .0003) |
| Relevance | +2.8 points | +2.7 points |

The two channels give the same share in 6 of the 9 verdicts. The three that differ (one coverage verdict, two relevance verdicts) move no reported result: on the second yardstick, the one the paper reports with the reruns, the CLI and API rows are identical. The CLI values are locked by `tests/test_study_2026_11b.py::test_cli_verdicts_on_reruns_match_the_api_row`.
