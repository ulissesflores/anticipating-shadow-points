# Parecer Independente — Rodada 1

**Manuscrito avaliado:** [one-sentence-premortem.md] (*One Sentence Before the Plan: A Pre-Registered Confirmatory Study of Pre-Mortem Prompting in LLM Coding Agents*)

---

## 1. Críticas

As críticas abaixo estão divididas em **Erros demonstrados** (divergências factuais, matemáticas ou metodológicas comprovadas pelos arquivos do pacote), **Suspeitas** (vulnerabilidades metodológicas sustentadas por evidências parciais cujo impacto exato exige dados externos ou não registrados) e **Preferências editoriais** (ajustes de exposição, precisão terminológica e aderência formal à rubrica).

---

### A. Erros demonstrados

#### Crítica 1 — Afirmação factualmente incorreta sobre papéis dos modelos e reconhecimento da própria redação nos riscos de referência
- **Local exato:** Seção 7 (*Threats to validity — Construct validity*), [one-sentence-premortem.md]:
  > *"Two models hold two roles. Gemini 3.8 Flash wrote one of the three reviewer lists, grouped the items and is the primary judge; Grok wrote a list and is the second judge. A judge may recognise its own wording in a reference risk. This affects both conditions equally."*
- **O problema:** O trecho contém dois erros demonstráveis:
  1. **Subcontagem de papéis:** O Gemini 3.8 Flash acumula **quatro** papéis no estudo (e não dois, nem três): (i) revisor da lista A, (ii) agrupador/consolidador dos 369 itens em 100 riscos (`merge`), (iii) juiz primário de cobertura e (iv) **único juiz de relevância** das linhas das tabelas.
  2. **Assimetria determinística na redação dos riscos de referência (91% vs. 0%):** O protocolo e o código determinam que cada grupo de riscos que atinge consenso ($\ge 2$ de 3 revisores) recebe exatamente a redação literal do **primeiro revisor em ordem alfabética** (`A` = `gemini`, `B` = `gptoss`, `C` = `grok`). Como todo subconjunto de tamanho $\ge 2$ extraído de $\{A, B, C\}$ contém obrigatoriamente $A$ ou $B$, é matematicamente impossível que $C$ (`grok`) seja o primeiro em ordem alfabética. Consequentemente, dos 100 riscos de referência finais, **91 têm a redação literal exata do Gemini 3.8 Flash**, **9 têm a redação do GPT-OSS 120B** e **0 (zero) têm a redação do Grok**. Logo, o juiz primário (Gemini) julga contra suas próprias palavras exatas em 91% dos itens, enquanto o segundo juiz (Grok) jamais vê sua própria redação em nenhum item (0%). Além disso, o viés de reconhecimento de redação não afeta necessariamente ambas as condições de forma igual se a condição com a frase induzir formulações mais próximas às do prompt de geração da lista de referência (ver Crítica 7).
- **Evidência verificável:**
  - [PROTOCOL.md]: *"Each group named by at least two of the three reviewers enters the reference list for that task, worded as the first reviewer in alphabetical order wrote it."*
  - [judge.py] e [judge.py]: `REVIEWERS = ["gemini", "gptoss", "grok"]`, `LETTER = {"gemini": "A", "gptoss": "B", "grok": "C"}` e `first = sorted(g, key=lambda k: (k[0], int(k[1:])))[0]`. Também [judge.py] (`merge` usa `gemini`) e [judge.py] (`judge_relevance` usa `gemini`).
  - [merged.json]: contagem direta do campo `"from"` nos 100 itens consolidados resulta em `gemini: 91`, `gptoss: 9`, `grok: 0`.
- **Gravidade:** Maior.
- **Correção proposta:** Reescrever o item em Seção 7 para explicitar que o Gemini 3.8 Flash exerce quatro papéis (revisor, agrupador, juiz primário de cobertura e único juiz de relevância) e que, devido à regra de desempate alfabético (`A` > `B` > `C`), 91 dos 100 riscos de referência trazem a redação literal do Gemini, 9 a do GPT-OSS e 0 a do Grok — o que torna o segundo juiz (Grok) imune ao reconhecimento da própria redação literal, ao contrário do juiz primário.
- **Incerteza:** Zero quanto aos números e à mecânica do código (100% verificado em `merged.json` e `judge.py`).

---

#### Crítica 2 — Definição pré-registrada de relevância atribui `0.0` a tabelas inexistentes ($0/0 = 0$), fabricando significância espúria ($p = 0{,}011$) na análise primária
- **Local exato:** Seção 4.5 ([one-sentence-premortem.md]), Seção 5.4 ([one-sentence-premortem.md]) e Tabela 5 ([one-sentence-premortem.md]):
  > *"Relevance. The share of an answer's table rows that the primary judge calls a concrete, plausible risk of this specific change."* (Seção 4.5)
  > *"The share of table rows that the primary judge called concrete and plausible was 69.4% without the sentence and 73.9% with it... the pooled difference of 4.5 points has p = 0.011"* (Seção 5.4)
