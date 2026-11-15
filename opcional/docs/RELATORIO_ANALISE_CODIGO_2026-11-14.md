# Relatório de análise do código — SkyFetch

> Registro histórico. Os cinco pontos foram tratados posteriormente; veja [correções e revisão posterior](RELATORIO_CORRECOES_PONYTAIL_2026-11-14.md).

**Data:** 14/11/2026. **Projeto analisado:** `C:\Users\peter\Downloads\SkyFetch-dev`, branch `feature/skyfetch-postgres-search`. HEAD: `07ef49787339c4418e43d06d8f07c7cde9564b67`; a implementação está no working tree e não nesse commit.

**Veredito:** o núcleo da busca funciona e a arquitetura é proporcional ao PRJ.9. Os testes de parser, API, PostgreSQL e interface passaram novamente. Não encontrei falha P0 ou P1 no escopo examinado. Há três achados P2, sendo um condicionado à adoção do PostgreSQL 18, e dois refinamentos P3. Recomendo tratar os pontos abaixo antes de considerar a revisão encerrada.

O código da aplicação não foi corrigido ou alterado nesta análise. Foram produzidos somente este relatório e os registros de revisão. A avaliação foi feita por um único agente, com inspeção estática, execução da suíte e verificações adicionais, sem alegar revisão independente por especialistas.

**Resumo dos achados**

| ID | Prioridade | Achado | Evidência |
|---|---|---|---|
| A01 | P2 | Página descarta silenciosamente parâmetros `q` repetidos | Reproduzido no Chrome e comparado com a API |
| A02 | P2 | Contraste de textos pequenos abaixo de 4,5:1 | Cores computadas no navegador e cálculo de luminância |
| A03 | P2, condicionado | Validador de schema rejeita a representação de NOT NULL do PostgreSQL 18 | Análise, documentação oficial e projeção de catálogo; sem servidor 18 real |
| A04 | P3 | Requisição sem resposta pode manter loading sem prazo definido | Retenção controlada no browser e inspeção do JS |
| A05 | P3 | Documento de ambiente ainda informa oito testes JS | Diverge da suíte atual de onze testes |

P2 indica impacto moderado na experiência ou compatibilidade. P3 indica melhoria de robustez ou documentação. Nenhum desses achados comprova exploração de segurança ou perda de dados.

**A01 — P2 — URL com `q` repetido é reinterpretada pela página**

Referências: `static/js/app.js:163`, `static/js/app.js:129` e `app.py:37`.

Ao abrir `/?q=latam&q=gol`, o frontend lê apenas o primeiro valor com `URLSearchParams.get('q')`. Em seguida, `searchParams.set` remove a duplicação da URL e a requisição para a API contém somente `q=latam`.

Na reprodução, a URL terminou como `/?q=latam`, o campo mostrou `latam` e apareceram três combinações. Já `GET /api/search?q=latam&q=gol` retornou corretamente HTTP 422 com `UNSUPPORTED_SYNTAX`.

O problema é a inconsistência entre as duas entradas: um endereço ambíguo compartilhado pelo usuário resulta em uma pesquisa parcial, sem aviso de que outro valor foi descartado. Não é uma falha de parametrização SQL nem um desvio da validação no endpoint; a página reconstrói a requisição antes que o endpoint possa rejeitá-la.

Recomendação: verificar `getAll('q')` no carregamento e apresentar erro de duplicação ou encaminhar a duplicação para a API, sem normalizá-la silenciosamente antes da validação. Manter o comportamento atual para parâmetro ausente e parâmetro único vazio.

Teste de regressão sugerido: cobrir `/?q=latam&q=gol`, `/?q=&q=latam`, `/?q=` e `/` em Node/browser. Para as duas primeiras entradas, não exibir resultados parciais nem reescrever silenciosamente a pesquisa para um único valor.

**A02 — P2 — Alguns textos informativos têm contraste insuficiente**

Referências: `static/css/style.css:48`, `:78`, `:81`, `:97` e `:104`.

As cores foram obtidas por `getComputedStyle` no Chrome, usando o fundo branco efetivo dos componentes. O cálculo aplicou luminância relativa sRGB; não foi uma estimativa baseada no screenshot.

