'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

test('dashboard boots, renders demo data, accepts a manual reading and supports alert review', async function () {
  const root = path.join(__dirname, '..');
  const source = fs.readFileSync(path.join(root, 'dashboard', 'app.js'), 'utf8');
  const csv = fs.readFileSync(path.join(root, 'data', 'synthetic', 'demo_telemetry.csv'), 'utf8');
  const lines = csv.trim().split(/\r?\n/);
  const headers = lines[0].split(',');
  const readings = lines.slice(1).map(function (line) {
    const values = line.split(',');
    const reading = {};
    headers.forEach(function (header, index) {
      const value = values[index] || '';
      reading[header] = value;
    });
    if (reading.value !== '') reading.value = Number(reading.value);
    if (reading.mission_day !== '') reading.mission_day = Number(reading.mission_day);
    return reading;
  });
  const report = {
    results: readings.map(function (reading) { return { reading: reading }; }),
    validation_issues: []
  };

  const elements = new Map();
  function getElement(id) {
    if (!elements.has(id)) {
      elements.set(id, {
        id: id,
        value: ({
          'baseline-start': '2026-11-01',
          'baseline-end': '2026-11-07',
          threshold: '2',
          'repeat-count': '2',
          'minimum-samples': '3',
          'metric-filter': 'all',
          'astronaut-filter': 'all',
          'status-filter': 'all'
        })[id] || '',
        innerHTML: '',
        textContent: '',
        className: '',
        handlers: {},
        formData: {},
        attrs: {},
        addEventListener: function (type, callback) {
          this.handlers[type] = callback;
        },
        reset: function () { this.formData = {}; },
        getAttribute: function (name) { return this.attrs[name] || null; }
      });
    }
    return elements.get(id);
  }

  const documentStub = {
    readyHandler: null,
    addEventListener: function (type, callback) {
      if (type === 'DOMContentLoaded') this.readyHandler = callback;
    },
    querySelector: function (selector) {
      return getElement(selector.replace(/^#/, ''));
    }
  };
  const windowStub = { isSecureContext: true };
  const navigatorStub = {
    serviceWorker: {
      register: async function (script) {
        assert.equal(script, '../sw.js');
        return {};
      },
      ready: Promise.resolve({})
    }
  };
  const fetchStub = async function (url) {
    assert.equal(url, '../output/demo-report.json');
    return { ok: true, json: async function () { return report; } };
  };
  const FormDataStub = function (form) {
    this.get = function (name) {
      return form.formData[name] == null ? '' : form.formData[name];
    };
  };

  vm.runInNewContext(source, {
    document: documentStub,
    window: windowStub,
    navigator: navigatorStub,
    fetch: fetchStub,
    FormData: FormDataStub
  });
  assert.equal(typeof documentStub.readyHandler, 'function');
  documentStub.readyHandler();
  await new Promise(function (resolve) { setImmediate(resolve); });

  assert.match(getElement('stats').innerHTML, /60/);
  assert.match(getElement('indicator-cards').innerHTML, /sleep duration/i);
  assert.equal((getElement('indicator-cards').innerHTML.match(/class="indicator-card"/g) || []).length, 6);
  assert.match(getElement('metric-filter').innerHTML, /sleep_duration \(hours\)/);
  assert.equal(getElement('metric-filter').value, JSON.stringify(['sleep_duration', 'hours']));
  assert.equal((getElement('alerts').innerHTML.match(/Mark reviewed/g) || []).length, 2);
  assert.equal(getElement('offline-status').textContent, 'OFFLINE SHELL READY');

  const firstReviewKey = getElement('alerts').innerHTML.match(/data-review-key="([^"]+)"/)[1]
    .replace(/&quot;/g, '"')
    .replace(/&amp;/g, '&')
    .replace(/&#39;/g, "'");
  getElement('alerts').handlers.click({
    target: {
      closest: function () {
        return { getAttribute: function () { return firstReviewKey; } };
      }
    }
  });
  assert.match(getElement('alerts').innerHTML, /Reopen review/);

  getElement('manual-form').formData = {
    timestamp: '2026-11-11T08:00',
    astronaut_id: 'ASTRA-01',
    metric: 'sleep_duration',
    value: '5.5',
    unit: 'hours',
    source_type: 'synthetic',
    source: 'ASTRA-browser-entry',
    source_reference: '',
    quality: 'valid',
    mission_day: '39',
    context_note: 'automated UI test'
  };
  getElement('manual-form').handlers.submit({ preventDefault: function () {} });
  assert.equal(getElement('log-count').textContent, 'Showing 61 of 61 observations.');

  getElement('threshold').value = '1.5';
  getElement('run-analysis').handlers.click();
  assert.equal(getElement('log-count').textContent, 'Showing 61 of 61 observations.');
  assert.match(getElement('workspace-notice').textContent, /Analysis completed/);
});
