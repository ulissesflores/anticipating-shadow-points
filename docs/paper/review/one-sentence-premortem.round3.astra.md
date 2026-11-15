# Parecer do GPT-6 Astra, artigo 3, rodada 3 (2026-11-15)

Canal: codex exec, modelo gpt-6-astra, esforço high, pasta somente leitura, commit d70b7b0. Texto integral abaixo.

Recomendo **revisão maior, concentrada na interpretação**. O resultado primário é reproduzível nos arquivos fornecidos, e os acréscimos exploratórios são relatados com transparência. As principais fragilidades são conclusões causais extraídas de subgrupos selecionados depois do tratamento, uma afirmação excessiva sobre preservação da relevância e lacunas na conferência de algumas referências.

Li o manuscrito inteiro. Executei, sem escrita, as 21 funções de teste de números do artigo: todas passaram. Recalculei, a partir dos vereditos, as estimativas e permutações dos dois juízes originais, da segunda régua e do terceiro juiz: coincidiram com os resultados armazenados. A verificação local do ledger também passou: 1.907 entradas, 26 substituídas. Não executei `run_all.py`, pois ele escreve arquivos.

Nas referências abaixo, **M** significa `repo/paper/one-sentence-premortem.md`; **S** significa `repo/benchmark/study-2026-11b/`.

**1. Críticas**

1. **Erro demonstrado — o resumo confunde retirar rodadas com retirar estratos.**  
   **Local:** Abstract e Resumo, M:12 e M:18: “Without three trials […] the difference is 10.1 points”; também Seção 7, objeção 6, M:402.  
   **Problema:** +10,1 corresponde à exclusão dos três estratos completos, não apenas das três rodadas. São retiradas 30 observações, incluindo 27 sem erro.  
   **Evidência:** `S/sensitivity.json:8–23`: `without_strata` = 0,1010; `without_trials` = 0,1051. A Tabela 7 distingue corretamente as duas análises.  
   **Gravidade:** menor; não altera a decisão.  
   **Correção:** escrever “excluding the three strata containing network-error trials”, ou usar +10,5 para a exclusão apenas das rodadas. Corrigir os dois idiomas.  
   **Incerteza:** baixa.

2. **Erro de inferência demonstrado — os subgrupos não excluem explicações causais.**  
   **Local:** Seção 5.4, M:277: “The gain is therefore not explained by longer tables”; Seção 7, objeção 13, M:416: “The tool call does not explain the gain”.  
   **Problema:** número de linhas e gravação do plano são comportamentos posteriores à intervenção, alterados por ela. Condicionar a análise nesses comportamentos rompe a comparabilidade produzida pela alocação original. Dez linhas também podem conter quantidades diferentes de riscos e detalhes.  
   **Evidência:** `S/describe.py:237–246` seleciona tabelas com dez linhas; `:280–284` seleciona respostas que gravaram arquivo. Restam, respectivamente, 17 e dez estratos. O manuscrito informa 56 versus 82 tabelas completas e 59 versus 22 gravações em Opus.  
   **Gravidade:** maior.  
   **Correção:** apresentar essas comparações como descrições compatíveis com várias explicações. Para separar mecanismos, fixar experimentalmente o orçamento de saída e o comportamento de gravação. Sonnet mostra que gravar arquivo não é necessário para haver efeito; não resolve a mediação em Opus.  
   **Incerteza:** baixa sobre a limitação; magnitude do viés não verificada.

3. **Excesso inferencial — ausência de queda observada não demonstra preservação da relevância.**  
   **Local:** Seção 5.4, M:275: “relevance did not fall, so the coverage gain was not bought with vaguer rows”; repetido em M:293 e M:396.  
   **Problema:** as médias observadas são favoráveis, mas o estudo não estabelece não inferioridade nem equivalência. Os testes de aumento, sobretudo após excluir erros, não sustentam a conclusão geral de que não existe perda.  
   **Evidência:** `S/PROTOCOL.md:47–60` não fixa margem de não inferioridade; `S/sensitivity.json:63–87` mostra diferenças positivas, com p = 0,0914 ou 0,0536, dependendo da exclusão.  
   **Gravidade:** maior para a interpretação, sem comprometer o efeito primário de cobertura.  
   **Correção:** “Não observamos redução na relevância média julgada; a análise não foi desenhada para demonstrar não inferioridade.” Manter a distinção já correta entre plausibilidade e correção factual.  
   **Incerteza:** baixa; “did not fall” isoladamente poderia ser descritivo, mas a conclusão introduzida por “so” ultrapassa essa leitura.

