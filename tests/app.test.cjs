const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../static/js/app.js'), 'utf8');
const flush = () => new Promise((resolve) => setImmediate(resolve));
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
};

// DOM mínimo para exercitar o código real, eventos e mutações de estado.
class Element {
  constructor(tag = 'div') {
    this.tagName = tag; this.children = []; this.attrs = {}; this.style = {};
    this.events = {}; this.value = ''; this._text = '';
  }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map((child) => child.textContent).join(''); }
  append(...children) { this.children.push(...children); }
  appendChild(child) { this.append(child); }
  replaceChildren(...children) { this.children = children; this._text = ''; }
  setAttribute(key, value) { this.attrs[key] = value; }
  getAttribute(key) { return this.attrs[key] ?? null; }
  addEventListener(event, handler) { this.events[event] = handler; }
  focus() { this.focused = true; }
}

function setup(search = '') {
  const ids = Object.fromEntries(['pesquisa', 'search-input', 'results-list', 'result-count', 'search-summary']
    .map((id) => [id, new Element()]));
  ids['search-input'].value = 'voos latam';
  const chip = new Element('button');
  chip.setAttribute('data-search', 'voos gol exceto noturnos');
  const pending = [];
  const timers = new Map();
  let timerId = 0;
  const window = { location: new URL('http://localhost/' + search), history: {} };
  window.history.replaceState = (_, __, url) => { window.location = new URL(url); };
  const document = {
    getElementById: (id) => ids[id], querySelectorAll: () => [chip],
    createElement: (tag) => new Element(tag), createElementNS: (_, tag) => new Element(tag),
    createTextNode: (text) => { const node = new Element('#text'); node.textContent = text; return node; },
  };
  vm.runInNewContext(source, {
    document, window, URL, URLSearchParams, AbortController,
    setTimeout: (fn) => { const id = ++timerId; timers.set(id, fn); return id; },
    clearTimeout: (id) => timers.delete(id),
    fetch: (url) => { const request = { url, ...deferred() }; pending.push(request); return request.promise; },
  });
  return {
    ids, chip, pending, window, timers, list: ids['results-list'], summary: ids['search-summary'],
    submit(query) { ids['search-input'].value = query; ids.pesquisa.events.submit({ preventDefault() {} }); },
  };
}

function payload(status = 'success', total = 1) {
  const result = { status, query: 'voos', total, isDemoData: true, items: [], interpreted: { include: [], exclude: [] } };
  for (let i = 0; i < total; i++) {
    result.items.push({ id: `server:${i}`, company: 'nova', companyName: 'Companhia do servidor',
      city: 'nova', cityName: `Cidade fornecida pela API ${i}`, shift: 'tarde', shiftName: 'Turno da API' });
  }
  if (!['success', 'no-results'].includes(status)) result.error = { code: 'EXAMPLE', message: 'Complete a frase.' };
  return result;
}

function respond(request, result, http = 200) {
  request.resolve({ status: http, json: async () => result });
}

test('initial loading, server-only cards and URL preserve other parameters', async () => {
  const ui = setup('?other=value#results');
  assert.equal(ui.list.getAttribute('aria-busy'), 'true');
  assert.match(ui.pending[0].url, /^\/api\/search\?q=voos\+latam$/);
  respond(ui.pending[0], payload());
  await flush();
  assert.equal(ui.list.getAttribute('aria-busy'), 'false');
  assert.match(ui.list.textContent, /Cidade fornecida pela API/);
  assert.match(ui.list.textContent, /Companhia do servidor/);
  assert.equal(ui.window.location.searchParams.get('other'), 'value');
  assert.equal(ui.window.location.hash, '#results');
});

test('q empty is respected and URL queries are never silently truncated', async () => {
  const empty = setup('?q=');
  assert.equal(empty.ids['search-input'].value, '');
  respond(empty.pending[0], payload('empty-query', 0), 400);
  await flush();
  assert.match(empty.summary.textContent, /Digite uma frase/);
  const long = 'a'.repeat(151);
  const ui = setup('?q=' + long);
  assert.equal(ui.ids['search-input'].value, long);
  assert.equal(new URL(ui.pending[0].url, 'http://localhost').searchParams.get('q'), long);
});

test('chips and form Enter submit fresh requests, update URL and preserve focus', async () => {
  const ui = setup();
  respond(ui.pending[0], payload()); await flush();
  ui.chip.events.click();
  assert.equal(ui.ids['search-input'].focused, true);
  assert.equal(ui.window.location.searchParams.get('q'), 'voos gol exceto noturnos');
  respond(ui.pending[1], payload()); await flush();
  ui.submit('voos azul');
  assert.equal(ui.list.getAttribute('aria-busy'), 'true');
  assert.equal(ui.window.location.searchParams.get('q'), 'voos azul');
  respond(ui.pending[2], payload()); await flush();
  assert.equal(ui.list.getAttribute('aria-busy'), 'false');
});

