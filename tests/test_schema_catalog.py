from unittest.mock import Mock

import pytest

from scripts.setup_database import SchemaError, validate_schema


def catalog(not_null_valid=True, missing_check=False):
    connection = Mock()
    results = []
    for oid, table, columns in [(1, 'companhia_aerea', ['companhia', 'cidade']), (2, 'cidades', ['cidade', 'turno'])]:
        checks = [(f'CHECK (length(btrim({columns[0]})) > 0)', True, 'c')]
        checks += [("CHECK (turno = ANY (ARRAY['manha'::text,'tarde'::text,'noite'::text])))", True, 'c')] if table == 'cidades' else [('CHECK (length(btrim(cidade)) > 0)', True, 'c')]
        if missing_check: checks = checks[1:]
        checks += [(f'PRIMARY KEY ({", ".join(columns)})', True, 'p')]
        checks += [(f'NOT NULL {col}', not_null_valid, 'n') for col in columns]
        results += [Mock(fetchone=Mock(return_value=(oid, 'r'))),
                    Mock(fetchall=Mock(return_value=[(col, 'text', True) for col in columns])),
                    Mock(fetchall=Mock(return_value=checks))]
    connection.execute.side_effect = results
    return connection


def test_postgres18_not_null_entries_do_not_invalidate_schema():
    validate_schema(catalog())


@pytest.mark.parametrize('kwargs', [{'not_null_valid': False}, {'missing_check': True}])
def test_postgres18_projection_still_rejects_invalid_constraints(kwargs):
    with pytest.raises(SchemaError):
        validate_schema(catalog(**kwargs))
