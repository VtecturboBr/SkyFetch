# Critérios do plano mestre — estado após etapas 4 e 5

| Critério | Estado | Evidência / limite |
|---|---|---|
| AC-001 interface preservada | CONFIRMADO | Chrome 1280/768/390 px, capturas inspecionadas, CSS inalterado |
| AC-002 schema/seed | CONFIRMADO | PostgreSQL real: 4/4/5 em desenvolvimento e testes; seed repetido |
| AC-003 Flask/PostgreSQL | CONFIRMADO | Navegador → API → banco → cartões; falha de conexão sem dados fictícios |
| AC-004 parser | CONFIRMADO | Aliases, acentos, gramática v1.2, precedência, rejeições e limites |
| AC-005 operações SQL | CONFIRMADO | JOIN/UNION/EXCEPT parametrizados executados no PostgreSQL, matriz de conjuntos |
| AC-006 contrato API | CONFIRMADO | JSON estável, q repetido, HTTP 200/400/422/503/500, valores parametrizados |
| AC-007 frontend API | CONFIRMADO | Motor local removido, fetch real e proteção de respostas antigas |
| AC-008 erros | CONFIRMADO | Testes de API, banco e browser; loading, zero, inválido, 503/500/rede/JSON |
| AC-009 testes | CONFIRMADO | 98 Python, 11 Node e smoke Chrome real aprovados |
| AC-010 setup em outra máquina | NÃO VERIFICADO | README e instruções SQL atualizados; instalação limpa em outra máquina não executada |
| AC-011 preservação/segurança | CONFIRMADO NO ESCOPO | Fonte original preservada; testes de parametrização/XSS, permissões e logs; credencial de teste exposta em falha inicial foi renovada; não substitui auditoria profunda |
| AC-012 branch/PR | NÃO VERIFICADO | Branch separada existente, sem PR/commit/push porque não foram autorizados |

O teste de parada real do cluster foi bloqueado pela revisão automática. A alternativa confirma recusa real de conexão, erro 503 e preservação da página sem interromper PostgreSQL. Não afirmar que o desligamento foi executado.
