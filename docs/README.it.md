---
title: "Italiano"
layout: default
parent: Translations
nav_order: 3
---

# ASP — Anticipating Shadow Points (Anticipare i Punti d'Ombra)

> **Skill per Claude Code che trasforma compiti ambiziosi in deliverable spediti — tramite ricerca preventiva obbligatoria, rilevamento pre-mortem di "shadow points", piani validati da agente indipendente, micro-TODO contrattuali ed esecuzione autonoma via `/goal`.**

[🇬🇧 English](../README.md) · [🇪🇸 Español](README.es.md) · [🇧🇷 Português](README.pt.md) · 🇮🇹 Italiano (questo file) · [🇮🇱 עברית](README.he.md)

📐 **[ARCHITECTURE.md](ARCHITECTURE.md)** — Doc completa dello stato dell'arte: contesto accademico, percorso v1→v5, scoperte empiriche (incl. Iron Law 11), contributi user/advisor, derivazione delle 12 Iron Laws.

> Traduzione assistita da IA — revisione nativa benvenuta via PR.

---

## Cos'è ASP?

**ASP** sta per **Ant-Shadow-Point** — quei piccoli punti di fallimento facilmente sfuggenti che si nascondono nelle ombre di qualsiasi compito non banale e appaiono dopo come bug, incidenti o PR respinte.

Invocata con `/asp <il tuo compito>`, questa skill orchestra un protocollo di 13 fasi che:

1. **Pone le domande giuste** (≤3 pre-ricerca, ≤3 post-ricerca).
2. **Ricerca in parallelo** (codebase + web + lezioni precedenti).
3. **Fa pre-mortem del fallimento** (Klein 1998 + tassonomia MAST a 14 modi di Berkeley).
4. **Valida con agente indipendente** (prompt separato — niente collusione di auto-critica).
5. **Esegue via `/goal`** (separazione worker/evaluator nativa Anthropic, rilasciata 2026-05-12).
6. **Accetta per deliverable** e scrive lezioni a memoria persistente.

---

## Perché usare ASP?

Se hai mai consegnato qualcosa e 24h dopo pensato *"perché non ci ho pensato?"*, ASP fa per te.

**ASP è appropriata per:**
- Feature che toccano dati o stato condiviso
- Refactor su molti file
- Migrazioni (schema, dipendenza, API)
- Deploy con dipendenze esterne
- Decisioni di architettura
- Investigazioni di debug che richiedono disciplina root-cause

---

## Quick Start

```bash
git clone https://github.com/ulissesflores/anticipating-shadow-points.git ~/Developer/ASP
cd ~/Developer/ASP
./scripts/verify.sh --pre-install
./scripts/install.sh --dry-run
./scripts/install.sh
```

Invocare:

```
/asp Aggiungi colonna `tier` (NOT NULL, default 'free') in user_profiles. La tabella ha 1M righe.
```

Disinstallare:

```bash
./scripts/uninstall.sh
```

---

## Casi d'Uso (Esempi)

Scenari concreti dove ASP eccelle. Ciascuno proviene dai 5 eval strutturati che accompagnano lo skill (`skills/anticipating-shadow-points/evals/`).

### 1. Migrazione di schema su tabella di produzione
> *"Aggiungi colonna NOT NULL `tier` (default 'free') in `user_profiles`. Tabella ha ~1M righe in prod."*

ASP forza audit upfront di: policy RLS, strategia di backfill + lock contention, replica lag durante DDL, ordine di deploy app vs migration, interazione con trigger, locks in cascata via FK, piano di rollback, spike di monitoring, finestra di downtime, reload dello schema cache di PostgREST.

### 2. Refactor di util usato in molti file
> *"Rifattorizza `formatDate(d: Date): string` per accettare timezone opzionale. Usato in 30 file."*

ASP fa emergere: semantica del contratto API, implicazioni di locale/i18n, enumerazione di callsites via `ts-morph` (non grep), test di limite DST, deprecation period, strategia di branches, dependency graph transitivo.

### 3. Deploy di edge function con dipendenza esterna
> *"Deploy edge function `notify-on-signup` che chiama Resend (rate limit 100 req/sec)."*

ASP forza design upfront di: `RESEND_API_KEY` in `supabase secrets`, backoff via outbox pattern, idempotency keys, cold-start timeout, observability strutturata, euristiche anti-bot, deliverability (SPF/DKIM/DMARC).

### 4. Modifica di RLS policy che referenzia nuova colonna
> *"Aggiorna RLS di `user_profiles` perché utenti vedano solo righe con stesso tier."*

