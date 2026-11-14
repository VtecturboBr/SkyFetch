# Evidências e limites — 14/11/2026

- Baseline remota confirmada pelo clone: `07ef49787339c4418e43d06d8f07c7cde9564b67`. Sem `AGENTS.md` no checkout ou nos diretórios ancestrais verificados.
- Node baseline: oito testes passaram. Os defeitos conhecidos do parser demonstrativo permanecem; não foram incluídos no escopo autorizado.
- Python 3.11 disponível no launcher Windows; `.venv` criado explicitamente com `py -3.11 -m venv .venv`.
- Dependências instaladas localmente via `requirements-dev.txt`; nenhum conflito em `pip check`.
- PostgreSQL obtido do arquivo oficial EDB `postgresql-17.12-1-windows-x64-binaries.zip` (386263884 bytes). SHA256 observado: `a2cd8a774389347b70be7748ac4a37ef43cb6ee539c5fc3e85ae264b15e4a04c`. O hash registra o artefato recebido; não foi comparado a manifesto separado do fornecedor.
- Referências consultadas: https://www.postgresql.org/download/windows/ ; https://www.enterprisedb.com/download-postgresql-binaries ; https://www.psycopg.org/psycopg3/docs/basic/install.html .
- Cluster privado em `%LOCALAPPDATA%\SkyFetch\PostgreSQL17`, bind `127.0.0.1:5432`; autenticação SCRAM-SHA-256.
- `check_environment.py` passou: três conexões reais, papéis limitados, leitura permitida, escrita real recusada, três tentativas de acesso cruzado recusadas e limpeza da tabela descartável.
- Flask test client: `/` retornou HTTP 200 e `/api/search?q=voos` retornou 404, como esperado antes da implementação.
- Ciclo stop/start aprovado e start repetido reconhece servidor já ativo. O helper usa `WaitForExit` somente para pg_ctl; `Start-Process -Wait` aguardaria também o servidor filho no Windows.
- PostgreSQL escuta somente em `127.0.0.1:5432`. `.env` e `.venv` ignorados pelo Git. `git diff --check` passou. Python do ambiente: 3.11.9.
- Não implementado: schema/seed do exercício, parser Python, SQL de busca, API e integração frontend. Não executado: inspeção visual, testes do negócio futuro, PR e deploy.