for (const [status, http, expected] of [
  ['no-results', 200, /Nenhum resultado/], ['invalid-query', 422, /Complete a frase/],
  ['service-unavailable', 503, /Tente novamente/], ['internal-error', 500, /erro inesperado/],
]) {
  test(`handles ${status} without fake results`, async () => {
    const ui = setup(); respond(ui.pending[0], payload(status, 0), http); await flush();
    assert.match(ui.list.textContent, expected);
    assert.equal(ui.ids['result-count'].textContent, '00');
    assert.equal(ui.list.getAttribute('aria-busy'), 'false');
  });
}

test('network failure and malformed JSON leave retry available', async () => {
  const ui = setup(); ui.pending[0].reject(new Error('offline')); await flush();
  assert.match(ui.summary.textContent, /indisponível/);
  ui.submit('voos');
  ui.pending[1].resolve({ status: 200, json: async () => { throw new SyntaxError('HTML instead of JSON'); } });
  await flush();
  assert.match(ui.list.textContent, /erro inesperado/);
  ui.submit('voos'); respond(ui.pending[2], payload()); await flush();
  assert.match(ui.list.textContent, /Cidade fornecida/);
});

test('old responses and old catch/finally never replace newer UI', async () => {
  const ui = setup(); ui.submit('voos gol');
  respond(ui.pending[1], payload('no-results', 0)); await flush();
  const visible = ui.list.textContent;
  respond(ui.pending[0], payload()); await flush();
  assert.equal(ui.list.textContent, visible);
  ui.submit('latam'); ui.submit('azul');
  ui.pending[2].reject(new Error('late error')); await flush();
  assert.equal(ui.list.getAttribute('aria-busy'), 'true');
  respond(ui.pending[3], payload()); await flush();
  assert.equal(ui.list.getAttribute('aria-busy'), 'false');
});

test('old JSON resolving while a new request loads cannot clear loading', async () => {
  const ui = setup(); const json = deferred();
  ui.pending[0].resolve({ status: 200, json: () => json.promise }); await flush();
  ui.submit('voos gol'); json.resolve(payload()); await flush();
  assert.equal(ui.list.getAttribute('aria-busy'), 'true');
  assert.match(ui.list.textContent, /Buscando/);
  respond(ui.pending[1], payload('no-results', 0)); await flush();
  assert.match(ui.list.textContent, /Nenhum resultado/);
});

test('untrusted values are rendered as text and inconsistent payloads are rejected', async () => {
  const ui = setup(); const result = payload(); result.items[0].cityName = '<img src=x onerror=alert(1)>';
  respond(ui.pending[0], result); await flush();
  assert.match(ui.list.textContent, /<img src=x/);
  ui.submit('voos'); respond(ui.pending[1], { ...payload(), total: 99 }); await flush();
  assert.match(ui.list.textContent, /erro inesperado/);
});

test('duplicate URL queries are rejected without fetching or rewriting the address', async () => {
  for (const query of ['?q=latam&q=gol', '?q=&q=latam']) {
    const ui = setup(query);
    await flush();
    assert.equal(ui.pending.length, 0);
    assert.equal(ui.window.location.search, query);
    assert.match(ui.list.textContent, /apenas uma vez/);
    assert.equal(ui.list.getAttribute('aria-busy'), 'false');
    ui.submit('voos'); respond(ui.pending[0], payload()); await flush();
    assert.equal(ui.window.location.searchParams.getAll('q').length, 1);
    assert.match(ui.list.textContent, /Cidade fornecida/);
  }
});

test('deadline ends stalled fetch and stalled JSON and allows retry', async () => {
  for (const jsonStalled of [false, true]) {
    const ui = setup();
    if (jsonStalled) {
      ui.pending[0].resolve({ status: 200, json: () => new Promise(() => {}) });
      await flush();
    }
    [...ui.timers.values()][0](); await flush();
    assert.equal(ui.list.getAttribute('aria-busy'), 'false');
    assert.match(ui.list.textContent, /Tente novamente/);
    assert.equal(ui.timers.size, 0);
    ui.submit('gol'); respond(ui.pending[1], payload()); await flush();
    assert.match(ui.list.textContent, /Cidade fornecida/);
    assert.equal(ui.timers.size, 0);
  }
});

test('old deadline never clears loading of a newer request', async () => {
  const ui = setup();
  const expire = [...ui.timers.values()][0];
  ui.submit('voos gol'); expire(); await flush();
  assert.equal(ui.list.getAttribute('aria-busy'), 'true');
  respond(ui.pending[1], payload()); await flush();
  assert.equal(ui.list.getAttribute('aria-busy'), 'false');
  assert.equal(ui.timers.size, 0);
});
