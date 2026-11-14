# SKYFETCH — PLANO MESTRE DE IMPLEMENTAÇÃO (REVISÃO v1.2)

> **Atualização posterior:** o usuário autorizou as etapas 4 e 5. O núcleo e a integração da interface foram implementados; os limites históricos abaixo sobre etapas 1–3 não se aplicam à nova autorização. Consulte `.nexus/plans/implementacao/` para evidências reais. Não há autorização para commit, push, PR ou deploy.

> **Revisão v1.2 (14/11/2026):** esclarece as ligações da gramática e separa credenciais de instalação, aplicação e testes. A preparação atual foi autorizada somente até a etapa 3 da conversa. Este plano completo não autoriza executar etapas posteriores. Os documentos originais v1.1 foram preservados fora deste repositório.

> As seções de descoberta e evidências v1.1 abaixo registram a análise histórica. O ambiente foi preparado posteriormente; consulte `docs/AMBIENTE_LOCAL.md` e `.nexus/plans/preparacao/` para o estado atual. Schema/seed e busca PostgreSQL ainda não foram implementados.

**Projeto:** SkyFetch — PRJ.9 · Busca de companhias aéreas por linguagem natural  
**Status:** documento de PLANEJAMENTO revisado após auditoria estática; nenhum código ou banco foi alterado por este plano  
**Referência do projeto:** https://github.com/VtecturboBr/SkyFetch  
**Referência de engenharia:** https://github.com/DietrichGebert/ponytail  
**Método de planejamento:** NEXUS WEB v1.1 (arquivo fornecido pelo usuário) + princípios Ponytail  
**Baseline inspecionada:** branch `main`, commit `07ef49787339c4418e43d06d8f07c7cde9564b67`, em 13/11/2026  
**Destinatário:** agente de programação (Codex ou equivalente)  
**Idioma da interface:** português brasileiro  
**Regra central:** preservar o frontend já aprovado e implementar apenas o necessário para cumprir o PRJ.9 com qualidade.

> **Registro de revisão v1.1 (13/11/2026):** foram corrigidas ambiguidades de gramática, stopwords, pontuação e aliases; responsabilidades de apresentação; critérios de validação do schema; classificação de falhas do banco; proteção contra respostas antigas; URL e testes de regressão do frontend. Ver `SKYFETCH_AUDITORIA_DO_PLANO.md`. Nenhuma implementação foi realizada.

> **Para a IA implementadora:** leia todo o documento antes de modificar arquivos. Revalide primeiro o estado atual do repositório. Trabalhe em uma branch separada, sem merge automático na `main`. Não substitua o frontend por React ou um novo layout. Implemente em incrementos verificáveis. O texto a seguir é uma especificação de trabalho, não evidência de software implementado.

---

## 1. Objetivo, escopo e definição de sucesso

### 1.1. Problema a resolver

O usuário digita uma frase curta — como `voos latam`, `voos latam e manhã`, `voos latam ou azul`, `voos gol exceto noturnos` — e a aplicação interpreta a frase, consulta tabelas em PostgreSQL e exibe combinações de **companhia + cidade + turno**. O enunciado exige **Python Flask, PostgreSQL e operações JOIN, UNION e EXCEPT**.

### 1.2. Resultado desejado

1. O usuário acessa a página SkyFetch existente e consegue pesquisar usando linguagem natural restrita.
2. O navegador envia a pesquisa à API Flask pelo mesmo domínio (`GET /api/search?q=...`).
3. O backend valida, normaliza, tokeniza e interpreta a frase de forma determinística.
4. Uma camada de consultas transforma filtros válidos em **SQL parametrizado**.
5. PostgreSQL executa `JOIN` para combinar tabelas, `UNION` para `ou`, `EXCEPT` para `exceto`, e filtros `AND` para `e`.
6. O backend devolve um contrato JSON documentado, com resultados e erros previsíveis.
7. O frontend renderiza exclusivamente a resposta do backend, incluindo estados de carregamento, vazio e falha.
8. Testes reproduzíveis comprovam comportamento, segurança básica e preservação do design.

### 1.3. Não objetivos (MVP)

- **Não** usar IA generativa, modelos de linguagem, APIs externas de aviação ou serviço de passagens.
- **Não** criar reservas, contas, pagamentos, login, autenticação, perfis, rotas reais, aeroportos ou horários de partida.
- **Não** introduzir React, Next.js, TypeScript, microserviços, ORMs, filas, Redis ou arquitetura de plugins.
- **Não** criar painel administrativo nem sistema de escrita de dados para usuários.
- **Não** alterar as cores, estrutura geral, identidade ou experiência central do frontend atual sem necessidade comprovada.
- **Não** fazer deploy público nem assumir custos de hospedagem nesta fase.

### 1.4. Nota de integridade semântica

As tabelas do professor dizem (a) onde a companhia opera e (b) que turnos existem naquela cidade. O cruzamento por cidade **não demonstra** que aquela companhia tenha voos reais em todos os turnos. Logo, o produto deve dizer **“combinações encontradas nos dados do exercício”**, não prometer horários reais. O banco deve reproduzir os dados do trabalho; não inventar partidas, números de voo ou preços.

---

## 2. Descoberta: estado real do repositório

### 2.1. Fatos conferidos no GitHub

| Arquivo atual | Função constatada | Direção |
|---|---|---|
| `app.py` | Flask com `GET /` servindo `templates/index.html`; `debug=True` no `__main__` | Manter entrada e adicionar rota de API; configuração segura de debug |
| `templates/index.html` | Layout SkyFetch pronto, com formulário, sugestões, painel de resultados e barra lateral | Preservar DOM/identidade; alterar apenas integração e estados necessários |
| `static/css/style.css` | Tema navy/turquesa, responsivo e regras de redução de movimento | Manter e aplicar ajustes pontuais de feedback/acessibilidade |
| `static/js/search.js` | Faz JOIN e filtragem de **arrays locais**, no navegador; não usa PostgreSQL | Substituir motor local pela implementação Python, após testes de paridade |
| `static/js/app.js` | Interage com formulário e renderiza cartões usando o motor local | Adaptar para `fetch('/api/search?...')`, estados e cancelamento de buscas anteriores |
| `static/favicon.svg` | Identidade SkyFetch | Preservar |
| `tests/search.test.cjs` | 8 testes do motor JavaScript demonstrativo | Usar como referência de comportamento; migrar cobertura para Python/integração antes de remover motor local |
| `requirements.txt` | Apenas `Flask>=3.1,<4.0` | Adicionar driver PostgreSQL e dependências estritamente necessárias |
| `README.md` | Informa que busca é demonstrativa e aponta próximas etapas | Atualizar apenas ao concluir cada etapa |
| `.gitignore` | Ignora `.env`, virtualenv, cache e node_modules | Preservar; versionar somente `.env.example` sem segredos |

**Não verificado:** execução local de Flask, conexão PostgreSQL real, implantação, acessibilidade automatizada e testes end-to-end em browser. Estes itens **não** devem ser declarados aprovados antes de serem realmente executados.

### 2.2. Análise da referência Ponytail

O Ponytail é um conjunto de instruções para agentes de desenvolvimento. A regra central de `AGENTS.md` e `skills/ponytail/SKILL.md` é: entender o fluxo existente e fazer a menor alteração completa; reutilizar código/recursos nativos, mas nunca cortar validação, segurança, tratamento de erros ou testes de lógica. Seus comandos de revisão e auditoria são úteis **mais tarde**, durante a inspeção de implementação, e não substituem testes. **Não instalar a ferramenta Ponytail como dependência da aplicação SkyFetch.**

### 2.3. Alternativas avaliadas

| Alternativa | Prós | Contras | Resultado |
|---|---|---|---|
| Flask monolítico + Jinja + JavaScript nativo + psycopg | Reúso máximo, simples, cumpre enunciado, teste fácil | Menos abstrações para expansão enorme | **ESCOLHIDA** |
| Flask API + frontend SPA React | Separação forte para produto grande | Ferramentas/build e reescrita sem necessidade | Rejeitada para PRJ.9 |
| Flask + SQLAlchemy/Alembic | ORM e migrações sofisticadas | Oculta JOIN/UNION/EXCEPT explícitos, mais dependências | Rejeitada para MVP |

**Quando reavaliar:** somente se a disciplina mudar o escopo (dados reais, muitos registros, painel de edição, autenticação ou hospedagem em produção).

---

## 3. Arquitetura de ponta a ponta

