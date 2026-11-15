# PROMPT MESTRE REVISADO v1.2 PARA CODEX — IMPLEMENTAÇÃO DO SKYFETCH PRJ.9

> **Atualização posterior:** etapas 4 e 5 foram autorizadas e implementadas. O registro abaixo sobre preparação até a etapa 3 é histórico. Consulte `.nexus/plans/implementacao/`; instruções antigas de abrir PR não concedem autorização para publicação.

> **Escopo atual:** referência para implementação futura. Em 14/11/2026 o usuário autorizou somente as etapas 1–3: repositório, ajustes do plano e ambiente. Consultar `.nexus/plans/preparacao/tasks.md`. As instruções abaixo não autorizam iniciar schema/seed, parser, API, UI ou PR.

> **Use este arquivo junto do `SKYFETCH_PLANO_MESTRE_REVISADO_v1.2.md`.** O plano mestre é a especificação principal. Este arquivo orienta a execução quando ela for autorizada.

Você é o engenheiro responsável por transformar o projeto GitHub **https://github.com/VtecturboBr/SkyFetch** numa aplicação funcional com **Python, Flask, PostgreSQL e busca textual** segundo o enunciado acadêmico PRJ.9.

## Ordem inicial

1. Leia integralmente o arquivo anexo **`SKYFETCH_PLANO_MESTRE_REVISADO_v1.2.md`** e use suas seções de arquitetura, modelo de dados, gramática, API, tarefas e critérios de aceite como contrato.
2. Consulte o repositório **atual** antes de editar qualquer coisa. O baseline observado no planejamento foi `main`/`07ef49787339c4418e43d06d8f07c7cde9564b67`, mas pode ter mudado. Compare e preserve todas as alterações novas.
3. Adote **NEXUS** como metodologia de planejamento/verificação (se o arquivo correspondente foi fornecido). Aplique os princípios **Ponytail** do repositório https://github.com/DietrichGebert/ponytail: a menor mudança completa, reutilização, sem overengineering, sem eliminar segurança/acessibilidade/testes. Não instale Ponytail como dependência do site.
4. Crie branch **`feature/skyfetch-postgres-search`** (ou nome livre equivalente se ocupado); nunca implemente direto em `main`.
5. Implemente as tarefas **T001–T012** na ordem permitida pelas dependências. Priorize fatias completas, com testes reais, em vez de gerar todos os arquivos antes de testar.

## Invariantes obrigatórios

- Mantenha o layout atual (HTML/CSS/JS) e as cores/identidade SkyFetch; **não** refaça o frontend nem introduza React.
- Use as duas tabelas do enunciado: `companhia_aerea(companhia,cidade)` e `cidades(cidade,turno)` com chaves compostas e seed idempotente.
- A busca real deve rodar no backend e usar **JOIN, UNION e EXCEPT no PostgreSQL**, com **valores parametrizados**. `e` significa AND; `ou` UNION; `exceto` EXCEPT sobre o resultado positivo completo.
- O parser Python deve reconhecer `latam`, `gol`, `azul`, `sjc`, `bel`, `campinas`, `manhã`, `tarde`, `noite` e aliases especificados no plano. **Consumir 100% da frase**, reconhecer nomes multi-palavra antes de ignorar ligações (`São José dos Campos`), aceitar `voos` isolado como busca de todas as cinco combinações, rejeitar entrada vazia, pontuação desconhecida, operador solto, cauda desconhecida e `q` repetido. Entrada inválida não pode retornar resultado parcial enganoso.
- O navegador usa `GET /api/search?q=...` e renderiza exclusivamente JSON do servidor. A API Python fornece `companyName/cityName/shiftName` para os cartões existentes: não recriar mapa de exibição no JS. Depois da migração e dos testes, remova o mecanismo JavaScript de dados fictícios para não deixar duas fontes da verdade.
- Preserve estados de UI `loading`, `success`, `no-results`, `invalid-query`, `service-unavailable` e erro inesperado. Use um token crescente `requestVersion` com checagem inclusive no `catch`/`finally` para impedir que uma busca antiga sobrescreva a recente. Use `history.replaceState` para `?q=` sem adicionar entradas ao histórico; diferencie `q` ausente de `?q=` vazio.
- Sem segredos em arquivos versionados, sem debug em produção, sem HTML dinâmico inseguro, sem fallback silencioso para dados de demonstração quando o banco falha.
- O projeto continua usando dados **fictícios/didáticos** do professor: não apresentar resultados como voos reais.
- Evite dependências extras, ORMs, microserviços, abstrações genéricas e recursos não pedidos.

