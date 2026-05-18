---
title: "Português"
layout: default
parent: Translations
nav_order: 2
---

# ASP — Anticipating Shadow Points (Antecipando Pontos de Sombra)

> **Skill para Claude Code que transforma tarefas ambiciosas em entregáveis enviados — através de pesquisa antecipada obrigatória, detecção pre-mortem de "shadow points", planos validados por agente independente, micro-TODOs contratuais e execução autônoma via `/goal`.**

[🇬🇧 English](../README.md) · 🇧🇷 Português (este arquivo) · [🇪🇸 Español](README.es.md) · [🇮🇹 Italiano](README.it.md) · [🇮🇱 עברית](README.he.md)

📐 **[ARCHITECTURE.md](ARCHITECTURE.md)** — Doc completa do estado da arte: background acadêmico, jornada v1→v5, descobertas empíricas (incl. Iron Law 11), contribuições user/advisor, derivação das 12 Iron Laws.

> Tradução nativa (autor é falante PT-BR).

---

## O que é ASP?

**ASP** vem de **Ant-Shadow-Point** — aqueles pontos de falha pequenos e facilmente despercebidos que se escondem nas sombras de qualquer tarefa não-trivial e aparecem depois como bugs, incidentes ou PRs rejeitados.

Invocada por `/asp <sua tarefa>`, essa skill orquestra um protocolo de 13 fases que:

1. **Faz as perguntas certas** (≤3 pré-pesquisa, ≤3 pós-pesquisa — nunca sobre implementação).
2. **Pesquisa em paralelo** (codebase + web + lições prévias do agentic-stack).
3. **Faz pre-mortem da falha** (Klein 1998 + taxonomia MAST de 14 modos de Berkeley).
4. **Valida com agente independente** (prompt separado — sem colusão de auto-crítica).
5. **Executa via `/goal`** (separação worker/evaluator nativa Anthropic, lançada 2026-05-12).
6. **Aceita por entregável**, depois escreve lições na memória durável.

O protocolo é opinativo. Existe porque skills que "só sugerem" são ignoradas sob pressão.

---

## Por que usar ASP?

Se você já entregou alguma coisa e 24h depois pensou *"por que não pensei nisso?"*, ASP é pra você.

**ASP é apropriada para:**
- Features que tocam dados ou estado compartilhado
- Refactors em muitos arquivos
- Migrações (schema, dependência, API)
- Deploys com dependências externas
- Decisões de arquitetura
- Investigações de debug que exigem disciplina de root-cause

**ASP é exagero para:**
- Correção de typo
- Edits de uma linha
- Perguntas que você responde lendo um arquivo

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/ulissesflores/anticipating-shadow-points.git ~/Developer/ASP
cd ~/Developer/ASP
```

### 2. Verifique dependências

```bash
# Obrigatório: Claude Code 2.1.139+ (lançado 2026-05-12)
claude --version  # deve ser ≥2.1.139

