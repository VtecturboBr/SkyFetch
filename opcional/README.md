# Material opcional

Esta pasta reúne material que pode ser removido sem afetar a execução da aplicação:

- `.nexus/`: planejamento, histórico de trabalho, relatórios de progresso e capturas.
- `docs/`: planos e relatórios de análise/correções.
- `scripts/browser_smoke.cjs`: verificação opcional no Chrome com Playwright externo.
- `scripts/check_environment.py`: diagnóstico de ambiente e permissões.

Os documentos arquivados podem descrever caminhos anteriores à reorganização; são registros históricos. O guia atual de execução permanece em `../docs/AMBIENTE_LOCAL.md` e no README principal.

Execute os scripts opcionais a partir da raiz do projeto:

```powershell
. .\scripts\activate.ps1
python -B opcional/scripts/check_environment.py
# Com Playwright disponível no NODE_PATH e servidor de teste iniciado:
node opcional/scripts/browser_smoke.cjs
```

Se remover esta pasta futuramente, remova também as referências opcionais do README. A aplicação, o setup do banco e os testes Python/Node leves não dependem dela.

Os caches são recriados automaticamente e não foram arquivados. `.venv`, `tests`, `pytest.ini` e `requirements-dev.txt` foram mantidos na raiz para preservar o ambiente e a verificação do projeto.