ASP cattura: ambiguità di spec, ricorsione self-reference, vulnerabilità di self-promotion, `FORCE ROW LEVEL SECURITY`, transazione atomica, helper `SECURITY DEFINER` con `search_path` fissato.

### 5. Cron che può conflittare con servizi disabilitati
L'integrazione `recall.py` di Phase 1 fa emergere memoria di incidente precedente. Nell'eval empirico, il validator subagent **ha rifiutato l'implementazione** scoprendo che il path dello script coincide con servizio precedentemente disabilitato.

### 6. Decisione di architettura cross-team
Phase 3 (Project Charter) + Phase 4 (Deliverables Register con accettazione per-deliverable + owners) elimina il "pensavo fosse tuo".

---

## Come Funziona — Le 13 Fasi

| # | Fase | Output |
|---|---|---|
| 0a | Pre-ricerca Q&A (≤3) | Intake |
| 1 | Ricerca parallela | Sintesi |
| 0b | Post-ricerca Q&A (≤3, saltabile) | Intake raffinato |
| 2 | Rilevamento Shadow Points (Klein + MAST 14) | Lista + mitigazioni |
| 3 | Project Charter | Charter compilato |
| 4 | Macro Plan + Deliverables Register | Deliverable D01..Dn |
| 5 | Validator indipendente | APPROVE / REVISE |
| 6 | Loop interno cap=3 + advisor() opzionale | Piano finale |
| 7 | Utente approva 3 artefatti | Go/No-Go |
| 8 | Micro-TODO contrattuale + Goal Spec | N tasks + completion condition |
| 9 | Esecuzione via `/goal` | Tasks completed con evidenza |
| 10 | Sign-off per deliverable | Tutti `aceito` |
| 11 | Execution Report + memory write-back | Chiusura |
| 12 | (Opt-in) Release pubblica | Solo dopo approvazione |

---

## Contratto di Non-Violazione

Ogni micro-passo emette un `TaskCreate` con 5 campi:

```
PRECONDITION: <invariante prima>
ACTION: <comando esatto>
POSTCONDITION: <cosa è cambiato>
ACCEPTANCE-TEST: <comando + output atteso>
FALSIFICATION-TEST: <test che proverebbe fallimento>
DEPENDS-ON: <tasks upstream>
DELIVERABLE-ID: <a quale deliverable contribuisce>
```

Nessun task è `completed` senza **evidenza fresca** dell'ACCEPTANCE-TEST.

---

## Flag di Profondità

| Flag | Comportamento | Costo |
|---|---|---|
| `--quick` | Salta validator + `/goal` | 1× |
| `--standard` (default) | Pre-mortem + MAST + 1 validator + `/goal` | 3× |
| `--paranoid` | + `advisor()` + 2 validator + 3 round | 6×+ |
| `--no-goal` | Fallback `executing-plans` | −1× |

---

## v5 (2026-05-17) — `claude -p /goal` come kernel primario

Validazione empirica ha confermato che `claude -p` accetta `/goal` come first piped input. ASP v5 promuove questo pattern a kernel primario di Phase 9. Native kernel (in-session) diventa fallback. **Iron Law critica**: mai fidarsi di `$?` da `claude -p` — fare parse del JSON (`is_error`, `terminal_reason`, `total_cost_usd`). Dettagli in `tests/claude-p-goal-runner-probe.md`.

## Autore

**Ulisses Flores** — CTO & Chief Researcher presso [Codex Hash Research Laboratory](https://ulissesflores.com); MSc AI candidate, American Global Tech University. San Paolo, Brasile.

- 🌐 [ulissesflores.com](https://ulissesflores.com)
- 🐙 [@ulissesflores su GitHub](https://github.com/ulissesflores)
- ✉️ c.ulisses@gmail.com (segnalazione di sicurezza in [SECURITY.md](../SECURITY.md))

Aree: Finanza Quantitativa & Web3, Hardware & IoT, IA & Data Science. Lingue del mantenitore: Portoghese (nativo), Inglese/Spagnolo (fluente), Italiano (conversazionale), Ebraico (lettura accademica). Revisione di madrelingua ES/IT/HE benvenuta via PR.

**Co-autore**: Claude (Anthropic, Opus 4.7) — sintesi di ricerca e drafting sotto direzione human-in-the-loop. Vedi [AUTHORS](../AUTHORS).

## Community

- [CONTRIBUTING.md](../CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) · [SECURITY.md](../SECURITY.md) · [CHANGELOG.md](../CHANGELOG.md)

## Licenza

MIT — vedi [LICENSE](../LICENSE).
