/* Interface: somente DOM seguro, sem inserir texto da busca como HTML. */
(function () {
  'use strict';
  const form = document.getElementById('pesquisa');
  const input = document.getElementById('search-input');
  const list = document.getElementById('results-list');
  const count = document.getElementById('result-count');
  const summary = document.getElementById('search-summary');
  const engine = globalThis.SkyFetchSearch;
  if (!form || !input || !list || !count || !summary || !engine) return;

  const icon = (path) => {
    const el = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    el.setAttribute('viewBox', '0 0 24 24');
    el.setAttribute('width', '20');
    el.setAttribute('height', '20');
    el.setAttribute('fill', 'none');
    el.setAttribute('stroke', 'currentColor');
    el.setAttribute('stroke-width', '1.8');
    el.setAttribute('stroke-linecap', 'round');
    el.setAttribute('stroke-linejoin', 'round');
    el.setAttribute('aria-hidden', 'true');
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    line.setAttribute('d', path);
    el.appendChild(line);
    return el;
  };

  function makeResult(flight, index) {
    const card = document.createElement('article');
    card.className = 'flight-card';

    const left = document.createElement('div');
    left.className = 'flight-main';
    const avatar = document.createElement('div');
    avatar.className = `company-avatar company-${flight.company}`;
    avatar.textContent = flight.companyName.slice(0, 1);
    avatar.setAttribute('aria-hidden', 'true');
    const details = document.createElement('div');
    details.className = 'flight-details';
    const heading = document.createElement('h3');
    heading.textContent = flight.cityName;
    const sub = document.createElement('p');
    sub.textContent = `${flight.companyName} · ${flight.city.toUpperCase()}`;
    details.append(heading, sub);
    left.append(avatar, details);

    const right = document.createElement('div');
    right.className = 'flight-meta';
    const shiftLabel = document.createElement('span');
    shiftLabel.className = 'meta-label';
    shiftLabel.textContent = 'TURNO';
    const shift = document.createElement('span');
    shift.className = 'shift-value';
    shift.append(icon('M12 3v2m0 14v2M3 12h2m14 0h2M5.6 5.6l1.4 1.4m10 10 1.4 1.4M5.6 18.4 7 17m10-10 1.4-1.4M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z'));
    shift.append(document.createTextNode(flight.shiftName));
    right.append(shiftLabel, shift);

    card.append(left, right);
    card.style.animationDelay = `${Math.min(index, 5) * 40}ms`;
    return card;
  }

  function showMessage(titleText, detailText) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    const visual = document.createElement('span');
    visual.className = 'empty-icon';
    visual.append(icon('M10 3a7 7 0 1 0 0 14 7 7 0 0 0 0-14Zm5.5 12.5L21 21'));
    const title = document.createElement('h3');
    title.textContent = titleText;
    const detail = document.createElement('p');
    detail.textContent = detailText;
    empty.append(visual, title, detail);
    list.appendChild(empty);
  }

  function render(query) {
    const result = engine.searchFlights(query);
    list.replaceChildren();
    count.textContent = String(result.flights.length).padStart(2, '0');
    if (result.status === 'empty-query') {
      summary.textContent = 'Digite uma frase para começar.';
      showMessage('O que vamos procurar?', 'Experimente “voos latam”, “voos gol” ou uma das sugestões acima.');
    } else if (result.status === 'unrecognized') {
      summary.textContent = 'Não conseguimos interpretar essa pesquisa.';
      showMessage('Tente outra frase', 'Use uma companhia (latam, gol, azul), uma cidade ou um turno. Você pode combinar com “e”, “ou” ou “exceto”.');
    } else if (result.status === 'no-results') {
      summary.textContent = `Busca: “${query.trim()}”`;
      showMessage('Nenhum resultado encontrado', 'Não existe combinação correspondente nos dados de exemplo. Tente mudar a companhia, cidade ou turno.');
    } else {
      summary.textContent = `${result.flights.length} ${result.flights.length === 1 ? 'combinação encontrada' : 'combinações encontradas'} para “${query.trim()}”.`;
      result.flights.forEach((flight, index) => list.appendChild(makeResult(flight, index)));
    }
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    render(input.value);
  });

  document.querySelectorAll('[data-search]').forEach((button) => {
    button.addEventListener('click', () => {
      input.value = button.getAttribute('data-search') || '';
      render(input.value);
      input.focus();
    });
  });

  const urlQuery = new URLSearchParams(window.location.search).get('q');
  if (urlQuery) input.value = urlQuery.slice(0, 150);
  render(input.value);
})();
