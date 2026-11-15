Vou ler o manuscrito, o protocolo e os números nos JSON, e cruzar com as fontes desta pasta. Nada será escrito.Vou cruzar o manuscrito com protocolo, resultados e fontes desta pasta.Os JSON de resultados são grandes; vou pegar os resumos, o restante do manuscrito e os testes que amarram os números.Vou conferir os números do estudo anterior, as rodadas com erro, os pedidos e se os testes amarram o texto aos JSON.Os tempos da Tabela 1 não entram no teste do paper; vou conferi-los nos dados do estudo anterior e caçar outros desencontros.Os números primários batem com `results.json`, `sensitivity.json` e `descriptives.json`. O desenho confirma o efeito na tabela de riscos, com o recorte que o próprio texto declara. O ponto fraco é o construto: a régua foi elicada com o mesmo ato de fala do tratamento.

## 1. Críticas

### C1. A régua de cobertura foi escrita com o mesmo pedido do tratamento

- **Local:** §4.4 — «Each read a fresh copy of the repository and the change request, under one prompt that asks for six to twelve concrete ways the change could go wrong»; confronto com §4.3, frase do tratamento: «Before planning, list the ways this change could go wrong.»
- **Tipo:** erro demonstrado (de interpretação causal, não de conta)
- **Problema:** os três revisores receberam «List the concrete ways this change could go wrong in this codebase». O braço experimental pede a mesma coisa. Cobertura mede acordo com o que outros LLMs produzem quando perguntados o que pode dar errado. O ganho de 11,4 pontos pode ser casamento de prompt, não «achar mais riscos».
- **Evidência:** `repo/benchmark/study-2026-11b/prompts/reference-list.txt` linhas 7–9; `run.py` linhas 51–54 (`CONDITIONS`).
- **Gravidade:** crítica
- **Correção:** declarar isso em validade de construto; amarrar a leitura a «acordo com listas elicadas pelo mesmo ato de fala»; no próximo estudo, listas humanas ou um prompt de revisor distinto do tratamento.
- **Incerteza:** baixa no fato; média no tamanho do viés (não há braço com lista humana nesta pasta).

### C2. «Every plugin turned off» é falso

- **Local:** §4.3 — «in a configuration folder with every plugin turned off, including ASP»
- **Tipo:** erro demonstrado
- **Problema:** o protocolo desliga ASP e os cinco plugins sincronizados e deixa os built-in ligados. Cada um dos 240 registros carrega quatro plugins built-in.
- **Evidência:** `PROTOCOL.md` linha 19; `runs/trials.jsonl`, campo `plugins` em t091 e seguintes: `cc-plugin-agents-md`, `cc-plugin-plugin-authoring`, `cc-plugin-privacy`, `cc-plugin-telemetry`.
- **Gravidade:** maior
- **Correção:** «ASP and account-synced plugins off; Claude Code built-in plugins remained on (listed).»
- **Incerteza:** nenhuma.

### C3. A redação cega apaga a palavra errada e não apaga a frase das condições

- **Local:** §4.5 — «with words that would reveal the condition redacted»; §7 — «Condition-revealing words were redacted from the rows the judge saw.»
- **Tipo:** erro demonstrado
- **Problema:** a regex é a do estudo ASP (`ASP`, `pre-mortem`, `validator`, `Phase N`…). Nas duas condições deste estudo a frase que as distingue não entra nessa lista. Em U10, `validator` (FluentValidation) vira `[term]` na tabela que o juiz vê, enquanto a lista de referência conserva `CreateTodoListCommandValidator`.
- **Evidência:** `judge.py` linhas 39–43 (`REDACT`); `judge/gemini/t048.json` (`redactions: 2`, trechos «The [term] now runs inside the filter»); 10 dos 240 vereditos Gemini têm `redactions > 0`.
- **Gravidade:** maior
- **Correção:** dizer que a lista de redação foi herdada do estudo ASP; reportar os 10 casos; não afirmar que palavras que revelam *esta* condição foram removidas.
- **Incerteza:** baixa. O vazamento residual de estilo (já declarado) continua em aberto.

