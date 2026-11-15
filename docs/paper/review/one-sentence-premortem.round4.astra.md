# Parecer do GPT-6 Astra, artigo 3, rodada 4 (2026-11-15)

Canal: codex exec, modelo gpt-6-astra, esforço high, pasta somente leitura, commit a37b84d. Texto integral abaixo.

O resultado central está sustentado pelos arquivos: a frase aumenta a cobertura das listas de referência, nas condições estudadas. Não encontrei divergência nos resultados estatísticos publicados. Há, porém, correções necessárias na cronologia e em algumas formulações sobre novidade e interpretação.

Li o manuscrito inteiro e as notas bibliográficas fornecidas. Executei os 21 testes de correspondência entre texto e números; todos passaram. Recalculei **em memória, sem gravar arquivos**, `results.json`, `sensitivity.json`, `descriptives.json`, `results2.json`, `results3.json` e `results4.json`: os resultados coincidiram integralmente. A cadeia de 1.908 entradas passou na verificação local. Também conferi a estrutura de 960 vereditos completos, sem encontrar chaves ausentes ou valores inválidos.

Nas referências abaixo, **P** significa `repo/paper/one-sentence-premortem.md` e **S**, `repo/benchmark/study-2026-11b/`.

**Críticas — erros demonstrados ou problemas de interpretação**

1. **A hora da primeira rodada na Tabela 4 contradiz os registros da sessão.**  
   **Local:** Seção 4.7, Tabela 4: “First counted trial […] 16:10” — P:208.  
   **Problema:** uma rodada contabilizada já estava produzindo respostas antes desse horário. A coluna “Record” aponta para um arquivo que nem sequer registra timestamps das rodadas.  
   **Evidência:** a linha 8 do conteúdo descompactado de `S/runs/envelopes/t091.jsonl.gz` contém `2026-11-09T19:08:44.276Z`, isto é, **16:08:44,276 em UTC−3**. `t091` é a primeira entrada de `S/runs/trials.jsonl`, que contém duração, mas não horário de início. `S/PROTOCOL.md:106` também situa valores fixados “before trial 1” em aproximadamente 16h10.  
   **Gravidade:** **maior**, pela importância da cronologia para a alegação de pré-registro; não pelo tamanho da diferença temporal.  
   **Correção:** reconstruir a sequência a partir dos envelopes e dos registros de publicação, distinguindo início, primeira resposta, conclusão e registro no ledger. Corrigir a tabela e a entrada aproximada do protocolo.  
   **Incerteza:** baixa quanto à incompatibilidade dos horários; alta quanto à sua causa. **Isso não demonstra coleta anterior ao protocolo:** o ledger registra protocolo e código às 19:07:59Z, antes da resposta observada. A precedência externa da publicação permanece **não verificada nesta auditoria local**.

2. **A frase de novidade precisa excluir explicitamente o estudo originador.**  
   **Local:** Seção 1.1: “no prior study measures the effect…” — P:47.  
   **Problema:** literalmente, a frase é contradita pelo estudo anterior do próprio autor. Uma comparação secundária continua sendo uma medição do efeito.  
   **Evidência:** P:91–105 descreve exatamente a comparação entre a frase e o pedido simples, com cobertura de riscos independentes e diferença de aproximadamente dez pontos. `repo/paper/asp-preprint.md:660` identifica esse resultado como comparação secundária pré-registrada.  
   **Gravidade:** **menor**, corrigível sem alterar a contribuição científica.  
   **Correção:** escrever, por exemplo: “Beyond the originating study, we found no prior study…”; identificar a novidade deste artigo como **confirmação prospectiva da comparação primária em novas tarefas e dois modelos**.  
   **Incerteza:** baixa sobre a contradição literal; reconheço que o leitor pode inferir a exceção pretendida.

