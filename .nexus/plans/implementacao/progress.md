# Verificação das etapas 4 e 5 — 14/11/2026

Núcleo Python/PostgreSQL e integração da interface implementados na branch `feature/skyfetch-postgres-search`, em `C:\Users\peter\Downloads\SkyFetch-dev`. A pasta original foi preservada.

## Resultado real

- Python: **98 testes passaram**, sem skips no ambiente preparado. Incluem gramática, API, matriz SQL em PostgreSQL, seed repetido, schema incompatível, órfãos, dados adicionais, parametrização, tabela ausente (500), timeout real (503) e recusa real de conexão (503).
- Node: **11 testes passaram**. Cobrem loading, retorno do servidor, Enter/chips/foco, URL/vazio, erros de API/JSON/rede, respostas fora de ordem e `catch/finally` antigos.
- `scripts/check_environment.py`: passou com conexões reais, schema, API, leitura limitada e isolamento dos bancos.
- Chrome headless real: cinco combinações PostgreSQL renderizadas em 1280, 768 e 390 px; sem overflow horizontal. Enter, chips, foco, URL/refresh, vazio, consulta longa, XSS, loading, erro 503/500/JSON/offline, retry, respostas fora de ordem e redução de movimento passaram. Nenhum erro JavaScript não tratado.
- Capturas desktop e mobile inspecionadas visualmente; layout, cores e cartões preservados. CSS existente sem alterações.
- Ambos os bancos contêm quatro linhas por tabela e cinco combinações; o seed foi aplicado novamente sem duplicações. Testes de alterações do schema/dados usam transações revertidas no banco exclusivo.
- Execução final após remover o motor antigo: 98 Python e 11 Node passaram novamente, browser completo aprovado, `pip check` sem conflitos e `git diff --check` sem erros. Dez arquivos originais comparados à baseline e preservados; CSS da cópia de trabalho inalterado; nenhuma das três senhas locais encontrada nos arquivos compartilháveis.

## Evidências

- [Desktop](evidence/desktop.png), [tablet](evidence/tablet.png), [mobile](evidence/mobile.png).
- [Resultado do browser](evidence/browser-result.json).

## Repetir o smoke opcional de navegador

O Playwright foi instalado somente em `%LOCALAPPDATA%\SkyFetch\browser-qa`, fora das dependências do projeto. Usa o Chrome já instalado, sem instalar navegador adicional:

```powershell
# Terminal 1, com banco iniciado e variáveis carregadas:
. .\scripts\activate.ps1
python -m flask --app app run --host 127.0.0.1 --port 5055

# Terminal 2, no diretório do projeto:
$qaRoot=Join-Path $env:LOCALAPPDATA 'SkyFetch\browser-qa'
npm.cmd install --prefix $qaRoot playwright --no-audit --no-fund
$env:NODE_PATH=Join-Path $qaRoot 'node_modules'
node scripts/browser_smoke.cjs
```

O smoke simula algumas falhas de rede/HTTP no browser; as recusas de conexão, timeout e tabela ausente também têm testes de backend/PostgreSQL. O script não é requisito para executar a aplicação nem para os testes Node leves.

## Limites e ocorrências

- O teste que desligaria o PostgreSQL foi rejeitado pela revisão automática com `blocked by policy`, sem detalhamento. O cluster não foi interrompido; a alternativa aprovada verifica recusa real numa porta local reservada sem serviço e mantém a página disponível.
- Um teste de fechamento de conexão inicialmente falhou, exibindo a configuração de conexão de teste no traceback. A credencial de testes foi renovada, as fixtures passaram a ocultar DSNs e os tracebacks foram reduzidos. A execução final passou.
- Sem commit, push, PR, merge, deploy ou auditoria profunda posterior. Não foram introduzidas dependências adicionais de produção, além do psycopg já preparado.