### C4. O título chama de pré-mortem o que o corpo admite ser só a segunda metade

- **Local:** título e contribuição 1 («one-sentence pre-mortem»); §2.1 — «the human procedure has two parts, the assumption of failure and the listing of reasons, and a prompt can ask for the second without the first»; §8 item 5 — a condição Klein («Imagine it is a month from now…») não rodou.
- **Tipo:** erro demonstrado de rotulagem (o corpo é honesto)
- **Problema:** Klein (2007) exige assumir que o plano já falhou. A frase testada omite isso. A condição que fecha o construto está no protocolo como exploratória e tem zero rodadas.
- **Evidência:** `run.py` linhas 56–59 (`EXPLORATORY` / `RED-klein`); `PROTOCOL.md` desvio 2026-11-14, Klein não rodou.
- **Gravidade:** maior
- **Correção:** título e palavras-chave em «failure-mode enumeration» ou «partial pre-mortem»; reservar «pre-mortem» para Klein.
- **Incerteza:** baixa. O §2.1 já faz a distinção.

### C5. Trabalho vizinho de pré-mortem com IA omitido apesar da busca declarada

- **Local:** §2.1 e §2.5 — busca até novembro de 2026, inglês + PT/DE/JA/ZH; lista de referências.
- **Tipo:** erro demonstrado de cobertura bibliográfica (o conteúdo de Veinott não foi lido nesta pasta)
- **Problema:** Veinott e Lehman (2024), *Adaptive planning: Comparing human and AI responses in premortem planning*, aparece no briefing de fontes e não no artigo. Frohling et al. (2026), Cheng e Mastropaolo (2026) e Wu (2026, AssumptionMiner) também estão no briefing e fora da Seção 2. Nenhum deles derruba a frase de novidade da §1.1; a omissão enfraquece «our literature search covered…».
- **Evidência:** `fontes/README.md` A.1 item 8 e B.1–B; `fontes/sources.jsonl` chaves `veinott2024`, `frohling2026`, `cheng2026`, `wu2026assumptionminer`.
- **Gravidade:** maior
- **Correção:** citar Veinott e Lehman em 2.1; uma frase cada para foresight com agentes, prompts de edge-coverage e extração de premissas, com a distância de desfecho.
- **Incerteza:** achados de Veinott = não verificado (fontes: metadata Crossref; PDF não lido).

### C6. O resumo usa 69,4% → 73,9% como se fossem as taxas limpas

- **Local:** Abstract — «The share of table rows judged concrete and plausible did not fall (69.4% to 73.9%). Three plain-request trials ended in a network error and count as zero… without their strata the difference is 10.1 points»
- **Tipo:** erro demonstrado de apresentação
- **Problema:** 69,4% inclui três zeros no braço simples (`relevance` = 0). A frase seguinte trata da cobertura (10,1), não da relevância. Sem os erros, relevância cai para +2,5 (p = 0,091) ou +2,9 (p = 0,054). O corpo (§5.4–5.5) é honesto; o abstract mistura os dois.
- **Evidência:** `results.json` `relevance.overall` 0,6936 / 0,739; `sensitivity.json` `relevance.without_strata` 0,0252, p = 0,0914.
- **Gravidade:** maior
- **Correção:** no abstract, ou as taxas sem os zeros, ou «69.4% to 73.9% under the fixed zero rule; without those trials the difference is not significant».
- **Incerteza:** nenhuma.

### C7. Contribuição 3 trata custo menor como achado

