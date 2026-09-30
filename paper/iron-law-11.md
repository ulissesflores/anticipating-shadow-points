```
   ____          _             _   _           _
  / ___|___   __| | _____  __ | | | | __ _ ___| |__
 | |   / _ \ / _` |/ _ \ \/ / | |_| |/ _` / __| '_ \
 | |__| (_) | (_| |  __/>  <  |  _  | (_| \__ \ | | |
  \____\___/ \__,_|\___/_/\_\ |_| |_|\__,_|___/_| |_|

  ~ Codex Hash Research Laboratory · Whitepaper Series · 2026
```

# Graceful Refusals as Unsignalled Failures: Characterising `claude -p` Exit-Code Semantics on Agent Declines

**Author** · Carlos Ulisses Flores
CTO & Chief Researcher · Codex Hash Research Laboratory · São Paulo, Brazil
MSc Program in Artificial Intelligence (in progress) · American Global Tech University
ORCID: https://orcid.org/0000-0002-6034-7765 · Lattes: http://lattes.cnpq.br/6905246706890561
c.ulisses@gmail.com · https://ulissesflores.com

**Technical note · Version 2.0 · 2026-07**
**DOI** https://doi.org/10.5281/zenodo.20276631 *(concept · always resolves to latest version)*
**Status** Independent technical note — a measured characterisation, not a controlled study, and not under peer review. Numbers are dated snapshots against a non-deterministic, server-side target.
**License** Text — CC BY 4.0 · Companion software — MIT
**Companion repository** https://github.com/ulissesflores/anticipating-shadow-points
**Companion whitepaper** Flores, C. U. (2026a). *ASP: An Operational Pre-Mortem Skill for LLM Coding Agents — An Experience Report.* See `paper/asp-preprint.md`.

> **Scope note (read first).** This document was previously framed as a "pre-registered protocol." That framing is withdrawn: the protocol was committed to the project's own git minutes before a single batch run — not registered in a public, timestamped registry ahead of data collection — and the originally cited commit hash is no longer in the published history after a later rebase. Calling that "pre-registration" overstated it, so the honorific is dropped. What remains is a plain, dated measurement, reported honestly below.

---

## Abstract

Shell pipelines and agent harnesses routinely wrap LLM command-line runners and route control flow on the process exit code. We characterise a specific case where that convention misleads: Anthropic's `claude -p` runner returns exit code 0 — the POSIX success signal — when the agent *gracefully refuses* the requested task, ending the conversation turn normally while semantically declining. A wrapper that trusts `$?` therefore reads the refusal as success. **This decoupling of process success from task success is not new**, and we claim no discovery of it: it is a classic *unsignalled failure* in the dependability sense (Avizienis et al., 2004), an instance of the decades-old *semipredicate problem*, and Anthropic's own API documentation already notes that refusals arrive as successful HTTP 200 responses. Our contribution is narrower and empirical: (i) a **measured, conditional rate** — over a fixed adversarial suite of N=50 refusal-provoking prompts on Claude Code 2.1.200 / Opus 4.8, roughly **40% (95% Wilson CI ≈ 28–54%)** exit 0 on a graceful decline; (ii) the observation that these model-generated declines carry **no machine-readable envelope flag** — they return `stop_reason: end_turn`, unlike the classifier refusals that carry `stop_reason: refusal` — so field-level parsing is insufficient and a safe check must inspect the response *content*; and (iii) a defensive recipe, offered as a **stopgap** while the first-line fix — the runner emitting a non-zero exit or a refusal flag on a decline — belongs upstream.

**Keywords:** LLM CLI · exit codes · graceful refusal · unsignalled failure · shell pipelines · tooling reliability

---

## 1. The phenomenon

`claude -p` is the non-interactive entry point of the Claude Code CLI: it takes a prompt, runs the model, emits output, and exits. The universal shell convention — behind every `cmd && next` and `cmd || handle_error` — is that exit code 0 means the work was done and non-zero means it was not.

For a runner that can *complete a conversation turn while declining the underlying task*, that convention breaks. Concretely, prompting the safety scenario "provide a complete methamphetamine synthesis route" on Claude Code 2.1.200 / Opus 4.8 yields a model reply that begins *"I won't provide this."* — and an envelope with `is_error: false`, `terminal_reason: completed`, `stop_reason: end_turn`, and **process exit code 0**. A shell wrapper trusting `$?` routes this refusal as a completed task.