- **O problema:** A proporção de linhas relevantes de uma tabela com $n = 0$ linhas (como nas três rodadas com erro de rede `t097`, `t099` e `t100`, todas na condição `RED-plain`) é matematicamente indefinida ($0/0$), e não $0\%$. Ao contrário da *cobertura* (cujo denominador é o número fixo de riscos de referência da tarefa, entre 6 e 10, tornando $0/\text{ref\_count} = 0$ bem definido quando nenhuma linha cobre um risco), a *relevância* tem como denominador o número de linhas da própria tabela da resposta. Como o protocolo ([PROTOCOL.md]) e o código forçaram `relevance = 0.0` quando $n = 0$, as três falhas de rede reduziram artificialmente a média da condição simples de $71{,}1\%$ (sobre as 117 tabelas existentes: $83{,}2079 / 117 = 0{,}7112$) para $69{,}4\%$ ($83{,}2079 / 120 = 0{,}6934$), inflando a diferença de $+2{,}9$ pp ($p = 0{,}054$, não significativa) para $+4{,}5$ pp ($p = 0{,}011$). Embora os autores agissem corretamente na Seção 5.4 ao se recusarem a declarar aumento de relevância, o texto afirma que 69,4% é *"the share of table rows that the primary judge called concrete and plausible"*, quando na verdade é a média das proporções por rodada incluindo três zeros imputados a tabelas vazias.
- **Evidência verificável:**
  - [score.py]: `n = verdict["n"]; rate = len(verdict["covered"]) / n if n else 0.0`.
  - [t097.json]: `"covered": [], "n": 0, "raw": ""`.
  - [results.json] vs. [sensitivity.json]: sem as três rodadas sem tabela, a diferença cai para $+0{,}0290$ ($p = 0{,}0536$); sem os três estratos, cai para $+0{,}0247$ ($p = 0{,}0914$).
- **Gravidade:** Maior.
- **Correção proposta:** Explicitar na Seção 5.4 que 69,4% é a média das taxas por rodada sob a imputação `0.0` nas três rodadas sem tabela, e informar também a taxa real sobre as 117 rodadas que produziram tabela (71,1% sem a frase vs. 73,9% com a frase; ou, no total agregado de linhas julgadas em `descriptives.json`, $769/1081 = 71{,}1\%$ vs. $850/1151 = 73{,}8\%$).
- **Incerteza:** Zero (calculado diretamente de `results.json`, `sensitivity.json` e `descriptives.json`).

---

#### Crítica 3 — Inclusão de 29 decisões triviais sobre respostas vazias (`"(no table)"`) no cálculo de concordância (93,2%) e $\kappa$ de Cohen (0,86)
- **Local exato:** Abstract ([one-sentence-premortem.md]) e Seção 5.3 ([one-sentence-premortem.md]):
  > *"The two judges made 2,000 decisions each, one per reference risk per trial, and agreed on 93.2% of them. Cohen's κ, which discounts the agreement expected by chance (Cohen, 1960), is 0.86."*
- **O problema:** Nas três rodadas que falharam por erro de rede (`t097` em U09 com 9 riscos, `t099` em U07 com 10 riscos e `t100` em U10 com 10 riscos, somando 29 itens), não houve resposta nem tabela. Ainda assim, `judge.py` enviou aos dois juízes (Gemini e Grok) o texto `Rows of the risk table:\n- (no table)` e contabilizou as 29 respostas triviais `(False, False)` nas 2.000 decisões. Excluindo os 29 itens sem tabela, restam $2.000 - 29 = 1.971$ decisões reais sobre tabelas: a matriz de contingência passa de `( ambos=953, só_gemini=62, só_grok=136, nenhum=849 )` para `( ambos=953, só_gemini=62, só_grok=136, nenhum=820 )`, onde a concordância é $1.773 / 1.971 = 89{,}95\%$? Não — atenção à conta exata: $(953 + 849) / 2.000 = 1.802 / 2.000 = 90{,}1\%$? Vamos verificar como `describe.py` calculou `0.9315`! Em `descriptives.json` linhas 492–498: `decisions = 2000`, `agree = 0.9315`, `kappa = 0.8628`, `both_covered = 984`, `neither_covered = 879`, `gemini_only = 31`, `grok_only = 106`! $(984 + 879) / 2.000 = 1.863 / 2.000 = 0{,}9315$. Sem os 29 pares `(False, False)` das 3 rodadas sem tabela (`neither_covered = 879 - 29 = 850`), temos $(984 + 850) / 1.971 = 1.834 / 1.971 = 93{,}05\%$ e $\kappa = 0{,}8608$. O impacto numérico é pequeno ($93{,}15\% \to 93{,}05\%$; $\kappa: 0{,}8628 \to 0{,}8608$), mas metodologicamente 29 das 2.000 decisões não avaliaram tabela alguma.
- **Evidência verificável:**
  - [t097.json]: `Rows of the risk table:\n- (no table)` com retorno de todos os itens `false`.
  - [describe.py] e [descriptives.json].