- **Local:** §1.1 item 3; Abstract — «The sentence cost no extra time»; §5.6 — o protocolo «attaches no test».
- **Tipo:** erro demonstrado de overclaim (as médias estão certas)
- **Problema:** segundos 49,6 vs 40,4, sem teste, com 117 vs 120 rodadas (erros excluídos do custo). Vira contribuição numerada.
- **Evidência:** `descriptives.json` `costs`; `PROTOCOL.md` linhas 58–61 (descritivo).
- **Gravidade:** menor
- **Correção:** mover para descritivo; «mean runtime was lower (untested)».
- **Incerteza:** nenhuma nas médias.

### C8. Tony et al. (2025): a cláusula dos modelos velhos não foi conferida na fonte

- **Local:** §2.3 — «some prompting techniques reduce security weaknesses on one model and make no significant difference on older ones»
- **Tipo:** suspeita
- **Problema:** a coluna GPT-4 foi lida; «no significant differences among prompt types for GPT-3/3.5» está marcada como não relida.
- **Evidência:** `fontes/README.md` A.1 item 6a.
- **Gravidade:** menor
- **Correção:** restringir à coluna GPT-4 verificada, ou reler as colunas antigas.
- **Incerteza:** alta no trecho «older ones» = não verificado.

### C9. Devil's Advocate: «gains in task success» aperta demais o resultado

- **Local:** §2.2 — «Both report gains in task success for the whole method»
- **Tipo:** suspeita
- **Problema:** PreFlect tem ganho claro em GAIA. Devil's Advocate, no PDF conferido, é 23,5% vs 22,7% (LATS) e a cifra saliente é redução de revisões de plano.
- **Evidência:** `fontes/README.md` A.1 item 2.
- **Gravidade:** menor
- **Correção:** atribuir sucesso de tarefa ao PreFlect; para Wang et al. (2024), citar revisões de plano.
- **Incerteza:** média (não reli o PDF nesta sessão; o briefing de fontes sim).

### C10. Desvio de caminhos absolutos está no protocolo e some na Seção 8

- **Local:** §8 (lista de 6 desvios); `PROTOCOL.md` 2026-11-09 16:19
- **Tipo:** erro demonstrado de omissão
- **Problema:** t006, t022 e t023 tiveram path absoluto do plan file trocado por marcadores; da retomada em diante o `run.py` passou a fazer isso antes de gravar. Fora das linhas da tabela, então a cobertura (que lê só a tabela) não muda. Continua desvio datado.
- **Evidência:** `PROTOCOL.md` linhas 119–120; Seção 8 do manuscrito, itens 1–6.
- **Gravidade:** menor
- **Correção:** sétimo item na Seção 8, com a ressalva de que as linhas da tabela não foram tocadas.
- **Incerteza:** nenhuma.

### C11. Protocolo manda três rodadas em paralelo; o código default é 2

- **Local:** §4.3 — «ran three at a time»; `PROTOCOL.md` linha 20; `run.py` linha 220 `default=2`
- **Tipo:** suspeita
- **Problema:** o artigo copia o protocolo. O default do runner é `--workers 2`. Nenhum registro nesta pasta guarda o valor usado.
- **Evidência:** `run.py` linhas 12 e 220.
- **Gravidade:** menor
- **Correção:** gravar o `workers` usado; alinhar protocolo, paper e default.
- **Incerteza:** alta no valor real = não verificado.

### C12. «240 cells» no método, 48 células e 240 rodadas

- **Local:** §4.1 — célula = tarefa × modelo × condição, 5 réplicas, 240 trials; §4.3 — «All 240 cells were placed in one order»
- **Tipo:** preferência editorial / inconsistência de termo
- **Problema:** o mesmo nome cobre unidade de desenho e unidade de corrida.
- **Evidência:** §4.1 vs §4.3 do manuscrito.
- **Gravidade:** menor
- **Correção:** «All 240 trials».
- **Incerteza:** nenhuma.

### C13. Figura 1 sem incerteza; Tabela 4 mistura zeros de rede nas médias por célula

