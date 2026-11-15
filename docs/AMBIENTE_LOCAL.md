# Ambiente local SkyFetch — etapas 1 a 5

Preparado em 14/11/2026 e atualizado após a implementação autorizada das etapas 4 e 5. A cópia original e os documentos externos foram preservados.

## Cópia de trabalho

- Diretório: `C:\Users\peter\Downloads\SkyFetch-dev`.
- Remoto: `https://github.com/VtecturboBr/SkyFetch.git`.
- Branch: `feature/skyfetch-postgres-search`.
- Baseline: `07ef49787339c4418e43d06d8f07c7cde9564b67`.
- Alterações preparadas localmente; sem commit, push, PR, merge ou deploy.

## Ativar e executar

Abra PowerShell no diretório de trabalho:

```powershell
Set-Location 'C:\Users\peter\Downloads\SkyFetch-dev'
. .\scripts\activate.ps1
.\scripts\postgres.ps1 start
python scripts/setup_database.py
python scripts/setup_database.py --test
python -B opcional/scripts/check_environment.py
python app.py
```

Abra `http://127.0.0.1:5000/`. `Ctrl+C` encerra Flask. O debug fica desligado por padrão; `$env:SKYFETCH_DEBUG='1'` o ativa explicitamente para desenvolvimento. A página consulta a API Flask e o PostgreSQL; não há arrays de demonstração no navegador.

O ponto seguido de espaço em `. .\scripts\activate.ps1` é necessário para ativar o ambiente no terminal atual. O script ativa `.venv`, carrega as três conexões do `.env` sem exibir seus valores e acrescenta os binários PostgreSQL ao PATH apenas nesse terminal. O Flask não lê `.env` automaticamente. Não é necessário mudar o PATH global nem a política de execução do Windows.

```powershell
.\scripts\postgres.ps1 status
.\scripts\postgres.ps1 stop
```

A instância PostgreSQL não é um serviço do Windows e não inicia automaticamente após reiniciar o computador. Execute `start` novamente quando necessário. `stop` encerra as conexões dessa instância; não apaga seus dados.

## Dependências