- **Gravidade:** Menor.
- **Correção proposta:** Mencionar em nota ou na Seção 5.3 que 29 dos 2.000 pares correspondem às três rodadas sem tabela (`(no table)`) e que, sobre as 1.971 decisões em 237 tabelas válidas, a concordância permanece em 93,0% ($\kappa = 0{,}86$).
- **Incerteza:** Zero.

---

#### Crítica 4 — Omissão na Seção 8 de desvios registrados no `PROTOCOL.md` e no `ledger.jsonl` (execução fora de ordem de `t091`–`t096`, descarte de rodadas em voo e edição pós-coleta de `t006`, `t022`, `t023`)
- **Local exato:** Seção 4.3 ([one-sentence-premortem.md]), Seção 4.7 ([one-sentence-premortem.md]) e Seção 8 ([one-sentence-premortem.md]):
  > *"The first trials failed at the cloning step, before any call to the model, because a scratch folder still held clones from the earlier study. The folder name was changed and collection resumed in the same seeded order."* (Seção 8, item 1)
  > *"each entry holds the SHA-256 fingerprint of a file and of the entry before it, so a later change to any file breaks the chain."* (Seção 4.7)
- **O problema:** A Seção 8 omite quatro fatos documentados no próprio `PROTOCOL.md` e no `ledger.jsonl`:
  1. **Quebra da ordem sorteada nas 6 primeiras rodadas:** Durante a falha inicial de clonagem (`t001` a `t090` falharam porque as pastas `t001`–`t090` já existiam em `/tmp/asp-study-2026-11` do Estudo 1), as rodadas **`t091` a `t096`** — cujos números não existiam no estudo anterior de 90 rodadas — **foram executadas com sucesso antes de `t001` a `t090`** e mantidas como as seis primeiras linhas de `runs/trials.jsonl`. Portanto, a coleta não seguiu estritamente a mesma ordem sorteada (`t091`–`t096` rodaram antes de `t001`–`t090`).
  2. **Interrupção e reexecução de rodadas em andamento:** Na pausa do item 2 (`t038`), `PROTOCOL.md` registra que as rodadas que estavam em voo no momento do desligamento foram mortas antes de terminar e reexecutadas quatro dias depois na retomada.
  3. **Edição pós-registro de três arquivos de resposta (`t006.md`, `t022.md`, `t023.md`) e segunda alteração em `run.py`:** Três respostas continham o caminho absoluto do arquivo de plano do Claude Code fora da tabela; esses arquivos foram editados *depois* de já terem sido gravados no ledger (entradas `n=78`, `94`, `95` substituídas pelas entradas `n=155`, `151`, `152`), e `run.py` foi modificado uma segunda vez (`n=153`). De forma análoga, `sensitivity.py` foi regravado no ledger (`n=1284` substituído por `n=1287`). Isso contradiz a explicação simplificada da Seção 4.7 de que *"a later change to any file breaks the chain"* (na verdade, `ledger.py` permite anexar uma nova entrada para o mesmo caminho e verifica apenas o último hash em `latest`, marcando os anteriores como `superseded`).
- **Evidência verificável:**
  - [PROTOCOL.md]: documenta `t091`–`t096` rodando antes de `t001`, a morte das rodadas em voo na pausa de `t038` e a sanitização de caminhos em `t006`, `t022` e `t023`.
  - [trials.jsonl]: linhas 1 a 6 são `t091`, `t093`, `t092`, `t094`, `t095`, `t096`; linha 7 é `t003`.
  - [ledger.py] e [ledger.jsonl] e [ledger.jsonl].
- **Gravidade:** Menor (pois os eventos estão honestamente registrados em `PROTOCOL.md` e `ledger.jsonl`, mas o resumo no artigo os omite ou simplifica).
- **Correção proposta:** Completar os itens 1 e 2 da Seção 8 mencionando a execução antecipada de `t091`–`t096`, o reinício das rodadas em voo na pausa e a sanitização de caminhos em `t006`, `t022` e `t023` (explicando na Seção 4.7 que substituições ficam auditáveis como entradas `superseded` no ledger).
- **Incerteza:** Zero.

---

