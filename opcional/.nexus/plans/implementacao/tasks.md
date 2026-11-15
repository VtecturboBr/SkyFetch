# Etapas 4 e 5 autorizadas

- [x] IMPL-001 — Schema/seed e setup seguro. PostgreSQL com duas tabelas; seed idempotente; validação de estrutura e órfãos; preservação de dados extras.
- [x] IMPL-002 — Parser Python com consumo total, aliases longos, precedência, limites e rejeições; testes de regressão dos defeitos do protótipo.
- [x] IMPL-003 — SQL parametrizado com JOIN/UNION/EXCEPT e timeout, confirmado no PostgreSQL real.
- [x] IMPL-004 — API GET e JSON estável; 400/422/503/500; sem segredos em logs/respostas e debug explícito.
- [x] IMPL-005 — Interface via fetch; loading/erro/zero/sucesso, URL e proteção de respostas antigas; testes Node e navegador real.
- [x] IMPL-006 — Remover motor JS e testes antigos somente após cobertura substituta e confirmação do fluxo ponta a ponta.
- [x] IMPL-007 — Encerrar revisão, documentação, evidências e testes finais. Execução final: 98 Python + 11 Node aprovados, browser real desktop/tablet/mobile aprovado, seed 4/4/5 em ambos os bancos, `pip check` e `git diff --check` aprovados. CSS e pasta original preservados; segredos locais ausentes dos arquivos compartilháveis.

Publicação, PR, commit e deploy não foram autorizados. Esta é a lista operacional; a lista da preparação foi encerrada anteriormente.