## Sequência e verificação

1. **Baseline:** confirme SHA, arquivos, testes atuais e branch isolada.
2. **Banco:** use `SETUP_DATABASE_URL` para schema/seed e `DATABASE_URL` somente para leitura da aplicação. Testes usam exclusivamente `TEST_DATABASE_URL`, com outro owner e outro banco. Crie `db/schema.sql` e `db/seed.sql`; execute contra PostgreSQL isolado e confira 4 registros de companhias, 4 de cidades e 5 combinações no JOIN. Seed repetida não duplica. **Detecte esquema incompatível apesar do `IF NOT EXISTS` e cidades órfãs**. Nunca limpe banco alheio para atingir contagens.
3. **Parser:** implemente módulo Python separado do Flask. Teste acentos, aliases multi-palavra, ligações opcionais bem posicionadas, precedência `e > ou > exceto`, entrada vazia vs `voos`, operadores incompletos, termos desconhecidos, caracteres especiais, `q` duplicado e combinações contraditórias.
4. **SQL:** implemente construtor seguro com conjuntos `UNION`/`EXCEPT` e placeholders psycopg; teste no PostgreSQL real os exemplos da seção 5.5 do plano.
5. **Flask:** exponha `GET /api/search` com JSON uniforme e HTTP 200/400/422/503/500 conforme o contrato; use `DATABASE_URL` do ambiente.
6. **Frontend:** conecte o `fetch` à API, preserve cartões/CSS, implemente estados e proteção contra respostas fora de ordem.
7. **Limpeza:** elimine a duplicidade entre parser JS e Python depois de comprovar cobertura. **Preserve pelo menos um teste/smoke verificável de UI assíncrona** (loading, erros, resultados fora de ordem e URL) para evitar perder a cobertura de comportamento de navegador. Atualize scripts de teste e README para Windows.
8. **QA:** execute unitários, Flask test client, integração PostgreSQL e inspeção visual quando houver navegador disponível. Diferencie banco desconectado (503) de banco conectado com tabelas ausentes/incompatíveis (500). Registre exatamente quais testes passaram/falharam/não foram executados.
9. **Entrega:** crie PR para revisão **sem mesclar**. Descreva alterações, comandos, resultados reais, limitações e riscos remanescentes.

## Evidência obrigatória no encerramento

Entregue um resumo com: (1) URL da branch/PR, (2) arquivos alterados e propósito, (3) testes executados com saída/resumo, (4) matriz de critérios de aceite marcados **CONFIRMADO / FALHOU / NÃO VERIFICADO**, (5) pendências e (6) próxima ação recomendada.

Não alegue que PostgreSQL ou o navegador foram testados se o ambiente não permitiu. Não mescle na `main`. Não inicie auditoria profunda de qualidade além dos testes do próprio desenvolvimento; o usuário solicitará uma revisão posterior separada.

**Comece agora pela T001: ler o estado atual do projeto e confirmar baseline.** Não faça perguntas por detalhes que o plano já responde; se surgir impedimento real, documente-o e complete as partes independentes possíveis.

> **Auditoria:** leia também `SKYFETCH_AUDITORIA_DO_PLANO.md`. A revisão corrigiu a especificação; não é um teste de implementação e não autoriza pular testes reais.
