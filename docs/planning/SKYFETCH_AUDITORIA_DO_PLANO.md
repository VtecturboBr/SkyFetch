# Auditoria NEXUS + Ponytail — SkyFetch PRJ.9

**Data:** 13/11/2026  
**Alvo:** `SKYFETCH_PLANO_MESTRE.md` (820 linhas), `SKYFETCH_PROMPT_PARA_CODEX.md`, NEXUS WEB v1.1, regras Ponytail `AGENTS.md`/`SKILL.md`, e código demonstrativo do SkyFetch em `main` (`07ef49787339c4418e43d06d8f07c7cde9564b67`).  
**Escopo:** revisão de especificação, compatibilidade com o enunciado, segurança, riscos de regressão, redução de complexidade e teste do motor JS já existente.  
**Sem alterações no repositório.** Não foram executados Flask/PostgreSQL, porque as dependências/servidor não estão disponíveis neste ambiente.

## Veredito

**REVISAR ANTES DE CODIFICAR.** A arquitetura (Flask + Jinja/JS nativo + psycopg + PostgreSQL) é proporcional e cumpre a atividade; **não** convém refazê-la. Foram identificadas ambiguidades implementáveis do plano e bugs reais do motor JavaScript demonstrativo, que o parser Python novo deve corrigir. A versão `SKYFETCH_PLANO_MESTRE_REVISADO_v1.1.md` incorpora as correções propostas aqui.

Prioridades: **P1** = deve resolver antes de implementar as partes afetadas; **P2** = risco ou lacuna de qualidade; **P3** = refinamento sem bloqueio. Não há evidência para afirmar que o backend final possui vulnerabilidade, porque ele ainda não foi implementado.

## Achados fundamentados

### A01 — P1 — Gramática aceita entrada vazia contradizendo o contrato
- **Evidência:** plano original linhas 243–252: `SEARCH := [INTRO] [EXPRESSION] [EXCEPT_PART]` pode gerar cadeia vazia, mas a matriz exige `empty-query` para string vazia; `voos` sozinho é uma busca válida.
- **Falha possível:** um parser fiel à gramática retorna os 5 registros para entrada vazia, ignorando `400/EMPTY_QUERY`.
- **Correção v1.1:** só permitir expressão vazia depois do token inicial `voo`/`voos`; sem prefixo exigir filtro ou `exceto` + filtro.
- **Teste obrigatório:** `''`/`'  '` -> 400; `'voos'` -> 5 resultados; `'exceto noturnos'` -> 3.

### A02 — P1 — Palavras de ligação/aliases longos não formam uma gramática completa
- **Evidência:** linhas 225–240 permitem `de/da/do/em/para`, mas `TERM` (245–250) não inclui ligações. `São José dos Campos` contém `dos` como parte do nome.
- **Falha possível:** `voos da latam em Belém` inválida, `São José dos Campos` fragmentado ou uso de stopwords para esconder erro.
- **Correção v1.1:** resolver alias mais longo antes de separação das ligações; aceitar ligações apenas entre termos válidos, nunca soltas; consumir todos os tokens.
- **Testes:** `voos da latam em Belém` -> 1; `voos São José dos Campos` -> 2; `voos latam de` -> 422.

### A03 — P1 — Validação lexical pode engolir trechos perigosos/desconhecidos
- **Evidência:** linhas 235–241 pedem normalização, mas não definem a ordem exata entre rejeitar pontuação e normalizar. No motor atual (`static/js/search.js`) a função `normalize()` remove símbolos e `getFilters()` procura aliases presentes em qualquer trecho.
- **Bug reproduzido no JS:** `'voos latam xyz'` -> 3 registros; `'latam; DROP TABLE cidades'` -> 3 registros; `'voos latam ou'` -> 3 registros, quando deveriam ser inválidos. **Não é SQL injection no JS atual**, porque não há SQL ali.
- **Correção v1.1:** validação de caracteres antes de normalizar, consumo total do fluxo de tokens, operador incompleto -> 422, sem substrings parciais.
- **Testes:** entradas acima -> 422 e nenhuma ida ao banco; SQL deve continuar parametrizado.

### A04 — P1 — `CREATE TABLE IF NOT EXISTS` não garante schema compatível
- **Evidência:** linhas 157–217 criam tabelas com `IF NOT EXISTS` e fazem seed com `ON CONFLICT DO NOTHING`, assumindo estrutura esperada.
- **Falha possível:** banco já contém tabela homônima de colunas/tipos/constraints incorretos; criação é pulada e integração falha depois, com erro pouco claro. Com registros preexistentes, contagens totais 4/4/5 não são garantia.
- **Correção v1.1:** testar criação e seed em banco novo isolado; validar schema existente, PK e ausência de cidades órfãs sem apagar dados; não presumir contagens em banco compartilhado.
- **Testes:** executar seed duas vezes em banco novo; schema incompatível deve ser detectado e documentado.