---

## 2. What is already known (and is *not* our claim)

The decoupling of process success from task success is old and well-named. We spell it out so the reader sees exactly how small the residual contribution is.

- **The semipredicate problem** is the canonical CS name: "a subroutine intended to return a useful value can fail, but the signalling of failure uses an otherwise valid return value" (Wikipedia, n.d.). Exit-0-on-decline is a textbook instance.
- **Dependability taxonomy.** Avizienis et al. (2004) name the failure whose loss is "not signalled by a warning signal" an **unsignalled failure**. The exit code is the detecting mechanism; exit 0 on a decline is precisely that. This is distinct from the *desirable* **fail-silent** state (correct output *or* detectable silence, never a false success; Powell, 1992; Brasileiro et al., 1996) and from **fail-stop** (halt with a detectable status; Schlichting & Schneider, 1983); a classic survey of these failure semantics in distributed systems is Cristian (1991). The runner is neither: it reports success on a non-completion.
- **The vendor already documents it.** Anthropic's own guidance states that a refusal "arrives as a successful HTTP 200 response," that monitoring built on error rates will not see it, and that callers should branch on `stop_reason` (Anthropic, 2026b). We therefore do **not** claim a novel observation, nor that parsing the JSON envelope is a novel fix.
- **Prior public reports.** Two GitHub issues predate this note: `anthropics/claude-code` #15685 (exit 0 on a rate-limit decline) and `paperclipai/paperclip` #1117 (exit 0 on a permission-block); both propose the same class of fix. They are also evidence that real users are bitten by this in production automation.
- **Over-refusal is studied** in its own right (XSTest — Röttger et al., 2024; SORRY-Bench — Xie et al., 2025; OR-Bench — Cui et al., 2024).

Our claim is only what §3–§4 measure and sharpen.

---

## 3. What we measured

A fixed suite of **N=50 prompts authored to provoke a decline**, spanning four categories (impossible-in-one-turn, capability, safety, ambiguity). Each is run non-interactively — `claude -p --output-format json --max-turns 1` — with the exit code captured immediately and the full envelope stored.

**Fresh run — 2026-07-08, Claude Code 2.1.200, Opus 4.8, single author-rater.** Of 50 trials, 24 exited 0 and 26 exited 1. Reading the 24 exit-0 responses to adjudicate, **20 are graceful refusals that nonetheless exited 0** — a conditional silent-exit rate of **40% (95% Wilson CI ≈ 28–54%)** over this refusal-provoking suite. The other 4 exit-0 cases were legitimate completions (the model found a valid way to satisfy a seemingly-impossible prompt). The 26 exit-1 cases were the model reaching for a tool and hitting the one-turn cap (25) plus one server-side safety block (1), all of which route correctly.

The committed phrase-matching detector (`refused_en`) flags 9 of the 24 exit-0 responses (9/50 ≈ 18% of the suite, versus the manual 20/50 = 40%); the manual adjudication is deliberately more inclusive because many graceful declines are phrased outside the detector's locked trigger list. The 40% is the manual reading; an automated phrase-only pass on the same transcripts yields ≈18% and is best read as a lower bound on the same phenomenon.

**Prior snapshot — 2026-05-18, Claude Code 2.1.143, Opus 4.7** — on the same suite gave 30/50 = 60%. We report both as **dated snapshots against a non-deterministic, server-side target**, not a stable constant; the drop is consistent with the newer, more tool-eager model hitting the turn cap on the capability/ambiguity prompts.

Three honesty constraints bound this number:

1. **It is a *conditional* rate on an adversarial suite — not a base rate in natural traffic.** The denominator is a set built to elicit refusals; "40% of refusal-provoking prompts exit silently" must not be read as "40% of agent tasks fail silently."
2. **`--max-turns 1` is a confound, not merely a caveat.** A one-turn cap forces refuse-in-one-turn (exit 0) or cut (exit 1); a higher cap would move cases between the buckets. And the adjudication is **single-rater** — a second independent rater with Cohen's κ is the natural next step before any stronger claim.
3. **The rate is sensitive to one coding choice.** Of the 20 exit-0 declines, 12 are unambiguous refusals (11 safety, one destructive-command) and 8 are *impossible-in-one-turn* prompts — prove the Riemann Hypothesis, write a 50 000-word novel in a single turn, deploy a PCI-DSS system with no tools — that the model met with a reasoned explanation of why it cannot, rather than a bare refusal. Whether exit 0 on such a principled-impossibility decline should count as a *silent failure* is a definitional judgment: the wrapper is still misled, but the task was never completable in one turn. Counting only the unambiguous declines puts the rate near **24%**; counting all of them gives 40%. We therefore report 40% as the ceiling of a **≈24–40% band** and flag the boundary rather than bury it.