# Opcional: ~/.agent/ agentic-stack (habilita recuperação de lições via recall.py)
ls ~/.agent/ 2>/dev/null
```

### 3. Inspecione antes de instalar

```bash
./scripts/verify.sh --pre-install
```

### 4. Instale

```bash
./scripts/install.sh --dry-run    # preview
./scripts/install.sh              # aplicar
```

### 5. Invoque

```
/asp Adicione coluna `tier` (NOT NULL, default 'free') em user_profiles. Tabela tem 1M rows.
```

### 6. Desinstale

```bash
./scripts/uninstall.sh
```

---

## Casos de Uso (Exemplos)

Cenários concretos onde ASP brilha. Cada um vem dos 5 evals estruturados que acompanham a skill (`skills/anticipating-shadow-points/evals/`).

### 1. Migração de schema em tabela de produção
> *"Adicione uma coluna NOT NULL `tier` (default 'free') em `user_profiles`. Tabela tem ~1M rows em prod."*

ASP força auditoria upfront de: políticas RLS, estratégia de backfill + lock contention, replica lag durante DDL, ordem de deploy app vs migration, interação com triggers, locks em cascade via FK, plano de rollback, spike de monitoring, janela de downtime, reload do schema cache do PostgREST. Baseline sem ASP: ~60% coverage. Com ASP: 100%.

### 2. Refactor de util usado em muitos arquivos
> *"Refatore `formatDate(d: Date): string` pra aceitar timezone opcional. Usado em 30 arquivos."*

ASP surfaca: semântica do contrato API com nova assinatura, implicações de locale/i18n, enumeração de callsites via `ts-morph` (não grep — que perde JSX spreads e imports dinâmicos), testes de DST boundary, deprecation period, branch strategy, build/CI cache, dependency graph transitivo, snapshot test breakage.

### 3. Deploy de edge function com dependência externa
> *"Deploy edge function `notify-on-signup` que chama Resend (rate limit 100 req/sec) em cada signup."*

ASP força design upfront de: `RESEND_API_KEY` em `supabase secrets` (não `.env`), backoff via outbox pattern, idempotency keys, cold-start timeout, observability estruturada (sem PII em logs), heurística anti-bot, deliverability (SPF/DKIM/DMARC), verificação de webhook signature, DLQ para sends falhados.

### 4. Mudança de RLS policy referenciando nova coluna
> *"Atualize RLS de `user_profiles` pra usuários verem só rows com mesmo tier que o deles."*

ASP captura: ambiguidade de spec (own-row only, cohort visibility, ou tier-rank floor? — leitura literal vaza dados), recursão self-reference em subquery, vulnerabilidade de self-promotion sem `REVOKE UPDATE (tier)`, `FORCE ROW LEVEL SECURITY`, transação atômica drop-and-create, helper `SECURITY DEFINER` com `search_path` pinned.

### 5. Cron que pode conflitar com serviços desabilitados
> *"Setup cron 08:00 diário pra `~/ulisses-kb/sync/update.sh`."*

A integração `recall.py` da Phase 1 surfaca memória de incidente prévio antes de qualquer scheduling. No eval empírico, o validator subagent **recusou implementação** ao descobrir que o caminho do script bate com serviço previamente desabilitado por incidente de JVM-spawn-loop. ASP fez cumprir a regra agentic-stack "stop if a surfaced lesson would be violated".

### 6. Decisão de arquitetura cross-team
Phase 3 (Project Charter) + Phase 4 (Deliverables Register com aceite per-deliverable + owners) elimina o "achei que era teu" — cada time afetado tem deliverables nomeados que assina individualmente.

---

## Como Funciona — As 13 Fases

| # | Fase | Output |
|---|---|---|
| 0a | Pré-pesquisa Q&A (≤3) | Intake |
| 1 | Pesquisa paralela (codebase + web + recall.py) | Resumo |
| 0b | Pós-pesquisa Q&A (≤3, pulável) | Intake refinado |
| 2 | Detecção de Shadow Points (Klein + MAST 14) | Lista categorizada + mitigações |
| 3 | Project Charter | Charter preenchido |
| 4 | Macro Plan + Deliverables Register | Entregáveis D01..Dn |
| 5 | Validador independente (prompt separado) | APPROVE / REVISE |
| 6 | Loop interno cap=3 + advisor() opcional | Plano final |
| 7 | Usuário aprova os 3 artefatos | Go/No-Go |
| 8 | Micro-TODO contratual + Goal Spec | N tasks + completion condition |
| 9 | Execução via `/goal` | Tasks completed com evidência |
| 10 | Sign-off por entregável | Todos `aceito` |
| 11 | Execution Report + memory write-back | Fechamento |
| 12 | (Opt-in) Release público | Só após aprovação |

---

## Contrato de Não-Violação

Característica-assinatura do ASP: ao aceitar o macro plano, a skill emite um `TaskCreate` por micro-passo, cada um com 5 campos labeled:

```
PRECONDITION: <invariante antes>
ACTION: <comando exato>
POSTCONDITION: <o que mudou>
ACCEPTANCE-TEST: <comando + saída esperada>
FALSIFICATION-TEST: <teste que provaria falha>
DEPENDS-ON: <tasks upstream>
DELIVERABLE-ID: <a qual entregável contribui>
```

Nenhuma task pode ser `completed` sem ACCEPTANCE-TEST passar com **evidência fresca**. Se FALSIFICATION-TEST dispara, execução para e re-entra no ASP.

---

## Flags de Profundidade

| Flag | Comportamento | Custo |
|---|---|---|
| `--quick` | Pula validator + `/goal` | 1× |
| `--standard` (default) | Pre-mortem + MAST + 1 validator + `/goal` | 3× |
| `--paranoid` | + `advisor()` + 2 validators + 3 rounds | 6×+ |
| `--no-goal` | Fallback `executing-plans` | −1× |

---

## v5 (2026-05-17) — `claude -p /goal` como kernel primário

Validação empírica confirmou que `claude -p` aceita `/goal` como first piped input. ASP v5 promove esse padrão a kernel primário da Phase 9. Native kernel (in-session) vira fallback. **Iron Law crítica**: nunca confiar em `$?` do `claude -p` — parsear JSON (`is_error`, `terminal_reason`, `total_cost_usd`). Detalhes em `tests/claude-p-goal-runner-probe.md`.

## Autor

**Carlos Ulisses Flores** — CTO & Chief Researcher na [Codex Hash Research Laboratory](https://ulissesflores.com); MSc AI candidate, American Global Tech University. São Paulo, Brasil. ORCID: [`0000-0002-6034-7765`](https://orcid.org/0000-0002-6034-7765) · Lattes: [`6905246706890561`](http://lattes.cnpq.br/6905246706890561).

- 🌐 [ulissesflores.com](https://ulissesflores.com)
- 🐙 [@ulissesflores no GitHub](https://github.com/ulissesflores)
- ✉️ c.ulisses@gmail.com (disclosure de segurança em [SECURITY.md](../SECURITY.md))

Foco de domínio: Finanças Quantitativas & Web3, Hardware & IoT, IA & Ciência de Dados. Os docs multilíngue (EN/ES/PT/IT/HE) refletem os idiomas de trabalho do mantenedor — Português (nativo), Inglês/Espanhol (fluente), Italiano (conversacional), Hebraico (leitura acadêmica).

> *"Atuando na fronteira do desenvolvimento tecnológico, integrando rigor acadêmico e pragmatismo executivo para solucionar problemas em sistemas complexos adaptativos."*

**Co-autor**: síntese de pesquisa, drafting inicial e scripts de verificação produzidos em colaboração com Claude (Anthropic, Opus 4.7) sob direção explícita human-in-the-loop. Ver [AUTHORS](../AUTHORS) e [docs/ARCHITECTURE.md](ARCHITECTURE.md) Partes 5-6.

## Comunidade

- [CONTRIBUTING.md](../CONTRIBUTING.md) — como contribuir
- [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)
- [SECURITY.md](../SECURITY.md)
- [CHANGELOG.md](../CHANGELOG.md)

## Licença

MIT — ver [LICENSE](../LICENSE).