### A05 — P2 — Código de status para esquema ausente confunde operação e configuração
- **Evidência:** tabela de falhas linha 582 sugere 503 para banco alcançável mas com tabelas ausentes; linha 425 define 503 para banco indisponível e 500 para erro inesperado.
- **Consequência:** tratar defeito de configuração como indisponibilidade temporária dificulta diagnóstico.
- **Correção v1.1:** 503 para conexão/timeout indisponíveis, 500 genérico para esquema ausente/incompatível; log seguro com instrução local.
- **Teste:** simular conectividade indisponível (503) e tabela ausente (500), sem traceback nem DSN no JSON.

### A06 — P2 — Responsabilidades de nomes formatados duplicadas
- **Evidência:** seção 3.1 dá ao frontend o dever de formatar nomes; 4.2 fala em mapa no frontend; resposta de API (linhas 370–396) já traz `companyName`, `cityName`, `shiftName`. O JS atual depende exatamente desses campos.
- **Consequência:** duas fontes de verdade de nomes de cidades, com divergências possíveis.
- **Correção v1.1:** manter esses três campos na API Python e fazer o JS somente apresentá-los, sem mapa próprio.
- **Teste:** cada cartão utiliza nomes do JSON; nenhum catálogo de empresas/cidades restante no JavaScript.

### A07 — P2 — `AbortController` sozinho pode não proteger todas as atualizações de UI
- **Evidência:** seção 8.3 linha 463 permite `AbortController` **ou** contador, mas não obriga a verificar estado em `catch`/`finally`.
- **Consequência:** resposta/cancelamento da busca antiga pode desligar loading ou exibir erro enquanto a nova ainda está pendente.
- **Correção v1.1:** contador monotônico `requestVersion` verificado antes de cada mutação de UI e no `catch`/`finally`; abort opcional.
- **Teste:** simular duas buscas, resolver primeiro a segunda e depois a primeira; mostrar somente a segunda, inclusive no loading.

### A08 — P2 — Plano remove os testes JS sem substituição equivalente do frontend
- **Evidência:** linhas 468, 628, 653–673 orientam migrar `tests/search.test.cjs` para Python. Isso cobre parser/SQL, **não** fluxo assíncrono do navegador.
- **Consequência:** loading, erro de API, Enter, chips e URL perdem verificação automatizada/documentada.
- **Correção v1.1:** mover os testes de regra de negócio para Python e manter um smoke test leve/documentado para o DOM + fetch; não obrigar Playwright/React no MVP.
- **Teste:** execução manual reprodutível com evidência ou automação leve se houver ambiente, incluindo resposta fora de ordem.

### A09 — P2 — Histórico/URL sem decisão concreta
- **Evidência:** linha 466 deixa `pushState` vs `replaceState` aberto, com obrigação adicional de `popstate` se usar `pushState`.
- **Consequência:** agente pode adicionar complexidade de navegação e errar `?q=` vazio.
- **Correção v1.1:** preferir `replaceState`, diferenciação entre parâmetro ausente e presente-vazio, sem `popstate` no MVP.
- **Teste:** carregar `/` e `/?q=`, clicar chips, atualizar página, verificar valor exibido e resultado.

### A10 — P2 — Parâmetros HTTP duplicados não especificados
- **Evidência:** rota `GET /api/search?q=...` na seção 7.1 não define `?q=latam&q=gol`.
- **Consequência:** Flask pode tomar primeiro valor e ignorar outro sem avisar; clientes com comportamento distinto produzem semântica oculta.
- **Correção v1.1:** exigir exatamente uma ocorrência de `q`, resposta 422 para duplicação.
- **Teste:** `GET /api/search?q=latam&q=gol` -> 422, sem acesso ao PostgreSQL.

### A11 — P2 — Integridade referencial lógica requer teste
- **Evidência:** seção 4.1 corretamente explica por que FK direta para `cidades(cidade)` seria inválida: `cidade` é repetida por turno. Mas o plano inicial não verifica companhias com cidade sem qualquer turno.
- **Consequência:** uma linha de companhia pode desaparecer silenciosamente no `INNER JOIN` se cidade não existir em `cidades`.
- **Correção v1.1:** verificação SQL de órfãos no setup/testes, sem criar terceira tabela nem mudar esquema do professor.
- **Teste:** inserir cidade sem turno somente em banco descartável e verificar que validador detecta a inconsistência.