```mermaid
flowchart TD
    U[Usuário] --> F[Browser: Jinja HTML + CSS + JS]
    F -->|GET /| W[Flask: app.py]
    W -->|render_template| F
    F -->|GET /api/search?q=...| API[Flask: rota de pesquisa]
    API --> V[Validação de entrada]
    V --> P[Parser Python: frase para filtros]
    P --> Q[Construtor SQL seguro: JOIN / UNION / EXCEPT]
    Q --> D[psycopg: DATABASE_URL]
    D --> PG[(PostgreSQL: companhia_aerea + cidades)]
    PG --> D --> API
    API -->|JSON: status, items, total| F
    F --> R[Cartões e mensagens de estado]
```

### 3.1. Responsabilidades obrigatórias

**Frontend:** coletar frase, disparar requisição, exibir carregamento, resultados e falhas; **exibir nomes já fornecidos pela API**, sem manter outro catálogo de aliases/nomes; manter responsividade e acessibilidade. **Não** conhecer SQL nem guardar dataset duplicado.

**Rotas Flask:** hospedar a página, validar parâmetros HTTP, chamar serviços, serializar JSON, mapear erros para códigos HTTP e registrar falhas de infraestrutura sem expor segredos.

**Parser:** transformar texto em uma expressão estruturada, preservando precedência e negando entradas ambíguas. Não montar SQL diretamente nem acessar HTTP.

**Construtor/consulta:** receber filtros estruturados; aplicar somente colunas de uma lista de permissão; executar `JOIN`, `UNION` e `EXCEPT` seguros; retornar registros tipados/normalizados.

**PostgreSQL:** armazenar apenas as relações fornecidas pelo professor e responder consultas. Nenhuma lógica de apresentação na base.

### 3.2. Fluxo nominal de uma busca

1. Usuário pesquisa `voos latam ou gol exceto noturnos`.
2. JS faz `GET /api/search?q=voos+latam+ou+gol+exceto+noturnos`.
3. Flask verifica tamanho e forma de `q`.
4. Parser retorna **incluir** (`latam` OU `gol`) e **excluir** (`noite`).
5. SQL une as duas seleções com `UNION`; remove turno noturno com `EXCEPT`; a base é criada com `JOIN`.
6. PostgreSQL retorna três combinações (`latam/sjc/tarde`, `latam/bel/manhã`, `gol/bel/manhã`).
7. Flask responde JSON consistente.
8. JS cria 3 cartões usando APIs seguras do DOM.

### 3.3. Quem é a fonte da verdade?

- **Dados de companhias/cidades/turnos:** PostgreSQL.
- **Gramática, aliases e regras:** módulo Python único.
- **Textos/estilos de UI:** HTML/CSS/JS.
- **Estado temporário da busca no navegador:** frontend, sem persistência de resultados.
- **Configuração de banco:** variável de ambiente `DATABASE_URL`, nunca escrita no frontend ou versionada com credenciais.

---

## 4. Banco de dados: modelo e regras

### 4.1. Tabelas obrigatórias

Usar dois nomes físicos SQL legíveis e sem espaço: `companhia_aerea` e `cidades`, ambos em minúsculas.

```mermaid
erDiagram
  COMPANHIA_AEREA {
    text companhia PK
    text cidade PK
  }
  CIDADES {
    text cidade PK
    text turno PK
  }
  COMPANHIA_AEREA }o--o{ CIDADES : "JOIN por cidade (não FK)"
```

**Observação importante:** `cidades.cidade` não é único porque `sjc` tem dois turnos. Portanto, **não** criar `FOREIGN KEY (cidade)` apontando diretamente para `cidades(cidade)`; PostgreSQL exige destino único ou chave primária. Para permanecer nas duas tabelas do professor, usar relacionamento lógico por `JOIN`. Uma tabela extra `localidades` seria opção futura, mas não é necessária.

### 4.2. SQL de criação **proposto**, não executado

```sql
CREATE TABLE IF NOT EXISTS companhia_aerea (
    companhia TEXT NOT NULL CHECK (length(trim(companhia)) > 0),
    cidade TEXT NOT NULL CHECK (length(trim(cidade)) > 0),
    PRIMARY KEY (companhia, cidade)
);

CREATE TABLE IF NOT EXISTS cidades (
    cidade TEXT NOT NULL CHECK (length(trim(cidade)) > 0),
    turno TEXT NOT NULL CHECK (turno IN ('manha', 'tarde', 'noite')),
    PRIMARY KEY (cidade, turno)
);
```

- `PRIMARY KEY` composta impede linhas duplicadas com a mesma dupla de valores.
- Guardar códigos internos em minúsculas e sem acentos, por exemplo `manha`, `bel`, `sjc`.
- `CHECK` dos turnos mantém consistência do exercício.
- A **API Python** é a única responsável por fornecer `companyName`, `cityName` e `shiftName` a partir de um pequeno mapa estático de apresentação. O frontend apenas exibe essas propriedades por `textContent`, preservando `makeResult()`. Não manter um segundo mapa de apresentação em JavaScript.
- Valores futuros não mapeados devem usar fallback de texto escapado derivado do código, sem crash ou ocultação de resultados; aliases de entrada adicionais exigem aprovação explícita.
- Em dados maiores, avaliar índices conforme `EXPLAIN ANALYZE`; para 4 linhas em cada tabela não inventar otimização.

### 4.3. Seeds exatamente baseadas no enunciado

```sql
INSERT INTO companhia_aerea (companhia, cidade) VALUES
  ('latam', 'sjc'),
  ('latam', 'bel'),
  ('gol', 'bel'),
  ('azul', 'campinas')
ON CONFLICT DO NOTHING;

INSERT INTO cidades (cidade, turno) VALUES
  ('sjc', 'tarde'),
  ('sjc', 'noite'),
  ('bel', 'manha'),
  ('campinas', 'noite')
ON CONFLICT DO NOTHING;
```

**Número esperado:** 4 linhas em cada tabela e **5 combinações derivadas** do `JOIN` (latam/sjc/tarde; latam/sjc/noite; latam/bel/manhã; gol/bel/manhã; azul/campinas/noite). `ON CONFLICT DO NOTHING` torna o seed repetível, sem apagar dados existentes. **Atenção:** não comprova que um banco com tabelas preexistentes tem o formato esperado: antes do seed, verificar colunas, tipos, constraints e ausência de registros órfãos em ambiente isolado. Não limpar tabelas de produção para obter artificialmente as contagens do exercício.

### 4.4. Consulta base obrigatória (JOIN)

```sql
SELECT
    a.companhia AS company,
    a.cidade AS city,
    c.turno AS shift
FROM companhia_aerea AS a
INNER JOIN cidades AS c ON c.cidade = a.cidade;
```

A consulta base deve ser reutilizada conceitualmente nas operações de busca; não inserir as 5 combinações como uma terceira tabela materializada.

### 4.5. Inicialização e evolução

- Criar `db/schema.sql` e `db/seed.sql`, com instruções claras no README para executar com `psql`.
- Nenhum `DROP TABLE` ou `TRUNCATE` em scripts normais.
- Se uma alteração futura exigir migração, adicionar script numerado **aditivo e idempotente**, com estratégia de backup/rollback.
- Para a primeira entrega, SQL explícito é mais didático que ORM; não usar Alembic apenas para duas tabelas.
- Fazer um teste que execute seed duas vezes **num banco de teste inicialmente vazio** e confirme que os totais permanecem 4, 4, 5. Em banco que já contenha dados, as contagens podem ser maiores; verificar as cinco tuplas do exercício, sem presumir cardinalidade total.
- Detectar esquema incompatível em vez de tratar `CREATE TABLE IF NOT EXISTS` como prova de compatibilidade. Validar explicitamente colunas/tipos/chaves no setup ou nos testes de integração. Se houver divergência, falhar com instrução de migração manual não destrutiva.
- Sem FK direta entre as tabelas, adicionar teste de integridade para identificar `companhia_aerea.cidade` sem correspondente em `cidades.cidade`; relatar o problema, não inserir/alterar dados automaticamente.

---

## 5. Linguagem de pesquisa: gramática formal

### 5.1. Vocabulário inicial

