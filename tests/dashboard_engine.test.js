'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'dashboard', 'app.js'), 'utf8');
const browserDocumentStub = { addEventListener: function () {} };
const browserWindowStub = {};
vm.runInNewContext(source, {
  document: browserDocumentStub,
  window: browserWindowStub
});
const engine = browserWindowStub.ASTRA_ENGINE;

function reading(timestamp, value, sourceName) {
  return {
    timestamp: timestamp,
    astronaut_id: 'ASTRA-01',
    metric: 'heart_rate',
    value: value,
    unit: 'bpm',
    source_type: 'synthetic',
    source: sourceName || 'unit-test-sensor',
    source_reference: '',
    quality: 'valid',
    mission_day: null,
    context_note: ''
  };
}

test('CSV parser preserves quoted commas and maps headers', function () {
  const records = engine.parseCSV(
    'timestamp,astronaut_id,metric,value,unit,source_type,source,context_note\n' +
    '"2026-11-01T08:00:00Z",ASTRA-01,sleep_duration,7.2,hours,synthetic,demo,"heavy workload, exercise"\n'
  );
  assert.equal(records.length, 1);
  assert.equal(records[0].context_note, 'heavy workload, exercise');
  assert.equal(records[0].metric, 'sleep_duration');
});

test('CSV parser rejects files missing required telemetry columns', function () {
  assert.throws(function () {
    engine.parseCSV('timestamp,metric,value\n2026-11-01T08:00:00Z,sleep,7\n');
  }, /missing required columns/i);
});

test('real readings require a traceable source reference', function () {
  const checked = engine.validateReading({
    timestamp: '2026-11-01T08:00:00Z',
    astronaut_id: 'ASTRA-01',
    metric: 'heart_rate',
    value: '70',
    unit: 'bpm',
    source_type: 'real',
    source: 'wearable-device',
    source_reference: '',
    quality: 'valid'
  }, 2);
  assert.equal(checked.reading, null);
  assert.ok(checked.errors.some(function (issue) {
    return issue.code === 'missing_source_reference';
  }));
});

test('personal baselines are grouped by source provenance', function () {
  const samples = [
    reading('2026-11-01T08:00:00Z', 10),
    reading('2026-11-02T08:00:00Z', 11),
    reading('2026-11-03T08:00:00Z', 9),
    reading('2026-11-01T08:00:00Z', 100, 'different-sensor')
  ];
  const baselines = engine.buildBaselines(samples, {
    start: Date.parse('2026-11-01T00:00:00Z'),
    end: Date.parse('2026-11-03T23:59:59Z'),
    minimumSamples: 3
  });
  assert.equal(baselines.length, 1);
  assert.equal(baselines[0].mean, 10);
  assert.equal(baselines[0].sample_count, 3);
  const results = engine.analyze(samples, baselines, { threshold: 2, repeats: 2 });
  assert.equal(results.find(function (r) {
    return r.reading.source === 'different-sensor';
  }).status, 'no_baseline');
});

test('two consecutive deviations create a review alert, not a single deviation', function () {
  const samples = [
    reading('2026-11-01T08:00:00Z', 10),
    reading('2026-11-02T08:00:00Z', 11),
    reading('2026-11-03T08:00:00Z', 9),
    reading('2026-11-04T08:00:00Z', 12),
    reading('2026-11-05T08:00:00Z', 13)
  ];
  const baselines = engine.buildBaselines(samples, {
    start: Date.parse('2026-11-01T00:00:00Z'),
    end: Date.parse('2026-11-03T23:59:59Z'),
    minimumSamples: 3
  });
  const results = engine.analyze(samples, baselines, { threshold: 2, repeats: 2 });
  assert.equal(results[3].status, 'deviation');
  assert.equal(results[3].alert, false);
  assert.equal(results[4].status, 'repeated_deviation');
  assert.equal(results[4].alert, true);
});

test('timestamps without an explicit timezone are rejected', function () {
  const checked = engine.validateReading({
    timestamp: '2026-11-01T08:00:00',
    astronaut_id: 'ASTRA-01',
    metric: 'heart_rate',
    value: '70',
    unit: 'bpm',
    source_type: 'synthetic',
    source: 'unit-test-sensor',
    quality: 'valid'
  }, 2);
  assert.equal(checked.reading, null);
  assert.ok(checked.errors.some(function (issue) {
    return issue.code === 'invalid_timestamp';
  }));
});


test('operational dashboard engine never loads the separate NASA research JSON', function () {
  assert.equal(source.includes('osd569-cbc.json'), false);
  assert.ok(source.includes('../output/demo-report.json'));
});
