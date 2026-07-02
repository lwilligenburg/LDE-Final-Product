/* ============================================================================
 * engine.js — faithful JavaScript port of the Python backend
 * (back_end/impacts.py + metrics.py + scoring.py + engine.py)
 *
 * The Python package remains the engine of record; this file mirrors it 1:1
 * so the app runs standalone in a browser. If you change the Python logic,
 * change it here the same way (and vice versa).
 * ========================================================================== */

"use strict";

/* ------------------------------- impacts.py ------------------------------ */

// The 5-point scale. Edit numbers here to re-shape how ratings map to points.
const RATING_SCALE = {
  "Very Low": 0.0,
  "Low": 25.0,
  "Medium": 50.0,
  "High": 75.0,
  "Very High": 100.0,
};

function ratingValue(r) {
  if (r === null || r === undefined) return null;
  if (typeof r === "number") return r;
  if (r in RATING_SCALE) return RATING_SCALE[r];
  throw new Error(`Unknown rating ${r}. Use one of ${Object.keys(RATING_SCALE)}, a 0-100 number, or null.`);
}

// An Impact = {climate, financial, time} where each is 0-100 or null (= N/A).
function rate(climate = null, financial = null, time = null) {
  return {
    climate: ratingValue(climate),
    financial: ratingValue(financial),
    time: ratingValue(time),
  };
}

// 'Does nothing' baseline — all three at Very Low (0), all applicable.
const ZERO = { climate: 0.0, financial: 0.0, time: 0.0 };

function lerpImpact(a, b, t) {
  t = Math.max(0.0, Math.min(1.0, t));
  const mix = (x, y) => (x === null || y === null) ? null : x + (y - x) * t;
  return {
    climate: mix(a.climate, b.climate),
    financial: mix(a.financial, b.financial),
    time: mix(a.time, b.time),
  };
}

/* ------------------------------- metrics.py ------------------------------ */

class PercentageMetric {
  constructor({ id, label, impact_at_0 = ZERO, impact_at_100 = ZERO, default_pct = 0.0, unit = "%", response = null }) {
    this.id = id; this.label = label;
    this.impact_at_0 = impact_at_0; this.impact_at_100 = impact_at_100;
    this.default_pct = default_pct; this.unit = unit; this.response = response;
    this.kind = "percentage";
  }
  validate(v) {
    if (typeof v !== "number" || Number.isNaN(v)) throw new Error(`${this.id}: expected a number, got ${v}`);
    if (v < 0 || v > 100) throw new Error(`${this.id}: ${v} out of range 0-100`);
  }
  impactOf(v) {
    this.validate(v);
    const t = this.response ? this.response(v) : v / 100.0;
    return lerpImpact(this.impact_at_0, this.impact_at_100, t);
  }
  default() { return this.default_pct; }
  describe(v) { return `${v}${this.unit}`; }
}

class ChoiceMetric {
  constructor({ id, label, options, default_option = "" }) {
    this.id = id; this.label = label; this.options = options;
    const keys = Object.keys(options);
    if (!keys.length) throw new Error(`${id}: ChoiceMetric needs at least one option`);
    this.default_option = default_option || keys[0];
    if (!(this.default_option in options)) throw new Error(`${id}: default_option ${default_option} is not one of ${keys}`);
    this.kind = "choice";
  }
  get choices() { return Object.keys(this.options); }
  validate(v) {
    if (!(v in this.options)) throw new Error(`${this.id}: ${v} is not a valid option; choose from ${this.choices}`);
  }
  impactOf(v) { this.validate(v); return this.options[v]; }
  default() { return this.default_option; }
  describe(v) { return String(v); }
}

class LevelMetric {
  constructor({ id, label, levels = 5, impact_at_min = ZERO, impact_at_max = ZERO, per_level = {}, level_names = [], default_level = 1 }) {
    if (levels < 2) throw new Error(`${id}: need at least 2 levels`);
    this.id = id; this.label = label; this.levels = levels;
    this.impact_at_min = impact_at_min; this.impact_at_max = impact_at_max;
    this.per_level = per_level; this.level_names = level_names; this.default_level = default_level;
    this.kind = "level";
  }
  validate(v) {
    if (!Number.isInteger(v)) throw new Error(`${this.id}: level must be an int, got ${v}`);
    if (v < 1 || v > this.levels) throw new Error(`${this.id}: level ${v} out of range 1-${this.levels}`);
  }
  impactOf(v) {
    this.validate(v);
    if (v in this.per_level) return this.per_level[v];
    const t = (v - 1) / (this.levels - 1);
    return lerpImpact(this.impact_at_min, this.impact_at_max, t);
  }
  default() { return this.default_level; }
  describe(v) {
    if (this.level_names.length && v >= 1 && v <= this.level_names.length) return `L${v} · ${this.level_names[v - 1]}`;
    return `L${v}`;
  }
}

