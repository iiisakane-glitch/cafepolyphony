// Integration checks for translations and accessible mobile navigation.
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const root = new URL('../', import.meta.url);
const source = readFileSync(new URL('js/site.js', root), 'utf8');
const html = readFileSync(new URL('index.html', root), 'utf8');
const keys = [...new Set([...html.matchAll(/data-i18n="([^"]+)"/g)].map(match => match[1]))];

function element(dataset = {}) {
  return {
    dataset, hidden: false, innerHTML: '', textContent: '', attributes: {}, events: {},
    classList: { values: new Set(), add(value) { this.values.add(value); } },
    setAttribute(name, value) { this.attributes[name] = value; },
    addEventListener(name, handler) { this.events[name] = handler; },
    focus() { this.focused = true; }
  };
}

function render(language) {
  const translated = keys.map(i18n => element({ i18n }));
  const nodes = Object.fromEntries(['language-select', 'mobile-nav', 'toggle'].map(id => [id, element()]));
  const document = {
    documentElement: {}, events: {},
    getElementById(id) { return nodes[id]; },
    querySelector(selector) {
      assert.equal(selector, '.menu-toggle');
      return nodes.toggle;
    },
    querySelectorAll(selector) {
      if (selector === '[data-i18n]') return translated;
      throw new Error(`Unexpected selector: ${selector}`);
    },
    addEventListener(name, handler) { this.events[name] = handler; }
  };
  vm.runInNewContext(source, {
    document, URL, URLSearchParams,
    location: { search: `?lang=${language}`, href: `https://example.test/?lang=${language}`, assign(value) { this.assigned = value; } },
    window: { matchMedia() { return { addEventListener() {} }; } }
  });
  return { document, nodes, translated };
}

for (const language of ['ja', 'en', 'zh-CN', 'zh-TW', 'ko']) {
    const result = render(language);
    assert.equal(result.document.documentElement.lang, language);
    if (language !== 'ja') {
      for (const node of result.translated) assert.ok(node.innerHTML, `Missing ${language}: ${node.dataset.i18n}`);
    }
    result.nodes.toggle.events.click();
    assert.equal(result.nodes['mobile-nav'].hidden, false);
    assert.equal(result.nodes.toggle.attributes['aria-expanded'], 'true');
    result.document.events.keydown({ key: 'Escape' });
    assert.equal(result.nodes['mobile-nav'].hidden, true);
    assert.equal(result.nodes.toggle.focused, true);
}
assert.equal(render('unsupported').document.documentElement.lang, 'ja');
console.log('PASS: 5-language translation coverage, mobile menu, Escape focus, invalid-language fallback');
