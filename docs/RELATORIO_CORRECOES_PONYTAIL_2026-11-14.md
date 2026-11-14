# Correções e revisão posterior — SkyFetch

14/11/2026. Branch `feature/skyfetch-postgres-search`. Trabalho anterior preservado; sem commit ou publicação.

Seguidos os princípios [Ponytail](https://github.com/dietrichgebert/ponytail): corrigir a causa com recursos nativos, preservar validações e acrescentar testes específicos. Revisão por um único agente, sem alegar especialistas independentes.

| Achado | Correção | Verificação |
|---|---|---|
| A01: q repetido | getAll antes de reescrever URL ou fazer fetch inicial; erro sem resultados parciais, endereço preservado | Node e Chrome: dois valores válidos ou primeiro vazio; nova busca válida recupera a UI |
| A02: contraste | Cinco textos usam #637587, cor já existente no tema | Python e Chrome: contraste >=4,5:1 nos cinco elementos |
| A03: PostgreSQL 18 | Consulta inclui contype; comparação de PK/CHECK separada das entradas NOT NULL, mantendo attnotnull e todas as constraints validadas | PostgreSQL 17.12 real e catálogo 18 simulado; NOT NULL não validado e CHECK ausente continuam rejeitados |
| A04: espera | AbortController e prazo único de 15 s para fetch e JSON; timer limpo em finally; versionamento preservado | Node: fetch/JSON pendentes, prazo antigo durante nova busca, retry e limpeza. Chrome: prazo real de 15 s e retry com cinco resultados |
| A05: documentação | Referência aos oito testes substituída pela suíte atual; README descreve novo comportamento | Referências conferidas |

**Resultado final:** 102 testes Python e 14 testes Node passaram. O smoke Chrome também passou em 1280/768/390 px: resultados reais, sem overflow, teclado/chips/foco, URL/refresh/vazio, sintaxe inválida, XSS, erros HTTP/JSON/rede, concorrência, prazo/retry e redução de movimento. Nenhum erro JavaScript não tratado. Capturas atualizadas em `.nexus/plans/implementacao/evidence/`.

**Revisão de otimização:** nenhuma dependência adicionada. Um timer por busca, reutilizado para conexão e corpo JSON, limpo em todos os caminhos. A validação de URL ocorre na entrada inicial e mantém a proteção independente da API. O validador de schema reutiliza a consulta existente, sem consulta extra ou ramificação por versão. O contraste reutiliza a paleta. SQL de busca e API não precisaram mudar.

Os casos anteriores de parser, JOIN/UNION/EXCEPT, seed repetido, schema incompatível, permissões, parametrização e concorrência continuaram passando. Não foram detectadas regressões nos cenários executados. Isso não garante ausência absoluta de bugs.

**Limites:** PostgreSQL 18 foi coberto por catálogo simulado, não por servidor 18 real. Integração real executada no 17.12. Sem teste de carga, instalação em outra máquina ou auditoria WCAG completa. Nenhum commit, push ou deploy.