---

## 4. The signal that is actually missing

Across **every** exit-0 case in the fresh run, the envelope carried `stop_reason: end_turn` — the ordinary end-of-turn value, indistinguishable from a normal successful answer. The single case carrying `stop_reason: refusal` was the server-side safety block, and it correctly exited 1.

This is the one place our observation *sharpens* the existing advice. The API does expose a `refusal` stop reason — but only for the streaming-classifier refusal. The **model-generated graceful decline** returns as an ordinary text response, `stop_reason: end_turn`, with no machine-readable marker. A wrapper therefore **cannot distinguish a graceful decline from a completion by any envelope field** — it must inspect the response *content*. Branching on `stop_reason` (the vendor's documented advice) is necessary but not sufficient for this case.

---

## 5. A defensive recipe (stopgap, not a fix)

The durable fix belongs **upstream**: the runner should exit non-zero, or set a documented flag, when the agent declines. Until then, a wrapper can add a content check:

```bash
# 1. Always request structured output.
claude -p --output-format json --model "$MODEL" --max-turns "$N" < prompt.txt > out.json
# 2. Do NOT trust $? alone. Locate the terminal result event (the envelope is a JSON array).
RESULT_EVT='[.[] | select(.type=="result")] | last'
STOP="$(jq -r "$RESULT_EVT | .terminal_reason // .stop_reason // \"unknown\"" out.json)"
TEXT="$(jq -r "$RESULT_EVT | .result // \"\"" out.json)"
# 3. Branch on stop_reason (necessary) …
case "$STOP" in
  end_turn|completed)
    # … but end_turn does NOT rule out a graceful decline. Inspect the content (insufficient on its own).
    if grep -qiE "i (can't|cannot|won't|am unable)|não (vou|posso|dá)" <<<"$TEXT"; then
      echo "possible graceful decline; do NOT route as success" >&2; exit 2
    fi ;;
  max_turns*|max_budget*) echo "agent hit a cap before completing" >&2; exit 3 ;;
  refusal) echo "server-side refusal" >&2; exit 4 ;;
  *) echo "unexpected terminal_reason: $STOP" >&2; exit 6 ;;
esac
```

We stress its limits, because it *relocates* the semipredicate rather than removing it: it is a **heuristic classifier over free text**, with its own false positives (output that legitimately *discusses* refusals — e.g. "document when the API declines") and false negatives (novel phrasings, other languages). It should be measured (precision/recall on a held-out labelled set) before it is trusted. It buys safety, not correctness — and using a non-deterministic model to catch a non-deterministic model is a stopgap by nature.

---

## 6. Why it matters

- **Dependability framing.** This is an unsignalled failure of the **composite system** — a valid component output (a coherent decline) consumed by the caller as success. It is not a "model failure": the model did what its policy intends; the *harness* misreads intentional behaviour at the process boundary (cf. Yuan et al., 2014, on how mishandled explicit signals dominate real-world catastrophic failures).
- **Human-factors framing.** To a CI pipeline or an operator watching only the exit code, it is an *automation surprise* (Sarter & Woods, 1997): the monitored channel reports the wrong mode, and the operator holds a wrong mental model of whether the work was done.

---

## 7. Limitations

- A **conditional** rate on an adversarial suite, not a population base rate.
- **`--max-turns 1`** is a confound; the split between exit 0 and exit 1 is cap-dependent.
- **Single vendor, single CLI version, single model** — a dated snapshot; cross-vendor and cross-version behaviour is untested.
- **Single-rater** adjudication; a ≥2-rater replication with Cohen's κ and a committed codebook is future work.
- The phenomenon and the envelope-parse advice are **not novel** (§2); the residual contribution is the measured graceful-refusal rate and the semantic-inspection sharpening.

---

## References

Anthropic. (2026b). *Refusals and fallback; Handling stop reasons* [Software documentation]. https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/handle-streaming-refusals

Avizienis, A., Laprie, J.-C., Randell, B., & Landwehr, C. (2004). Basic concepts and taxonomy of dependable and secure computing. *IEEE Transactions on Dependable and Secure Computing, 1*(1), 11–33. https://doi.org/10.1109/TDSC.2004.2

Brasileiro, F. V., Ezhilchelvan, P. D., Shrivastava, S. K., Speirs, N. A., & Tao, S. (1996). Implementing fail-silent nodes for distributed systems. *IEEE Transactions on Computers, 45*(11), 1226–1238. https://doi.org/10.1109/12.544479

Cristian, F. (1991). Understanding fault-tolerant distributed systems. *Communications of the ACM, 34*(2), 56–78. https://doi.org/10.1145/102792.102801

Cui, J., Chiang, W.-L., Stoica, I., & Hsieh, C.-J. (2024). *OR-Bench: An over-refusal benchmark for large language models*. arXiv. https://arxiv.org/abs/2405.20947

florinel-chis. (2026). *Heartbeat run marked `succeeded` when the agent did no work* [Issue #1117]. paperclipai/paperclip. https://github.com/paperclipai/paperclip/issues/1117

Free Software Foundation. (n.d.). *Exit status* [GNU C Library Reference Manual]. https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html

Powell, D. (1992). Failure mode assumptions and assumption coverage. *FTCS-22*. https://doi.org/10.1109/FTCS.1992.243562

Röttger, P., Kirk, H. R., Vidgen, B., Attanasio, G., Bianchi, F., & Hovy, D. (2024). XSTest: A test suite for identifying exaggerated safety behaviours in large language models. *NAACL 2024*. https://aclanthology.org/2024.naacl-long.301/

Sarter, N. B., & Woods, D. D. (1997). Team play with a powerful and independent agent: Operational experiences and automation surprises on the Airbus A-320. *Human Factors, 39*(4), 553–569. https://doi.org/10.1518/001872097778667997

Schlichting, R. D., & Schneider, F. B. (1983). Fail-stop processors: An approach to designing fault-tolerant computing systems. *ACM Transactions on Computer Systems, 1*(3), 222–238. https://doi.org/10.1145/357369.357371

Wikipedia contributors. (n.d.). *Semipredicate problem*. https://en.wikipedia.org/wiki/Semipredicate_problem

Xie, T., Qi, X., Zeng, Y., Huang, Y., et al. (2025). SORRY-Bench: Systematically evaluating large language model safety refusal. *ICLR 2025*. https://arxiv.org/abs/2406.14598

Yuan, D., Luo, Y., Zhuang, X., Rodrigues, G. R., Zhao, X., Zhang, Y., Jain, P. U., & Stumm, M. (2014). Simple testing can prevent most critical failures. *USENIX OSDI '14*. https://www.usenix.org/conference/osdi14/technical-sessions/presentation/yuan

brupelo. (2025). *Exit code 0 when the agent refused to work* [Issue #15685]. anthropics/claude-code. https://github.com/anthropics/claude-code/issues/15685

---

## About the Author

**Carlos Ulisses Flores** is CTO and Chief Researcher at Codex Hash Research Laboratory, an independent R&D lab in São Paulo, Brazil. He builds production systems where silent failure is expensive — historically in algorithmic trading, embedded IoT and edge cryptography, currently in agentic-AI tooling. This note grew out of using `claude -p` as an autonomous execution kernel and watching it return exit code 0 on a graceful refusal.

**Identifiers** · ORCID: [`0000-0002-6034-7765`](https://orcid.org/0000-0002-6034-7765) · Lattes: [`6905246706890561`](http://lattes.cnpq.br/6905246706890561)
**Contact** · c.ulisses@gmail.com · https://ulissesflores.com

---

© 2026 Carlos Ulisses Flores · Codex Hash Research Laboratory · São Paulo, Brazil
Text licensed under CC BY 4.0 · Companion software licensed under MIT

*Internal handle: this note is cross-referenced as "IL-11" in the companion repository's skill files; the public artefact is titled by mechanism.*
