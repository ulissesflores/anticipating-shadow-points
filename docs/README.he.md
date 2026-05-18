---
title: "עברית"
layout: default
parent: Translations
nav_order: 4
---

<div dir="rtl">

# ASP — Anticipating Shadow Points (חיזוי נקודות-צל)

> **Skill עבור Claude Code שהופך משימות שאפתניות לתוצרים שנשלחו — באמצעות מחקר מקדים חובה, גילוי pre-mortem של "shadow points", תוכניות שעוברות תיקוף על-ידי סוכן עצמאי, מיקרו-TODO חוזיים וביצוע אוטונומי דרך `/goal`.**

[🇬🇧 English](../README.md) · [🇪🇸 Español](README.es.md) · [🇧🇷 Português](README.pt.md) · [🇮🇹 Italiano](README.it.md) · 🇮🇱 עברית (קובץ זה)

📐 **[ARCHITECTURE.md](ARCHITECTURE.md)** — מסמך מלא של state-of-the-art: רקע אקדמי, מסע v1→v5, גילויים אמפיריים (כולל Iron Law 11), תרומות user/advisor, גזירת 12 Iron Laws.

> תרגום בעזרת AI — ביקורת מקומית מתקבלת בברכה דרך PR.

---

## מה זה ASP?

**ASP** מקיצור **Ant-Shadow-Point** — נקודות הכשל הקטנות והנשכחות שמסתתרות בצללים של כל משימה לא טריוויאלית ומופיעות מאוחר יותר כ-bugs, תקריות או PRs שנדחו.

מופעל ב-`/asp <המשימה שלך>`, skill זה מתזמר פרוטוקול בן 13 שלבים שמבצע:

1. **שואל את השאלות הנכונות** (≤3 לפני המחקר, ≤3 אחרי).
2. **חוקר במקביל** (codebase + web + שיעורים קודמים).
3. **עורך pre-mortem לכישלון** (Klein 1998 + טקסונומיית MAST של ברקלי, 14 מצבים).
4. **מתקף עם סוכן עצמאי** (prompt נפרד — בלי קנוניית ביקורת עצמית).
5. **מבצע דרך `/goal`** (הפרדת worker/evaluator מקורית של Anthropic, שוחררה 2026-05-12).
6. **מקבל לפי תוצר** ואז כותב לקחים לזיכרון מתמיד.

---

## למה להשתמש ב-ASP?

אם פעם שלחת משהו ו-24 שעות אחר כך חשבת *"למה לא חשבתי על זה?"*, ASP הוא בשבילך.

**ASP מתאים ל:**
- Features שנוגעות בנתונים או במצב משותף
- Refactors על קבצים רבים
- Migrations (schema, dependency, API)
- Deploys עם תלויות חיצוניות
- החלטות ארכיטקטורה
- חקירות debug שדורשות משמעת של root-cause

---

## Quick Start

```bash
git clone https://github.com/ulissesflores/anticipating-shadow-points.git ~/Developer/ASP
cd ~/Developer/ASP
./scripts/verify.sh --pre-install
./scripts/install.sh --dry-run
./scripts/install.sh
```

הפעלה:

```
/asp הוסף עמודה `tier` (NOT NULL, default 'free') ב-user_profiles. בטבלה יש 1M שורות.
```

הסרה:

```bash
./scripts/uninstall.sh
```

---

## מקרי שימוש (דוגמאות)

תרחישים קונקרטיים בהם ASP זוהר. כל אחד מגיע מ-5 ה-evals המובנים שמלווים את ה-skill (`skills/anticipating-shadow-points/evals/`).

### 1. Migration של schema על טבלה בפרודקשן
> *"הוסף עמודת NOT NULL `tier` (default 'free') ב-`user_profiles`. הטבלה כוללת כ-1M שורות בפרודקשן."*

ASP מאלץ בדיקה מוקדמת של: RLS policies, אסטרטגיית backfill + lock contention, replica lag במהלך DDL, סדר deploy של app מול migration, אינטראקציה עם triggers, locks ב-cascade דרך FK, תוכנית rollback, ספייק של monitoring, חלון downtime, רענון schema cache של PostgREST.

### 2. Refactor של util בשימוש בקבצים רבים
> *"בצע refactor ל-`formatDate(d: Date): string` שיקבל timezone אופציונלי. בשימוש ב-30 קבצים."*

ASP חושף: סמנטיקת חוזה API, השלכות locale/i18n, enumeration של callsites דרך `ts-morph` (לא grep), בדיקות DST boundary, תקופת deprecation, אסטרטגיית branches, dependency graph טרנזיטיבי.

### 3. Deploy של edge function עם תלות חיצונית
> *"Deploy edge function `notify-on-signup` שקורא ל-Resend (rate limit 100 req/sec)."*

ASP מאלץ עיצוב מוקדם של: `RESEND_API_KEY` ב-`supabase secrets`, backoff דרך outbox pattern, idempotency keys, cold-start timeout, observability מובנית, היוריסטיקות anti-bot, deliverability (SPF/DKIM/DMARC).

