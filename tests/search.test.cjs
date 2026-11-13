const test = require('node:test');
const assert = require('node:assert/strict');
const { searchFlights, FLIGHTS } = require('../static/js/search.js');

test('as duas tabelas geram 5 combinações', () => {
  assert.equal(FLIGHTS.length, 5);
});

test('consulta por companhia LATAM', () => {
  const result = searchFlights('voos LATAM');
  assert.equal(result.status, 'success');
  assert.equal(result.flights.length, 3);
});

test('combinação por e: companhia e turno', () => {
  const result = searchFlights('voos latam e manhã');
  assert.equal(result.flights.length, 1);
  assert.equal(result.flights[0].city, 'bel');
});

test('combinação por ou: união sem duplicação', () => {
  const result = searchFlights('voos latam ou azul');
  assert.equal(result.flights.length, 4);
  assert.equal(new Set(result.flights.map((flight) => flight.id)).size, 4);
});

test('exceto remove resultados noturnos', () => {
  const result = searchFlights('voos latam exceto noturnos');
  assert.equal(result.flights.length, 2);
  assert.ok(result.flights.every((flight) => flight.shift !== 'noite'));
});

test('reconhece acentos e nomes de cidade', () => {
  assert.equal(searchFlights('voos Belém').flights.length, 2);
  assert.equal(searchFlights('voos São José dos Campos').flights.length, 2);
});

test('busca sem correspondência mostra estado vazio', () => {
  assert.equal(searchFlights('voos latam e campinas').status, 'no-results');
});

test('busca sem filtros reconhecidos pede outra frase', () => {
  assert.equal(searchFlights('aeroporto internacional').status, 'unrecognized');
  assert.equal(searchFlights('voos latam exceto').status, 'unrecognized');
  assert.equal(searchFlights('').status, 'empty-query');
});
