/* Interface: somente DOM seguro, sem inserir texto da busca como HTML. */
(function () {
  'use strict';
  const form = document.getElementById('pesquisa');
  const input = document.getElementById('search-input');
  const list = document.getElementById('results-list');
  const count = document.getElementById('result-count');
  const summary = document.getElementById('search-summary');
  if (!form || !input || !list || !count || !summary) return;
  let requestVersion = 0;

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

  function validPayload(response, result) {
    const http = {
      success: [200], 'no-results': [200], 'empty-query': [400],
      'invalid-query': [400, 422], 'service-unavailable': [503], 'internal-error': [500],
    };
    if (!result || !http[result.status]?.includes(response.status) ||
        typeof result.query !== 'string' || result.isDemoData !== true ||
        !Array.isArray(result.items) || !Number.isInteger(result.total) || result.total !== result.items.length) return false;
    if (result.status === 'success') {
      return result.total > 0 && result.items.every((item) => item &&
        ['id', 'company', 'companyName', 'city', 'cityName', 'shift', 'shiftName']
          .every((key) => typeof item[key] === 'string' && item[key].length > 0));
    }
    if (result.status === 'no-results') return result.total === 0;
    return result.total === 0 && typeof result.error?.message === 'string';
  }

  function showResult(result, query) {
    count.textContent = String(result.total).padStart(2, '0');
    if (result.status === 'empty-query') {
      summary.textContent = 'Digite uma frase para começar.';
      showMessage('O que vamos procurar?', 'Experimente “voos latam”, “voos gol” ou uma das sugestões acima.');
    } else if (result.status === 'invalid-query') {
      summary.textContent = 'Não conseguimos interpretar essa pesquisa.';
      showMessage('Tente outra frase', result.error.message);
    } else if (result.status === 'no-results') {
      summary.textContent = `Busca: “${query.trim()}”`;
      showMessage('Nenhum resultado encontrado', 'Não existe combinação correspondente nos dados de exemplo. Tente mudar a companhia, cidade ou turno.');
    } else if (result.status === 'success') {
      summary.textContent = `${result.total} ${result.total === 1 ? 'combinação encontrada' : 'combinações encontradas'} para “${query.trim()}”.`;
      result.items.forEach((flight, index) => list.appendChild(makeResult(flight, index)));
    } else if (result.status === 'service-unavailable') {
      summary.textContent = 'Serviço temporariamente indisponível.';
      showMessage('Tente novamente', 'Confira sua conexão e envie a pesquisa novamente pelo botão Buscar.');
    } else {
      summary.textContent = 'Não foi possível concluir a pesquisa.';
      showMessage('Tente novamente', 'Ocorreu um erro inesperado. Envie a pesquisa novamente pelo botão Buscar.');
    }
  }

  async function render(query, initialParams = null) {
    const version = ++requestVersion;
    list.replaceChildren();
    count.textContent = '00';
    summary.textContent = 'Buscando combinações nos dados do exercício…';
    list.setAttribute('aria-busy', 'true');
    showMessage('Buscando…', 'Aguarde enquanto consultamos os dados.');
    let responseReceived = false;
    const controller = new AbortController();
    let timer;
    try {
      if (initialParams && initialParams.getAll('q').length > 1) {
        list.replaceChildren();
        showResult({ status: 'invalid-query', total: 0,
          error: { message: 'Informe o parâmetro q apenas uma vez.' } }, query);
        return;
      }
      const url = new URL(window.location.href);
      url.searchParams.set('q', query);
      window.history.replaceState(null, '', url);
      // Um prazo cobre tanto a conexão quanto a leitura do JSON.
      const deadline = new Promise((_, reject) => {
        timer = setTimeout(() => {
          controller.abort();
          reject(new Error('Tempo de espera esgotado'));
        }, 15000);
      });
      const response = await Promise.race([
        fetch('/api/search?' + new URLSearchParams({ q: query }), { signal: controller.signal }), deadline,
      ]);
      if (version !== requestVersion) return;
      responseReceived = true;
      const result = await Promise.race([response.json(), deadline]);
      if (version !== requestVersion) return;
      if (!validPayload(response, result)) throw new Error('Resposta inesperada da API');
      list.replaceChildren();
      showResult(result, query);
    } catch (error) {
      if (version !== requestVersion) return;
      list.replaceChildren();
      summary.textContent = responseReceived ? 'Não foi possível concluir a pesquisa.' : 'Serviço temporariamente indisponível.';
      showMessage('Tente novamente', responseReceived
        ? 'Ocorreu um erro inesperado. Envie a pesquisa novamente pelo botão Buscar.'
        : 'Confira sua conexão e envie a pesquisa novamente pelo botão Buscar.');
    } finally {
      clearTimeout(timer);
      if (version === requestVersion) list.setAttribute('aria-busy', 'false');
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

  const initialParams = new URLSearchParams(window.location.search);
  const urlQuery = initialParams.get('q');
  if (urlQuery !== null) input.value = urlQuery;
  render(input.value, initialParams);
})();
