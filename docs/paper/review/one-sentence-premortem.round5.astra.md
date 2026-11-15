# Parecer do GPT-6 Astra, artigo 3, rodada 5 (2026-11-15)

Canal: codex exec, modelo gpt-6-astra, esforço high, pasta somente leitura, commit b570496. Texto integral abaixo.

O resultado confirmatório estreito se sustenta: a frase aumentou a cobertura das listas de referência nas tabelas finais desses dois modelos. Não encontrei erro numérico que reverta essa conclusão. As principais ressalvas restantes dizem respeito à construção da régua e a algumas afirmações excessivas sobre auditabilidade.

Li integralmente o manuscrito, conferi os protocolos e adendos e consultei as notas bibliográficas fornecidas. Executei, sem escrita, as 21 funções de verificação de `test_paper3_numbers.py`: todas passaram. Recalculei as análises dos dois juízes originais, relevância e segunda régua; coincidiram com os JSONs. Conferi 1.242 arquivos de vereditos, sem discrepância entre respostas booleanas e campos `covered`. O ledger passou na verificação: 1.909 entradas, 28 versões substituídas. O `pytest` não está instalado; não executei a suíte completa nem `run_all.py`, que escreve arquivos.

Para abreviar as evidências: **M** = `repo/paper/one-sentence-premortem.md`; **S** = `repo/benchmark/study-2026-11b/`.

**1. Críticas**

1. **Suspeita fundamentada — a segunda régua conserva parte do enquadramento que pretende testar. Gravidade: maior para a interpretação, não para o cálculo.**  
   **Local:** §5.8, M:347: “the gain is not only a match of wording”; §1.1, M:43: “Checks that the gain is not an artefact”.  
   **Problema:** a nova elicitação retira “go wrong”, mas a etapa que agrupa e seleciona os riscos continua recebendo esse enquadramento. Portanto, a checagem não remove essas palavras de todo o processo de construção da régua.  
   **Evidência:** `S/yardstick2/judge/merge/U08.prompt.txt:1`: “Three reviewers independently listed ways a software change could go wrong.” A origem está em `S/judge.py:122`; `yardstick2.py:161` reutiliza esse agrupador.  
   **Correção:** dizer que o efeito sobreviveu à reformulação **do pedido inicial aos redatores**, mantendo o agrupamento original. Trocar “not an artefact” por uma descrição das verificações realizadas. Uma futura checagem poderia neutralizar também o agrupamento.  
   **Incerteza:** a persistência do enquadramento é demonstrada; sua influência sobre os grupos e sobre o efeito não foi medida.

2. **Suspeita fundamentada — o filtro de consenso pode favorecer riscos comuns e excluir contribuições especializadas. Gravidade: maior como ameaça à validade de construto.**  
   **Local:** §7, objeção 2, M:396: “A risk that all three reviewers missed cannot be credited.”  
   **Problema:** essa formulação descreve apenas parte da exclusão. Um risco identificado corretamente por **um** revisor também não recebe crédito próprio. O filtro pode privilegiar aquilo que modelos diferentes tendem a repetir, independentemente da importância do risco.  
   **Evidência:** `S/judge.py:168–174` exige dois revisores. Contando os grupos dos arquivos `judge/merge/*.raw.txt`, encontrei 232 grupos originais, dos quais 132 pertencem a um único revisor e são excluídos. Na segunda régua, são 102 de 213. Por exemplo, U08/C5, sobre a substituição de `signer_kwargs`, fica sozinho em `S/judge/merge/U08.raw.txt:16`; seu conteúdo está em `S/lists/grok/U08.md:9`.  
   **Correção:** declarar explicitamente essa seleção por consenso e propor auditoria humana de uma amostra dos grupos excluídos, sem alterar retrospectivamente a análise confirmatória.  
   **Incerteza:** a exclusão é demonstrada. A correção técnica do exemplo no repositório original e a direção do viés resultante estão **não verificadas**.

3. **Erro demonstrado de documentação — o terceiro adendo promete preservar mais da resposta da API do que o código conserva. Gravidade: menor.**  
   **Local:** §8, item 9, M:438, e o adendo que fundamenta o procedimento.  
   **Problema:** `ADDENDUM-3.md:15` promete salvar a resposta completa da API. A implementação salva o conteúdo textual e apenas alguns metadados. Essa diferença não aparece entre os desvios relatados.  
   **Evidência:** `S/addendum3/addendum3.py:150–163` seleciona somente `id`, `model`, `provider` e `usage` para `api`, além de `message.content` para `raw`. Não conserva integralmente `choices`, motivos de término ou outros campos da resposta.  
   **Correção:** registrar que foram preservados o veredito textual e metadados selecionados; reconhecer a diferença em relação ao adendo. Em novas coletas, preservar o envelope completo.  
   **Incerteza:** baixa quanto à discrepância documental; não encontrei impacto nos escores publicados.