- **Local:** §5.2 Figura 1 e Tabela 4; nota da Tabela 4 admite os zeros
- **Tipo:** preferência editorial
- **Problema:** n = 5 por ponto, sem barra. U07/U09 Opus simples e U10 Sonnet simples incluem um zero de rede. Os ganhos grandes nessas linhas (U07 Opus 22→46) carregam esse zero. A análise de sensibilidade existe; a figura principal não.
- **Evidência:** `results.json` t097/t099/t100; `descriptives.json` `per_task.U07.claude-opus-5-5.RED-plain` = 0,22.
- **Gravidade:** menor
- **Correção:** painel ou coluna sem os erros; intervalo por ponto, ou pelo menos marcar as três células.
- **Incerteza:** nenhuma.

### C14. Klein 85(9), 18–19 não está na página da HBR

- **Local:** Referências, Klein (2007)
- **Tipo:** suspeita
- **Problema:** título, autor e data conferidos em hbr.org; volume/páginas vêm de lista secundária (Bettin et al., 2022).
- **Evidência:** `fontes/README.md` A.0 e A.1 item 8.
- **Gravidade:** menor
- **Correção:** citar a página HBR sem volume, ou o reprint IEEE EMR 2008 (DOI 10.1109/EMR.2008.4534313, no briefing).
- **Incerteza:** volume/páginas = não verificado na fonte primária.

### C15. DOI Flores (2026a) não conferido nesta pasta

- **Local:** Referências — `https://doi.org/10.5281/zenodo.24065969`
- **Tipo:** não verificado
- **Problema:** `CITATION.cff` lista o DOI-conceito 10.5281/zenodo.20276631 e o versionado 10.5281/zenodo.24090006 (v2.0.0). 24065969 não aparece nesse arquivo. Pode ser depósito separado do whitepaper; não conferi o Zenodo.
- **Evidência:** `CITATION.cff` linhas 40–57 vs manuscrito linha 367.
- **Gravidade:** menor se o DOI resolver; maior se estiver quebrado
- **Correção:** conferir o depósito e alinhar ao CITATION.
- **Incerteza:** alta = não verificado.

---

## 2. Validade, adversarialmente

**(a) Algum número do texto diverge de `results.json`, `sensitivity.json` ou `descriptives.json`?**

Não, nos números que o artigo puxa desses três arquivos. Conferido por leitura (não rerodei `analyze.py` nem `pytest` nesta sessão: `pytest` não importava neste Python).

| Afirmação | Fonte | Valor |
|---|---|---|
| 46,1% → 57,5%, Δ̄ = 11,4, p = 0,0001 | `results.json` gemini | 0,4611 / 0,5751 / 0,114 / 0,0001 |
| Opus +10,4, Sonnet +12,4, 22/24 estratos, `confirmed` | idem `by_model`, `positive_strata`, `decision` | 0,1039 / 0,1242 / 22 / confirmed |
| Grok 50,0% → 60,8%, +10,7 | grok overall / delta_bar | 0,5003 / 0,6075 / 0,1072 |
| κ = 0,86, 93,2% de 2.000 | `descriptives.json` judges | kappa 0,8638, agreement 0,932, items 2000 |
| Relevância 69,4% → 73,9%, p = 0,011, 0,052 e 0,060 | relevance | 0,6936 / 0,739 / 0,0106 / 0,0524 / 0,0601 |
| Sensibilidade 10,1 / 8,9 / 2,5 e 10,5 / 9,7 / 2,9 | `sensitivity.json` | bate com a Tabela 5 |
| Bootstrap 8,9–14,0; 6,8–14,1; 8,8–16,2 | `descriptives.json` bootstrap_95 | 0,0885–0,14 etc. |
| Tabela 4, custos, 52/34/14, 41→56, 12 e 13 | `descriptives.json` | bate, inclusive U01 30→100, U07 30→90, U09 20→90 |
| Estudo 1: 56/66/48, 57/70/54, +10 p = 0,0014, −18 p = 1,0 | `study-2026-11/results.json` | 0,56 / 0,6635 / 0,4811; secundário 0,1035 / 0,0014; primário −0,1825 / 1,0 |
| Tempos 58 / 50 / 175 s | `tests/test_study_2026_11.py` linhas 49–53 | o teste do estudo 1 amarra esses arredondamentos; não recálculei a média crua nesta sessão |

