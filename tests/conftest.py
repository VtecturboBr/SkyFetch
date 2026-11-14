import os

import psycopg
import pytest

from scripts.setup_database import initialize, test_database_url as get_test_url


class RedactedDsn(str):
    def __repr__(self):
        return '<TEST_DATABASE_URL redigida>'


@pytest.fixture(scope='session')
def database_url():
    if not os.environ.get('TEST_DATABASE_URL'):
        pytest.skip('Integração não executada: TEST_DATABASE_URL ausente')
    url = get_test_url()
    with psycopg.connect(url, connect_timeout=3) as connection:
        initialize(connection)
    return RedactedDsn(url)


@pytest.fixture
def connection(database_url):
    with psycopg.connect(database_url, connect_timeout=3) as conn:
        try:
            yield conn
        finally:
            # Todas as alterações de casos extremos são transitórias no banco _test.
            conn.rollback()