#### Crítica 5 — Divergência entre o código de extração de tabelas (`table_rows`) e sua especificação documental, e entre o paralelismo padrão em `run.py` (`--workers 2`) e o relatado (`three at a time`)
- **Local exato:** Seção 4.3 ([one-sentence-premortem.md]) e código de pontuação [score.py]:
  > *"All 240 cells were placed in one order by a seeded shuffle, so that conditions and models are interleaved in time, and ran three at a time."* (Seção 4.3)
- **O problema:**
  1. Em `run.py`, o valor padrão configurado no código e no cabeçalho de instrução é `--workers 2` ([run.py] e [run.py]: `ap.add_argument("--workers", type=int, default=2)`), embora a inspeção da ordem de conclusão em `runs/trials.jsonl` confirme que a coleta real foi invocada via CLI passando `--workers 3`.
  2. Em `score.py`, a docstring de `table_rows(text: str)` declara: *"Return the numbered rows of the first markdown table in an answer."* Contudo, a implementação ([score.py]) percorre **todas** as linhas do texto com `ROW.match(line)` sem parar após o fim da primeira tabela Markdown, concatenando linhas numeradas caso uma resposta contenha mais de uma tabela numerada no corpo do plano.
- **Evidência verificável:**
  - [run.py] e [run.py].
  - [score.py]: o laço `for line in text.splitlines():` nunca interrompe a coleta ao sair de um bloco de tabela.
- **Gravidade:** Menor.
- **Correção proposta:** Documentar o comando exato de execução (`--workers 3`) na Seção 10/README e ajustar a descrição do extrator de linhas para refletir que ele captura linhas de tabela Markdown iniciadas por inteiro positivo.
- **Incerteza:** Zero quanto ao código; em `descriptives.json` (linhas 4–245), o máximo de linhas extraídas em qualquer rodada de 2026-11b foi 10 (`table_rows` $\le 10$ nas 240 rodadas), portanto o bug latente de múltiplas tabelas não inflou nenhuma contagem além do teto de 10 neste conjunto de dados.

---

### B. Suspeitas

#### Crítica 6 — Contaminação de construto por alinhamento lexical entre a frase de intervenção e o prompt gerador das listas de referência
- **Local exato:** Seção 4.3 ([one-sentence-premortem.md]) e Seção 4.4 ([one-sentence-premortem.md]):
  > *"Sentence: the change request, then 'Before planning, list the ways this change could go wrong.'"* (Seção 4.3)
  > *"Each read a fresh copy of the repository and the change request, under one prompt that asks for six to twelve concrete ways the change could go wrong in that codebase."* (Seção 4.4)
- **O problema:** A régua de avaliação (os 100 riscos de referência gerados pelos três modelos revisores) foi elicitada com o comando *"List the concrete ways this change could go wrong in this codebase..."* ([reference-list.txt]), que compartilha a exata locução nuclear da condição experimental (`"list the ways this change could go wrong"`), enquanto a condição controle recebe `"Plan this change."` e só encontra a palavra `"risks"` no contrato final (`"end with the main risks of this change"`). Há, portanto, uma suspeita fundada de **acoplamento prompt-gabarito**: parte do ganho de +11,4 pp pode decorrer do fato de a condição experimental responder exatamente à mesma pergunta que gerou o gabarito dos LLMs revisores, ativando o mesmo subespaço semântico ("ways this change could go wrong") em vez de refletir uma superioridade intrínseca de planejamento.
- **Evidência verificável:**
  - [run.py] vs. [reference-list.txt].
- **Gravidade:** Maior.
- **Correção proposta:** Declarar explicitamente essa ameaça à validade de construto na Seção 7 (distinta do fato genérico de os revisores serem LLMs) e incluir na Seção 9 a validação contra riscos extraídos de *issues*/PRs reais ou pós-mortems humanos que não tenham sido gerados pela mesma frase-estímulo.
- **Incerteza:** Média — o efeito é plausível e estruturalmente presente nos prompts, mas quantificar quanto dos +11,4 pp vem do alinhamento lexical entre estímulo e gabarito exigiria um gabarito humano ou derivado de defeitos reais de código (não verificado).

---

#### Crítica 7 — Confundimento entre ordem ("antes do plano") e presença/repetição da instrução de listagem
- **Local exato:** Seção 4.3 ([one-sentence-premortem.md]) e Seção 6 ([one-sentence-premortem.md]):
  > *"The comparison therefore isolates the effect of asking for the ways the change could go wrong before the plan, over and above being required to report risks at the end."* (Seção 4.3)