4. **Imprecisão demonstrada — “adicionar” descreve mal a intervenção executada.**  
   **Local:** introdução, M:26: “adding the sentence […] to a planning request”; conclusão, M:440: “One sentence placed before a planning request”.  
   **Problema:** o tratamento substitui “Plan this change.” pela frase experimental. Não conserva a instrução explícita de planejamento e acrescenta outra frase. Isso importa porque a avaliação recompensa a tabela de riscos, sem medir a qualidade do planejamento.  
   **Evidência:** `S/run.py:51–55` e Tabela A1, M:549–550. O próprio artigo descreve corretamente a substituição na Seção 4.3.  
   **Gravidade:** menor, porque os pedidos completos estão disponíveis.  
   **Correção:** harmonizar resumo, introdução e conclusão com “replacing the planning instruction with…”. Um braço que preserve “Plan this change.” permitiria testar uma intervenção estritamente aditiva.  
   **Incerteza:** baixa sobre os pedidos; efeito dessa diferença não verificado.

5. **Lacuna documental — alguns resultados bibliográficos são afirmados além da verificação disponível.**  
   **Local:** Seção 2.1, M:55: “178 students […] 25.0 […] 14.0 […] 12.4”; M:57, caracterização do desenho de Veinott e Lehman.  
   **Problema:** as notas fornecidas não sustentam tratar esses resultados como conferidos na fonte primária.  
   **Evidência:** `fontes/README.md:74` declara que Veinott et al. (2010) foi consultado apenas indiretamente e recomenda não citar os números; `:75` declara não lidos os resultados de Veinott e Lehman (2024). `fontes/sources.jsonl:18–19` mantém essas restrições.  
   **Gravidade:** menor para a tese central, mas relevante para correção factual.  
   **Correção:** fornecer a conferência primária com página/tabela ou retirar os números e limitar a caracterização do estudo de 2024 ao que foi efetivamente consultado.  
   **Incerteza:** **não verificado**; não estou afirmando que os números sejam falsos. Metadados e conteúdo precisam de avaliações separadas.

6. **Suspeita metodológica — a interrupção pode ter produzido seleção por duração.**  
   **Local:** Seção 8, item 2, M:427: “Trials in flight […] left no record and ran again”.  
   **Problema:** tentativas interrompidas desapareceram, e apenas suas repetições entraram no conjunto final. Se duração e conteúdo estiverem relacionados, interromper as tentativas ainda em andamento pode selecionar realizações específicas, mesmo sem seleção deliberada pelo resultado.  
   **Evidência:** `S/PROTOCOL.md:115–118` registra o procedimento, mas não quantifica nem identifica as tentativas interrompidas. A Tabela 8 mostra durações diferentes entre condições.  
   **Gravidade:** maior como ameaça à validade interna ainda não quantificada.  
   **Correção:** informar quantidade, identificadores, condições, tempos decorridos e regra de descarte, se recuperáveis; caso contrário, declarar a impossibilidade de avaliar essa seleção.  
   **Incerteza:** alta quanto ao impacto. Há evidência da interrupção, não de que ela tenha produzido viés favorável.

7. **Lacuna demonstrada no pacote recebido — parte da trilha documental prometida não está disponível.**  
   **Local:** Seção 7, M:390, e Tabela 11, M:463: relatórios em `docs/paper/review/`; Seção 2.5, M:85, registro da busca bibliográfica.  
   **Problema:** `repo/docs/paper/review/` não existe nesta cópia. As notas em `fontes/` documentam boa parte da busca, mas não permitem conferir as consultas adicionais nos quatro idiomas anunciados.  
   **Evidência:** inventário local; `fontes/README.md:83–98` lista consultas e limitações, sem registrar essas consultas multilíngues.  
   **Gravidade:** menor.  
   **Correção:** incluir os relatórios e o registro completo das consultas no pacote de replicação, com caminhos estáveis.  
   **Incerteza:** baixa sobre a ausência local; existência no repositório público ou em outra versão: **não verificado**.