| Categoria | Valores internos aceitos | Sinônimos da entrada |
|---|---|---|
| Companhia | `latam`, `gol`, `azul` | grafia sem distinção de maiúsculas |
| Cidade | `sjc`, `bel`, `campinas` e cidades citadas no enunciado | `São José dos Campos` ↔ `sjc`; `Belém` ↔ `bel`; `Manaus`, `Salvador`, `Porto Alegre`, `São Paulo` (aceitas mesmo se ainda sem linhas no seed; `dos` integra o nome próprio, não é ruído) |
| Turno | `manha`, `tarde`, `noite` | `manhã`, `matutino(s)`; `vespertino(s)`; `noturno(s)` |
| Conectores | `e`, `ou`, `exceto` | somente operadores declarados nesta etapa |
| Ruído permitido | `voos`, `voo`, `de`, `da`, `do`, `em`, `para` | somente quando usados como palavras de ligação |

Qualquer palavra não reconhecida **não deve ser ignorada silenciosamente**. Rejeitar com mensagem explicativa e sugestão de vocabulário. **Cidades explicitamente mencionadas nos exemplos do enunciado** (Manaus, Salvador, Porto Alegre e São Paulo) devem ser aceitas como filtros mesmo quando não aparecem no seed, gerando consulta válida com zero resultados. Dados ausentes não são equivalentes a sintaxe inválida: `latam e campinas` e `latam manaus` são consultas válidas sem correspondência no seed inicial. O cadastro de novos aliases além dos presentes no enunciado deverá acompanhar futuras expansões do banco; nunca aceitar palavras aleatórias como cidades.

### 5.2. Regras de normalização e tokenização **sem perda de informação**

- Validar que o parâmetro HTTP `q` aparece **exatamente uma vez**, é string, tem de 1 a 150 caracteres Unicode **antes da normalização** e não contém controles, pontuação estranha, aspas, ponto e vírgula, parênteses ou outros operadores não previstos. Ausência/vazio = 400; repetição ou sintaxe não suportada = 422. Não unir valores repetidos de `q`.
- Para comparação, usar `strip()`, `casefold()`, Unicode `NFKD`, remoção de marcas diacríticas e compressão de espaços. O texto normalizado **não substitui** a validação lexical: nenhum símbolo pode desaparecer silenciosamente tornando válida uma frase inválida.
- Tokenizar preservando posições e consumir **toda** a frase. Reconhecer nomes multi-palavra pelo alias mais longo (por exemplo `sao jose dos campos`) **antes** de interpretar palavras de ligação. O termo `dos` faz parte desse nome e não pode separá-lo.
- `voo`/`voos` só podem aparecer como introdução inicial, no máximo uma vez. `de`, `da`, `do`, `em`, `para` são palavras de ligação opcionais **apenas quando ligam termos válidos**: `voos da latam em belem` é válido; `de` sozinho e `voos latam de` são inválidos. Jamais ignorar palavras de ligação sobrando no começo/fim ou após um operador incompleto.
- Cada token deve ser classificado como introdução, alias, operador, ligação válida ou erro. Não converter texto do usuário em identificadores SQL. Rejeitar termos desconhecidos depois de um termo válido e **não** produzir resultados parciais.
- Limitar a 12 filtros reconhecidos e até 8 cláusulas de `ou`, contabilizando também a expressão após `exceto` para impedir evasão dos limites. Não criar parser genérico de linguagem natural.

### 5.3. Gramática do MVP (sem parênteses)

```text
SEARCH       := INTRO (LINK? EXPRESSION EXCEPT_PART? | EXCEPT_PART | ε)
              | EXPRESSION EXCEPT_PART?
              | EXCEPT_PART
INTRO        := "voos" | "voo"
EXCEPT_PART  := "exceto" EXPRESSION
EXPRESSION   := CLAUSE ("ou" CLAUSE)*
CLAUSE       := TERM (AND_JOIN TERM)*
AND_JOIN     := "e" | LINK | ε
LINK         := "de" | "da" | "do" | "em" | "para"
TERM         := COMPANY | CITY | SHIFT
```

O `ε` em `AND_JOIN` representa dois termos justapostos e separados por espaço. Uma única `LINK` é permitida após a introdução e antes do primeiro termo (`voos da latam`), ou entre termos (`latam em Belém`). Sem introdução, a busca deve começar por um termo ou `exceto`. Não aceitar ligações consecutivas, isoladas, nem imediatamente após `e`, `ou` ou `exceto`, quando é obrigatório um termo. São inválidas: `da latam`, `voos da`, `latam de em Belém`, `latam ou da gol` e `exceto de noite`. Resolver aliases multi-palavra antes dessas regras: `dos` pertence a `São José dos Campos`. Nenhuma ligação pode consumir operadores ou texto desconhecido.

`ε` (expressão vazia) é permitido **somente depois** de `voo`/`voos`: `voos` devolve todas as combinações; uma string vazia devolve `400/empty-query`. `exceto noite` sem inclusão explícita equivale a “todos menos os noturnos”. `AND_JOIN` implícito admite espaço e ligações opcionais válidas conforme §5.2; não consome operadores ou texto desconhecido. **No máximo um `exceto`.** Expressões incompletas (`latam ou`, `latam e`, `latam exceto`) são inválidas. Não aceitar repetição de introdução, operador sem operando nem palavras de ligação soltas.

**Precedência (decisão de produto):** `e` e a justaposição de termos são avaliados primeiro; `ou` une as cláusulas; `exceto` subtrai do **resultado positivo inteiro**. Exemplo: `latam ou gol exceto noturnos` = `(latam ∪ gol) − noite`. Não dar suporte a agrupamento arbitrário com parênteses no MVP.

### 5.4. Estrutura intermediária esperada

```json
{
  "include": [
    [{"field": "company", "value": "latam"}],
    [{"field": "company", "value": "gol"}]
  ],
  "exclude": [
    [{"field": "shift", "value": "noite"}]
  ]
}
```

Cada lista interna é um grupo **AND**; listas externas são **OR**. `exclude` é aplicado após `include`. Com `voos` isolado, `include: []` significa conjunto universal. `exclude: []` significa sem exclusão.

### 5.5. Matriz de comportamento e oráculos de teste

| Pesquisa | Status | Conjuntos esperados | Total |
|---|---|---|---:|
| `voos` | success | todos | 5 |
| `voos da latam em Belém` | success | latam/bel/manhã | 1 |
| `voos latam de` | invalid-query | ligação sem termo seguinte | — |
| `voos voos latam` | invalid-query | introdução duplicada | — |
| `?q=latam&q=gol` (HTTP) | invalid-query | parâmetro duplicado | — |
| `voos latam` | success | latam/sjc/tarde; latam/sjc/noite; latam/bel/manhã | 3 |
| `voos gol` | success | gol/bel/manhã | 1 |
| `voos azul` | success | azul/campinas/noite | 1 |
| `voos latam e manhã` | success | latam/bel/manhã | 1 |
| `voos latam bel` | success | latam/bel/manhã | 1 |
| `voos latam ou azul` | success | 3 da latam + 1 da azul | 4 |
| `voos bel` | success | latam/bel/manhã; gol/bel/manhã | 2 |
| `voos sjc` | success | latam/sjc/tarde; latam/sjc/noite | 2 |
| `voos São José dos Campos` | success | mesmos 2 de `sjc` | 2 |
| `voos Belém` | success | mesmos 2 de `bel` | 2 |
| `voos noturnos` | success | latam/sjc/noite; azul/campinas/noite | 2 |
| `voos latam exceto noturnos` | success | latam/sjc/tarde; latam/bel/manhã | 2 |
| `voos gol exceto noturnos` | success | gol/bel/manhã | 1 |
| `voos exceto noturnos` | success | latam/sjc/tarde; latam/bel/manhã; gol/bel/manhã | 3 |
| `voos latam ou gol exceto noturnos` | success | latam/sjc/tarde; latam/bel/manhã; gol/bel/manhã | 3 |
| `voos latam e campinas` | no-results | nenhum | 0 |
| `voos latam manaus` | no-results | Manaus é válida no enunciado, mas não está no seed inicial | 0 |
| `voos latam e gol` | no-results | nenhum (AND contraditório) | 0 |
| `voos latam ou` | invalid-query | sintaxe incompleta | — |
| `voos latam exceto` | invalid-query | sintaxe incompleta | — |
| `voos latam exceto noite exceto tarde` | invalid-query | operador repetido | — |
| `voos avião espacial` | invalid-query | termos desconhecidos | — |
| `voos latam xyz` | invalid-query | termo desconhecido após válido | — |
| `latam; DROP TABLE cidades` | invalid-query | pontuação e termos não suportados | — |
| `voos latam ou gol exceto noite ou tarde` | success | latam/bel/manhã; gol/bel/manhã | 2 |
| string vazia | empty-query | ausência de pesquisa | — |

