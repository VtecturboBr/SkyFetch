# SkyFetch ✈

Buscador acadêmico PRJ.9 com Python, Flask, PostgreSQL e linguagem textual restrita. A interface original foi preservada e agora recebe seus resultados exclusivamente da API.

Os dados são fictícios: cada resultado é uma combinação de companhia, cidade e turno das duas tabelas do exercício, sem horários, preços ou voos reais.

## Executar nesta máquina

Use a cópia Git `C:\Users\peter\Downloads\SkyFetch-dev`, branch `feature/skyfetch-postgres-search`:

```powershell
Set-Location 'C:\Users\peter\Downloads\SkyFetch-dev'
. .\scripts\activate.ps1
.\scripts\postgres.ps1 start
python scripts/setup_database.py
python app.py
```

Abra **http://127.0.0.1:5000/**. O setup valida o schema, preserva dados existentes e aplica o seed sem duplicações. Não use a conexão somente leitura da aplicação para criar tabelas. A instância PostgreSQL local não inicia automaticamente após reiniciar o computador.

`debug` fica desligado por padrão. Para desenvolvimento local, pode ser ativado explicitamente com `$env:SKYFETCH_DEBUG='1'`. O servidor Flask de desenvolvimento não deve ser usado em produção.

## Preparar outro ambiente

Use Python 3.11 e PostgreSQL 17 ou outra versão suportada compatível. Node.js só é necessário para os testes da interface.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Prepare os bancos e papéis conforme [Ambiente local](docs/AMBIENTE_LOCAL.md), substitua os exemplos do `.env` pelas conexões locais e execute `. .\scripts\activate.ps1`. Esse helper lê somente as três variáveis de conexão; o Flask não carrega `.env` automaticamente. Nunca compartilhe o arquivo real.

## Linguagem de busca

- `voos` → todas as cinco combinações iniciais.
- `voos latam e manhã` → filtros AND.
- `voos latam ou azul` → UNION sem duplicações.
- `voos latam ou gol exceto noturnos` → EXCEPT sobre a inclusão inteira.
- `voos da latam em Belém` e `voos São José dos Campos` → ligações e aliases.
- `voos latam manaus` → consulta válida sem correspondências no seed.

Precedência: `e`/justaposição, depois `ou`, depois `exceto`. No máximo um `exceto`, 150 caracteres, 12 filtros e 8 cláusulas ao todo, incluindo exclusões. Não são aceitos parênteses, pontuação, palavras desconhecidas, operadores incompletos ou ligações soltas. O parser consome toda a frase.

## API

`GET /api/search?q=<frase>` retorna `status`, `query`, `total`, `items` e `isDemoData: true`. Buscas válidas incluem `interpreted`; erros incluem `error.code` e `error.message`. Cada item contém códigos e nomes de apresentação fornecidos pelo Python.

| HTTP | Significado |
|---|---|
| 200 | Resultados ou consulta válida sem correspondências |
| 400 | Pesquisa ausente/vazia ou maior que 150 caracteres |
| 422 | Sintaxe/vocabulário inválidos ou parâmetro `q` repetido |
| 503 | Conexão/configuração do banco indisponível ou timeout |
| 500 | Falha inesperada, incluindo tabela ausente/schema incorreto |

O navegador usa `fetch`, estados de carregamento/erro e `requestVersion` para descartar respostas antigas. A URL usa `replaceState`, respeita `?q=` vazio e preserva outros parâmetros. Não existe fallback para dados locais.

URLs com `q` repetido são rejeitadas também pela página, sem descartar valores silenciosamente. Um prazo de 15 segundos cobre a requisição e a leitura do JSON; após expirar, a interface libera o carregamento e permite nova tentativa.

## Testes

```powershell
. .\scripts\activate.ps1
.\scripts\postgres.ps1 start
python scripts/setup_database.py --test
python -m pytest -q
node --test tests/app.test.cjs
python -B opcional/scripts/check_environment.py
python -m pip check
```

Integração usa exclusivamente `TEST_DATABASE_URL`, em banco com nome terminado em `_test`, diferente do desenvolvimento. A suíte aplica schema/seed nesse banco e reverte as alterações dos testes de casos extremos. Sem a variável explícita, testes de integração são marcados como não executados; isso não comprova o funcionamento do PostgreSQL.

O smoke opcional em navegador real está em `opcional/scripts/browser_smoke.cjs`. Instruções e capturas desktop/tablet/mobile: [Verificação da implementação](opcional/.nexus/plans/implementacao/progress.md).

## Estrutura

```text
app.py                       Flask, página e API
skyfetch/parser.py           validação, aliases e gramática
skyfetch/repository.py       SQL parametrizado JOIN/UNION/EXCEPT
db/schema.sql, db/seed.sql   duas tabelas e dados do exercício
scripts/setup_database.py   validação do schema/integridade e seed idempotente
static/js/app.js            integração assíncrona e DOM seguro
templates/, static/css/     interface existente preservada
tests/                      parser, API, PostgreSQL real e UI assíncrona
```

Planejamento: [mestre v1.2](opcional/docs/planning/SKYFETCH_PLANO_MESTRE_REVISADO_v1.2.md). O método NEXUS e a auditoria fornecida são documentos de referência, não dependências da aplicação nem evidência de testes executados.