class AllocationMetric {
  constructor({ id, label, groups, default_allocation = null, tolerance = 0.5 }) {
    if (Object.keys(groups).length < 2) throw new Error(`${id}: AllocationMetric needs at least two groups`);
    this.id = id; this.label = label; this.groups = groups; this.tolerance = tolerance;
    if (default_allocation === null) {
      const even = 100.0 / Object.keys(groups).length;
      default_allocation = Object.fromEntries(Object.keys(groups).map(g => [g, even]));
    }
    this.default_allocation = default_allocation;
    this.validate(this.default_allocation); // surface config errors eagerly
    this.kind = "allocation";
  }
  get group_names() { return Object.keys(this.groups); }
  validate(v) {
    if (typeof v !== "object" || v === null) throw new Error(`${this.id}: allocation must be an object of group -> percent`);
    const a = new Set(Object.keys(v)), b = new Set(this.group_names);
    if (a.size !== b.size || [...a].some(g => !b.has(g)))
      throw new Error(`${this.id}: allocation must cover exactly ${this.group_names}, got ${Object.keys(v)}`);
    let total = 0;
    for (const [g, share] of Object.entries(v)) {
      if (typeof share !== "number" || Number.isNaN(share)) throw new Error(`${this.id}: share for ${g} must be a number`);
      if (share < 0) throw new Error(`${this.id}: share for ${g} is negative (${share})`);
      total += share;
    }
    if (Math.abs(total - 100.0) > this.tolerance) throw new Error(`${this.id}: shares must sum to 100 (got ${total})`);
  }
  impactOf(v) {
    this.validate(v);
    const total = Object.values(v).reduce((s, x) => s + x, 0) || 100.0;
    const out = {};
    for (const dim of ["climate", "financial", "time"]) {
      const perGroup = this.group_names.map(g => [this.groups[g][dim], v[g]]);
      const defined = perGroup.filter(([val]) => val !== null);
      if (defined.length === 0) out[dim] = null;
      else if (defined.length === perGroup.length)
        out[dim] = perGroup.reduce((s, [val, share]) => s + val * share, 0) / total;
      else throw new Error(`${this.id}: dimension ${dim} is set for some groups but not all; make it consistent.`);
    }
    return out;
  }
  default() { return { ...this.default_allocation }; }
  describe(v) { return this.group_names.map(g => `${g} ${v[g]}%`).join(" · "); }
}

/* ------------------------------- scoring.py ------------------------------ */

class ScoreWeights {
  constructor(climate = 1.0, financial = 1.0, time = 1.0) {
    this.climate = climate; this.financial = financial; this.time = time;
  }
  normalised() {
    const total = this.climate + this.financial + this.time;
    if (total <= 0) throw new Error("Score weights must sum to a positive number");
    return new ScoreWeights(this.climate / total, this.financial / total, this.time / total);
  }
  combine(climateScore, financialScore, timeScore) {
    const w = this.normalised();
    return climateScore * w.climate + financialScore * w.financial + timeScore * w.time;
  }
}

/* -------------------------------- engine.py ------------------------------ */

class Simulation {
  constructor(metrics, weights = null) {
    this.metrics = {};
    for (const m of metrics) {
      if (m.id in this.metrics) throw new Error(`Duplicate metric id: ${m.id}`);
      this.metrics[m.id] = m;
    }
    this.weights = weights || new ScoreWeights();
  }

  defaultChoices() {
    return Object.fromEntries(Object.entries(this.metrics).map(([id, m]) => [id, m.default()]));
  }

  evaluate(choices = {}) {
    const unknown = Object.keys(choices).filter(id => !(id in this.metrics));
    if (unknown.length) throw new Error(`Unknown metric id(s): ${unknown.sort()}`);

    const contributions = [];
    const buckets = { climate: [], financial: [], time: [] };

    for (const [mid, metric] of Object.entries(this.metrics)) {
      const value = (mid in choices) ? choices[mid] : metric.default();
      const impact = metric.impactOf(value);
      for (const dim of ["climate", "financial", "time"]) {
        if (impact[dim] !== null) buckets[dim].push(impact[dim]); // null = N/A, skipped
      }
      contributions.push({ metric_id: mid, label: metric.label, value, rendered: metric.describe(value), impact });
    }

    const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : 0.0;
    const climate_score = mean(buckets.climate);
    const financial_score = mean(buckets.financial);
    const time_score = mean(buckets.time);
    const composite = this.weights.combine(climate_score, financial_score, time_score);

    return { climate_score, financial_score, time_score, composite, contributions };
  }
}
