---
title: "עברית"
layout: default
parent: Translations
nav_order: 4
---

<div dir="rtl" markdown="1">

<div align="center" markdown="1">

<img src="../assets/icon.svg" width="96" alt="סמל ASP: שמש נמוכה בצבע ענבר המטילה צל ארוך מעל האופק">

# ASP — Anticipating Shadow Points

**תוסף ל-Claude Code שגורם לסוכן לכתוב את ה-post-mortem לפני שהוא כותב את הקוד, ושכבת שכפול שגוזרת מחדש כל מספר שאנחנו מפרסמים עליו.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20276631.svg)](https://doi.org/10.5281/zenodo.20276631)
[![Code: MIT](https://img.shields.io/badge/code-MIT-yellow.svg)](../LICENSE)
[![Papers and data: CC BY 4.0](https://img.shields.io/badge/papers%20%26%20data-CC%20BY%204.0-lightgrey.svg)](../LICENSES/CC-BY-4.0.txt)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](../pyproject.toml)
[![tests](https://img.shields.io/badge/tests-49_passing-brightgreen.svg)](../tests/)
[![reproducible](https://img.shields.io/badge/reproducible-SHA--256_chain-blueviolet.svg)](../output/hash-chain.md)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-orange.svg)](#install)

[English](../README.md) · [Português (BR)](README.pt.md) · [Español](README.es.md) · [Italiano](README.it.md) · עברית (קובץ זה)

*תורגם מה-README האנגלי של גרסה v2.0.0; הקובץ האנגלי הוא הקנוני. תרגום בסיוע מכונה; סקירה של דוברי עברית שפת אם תתקבל בברכה.*

</div>

> [!IMPORTANT]
> **ממצא (Iron Law 11).** הפקודה `claude -p` מחזירה exit code 0 כאשר הסוכן מסרב בנימוס לבצע את המשימה, בלי שום דגל סירוב קריא-מכונה במעטפת ה-JSON. על סט קבוע של 50 הנחיות שנועדו לעורר סירוב (Claude Code 2.1.200, יולי 2026), **24 מתוך 50 הסתיימו ב-0, כולם עם `stop_reason: end_turn`**, ו-**12 עד 20 מהם היו סירובים**: 24% עד 40% מהסט, בהתאם לאופן שבו סופרים סירוב. עטיפת shell שסומכת על `$?` קוראת את כולם כהצלחה.
>
> **טרם נמדד: האם ASP משפר תוכניות.** המחבר צפה בכך ללא עיוורון בחמש משימות במאי 2026, והתמלילים ההם לא נשמרו. הנתון "80% מול 4%" בגרסאות קודמות נבע מניקוד של fixtures שהמחבר כתב כדי לבדוק את ה-matcher, ולא מפלטים של מודלים; הוא נמשך כראיה. בנצ'מארק אמיתי שנרשם מראש [מתוכנן](../PREREGISTRATION.md).

מאמרים: [*ASP: an operational pre-mortem skill for LLM coding agents*](../paper/asp-preprint.md) ([PDF](../paper/asp-preprint.pdf)) · [*Graceful refusals as unsignalled failures*](../paper/iron-law-11.md) ([PDF](../paper/iron-law-11.pdf)). שניהם דוחות טכניים שלא עברו ביקורת עמיתים.

## מה הפרויקט תורם

1. **פרוטוקול תכנון שאפשר להתקין.** שלושה עשר שלבים: מחקר, pre-mortem של Klein שנאלץ לעבור דרך 14 מצבי הכשל של MAST למערכות מרובות סוכנים, תת-סוכן מאמת עצמאי, חוזה של משימות עם בדיקות קבלה, ואישור סופי של התוצרים. שנים עשר "Iron Laws" מונעים מהסוכן לדלג על שלבים.
2. **כשל שנמדד בדפוס נפוץ של harness.** `claude -p` יוצא עם 0 בסירוב מנומס. המדידה, ארבע הקריאות שלה ומתכון לפענוח הגנתי נמצאים ב-[`paper/iron-law-11.md`](../paper/iron-law-11.md); המתכון מובנה בשלב הביצוע של ה-skill.
3. **כל מספר שפורסם כבדיקה.** `python run_all.py` גוזר מחדש את המספרים מנתונים שב-commit, מאמת (assert) כל אחד מהם, ואוטם קוד, בדיקות, נתונים ותוצאות תחת chain hash אחד של SHA-256.

## במבט מהיר

| | |
|---|---|
| מה זה | תוסף ל-Claude Code (skill + פקודת `/asp`), בתוספת שכבת שכפול ב-Python |
| התקנה | `claude plugin marketplace add ulissesflores/anticipating-shadow-points` |
| דרישות זמן ריצה | Claude Code, `bash`, `jq` |
| דרישות שכפול | Python 3.11+, `matplotlib`, `pytest`; ללא קריאות למודל, כ-10 שניות |
| ראיות | 2 × 50 תמלילי `claude -p` (מאי ויולי 2026); עדיין אין תמלילים שנשמרו עבור אפקט ה-ASP |
| הרשאות | ה-skill לעולם אינו קובע מצב הרשאות; סשן-הבן שהוא מפעיל רץ תחת ההגדרות שלך |

## ראו זאת

| שכפול כל מספר במצב לא מקוון | הכשל, מתוך ראיות מוקלטות |
|---|---|
| ![run_all.py גוזר מחדש את התוצאות, מריץ את הבדיקות ומאמת את חותם ה-SHA-256](../assets/demo/replicate.gif) | ![ניסוי מוקלט מיולי 2026: הסוכן מסרב, ה-exit code הוא 0, ה-stop_reason הוא end_turn](../assets/demo/exit-code.gif) |

שתי ההקלטות הן השמעות חוזרות של קבצים שב-commit, מתוסרטות באמצעות [vhs](https://github.com/charmbracelet/vhs) ב-[`assets/demo/`](../assets/demo/). אף אחת מהן אינה קוראת למודל.

## התחלה מהירה

### שימוש בתוסף

<div dir="ltr" markdown="1">

```bash
claude plugin marketplace add ulissesflores/anticipating-shadow-points
claude plugin install anticipating-shadow-points@anticipating-shadow-points
```

</div>

לאחר מכן, בכל סשן של Claude Code: `/anticipating-shadow-points:asp <your task>`. דגלי עומק: `--quick` (ללא validator, ללא ביצוע אוטונומי), `--standard` (ברירת מחדל), `--paranoid`.

### שכפול המאמרים

<div dir="ltr" markdown="1">

```bash
git clone https://github.com/ulissesflores/anticipating-shadow-points
cd anticipating-shadow-points
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python run_all.py
```

</div>

פלט צפוי:

<div dir="ltr" markdown="1">

```text
== results: analysis/results.py
results -> output/results.json | July author 20/50, codebook 19/50, detector 9/50
== figures: analysis/make_figures.py
figures -> output/figures (3 x PNG+SVG)
== tests: -m pytest -q tests
.............                                                            [100%]
== provenance: make_provenance.py
provenance written: chain_hash <64 hex characters>
== verify: make_provenance.py --verify
provenance verified: chain_hash <the same 64 hex characters>
run_all OK: results reproduced, tests passed, provenance verified
```

</div>

## תוצאות

### Iron Law 11: ה-exit code של `claude -p` בסירוב מנומס

| צילום מצב | CLI | המודל שענה | Exit 0 | סירובים עם exit 0 | קריאה |
|---|---|---|---|---|---|
| 2026-05-18 | 2.1.143 | Opus 4.7 | 36/50 | **30/50 (60%)** | גלאי ביטויים נעול |
| 2026-07-08 | 2.1.200 | Fable 5 (34), Opus 4.8 (16, כולל את כל 12 הנחיות הבטיחות) | 24/50 | **9/50 (18%)** | אותו גלאי ביטויים נעול |
| | | | | **12/50 (24%)** | סירובים חד-משמעיים בלבד |
| | | | | **19/50 (38%)** | רוב של 5 מדרגים עיוורים, codebook |
| | | | | **20/50 (40%)** | התיוג של המחבר |

![קריאות של סירוב שקט עם רווחי Wilson של 95%](../output/figures/fig1_silent_refusal_readings.png)

הרצות מאי ויולי נבדלות במודל וב-CLI, ולכן הירידה מ-60% ל-18% תחת אותו גלאי היא שינוי של מושא המדידה, לא מגמה. ביולי, כל אחד מ-24 ניסויי ה-exit 0 נשא `stop_reason: end_turn`; ה-`stop_reason: refusal` היחיד היה חסימה בצד השרת, והוא יצא עם 1.

### השפעת ASP על תוכניות: טרם נמדדה

| ראיה | מהי | מה היא תומכת בו |
|---|---|---|
| קריאת המחבר ב-10 תוכניות של תת-סוכנים, 2026-05-17 ([סיכום](../tests/evals-summary.md)) | שיפוט ללא עיוורון מול רשימות שהמחבר כתב; RED קרוב ל-47%, GREEN קרוב ל-100%; התמלילים לא נשמרו | תצפית, לא מדידה |
| הרצת בנצ'מארק מדומה (mock), 2026-05-18 | ה-matcher הדטרמיניסטי מנקד fixtures שהמחבר כתב כדי להפעיל אותו: RED 4%, GREEN 80% | שום דבר לגבי ASP. היא מראה שה-matcher מבחין בין משימות: 80% על הרשימה של ה-fixture עצמו, 0.5% על הרשימות של משימות אחרות |

![בדיקת כלי המדידה על ה-fixtures שנבנו](../output/figures/fig2_adjudicator_fixture_check.png)

## מה נטען ומה לא

| | |
|---|---|
| **נטען** | `claude -p` יצא עם 0 ועם `stop_reason: end_turn` בסירובים מנומסים בשני צילומי מצב מתוארכים; הספירות לעיל נובעות באופן דטרמיניסטי מהתמלילים שב-commit; ה-matcher שנשלח מבחין בין משימות על fixtures שנבנו |
| **לא נטען** | שיעור בסיס של כשל שקט בתעבורת סוכנים אמיתית (הסט נבנה כדי לעורר סירובים); שהירידה מ-60% ל-18% היא מגמה; ש-ASP משפר תוכניות או תוצאות בעולם האמיתי (לא נמדד על פלט מודל שנשמר); שציוני ה-fixtures 80%/4% אומרים משהו על ASP |
| **קפוא** | התמלילים. המודלים שהפיקו אותם אינם מקובעים (pinned) ולא ניתן לשאול אותם שוב; הרצה מחדש של ההנחיות נותנת צילום מצב חדש, לא שכפול |
| **תוקן בגרסה זו** | טקסט קודם ייחס את ריצת יולי ל-"Opus 4.8"; המעטפות מראות ש-Fable 5 היה מודל הסשן, ו-Opus 4.8 ענה על 16 ניסויים. טקסט קודם השווה את ספירת הגלאי של מאי (60%) עם הספירה הידנית של יולי (40%); ההשוואה התואמת (like-for-like) היא 60% מול 18%. גרסאות קודמות הציגו את ציוני ה-matcher על fixtures שהמחבר כתב (80% מול 4%) כקריאה של עשרה תמלילי מודל; הריצה היא ריצה מדומה (mock), והטענה נמשכה. כותרת ההפניה ל-GitHub issue #15685 הומצאה, וכעת מופיעה הכותרת האמיתית. התווית "נרשם מראש" (pre-registered) על ריצת מאי נמשכה ביולי 2026 |

שיטה מלאה ומגבלות: [`REPRODUCIBILITY.md`](../REPRODUCIBILITY.md). המדידה הבאה מתוכננת ב-[`PREREGISTRATION.md`](../PREREGISTRATION.md) (טיוטה, טרם הופקדה).

## שלמות

`output/hash-chain.md` מחזיק `chain_hash` אחד של SHA-256 על פני חמישה עלים: קוד, בדיקות, קלטים קפואים, נתונים ותוצאות נגזרות. כדי לוודא שדבר לא השתנה מאז שנאטם:

<div dir="ltr" markdown="1">

```bash
python3 make_provenance.py --verify
```

</div>

הוא דורש רק את הספרייה הסטנדרטית. ה-CI מריץ אותו לפני התקנת כל דבר, ואז מריץ את `run_all.py` על Python 3.11 ו-3.12.

<a id="install"></a>

## התקנה

| נתיב | פקודה | הפעלה |
|---|---|---|
| Plugin marketplace (מומלץ) | `claude plugin marketplace add ulissesflores/anticipating-shadow-points` ואז `claude plugin install anticipating-shadow-points@anticipating-shadow-points` | `/anticipating-shadow-points:asp` |
| לסשן הנוכחי בלבד, מתוך clone | `claude --plugin-dir /path/to/anticipating-shadow-points` | `/anticipating-shadow-points:asp` |
| סקריפט עצמאי | `./scripts/verify.sh --pre-install && ./scripts/install.sh` | `/asp` |

<details markdown="1">
<summary><b>פתרון תקלות</b></summary>

- **`claude plugin install` נכשל עם SSH permission denied.** ה-git שלך משכתב כתובות GitHub ל-SSH ואין לך מפתח רשום. תיקון חד-פעמי: `git config --global url."https://github.com/".insteadOf "git@github.com:"`.
- **`/asp` עובד אבל `/anticipating-shadow-points:asp` לא, או להפך.** הם מגיעים מנתיבי התקנה שונים (עצמאי מול תוסף) ויכולים להתקיים יחד.
- **שם התוסף מופיע פעמיים (`name@marketplace`).** המאגר הוא ה-marketplace של עצמו, ולכן שני החלקים הם אותה מחרוזת.
- **השלב האוטונומי נעצר בגלל דחיית הרשאה.** כמתוכנן. ASP אינו מעביר שום דגל הרשאה לתהליך-הבן `claude -p`; כל מה שההגדרות שלך אינן מתירות כבר נדחה במצב לא-אינטראקטיבי, וה-skill מדווח על כך במקום לנסות שוב עם יותר הרשאה.

</details>

### מתי להשתמש ב-ASP

השתמשו בו עבור מיגרציות, deploys עם תלויות חיצוניות, refactors על פני קבצים רבים, שינויים במדיניות גישה, החלטות ארכיטקטורה וחקירות root-cause. דלגו עליו בתיקוני typo, עריכות של שורה אחת ושאלות לקריאה בלבד.

## מבנה המאגר

<div dir="ltr" markdown="1">

```text
.claude-plugin/        plugin and marketplace manifests
skills/                the ASP skill: protocol, Iron Laws, templates, 5 evals
commands/              /asp command
paper/                 the two papers (Markdown source + PDF)
analysis/              derivation of every published number, figures, redacted extractor
data/                  July 2026 redacted extract, labels, codebook
tests/                 paper-number and determinism tests; iron-law-11/ holds the May 2026 run
benchmark/             RED/GREEN benchmark package and its committed May 2026 run
output/                results.json, hash-chain.md, provenance.json, figures/
assets/                icon, demo GIFs and their vhs scripts
docs/                  architecture notes and translations
run_all.py             single entry point: results -> figures -> tests -> seal -> verify
make_provenance.py     build or --verify the SHA-256 chain
```

</div>

לקריאה נוספת: [ארכיטקטורה והיסטוריית העיצוב](ARCHITECTURE.md) · [ה-skill ו-12 ה-Iron Laws שלו](../skills/anticipating-shadow-points/SKILL.md) · [5 ההערכות](../skills/anticipating-shadow-points/evals/) · [תרומה לפרויקט](../CONTRIBUTING.md) · [מדיניות אבטחה](../SECURITY.md) · [יומן שינויים](../CHANGELOG.md) · [מפת דרכים](../ROADMAP.md).

## מחבר

**Carlos Ulisses Flores** — CTO וחוקר ראשי, Codex Hash Research Laboratory, סאו פאולו, ברזיל · תואר שני (MSc) בבינה מלאכותית (בתהליך), American Global Tech University.

[![ORCID](https://img.shields.io/badge/ORCID-0000--0002--6034--7765-a6ce39.svg)](https://orcid.org/0000-0002-6034-7765)
[![Website](https://img.shields.io/badge/web-ulissesflores.com-black.svg)](https://ulissesflores.com)
[![Lattes](https://img.shields.io/badge/Lattes-6905246706890561-blue.svg)](http://lattes.cnpq.br/6905246706890561)

סינתזת המחקר, הניסוח וסקריפטי האימות הופקו עם Claude (Anthropic) בהנחיית המחבר; כל מספר במאמרים נגזר על ידי קוד במאגר זה. ראו [`AUTHORS`](../AUTHORS).

## ציטוט

ציטטו את ה-**concept DOI** כדי להפנות ל-ASP באופן כללי; הוא תמיד מפנה לגרסה האחרונה. ציטטו **version DOI** כדי לקבע את הקבצים המדויקים שבהם השתמשתם. ה-version DOI של v2.0.0 נוצר בעת ההוצאה (release) ויופיע כאן וב-[`CITATION.cff`](../CITATION.cff).

<div dir="ltr" markdown="1">

```bibtex
@software{flores_asp_2026,
  author    = {Flores, Carlos Ulisses},
  title     = {{ASP — Anticipating Shadow Points}},
  year      = {2026},
  version   = {2.0.0},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.20276631},
  url       = {https://doi.org/10.5281/zenodo.20276631}
}
```

</div>

כפתור "Cite this repository" של GitHub קורא את [`CITATION.cff`](../CITATION.cff), שמפרט גם את ההפניות המתודולוגיות שיש לצטט לצד ASP.

## רישיון

הקוד תחת [MIT](../LICENSE). המאמרים, האיורים, הנתונים והטקסט תחת [CC BY 4.0](../LICENSES/CC-BY-4.0.txt). המיפוי קובץ-אחר-קובץ נמצא ב-[`NOTICE`](../NOTICE).

## הפניות עוגן

- Klein, G. (2007). Performing a project premortem. *Harvard Business Review*, 85(9), 18–19.
- Mitchell, D. J., Russo, J. E., & Pennington, N. (1989). Back to the future: Temporal perspective in the explanation of events. *Journal of Behavioral Decision Making*, 2(1), 25–38. https://doi.org/10.1002/bdm.3960020103
- Cemri, M., et al. (2025). *Why do multi-agent LLM systems fail?* arXiv:2503.13657. https://arxiv.org/abs/2503.13657
- Avizienis, A., Laprie, J.-C., Randell, B., & Landwehr, C. (2004). Basic concepts and taxonomy of dependable and secure computing. *IEEE TDSC*, 1(1), 11–33. https://doi.org/10.1109/TDSC.2004.2
- Huang, J., et al. (2024). Large language models cannot self-correct reasoning yet. *ICLR 2024*. https://arxiv.org/abs/2310.01798

</div>