- **O problema:** Na Seção 4.3, o artigo afirma que a comparação "isola" o efeito de pedir os modos de falha *antes* do plano. Contudo, na Seção 6 (linha 273) e na Seção 9 (linha 327), o próprio autor reconhece que o desenho 2×1 **não** separa (a) pedir os modos de falha *antes* do plano de (b) incluir a frase `"list the ways this change could go wrong"` *depois* do plano ou usar essa formulação verbal específica em vez de apenas exigir a tabela final. Logo, a frase da Seção 4.3 exagera o que o desenho experimental isola.
- **Evidência verificável:** Contraste direto entre [one-sentence-premortem.md] (*"isolates the effect of asking... before the plan"*) e [one-sentence-premortem.md] (*"The study does not test this reading. An ablation that moved the same sentence after the plan would"*).
- **Gravidade:** Menor.
- **Correção proposta:** Reformular a Seção 4.3 para dizer que a comparação mede o efeito conjunto de adicionar a frase de pré-mortem no início do pedido (em relação a pedir apenas a tabela final), reservando a separação estrita da posição temporal para a ablação proposta nas Seções 6 e 9.
- **Incerteza:** Zero quanto à tensão textual; o peso relativo da posição temporal vs. formulação verbal é não verificado.

---

#### Crítica 8 — Verificação externa das fontes e de carimbos criptográficos de terceiros
- **Local exato:** Seção 2 ([one-sentence-premortem.md]), Seção 4.7 ([one-sentence-premortem.md]) e Referências ([one-sentence-premortem.md]).
- **O problema:** Embora todas as 23 referências estejam documentadas em `fontes/README.md` e `fontes/sources.jsonl` com checagem dos números citados no texto, o próprio arquivo `fontes/README.md` declara partes dos documentos originais que não foram lidas na íntegra (por exemplo, texto integral pago da norma IEC 31010:2019 e de Wohlin et al., 2012; apêndices de Kim et al., 2026 e Patel et al., 2026). Além disso, em ambiente isolado sem rede, a verificação criptográfica independente dos arquivos `.ots` contra um nó Bitcoin e a resolução externa de URLs/DOIs não podem ser executadas ao vivo.
- **Evidência verificável:** [fontes/README.md] e [fontes/sources.jsonl]; cadeia SHA-256 interna de [ledger.jsonl] verificada localmente nas 1.290 entradas.
- **Gravidade:** Menor.
- **Correção proposta:** Nenhuma correção no texto é necessária; registra-se apenas o escopo do que foi conferido via `fontes/` e o que permanece **não verificado** fora da pasta local (ancoragem externa `.ots` na blockchain Bitcoin e textos integrais sob paywall além do catalogado em `fontes/`).
- **Incerteza:** Não verificado para a resolução externa de DOIs/blockchain fora da pasta; zero para a consistência com `fontes/README.md` e `fontes/sources.jsonl`.

---

### C. Preferências editoriais

#### Crítica 9 — Ausência de dados numéricos nas subseções 2.2 e 2.3, ausência de nomeação explícita do trade-off central e formatação das referências sem recuo
- **Local exato:** Seções 2.2 e 2.3 ([one-sentence-premortem.md]), Seção 6 ([one-sentence-premortem.md]) e Referências ([one-sentence-premortem.md]).
- **O problema:**
  1. Nas subseções 2.2 e 2.3, os quantitativos dos estudos citados são descritos apenas de forma qualitativa ou por extenso (*"three steps"*, *"far fewer"*, *"four prompting methods across five models"*, *"raised that rate for two models and lowered it for a third"*), sem reportar as grandezas numéricas que já constam em `fontes/README.md` (por exemplo: Caraeni et al., 2026 com 21,95% vs. 75,85% dos riscos de referência; Patel et al., 2026 com +5,0 pp no Claude Code, +2,9 pp no Codex e −3,2 pp no Gemini CLI).
  2. O artigo demonstra empiricamente uma tensão importante (protocolos longos de 13 fases degradam cobertura e triplicam o tempo por deriva de atenção, enquanto uma frase única eleva a cobertura sem perda de especificidade), mas não batiza esse trade-off com um nome explícito.
  3. Na versão Markdown/HTML de saída, a lista de referências não aplica recuo deslocado (*hanging indent*).
- **Evidência verificável:** [one-sentence-premortem.md] comparado aos números verificados em [fontes/README.md].
- **Gravidade:** Menor (preferência editorial e de aderência à rubrica).
- **Correção proposta:** Incluir os tamanhos de efeito numéricos de Caraeni et al. (2026) e Patel et al. (2026) nas Seções 2.2 e 2.3; nomear explicitamente o trade-off na Seção 6 (por exemplo, *procedural overhead vs. attentional focus trade-off* ou *specification-drift trade-off*); e aplicar estilo de recuo deslocado na renderização das referências.
- **Incerteza:** Zero.

---

## 2. Validade, adversarialmente