8. **Erro descritivo demonstrado — a Figura 12 não contém “every estimate”.**  
   **Local:** Seção 6, M:374 e M:378: “every estimate […] side by side”.  
   **Problema:** a figura termina na segunda régua de +6,7; não inclui os resultados posteriores da Tabela 10, entre eles +4,2, +5,6, +7,7 e +9,0.  
   **Evidência:** `repo/output/figures/fig13_effects.png`, comparada com M:357–362.  
   **Gravidade:** menor.  
   **Correção:** atualizar a figura ou substituir “every” por “selected”, explicitando o critério de seleção.  
   **Incerteza:** baixa. Isso não prova seleção oportunista: o corpo apresenta os números omitidos.

9. **Preferência editorial — ordenar as tabelas pela primeira aparição.**  
   **Local:** Tabela 4 em M:161 antecede a Tabela 3 em M:202.  
   **Problema:** a sequência dificulta a navegação, embora as remissões sejam compreensíveis.  
   **Evidência:** ordem das duas tabelas no manuscrito.  
   **Gravidade:** menor.  
   **Correção:** renumerar e atualizar remissões e testes.  
   **Incerteza:** nenhuma sobre a ordem; a importância é editorial.

**2. Validade, adversarialmente**

**(a) Há números divergentes?**  
Não encontrei divergência nas estimativas recalculadas, nas tabelas verificadas ou nos números vinculados pelos 21 testes. Há, contudo, a associação incorreta de +10,1 à retirada de apenas três rodadas no resumo e na objeção 6. O número existe nos dados, mas descreve outra análise. Os testes passam porque verificam sua presença, sem verificar adequadamente essa associação semântica.

**(b) O desenho sustenta as afirmações?**  
Sustenta um efeito da diferença entre os dois pedidos sobre a cobertura julgada das tabelas finais, neste conjunto de tarefas, modelos e configurações. O artigo limita corretamente efeitos em código, generalização entre fornecedores e explicação do mecanismo. Também não reivindica aumento robusto de relevância.

As exceções são as conclusões fortes sobre ausência de perda de relevância e exclusão das explicações por extensão da tabela ou gravação do plano. A formulação “adding” também merece correção.

**(c) A regra aplicada coincide com o protocolo? Todos os desvios estão declarados?**  
Sim, para a análise principal: pelo menos 18 estratos completos, p combinado abaixo de 0,05 e p abaixo de 0,05 em ambos os modelos. Os 24 estratos registrados satisfazem a completude definida pelo tratamento pré-fixado dos erros. `S/analyze.py:96–105` implementa essa regra; o recálculo retorna “confirmed”.

Os desvios materiais que identifiquei estão declarados na Seção 8 ou nas respectivas seções metodológicas. Isso inclui pausa, correção de diretório, redação de caminhos, plugins, interrupções por cota e acréscimos exploratórios.

**Ressalva de verificação:** a cadeia local íntegra demonstra consistência dos arquivos e registros. A cópia não contém histórico Git, e não validei externamente os blocos Bitcoin ou o arquivo Software Heritage. Portanto, a certificação independente da anterioridade pública permanece **não verificada**; não a considero refutada.

**(d) Erros de rede e análises não planejadas são tratados honestamente?**  
Sim. O artigo declara que os três erros pertencem ao controle e favorecem a hipótese quando recebem zero. Mostra exclusões de rodadas e estratos, limite extremo de cobertura completa e repetições posteriores. Mantém a análise confirmatória original e identifica as demais como exploratórias. A confusão do resumo deve ser corrigida, mas não encontrei ocultação do resultado menos favorável.

**(e) A novidade resiste a InvThink e Patel et al.?**  
Resiste **na formulação estreita e perante a literatura documentada no pacote**. InvThink já sustenta enumeração antecipatória; Patel já testa previsão de falhas em agentes de código. O artigo reconhece ambos. A contribuição distinta combina dose de uma frase, planejamento de mudanças e cobertura de riscos elicidados separadamente.