O ambiente virtual usa Python 3.11 e as dependências de `requirements-dev.txt`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check
```

Versões verificadas nesta preparação: Flask 3.1.3, psycopg/psycopg-binary 3.3.9 e pytest 9.2.0. Node.js é usado somente pelos testes de integra??o ass?ncrona em `tests/app.test.cjs`.

## PostgreSQL e credenciais

PostgreSQL 17.12 foi instalado a partir dos binários Windows x64 da EDB, indicados pela [página oficial PostgreSQL](https://www.postgresql.org/download/windows/). Não foram instalados pgAdmin, Docker ou serviço de sistema.

- Instalação e dados: `%LOCALAPPDATA%\SkyFetch\PostgreSQL17`.
- Executáveis: `pgsql\bin` dentro desse diretório.
- Dados persistentes: `data`.
- Log: `postgres.log`.
- Escuta: somente `127.0.0.1:5432`, com autenticação SCRAM-SHA-256.

| Variável | Banco | Papel | Finalidade |
|---|---|---|---|
| `DATABASE_URL` | `skyfetch` | `skyfetch_user` | Leitura das tabelas da aplicação |
| `SETUP_DATABASE_URL` | `skyfetch` | `skyfetch_owner` | Criação de tabelas e seed futuros |
| `TEST_DATABASE_URL` | `skyfetch_test` | `skyfetch_test_owner` | Testes em banco exclusivo |

Os três papéis não são superusuários e não podem criar bancos ou papéis. Os papéis de desenvolvimento não conectam ao banco de testes, e o owner de testes não conecta ao banco de desenvolvimento. O usuário da aplicação não pode criar tabelas. As tabelas futuras criadas pelo owner no schema `public` concedem automaticamente apenas SELECT à aplicação.

As senhas aleatórias estão somente no `.env` local, ignorado pelo Git. `.env.example` é um modelo sem senhas reais. A credencial administrativa do cluster está em `admin.json` dentro da instalação local, fora do repositório. O `.env` e a instalação local têm acesso restrito ao usuário Windows atual e SYSTEM. Não copie esses arquivos para documentação, mensagens, Git ou screenshots.

Os dois bancos contêm o schema e o seed do exercício: quatro linhas por tabela e cinco combinações no JOIN. Use `python scripts/setup_database.py` para desenvolvimento e `python scripts/setup_database.py --test` para testes. O helper valida colunas, tipos, NOT NULL, chaves, CHECKs e cidades órfãs antes de confirmar a transação. Ele falha com orientação para migração manual se encontrar incompatibilidade e não limpa dados existentes. Contagens podem ser maiores quando houver dados adicionais.

Nunca execute scripts de criação pela conexão somente leitura da aplicação e nunca reutilize o banco de desenvolvimento nos testes. Os arquivos SQL também podem ser abertos no pgAdmin/SQL Shell; prefira o helper para validar o schema existente antes de aplicar o seed. Não é necessário `psql` no PATH para usar o helper.

## Preparar bancos em outra instalação

Instale Python 3.11 e PostgreSQL a partir da página oficial indicada acima. Em outra instalação, o servidor pode ser um serviço Windows: o helper `postgres.ps1` controla somente a instalação privada já preparada nesta máquina.

No SQL Shell (`psql`) ou pgAdmin, conecte como administrador ao banco `postgres`. Execute os comandos de criação de banco fora de uma transação explícita. As senhas abaixo são exemplos que precisam ser substituídos localmente:

```sql
CREATE ROLE skyfetch_owner LOGIN PASSWORD 'SENHA_OWNER' NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE skyfetch_user LOGIN PASSWORD 'SENHA_APP' NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE skyfetch_test_owner LOGIN PASSWORD 'SENHA_TESTE' NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE DATABASE skyfetch OWNER skyfetch_owner;
CREATE DATABASE skyfetch_test OWNER skyfetch_test_owner;
REVOKE ALL ON DATABASE skyfetch FROM PUBLIC;
REVOKE ALL ON DATABASE skyfetch_test FROM PUBLIC;
GRANT CONNECT ON DATABASE skyfetch TO skyfetch_user;
```

Conecte ao banco `skyfetch` como administrador/owner e execute:

```sql
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO skyfetch_user;
ALTER DEFAULT PRIVILEGES FOR ROLE skyfetch_owner IN SCHEMA public
    GRANT SELECT ON TABLES TO skyfetch_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO skyfetch_user;
```

No banco `skyfetch_test`, revogue também `CREATE ON SCHEMA public FROM PUBLIC`; o owner continua criando as tabelas dos testes. Se os nomes já existirem, inspecione-os e seus privilégios antes de alterar; não apague bancos ou papéis para repetir o setup. Copie `.env.example` somente se o `.env` não existir, edite as três conexões e ative o ambiente conforme o README.

## Verificações disponíveis

```powershell
. .\scripts\activate.ps1
python -B opcional/scripts/check_environment.py
python -m pip check
node --test tests/app.test.cjs
python -m pytest -q
```

`check_environment.py` verifica versões, schema/integridade, identidades, limites dos papéis, isolamento dos bancos, página Flask e API com dados do PostgreSQL. Ele cria uma tabela descartável com nome único no banco de desenvolvimento, comprova leitura e recusa de escrita pela aplicação e remove somente essa tabela ao final, preservando o schema e os dados existentes.

A API `/api/search?q=voos` responde 200 com cinco combinações no seed inicial. A suíte Python cobre parser, contrato HTTP e PostgreSQL real; a suíte Node cobre loading, erros, eventos, URL e concorrência. O motor demonstrativo e seus testes foram substituídos após comprovar a cobertura e o fluxo real no navegador.

## Planejamento revisado

Os arquivos de referência estão em `opcional/docs/planning/`. O mestre v1.2 e seu prompt distinguem instalação, leitura e testes. A gramática agora representa uma ligação opcional após a introdução (`voos da latam`) e uma ligação entre termos (`latam em Belém`), com rejeição de ligações soltas, repetidas ou após operadores. A auditoria v1.1 foi copiada sem alterar seu histórico.

As etapas 4 e 5 foram autorizadas posteriormente e implementadas. Commit, push, PR, merge e deploy não fazem parte desta autorização. O estado atual e as evidências estão em `opcional/.nexus/plans/implementacao/`.
