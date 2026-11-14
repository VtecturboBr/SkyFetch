"""SQL explícito e parametrizado; uma conexão e uma consulta por busca."""

import psycopg


class DatabaseUnavailable(RuntimeError):
    pass


COLUMNS = {"company": "company", "city": "city", "shift": "shift"}
BASE = """SELECT a.companhia AS company, a.cidade AS city, c.turno AS shift
FROM public.companhia_aerea a JOIN public.cidades c ON c.cidade = a.cidade"""
SELECT = "SELECT company, city, shift FROM base"


def build_query(interpreted):
    params = []

    def selection(groups):
        if not groups:
            return SELECT
        queries = []
        for terms in groups:
            conditions = []
            for term in terms:
                # O mapa fixo é a única fonte de identificadores; valores são parâmetros.
                conditions.append(COLUMNS[term["field"]] + " = %s")
                params.append(term["value"])
            if not conditions:
                raise ValueError("Cláusula sem filtros")
            queries.append(SELECT + " WHERE " + " AND ".join(conditions))
        return " UNION ".join(queries)

    included = selection(interpreted["include"])
    query = f"WITH base AS ({BASE}), included AS ({included})"
    if interpreted["exclude"]:
        excluded = selection(interpreted["exclude"])
        query += f", excluded AS ({excluded})"
        result = "SELECT company, city, shift FROM included EXCEPT SELECT company, city, shift FROM excluded"
    else:
        result = "SELECT company, city, shift FROM included"
    return query + " " + result + " ORDER BY company, city, shift", params


def search(interpreted, database_url):
    if not database_url:
        raise DatabaseUnavailable("DATABASE_URL não configurada")
    query, params = build_query(interpreted)
    # Erro na abertura (inclusive DSN inválida) é diferente de schema/SQL inválido.
    try:
        connection = psycopg.connect(database_url, connect_timeout=3,
                                     options="-c statement_timeout=3000 -c default_transaction_read_only=on")
    except (psycopg.Error, ValueError) as exc:
        raise DatabaseUnavailable("Conexão indisponível") from exc
    try:
        with connection:
            return connection.execute(query, params).fetchall()
    except (psycopg.OperationalError, psycopg.InterfaceError) as exc:
        raise DatabaseUnavailable("Banco indisponível ou consulta expirou") from exc