3. **A descrição de Patel et al. simplifica uma métrica conjunta como se medisse somente prevenção de defeitos.**  
   **Local:** Seção 2.3: “whether the patch avoids a defect…” — P:73; discussão: “raised defect avoidance…” — P:384.  
   **Problema:** os números citados dizem respeito a uma condição conjunta de resolução da tarefa e prevenção do defeito. Uma mudança nessa taxa não identifica, isoladamente, mudança na prevenção de defeitos entre tarefas resolvidas.  
   **Evidência:** `fontes/README.md:90` define FRR como “task resolved AND the defect […] is avoided” e confirma os valores utilizados. A mesma nota informa queda na taxa de resolução nos três modelos.  
   **Gravidade:** **menor**, mas relevante para interpretar o precedente mais próximo.  
   **Correção:** nomear FRR e descrever os percentuais como taxa conjunta de resolução e prevenção do defeito posterior. Preservar a advertência sobre heterogeneidade entre modelos.  
   **Incerteza:** baixa segundo a documentação fornecida; não reli o PDF original nesta auditoria.

4. **A discussão atribui à forma de perguntar uma dependência que o desenho não isola.**  
   **Local:** Seção 6: “the size of the effect depends on how the yardstick is asked for, and its direction does not” — P:376.  
   **Problema:** há duas realizações de listas, diferentes também em conteúdo, tamanho e ocasião de coleta. O estudo demonstra estimativas diferentes entre essas listas; não identifica o efeito causal da redação sobre o tamanho estimado, nem invariância da direção entre formulações em geral.  
   **Evidência:** a própria Seção 5.8 reconhece isso corretamente em P:349: “The data do not say how much […] comes from the wording.” As listas têm 100 e 111 itens.  
   **Gravidade:** **menor**.  
   **Correção:** substituir por “The estimated gain was smaller with the second elicited yardstick and remained positive with both.”  
   **Incerteza:** baixa quanto à falta de identificação; moderada quanto à intenção causal da frase original.

5. **Uma afirmação sobre relevância é mais forte que a análise permite.**  
   **Local:** Seção 7, objeção 1: “shows that the rows did not become less concrete” — P:394.  
   **Problema:** a ausência de redução na média observada não demonstra ausência de deterioração. A Seção 5.4 faz essa distinção corretamente, mas essa frase a perde.  
   **Evidência:** P:277 declara ausência de margem de não inferioridade. A Tabela 7 mostra diferença de relevância de +2,5 pontos, p = 0,091, excluindo os estratos afetados, e +2,9, p = 0,054, excluindo somente as rodadas.  
   **Gravidade:** **menor**.  
   **Correção:** uniformizar a formulação para “No reduction in mean judged relevance was observed.”  
   **Incerteza:** baixa. Não estou afirmando que a relevância caiu; estou distinguindo observação e demonstração de preservação.

**Crítica — ameaça plausível, não erro demonstrado**

6. **A incerteza decorrente da construção e aplicação da régua não entra nos intervalos reportados.**  
   **Local:** Seções 5.2 e 7: intervalos bootstrap e “Conclusion validity” — P:244 e P:422.  
   **Problema:** os intervalos condicionam nas listas, na fusão dos itens e nos vereditos obtidos. Mesmo o bootstrap por tarefa não representa uma nova elicitação, nova fusão ou novo julgamento. O texto discute vieses desses componentes, mas não explicita suficientemente essa limitação da incerteza estatística.  
   **Evidência:** `S/describe.py:111–136` reamostra valores já pontuados; `S/analyze.py:65–75` permuta esses valores fixos. Os ganhos variam de 11,4 para 6,7 pontos entre réguas e de 6,7 para 9,0 entre juízes na segunda régua. Essas diferenças não são estimativas puras de erro de medição, mas evidenciam que a escolha do instrumento importa.  
   **Gravidade:** **maior para interpretar os intervalos como precisão sobre “cobertura de riscos” em geral**; não invalida o teste condicional pré-registrado.  
   **Correção:** declarar expressamente a natureza condicional dos p-valores e intervalos. Em trabalho posterior, repetir elicitações, fusões e julgamentos, além de obter validação humana.  
   **Incerteza:** baixa sobre o que os cálculos condicionam; **não verificado** quanto ao tamanho e à direção da incerteza adicional.