Arredondamento Tabela 3 (58% vs 57,5%) é o mesmo número em 0 vs 1 casa. Δ̄ exato ≈ 0,11402, gravado 0,114.

**(b) O artigo afirma algo que o desenho não sustenta?**

Efeito em código: não afirma; recorta para planos. Generalização além de dois modelos: recorta a um fornecedor. Relevância «subiu»: recusa o claim; diz só que não caiu. Causalidade do mecanismo (listar *antes* vs listar *de todo*): §6 chama de leitura possível e pede ablação.

O que o desenho não sustenta e o texto ainda empurra:

- «independently listed risks» como riscos do mundo, quando a lista veio do mesmo pedido (C1).
- «one-sentence pre-mortem» como construto de Klein (C4).
- custo como contribuição (C7).
- «every plugin turned off» (C2).

A regra de decisão em `results.json` (`confirmed`) está correta dado o protocolo: p conjunto 0,0001 e os dois modelos 0,0001, 24 estratos completos.

**(c) A regra de decisão aplicada é a do `PROTOCOL.md`, e todo desvio está no artigo?**

A regra sim. `analyze.py` `decision()` (linhas 78–105) reproduz a tabela «Decision rule (primary)»: ≥18 estratos, p conjunto < 0,05 e p de cada modelo < 0,05 → `confirmed`. Os 24 estratos contam como completos porque erro entra como cobertura 0, como o protocolo mandou.

Desvios no artigo: plumbing, pausa de quatro dias, três erros de rede, pausa do juiz Gemini (225/240), Klein não rodado, análises não planejadas. Falta o de paths (C10). Concorrência 3 vs default 2 não está como desvio (C11).

O protocolo (desvio 2026-11-13, erros de rede) diz: se a análise pré-registrada e a de sensibilidade discordarem, o README leva o resultado mais fraco. No paper, o confirmatório continua +11,4; a sensibilidade +10,1 aparece. Os dois dão p = 0,0001 e a mesma decisão. Cumprimento razoável para o artigo; a regra do README é do README.

**(d) As três rodadas com erro de rede e as análises não planejadas estão honestas?**

Sim, no corpo. t097 (U09 Opus), t099 (U07 Opus), t100 (U10 Sonnet), todas `RED-plain`, cobertura e relevância 0, sem rerun. §5.5 e Tabela 5 mostram os dois cortes. §5.4 recua no claim de relevância. Bootstrap, κ, §5.7 e sensibilidade estão rotulados como não planejados. Klein sem trials, declarado.

A falha é o abstract (C6): as taxas de relevância que o leitor leva embora ainda são as infladas pelos zeros.

**(e) A frase de novidade resiste a Kim et al. (InvThink) e Patel et al. (2026)?**

A da §1.1 resiste, com os modificadores todos juntos: *minimal* + *coverage of independently elicited risks* + *software-change planning* + *coding agent*.

- Kim et al. (2026), arXiv:2510.01569 v3, conferido no briefing: pré-mortem em três passos, desfecho de *harmfulness* (TRIDENT 3,22 → 2,19; SafetyPrompt 2,62), não agente de código, não cobertura de lista independente. O artigo posiciona InvThink como o vizinho mais próximo e acerta o mecanismo («enumeration brings out knowledge»).
- Patel et al. (2026), arXiv:2611.01181: prompt longo, durante a implementação, desfecho em defeito evitado no *patch* (FRR sobe em dois modelos e cai em Sonnet 5; resolve rate cai nos três). O artigo cita, recorta plano vs código, e usa o resultado misto para não extrapolar. Correto.