`fontes/README.md:26–28` e `:90` apoiam essas distinções. O manuscrito usa os números da tabela de Patel, evitando a discrepância do resumo daquela fonte registrada nas notas. Isso sustenta novidade incremental, não prioridade sobre o mecanismo geral. A inexistência universal de antecedentes continua **não verificada**, e “to our knowledge” é indispensável.

**(f) A segunda régua é relatada honestamente?**  
Sim. Conferem 111 riscos, 55,8% → 62,5%, +6,7 pontos, p = 0,0002, e 16 estratos positivos. A leitura segue `yardstick2/ADDENDUM.md:24–26`, que exige efeito positivo e significância **combinada**, não confirmação separada nos dois modelos.

O resumo, a discussão e a conclusão apresentam os tamanhos das duas réguas. O texto declara a redução, a incompletude do segundo juiz e a impossibilidade de atribuir toda a diferença à redação. Também informa que Opus perde significância no limite extremo. Não encontrei escolha exclusiva da estimativa maior.

**(g) Os dois acréscimos são relatados honestamente?**  
Sim, com a ressalva cronológica já indicada. Conferem:

- Astra na segunda régua: +9,0 sob a regra original, +6,5 no limite extremo e +7,7 com repetições.
- Gemini via API com repetições: +10,5 na régua original e +5,6 na segunda.
- Conferência de canal: 281 decisões, 98,2% de concordância, κ = 0,96, médias de 56,4% e 56,0%.

Os adendos aparecem no ledger antes dos registros dos respectivos resultados: entradas 1604–1605 antes de 1607; 1862–1866 antes de 1867. Isso é compatível com a cronologia declarada, embora o momento de registro de um resultado não certifique sozinho o momento da chamada.

As linhas fixadas não foram substituídas. M:368 declara operador conhecedor do resultado, possível mudança do modelo, fornecedor compartilhado entre Astra e GPT-OSS e troca de canal. O texto preserva Gemini +6,7 apesar de Astra produzir +9,0. Os vereditos incompletos do canal original permanecem pendentes, não disfarçados de concluídos.

**(h) Que ameaça importante falta declarar?**  
A principal é **seleção posterior ao tratamento nas análises de mecanismo**: tabelas completas e gravação do plano são consequências potenciais do pedido experimental. Os subgrupos não mantêm automaticamente a comparabilidade original. O artigo apresenta essas análises como respostas fortes às objeções, sem reconhecer essa ameaça.

Uma segunda ameaça insuficientemente tratada é a seleção das tentativas que terminaram antes do desligamento, enquanto as ainda em andamento foram descartadas e repetidas. Sua magnitude não pode ser determinada pelos registros apresentados.

**3. Rubrica**

| Dimensão | Nota | Justificativa |
|---|---:|---|
| 1. Estrutura formal | **138/150** | Tese inicial, subtítulo, resumos espelhados, palavras-chave e figuras úteis; recuo bibliográfico confirmado no DOCX. Pequenos problemas na ordem das tabelas e atualização da figura. |
| 2. Densidade técnica | **228/250** | Métodos, estimandos, testes e resultados concretos sustentam densidade amplamente superior ao mínimo; há repetição entre resultados, objeções e conclusão. Percentual exato de enchimento não foi codificado. |
| 3. Fundamentação | **127/150** | Fontes numerosas, recentes e variadas, incluindo artigos, livro, norma e documentação; lacunas de conferência em resultados humanos e na documentação da busca. |
| 4. Originalidade e tese | **178/200** | Tese testável, contribuição incremental clara, resultado não óbvio, trade-off nomeado e próximos passos enumerados; mecanismo geral já tem antecedentes reconhecidos. |
| 5. Consistência interna | **84/100** | Forte alinhamento entre dados e tabelas; perdas pela confusão rodadas/estratos, descrição aditiva e conclusões mais fortes que suas análises auxiliares. |
| 6. Correção factual | **126/150** | Resultados centrais reproduzidos e adendos transparentes; algumas afirmações bibliográficas e a anterioridade externa permanecem não verificadas. |

A regra dura não se aplica: densidade técnica acima de 100.

NOTA: 881/1000
