from unittest.mock import Mock
import socket

import psycopg
import pytest
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from app import app
from scripts.setup_database import SchemaError, initialize, test_database_url as get_test_url, validate_integrity, validate_schema
from skyfetch import repository
from skyfetch.parser import parse_query

ALL = {('latam', 'sjc', 'tarde'), ('latam', 'sjc', 'noite'), ('latam', 'bel', 'manha'),
       ('gol', 'bel', 'manha'), ('azul', 'campinas', 'noite')}
LATAM = {r for r in ALL if r[0] == 'latam'}
DAY = {r for r in ALL if r[2] != 'noite'}


@pytest.mark.integration
@pytest.mark.parametrize('query,expected', [
    ('voos', ALL), ('voos da latam em Belém', {('latam', 'bel', 'manha')}),
    ('voos latam', LATAM), ('voos gol', {('gol', 'bel', 'manha')}),
    ('voos azul', {('azul', 'campinas', 'noite')}),
    ('voos latam e manhã', {('latam', 'bel', 'manha')}),
    ('voos latam bel', {('latam', 'bel', 'manha')}),
    ('voos latam ou azul', {r for r in ALL if r[0] in {'latam', 'azul'}}),
    ('voos bel', {r for r in ALL if r[1] == 'bel'}),
    ('voos sjc', {r for r in ALL if r[1] == 'sjc'}),
    ('voos São José dos Campos', {r for r in ALL if r[1] == 'sjc'}),
    ('voos Belém', {r for r in ALL if r[1] == 'bel'}),
    ('voos noturnos', ALL - DAY), ('voos latam exceto noturnos', LATAM & DAY),
    ('voos gol exceto noturnos', {('gol', 'bel', 'manha')}),
    ('voos exceto noturnos', DAY), ('exceto noturnos', DAY),
    ('voos latam ou gol exceto noturnos', DAY),
    ('voos latam e campinas', set()), ('voos latam manaus', set()),
    ('voos latam e gol', set()), ('voos latam ou gol exceto noite ou tarde', {r for r in ALL if r[2] == 'manha'}),
    ('latam ou latam', LATAM), ('gol ou latam e noite', {('gol', 'bel', 'manha'), ('latam', 'sjc', 'noite')}),
    ('voos São Paulo', set()), ('voos Salvador', set()), ('voos Porto Alegre', set()),
])
def test_real_sql_matrix(database_url, query, expected):
    rows = repository.search(parse_query(query), database_url)
    assert set(rows) == expected
    assert rows == sorted(rows)
    assert len(rows) == len(set(rows))


@pytest.mark.integration
def test_idempotent_seed_schema_and_counts(connection):
    assert initialize(connection) == (4, 4, 5)
    assert initialize(connection) == (4, 4, 5)
    validate_schema(connection)
    validate_integrity(connection)


@pytest.mark.integration
@pytest.mark.parametrize('alter', [
    'ALTER TABLE public.companhia_aerea ALTER COLUMN companhia TYPE varchar(30)',
    'ALTER TABLE public.companhia_aerea DROP CONSTRAINT companhia_aerea_pkey',
    'ALTER TABLE public.cidades DROP CONSTRAINT cidades_turno_check',
    'ALTER TABLE public.cidades DROP CONSTRAINT cidades_pkey; ALTER TABLE public.cidades ALTER COLUMN turno DROP NOT NULL',
    'ALTER TABLE public.cidades RENAME TO cidades_incompativeis',
])
def test_incompatible_schema_detected_without_deleting_data(connection, alter):
    connection.execute(alter)
    with pytest.raises(SchemaError):
        validate_schema(connection)


@pytest.mark.integration
def test_orphans_detected_and_additional_data_preserved(connection):
    connection.execute("INSERT INTO public.companhia_aerea VALUES ('nova', 'sem turno')")
    with pytest.raises(SchemaError):
        validate_integrity(connection)
    connection.execute("INSERT INTO public.cidades VALUES ('sem turno', 'tarde')")
    assert initialize(connection) == (5, 5, 6)
    assert connection.execute("SELECT count(*) FROM public.companhia_aerea WHERE companhia='nova'").fetchone()[0] == 1


@pytest.mark.integration
def test_parameters_even_if_parser_bypassed(connection):
    query, params = repository.build_query({'include': [[{'field': 'company', 'value': "latam' OR 1=1 --"}]], 'exclude': []})
    assert params == ["latam' OR 1=1 --"] and params[0] not in query
    assert connection.execute(query, params).fetchall() == []
    assert connection.execute('SELECT count(*) FROM public.cidades').fetchone()[0] == 4