A ordenação é **determinística** por `company, city, shift` (ordenar no SQL). Testes devem comparar **conjuntos/tuplas** quando a ordem não for essencial e verificar ordenação em teste separado.

### 5.6. Observação sobre o código JavaScript atual

O parser atual em `static/js/search.js` reconhece palavras por correspondência, mas não oferece validação rigorosa de sintaxe/trailing tokens. A migração **não deve replicar silenciosamente essas limitações**. O novo parser Python terá testes de rejeição explícitos. Depois que todos os resultados válidos forem conferidos, remover o motor de busca local para não existir lógica duplicada.

---

## 6. Contrato do construtor SQL

### 6.1. Transformação permitida

- Uma cláusula **AND** vira um `WHERE` com condições unidas por `AND`.
- Cláusulas alternativas **OR** viram consultas compatíveis unidas por **`UNION`** (sem `ALL`, para retirar duplicatas).
- `EXCETO` vira **`EXCEPT`** aplicado ao conjunto positivo completo.
- A base combinada é construída com **`JOIN`** entre `companhia_aerea` e `cidades`.
- Cada ramo de `UNION` e `EXCEPT` deve selecionar exatamente `company, city, shift` na mesma ordem e tipos compatíveis. O `ORDER BY` final aplica-se ao conjunto resultante.
- Nunca gerar `WHERE` substituindo valores diretamente em strings; usar placeholders e parâmetros DB-API (`%s` ou parâmetros nomeados do psycopg).
- Nomes de coluna devem vir exclusivamente do mapa constante: `company`, `city`, `shift`.
- SQL dinâmico autorizado somente para selecionar **fragmentos estáticos da gramática** e compor operadores; nenhuma entrada literal pode alterar sintaxe SQL.

### 6.2. Padrão SQL ilustrativo

**Exemplo de busca:** `voos latam ou gol exceto noturnos`.

```sql
WITH base AS (
    SELECT a.companhia AS company, a.cidade AS city, c.turno AS shift
    FROM companhia_aerea a
    JOIN cidades c ON c.cidade = a.cidade
),
included AS (
    SELECT company, city, shift FROM base WHERE company = %s
    UNION
    SELECT company, city, shift FROM base WHERE company = %s
),
excluded AS (
    SELECT company, city, shift FROM base WHERE shift = %s
)
SELECT company, city, shift FROM included
EXCEPT
SELECT company, city, shift FROM excluded
ORDER BY company, city, shift;
```

**Parâmetros:** `('latam', 'gol', 'noite')`. Esse exemplo é um **contrato de desenho**: para buscas sem `ou` ou sem `exceto`, o construtor deve omitir CTEs/operadores desnecessários. Para `include=[]`, a seleção positiva deve ser `SELECT company, city, shift FROM base`. Para `exclude=[]`, não gerar `EXCEPT`. Não adicionar `LIMIT` por padrão a 5 registros sem necessidade; se houver paginação futura, definir total/página explicitamente antes de alterar contrato.

**Atenção à precedência:** PostgreSQL avalia `UNION`/`EXCEPT` da esquerda para a direita no mesmo nível, salvo agrupamento explícito; o plano usa `included AS (...)` e `excluded AS (...)` para garantir que a subtração ocorre *depois* da união. Em conjuntos, as colunas/tipos devem coincidir.

### 6.3. Contrato do serviço de consulta

Entrada: filtros estruturados e validados pelo parser.  
Saída: lista de tuplas/objetos com `company`, `city`, `shift`, sem detalhes de apresentação.  
Erros: conexão indisponível, timeout e SQL inesperado propagam **erros internos tipados**, capturados na rota HTTP; nunca expor SQL ou dados de conexão ao navegador.  
Conexão: usar `psycopg` (versão 3), `DATABASE_URL`, conexão por requisição simples com context manager e cursor. **Não** adotar pool antes de demonstrar necessidade real. Aplicar `connect_timeout` e `statement_timeout` curto (ex.: 3 s) no escopo da sessão/transação.

---

## 7. API Flask — contrato HTTP estável

### 7.1. Rotas

| Método / rota | Função | Observações |
|---|---|---|
| `GET /` | Renderizar a página SkyFetch | Não precisa conectar ao banco para renderizar |
| `GET /api/search?q=<frase>` | Processar pesquisa e retornar JSON | Contrato abaixo; fonte de verdade é PostgreSQL; `q` único |

**Sem POST, CORS, sessões ou autenticação no MVP.** A API e o frontend estarão no mesmo domínio/origem. Toda alteração da base será feita por scripts de seed/migração, não por requisição pública.

### 7.2. Resposta bem-sucedida — HTTP 200

```json
{
  "status": "success",
  "query": "voos latam e manhã",
  "total": 1,
  "items": [
    {
      "id": "latam:bel:manha",
      "company": "latam",
      "companyName": "LATAM",
      "city": "bel",
      "cityName": "Belém",
      "shift": "manha",
      "shiftName": "Manhã"
    }
  ],
  "interpreted": {
    "include": [[{"field": "company", "value": "latam"}, {"field": "shift", "value": "manha"}]],
    "exclude": []
  },
  "isDemoData": true
}
```

`total` deve ser exatamente `items.length` na versão sem paginação. `id` é determinístico (`company:city:shift`); não representa identificador de voo real. `isDemoData` **não** deve virar `false` apenas porque existe PostgreSQL: os dados continuam vindo do exercício. `interpreted` permite conferir a intenção processada, mas **jamais** deve revelar SQL. Os campos `companyName`, `cityName` e `shiftName` são **montados apenas no Python** para reutilização dos cartões JS existentes; o frontend não deve recalculá-los. Os campos `status`, `query`, `total`, `items`, `isDemoData` são obrigatórios em todas as respostas de `/api/search`; `interpreted` é incluído apenas em buscas válidas e `error` apenas nos erros. Em respostas válidas sem correspondência, `interpreted` deve continuar presente.

Para uma busca sintaticamente válida sem correspondências, responder **HTTP 200** com `status: "no-results"`, `items: []`, `total: 0`, e a mesma estrutura restante.

### 7.3. Erros esperados

O contrato de erro preserva campos estáveis e adiciona `error`:

```json
{
  "status": "invalid-query",
  "query": "voos latam ou",
  "total": 0,
  "items": [],
  "isDemoData": true,
  "error": {
    "code": "INCOMPLETE_OPERATOR",
    "message": "Complete a pesquisa após 'ou'."
  }
}
```

| HTTP | `status` | `error.code` (exemplo) | Situação |
|---:|---|---|---|
| 400 | `empty-query` | `EMPTY_QUERY` | `q` ausente ou em branco |
| 400 | `invalid-query` | `QUERY_TOO_LONG` | mais de 150 caracteres |
| 422 | `invalid-query` | `UNKNOWN_TERM` | termo desconhecido |
| 422 | `invalid-query` | `INCOMPLETE_OPERATOR` | `e`, `ou`, `exceto` sem operando |
| 422 | `invalid-query` | `UNSUPPORTED_SYNTAX` | parênteses, operadores repetidos, `q` duplicado ou expressão não suportada |
| 503 | `service-unavailable` | `DATABASE_UNAVAILABLE` | PostgreSQL desconectado, timeout ou configuração ausente |
| 500 | `internal-error` | `INTERNAL_ERROR` | bug inesperado sem revelar traceback ao cliente |

O backend pode adicionar um `requestId` interno **se já houver infraestrutura**; não criar sistema de rastreamento apenas para o trabalho. Não variar arbitrariamente `items`, `total` ou `status` entre sucesso e erro.

### 7.4. Erros que não são bugs

- `latam e campinas` é busca válida, retorna **200/no-results**.
- `latam ou` é sintaxe incompleta, retorna **422**.
- PostgreSQL indisponível retorna **503**, nunca fingir que retornou zero resultados.
- `latam'; DROP TABLE ...` deve ser rejeitada como entrada inválida e nunca virar SQL executável.
- Repetição de requisições `GET` não altera dados: idempotência de leitura.

---

## 8. Frontend — integração sem redesenho

### 8.1. Manter a identidade existente

Preservar: cabeçalho SkyFetch, marca navy/turquesa, hero com campo de busca, chips de exemplos, cartões de resultado, seção “Como funciona?”, painel informativo, layout mobile, foco visível, `prefers-reduced-motion` e links existentes.

