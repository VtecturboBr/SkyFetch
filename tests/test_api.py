from unittest.mock import Mock

import psycopg
import pytest

from app import app
from skyfetch import repository


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://user:SECRET@localhost/skyfetch')
    with app.test_client() as client:
        yield client


def test_success_and_display_names(client, monkeypatch):
    search = Mock(return_value=[('latam', 'bel', 'manha')])
    monkeypatch.setattr(repository, 'search', search)
    response = client.get('/api/search', query_string={'q': 'voos latam e manhã'})
    body = response.json
    assert response.status_code == 200
    assert body['status'] == 'success' and body['total'] == len(body['items']) == 1
    assert body['items'][0] == {'id': 'latam:bel:manha', 'company': 'latam', 'companyName': 'LATAM',
                                'city': 'bel', 'cityName': 'Belém', 'shift': 'manha', 'shiftName': 'Manhã'}
    assert body['isDemoData'] and 'interpreted' in body and 'error' not in body
    search.assert_called_once()


@pytest.mark.parametrize('url,http,status', [
    ('/api/search', 400, 'empty-query'), ('/api/search?q=', 400, 'empty-query'),
    ('/api/search?q=latam&q=gol', 422, 'invalid-query'),
    ('/api/search?q=latam+ou', 422, 'invalid-query'),
    ('/api/search?q=latam+xyz', 422, 'invalid-query'),
    ('/api/search?q=' + 'a' * 151, 400, 'invalid-query'),
])
def test_invalid_never_calls_database(client, monkeypatch, url, http, status):
    search = Mock(side_effect=AssertionError('Não acessar banco para entrada inválida'))
    monkeypatch.setattr(repository, 'search', search)
    response = client.get(url)
    assert response.status_code == http
    assert response.json['status'] == status
    assert response.json['total'] == 0 and response.json['items'] == [] and response.json['isDemoData']
    assert 'error' in response.json and 'interpreted' not in response.json
    search.assert_not_called()


def test_no_results(client, monkeypatch):
    monkeypatch.setattr(repository, 'search', lambda *_: [])
    response = client.get('/api/search?q=latam+manaus')
    assert response.status_code == 200 and response.json['status'] == 'no-results'
    assert response.json['total'] == 0 and response.json['items'] == []
    assert 'interpreted' in response.json


@pytest.mark.parametrize('failure,http,status', [
    (repository.DatabaseUnavailable('SECRET DSN'), 503, 'service-unavailable'),
    (psycopg.errors.UndefinedTable('SECRET SQL'), 500, 'internal-error'),
    (RuntimeError('SECRET traceback'), 500, 'internal-error'),
])
def test_failures_are_safe(client, monkeypatch, caplog, failure, http, status):
    monkeypatch.setattr(repository, 'search', Mock(side_effect=failure))
    response = client.get('/api/search?q=voos')
    assert response.status_code == http and response.json['status'] == status
    assert response.json['items'] == [] and response.json['total'] == 0
    assert 'SECRET' not in response.text and 'SECRET' not in caplog.text


def test_page_works_without_database(client, monkeypatch):
    monkeypatch.delenv('DATABASE_URL')
    assert client.get('/').status_code == 200
    assert client.get('/api/search?q=voos').status_code == 503


def test_fallback_names_use_codes(client, monkeypatch):
    monkeypatch.setattr(repository, 'search', lambda *_: [('nova', 'cidade nova', 'manha')])
    item = client.get('/api/search?q=voos').json['items'][0]
    assert item['companyName'] == 'nova' and item['cityName'] == 'cidade nova'


def test_read_only_endpoint_and_debug_default(client):
    assert client.post('/api/search').status_code == 405
    assert not app.debug