@pytest.mark.integration
def test_api_through_real_database(database_url, monkeypatch):
    monkeypatch.setenv('DATABASE_URL', database_url)
    with app.test_client() as client:
        response = client.get('/api/search?q=latam+ou+gol+exceto+noturnos')
        assert response.status_code == 200
        assert response.json['total'] == 3
        assert all(item['shift'] != 'noite' for item in response.json['items'])


@pytest.mark.integration
def test_missing_table_is_500_and_rolls_back(database_url, monkeypatch):
    connection = psycopg.connect(database_url)
    try:
        connection.execute('ALTER TABLE public.cidades RENAME TO cidades_ausentes')
        with monkeypatch.context() as patch:
            patch.setattr(psycopg, 'connect', Mock(return_value=connection))
            patch.setenv('DATABASE_URL', 'test-connection')
            with app.test_client() as client:
                response = client.get('/api/search?q=voos')
                assert response.status_code == 500 and response.json['status'] == 'internal-error'
    finally:
        if not connection.closed:
            connection.rollback()
            connection.close()
    # O repositório fecha sua conexão e reverte a renomeação ao receber o erro SQL.
    with psycopg.connect(database_url) as restored:
        assert restored.execute("SELECT to_regclass('public.cidades')").fetchone()[0] is not None


@pytest.mark.integration
def test_real_query_timeout_maps_to_503(database_url, monkeypatch):
    connect = psycopg.connect
    monkeypatch.setenv('DATABASE_URL', database_url)
    monkeypatch.setattr(psycopg, 'connect', lambda dsn, **kwargs: connect(
        dsn, connect_timeout=3, options='-c statement_timeout=1 -c default_transaction_read_only=on'))
    monkeypatch.setattr(repository, 'build_query', lambda _: ("SELECT 'latam', 'bel', 'manha' FROM pg_sleep(0.05)", []))
    with app.test_client() as client:
        response = client.get('/api/search?q=voos')
        assert response.status_code == 503 and response.json['status'] == 'service-unavailable'


@pytest.mark.integration
def test_real_connection_refused_maps_to_503(database_url, monkeypatch, caplog):
    # Reservar uma porta sem listen produz recusa local sem interromper o banco.
    with socket.socket() as unused:
        unused.bind(('127.0.0.1', 0))
        config = conninfo_to_dict(database_url)
        config.update(host='127.0.0.1', port=str(unused.getsockname()[1]))
        monkeypatch.setenv('DATABASE_URL', make_conninfo(**config))
        with app.test_client() as client:
            assert client.get('/').status_code == 200
            response = client.get('/api/search?q=voos')
            assert response.status_code == 503 and response.json['items'] == []
            assert response.json['status'] == 'service-unavailable'
        assert config['password'] not in caplog.text


def test_sql_operators_and_column_allowlist():
    query, params = repository.build_query(parse_query('latam ou gol exceto noite ou tarde'))
    assert 'JOIN' in query and query.count('UNION') == 2 and 'EXCEPT' in query
    assert params == ['latam', 'gol', 'noite', 'tarde']
    query, params = repository.build_query(parse_query('voos'))
    assert 'UNION' not in query and 'EXCEPT' not in query and params == []
    with pytest.raises(KeyError):
        repository.build_query({'include': [[{'field': 'company; DROP TABLE cidades', 'value': 'latam'}]], 'exclude': []})


@pytest.mark.parametrize('failure', [psycopg.OperationalError('SECRET'), psycopg.ProgrammingError('SECRET')])
def test_connection_errors_are_typed(monkeypatch, failure):
    monkeypatch.setattr(psycopg, 'connect', Mock(side_effect=failure))
    with pytest.raises(repository.DatabaseUnavailable):
        repository.search(parse_query('voos'), 'invalid')


def test_test_database_guard(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://reader@localhost/skyfetch')
    monkeypatch.setenv('SETUP_DATABASE_URL', 'postgresql://owner@localhost/skyfetch')
    monkeypatch.setenv('TEST_DATABASE_URL', 'postgresql://test@127.0.0.1/skyfetch')
    with pytest.raises(SchemaError):
        get_test_url()
    monkeypatch.setenv('DATABASE_URL', 'postgresql://reader@localhost/skyfetch_test')
    monkeypatch.setenv('TEST_DATABASE_URL', 'postgresql://test@127.0.0.1/skyfetch_test')
    with pytest.raises(SchemaError):
        get_test_url()