### 4. שינוי RLS policy המתייחס לעמודה חדשה
> *"עדכן RLS של `user_profiles` כך שמשתמשים יראו רק שורות עם אותו tier."*

ASP תופס: עמימות spec, רקורסיה self-reference, פגיעות self-promotion, `FORCE ROW LEVEL SECURITY`, טרנזקציה אטומית, helper `SECURITY DEFINER` עם `search_path` קבוע.

### 5. Cron שעלול להתנגש עם שירותים מבוטלים
האינטגרציה `recall.py` של Phase 1 חושפת זיכרון של תקלה קודמת. ב-eval האמפירי, ה-validator subagent **סירב לבצע** כשגילה שה-path של הסקריפט תואם לשירות שבוטל בעבר.

### 6. החלטת ארכיטקטורה cross-team
Phase 3 (Project Charter) + Phase 4 (Deliverables Register עם אישור per-deliverable + owners) מבטל את "חשבתי שזה שלך".

---

## איך זה עובד — 13 השלבים

| # | שלב | פלט |
|---|---|---|
| 0a | שאלות לפני מחקר (≤3) | Intake |
| 1 | מחקר מקבילי | סיכום |
| 0b | שאלות אחרי מחקר (≤3, ניתן לדלג) | Intake מעודן |
| 2 | זיהוי Shadow Points (Klein + MAST 14) | רשימה + מיתון |
| 3 | Project Charter | Charter ממולא |
| 4 | Macro Plan + Deliverables Register | תוצרים D01..Dn |
| 5 | Validator עצמאי | APPROVE / REVISE |
| 6 | לולאה פנימית cap=3 + advisor() אופציונלי | תוכנית סופית |
| 7 | משתמש מאשר 3 ארטיפקטים | Go/No-Go |
| 8 | Micro-TODO חוזי + Goal Spec | N tasks + completion condition |
| 9 | ביצוע דרך `/goal` | Tasks completed עם הוכחה |
| 10 | אישור לכל תוצר | כולם `aceito` |
| 11 | Execution Report + כתיבה לזיכרון | סגירה |
| 12 | (Opt-in) שחרור ציבורי | רק אחרי אישור |

---

## חוזה אי-הפרה

כל מיקרו-שלב פולט `TaskCreate` עם 5 שדות:

```
PRECONDITION: <invariant לפני>
ACTION: <פקודה מדויקת>
POSTCONDITION: <מה השתנה>
ACCEPTANCE-TEST: <פקודה + פלט צפוי>
FALSIFICATION-TEST: <מבחן שהיה מוכיח כישלון>
DEPENDS-ON: <tasks upstream>
DELIVERABLE-ID: <לאיזה תוצר תורם>
```

שום task לא מסומן `completed` בלי **הוכחה טרייה** של ה-ACCEPTANCE-TEST.

---

## דגלי עומק

| Flag | התנהגות | עלות |
|---|---|---|
| `--quick` | מדלג על validator + `/goal` | 1× |
| `--standard` (default) | Pre-mortem + MAST + validator אחד + `/goal` | 3× |
| `--paranoid` | + `advisor()` + 2 validators + 3 סבבים | 6×+ |
| `--no-goal` | Fallback `executing-plans` | −1× |

---

## v5 (2026-05-17) — `claude -p /goal` ככרנל ראשי

אימות אמפירי אישר ש-`claude -p` מקבל `/goal` כקלט מועבר ראשון. ASP v5 מקדם דפוס זה לכרנל ראשי של Phase 9. Native kernel (in-session) הופך ל-fallback. **Iron Law קריטי**: אסור לסמוך על `$?` מ-`claude -p` — לפרסר את ה-JSON (`is_error`, `terminal_reason`, `total_cost_usd`). פרטים ב-`tests/claude-p-goal-runner-probe.md`.

## מחבר

**Ulisses Flores** — CTO וחוקר ראשי ב-[Codex Hash Research Laboratory](https://ulissesflores.com); מועמד MSc AI, American Global Tech University. סאו פאולו, ברזיל.

- 🌐 [ulissesflores.com](https://ulissesflores.com)
- 🐙 [@ulissesflores ב-GitHub](https://github.com/ulissesflores)
- ✉️ c.ulisses@gmail.com (חשיפת אבטחה ב-[SECURITY.md](../SECURITY.md))

תחומים: מימון כמותי & Web3, חומרה & IoT, AI & מדעי הנתונים. שפות המתחזק: פורטוגזית (שפת אם), אנגלית/ספרדית (שוטף), איטלקית (שיחה), עברית (קריאה אקדמית). ביקורת דוברי שפת אם של ES/IT/HE מתקבלת בברכה דרך PR.

**שותף ליצירה**: Claude (Anthropic, Opus 4.7) — סינתזת מחקר וטיוטה תחת הכוונת human-in-the-loop. ראה [AUTHORS](../AUTHORS).

## קהילה

- [CONTRIBUTING.md](../CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) · [SECURITY.md](../SECURITY.md) · [CHANGELOG.md](../CHANGELOG.md)

## רישיון

MIT — ראה [LICENSE](../LICENSE).

</div>