Alterar apenas quando necessário: textos que afirmem “dados locais”, badges de status, feedback de rede, ligação dos botões ao endpoint e acessibilidade de estado dinâmico.

### 8.2. Estados visuais obrigatórios

| Estado | Quando | Comportamento no painel |
|---|---|---|
| Inicial | Página abre com `voos latam` (ou `?q=` existente) | Buscar automaticamente **pela API**; exibir carregando |
| Loading | Requisição ativa | Mensagem de carregamento/`aria-busy=true`; impedir resultados obsoletos |
| Success | `200/success` | Renderizar cartões e contador com dados da API |
| No results | `200/no-results` | Mensagem amigável para refinar a busca |
| Invalid query | `400` ou `422` | Mensagem clara de sintaxe/vocabulário, não mensagem genérica de servidor |
| Offline / DB down | falha de rede ou `503` | Mensagem “Serviço temporariamente indisponível”, botão/reenvio de busca |
| Unexpected | `500` ou JSON inválido | Mensagem segura + possibilidade de tentar novamente |

### 8.3. Modificações de JS

1. `static/js/app.js`: substituir `engine.searchFlights()` por função assíncrona `fetch('/api/search?' + new URLSearchParams({q}))`.
2. Preferir **um contador monotônico `requestVersion`** para cada nova pesquisa. Depois de `await fetch()` e `await response.json()`, antes de atualizar resultados, erros, contador ou `aria-busy` (inclusive no `catch`/`finally`), confirmar que a versão ainda é a mais recente. Isso resolve respostas fora de ordem sem criar nova dependência. `AbortController` é opcional se medições justificarem cancelar rede; sozinho não substitui a checagem de versão.
3. Reutilizar `makeResult()`, `showMessage()` e elementos DOM atuais. Usar `textContent` e `createElement`, jamais `innerHTML` com `query` ou texto de banco.
4. Manter Enter, botão Buscar e chips; durante carregamento, não bloquear permanentemente o formulário.
5. Usar **`history.replaceState`** ao submeter pesquisa/chips (sem acrescentar entrada ao histórico a cada busca). No carregamento, se a URL **contém** `q`, respeitar seu valor inclusive `?q=` vazio (mostrar erro apropriado); se `q` está ausente, usar o exemplo inicial `voos latam`. Não usar `pushState` no MVP; assim não é preciso implementar navegação `popstate`. Preservar demais parâmetros de URL quando possível.
6. Não mostrar dados falsos como fallback silencioso se API falhar.
7. Após integração validada, remover `static/js/search.js` do template (e o arquivo se não houver consumidores). **Não perder cobertura:** migrar testes de lógica de pesquisa para Python/SQL, mas manter ao menos uma verificação independente do fluxo JS (manual com registro de evidência ou automatizada leve) para carregamento, erro, requests fora de ordem, chips e URL. Conferir importações/referências antes de excluir.

### 8.4. Acessibilidade / visual

- O campo deve ter `<label>` acessível; formulário acionável pelo teclado.
- Informações de carregamento/erro devem ser anunciadas por `aria-live` sem verbosidade excessiva.
- Usar `aria-busy` somente durante requisição ativa.
- Preservar contraste e foco visível, inclusive botões/chips.
- Em telas pequenas, cartões não devem causar scroll horizontal.
- Respeitar `prefers-reduced-motion` já implementado.
- Revisar uso do título “voos” para não sugerir partidas reais; a nota de dados didáticos deve continuar visível.

---

## 9. Estrutura de arquivos proposta (incremental)

```text
SkyFetch/
├── README.md                      # atualizar instruções de execução e escopo
├── .gitignore                     # preservar
├── .env.example                   # DATABASE_URL de exemplo, sem credenciais reais
├── requirements.txt               # Flask + psycopg
├── requirements-dev.txt           # pytest e ferramentas de desenvolvimento estritamente necessárias
├── app.py                         # Flask, /, /api/search e tratamento de erros
├── skyfetch/                      # lógica desacoplada de Flask
│   ├── __init__.py
│   ├── parser.py                  # normalização, aliases, gramática, AST/filtros
│   └── repository.py              # montagem de SQL seguro + acesso PostgreSQL
├── db/
│   ├── schema.sql                 # criação de tabelas
│   └── seed.sql                   # dados do enunciado, idempotentes
├── templates/
│   └── index.html                 # EXISTENTE; pequenas integrações
├── static/
│   ├── favicon.svg                # EXISTENTE
│   ├── css/style.css              # EXISTENTE
│   └── js/
│       └── app.js                 # EXISTENTE, adaptado à API
└── tests/
    ├── test_parser.py             # gramática, acentos, erro, precedência
    ├── test_api.py                # Flask test client, mocks de repositório
    └── test_database.py           # integração real com PostgreSQL isolado
```

**Estrutura é proposta, não observada:** `skyfetch/`, `db/`, arquivos Python de testes e `.env.example` ainda não existem no baseline. `static/js/search.js` e `tests/search.test.cjs` **existem hoje**, mas podem ser removidos **após** migração de cobertura; não apagá-los no primeiro commit. Evitar subpastas/camadas extras se `parser.py` e `repository.py` forem suficientes. `app.py` continua o ponto de entrada.

---

## 10. Configuração e execução local (Windows, sem custos externos)

### 10.1. Ferramentas-alvo

- Python 3.11 ou 3.12.
- PostgreSQL instalado localmente (preferencialmente uma versão ainda suportada, por exemplo 17).
- Node.js **não** é dependência de produção; só será usado para os testes JS atuais até a migração.
- `pip` e `venv` do Python. Editor livre (VS Code, Codex etc.).
- Driver `psycopg` 3 — escolhido por integração direta e parâmetros seguros.

### 10.2. Dependências desejadas

`requirements.txt`: `Flask>=3.1,<4.0` e `psycopg[binary]>=3.2,<4` (faixas sugeridas; a IA deve verificar compatibilidade/instalação e registrar versões instaladas em teste).  
`requirements-dev.txt`: `-r requirements.txt` e `pytest` (faixa estável compatível).  
**Não** adicionar `flask-cors`, SQLAlchemy, Pydantic, dotenv ou pool de conexão sem necessidade demonstrada.

### 10.3. `DATABASE_URL`

Exemplo sem credenciais reais (arquivo `.env.example`):

```env
DATABASE_URL=postgresql://skyfetch_user:CHANGE_ME@localhost:5432/skyfetch
```

Documentar como definir `DATABASE_URL` nas variáveis de ambiente do terminal/PowerShell e como criar banco/usuário local de menor privilégio. A conexão da aplicação deve usar usuário **apenas com SELECT** nas tabelas; a criação de schema e seed usa credenciais administrativas/owner somente na instalação. O README deve evitar expor senhas em capturas, commits ou logs; qualquer exemplo literal de senha deve ser obviamente fictício. `os.environ` lê a variável no Python; o arquivo `.env.example` é **apenas modelo**, não é carregado automaticamente. Não versionar `.env` real. Não colocar senha em JS, HTML, screenshot, erro HTTP ou logs.

### 10.4. Comandos que o README final deve ensinar

Usar três conexões distintas: `SETUP_DATABASE_URL` para o owner de instalação, `DATABASE_URL` para a aplicação somente leitura e `TEST_DATABASE_URL` para um owner exclusivo de outro banco. A conexão da aplicação nunca executa schema/seed. Criar `skyfetch` com owner `skyfetch_owner` e `skyfetch_test` com owner `skyfetch_test_owner`. Revogar os privilégios de banco de `PUBLIC`, conceder acesso somente aos papéis previstos e revogar `CREATE` de `PUBLIC` no schema `public`. Para tabelas futuras, executar como administrador/owner: `ALTER DEFAULT PRIVILEGES FOR ROLE skyfetch_owner IN SCHEMA public GRANT SELECT ON TABLES TO skyfetch_user`. Para tabelas já existentes: `GRANT SELECT ON ALL TABLES IN SCHEMA public TO skyfetch_user`. O owner de testes não acessa o banco de desenvolvimento, e os papéis de desenvolvimento não acessam o de testes.

Na preparação atual, os bancos ficam vazios. Schema, seed e consultas de negócio pertencem à próxima etapa. Os comandos abaixo descrevem a implementação completa futura.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# Depois de criar o banco e usuário PostgreSQL:
$env:SETUP_DATABASE_URL="postgresql://skyfetch_owner:SENHA_OWNER@127.0.0.1:5432/skyfetch"
psql $env:SETUP_DATABASE_URL -v ON_ERROR_STOP=1 -f db/schema.sql
psql $env:SETUP_DATABASE_URL -v ON_ERROR_STOP=1 -f db/seed.sql

