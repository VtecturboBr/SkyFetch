# Decisões da preparação

- Escopo autorizado: somente etapas 1–3 da proposta na conversa, não confundir com T001–T003 do plano mestre (T002 inclui schema/seed, fora desta preparação).
- Cópia Git separada em `C:\Users\peter\Downloads\SkyFetch-dev`; branch `feature/skyfetch-postgres-search`; preservar o diretório original.
- Python 3.11 em `.venv`; Flask, psycopg binary e pytest; sem dependências globais.
- PostgreSQL 17.12 local ao usuário, somente loopback e sem serviço Windows; credenciais aleatórias fora do versionamento.
- Conexões distintas de aplicação, owner de instalação e owner de testes; testes isolados em `skyfetch_test`.
- Revisão v1.2 formaliza ligações na gramática e separa credenciais. Originais externos preservados.
- Sem schema/seed de negócio, parser, API, alterações de layout, commit, push, PR ou deploy nesta autorização.

## Autorização posterior — etapas 4 e 5

- O usuário pediu explicitamente implementar o núcleo e integrar a interface. A limitação anterior a etapas 1–3 passa a ser histórica; publicar/abrir PR permanece fora do escopo.
- Implementação mantém duas tabelas, SQL explícito parametrizado e gramática v1.2. Nomes formatados têm fonte única no Python.
- UI preservada, `requestVersion` e `replaceState`, sem fallback de arrays locais. O motor JS antigo foi removido após passar testes Python/Node e navegador real.
- Verificação de indisponibilidade usa uma porta local reservada sem serviço. Não foi desligado o cluster: o comando para essa interrupção foi rejeitado pela revisão automática, com a mensagem genérica `blocked by policy`.
