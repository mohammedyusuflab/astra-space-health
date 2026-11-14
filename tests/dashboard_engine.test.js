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

test('CSV parser rejects duplicate headers and rows with excess columns', function () {
  assert.throws(function () {
    engine.parseCSV(
      'timestamp,astronaut_id,metric,unit,source_type,source,metric\n' +
      '2026-11-01T08:00:00Z,A,sleep,hours,synthetic,demo,sleep\n'
    );
  }, /duplicate column names/i);
  assert.throws(function () {
    engine.parseCSV(
      'timestamp,astronaut_id,metric,unit,source_type,source\n' +
      '2026-11-01T08:00:00Z,A,sleep,hours,synthetic,demo,unexpected\n'
    );
  }, /more values than the header row/i);
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

test('calibration-window observations cannot trigger operational alerts', function () {
  const samples = [
    reading('2026-11-01T08:00:00Z', 10),
    reading('2026-11-02T08:00:00Z', 10),
    reading('2026-11-03T08:00:00Z', 10),
    reading('2026-11-04T08:00:00Z', 100),
    reading('2026-11-05T08:00:00Z', 100)
  ];
  const baselines = engine.buildBaselines(samples, {
    start: Date.parse('2026-11-01T00:00:00Z'),
    end: Date.parse('2026-11-05T23:59:59Z'),
    minimumSamples: 3
  });
  const results = engine.analyze(samples, baselines, {
    threshold: 1,
    repeats: 2,
    start: Date.parse('2026-11-01T00:00:00Z'),
    end: Date.parse('2026-11-05T23:59:59Z')
  });
  assert.equal(results.filter(function (result) { return result.alert; }).length, 0);
  assert.ok(results.every(function (result) { return result.status === 'within_baseline'; }));
  assert.ok(results.every(function (result) {
    return result.explanation.includes('calibration window');
  }));
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



test('CSV parser rejects malformed quote placement', function () {
  const header = 'timestamp,astronaut_id,metric,value,unit,source_type,source\n';
  assert.throws(function () {
    engine.parseCSV(header + '2026-11-01T08:00:00Z,A,"heart"rate,70,bpm,synthetic,demo\n');
  }, /characters after a closing quote/i);
  assert.throws(function () {
    engine.parseCSV(header + '2026-11-01T08:00:00Z,A,heart"rate,70,bpm,synthetic,demo\n');
  }, /quote inside an unquoted field/i);
});

test('analysis settings enforce the ranges shown in the dashboard', function () {
  const valid = engine.validateSettings({
    start: 1, end: 2, threshold: 0.1, repeats: 2, minimumSamples: 2
  });
  assert.equal(valid.threshold, 0.1);
  assert.equal(valid.repeats, 2);
  assert.equal(valid.minimumSamples, 2);
  assert.throws(function () {
    engine.validateSettings({ start: 1, end: 2, threshold: 10.1, repeats: 2, minimumSamples: 3 });
  }, /between 0.1 and 10/i);
  assert.throws(function () {
    engine.validateSettings({ start: 1, end: 2, threshold: 2, repeats: 21, minimumSamples: 3 });
  }, /between 2 and 20/i);
  assert.throws(function () {
    engine.validateSettings({ start: 1, end: 2, threshold: 2, repeats: 2, minimumSamples: 31 });
  }, /between 2 and 30/i);
  assert.throws(function () {
    engine.validateSettings({ start: 2, end: 1, threshold: 2, repeats: 2, minimumSamples: 3 });
  }, /on or after/i);
});

test('manual datetime defaults preserve local wall-clock time', function () {
  const local = new Date(2026, 10, 14, 13, 10, 30, 0);
  assert.equal(engine.localDateTimeValue(local), '2026-11-14T13:10');
});

test('CSV export neutralizes spreadsheet formula text without changing numeric values', function () {
  assert.equal(engine.csvCell('=HYPERLINK("https://example.com")'), '"\'=HYPERLINK(""https://example.com"")"');
  assert.equal(engine.csvCell('  @SUM(A1:A2)'), '"\'  @SUM(A1:A2)"');
  assert.equal(engine.csvCell(-12.5), '"-12.5"');
});

test('operational dashboard engine never loads the separate NASA research JSON', function () {
  assert.equal(source.includes('osd569-cbc.json'), false);
  assert.ok(source.includes('../output/demo-report.json'));
});