# Aplicação: papel separado, somente leitura nas tabelas.
$env:DATABASE_URL="postgresql://skyfetch_user:SENHA_APP@127.0.0.1:5432/skyfetch"
# Testes: outro owner, em outro banco.
$env:TEST_DATABASE_URL="postgresql://skyfetch_test_owner:SENHA_TESTE@127.0.0.1:5432/skyfetch_test"

python app.py
# Navegador: http://127.0.0.1:5000/
```

O README deve oferecer alternativa sem `psql` no PATH (utilizar SQL Shell/pgAdmin) sem exigir Docker. Também deve explicar que `python app.py` em modo de desenvolvimento não é servidor de produção.

---

## 11. Segurança, erros e desempenho

### 11.1. Segurança mínima obrigatória

- Queries parametrizadas (`%s`) para **todos** os valores de usuário.
- Lista de permissão fixa para campos/operadores; proibir nomes de tabela/coluna vindos da pesquisa.
- `q` com limite de tamanho e quantidade de termos; rejeitar operadores inválidos, caracteres inesperados, parâmetros repetidos e **sobras de tokens**.
- PostgreSQL com usuário de acesso limitado (no mínimo leitura para a conexão da API, se possível separar usuário de schema/seed).
- Não habilitar `debug=True` por padrão; usar flag local explícita no desenvolvimento.
- Não enviar stack trace, DSN, exceções de psycopg nem SQL bruto na API.
- Frontend sem `innerHTML` de conteúdo externo; manter `textContent` para pesquisa e resultados.
- Sem CORS aberto e sem credenciais no navegador.
- GET apenas para leitura; nenhuma operação de escrita em resposta a pesquisa.

### 11.2. Falhas previsíveis

| Falha | Resposta correta |
|---|---|
| Falta `DATABASE_URL` | Página `/` funciona; `/api/search` responde 503 e log seguro |
| PostgreSQL desligado | 503, sem retornar resultados demonstrativos locais |
| Banco acessível mas tabelas ausentes/schema incompatível | **500/internal-error** (erro de configuração/esquema; não é indisponibilidade temporária); instrução de inicialização em log seguro/README |
| Palavra desconhecida | 422 + mensagem de vocabulário; sem consulta SQL |
| Erro de SQL inesperado | 500 genérico e log técnico local sem segredos |
| Busca nova antes da anterior | Cancelar/descartar resposta antiga |
| Seed executado de novo | Sem duplicações |
| Uma cidade com dois turnos | JOIN gera duas combinações correspondentes |

### 11.3. Desempenho proporcional

Dataset de 8 linhas: índices das chaves primárias são suficientes; sem cache/paginação/pool no MVP. Medir somente se surgir carga real. Evitar queries por resultado (N+1): uma busca deve resultar numa única consulta SQL. Adotar timeout limitado da conexão e da consulta para não travar indefinidamente.

---

## 12. Requisitos rastreáveis

| ID | Requisito verificável | Critério de aceite |
|---|---|---|
| REQ-001 | UI SkyFetch preservada e responsiva | AC-001: desktop/mobile visualmente coerentes, sem regressão estrutural |
| REQ-002 | PostgreSQL com as duas tabelas do enunciado | AC-002: seed reproduz 4+4 linhas e JOIN 5 tuplas |
| REQ-003 | Conexão Flask → PostgreSQL | AC-003: API retorna dados reais do seed; falha no DB não vira resultado falso |
| REQ-004 | Parser de linguagem restrita | AC-004: reconhece alias/acentos e respeita precedência documentada |
| REQ-005 | Operações SQL exigidas | AC-005: JOIN, UNION e EXCEPT executados no PostgreSQL conforme frase |
| REQ-006 | API estável e segura | AC-006: contrato JSON e códigos HTTP conforme seção 7; parametrização |
| REQ-007 | Frontend consome API | AC-007: resultados vêm exclusivamente do backend; estados de rede corretos |
| REQ-008 | Erros úteis e consistentes | AC-008: vazio, inválido, sem resultados, 503 e 500 diferenciados |
| REQ-009 | Cobertura de testes | AC-009: unitários, Flask test client e integração PostgreSQL executados |
| REQ-010 | Reprodutibilidade/documentação | AC-010: outra pessoa prepara ambiente e roda testes seguindo README |
| REQ-011 | Segurança e preservação | AC-011: sem SQL injection/XSS evidentes, sem segredos, sem perda de código atual |
| REQ-012 | Processo revisável | AC-012: PR separado com diffs, evidência de testes e sem merge automático |

---

## 13. Plano de implementação por fatias verticais

Cada tarefa deve deixar uma melhoria verificável. A IA deve anotar resultados reais dos testes e arquivos alterados na descrição do PR. **Não marcar tarefas como concluídas por terem sido apenas planejadas.**

| Tarefa | Entregável concreto | Dependências | Critérios | Verificação / rollback |
|---|---|---|---|---|
| **T001 — Baseline** | Inspecionar branch atual, executar testes existentes, criar branch `feature/skyfetch-postgres-search` | — | AC-011/012 | Salvar SHA e saída dos testes; reverter só alterações da branch |
| **T002 — Dados** | `db/schema.sql`, `db/seed.sql` e instruções de criação; checar schema e órfãos | T001 | AC-002 | Banco de teste vazio, seed 2×: 4+4 linhas, JOIN=5; schema divergente deve falhar sem apagar dados |
| **T003 — Conexão** | `psycopg` + `DATABASE_URL` + gestão de conexão | T002 | AC-003 | Consulta simples via Python; simular banco indisponível |
| **T004 — Parser** | `skyfetch/parser.py` com tokenização de consumo total e gramática restrita | T001 | AC-004/008 | `pytest tests/test_parser.py`: busca vazia, `voos`, stopwords, aliases longos, cauda desconhecida e gramática |
| **T005 — SQL** | `skyfetch/repository.py` gera consultas parametrizadas | T002, T003, T004 | AC-005/006 | Integração PostgreSQL testa JOIN/UNION/EXCEPT e injeção |
| **T006 — Rota API** | `GET /api/search` e handler de erro | T003, T004, T005 | AC-003/006/008 | Flask test client valida HTTP/JSON e indisponibilidade |
| **T007 — Ligação UI** | `static/js/app.js` usando `fetch`, sem dados locais | T006 | AC-001/007 | Pesquisa via browser retorna mesmas 5 tuplas; buscar em mais de um dispositivo/tamanho |
| **T008 — Refinar estados** | Loading, zero, inválido, indisponível, acessibilidade, URL e token de requisição | T007 | AC-001/007/008 | Teclado, aria-live, mobile, respostas fora de ordem e `?q=` vazio |
| **T009 — Remover duplicações** | Retirar motor de busca local, migrar testes de parser e preservar cobertura do JS de integração | T007, T008 | AC-007/009/011 | Procurar referências a `SkyFetchSearch`; rodar pytest e teste/smoke frontend |
| **T010 — Documentar** | README, `.env.example`, instruções Windows e comandos | T002–T009 | AC-010/011 | Setup limpo guiado somente pelo README |
| **T011 — QA final** | Testes unitários + integração + inspeção visual + varredura segurança | T001–T010 | AC-001–011 | Relatório de resultados executados, falhas e limites |
| **T012 — Entrega para revisão** | PR não mesclado, mudanças organizadas e handoff | T011 | AC-012 | Revisar diff vs. baseline; `main` preservada |

### 13.1. Marcos e critérios de saída

**Marco M1 — Banco demonstrável:** schema/seed funcionando e JOIN=5; sem alterar frontend.  
**Marco M2 — Motor funcional:** parser e SQL mostram resultados certos, com testes de segurança.  
**Marco M3 — Integração vertical:** navegador → API Flask → PostgreSQL → navegador; dados locais eliminados.  
**Marco M4 — Entrega revisável:** interface preservada, testes documentados, README reproduzível, PR aguardando revisão.

### 13.2. Política de branches e commits

- Trabalhar na branch proposta, partindo do SHA verificado no momento da implementação (não presumir que o commit informado neste plano ainda seja o HEAD).
- Commits pequenos: `feat(db): ...`, `feat(search): ...`, `feat(api): ...`, `feat(ui): ...`, `test: ...`, `docs: ...`.
- Criar **um PR de integração** para revisão, sem fazer merge nem publicar deploy nesta etapa.
- Não sobrescrever alterações recentes do usuário; se `main` mudou, revalidar antes de aplicar o plano.

---

## 14. Estratégia detalhada de testes

### 14.1. Unitários do parser — sem banco

Verificar: maiúsculas/minúsculas; acentos; aliases longos **antes** do tratamento das palavras de ligação; `e` implícito; `ou`; `exceto`; precedência; termo ausente; operador no final/início; repetição de `exceto`; caracteres não permitidos; query longa; termo desconhecido; `voos` isolado; texto vazio; links `da` e `em` corretos e ligação sobrando; parâmetro HTTP `q` duplicado. Os testes devem conferir o AST/filtros, não SQL textual incidental.

### 14.2. API Flask — client de teste

Usar Flask `test_client` e substituto do repositório para validar contrato e mapeamentos de erro sem PostgreSQL, além de testar `GET /` sem banco. Cobrir 200/success, 200/no-results, 400/empty-query, 422/invalid-query, 503/unavailable e 500 inesperado. Respostas devem ser JSON válido, sem segredos ou stack trace.

### 14.3. Banco real isolado

Criar uma base `skyfetch_test` (ou banco descartável equivalente) e rodar schema/seed isolados. Usar uma variável explícita `TEST_DATABASE_URL` para testes de integração, **nunca reutilizar silenciosamente `DATABASE_URL`**; o teste deve recusar conexão se as duas URLs apontarem ao mesmo banco. Verificar todos os 5 resultados e as matrizes de consulta da seção 5, além de **contratos de schema, chaves e ausência de cidades órfãs**. Verificar que schema preexistente incompatível é reportado em vez de aceito silenciosamente. Provar `EXCEPT` e `UNION` no SQL real, não apenas por filtragem posterior no Python. Executar seed duas vezes. **Não** usar o banco de desenvolvimento em teste destrutivo.

### 14.4. Segurança

- SQL injection: termos como `latam' OR 1=1 --`, `'; DROP TABLE cidades; --` resultam em erro benigno; tabelas permanecem intactas.
- XSS: consulta contendo `<script>` deve ser exibida apenas como texto seguro, nunca executada.
- `DATABASE_URL` inválida: 503; log sem senha.
- Consulta de 151 caracteres: 400.
- Palavra completamente desconhecida após válida: não ignorar resto e produzir resultado enganoso.

### 14.5. Frontend

Testar manualmente ou por ferramenta de browser realmente disponível: desktop (≥1280 px), tablet (~768 px), celular (~390 px), teclado, Enter, chips, foco, sugestões, carregamento, falha de API, refresh com `?q=`, `?q=` **vazio**, busca rápida consecutiva, **resposta antiga chegando depois da recente**, redução de movimento. Se houver ambiente para testes JavaScript baratos, cobrir ao menos estado de requisição assíncrona/erro sem adicionar framework pesado; não declarar que `pytest` cobre estados da interface. Registrar screenshots/achados reais se a ferramenta existir. Um teste unitário Python **não** substitui inspeção visual.

### 14.6. Gates para declarar pronto

- `pytest` passa em testes de parser/API (registrar comando e saída).
- Integração PostgreSQL isolada passa; caso não haja banco disponível, reportar **NÃO VERIFICADO** e não considerar produto concluído.
- Demonstração ponta a ponta documentada: navegador exibindo busca alimentada pelo PostgreSQL.
- Nenhum segredo commitado; `debug` desligado por padrão.
- Dados locais não são mais a fonte oficial dos resultados.
- README reproduz setup e o PR explica limitações.

---

## 15. Riscos, decisões e mitigação

| Severidade | Risco/decisão | Mitigação / teste |
|---|---|---|
| **P1** | SQL injection ao concatenar entrada | Parâmetros psycopg + lista fixa de colunas + casos maliciosos |
| **P1** | Interface mostrar dados falsos quando DB cai | Sem fallback local; retornar 503 + estado de erro |
| **P1** | Refatoração apagar o visual aprovado | Adaptar JS sem redesenhar; capturas antes/depois, diff mínimo |
| **P1** | Erro de precedência `UNION`/`EXCEPT` | CTEs de conjuntos e testes mistos com `ou exceto` |
| **P2** | Banco não pode ter FK direta pela duplicidade de `cidade` | Documentar JOIN lógico; evitar FK inválida |
| **P2** | `latam` com termo desconhecido retornar resultados parciais | Parser rejeita tokens desconhecidos |
| **P2** | Demora de requisição anterior substituir a mais nova | `requestVersion` obrigatório; AbortController opcional |
| **P2** | Dois motores de busca divergirem (Python/JS) | Fazer migração com testes de paridade e remover motor local |
| **P2** | README presumir `.env` carregado automaticamente | Documentar variável de ambiente real e comandos PowerShell |
| **P1** | Gramática aceitar consulta vazia ou eliminar tokens desconhecidos | Parser consome toda a entrada e só permite ε após `voos`/`voo` |
| **P1** | Schema preexistente incompatível passar por `IF NOT EXISTS` | Verificação de estrutura, seed em teste isolado e erro explícito |
| **P2** | Resposta antiga ou `finally` desativar loading da busca nova | Versionamento monotônico de requisição e verificação antes de cada mutação da UI |
| **P2** | Remover JS tests sem conservar cobertura de UI | Smoke test de rede/URL/estado e revisão de DOM |
| **P3** | Apps maiores exigirem paginação/pool | Não construir agora; reavaliar com volume real |

### 15.1. Decisões explicitamente propostas (ainda não aprovadas pelo usuário individualmente)

- D001: Uma aplicação Flask única, sem framework de frontend adicional.
- D002: PostgreSQL com **duas** tabelas, chave composta e sem FK `cidade`→`cidades`.
- D003: Parser determinístico e SQL set-based; nenhuma IA externa.
- D004: `e` = AND; `ou` = UNION; `exceto` = EXCEPT com precedência documentada.
- D005: Entrada desconhecida gera erro, não resultado parcial enganoso.
- D006: Frontend atual mantido e motor JS local removido só após integração, preservando testes de integração UI.
- D009 (revisão): a API é a única responsável pelos nomes formatados usados nos cartões.
- D010 (revisão): `history.replaceState` e `requestVersion` minimizam complexidade de URL/concorrência.
- D011 (revisão): nenhuma tokenização pode descartar pontuação ou palavras desconhecidas.
- D007: Sem fallback de dados locais após API falhar.
- D008: Desenvolvimento em branch + PR não mesclado.

### 15.2. Rollback

- Toda mudança acontece em branch: reverter commits individuais ou abandonar branch sem afetar `main`.
- Banco de desenvolvimento: seeds **idempotentes, não destrutivos**; schema inicial `IF NOT EXISTS`; antes de evolução estrutural, exportar backup e validar restauração numa cópia.
- Não executar `DROP`, `TRUNCATE` ou transformação destrutiva dos dados do usuário para “voltar ao estado anterior”.
- Se a integração UI quebrar, reverter apenas o commit de integração mantendo banco/parser/tests intactos; registrar o problema antes de tentar outra abordagem.

---

## 16. Matriz de rastreabilidade REQ → AC → tarefa → teste

| REQ / AC | Tarefa(s) | Evidência planejada | Situação no momento deste plano |
|---|---|---|---|
| REQ-001 / AC-001 | T007–T008, T011 | Screenshots, browser mobile/desktop e acessibilidade | NÃO VERIFICADO |
| REQ-002 / AC-002 | T002, T011 | SQL seed duplicado + contagens e JOIN | NÃO VERIFICADO |
| REQ-003 / AC-003 | T003, T006 | Integração PostgreSQL + erro 503 | NÃO VERIFICADO |
| REQ-004 / AC-004 | T004 | `pytest tests/test_parser.py` | NÃO VERIFICADO |
| REQ-005 / AC-005 | T005 | SQL real com JOIN, UNION, EXCEPT | NÃO VERIFICADO |
| REQ-006 / AC-006 | T005–T006 | Flask test client; JSON e injection | NÃO VERIFICADO |
| REQ-007 / AC-007 | T007–T009 | Inspeção da rede no browser + remoção motor JS | NÃO VERIFICADO |
| REQ-008 / AC-008 | T004, T006, T008 | Matriz de status + simulações de erro | NÃO VERIFICADO |
| REQ-009 / AC-009 | T004–T011 | Saídas reais de pytest/integração/browser | NÃO VERIFICADO |
| REQ-010 / AC-010 | T010–T011 | Reinstalação a partir do README | NÃO VERIFICADO |
| REQ-011 / AC-011 | T001, T009–T011 | Diff, secrets, testes maliciosos | NÃO VERIFICADO |
| REQ-012 / AC-012 | T001, T012 | PR, branch e HEAD confirmados | NÃO VERIFICADO |

**Importante:** o frontend e os testes JavaScript atuais foram **inspecionados no repositório**, mas não executados novamente na produção deste documento. A matriz trata da *nova implementação futura*, portanto não marca seus gates como concluídos.

---

## 17. Revisão crítica do próprio planejamento (pré-implementação)

### Perguntas já respondidas

**O que a auditoria v1.1 corrigiu?** A gramática original aceitava o vazio sem introdução, não especificava como lidar com stopwords e nomes longos, e permitia à IA duplicar a apresentação de nomes no Python/JS. O tratamento de schemas divergentes, de `q` duplicado e de requisições concorrentes ficou mais rigoroso sem exigir novos serviços. A cobertura JavaScript de UI não deve desaparecer com a retirada do motor local.

**Por que não deixar a filtragem em JS e só buscar dados do banco?** Porque o enunciado exige consultas SQL com `JOIN/UNION/EXCEPT` e a regra precisa ter fonte única; senão o PostgreSQL seria apenas um dump de dados.

**Por que não SQLAlchemy?** SQL explícito é mais transparente e suficiente para a disciplina; ORM acrescentaria complexidade sem benefício prático no MVP.

**Por que não criar tabela `voos`?** O professor descreve relações companhia/cidade e cidade/turno, não registros de voos; inventar entidade de voo mudaria o trabalho. Pode ser ideia de V2 se novos requisitos aparecerem.

**Por que `cidade` não é FK?** Porque `cidades.cidade` possui duplicatas por turno; a modelagem das duas tabelas não oferece chave única de cidade. O relacionamento se dá pela igualdade do campo no JOIN.

**Por que remover dados locais?** Para não haver divergência visual entre respostas da API e dados inventados em JS.

### Lacunas a confirmar na entrega

- Se o professor exige explicitamente um formato SQL particular (por exemplo, `EXCEPT` literalmente visível num arquivo), mostrar consultas nos testes/docs; já está contemplado.
- Se haverá avaliação em máquina sem PostgreSQL instalado, README precisa detalhar instalação/configuração local; não substituir PostgreSQL por SQLite.
- Se o usuário quiser páginas adicionais ou recursos de dados reais, isso será **outro escopo**, não parte deste MVP.

### Quality gates NEXUS no estado atual

- **A — Problema:** especificado com base no enunciado e no repositório.
- **B — Requisitos:** especificados e rastreados; ainda não implementados.
- **C — Arquitetura:** definida em proposta; sem validação de execução.
- **D — Tarefas:** sequenciadas por dependências e com testes.
- **E — Implementação/testes:** **NÃO VERIFICADOS**; foram explicitamente adiados.
- **F — Continuidade:** este arquivo e o prompt de handoff contêm o plano transferível.

---

## 18. Protocolo para a IA implementadora (handoff)

1. Ler `README.md`, `app.py`, `templates/index.html`, `static/js/app.js`, `static/js/search.js`, `tests/search.test.cjs`, `.gitignore`, `requirements.txt` diretamente no **HEAD atual** antes de tocar o código.
2. Confirmar diferenças contra a baseline `07ef497` e **não sobrescrever** alterações surgidas depois.
3. Trabalhar exclusivamente em branch separada. Não fazer push na `main`, merge nem deploy sem autorização específica.
4. Seguir as tarefas T001–T012; mudanças pequenas, rastreáveis e com teste.
5. Usar práticas do Ponytail: antes de cada arquivo novo, verificar se uma função existente/stdlib resolve; não trocar estrutura visual nem instalar dependência sem justificativa.
6. Todo código novo de parser, SQL, erro, HTTP e tratamento de texto recebe pelo menos testes relevantes; jamais sacrificar segurança por menos linhas.
7. Após cada marco, registrar tarefas executadas, comandos de teste, resultados, falhas e mudanças que ainda faltam.
8. Caso a API e o banco não possam ser testados por falta de ambiente, **não** afirmar que o projeto está pronto. Relatar o bloqueio e preparar comandos reprodutíveis.
9. Ao finalizar, criar PR para revisão e relatar exatamente: `arquivo alterado`, `objetivo`, `teste realizado`, `resultado`, `risco residual`.
10. **Parar após a entrega do PR.** A auditoria profunda posterior será solicitada separadamente pelo usuário.

### Definição de pronto (DoD)

O projeto só é considerado implementado quando uma busca demonstrativa via browser atravessa `frontend → Flask → psycopg → PostgreSQL → Flask → frontend`, o banco contém as duas tabelas do enunciado, JOIN/UNION/EXCEPT foram demonstrados no SQL real, estados de erro são consistentes, a UI foi preservada, testes reais passaram e o README permite repetir tudo.

---

## 19. Plano da auditoria posterior (não executar ainda)

O usuário solicitou que a revisão profunda seja feita **depois** da implementação. Quando for solicitada, aplicar as lentes **NEXUS (`$nexus-review`/`$nexus-audit`)** e as rotinas **Ponytail (`/ponytail-review` e `/ponytail-audit`, quando a integração estiver de fato instalada na IA de código)**. A auditoria deve inspecionar mais do que o diff:

- **Correção:** parser/precedência, consultas SQL reais, contratos de API, estados de UI e erros de canto.
- **Segurança:** SQL injection, XSS, segredos, debug, acesso ao banco e erros HTTP.
- **Arquitetura:** duplicações JS/Python, abstrações desnecessárias, dependências, lógica em camadas erradas e risco de regressão.
- **Qualidade:** cobertura e utilidade dos testes, reprodutibilidade e ausência de exceções silenciosas.
- **UX/acessibilidade:** clareza de resultados didáticos, teclado, foco, mobile, latência, loading e erro.
- **Operação:** configuração Windows, falhas de PostgreSQL, reset de banco de teste, logging seguro e rollback.
- **Simplificação:** identificar código removível **sem** reduzir segurança, legibilidade nem funcionalidades exigidas.

Entregar achados priorizados em `P0/P1/P2/P3`, com evidência real (arquivo/linha, reprodução, impacto, correção e teste de regressão), distinguir melhorias desejáveis de bugs, e **não** declarar problemas hipotéticos como reproduzidos. Esta é uma **especificação da revisão futura**, não um relatório de auditoria já executada.

---

## 20. Fontes e trilha de evidências

- **Código SkyFetch inspecionado:** `https://github.com/VtecturboBr/SkyFetch` na branch `main`, commit `07ef49787339c4418e43d06d8f07c7cde9564b67`. Arquivos inspecionados: README, app.py, requirements, template, CSS, JS, testes, gitignore.
- **Ponytail consultado:** `https://github.com/DietrichGebert/ponytail`, `README.md`, `AGENTS.md`, `skills/ponytail/SKILL.md`, package.json. É uma metodologia para agentes, **não uma dependência do SkyFetch**.
- **NEXUS:** arquivo enviado pelo usuário, `NEXUS-WEB-MEGA-Skill-v1.1(1).md` (convenções de descoberta, especificação, planejamento, rastreabilidade, auditoria e handoff).
- **PostgreSQL — set operations:** https://www.postgresql.org/docs/current/queries-union.html — semântica de UNION/EXCEPT, compatibilidade de colunas e precedência.
- **Psycopg 3 — documentação:** https://www.psycopg.org/psycopg3/docs/basic/usage.html — conexão e consultas parametrizadas.
- **Flask — error handling:** https://flask.palletsprojects.com/en/stable/errorhandling/ — regras de tratamento HTTP.

**O que foi feito:** leitura de fontes, arquitetura, especificação, plano, análise de risco e auditoria estática v1.1; execução local dos oito testes JS do baseline e cinco casos adicionais de comportamento, conforme relatório separado.  
**O que não foi feito:** implementar, executar testes contra PostgreSQL/Flask, alterar repositório, abrir PR, fazer merge ou deploy.

**Próxima ação única:** entregar este documento à IA de código para começar pela **T001 (revalidação do repositório e da baseline)**, seguida de T002, sem iniciar uma revisão prematura antes de existir implementação verificável.