4. **Erro demonstrado de consistência — a Tabela 11 atribui aos registros uma prova temporal mais forte que a admitida no método. Gravidade: menor.**  
   **Local:** §10, Tabela 11, M:466: “the protocol predates the trials”.  
   **Problema:** essa promessa é categórica, enquanto §4.7 distingue corretamente integridade, existência dos arquivos e ordem temporal baseada no relógio do operador.  
   **Evidência:** M:198 esclarece que blockchain e arquivo não demonstram a precedência por segundos. A cópia fornecida não contém histórico `.git`; o ledger íntegro permite verificar os arquivos atuais e sua cadeia, mas não autentica sozinho os horários declarados.  
   **Correção:** fazer a Tabela 11 repetir a qualificação de §4.7: integridade verificável e cronologia sustentada pelos registros locais, com os limites das âncoras externas.  
   **Incerteza:** baixa quanto à inconsistência textual. Publicação dos commits e validação externa das âncoras: **não verificadas nesta revisão**.

5. **Erro demonstrado de escopo documental — o Apêndice A não apresenta todos os textos recebidos pelos modelos. Gravidade: menor.**  
   **Local:** Apêndice A, M:547: “every text that a model received in this study”.  
   **Problema:** a tabela apresenta os pedidos centrais, mas omite, entre outros, o pedido de agrupamento, o de relevância e a elicitação da segunda régua. Também não representa as instruções adicionais dos clientes.  
   **Evidência:** comparar M:551–557 com `S/judge.py:121–127`, `S/judge.py:304–310` e `S/yardstick2/reference-list-2.txt`. `S/addendum3/ADDENDUM-3.md:9` reconhece expressamente instruções adicionais do cliente CLI.  
   **Correção:** substituir “every text” por “the principal user prompts of the confirmatory experiment” e apontar os demais textos e as instruções do ambiente separadamente.  
   **Incerteza:** baixa; os pedidos omitidos estão disponíveis no pacote.

6. **Preferência editorial — qualificar melhor o pequeno estudo humano usado como referência externa. Gravidade: menor.**  
   **Local:** §2.2, M:65: “36.4% … against 78.6% for human planners”.  
   **Problema:** as porcentagens estão conferidas nas notas, mas sua apresentação sem os pequenos números absolutos pode sugerir evidência externa mais abrangente.  
   **Evidência:** `fontes/README.md:33` registra quatro riscos identificados no braço de IA, onze no humano e três sprints sequenciais; recomenda tratar o resultado como preliminar.  
   **Correção:** acrescentar “in a small, preliminary field study” e os números absolutos relevantes.  
   **Incerteza:** baixa quanto ao conteúdo das notas; não reli a fonte primária. Não classifico isso como número falso.

**2. Validade, adversarialmente**

**(a) Divergências numéricas:** não encontrei divergência material entre o texto e `results.json`, `sensitivity.json` ou `descriptives.json`. Conferi cobertura, diferenças por modelo, valores de p, concordância, intervalos, custos, contagens de riscos e análises condicionadas. Os arredondamentos explicam diferenças aparentes. Por exemplo, os 4,5 pontos de relevância vêm do cálculo anterior ao arredondamento intermediário para `0.0455`.

**(b) Afirmações além do desenho:** o corpo do artigo geralmente respeita seus limites. Ele não demonstra menos defeitos em código, generalização para outros fornecedores nem o mecanismo de “ativar conhecimento”. Também não afirma aumento robusto de relevância: §5.4 reconhece a ausência de margem de não inferioridade e a perda de significância nas sensibilidades. As expressões “not an artefact” e a interpretação forte da segunda régua merecem a correção do item 1. “Cobertura do plano”, no resumo, seria mais preciso como “cobertura da tabela final de riscos”.

**(c) Regra e desvios:** a regra aplicada corresponde a `PROTOCOL.md:63–73`: pelo menos 18 estratos completos, p agregado abaixo de 0,05 e p abaixo de 0,05 em ambos os modelos. Há 24 estratos e os três testes relevantes passam. Contar erros como zero corresponde à regra previamente escrita, não a exclusão oportunista.

Os desvios substantivos identificados estão relatados: falhas de clonagem, pausa, execuções interrompidas sem registro, versão do cliente, redações, cotas, condição não executada e análises posteriores. Contudo, **“todo desvio” não é literalmente verdadeiro**, pela preservação parcial da resposta da API apontada no item 3. Isso não muda a decisão estatística.

**(d) Erros de rede e análises não planejadas:** o tratamento é honesto. O artigo informa que todos os três erros favoreceram a hipótese e mantém a linha confirmatória original. Publica exclusão de estratos, exclusão de rodadas, limite adverso e repetição posterior, sem substituir silenciosamente os zeros. Também distingue o efeito sobre cobertura do resultado mais frágil de relevância. A seleção potencial causada pelas execuções interrompidas na pausa está expressamente reconhecida em M:431.