**Preferência editorial**

7. **As referências não apresentam recuo pendente no Markdown fornecido.**  
   **Local:** “References”, P:475 em diante.  
   **Problema:** falta um requisito formal da rubrica, sem consequência científica.  
   **Evidência:** as entradas são parágrafos simples, sem marcação de recuo.  
   **Gravidade:** **menor**.  
   **Correção:** aplicar recuo pendente na versão diagramada.  
   **Incerteza:** baixa sobre o Markdown; apresentação em um PDF final, **não verificada**.

Quanto à **validade adversarial**, minhas respostas são:

**(a) Divergências numéricas.** Não encontrei divergência entre os números estatísticos do texto e `results.json`, `sensitivity.json` ou `descriptives.json`, respeitados os arredondamentos. A discrepância demonstrada é cronológica, na Tabela 4, não nesses resultados.

**(b) Afirmações além do desenho.** O artigo delimita adequadamente o resultado a tabelas finais de riscos, dois modelos de um fornecedor e referências produzidas por modelos. Não apresenta melhora do código como resultado próprio, não reivindica aumento robusto da relevância e identifica o mecanismo proposto como hipótese. As exceções são as formulações apontadas nos itens 4 e 5. A recomendação prática permanece evidência sobre a saída desse procedimento de planejamento, não sobre segurança ou qualidade global do plano.

**(c) Regra de decisão e desvios.** A regra aplicada corresponde a `PROTOCOL.md:63–71`: pelo menos 18 estratos completos, p agrupado abaixo de 0,05 e p abaixo de 0,05 nos dois modelos. Existem 24 estratos completos e os três testes dão p arredondado de 0,0001. A implementação está em `analyze.py:78–105`. Não cabe exigir uma correção de multiplicidade como se fossem três descobertas independentes: a confirmação exige a conjunção dos resultados.

Os desvios operacionais relevantes encontrados estão relatados na Seção 8, inclusive interrupções sem registro completo, correção de pastas, redação de caminhos, quotas e mudança de canal. Contudo, **não posso certificar integralmente a história do protocolo anterior à coleta**: esta cópia não contém `.git`, há versões superadas do protocolo no ledger e a cronologia apresenta o problema do item 1. Conferi que `analyze.py`, `judge.py`, `score.py` e a lista original mesclada ainda correspondem aos seus primeiros hashes registrados.

**(d) Erros de rede e análises não planejadas.** O tratamento é honesto. As três falhas são controles, favorecem a hipótese quando pontuadas como zero e continuam zero na análise confirmatória. O artigo mostra exclusões, limite desfavorável e repetições separadamente. Também declara as rodadas interrompidas pelo desligamento, cujo número e condições não foram preservados. Não encontrei substituição silenciosa de dados confirmatórios.

**(e) Novidade diante de InvThink e Patel.** A contribuição estreita resiste a esses dois precedentes **conforme as fontes fornecidas**. InvThink já sustenta a ideia de enumerar danos antes de responder, mas difere em domínio, intervenção e desfecho; Patel testa um bloco de instruções durante implementação e um desfecho em código. O artigo os reconhece. A frase literal, entretanto, precisa da ressalva sobre Flores (2026a), apontada no item 2. A inexistência universal de outro precedente permanece **não verificada**; a busca documentada tem limitações de indexação e acesso explicitadas em `fontes/README.md:98–100`.

**(f) Segunda régua.** A Seção 5.8 relata corretamente:

| Resultado | Conferência |
|---|---|
| 111 riscos; cobertura 55,8% → 62,5% | Confere |
| Diferença +6,7 pontos; p = 0,0002 | Confere |
| Opus +6,5; Sonnet +6,9 | Confere |
| 16 estratos positivos, 2 nulos e 6 negativos | Confere |
| Grok incompleto, excluído dos resultados | Confere |

