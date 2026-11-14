import pytest

from skyfetch.parser import QueryError, parse_query


@pytest.mark.parametrize('query,field,value', [
    ('voos LATAM', 'company', 'latam'), ('voos São José dos Campos', 'city', 'sjc'),
    ('voos SA\u0303O JOSE\u0301 DOS CAMPOS', 'city', 'sjc'), ('voos Belém', 'city', 'bel'),
    ('voos matutinos', 'shift', 'manha'), ('vespertino', 'shift', 'tarde'),
    ('noturnos', 'shift', 'noite'), ('voo Porto Alegre', 'city', 'porto alegre'),
    ('São Paulo', 'city', 'sao paulo'), ('Manaus', 'city', 'manaus'), ('Salvador', 'city', 'salvador'),
])
def test_aliases(query, field, value):
    assert parse_query(query) == {'include': [[{'field': field, 'value': value}]], 'exclude': []}


def test_precedence_and_links():
    result = parse_query('voos da latam em Belém ou gol exceto noite ou tarde')
    assert result['include'] == [
        [{'field': 'company', 'value': 'latam'}, {'field': 'city', 'value': 'bel'}],
        [{'field': 'company', 'value': 'gol'}],
    ]
    assert result['exclude'] == [[{'field': 'shift', 'value': 'noite'}], [{'field': 'shift', 'value': 'tarde'}]]
    assert parse_query('latam manhã') == parse_query('latam e manhã')
    assert parse_query('voos') == {'include': [], 'exclude': []}
    assert parse_query('exceto noite')['include'] == []


@pytest.mark.parametrize('query,code,http', [
    ('', 'EMPTY_QUERY', 400), ('   ', 'EMPTY_QUERY', 400),
    ('a' * 151, 'QUERY_TOO_LONG', 400), ('voos latam xyz', 'UNKNOWN_TERM', 422),
    ('voos avião espacial', 'UNKNOWN_TERM', 422),
    ('voos latam ou', 'INCOMPLETE_OPERATOR', 422), ('voos latam e', 'INCOMPLETE_OPERATOR', 422),
    ('voos latam exceto', 'INCOMPLETE_OPERATOR', 422),
    ('voos latam de', 'UNSUPPORTED_SYNTAX', 422), ('voos da', 'UNSUPPORTED_SYNTAX', 422),
    ('voos voos latam', 'UNSUPPORTED_SYNTAX', 422),
    ('latam exceto noite exceto tarde', 'UNSUPPORTED_SYNTAX', 422),
    ('latam; DROP TABLE cidades', 'UNSUPPORTED_SYNTAX', 422),
    ("latam' OR 1=1 --", 'UNSUPPORTED_SYNTAX', 422),
    ('<script>alert</script>', 'UNSUPPORTED_SYNTAX', 422),
    ('latam\n', 'UNSUPPORTED_SYNTAX', 422), ('latam\tgol', 'UNSUPPORTED_SYNTAX', 422),
    ('latam\u200bgol', 'UNSUPPORTED_SYNTAX', 422), ('(latam)', 'UNSUPPORTED_SYNTAX', 422),
    ('de', 'UNSUPPORTED_SYNTAX', 422), ('da latam', 'UNSUPPORTED_SYNTAX', 422),
    ('latam de em Belém', 'UNSUPPORTED_SYNTAX', 422), ('latam ou da gol', 'UNSUPPORTED_SYNTAX', 422),
    ('exceto de noite', 'UNSUPPORTED_SYNTAX', 422), ('voos de exceto noite', 'UNSUPPORTED_SYNTAX', 422),
    ('latam ou ou gol', 'UNSUPPORTED_SYNTAX', 422), ('e latam', 'UNSUPPORTED_SYNTAX', 422),
])
def test_rejects_whole_input(query, code, http):
    with pytest.raises(QueryError) as caught:
        parse_query(query)
    assert (caught.value.code, caught.value.http_status) == (code, http)


def test_limits_include_exclusion():
    assert len(parse_query(' '.join(['gol'] * 12))['include'][0]) == 12
    for query in [' '.join(['gol'] * 13), ' ou '.join(['gol'] * 9),
                  ' '.join(['gol'] * 12) + ' exceto noite', ' ou '.join(['gol'] * 8) + ' exceto noite']:
        with pytest.raises(QueryError):
            parse_query(query)


def test_length_is_checked_before_normalizing():
    assert parse_query(' ' * 147 + 'gol')['include']
    with pytest.raises(QueryError) as caught:
        parse_query(' ' * 148 + 'gol')
    assert caught.value.code == 'QUERY_TOO_LONG'
