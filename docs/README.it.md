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

## Licenza

MIT — vedi [LICENSE](../LICENSE).
