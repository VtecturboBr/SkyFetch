# SkyFetch ✈

**SkyFetch** é um protótipo de buscador de voos em linguagem natural para o trabalho **PRJ.9**. A proposta é usar **Python, Flask e PostgreSQL** para pesquisar companhias, cidades e turnos com frases simples.

## Estado atual

A **primeira etapa (frontend)** está pronta: uma página Flask responsiva, com campo de pesquisa, exemplos clicáveis e resultados interativos.

> **Importante:** as buscas atuais são demonstrativas e acontecem no navegador com os dados fictícios do enunciado. **O PostgreSQL ainda não está conectado**. Não há dados reais de voos ou horários de partidas.

## Executando no computador

É necessário ter Python 3.10 ou superior instalado.

```bash
python -m venv .venv
```

Ative o ambiente virtual:

- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **Linux/macOS:** `source .venv/bin/activate`

Depois:

```bash
pip install -r requirements.txt
python app.py
```

Abra **http://127.0.0.1:5000** no navegador.

## Pesquisas de exemplo

- `voos latam`
- `voos latam e manhã`
- `voos latam ou azul`
- `voos gol exceto noturnos`
- `voos São José dos Campos`

A versão demonstrativa entende os nomes/abreviações de companhias, cidades e turnos presentes nas tabelas da atividade, além de `e` (interseção), `ou` (união) e `exceto` (diferença). Outras palavras da frase podem ser ignoradas. Não é um interpretador de linguagem natural completo.

## Estrutura

```text
SkyFetch/
├── app.py                    # servidor Flask
├── requirements.txt          # dependência Python
├── templates/
│   └── index.html            # página do buscador
├── static/
│   ├── css/style.css         # layout responsivo
│   ├── js/app.js             # interação com o DOM
│   ├── js/search.js          # mecanismo demonstrativo local
│   └── favicon.svg
└── tests/
    └── search.test.cjs       # testes do interpretador de exemplo
```

## Testes

Com Node.js instalado:

```bash
node --test tests/search.test.cjs
```

## Próximas etapas

1. Criar as tabelas `COMPANHIA_AEREA` e `CIDADES` no PostgreSQL e cadastrar as linhas do enunciado.
2. Criar rota Flask `/api/search` com queries parametrizadas.
3. Migrar as operações de JOIN, UNION e EXCEPT para o PostgreSQL.
4. Fazer o frontend consumir a API e acrescentar testes de integração.

**Nota de modelagem:** as tabelas do enunciado permitem combinar companhias/cidades com cidade/turno por `JOIN`, mas não comprovam que uma companhia realmente voa em cada turno associado à cidade.
