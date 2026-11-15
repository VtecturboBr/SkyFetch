# Preparação autorizada — etapas 1 a 3

Esta é a única lista operacional desta preparação. As tarefas T001–T012 do plano mestre descrevem uma implementação futura, de escopo mais amplo.

- [x] PREP-001 — Clonar sem sobrescrever a pasta original e criar branch separada. Evidência: origin GitHub, HEAD `07ef49787339c4418e43d06d8f07c7cde9564b67`, branch `feature/skyfetch-postgres-search`; oito testes Node passaram.
- [x] PREP-002 — Preparar mestre/prompt v1.2 e preservar os originais. Evidência: gramática com `LINK`, conexão `SETUP_DATABASE_URL` distinta de `DATABASE_URL`, banco/owner de testes exclusivos, referências do prompt atualizadas.
- [x] PREP-003 — Criar `.venv` Python 3.11 e instalar dependências. Evidência: Flask 3.1.3, psycopg 3.3.9, pytest 9.2.0; `pip check` aprovado.
- [x] PREP-004 — Preparar PostgreSQL e dois bancos isolados. Evidência: PostgreSQL 17.12 em loopback; três papéis sem privilégios administrativos; conexão real, SELECT e recusa de escrita/cross-access verificados; bancos vazios após verificação.
- [x] PREP-005 — Concluir verificação de reinício, documentação e revisão dos arquivos preparados. Evidência: ciclo stop/start/status e start repetido aprovados; `check_environment.py`, `pip check` e oito testes Node aprovados; `git diff --check` limpo; escuta somente em 127.0.0.1; `.env` e `.venv` ignorados.

Próxima etapa após esta preparação depende de nova autorização: implementar schema/seed, parser e SQL de busca. Não iniciá-la automaticamente.
