"""Valida schema antes de aplicar criação/seed, sem apagar dados existentes."""

import argparse
import os
from pathlib import Path
import re
import sys

import psycopg
from psycopg.conninfo import conninfo_to_dict

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "companhia_aerea": (['companhia', 'cidade'], {
        "checklengthbtrimcompanhia>0", "checklengthbtrimcidade>0",
        "primarykeycompanhia,cidade",
    }),
    "cidades": (['cidade', 'turno'], {
        "checklengthbtrimcidade>0", "checkturno=anyarray['manha','tarde','noite']",
        "primarykeycidade,turno",
    }),
}


class SchemaError(RuntimeError):
    pass


def canonical(definition):
    return re.sub(r"\s|[()]|::text", "", definition.lower()).replace('trimbothfrom', 'btrim')


def validate_schema(connection, allow_missing=False):
    for table, (columns, constraints) in EXPECTED.items():
        relation = connection.execute(
            "SELECT c.oid, c.relkind FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname='public' AND c.relname=%s", (table,),
        ).fetchone()
        if relation is None:
            if allow_missing:
                continue
            raise SchemaError(f"Tabela public.{table} ausente. Execute o setup com a conexão owner.")
        oid, kind = relation
        actual_columns = connection.execute(
            "SELECT attname, format_type(atttypid, atttypmod), attnotnull "
            "FROM pg_attribute WHERE attrelid=%s AND attnum>0 AND NOT attisdropped ORDER BY attnum", (oid,),
        ).fetchall()
        actual_constraints = connection.execute(
            "SELECT pg_get_constraintdef(oid), convalidated, contype FROM pg_constraint WHERE conrelid=%s", (oid,),
        ).fetchall()
        if (kind != 'r' or actual_columns != [(col, 'text', True) for col in columns]
                # PostgreSQL 18 também registra NOT NULL; attnotnull é verificado acima.
                or {canonical(row[0]) for row in actual_constraints if row[2] != 'n'} != constraints
                or not all(row[1] for row in actual_constraints)):
            raise SchemaError(f"Schema incompatível em public.{table}. Faça migração manual com backup; nenhum dado foi apagado.")


def validate_integrity(connection):
    orphan = connection.execute(
        "SELECT 1 FROM public.companhia_aerea a WHERE NOT EXISTS "
        "(SELECT 1 FROM public.cidades c WHERE c.cidade=a.cidade) LIMIT 1"
    ).fetchone()
    if orphan:
        raise SchemaError("Há companhia com cidade sem turno correspondente. Corrija os dados manualmente, sem exclusão automática.")


def initialize(connection):
    # O context manager do chamador garante rollback também se o seed falhar.
    validate_schema(connection, allow_missing=True)
    connection.execute((ROOT / 'db/schema.sql').read_text(encoding='utf-8'))
    validate_schema(connection)
    validate_integrity(connection)
    connection.execute((ROOT / 'db/seed.sql').read_text(encoding='utf-8'))
    validate_integrity(connection)
    return connection.execute(
        "SELECT (SELECT count(*) FROM public.companhia_aerea), "
        "(SELECT count(*) FROM public.cidades), "
        "(SELECT count(*) FROM public.companhia_aerea a JOIN public.cidades c USING (cidade))"
    ).fetchone()


def test_database_url():
    url = os.environ.get('TEST_DATABASE_URL')
    if not url:
        raise SchemaError('Defina TEST_DATABASE_URL explicitamente para os testes.')
    test = conninfo_to_dict(url)
    if not test.get('dbname') or not test['dbname'].endswith('_test'):
        raise SchemaError('O banco descartável deve ter nome terminado em _test.')
    for key in ('DATABASE_URL', 'SETUP_DATABASE_URL'):
        if os.environ.get(key) and conninfo_to_dict(os.environ[key]).get('dbname') == test['dbname']:
            raise SchemaError('Recusado: banco de testes com o mesmo nome do banco de desenvolvimento.')
    return url


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test', action='store_true', help='usar somente TEST_DATABASE_URL')
    args = parser.parse_args()
    try:
        url = test_database_url() if args.test else os.environ.get('SETUP_DATABASE_URL')
        if not url:
            raise SchemaError('Defina SETUP_DATABASE_URL; não use a conexão de leitura da aplicação.')
        with psycopg.connect(url, connect_timeout=3, options='-c statement_timeout=5000') as connection:
            counts = initialize(connection)
        print(f'Schema validado e seed aplicado: {counts[0]} linhas de companhias, {counts[1]} de cidades, {counts[2]} combinações.')
        print('Contagens podem ser maiores em banco com dados adicionais; nenhum registro existente foi removido.')
    except SchemaError as exc:
        print(f'FALHA: {exc}', file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:
        print(f'FALHA: {type(exc).__name__}. Confira conexão, permissões e schema; credenciais não foram exibidas.', file=sys.stderr)
        raise SystemExit(1)