| Elemento | Tamanho | Cor | Contraste contra branco |
|---|---:|---|---:|
| Rótulo `TURNO` | 9 px | `#95a5af` | 2,54:1 |
| Aviso de dados fictícios | 11 px | `#7f929f` | 3,22:1 |
| Nota da base demonstrativa | 11 px | `#899ba5` | 2,88:1 |
| Texto do rodapé | 12 px | `#82929f` | 3,20:1 |
| Placeholder da busca | 16 px | `#8b9aa5` | 2,89:1 |

Esses textos não têm tamanho de texto grande e ficam abaixo do limiar de 4,5:1 descrito no [critério de contraste mínimo WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). O aviso de que os resultados são fictícios é informação útil e não apenas decoração.

O CSS é o mesmo da baseline: esse achado foi herdado do frontend original, não introduzido pela integração com a API.

Recomendação: escurecer os tons desses textos, preservando o tema navy/turquesa. Verificar novamente os estados normal, hover, foco e placeholder. Não é necessário redesenhar a página.

Teste sugerido: adicionar uma verificação leve das cores relevantes e complementar com inspeção de acessibilidade. A correção desses cinco exemplos não equivale a certificação WCAG completa.

**A03 — P2 condicionado — Compatibilidade do setup com PostgreSQL 18**

Referências: `scripts/setup_database.py:48`, `scripts/setup_database.py:52` e `README.md:25`.

`validate_schema` lê todas as linhas de `pg_constraint` e compara exatamente o conjunto de definições com PRIMARY KEY e CHECKs esperados. A verificação de NOT NULL já é feita separadamente por `pg_attribute.attnotnull`.

