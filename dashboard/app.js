/* ASTRA browser workspace — client-side, provenance-aware demonstration engine. */
(function () {
  'use strict';

  const $ = (selector) => document.querySelector(selector);
  const state = {
    readings: [], results: [], baselines: [], issues: [],
    sourceLabel: 'Bundled demonstration dataset',
    excludedReal: 0,
    reviewed: new Set()
  };
  const REQUIRED = ['timestamp', 'astronaut_id', 'metric', 'unit', 'source_type', 'source'];
  const VALID_QUALITY = ['valid', 'missing', 'invalid', 'outlier'];
  const STATUS_LABELS = {
    within_baseline: 'Within baseline',
    deviation: 'Single deviation',
    repeated_deviation: 'Repeated deviation',
    missing_or_unusable: 'Missing / unusable',
    no_baseline: 'No baseline'
  };

  function esc(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
  function fmt(value) {
    return Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  function isoDate(value) {
    return String(value || '').slice(0, 10);
  }
  function parseTime(value) {
    const date = new Date(String(value || '').trim());
    if (!Number.isFinite(date.getTime())) throw new Error('Timestamp is invalid.');
    if (!/(Z|[+-]\d{2}:\d{2})$/i.test(String(value).trim())) {
      throw new Error('Timestamp must include a timezone, for example Z or +00:00.');
    }
    return date;
  }
  function keyFor(r) {
    return JSON.stringify([
      r.astronaut_id, r.metric, r.unit, r.source_type, r.source, r.source_reference || ''
    ]);
  }
  function alertKey(result) {
    return JSON.stringify([
      keyFor(result.reading), result.reading.timestamp, result.reading.value
    ]);
  }
  function normalizeReading(r) {
    return {
      timestamp: r.timestamp,
      astronaut_id: String(r.astronaut_id || '').trim(),
      metric: String(r.metric || '').trim().toLowerCase(),
      value: r.value == null || r.value === '' ? null : Number(r.value),
      unit: String(r.unit || '').trim(),
      source_type: String(r.source_type || '').trim().toLowerCase(),
      source: String(r.source || '').trim(),
      source_reference: String(r.source_reference || '').trim(),
      quality: String(r.quality || 'valid').trim().toLowerCase(),
      mission_day: r.mission_day == null || r.mission_day === '' ? null : Number(r.mission_day),
      context_note: String(r.context_note || '').trim()
    };
  }
  function validateReading(raw, rowNumber) {
    const r = normalizeReading(raw);
    const errors = [];
    REQUIRED.forEach(function (field) {
      if (!String(r[field] == null ? '' : r[field]).trim()) errors.push({
        row_number: rowNumber, field: field, code: 'required',
        message: "Required field '" + field + "' is empty."
      });
    });
    if (errors.length) return { reading: null, errors: errors };
    try { parseTime(r.timestamp); } catch (error) {
      return { reading: null, errors: [{
        row_number: rowNumber, field: 'timestamp', code: 'invalid_timestamp', message: error.message
      }] };
    }
    if (r.source_type !== 'synthetic' && r.source_type !== 'real') {
      errors.push({
        row_number: rowNumber, field: 'source_type', code: 'invalid_source_type',
        message: "source_type must be 'synthetic' or 'real'."
      });
    }
    if (r.source_type === 'real' && !r.source_reference) {
      errors.push({
        row_number: rowNumber, field: 'source_reference', code: 'missing_source_reference',
        message: 'Real data must include a traceable source URL, DOI, or repository reference.'
      });
    }
    if (VALID_QUALITY.indexOf(r.quality) < 0) {
      errors.push({
        row_number: rowNumber, field: 'quality', code: 'invalid_quality',
        message: 'quality must be one of: ' + VALID_QUALITY.join(', ') + '.'
      });
    }
    if (r.value !== null && !Number.isFinite(r.value)) {
      errors.push({
        row_number: rowNumber, field: 'value', code: 'invalid_value',
        message: 'Value must be a finite number.'
      });
    }
    if (r.value === null && r.quality === 'valid') {
      r.quality = 'missing';
      errors.push({
        row_number: rowNumber, field: 'value', code: 'missing_value',
        message: 'Value is missing; it will not be treated as a normal reading.'
      });
    }
    if (r.quality === 'missing' || r.quality === 'invalid') r.value = null;
    if (r.mission_day !== null &&
        (!Number.isInteger(r.mission_day) || r.mission_day < 1)) {
      errors.push({
        row_number: rowNumber, field: 'mission_day', code: 'invalid_mission_day',
        message: 'mission_day must be a positive integer.'
      });
    }
    if (errors.some(function (e) {
      return e.code !== 'missing_value';
    })) return { reading: null, errors: errors };
    return { reading: r, errors: errors };
  }

  function parseCSV(text) {
    const rows = [];
    let row = [], cell = '', quoted = false;
    for (let i = 0; i < text.length; i += 1) {
      const c = text[i], next = text[i + 1];
      if (quoted) {
        if (c === '"' && next === '"') { cell += '"'; i += 1; }
        else if (c === '"') quoted = false;
        else cell += c;
      } else if (c === '"' && cell === '') quoted = true;
      else if (c === ',') { row.push(cell); cell = ''; }
      else if (c === '\n' || c === '\r') {
        if (c === '\r' && next === '\n') i += 1;
        row.push(cell); cell = '';
        if (row.some(function (v) { return String(v).trim() !== ''; })) rows.push(row);
        row = [];
      } else cell += c;
    }
    if (quoted) throw new Error('CSV contains an unclosed quoted field.');
    row.push(cell);
    if (row.some(function (v) { return String(v).trim() !== ''; })) rows.push(row);
    if (rows.length < 2) throw new Error('CSV needs a header row and at least one data row.');
    const headers = rows[0].map(function (h) { return String(h).replace(/^\uFEFF/, '').trim(); });
    const missing = REQUIRED.filter(function (field) { return headers.indexOf(field) < 0; });
    if (missing.length) throw new Error('CSV is missing required columns: ' + missing.join(', '));
    return rows.slice(1).map(function (cells) {
      const record = {};
      headers.forEach(function (header, index) { record[header] = cells[index] == null ? '' : cells[index]; });
      return record;
    });
  }

  function buildBaselines(readings, settings) {
    const groups = new Map();
    readings.forEach(function (r) {
      const time = parseTime(r.timestamp).getTime();
      if (time < settings.start || time > settings.end) return;
      if (r.quality !== 'valid' || r.value === null) return;
      const key = keyFor(r);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(r);
    });
    const baselines = [];
    groups.forEach(function (group) {
      if (group.length < settings.minimumSamples) return;
      const values = group.map(function (r) { return r.value; });
      const mean = values.reduce(function (sum, v) { return sum + v; }, 0) / values.length;
      const variance = values.reduce(function (sum, v) {
        return sum + Math.pow(v - mean, 2);
      }, 0) / values.length;
      const first = group[0];
      baselines.push({
        astronaut_id: first.astronaut_id, metric: first.metric, unit: first.unit,
        source_type: first.source_type, source: first.source,
        source_reference: first.source_reference || '',
        mean: mean, standard_deviation: Math.sqrt(variance),
        sample_count: group.length,
        period_start: group.map(function (r) { return r.timestamp; }).sort()[0],
        period_end: group.map(function (r) { return r.timestamp; }).sort().slice(-1)[0]
      });
    });
    return baselines;
  }

  function analyze(readings, baselines, settings) {
    const baselineIndex = new Map();
    baselines.forEach(function (b) {
      baselineIndex.set(JSON.stringify([
        b.astronaut_id, b.metric, b.unit, b.source_type, b.source, b.source_reference || ''
      ]), b);
    });
    const groups = new Map();
    readings.forEach(function (r) {
      const key = keyFor(r);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(r);
    });
    const output = [];
    groups.forEach(function (group, key) {
      group.sort(function (a, b) { return parseTime(a.timestamp) - parseTime(b.timestamp); });
      const baseline = baselineIndex.get(key);
      let consecutive = 0;
      group.forEach(function (reading) {
        let result;
        if (reading.quality !== 'valid' || reading.value === null) {
          consecutive = 0;
          result = {
            reading: reading, status: 'missing_or_unusable',
            baseline_mean: baseline ? baseline.mean : null,
            baseline_standard_deviation: baseline ? baseline.standard_deviation : null,
            deviation_score: null, consecutive_deviations: 0, alert: false,
            explanation: 'This observation is missing or marked unusable. It is excluded from analysis and is not interpreted as normal.',
            suggested_action: 'Verify the source measurement; record a correction or context note if available.'
          };
        } else if (!baseline) {
          consecutive = 0;
          result = {
            reading: reading, status: 'no_baseline',
            baseline_mean: null, baseline_standard_deviation: null,
            deviation_score: null, consecutive_deviations: 0, alert: false,
            explanation: 'There is not enough valid personal reference data for this metric and unit.',
            suggested_action: 'Collect sufficient valid observations in a defined calibration period before comparing changes.'
          };
        } else {
          const delta = reading.value - baseline.mean;
          let score = null, isDeviation = false, comparison = '';
          if (baseline.standard_deviation === 0) {
            isDeviation = Math.abs(delta) > 1e-12;
            comparison = 'the calibration readings had no variation';
          } else {
            score = delta / baseline.standard_deviation;
            isDeviation = Math.abs(score) >= settings.threshold;
            comparison = (score >= 0 ? '+' : '') + score.toFixed(2) + ' baseline standard deviations from the personal mean';
          }
          if (isDeviation) {
            consecutive += 1;
            const alert = consecutive >= settings.repeats;
            result = {
              reading: reading, status: alert ? 'repeated_deviation' : 'deviation',
              baseline_mean: baseline.mean,
              baseline_standard_deviation: baseline.standard_deviation,
              deviation_score: score, consecutive_deviations: consecutive, alert: alert,
              explanation: alert
                ? reading.metric + ' is outside the configured demonstration band on ' + consecutive +
                  ' consecutive valid observations (' + comparison + '); the personal baseline is ' +
                  fmt(baseline.mean) + ' ' + baseline.unit + '.'
                : reading.metric + ' differs from the personal baseline (' + fmt(baseline.mean) +
                  ' ' + baseline.unit + ') by ' + comparison + '. One observation alone does not trigger an alert.',
              suggested_action: alert
                ? 'Verify the measurement and review mission-approved procedures or contact the mission medical officer according to protocol.'
                : 'Check the measurement and add relevant workload, schedule, or event context.'
            };
          } else {
            consecutive = 0;
            result = {
              reading: reading, status: 'within_baseline',
              baseline_mean: baseline.mean,
              baseline_standard_deviation: baseline.standard_deviation,
              deviation_score: score, consecutive_deviations: 0, alert: false,
              explanation: reading.metric + ' is within the configured demonstration band around the personal baseline (' +
                fmt(baseline.mean) + ' ' + baseline.unit + '; standard deviation ' +
                fmt(baseline.standard_deviation) + ' ' + baseline.unit + ').',
              suggested_action: 'No follow-up is generated by this demonstration rule; continue recording valid observations.'
            };
          }
        }
        output.push(result);
      });
    });
    return output.sort(function (a, b) {
      return parseTime(a.reading.timestamp) - parseTime(b.reading.timestamp) ||
        a.reading.astronaut_id.localeCompare(b.reading.astronaut_id) ||
        a.reading.metric.localeCompare(b.reading.metric);
    });
  }

  function settingsFromUI() {
    const startValue = $('#baseline-start').value;
    const endValue = $('#baseline-end').value;
    if (!startValue || !endValue) throw new Error('Choose both baseline dates.');
    const start = Date.parse(startValue + 'T00:00:00Z');
    const end = Date.parse(endValue + 'T23:59:59.999Z');
    if (end < start) throw new Error('Baseline end date must be on or after the start date.');
    const threshold = Number($('#threshold').value);
    const repeats = Number($('#repeat-count').value);
    const minimumSamples = Number($('#minimum-samples').value);
    if (!Number.isFinite(threshold) || threshold <= 0) throw new Error('Deviation threshold must be greater than zero.');
    if (!Number.isInteger(repeats) || repeats < 2) throw new Error('Repeated observations must be at least 2.');
    if (!Number.isInteger(minimumSamples) || minimumSamples < 2) throw new Error('Minimum baseline samples must be at least 2.');
    return { start: start, end: end, threshold: threshold, repeats: repeats, minimumSamples: minimumSamples };
  }

  function recalculate() {
    const settings = settingsFromUI();
    state.baselines = buildBaselines(state.readings, settings);
    state.results = analyze(state.readings, state.baselines, settings);
    renderAll();
  }

  function setNotice(message, type) {
    const box = $('#workspace-notice');
    box.className = 'notice-line ' + (type || 'info');
    box.textContent = message;
  }

  function renderMetrics() {
    const metrics = Array.from(new Set(state.readings.map(function (r) { return r.metric; })));
    const alertCount = state.results.filter(function (r) { return r.alert; }).length;
    const valid = state.readings.filter(function (r) { return r.quality === 'valid' && r.value !== null; }).length;
    const statData = [
      [state.readings.length, 'Operational observations'],
      [metrics.length, 'Tracked indicators'],
      [alertCount, 'Repeated-deviation alerts'],
      [state.issues.length, 'Input validation issues']
    ];
    $('#stats').innerHTML = statData.map(function (item) {
      return '<div class="metric"><small>' + esc(item[1]) + '</small><strong>' +
        esc(item[0]) + '</strong></div>';
    }).join('');
    $('#data-summary').textContent = valid + ' valid readings · ' +
      (state.readings.length - valid) + ' missing or unusable · ' + state.baselines.length +
      ' personal baselines · ' + state.excludedReal + ' excluded rows.';
  }

  function renderSelectors() {
    const metricSelect = $('#metric-filter');
    const astronautSelect = $('#astronaut-filter');
    let metricCurrent = metricSelect.value, astronautCurrent = astronautSelect.value;
    const metrics = Array.from(new Set(state.readings.map(function (r) { return r.metric; }))).sort();
    const astronauts = Array.from(new Set(state.readings.map(function (r) { return r.astronaut_id; }))).sort();
    if (metricCurrent === 'all' && metrics.length) {
      metricCurrent = metrics.indexOf('sleep_duration') >= 0 ? 'sleep_duration' : metrics[0];
    }
    metricSelect.innerHTML = '<option value="all">All indicators</option>' +
      metrics.map(function (m) { return '<option value="' + esc(m) + '">' + esc(m.replaceAll('_', ' ')) + '</option>'; }).join('');
    astronautSelect.innerHTML = '<option value="all">All crew IDs</option>' +
      astronauts.map(function (m) { return '<option value="' + esc(m) + '">' + esc(m) + '</option>'; }).join('');
    if (metrics.indexOf(metricCurrent) >= 0 || metricCurrent === 'all') metricSelect.value = metricCurrent;
    if (astronauts.indexOf(astronautCurrent) >= 0 || astronautCurrent === 'all') astronautSelect.value = astronautCurrent;
  }

  function renderChart() {
    const metric = $('#metric-filter').value;
    const astronaut = $('#astronaut-filter').value;
    $('#chart-title').textContent = metric === 'all' ? 'Operational indicator trends' :
      metric.replaceAll('_', ' ') + ' trend';
    if (metric === 'all' && new Set(state.readings.map(function (r) { return r.metric; })).size > 1) {
      $('#chart').innerHTML = '<text x="350" y="115" text-anchor="middle" fill="#91a4bc">Select one indicator to compare values with its personal baseline.</text>';
      $('#chart-note').textContent = 'Different indicators use different units and should not share one numeric axis.';
      return;
    }
    let points = state.results.filter(function (r) {
      return r.reading.value !== null &&
        (metric === 'all' || r.reading.metric === metric) &&
        (astronaut === 'all' || r.reading.astronaut_id === astronaut);
    });
    points.sort(function (a, b) { return parseTime(a.reading.timestamp) - parseTime(b.reading.timestamp); });
    const svg = $('#chart');
    if (!points.length) {
      svg.innerHTML = '<text x="350" y="115" text-anchor="middle" fill="#91a4bc">No numeric observations match these filters.</text>';
      $('#chart-note').textContent = 'Select another indicator or crew ID, or add valid readings.';
      return;
    }
    const values = points.map(function (p) { return Number(p.reading.value); });
    const segments = new Map();
    points.forEach(function (p) {
      const k = keyFor(p.reading);
      if (!segments.has(k)) segments.set(k, []);
      segments.get(k).push(p);
    });
    const baselineValues = points.map(function (p) { return p.baseline_mean; })
      .filter(function (v) { return v !== null && v !== undefined; });
    const scaleValues = values.concat(baselineValues);
    const min = Math.min.apply(null, scaleValues), max = Math.max.apply(null, scaleValues), span = max - min || 1;
    const x = function (i) { return 48 + i * (610 / Math.max(points.length - 1, 1)); };
    const y = function (v) { return 202 - ((v - min) / span) * 165; };
    const paths = [];
    paths.push('<line x1="45" y1="202" x2="660" y2="202" stroke="#34465d"/>');
    paths.push('<line x1="45" y1="25" x2="45" y2="202" stroke="#34465d"/>');
    segments.forEach(function (segment) {
      const base = segment[0].baseline_mean;
      const firstIndex = points.indexOf(segment[0]);
      const lastIndex = points.indexOf(segment[segment.length - 1]);
      if (base !== null && base !== undefined) {
        const lineY = y(base);
        paths.push('<line x1="' + x(firstIndex) + '" y1="' + lineY +
          '" x2="' + Math.max(x(firstIndex) + 16, x(lastIndex)) + '" y2="' + lineY +
          '" stroke="#f1bd68" stroke-dasharray="6 5"/>');
        paths.push('<text x="' + x(firstIndex) + '" y="' + Math.max(16, lineY - 7) +
          '" fill="#f1bd68" font-size="10">Baseline ' + esc(fmt(base)) + '</text>');
      }
      paths.push('<polyline fill="none" stroke="#65d4d0" stroke-width="2.5" points="' +
        segment.map(function (p) { return x(points.indexOf(p)) + ',' + y(p.reading.value); }).join(' ') + '"/>');
      segment.forEach(function (p) {
        const color = p.alert ? '#f07878' : (p.status === 'deviation' ? '#f1bd68' : '#65d4d0');
        paths.push('<circle cx="' + x(points.indexOf(p)) + '" cy="' + y(p.reading.value) +
          '" r="4.5" fill="' + color + '"><title>' + esc(p.reading.metric) + ': ' +
          esc(p.reading.value) + ' ' + esc(p.reading.unit) + ' · ' +
          esc(STATUS_LABELS[p.status]) + '</title></circle>');
      });
    });
    paths.push('<text x="45" y="225" fill="#91a4bc" font-size="11">' +
      esc(isoDate(points[0].reading.timestamp)) + '</text>');
    paths.push('<text x="660" y="225" text-anchor="end" fill="#91a4bc" font-size="11">' +
      esc(isoDate(points[points.length - 1].reading.timestamp)) + '</text>');
    svg.innerHTML = paths.join('');
    $('#chart-note').textContent = points.length + ' points · ' +
      (metric === 'all' ? 'all indicators' : metric.replaceAll('_', ' ')) +
      ' · baseline shown when a matching personal reference is available. Colors: cyan = within band, amber = single deviation, red = repeated alert.';
  }

  function renderAlerts() {
    const alerts = state.results.filter(function (r) { return r.alert; }).slice().reverse();
    $('#alerts').innerHTML = alerts.length ? alerts.map(function (r) {
      const key = alertKey(r);
      const reviewed = state.reviewed.has(key);
      return '<article class="alert"><b>' + esc(r.reading.metric.replaceAll('_', ' ')) +
        ' · ' + esc(r.reading.astronaut_id) + '</b><div>' + esc(r.explanation) +
        '</div><div class="muted">Day ' + esc(r.reading.mission_day == null ? '—' : r.reading.mission_day) +
        ' · ' + esc(r.reading.timestamp) + '</div><div class="muted"><strong>Suggested review:</strong> ' +
        esc(r.suggested_action) + '</div><div class="review-actions"><span class="tag">' +
        (reviewed ? 'ACKNOWLEDGED IN THIS SESSION' : 'AWAITING REVIEW') +
        '</span><button class="action-btn" type="button" data-review-key="' + esc(key) + '">' +
        (reviewed ? 'Reopen review' : 'Mark reviewed') + '</button></div></article>';
    }).join('') : '<div class="empty">No repeated-deviation alerts under the current settings.</div>';
  }

  function renderRows() {
    const query = $('#log-search').value.trim().toLowerCase();
    const status = $('#status-filter').value;
    const rows = state.results.slice().reverse().filter(function (r) {
      const haystack = [
        r.reading.astronaut_id, r.reading.metric, r.reading.source, r.reading.context_note,
        STATUS_LABELS[r.status]
      ].join(' ').toLowerCase();
      return (!query || haystack.indexOf(query) >= 0) && (status === 'all' || r.status === status);
    });
    $('#rows').innerHTML = rows.map(function (r) {
      const statusClass = r.alert ? 'state-danger' : (r.status === 'deviation' ? 'state-warn' : '');
      return '<tr><td>' + esc(isoDate(r.reading.timestamp)) + '</td><td>' +
        esc(r.reading.astronaut_id) + '</td><td>' +
        esc(r.reading.metric.replaceAll('_', ' ')) + '</td><td>' +
        esc(r.reading.value == null ? '—' : r.reading.value) + ' ' + esc(r.reading.unit) +
        '</td><td><span class="tag ' + statusClass + '">' + esc(STATUS_LABELS[r.status]) +
        '</span></td><td>' + esc(r.reading.source_type) + ' · ' + esc(r.reading.source) +
        '</td></tr>';
    }).join('');
    $('#log-count').textContent = 'Showing ' + rows.length + ' of ' + state.results.length + ' observations.';
  }

  function renderIssues() {
    if (!state.issues.length) {
      $('#issues').innerHTML = '<div class="empty">No input validation issues.</div>';
      return;
    }
    $('#issues').innerHTML = '<ul class="issue-list">' + state.issues.map(function (issue) {
      return '<li><strong>Row ' + esc(issue.row_number) + ' · ' + esc(issue.field) +
        '</strong>: ' + esc(issue.message) + '</li>';
    }).join('') + '</ul>';
  }

  function renderAll() {
    renderMetrics();
    renderSelectors();
    const sources = Array.from(new Set(state.readings.map(function (r) {
      return r.source_type + ' · ' + r.source;
    })));
    $('#provenance').textContent = sources.length ? sources.join('; ') :
      'No operational dataset is currently loaded.';
    renderChart();
    renderAlerts();
    renderRows();
    renderIssues();
    $('#source-label').textContent = state.sourceLabel;
  }

  function loadReadings(rawRows, sourceLabel) {
    const accepted = [], issues = [];
    rawRows.forEach(function (row, index) {
      const checked = validateReading(row, index + 2);
      if (checked.reading) accepted.push(checked.reading);
      checked.errors.forEach(function (issue) { issues.push(issue); });
    });
    state.readings = accepted;
    state.issues = issues;
    state.reviewed.clear();
    state.excludedReal = 0;
    state.sourceLabel = sourceLabel;
    recalculate();
  }

  async function loadDemo() {
    setNotice('Loading bundled demonstration readings…', 'info');
    try {
      const response = await fetch('../output/demo-report.json', { cache: 'no-store' });
      if (!response.ok) throw new Error('Bundled report could not be loaded (HTTP ' + response.status + ').');
      const report = await response.json();
      if (!Array.isArray(report.results)) throw new Error('Bundled report has no results array.');
      const readings = report.results.map(function (r) { return r.reading; });
      state.readings = readings.map(normalizeReading);
      state.issues = (report.validation_issues || []).slice();
      state.sourceLabel = 'Bundled demonstration dataset';
      state.excludedReal = 0;
      state.reviewed.clear();
      recalculate();
      setNotice('Demonstration dataset loaded. You can add readings, import a CSV, change baseline settings, and rerun the analysis.', 'success');
    } catch (error) {
      state.readings = [];
      state.issues = [];
      state.sourceLabel = 'No dataset loaded';
      recalculate();
      setNotice(error.message + ' Use the CSV importer or manual entry to load observations.', 'error');
    }
  }

  function addManualReading(event) {
    event.preventDefault();
    const form = $('#manual-form');
    const data = new FormData(form);
    const timestamp = new Date(String(data.get('timestamp'))).toISOString();
    const raw = {
      timestamp: timestamp,
      astronaut_id: data.get('astronaut_id'),
      metric: data.get('metric'),
      value: data.get('value'),
      unit: data.get('unit'),
      source_type: data.get('source_type'),
      source: data.get('source'),
      source_reference: data.get('source_reference'),
      quality: data.get('quality'),
      mission_day: data.get('mission_day'),
      context_note: data.get('context_note')
    };
    const checked = validateReading(raw, state.readings.length + 2);
    if (!checked.reading) {
      setNotice(checked.errors.map(function (e) { return e.message; }).join(' '), 'error');
      return;
    }
    state.readings.push(checked.reading);
    checked.errors.forEach(function (issue) { state.issues.push(issue); });
    state.sourceLabel = 'Browser workspace · manually extended dataset';
    recalculate();
    form.reset();
    $('#manual-timestamp').value = new Date().toISOString().slice(0, 16);
    $('#manual-astronaut').value = 'ASTRA-01';
    $('#manual-source').value = 'ASTRA-browser-entry';
    setNotice('Reading added and analysis rerun. Check its status in the observation log and review queue.', 'success');
  }

  function downloadFile(name, content, type) {
    const blob = new Blob([content], { type: type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name; a.click();
    URL.revokeObjectURL(url);
  }
  function reportObject() {
    return {
      baselines: state.baselines,
      results: state.results,
      validation_issues: state.issues,
      reviewed_alerts: Array.from(state.reviewed)
    };
  }
  function downloadCSV() {
    const columns = [
      'timestamp', 'astronaut_id', 'metric', 'value', 'unit', 'status',
      'baseline_mean', 'baseline_standard_deviation', 'deviation_score',
      'consecutive_deviations', 'alert', 'reviewed', 'source_type', 'source',
      'source_reference', 'quality', 'mission_day', 'context_note'
    ];
    function quote(v) {
      const s = String(v == null ? '' : v);
      return '"' + s.replace(/"/g, '""') + '"';
    }
    const lines = [columns.join(',')];
    state.results.forEach(function (r) {
      const item = r.reading;
      const values = [
        item.timestamp, item.astronaut_id, item.metric, item.value, item.unit, r.status,
        r.baseline_mean, r.baseline_standard_deviation, r.deviation_score,
        r.consecutive_deviations, r.alert, state.reviewed.has(alertKey(r)),
        item.source_type, item.source, item.source_reference, item.quality,
        item.mission_day, item.context_note
      ];
      lines.push(values.map(quote).join(','));
    });
    downloadFile('astra-analysis.csv', lines.join('\r\n'), 'text/csv;charset=utf-8');
  }
  function downloadTemplate() {
    const header = [
      'timestamp', 'astronaut_id', 'metric', 'value', 'unit', 'source_type',
      'source', 'source_reference', 'quality', 'mission_day', 'context_note'
    ];
    const example = [
      '2026-11-11T08:00:00Z', 'ASTRA-01', 'sleep_duration', '6.4', 'hours',
      'synthetic', 'ASTRA-imported-demo', '', 'valid', '39', 'High workload (example)'
    ];
    downloadFile('astra-telemetry-template.csv',
      header.join(',') + '\r\n' + example.map(function (v) { return '"' + String(v).replace(/"/g, '""') + '"'; }).join(',') + '\r\n',
      'text/csv;charset=utf-8');
  }

  function wireEvents() {
    $('#manual-form').addEventListener('submit', addManualReading);
    $('#run-analysis').addEventListener('click', function () {
      try {
        recalculate();
        setNotice('Analysis completed using the current baseline window and alert settings.', 'success');
      } catch (error) { setNotice(error.message, 'error'); }
    });
    $('#load-demo').addEventListener('click', loadDemo);
    $('#csv-file').addEventListener('change', async function (event) {
      const file = event.target.files && event.target.files[0];
      if (!file) return;
      try {
        const records = parseCSV(await file.text());
        loadReadings(records, 'Imported CSV · ' + file.name);
        setNotice('CSV imported. ' + state.readings.length + ' valid rows loaded; ' +
          state.issues.length + ' row or field issues listed below. Verify the baseline dates before using the results.', 'success');
      } catch (error) { setNotice(error.message, 'error'); }
      event.target.value = '';
    });
    $('#alerts').addEventListener('click', function (event) {
      const button = event.target.closest('button[data-review-key]');
      if (!button) return;
      const key = button.getAttribute('data-review-key');
      if (state.reviewed.has(key)) state.reviewed.delete(key);
      else state.reviewed.add(key);
      renderAlerts();
      setNotice(state.reviewed.has(key)
        ? 'Alert acknowledged for review in this browser session. The analysis result is unchanged.'
        : 'Alert returned to the review queue. The analysis result is unchanged.', 'success');
    });
    $('#metric-filter').addEventListener('change', renderChart);
    $('#astronaut-filter').addEventListener('change', renderChart);
    $('#log-search').addEventListener('input', renderRows);
    $('#status-filter').addEventListener('change', renderRows);
    $('#download-json').addEventListener('click', function () {
      downloadFile('astra-analysis.json', JSON.stringify(reportObject(), null, 2), 'application/json');
    });
    $('#download-csv').addEventListener('click', downloadCSV);
    $('#download-template').addEventListener('click', downloadTemplate);
    $('#clear-data').addEventListener('click', function () {
      if (!window.confirm('Clear all current operational readings from this browser session?')) return;
      state.readings = []; state.results = []; state.baselines = []; state.issues = [];
      state.sourceLabel = 'No dataset loaded'; state.excludedReal = 0;
      state.reviewed.clear();
      renderAll();
      setNotice('Operational workspace cleared. NASA historical research remains separate and unchanged.', 'success');
    });
  }

  function registerOfflineShell() {
    if (typeof navigator === 'undefined' || !('serviceWorker' in navigator) || !window.isSecureContext) {
      const status = $('#offline-status');
      if (status) status.textContent = 'OFFLINE CACHE UNAVAILABLE';
      return;
    }
    navigator.serviceWorker.register('../sw.js')
      .then(function () { return navigator.serviceWorker.ready; })
      .then(function () {
        const status = $('#offline-status');
        if (status) status.textContent = 'OFFLINE SHELL READY';
      })
      .catch(function () {
        const status = $('#offline-status');
        if (status) status.textContent = 'OFFLINE CACHE NOT INSTALLED';
      });
  }

  function init() {
    wireEvents();
    registerOfflineShell();
    $('#manual-timestamp').value = new Date().toISOString().slice(0, 16);
    $('#manual-astronaut').value = 'ASTRA-01';
    $('#manual-source').value = 'ASTRA-browser-entry';
    loadDemo();
  }
  if (typeof window !== 'undefined') {
    window.ASTRA_ENGINE = {
      parseCSV: parseCSV,
      validateReading: validateReading,
      buildBaselines: buildBaselines,
      analyze: analyze
    };
  }
  document.addEventListener('DOMContentLoaded', init);
})();