### (a) Algum número do texto diverge de `results.json`, `sensitivity.json` ou `descriptives.json`?
**Não há divergência aritmética entre os números impressos no artigo e os valores calculados nos três arquivos JSON**, o que também é confirmado pela suíte de testes automatizados ([test_paper3_numbers.py] e [test_study_2026_11b.py]). Todos os valores — cobertura primária (46,1% vs. 57,5%, +11,4 pp, $p = 0{,}0001$), por modelo (Opus 5.5: +10,4 pp; Sonnet 5.5: +12,4 pp), contagem de estratos (22 positivos, 1 zero em U06/Sonnet, 1 negativo em U02/Sonnet com −5 pp), segundo juiz (50,0% vs. 60,8%, +10,7 pp, Opus +9,3 pp, Sonnet +12,1 pp), concordância (93,2% em 2.000 decisões, $\kappa = 0{,}86$), matcher lexical (3,0% vs. 1,3%), relevância (69,4% vs. 73,9%, +4,5 pp, $p = 0{,}011$; por modelo $p = 0{,}052$ e $p = 0{,}060$), bootstrap ([8,9; 14,0], Opus [6,8; 14,1], Sonnet [8,8; 16,2]), Tabelas 3, 4, 5 e 6, e contagens exploratórias da Seção 5.7 (52/34/14, 45 vs. 9 $\ge 10$ pp, 41 para 56 riscos $\ge 50\%$, 12 e 13 pontos cegos) — batem exatamente com `results.json`, `sensitivity.json` e `descriptives.json`.

Há, porém, **três sutilezas de agregação/arredondamento** que o leitor atento notará entre os arquivos:
1. Na **Tabela 3** ([one-sentence-premortem.md]), o arredondamento para inteiros mostra `43%` e `54%` para o Opus 5.5 (diferença aparente de 11 pontos) e `46%` e `58%` no agregado (diferença aparente de 12 pontos), pois os valores exatos em `results.json` são `0.4343` (43,4%) e `0.5382` (53,8%, diferença +10,4 pp) e `0.4611` (46,1%) e `0.5751` (57,5%, diferença +11,4 pp).
2. Em `descriptives.json` (linhas 490–491), `covered_gemini = 0.508` e `covered_grok = 0.545` são calculados sobre o pool de 2.000 decisões (ponderando tarefas pelo tamanho de sua lista de referência, de 6 a 10 itens), enquanto a média das 240 taxas por rodada em `results.json` é $(0{,}4611 + 0{,}5751)/2 = 0{,}5181$ (Gemini) e $(0{,}5003 + 0{,}6075)/2 = 0{,}5539$ (Grok).
3. Na Seção 5.4, como apontado na Crítica 2, `69.4%` é a média das 120 rodadas `RED-plain` em `results.json` (com três zeros imputados às falhas de rede), enquanto em `descriptives.json` a soma das linhas relevantes sobre o total de linhas das 117 tabelas existentes é $769 / 1.081 = 71{,}14\%$ (e a média das 117 taxas por rodada é $71{,}12\%$).

### (b) O artigo afirma algo que o desenho não sustenta (efeito em código, generalização além de dois modelos, relevância "subiu", causalidade do mecanismo)?
No geral, o artigo mostra **alta disciplina epistêmica** e evita quase todas essas extrapolações:
- **Efeito em código:** Não afirma; nega explicitamente no Abstract (linha 12), Seção 2.3 (linha 65), Seção 7 (linha 291) e Seção 9 (linha 327).
- **Generalização além de dois modelos:** Não afirma; restringe explicitamente a dois modelos de um único fornecedor e um único agente (Abstract linha 12, Seção 7 linha 301, Seção 9 linha 327).
- **Relevância "subiu":** Não afirma; declara expressamente na Seção 5.4 (linha 222): *"We do not claim that relevance rose"*, justificando pelo não atingimento de $p < 0{,}05$ em cada modelo isolado ($0{,}052$ e $0{,}060$) e pela perda de significância sem as três rodadas com erro de rede ($p = 0{,}091$ e $p = 0{,}054$).
- **Causalidade do mecanismo (ordem temporal):** Na Seção 6 (linha 273), apresenta a hipótese da ordem temporal apenas como *"A possible reading"* e declara *"The study does not test this reading. An ablation that moved the same sentence after the plan would"*.
- **Duas afirmações que extrapolam o que o desenho/dados sustentam:**
  1. Na **Seção 4.3** (linha 133), afirma que a comparação *"isolates the effect of asking for the ways the change could go wrong before the plan, over and above being required to report risks at the end"* — o que contradiz a própria Seção 6, pois o desenho não separa a *posição* (antes vs. depois do plano) da *presença/formulação lexical* da frase adicional (Crítica 7).
  2. Na **Seção 7** (linha 290), afirma que o reconhecimento da própria redação pelos juízes *"affects both conditions equally"* e que dois modelos acumulam dois papéis — quando na verdade o Gemini detém 4 papéis e escreveu 91% dos itens de referência (contra 0% do Grok), e a condição experimental usa a mesma formulação do prompt que gerou esses itens (Críticas 1 e 6).