**(e) Novidade:** a frase delimitada resiste à literatura citada **conforme as notas fornecidas**. InvThink já sustenta a ideia de enumerar danos antes de responder; portanto, esse mecanismo não é novidade. Patel já testa antecipação de falhas por agentes de código; portanto, esse domínio geral também não é novidade.

A contribuição remanescente é a combinação específica: intervenção mínima, planejamento de mudanças e cobertura de riscos elicitados independentemente. `fontes/README.md:26–28` e `:90` sustentam essas distinções. O artigo ainda exclui corretamente o próprio estudo originador da reivindicação. Ausência universal de precedente permanece **não verificada**; a busca por títulos e resumos não poderia prová-la.

**(f) Segunda régua:** os números conferem:

| Medida | Valor conferido |
|---|---:|
| Riscos de referência | 111 |
| Cobertura, plain → sentence | 55,8% → 62,5% |
| Diferença agregada | +6,7 pontos; p = 0,0002 |
| Opus | +6,5; p = 0,002 |
| Sonnet | +6,9; p = 0,0013 |
| Estratos positivos / nulos / negativos | 16 / 2 / 6 |

A interpretação operacional segue `ADDENDUM.md:24`: positividade e significância **agregadas**. Não há troca indevida para a regra mais exigente do estudo confirmatório. A interrupção do Grok após 11 vereditos é declarada, e seus resultados incompletos não entram no JSON.

Resumo, discussão, conclusão e Figura 12 apresentam o efeito menor, além do original. Não detectei escolha sistemática do maior tamanho. Permanece a ressalva sobre o enquadramento do agrupador.

**(g) Acréscimos posteriores:** os números da Tabela 10 conferem com `results3.json`, `results4.json` e a sensibilidade da segunda régua:

| Tratamento dos erros | Gemini | Astra |
|---|---:|---:|
| Zero | +6,7 | +9,0 |
| Cobertura integral | +4,2 | +6,5 |
| Repetição | +5,6 | +7,7 |

Conferem também os resultados por modelo e seus valores de p, a repetição na régua original (+10,5), a concordância entre juízes (89,4%; κ = 0,77) e a conferência de canal (98,2%; κ = 0,96).

A cronologia local é compatível com os acréscimos fixados antes da coleta correspondente: o segundo adendo entra no ledger às 14:19:07 UTC; a primeira resposta das repetições aparece às 14:19:26 UTC. O terceiro entra às 17:22:46 UTC; o identificador mais antigo das respostas pagas contém horário posterior. Isso é evidência de consistência local; autenticação externa dessa precedência está **não verificada**.

Os acréscimos não substituem as linhas fixadas. O operador informado, o fornecedor compartilhado entre Astra e GPT-OSS e a troca de canal estão declarados em M:370. O resultado desfavorável de Opus no limite adverso do Gemini também permanece visível. Recomendo trazer ao artigo duas qualificações já presentes no terceiro adendo: os clientes acrescentam instruções diferentes e os níveis de raciocínio não têm equivalência demonstrada. Concordância elevada não prova identidade entre canais.

**(h) Ameaça importante não declarada explicitamente:** a seleção por consenso discutida no item 2. O artigo reconhece listas incompletas e riscos omitidos por todos os revisores, mas não desenvolve o possível favorecimento de riscos frequentemente repetidos em detrimento daqueles encontrados por apenas um especialista. A permanência do enquadramento “go wrong” no agrupador é outra limitação específica ainda não discutida.

**3. Rubrica**

| Dimensão | Nota | Justificativa |
|---|---:|---|
| Estrutura formal | **135/150** | Introdução com tese, título com subtítulo, numeração consistente, resumos espelhados e figuras úteis; recuo bibliográfico não está demonstrado no Markdown. |
| Densidade técnica | **235/250** | Métodos, estimandos, regras e números verificáveis são abundantes; há repetição entre resultados, objeções e desvios. Percentual exato de enchimento não verificado. |
| Fundamentação | **138/150** | Literatura pertinente, recente e variada, incluindo livro, norma e documentação; algumas fontes e endereços não têm conferência registrada em `fontes/`. |
| Originalidade e tese | **180/200** | Contribuição incremental bem delimitada, tese testável, trade-off nomeado e próximos passos enumerados; mecanismo e antecipação de falhas já têm precedentes. |
| Consistência interna | **94/100** | Excelente correspondência numérica e separação confirmatório/exploratório; pequenas inconsistências sobre completude documental e prova temporal. |
| Correção factual | **138/150** | Cálculos e vereditos conferidos, sem fabricação demonstrada; validade externa dos endereços e toda a cronologia pública não puderam ser autenticadas localmente. |

A regra dura não limita o total: densidade técnica acima de 100.

NOTA: 920/1000