### A12 — P3 — Critérios de conclusão e setup são caros de reproduzir se ninguém tiver banco
- **Evidência:** seção 14.3 exige PostgreSQL real e `TEST_DATABASE_URL`, corretamente, mas não permite declarar entrega sem isso.
- **Recomendação:** manter a exigência e melhorar README para Windows com `psql` ou pgAdmin, checagem de versão/DB e instrução clara de como executar `pytest`. Não introduzir SQLite ou Docker obrigatórios.

## Otimizações seguras recomendadas

| Otimização | Ganho | O que preservar |
|---|---|---|
| **Flask único + templates existentes** | Menos serviços, builds e dependências | Página, acessibilidade e contratos de API |
| **Parser de gramática restrita** | Sem IA externa, sem framework de NLP | Validação de todos os tokens e precedência |
| **Um módulo de parser + um de consultas** | Camadas pequenas e fáceis de testar | SQL parametrizado, errores tipados |
| **Reutilizar `makeResult()` e CSS** | Evita refazer UI aprovada | Estados de loading, erro, acessibilidade |
| **Mapa de nomes apenas no Python** | Remove duplicação e risco de divergência | Campos display da API |
| **`requestVersion` no JS** | Protege concorrência com pouquíssimo código | `catch`/`finally` versionados |
| **`replaceState` em vez de `pushState`** | Dispensa `popstate` e histórico de buscas | Valor `q` restaurável por refresh |
| **Conexão por requisição, sem pool/cache** | Menos configuração para 8 registros | Timeout e fechamento garantido |
| **SQL com JOIN/UNION/EXCEPT só quando necessário** | Consultas legíveis e cumprem PRJ.9 | Provar operadores no SQL real |
| **Testes curtos em camadas** | Menos falsos positivos e regressões | Unitários, contrato HTTP, banco real, UI smoke |

## O que **não** é recomendação de otimização

Não trocar PostgreSQL por SQLite, não usar ORM para esconder operações exigidas pelo professor, não reescrever HTML/CSS em React, não remover SQL parametrizado ou mensagens de erro para reduzir linhas, não cachear resultados redundantes, não adicionar Redis/Docker/Playwright como requisitos obrigatórios para um exercício pequeno.

## Evidências de execução

1. **Repo SkyFetch** confirmado no HEAD `07ef49787339c4418e43d06d8f07c7cde9564b67`; não havia PR de integração no momento da verificação.
2. **`node --test tests/search.test.cjs`** no snapshot local da baseline: **8 testes passaram; 0 falharam**.
3. **Probes manuais JS** via Node confirmaram casos aceitos indevidamente: `voos` → unrecognized; `voos latam ou` → success/3; `voos latam xyz` → success/3; `voos latam e` → success/3; `latam; DROP TABLE cidades` → success/3.
4. **Não executado:** backend Flask, `pytest` Python, banco PostgreSQL, SQL real `UNION/EXCEPT`, testes visuais depois de integração. O ambiente observado não tinha Flask nem psycopg instalados; psql não foi encontrado no PATH.
5. **Fonte técnica conferida:** documentação oficial PostgreSQL para `UNION/EXCEPT`, Psycopg 3 para conexão/SQL parametrizado, Flask para test client.

## Checagem dos documentos auxiliares

- **Prompt para Codex:** depende do nome do arquivo mestre e repetia critérios menos específicos. Foi emitido `SKYFETCH_PROMPT_PARA_CODEX_REVISADO_v1.1.md`, alinhado à revisão.
- **NEXUS WEB v1.1:** metodologia de organização, não um runtime. Não foi encontrado um bloqueador de arquitetura SkyFetch; não usar seus comandos textuais como testes executados.
- **Ponytail:** enfatiza menor alteração completa e testes de caminhos arriscados; preservar isso. Não adicionar Ponytail como dependência de produção. Instruções de sua documentação não provam testes do SkyFetch.

## Entrega / status

- **Concluído:** auditoria de Markdown, código demonstrativo e riscos; plano mestre revisado; prompt atualizado; testes de demonstração JS executados.
- **Não realizado:** implementação de Flask/PostgreSQL, correção do código no GitHub, criação de branch/PR ou execução de teste SQL.
- **Próxima ação única:** entregar `SKYFETCH_PLANO_MESTRE_REVISADO_v1.1.md` e `SKYFETCH_PROMPT_PARA_CODEX_REVISADO_v1.1.md` ao agente implementador, e iniciar pela revalidação do HEAD e testes da baseline.
