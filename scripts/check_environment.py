"""Verifica ambiente, permissoes e integracao Flask/PostgreSQL local."""

import importlib.metadata
import os
from pathlib import Path
import sys
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.setup_database import validate_schema, validate_integrity


def check(condition, description):
    if not condition:
        raise RuntimeError(description)
    print(f"OK: {description}")


def main():
    check(sys.version_info[:2] == (3, 11), "Python 3.11")
    check(sys.prefix != sys.base_prefix, "ambiente virtual ativo")
    for package in ("Flask", "psycopg", "psycopg-binary", "pytest"):
        print(f"{package}: {importlib.metadata.version(package)}")

    configs = {
        key: conninfo_to_dict(os.environ[key])
        for key in ("DATABASE_URL", "SETUP_DATABASE_URL", "TEST_DATABASE_URL")
    }
    app_config = configs["DATABASE_URL"]
    setup_config = configs["SETUP_DATABASE_URL"]
    test_config = configs["TEST_DATABASE_URL"]
    check(app_config["dbname"] == setup_config["dbname"] == "skyfetch", "banco de desenvolvimento separado")
    check(test_config["dbname"] == "skyfetch_test", "banco exclusivo skyfetch_test")
    check(len({c["user"] for c in configs.values()}) == 3, "tres usuarios distintos")

    for name, config in configs.items():
        with psycopg.connect(**config, connect_timeout=3) as conn:
            row = conn.execute(
                "SELECT current_database(), current_user, "
                "rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls "
                "FROM pg_roles WHERE rolname = current_user"
            ).fetchone()
            check(row[:2] == (config["dbname"], config["user"]) and not row[2], f"{name}: identidade e privilegios limitados")
            tables = conn.execute(
                "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"
            ).fetchone()[0]
            check(tables >= 2, f"{name}: tabelas do exercicio presentes")
            validate_schema(conn)
            validate_integrity(conn)
            if name == "DATABASE_URL":
                can_create = conn.execute("SELECT has_schema_privilege(current_user, 'public', 'CREATE')").fetchone()[0]
                check(not can_create, "aplicacao sem permissao de criar tabelas")

    # Prova o SELECT automatico e a recusa de escrita numa tabela descartavel.
    probe = sql.Identifier("skyfetch_environment_probe_" + uuid4().hex[:12])
    with psycopg.connect(**setup_config, connect_timeout=3, autocommit=True) as owner:
        tables_before = owner.execute("SELECT count(*) FROM pg_tables WHERE schemaname = 'public'").fetchone()[0]
        owner.execute(sql.SQL("CREATE TABLE public.{} (value integer)").format(probe))
        try:
            owner.execute(sql.SQL("INSERT INTO public.{} VALUES (42)").format(probe))
            with psycopg.connect(**app_config, connect_timeout=3, autocommit=True) as reader:
                row = reader.execute(sql.SQL("SELECT value FROM public.{}").format(probe)).fetchone()
                check(row == (42,), "aplicacao le tabelas criadas pelo owner")
                for privilege in ("INSERT", "UPDATE", "DELETE", "TRUNCATE"):
                    allowed = reader.execute(
                        "SELECT has_table_privilege(current_user, %s, %s)",
                        (f'public.{probe.as_string(owner)}', privilege),
                    ).fetchone()[0]
                    check(not allowed, f"aplicacao sem {privilege}")
                try:
                    reader.execute(sql.SQL("INSERT INTO public.{} VALUES (99)").format(probe))
                except psycopg.errors.InsufficientPrivilege:
                    print("OK: escrita real recusada pelo PostgreSQL")
                else:
                    raise RuntimeError("aplicacao conseguiu escrever")
        finally:
            owner.execute(sql.SQL("DROP TABLE public.{}").format(probe))
        check(owner.execute("SELECT count(*) FROM pg_tables WHERE schemaname = 'public'").fetchone()[0] == tables_before,
              "tabela de verificacao removida; tabelas existentes preservadas")

    for config, other_db in ((app_config, "skyfetch_test"), (setup_config, "skyfetch_test"), (test_config, "skyfetch")):
        try:
            with psycopg.connect(**{**config, "dbname": other_db}, connect_timeout=3):
                raise RuntimeError("acesso cruzado entre bancos permitido")
        except psycopg.OperationalError as exc:
            # Erros na abertura via libpq podem nao transportar SQLSTATE.
            denied = exc.sqlstate == "42501" or "permission denied for database" in str(exc)
            check(denied, "acesso cruzado entre bancos recusado por permissao")

    from app import app

    with app.test_client() as client:
        page = client.get("/")
        check(page.status_code == 200 and b"SkyFetch" in page.data, "pagina Flask atual responde HTTP 200")
        result = client.get("/api/search?q=voos")
        check(result.status_code == 200 and result.json['total'] >= 5,
              "API de busca retorna dados reais do PostgreSQL")
    print("Ambiente, schema, permissoes e API verificados.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Erros de conexao podem conter credenciais; nao imprimir a mensagem bruta.
        print(f"FALHA: {type(exc).__name__}. Revise o ambiente local sem compartilhar o .env.", file=sys.stderr)
        raise SystemExit(1)