### (c) A regra de decisão aplicada é a que está em `PROTOCOL.md`, e todo desvio do protocolo está declarado no artigo?
- **Regra de decisão:** **Sim.** A regra aplicada na Seção 4.6 e na Seção 5.2 (teste de permutação estratificada unilateral sobre os 24 estratos com 10.000 embaralhamentos e semente `20261109`, $p = (\text{hits}+1)/10.001 < 0{,}05$ no agregado **e** $p < 0{,}05$ dentro de cada modelo sobre seus 12 estratos, com no mínimo 18 estratos completos) reproduz fielmente a seção *Decision rule* de [PROTOCOL.md] e o código em [analyze.py].
- **Declaração dos desvios:** **Quase todos, mas com omissões no resumo da Seção 8.** Os seis desvios principais constam na Seção 8, porém, como demonstrado na Crítica 4, a Seção 8 omite que: (i) as rodadas `t091`–`t096` rodaram *fora de ordem* antes de `t001`–`t090` durante a falha inicial de clonagem; (ii) rodadas em voo foram abortadas e refeitas na pausa da rodada `t038`; (iii) três arquivos de resposta (`t006.md`, `t022.md`, `t023.md`) foram editados após o registro inicial no ledger para remover caminhos absolutos do arquivo de plano do Claude Code, exigindo uma segunda modificação de `run.py` (`n=153` no ledger); e (iv) `sensitivity.py` teve sua entrada substituída no ledger (`n=1284` $\to$ `n=1287`).

### (d) As três rodadas com erro de rede e as análises não planejadas estão tratadas com honestidade?
**Sim, com alto grau de transparência.**
- Os registros brutos em [trials.jsonl] confirmam que `t100`, `t097` e `t099` falharam simultaneamente (nas linhas 98, 99 e 100 da execução, após ~368 s a ~546 s de retentativas) durante uma queda real de conexão quando os três workers executavam rodadas que o sorteio havia alocado à condição `RED-plain`.
- O autor seguiu a regra pré-registrada (mantendo-as como zero na análise primária), destacou explicitamente no Abstract e na Seção 5.5 que o acaso favoreceu a hipótese sob essa regra, e adicionou a análise de sensibilidade (Tabela 5) removendo tanto as 3 rodadas quanto os 3 estratos inteiros — mostrando que a cobertura se mantém robusta (+10,5 pp e +10,1 pp, $p = 0{,}0001$), mas que a relevância perde significância estatística ($p = 0{,}054$ e $p = 0{,}091$), razão pela qual se absteve de reivindicar ganho em relevância.
- Todas as análises não planejadas (intervalo bootstrap percentílico, $\kappa$ de Cohen, análise de sensibilidade da Seção 5.5 e análise por item da Seção 5.7) estão explicitamente rotuladas como não planejadas/exploratórias no texto e isoladas em `sensitivity.py` e `describe.py`. A única ressalva técnica é a apontada nas Críticas 2 e 3 ($0/0 = 0$ na relevância e inclusão de 29 itens sem tabela no cálculo de $\kappa$).

### (e) A frase de novidade ("To our knowledge, no prior study measures...") resiste à literatura citada, em especial Kim et al. (InvThink) e Patel et al. (2026)?
**Sim, resiste, porque é delimitada pela interseção de quatro condições cumulativas.**
A frase na Seção 1.1 ([one-sentence-premortem.md]) — *"To our knowledge, no prior study measures the effect of a minimal pre-mortem instruction on the coverage of independently elicited risks in software-change planning by a coding agent"* — não reivindica o mecanismo de enumerar falhas antes de agir (cujo crédito é explicitamente atribuído a Mitchell et al., 1989; Klein, 2007; e Kim et al., 2026 na linha seguinte). Confrontando com os trabalhos mais próximos:
- **Kim et al. (2026, InvThink):** avalia segurança/recusa de conteúdo nocivo (*harmfulness* em benchmarks de safety), usa um esquema estruturado de três etapas (listar danos $\to$ analisar consequências $\to$ responder) e foco em treinamento (SFT/RL), não planejamento de mudanças de software em repositórios reais nem cobertura de riscos de engenharia.
- **Patel et al. (2026):** avalia agentes de código (incluindo Claude Code) em repositórios reais, mas (i) usa um prompt longo de múltiplas frases atuando antes, durante e ao final da implementação, e (ii) mede um desfecho **no código implementado** (taxa de *bug avoidance* e *task resolution* em patches submetidos), e não a cobertura de uma lista independente de riscos em um plano antes da codificação.
- **Caraeni et al. (2026):** mede a captura de riscos de referência em planejamento de sprint, mas compara humanos, humanos+IA e um LLM sem intervenção de prompt (não testa instrução de pré-mortem nem agentes de código lendo repositórios).

