"""SkyFetch PRJ.9: busca didática com Flask e PostgreSQL."""

import os

from flask import Flask, jsonify, render_template, request

from skyfetch import repository
from skyfetch.parser import QueryError, parse_query

app = Flask(__name__)


@app.get("/")
def index():
    """A página continua disponível mesmo sem conexão com o banco."""
    return render_template("index.html")


NAMES = {
    "company": {"latam": "LATAM", "gol": "GOL", "azul": "Azul"},
    "city": {"sjc": "São José dos Campos", "bel": "Belém", "campinas": "Campinas",
             "manaus": "Manaus", "salvador": "Salvador", "porto alegre": "Porto Alegre", "sao paulo": "São Paulo"},
    "shift": {"manha": "Manhã", "tarde": "Tarde", "noite": "Noite"},
}


@app.get("/api/search")
def search():
    values = request.args.getlist("q")
    query = values[0] if values else ""
    payload = {"query": query, "total": 0, "items": [], "isDemoData": True}

    def error(status, code, message, http_status):
        return jsonify(**payload, status=status, error={"code": code, "message": message}), http_status

    try:
        if len(values) > 1:
            raise QueryError("UNSUPPORTED_SYNTAX", "Informe o parâmetro q apenas uma vez.")
        interpreted = parse_query(query)
        rows = repository.search(interpreted, os.environ.get("DATABASE_URL"))
        items = []
        for company, city, shift in rows:
            item = {"id": f"{company}:{city}:{shift}", "company": company, "city": city, "shift": shift}
            for field in NAMES:
                item[field + "Name"] = NAMES[field].get(item[field], item[field])
            items.append(item)
        payload.update(items=items, total=len(items))
        return jsonify(**payload, status="success" if items else "no-results", interpreted=interpreted)
    except QueryError as exc:
        return error("empty-query" if exc.code == "EMPTY_QUERY" else "invalid-query",
                     exc.code, exc.message, exc.http_status)
    except repository.DatabaseUnavailable:
        app.logger.warning("Banco indisponível. Confira configuração local e disponibilidade do PostgreSQL.")
        return error("service-unavailable", "DATABASE_UNAVAILABLE", "Serviço temporariamente indisponível. Tente novamente.", 503)
    except Exception as exc:
        # Não registrar mensagens brutas de exceções: podem conter DSN e senhas.
        app.logger.error("Falha interna (%s). Confira o schema com scripts/setup_database.py.", type(exc).__name__)
        return error("internal-error", "INTERNAL_ERROR", "Não foi possível concluir a pesquisa. Tente novamente.", 500)


if __name__ == "__main__":
    app.run(debug=os.environ.get("SKYFETCH_DEBUG") == "1")
