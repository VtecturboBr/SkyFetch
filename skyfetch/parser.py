"""Gramática restrita: AND/justaposição > OR > exclusão do conjunto completo."""

from dataclasses import dataclass
import re
import unicodedata


class QueryError(ValueError):
    def __init__(self, code, message, http_status=422):
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text.casefold())
                   if not unicodedata.category(c).startswith("M"))


ALIASES = {
    "company": {"latam": "latam", "gol": "gol", "azul": "azul"},
    "city": {"sao jose dos campos": "sjc", "sjc": "sjc", "belem": "bel", "bel": "bel",
             "campinas": "campinas", "manaus": "manaus", "salvador": "salvador",
             "porto alegre": "porto alegre", "sao paulo": "sao paulo"},
    "shift": {"manha": "manha", "matutino": "manha", "matutinos": "manha",
              "tarde": "tarde", "vespertino": "tarde", "vespertinos": "tarde",
              "noite": "noite", "noturno": "noite", "noturnos": "noite"},
}
PHRASES = sorted(
    [(tuple(alias.split()), {"field": field, "value": value})
     for field, aliases in ALIASES.items() for alias, value in aliases.items()],
    key=lambda item: len(item[0]), reverse=True,
)
LINKS = {"de", "da", "do", "em", "para"}
OPERATORS = {"e", "ou", "exceto"}


@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    position: int


def tokenize(query):
    words = [(normalize(m.group()), m.start()) for m in re.finditer(r"\S+", query)]
    tokens = []
    i = 0
    while i < len(words):
        word, position = words[i]
        for phrase, term in PHRASES:
            if tuple(w for w, _ in words[i:i + len(phrase)]) == phrase:
                tokens.append(Token("term", term.copy(), position))
                i += len(phrase)
                break
        else:
            if word in {"voo", "voos"}:
                kind = "intro"
            elif word in OPERATORS:
                kind = word
            elif word in LINKS:
                kind = "link"
            else:
                raise QueryError("UNKNOWN_TERM", f"Termo não reconhecido na posição {position + 1}: '{word}'. Use uma companhia, cidade ou turno do exercício.")
            tokens.append(Token(kind, word, position))
            i += 1
    return tokens


def parse_query(query):
    if not isinstance(query, str):
        raise QueryError("UNSUPPORTED_SYNTAX", "A pesquisa deve ser um texto.")
    if len(query) > 150:
        raise QueryError("QUERY_TOO_LONG", "Use no máximo 150 caracteres.", 400)
    # Validar antes de strip/normalizar: controles e pontuação não podem desaparecer.
    if any(not (unicodedata.category(c)[0] in "LM" or
                (c.isspace() and unicodedata.category(c)[0] != "C")) for c in query):
        raise QueryError("UNSUPPORTED_SYNTAX", "Use apenas palavras e espaços, sem pontuação ou caracteres de controle.")
    if not query.strip():
        raise QueryError("EMPTY_QUERY", "Digite uma frase para pesquisar.", 400)
    tokens = tokenize(query)
    index = 0
    filters = clauses = 0
    interpreted = {"include": [], "exclude": []}

    def missing(previous):
        if previous in OPERATORS:
            raise QueryError("INCOMPLETE_OPERATOR", f"Complete a pesquisa após '{previous}'.")
        raise QueryError("UNSUPPORTED_SYNTAX", "Uma palavra de ligação precisa ser seguida por um termo válido.")

    def expression():
        nonlocal index, filters, clauses
        groups = [[]]
        clauses += 1
        while True:
            if clauses > 8:
                raise QueryError("UNSUPPORTED_SYNTAX", "Use no máximo 8 cláusulas de pesquisa, incluindo exclusões.")
            if index >= len(tokens) or tokens[index].kind != "term":
                raise QueryError("UNSUPPORTED_SYNTAX", "Esperávamos uma companhia, cidade ou turno após o operador.")
            groups[-1].append(tokens[index].value)
            index += 1
            filters += 1
            if filters > 12:
                raise QueryError("UNSUPPORTED_SYNTAX", "Use no máximo 12 filtros, incluindo exclusões.")
            if index == len(tokens) or tokens[index].kind == "exceto":
                return groups
            token = tokens[index]
            if token.kind == "term":
                continue
            if token.kind not in {"e", "ou", "link"}:
                raise QueryError("UNSUPPORTED_SYNTAX", "A introdução 'voos' só pode aparecer uma vez, no início.")
            index += 1
            if index == len(tokens):
                missing(token.value)
            if token.kind == "ou":
                groups.append([])
                clauses += 1

    if tokens[0].kind == "intro":
        index = 1
        if index == len(tokens):
            return interpreted
        if tokens[index].kind == "link":
            link = tokens[index]
            index += 1
            if index == len(tokens):
                missing(link.value)
            if tokens[index].kind != "term":
                raise QueryError("UNSUPPORTED_SYNTAX", "Após a ligação inicial, informe um termo válido.")
    if tokens[index].kind != "exceto":
        interpreted["include"] = expression()
    if index < len(tokens) and tokens[index].kind == "exceto":
        index += 1
        if index == len(tokens):
            missing("exceto")
        interpreted["exclude"] = expression()
    if index != len(tokens):
        raise QueryError("UNSUPPORTED_SYNTAX", "Use no máximo um 'exceto' por pesquisa.")
    return interpreted