A leitura segue `yardstick2/ADDENDUM.md:24–26`, que exige resultado agrupado positivo e significativo, sem exigir confirmação separada nos dois modelos. O resumo, a discussão e a conclusão incluem a estimativa menor; não escolhem apenas 11,4 pontos. A discussão precisa somente da precisão causal indicada no item 4.

**(g) Dois acréscimos.** Os números conferem integralmente:

| Tratamento na segunda régua | Gemini | GPT-6 Astra |
|---|---:|---:|
| Erros como zero | +6,7 | +9,0 |
| Erros como cobertura completa | +4,2 | +6,5 |
| Rodadas repetidas uma vez | +5,6, por API | +7,7 |

Também conferem os +10,5 pontos na régua original após as repetições, a concordância de 89,4% entre juízes e a conferência de canal de 98,2% em 281 decisões.

Os três adendos correspondem aos seus primeiros hashes no ledger; os registros locais são consistentes com a ordem declarada de fixação e coleta. A ancoragem externa dos adendos posteriores está **não verificada**; o próprio artigo informa que estava pendente. O teste neutro de conexão anterior ao terceiro adendo está explicitado em `ADDENDUM-3.md:3`.

As linhas exploratórias não substituem as linhas fixadas. A Seção 5.8 declara conhecimento prévio do operador, possível mudança do modelo, vínculo de fornecedor de Astra com GPT-OSS e troca de canal. Conferi também a compatibilidade dos identificadores, plugins e ausência de alterações de arquivos das três repetições com os registros originais. Isso confirma consistência observável, não identidade do modelo remoto.

A apresentação não oculta a estimativa menos favorável de +5,6 nem a perda de significância do Opus no limite desfavorável de Gemini. Os vereditos pendentes do canal original e do Grok continuam identificados como pendentes. A alta concordância na amostra de 30 não deve ser interpretada como equivalência comprovada entre canais.

**(h) Ameaça importante não declarada suficientemente.** A principal lacuna que identifiquei é a **incerteza do próprio instrumento de medição**, descrita no item 6. Os intervalos quantificam variação sob decisões de mensuração já fixadas; não quantificam quanto o efeito mudaria ao reconstruir e reaplicar a régua. Isso limita a interpretação substantiva da precisão, mesmo com p-valores pequenos.

A conferência bibliográfica utilizou `fontes/README.md` e `fontes/sources.jsonl`. Não tratei referências documentadas ali como “não verificadas” simplesmente por não reabri-las. A resolução atual de todos os endereços e DOIs, porém, não foi testada nesta auditoria restrita à pasta.

A pontuação pela rubrica é:

| Dimensão | Nota | Justificativa |
|---|---:|---|
| 1. Estrutura formal | **140/150** | Tese inicial, título com subtítulo, resumos espelhados, numeração, palavras-chave e figuras úteis; falta recuo nas referências fornecidas. |
| 2. Densidade técnica | **235/250** | Definições operacionais, testes, números e evidências abundantes; supera claramente três termos técnicos por 500 palavras, embora o percentual exato de enchimento não tenha sido mensurado. |
| 3. Fundamentação | **140/150** | Literatura recente e pertinente, artigos, livro, norma e documentação; boa conferência documentada, com algumas lacunas de acesso e a simplificação de FRR. |
| 4. Originalidade e tese | **180/200** | Confirmação útil, tese refutável, trade-off nomeado e próximos passos enumerados; novidade incremental e frase de prioridade a corrigir. |
| 5. Consistência interna | **90/100** | Números e análises coerentes; pequenas tensões entre ressalvas metodológicas e formulações mais fortes. |
| 6. Correção factual | **125/150** | Resultados reproduzidos e registro local íntegro; discrepância cronológica e limites de verificação da precedência externa. |
| **Total** | **910/1000** | A regra dura de densidade não se aplica. |

NOTA: 910/1000