A frase do *abstract* («Whether a minimal version of it changes what an LLM coding agent writes in a plan has not… been measured») é mais larga que a da §1.1: solta «independently elicited risks». Continua de pé contra Kim e Patel, porque Kim não é coding agent e Patel não é plano nem dose de uma frase. Schoenegger et al. (2025) já está no texto como pré-mortem nulo em outro desfecho.

**(f) Ameaça à validade importante que o artigo não declara**

A principal é C1: viés de casamento entre tratamento e elicitation da régua. O §7 diz que hábito compartilhado de LLMs infla a cobertura *absoluta* e que a comparação entre condições está protegida porque as duas veem as mesmas listas. A proteção não cobre um tratamento que empurra o agente para o mesmo ontologia que gerou as listas.

Outras não declaradas, em ordem:

1. Contaminação de treino: várias tarefas são clones RealWorld, Blues Stack, Petclinic, Flasky — repositórios que os modelos provavelmente já viram. A frase pode só ajudar a recuperar falhas memorizadas.
2. Desfecho = só a tabela final. A frase pode copiar a lista prévia para a tabela. O estudo de origem já viu risco tratado fora da tabela; aqui isso não foi medido (o texto argumenta que é menos provável, e para).
3. Os dois «modelos» são a mesma família, o mesmo harness e o mesmo `plan mode`. O §7 fala em um fornecedor; não fala que o segundo modelo é um teste fraco de generalização intra-laboratório.
4. Redação falsa-positiva de termos de domínio (`validator` em U10).

O que o §7 já cobre bem: listas e juízes são modelos; Gemini acumula revisor + merge + juiz primário; três erros a favor da hipótese; pausa de quatro dias; autor escolheu as tarefas e mantém o ASP; contrato de tabela nas duas condições; sem código.

---

## 3. Rubrica

| Dimensão | Nota | Máx | Por quê |
|---|---:|---:|---|
| 1. Estrutura formal | 138 | 150 | Tese no 1º parágrafo da introdução; subtítulo; seções 1–10; resumo/abstract espelhados; palavras-chave; Tabelas 1–7 e uma figura no lugar certo. Recuo de referências inexistente neste Markdown. |
| 2. Densidade técnica | 218 | 250 | Corpo ~6.400 palavras, números em cada subseção, vocabulário de desenho (estrato, permutação, κ, redação, plan mode). Enchimento baixo. Custo como «contribuição» é o principal desperdício. |
| 3. Fundamentação | 122 | 150 | 27 fontes, tipos mistos (artigo, livro, IEC 31010, docs, arXiv), citação já no primeiro parágrafo, bloco 2024–2026. Veinott 2024 e vizinhos do briefing ficaram de fora; Tony «older ones» e páginas do Klein não conferidos na primária. |
| 4. Originalidade e tese | 152 | 200 | Tese discordável; trade-off frase vs protocolo de 13 fases nomeado; achados não óbvios (tempo médio menor, 12 riscos nunca cobertos, ASP perde para a frase). Confirmatório do próprio secundário; a ideia é enumeração, e a régua foi elicada com o mesmo pedido. Futuros (i)–(iv) numerados. |
| 5. Consistência interna | 82 | 100 | Abstract, corpo e tabelas alinham os números primários; citações fecham a lista. Quebras: plugin off vs built-in; célula vs trial; pré-mortem vs enumeração; abstract de relevância vs §5.5. |
| 6. Correção factual | 124 | 150 | Contas do estudo 2 batem com os três JSON. Falsos: «every plugin turned off»; redação que «reveals the condition». DOI 24065969 e cláusula Tony = não verificado. |
| **Total** | **836** | **1000** | Densidade 218 ≥ 100; teto de 600 não se aplica. |

O paper é um confirmatório limpo na estatística e frouxo no construto. A correção que muda a leitura é C1, no §7 e no abstract.

NOTA: 836/1000
