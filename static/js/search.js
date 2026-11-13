/**
 * Motor DEMONSTRATIVO de pesquisa, executado no navegador.
 * Usa somente as duas tabelas do enunciado PRJ.9, NÃO um serviço de voos real.
 * A versão final substituirá os dados locais por consultas ao PostgreSQL no Flask.
 */
(function (root) {
  'use strict';

  const AIRLINES = [
    { company: 'latam', city: 'sjc' },
    { company: 'latam', city: 'bel' },
    { company: 'gol', city: 'bel' },
    { company: 'azul', city: 'campinas' },
  ];

  const CITIES = [
    { city: 'sjc', shift: 'tarde' },
    { city: 'sjc', shift: 'noite' },
    { city: 'bel', shift: 'manha' },
    { city: 'campinas', shift: 'noite' },
  ];

  const CITY_NAMES = { sjc: 'São José dos Campos', bel: 'Belém', campinas: 'Campinas' };
  const COMPANY_NAMES = { latam: 'LATAM', gol: 'GOL', azul: 'Azul' };
  const SHIFT_NAMES = { manha: 'Manhã', tarde: 'Tarde', noite: 'Noite' };

  // Junta as tabelas por cidade, exatamente como um JOIN da atividade.
  const FLIGHTS = AIRLINES.flatMap((airline) =>
    CITIES.filter((item) => item.city === airline.city).map((item) => ({
      id: `${airline.company}-${item.city}-${item.shift}`,
      company: airline.company,
      companyName: COMPANY_NAMES[airline.company],
      city: item.city,
      cityName: CITY_NAMES[item.city],
      shift: item.shift,
      shiftName: SHIFT_NAMES[item.shift],
    }))
  );

  function normalize(text) {
    return String(text).normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .toLowerCase().replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
  }

  const ALIASES = [
    { patterns: ['sao jose dos campos', 'sjc'], field: 'city', value: 'sjc' },
    { patterns: ['campinas'], field: 'city', value: 'campinas' },
    { patterns: ['belem', 'bel'], field: 'city', value: 'bel' },
    { patterns: ['latam'], field: 'company', value: 'latam' },
    { patterns: ['gol'], field: 'company', value: 'gol' },
    { patterns: ['azul'], field: 'company', value: 'azul' },
    { patterns: ['matutino', 'matutinos', 'manha'], field: 'shift', value: 'manha' },
    { patterns: ['vespertino', 'vespertinos', 'tarde'], field: 'shift', value: 'tarde' },
    { patterns: ['noturnos', 'noturno', 'noite'], field: 'shift', value: 'noite' },
  ];

  function containsPhrase(text, phrase) {
    return (` ${text} `).includes(` ${phrase} `);
  }

  function getFilters(clause) {
    const normalized = normalize(clause);
    const result = [];
    for (const item of ALIASES) {
      if (item.patterns.some((phrase) => containsPhrase(normalized, phrase))) {
        result.push({ field: item.field, value: item.value });
      }
    }
    return result;
  }

  // Em cada bloco separado por 'ou', todos os filtros devem coincidir (AND).
  // 'exceto' remove do resultado da busca principal os registros da busca negativa.
  function parseClauses(text) {
    return text.split(/\bou\b/).map(getFilters).filter((terms) => terms.length > 0);
  }

  function matches(flight, clauses) {
    return clauses.some((terms) => terms.every((term) => flight[term.field] === term.value));
  }

  function searchFlights(query) {
    const normalized = normalize(query);
    if (!normalized) return { status: 'empty-query', flights: [], query: '' };

    const marker = /(?:^| )exceto(?: |$)/.exec(normalized);
    const exceptIndex = marker ? marker.index : -1;
    const hasLeadingExcept = normalized.startsWith('exceto');
    const positiveText = hasLeadingExcept ? '' : exceptIndex < 0 ? normalized : normalized.slice(0, exceptIndex);
    const negativeText = hasLeadingExcept ? normalized.slice('exceto'.length).trim() : exceptIndex < 0 ? '' : normalized.slice(exceptIndex + marker[0].length).trim();
    const positive = parseClauses(positiveText);
    const negative = parseClauses(negativeText);

    if (!positive.length && !negative.length) return { status: 'unrecognized', flights: [], query };
    if ((exceptIndex >= 0 || hasLeadingExcept) && !negative.length) {
      return { status: 'unrecognized', flights: [], query };
    }

    const flights = FLIGHTS.filter((flight) =>
      (positive.length === 0 || matches(flight, positive)) &&
      (negative.length === 0 || !matches(flight, negative))
    );
    return { status: flights.length ? 'success' : 'no-results', flights, query };
  }

  const api = { searchFlights, normalize, getFilters, FLIGHTS };
  root.SkyFetchSearch = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(globalThis);