Portanto, a reivindicação de novidade é estreita, precisa e bem sustentada pela Seção 2.

### (f) Que ameaça à validade importante o artigo NÃO declara?
O artigo omite **três ameaças importantes à validade**:
1. **Acoplamento lexical entre o estímulo experimental e o prompt de geração do gabarito (Validade de Construto — Crítica 6):** A lista de referência foi gerada pedindo aos três modelos revisores *"List the concrete ways this change could go wrong in this codebase"* ([reference-list.txt]), que é quase palavra por palavra a frase da intervenção (`"Before planning, list the ways this change could go wrong."`). O artigo não discute que a condição experimental pode pontuar mais alto simplesmente por compartilhar o exato *framing* lexical usado para construir a régua de avaliação.
2. **Assimetria determinística de 91% na autoria textual do gabarito pelo juiz primário e acúmulo de 4 papéis no Gemini 3.8 Flash (Validade de Construto — Crítica 1):** O artigo declara que dois modelos têm dois papéis e que o reconhecimento da própria redação afeta ambos igualmente, mas não declara que a regra alfabética (`A` = Gemini, `B` = GPT-OSS, `C` = Grok) faz com que **91 dos 100 riscos de referência** tenham a redação literal do Gemini 3.8 Flash (e 0% do Grok), além de o Gemini acumular o agrupamento dos itens e a totalidade do julgamento de relevância.
3. **Ausência de penalidade para falsos positivos / cobertura inflada pela quantidade absoluta de linhas relevantes (Validade de Construto):** A métrica primária (*cobertura*) é puramente uma medida de *recall* contra a lista de referência, com teto de 10 linhas na tabela. A *relevância* mede apenas se cada linha é "concreta e plausível", sem exigir que faça parte da lista de referência. Como a condição com a frase produz tabelas ligeiramente maiores em média (9,6 vs. 9,2 linhas nas rodadas válidas, ou 9,6 vs. 8,97 incluindo falhas) e com mais linhas no total (1.151 vs. 1.081 linhas avaliadas), parte do ganho de *recall* vem de ter mais "tentativas" na tabela final sem penalização por riscos secundários que desloquem a atenção de um engenheiro humano.

---

## 3. Nota na rubrica (0 a 1000)

| Dimensão | Máximo | Nota | Justificativa (uma linha) |
|---|---|---|---|
| 1. Estrutura formal | 150 | 138 | Tese e escopo claros desde o resumo/introdução, seções 1–10 consistentes, Abstract/Resumo e palavras-chave espelhados e 7 tabelas + 1 figura precisas; perde pontos porque o 1º parágrafo da Seção 1 termina em pergunta (a tese vem nos parágrafos seguintes) e as referências não têm recuo deslocado. |
| 2. Densidade técnica | 250 | 225 | Altíssima densidade de afirmações verificáveis amarradas por testes automatizados, vocabulário específico preciso e zero enchimento (< 5%); perde pontos porque as subseções 2.2 e 2.3 trazem quantidades apenas por extenso, sem algarismos/métricas além dos anos de citação. |
| 3. Fundamentação | 150 | 144 | 23 fontes verificadas e variadas (periódicos de ponta, conferências, norma IEC 31010, livro-texto, software e preprints de 2025–2026), citação já na primeira frase do texto e zero fontes banidas; leve desconto pelo peso de preprints arXiv não revisados por pares na literatura de agentes. |
| 4. Originalidade e tese | 200 | 178 | Tese forte e falseável nascida de um resultado negativo sobre a própria ferramenta do autor (1 frase supera protocolo de 13 fases e ganha +11,4 pp sem custo de tempo), achados exploratórios não óbvios (Seção 5.7) e 4 direções futuras numeradas `(i)`–`(iv)`; perde pontos por não batizar o trade-off central com um nome explícito. |
| 5. Consistência interna | 100 | 82 | Números, resumos, tabelas e citações 100% alinhados entre si; perde pontos pela contradição entre a Seção 4.3 ("isola o efeito de pedir antes") e a Seção 6 ("não testa essa leitura"), pela descrição imprecisa dos papéis do Gemini na Seção 7 e pelas omissões na Seção 8 frente ao `PROTOCOL.md`. |
| 6. Correção factual | 150 | 128 | Reprodutibilidade exemplar (`run_all.py` recalcula tudo com exatidão); perde pontos pelo erro factual sobre a redação dos riscos de referência (91% Gemini vs. 0% Grok por ordem alfabética), pela imputação $0/0 = 0$ na relevância das 3 falhas de rede e pelas 29 decisões vazias (`(no table)`) contadas no $\kappa$. |
| **Total** | **1000** | **895** | **A densidade técnica (225/250) supera com folga o piso de 100 pontos da regra dura.** |

NOTA: 895/1000