O PostgreSQL 18 passou a registrar as declarações NOT NULL também em `pg_constraint`, com `contype='n'`. Isso está explicitamente documentado nas [notas da versão 18](https://www.postgresql.org/docs/18/release-18.html) e no [catálogo oficial](https://www.postgresql.org/docs/18/catalog-pg-constraint.html).

Essas linhas adicionais não estão no conjunto esperado. Portanto, um schema correto pode ser rejeitado como incompatível no PostgreSQL 18, interrompendo o setup antes do seed.

Evidência executada: o schema atual passou na validação real do PostgreSQL 17.12. Depois, uma conexão de projeção forneceu ao mesmo validador as linhas reais mais as declarações NOT NULL correspondentes às colunas existentes; o validador lançou `SchemaError`. Essa projeção confirma a incompatibilidade da comparação, mas não foi execução contra um servidor PostgreSQL 18.

Não foi constatado impacto no ambiente atual, que usa 17.12. O achado importa para atualização de versão ou instalação em outra máquina; o README menciona PostgreSQL 17 ou outra versão suportada compatível.

Recomendação: tratar separadamente PRIMARY KEY/CHECK e NOT NULL, considerando os catálogos das versões suportadas. Preservar a rejeição de constraints ausentes, inválidas ou não validadas. Se o suporte ficar restrito a 17, tornar esse limite explícito nos requisitos e no setup.

Teste sugerido: executar schema/seed e validação em PostgreSQL 17 e 18, além dos casos de schema incompatível já existentes. Não considerar a compatibilidade com 18 aprovada somente pelo teste de projeção.

**A04 — P3 — Ausência de prazo no cliente para uma requisição pendente**

Referência: `static/js/app.js:118` e `static/js/app.js:130`.

O contador `requestVersion` protege corretamente contra respostas antigas, mas o `fetch` não recebe sinal de cancelamento ou prazo. Os limites de conexão/consulta do backend não encerram uma requisição que fica retida na rede antes de chegar à aplicação ou depois de receber os cabeçalhos.

Na verificação controlada, uma requisição retida por 6,5 segundos permaneceu em `aria-busy=true` com a mensagem “Buscando…”. A inspeção do código não encontrou mecanismo próprio que encerre essa espera; o resultado observado em 6,5 segundos não é, sozinho, prova de duração infinita em toda rede/navegador.

O formulário continua utilizável, e uma nova pesquisa pode substituir a antiga. Por isso, classifico como melhoria de robustez, sem bloquear o fluxo nominal. O plano não exigia um timeout específico no frontend.

Recomendação: definir um prazo de espera no cliente, mostrar uma mensagem de tentativa novamente e manter o versionamento inclusive em `catch/finally`. Testar também a expiração de uma busca antiga enquanto outra busca ainda está ativa.

**A05 — P3 — Contagem de testes desatualizada na documentação**

Referência: `docs/AMBIENTE_LOCAL.md:47`.

O documento afirma que Node é usado pelos “oito testes JavaScript existentes”, mas a suíte atual é `tests/app.test.cjs` e contém onze testes. Os oito testes antigos foram substituídos. A divergência não quebra a aplicação, mas pode confundir a conferência da entrega.

Recomendação: atualizar a informação ou referenciar o comando da suíte sem fixar a contagem no texto operacional.

**O que está funcionando e deve ser preservado**

- Separação pequena entre rota Flask, parser e repositório SQL, sem frameworks ou serviços desnecessários.
- Consumo completo da frase, reconhecimento de aliases longos e precedência consistente de AND, UNION e EXCEPT.
- Valores SQL parametrizados e identificadores obtidos de mapa fixo, com teste de tentativa de injeção mesmo contornando o parser.
- JOIN/UNION/EXCEPT executados no PostgreSQL e ordenação determinística dos resultados.
- Contrato de erros diferenciando entrada inválida, conexão indisponível e erro inesperado; logs sem mensagens brutas de conexão.
- Conexão da aplicação somente leitura e testes em banco separado com guarda explícita de configuração.
- DOM com `textContent`/`createElement`, sem inserção de pesquisa ou valores do banco por `innerHTML`.
- Proteção correta das atualizações de UI por versão, inclusive nos caminhos de erro e finalização.
- Ausência de fallback silencioso para arrays locais quando a API falha.
- Debug desligado por padrão; credenciais locais fora do versionamento.

**Verificações executadas nesta revisão**

| Verificação | Resultado |
|---|---|
| `python -m pytest -q` | 98 passaram, incluindo PostgreSQL real, sem skips nesta execução |
| `node --test tests/app.test.cjs` | 11 passaram |
| `python -m pip check` | Nenhum conflito de dependências |
| Enumeração do parser | 299.592 frases de 1–6 palavras, vocabulário reduzido de oito palavras, zero divergências contra gramática de referência e zero exceções inesperadas |
| Browser adicional | Duplicação de `q`, estilos computados/contraste e requisição retida examinados no Chrome real |
| Compatibilidade de catálogo | PostgreSQL 17 validado; projeção do catálogo 18 rejeitada pelo validador |
| Segredos locais | Nenhuma das três senhas locais apareceu nos arquivos compartilháveis examinados; `.env` e `.venv` ignorados pelo Git |
| `git diff --check` | Sem erros; aviso de conversão LF/CRLF do README não é falha de execução |

A enumeração do parser usa um subconjunto controlado do vocabulário; não cobre toda sequência Unicode nem substitui os testes da linguagem completa. `pip check` verifica consistência de dependências, não vulnerabilidades conhecidas.

Os resultados brutos dos probes de navegador estão em [review-evidence/browser-probes.json](../.nexus/plans/implementacao/review-evidence/browser-probes.json). A revisão não reexecutou o smoke visual completo anterior para substituir suas capturas; foram usados probes adicionais específicos.

**Ordem recomendada de correção**

1. Alinhar o tratamento de `q` repetido entre página e API e acrescentar casos de regressão.
2. Ajustar o contraste dos textos pequenos sem alterar a identidade visual.
3. Corrigir ou delimitar a compatibilidade do validador antes de usar PostgreSQL 18.
4. Acrescentar prazo de requisição no cliente e corrigir a contagem desatualizada na documentação.

As mudanças podem ser pontuais. Não encontrei justificativa para trocar Flask, introduzir React, ORM, pool, cache ou outra arquitetura neste exercício.

**Limites:** não foi executado servidor PostgreSQL 18 real, instalação limpa em outra máquina, teste de carga, auditoria de vulnerabilidades das dependências ou avaliação com leitor de tela. Não houve correção de código, commit, PR ou publicação nesta revisão.
