/* ============================================================================
 * app.js — Sustainable Aviation: Wings of the Future
 * UI state machine + question→backend wiring.
 *
 * Question → metric mapping (agreed design):
 *   T1 SAF        : saf_co2_cuts · saf_time_to_100 · saf_WTC
 *   T2 Passport   : passport_digital_depth · passport_reg_support · passport_adoption
 *   T3 Next-Gen   : slider drives BOTH nextgen_decarb_commitment (value) and
 *                   nextgen_policy_instrument (<50 → Mandate, ≥50 → Incentive);
 *                   fuel choice → nextgen_tech_toggle (+ nextgen_tech_priority = 100);
 *                   actions → nextgen_actions
 *   T4 Transport  : transport_mode_shift · transport_carbon_tax · transport_buffer
 *   T5 Bio-Sensors: biosensor_maintenance · biosensor_reliability · biosensor_certification
 *   T6 Emission   : funding choice → funding_split (chosen group 100%, rest 0) [MOD 19]
 *                   participation slider → EGE_participation (0-100 → level 1-5)
 *                   trust → EGE_market_trust
 * Low/Medium/High buttons map to LevelMetric levels 1 / 3 / 5.
 * ========================================================================== */

"use strict";

/* ------------------------------ configuration --------------------------- */

// Character thresholds on each 0-100 dimension score.
const THRESHOLD_HIGH = 67;   // score >= HIGH  → happy face
const THRESHOLD_MEDIUM = 34; // score >= MEDIUM → neutral face; below → sad

const LMH_LEVELS = { "Low": 1, "Medium": 3, "High": 5 };

const TOPICS = [
  {
    id: "saf", title: "SAF", tagline: "Cleaner fuel, fewer flight emissions",
    icon: "assets/icon_saf.png",
    questions: [
      { type: "slider", label: "CO₂ cuts\n(%)", min: "0", max: "100", metric: "saf_co2_cuts" },
      { type: "slider", label: "Time to 100% SAF\n(% vol)", min: "0", max: "100", metric: "saf_time_to_100" },
      { type: "slider", label: "Willingness to contribute\nfinancially (WTC)\n( % premium accepted)", min: "0", max: "100", metric: "saf_WTC" },
    ],
  },
  {
    id: "passport", title: "Digital Product Passport", tagline: "Tracking every part's lifecycle data",
    icon: "assets/icon_passport.png",
    questions: [
      { type: "slider", label: "Data depth\n% (basic → full lifecycle)", min: "0", max: "100", metric: "passport_digital_depth" },
      { type: "choice", label: "Regulatory Support", options: ["Low", "Medium", "High"], metric: "passport_reg_support", map: "lmh" },
      { type: "choice", label: "Industry Adoption", options: ["Low", "Medium", "High"], metric: "passport_adoption", map: "lmh" },
    ],
  },
  {
    id: "roadmap", title: "Next-Gen Roadmapping", tagline: "Planning tomorrow's aviation path",
    icon: "assets/icon_roadmap.png",
    questions: [
      { type: "slider", label: "Mandates vs Incentives\n(Decarbonisation commitment)", min: "Mandate", max: "Incentive", metric: "nextgen_decarb_commitment", special: "policy" },
      { type: "choice", label: "Priority on new fuel system\n(SAF/H2/Electric)", options: ["SAF", "H2", "Electric"], metric: "nextgen_tech_toggle", special: "tech" },
      { type: "choice", label: "Who's actions needed", options: ["Airline", "OEM", "Government"], metric: "nextgen_actions", map: { "Airline": "Airlines", "OEM": "OEMs", "Government": "Government" } },
    ],
  },
  {
    id: "transport", title: "Green Transport", tagline: "Moving aircraft parts more sustainably",
    icon: "assets/icon_transport.png",
    questions: [
      { type: "slider", label: "Shift to low climate, resource,\nand air-quality impact modes\n(% of cargo)", min: "0", max: "100", metric: "transport_mode_shift" },
      { type: "slider", label: "Carbon Tax\n(Euro/tonne)", min: "0", max: "100", metric: "transport_carbon_tax" },
      { type: "choice", label: "Schedule Buffer", options: ["Low", "Medium", "High"], metric: "transport_buffer", map: "lmh" },
    ],
  },
  {
    id: "biosensor", title: "Bio-Sensors", tagline: "Smart sensors tracking aircraft health",
    icon: "assets/icon_biosensor.png",
    questions: [
      { type: "choice", label: "System maintenance effort", options: ["Low", "Medium", "High"], metric: "biosensor_maintenance", map: "lmh" },
      { type: "slider", label: "Reliability gain vs. current\nsensors (% more reliable)", min: "0", max: "100", metric: "biosensor_reliability" },
      { type: "choice", label: "Certification Support", options: ["Low", "Medium", "High"], metric: "biosensor_certification", map: "lmh" },
    ],
  },
  {
    id: "ecolabel", title: "Emission Guide & Eco-Label", tagline: "Rating on emission performance",
    icon: "assets/icon_ecolabel.png",
    questions: [
      { type: "choice", label: "Who funds it", options: ["Public", "Private", "Government"], metric: "funding_split", special: "funding" },
      { type: "slider", label: "Global Participation\n(incl. Eco-labels)", min: "0", max: "100", metric: "EGE_participation", special: "level5" },
      { type: "choice", label: "Market Trust in Label", options: ["Low", "Medium", "High"], metric: "EGE_market_trust", map: "lmh" },
    ],
  },
];

const SCORE_ROWS = [
  { key: "climate",   title: "Sustainability Score",  sub: "How much CO₂ you saved",      img: "earth" },
  { key: "financial", title: "ROI Score",              sub: "Return on your investment",    img: "plane" },
  { key: "time",      title: "Timeline Impact Score",  sub: "How fast impact is delivered", img: "stopwatch" },
];

const PHRASES = {
  earth:     { high: "The planet's breathing easier great job!", medium: "Some progress, but Earth needs more.",    low: "Emissions are still hurting the planet" },
  plane:     { high: "Smart investment the returns are flying high!", medium: "Breaking even, but not soaring yet.", low: "This one's losing money, I'm afraid" },
  stopwatch: { high: "Fast to impact\nno time wasted!", medium: "Getting there, but the clock's ticking.",           low: "This'll take a long time to deliver" },
};

/* --------------------------------- state -------------------------------- */

const sim = buildSimulation();

const state = {
  mode: "home",          // home | intro | topic | ready | results
  openTopic: null,       // index of the topic panel currently open
  answers: TOPICS.map(t => t.questions.map(q => (q.type === "slider" ? 0 : null))),
  completed: TOPICS.map(() => false),
  result: null,
};

const $ = sel => document.querySelector(sel);
const el = (tag, cls, html) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html !== undefined) n.innerHTML = html;
  return n;
};

/* --------------------------- choices → engine --------------------------- */

function collectChoices() {
  const choices = {};
  TOPICS.forEach((topic, ti) => {
    topic.questions.forEach((q, qi) => {
      const a = state.answers[ti][qi];
      if (q.special === "policy") {
        choices["nextgen_decarb_commitment"] = a;
        choices["nextgen_policy_instrument"] = a < 50 ? "Mandate" : "Incentive";
      } else if (q.special === "tech") {
        choices["nextgen_tech_toggle"] = a;
        choices["nextgen_tech_priority"] = 100; // full priority to the chosen tech (tunable)
      } else if (q.special === "funding") {
        const split = { "Government": 0, "Private": 0, "NGO": 0, "Public": 0 };
        split[a] = 100;
        choices["funding_split"] = split;
      } else if (q.special === "level5") {
        choices[q.metric] = 1 + Math.round((a / 100) * 4); // 0-100 slider → level 1-5
      } else if (q.map === "lmh") {
        choices[q.metric] = LMH_LEVELS[a];
      } else if (q.map && typeof q.map === "object") {
        choices[q.metric] = q.map[a];
      } else {
        choices[q.metric] = a;
      }
    });
  });
  return choices;
}

function stateFor(score) {
  if (score >= THRESHOLD_HIGH) return "high";
  if (score >= THRESHOLD_MEDIUM) return "medium";
  return "low";
}

function verdictFor(r) {
  const dims = [
    { key: "climate", score: r.climate_score, best: "Strong sustainability", worst: "but the planet pays" },
    { key: "financial", score: r.financial_score, best: "Strong returns", worst: "but the business case is weak" },
    { key: "time", score: r.time_score, best: "Fast to deliver", worst: "but slow to deliver" },
  ];
  const states = dims.map(d => stateFor(d.score));
  if (states.every(s => s === "high")) return "A rare hat-trick: green, profitable, and fast.";
  if (states.every(s => s === "low")) return "Back to the drawing board on all three fronts.";
  if (new Set(dims.map(d => Math.round(d.score))).size === 1) return "A perfectly balanced course on every front.";
  const best = dims.reduce((a, b) => (b.score > a.score ? b : a));
  const worst = dims.reduce((a, b) => (b.score < a.score ? b : a));
  return `${best.best}, ${worst.worst}.`;
}

function personaFor(r) {
  const s = [r.climate_score, r.financial_score, r.time_score];
  const max = Math.max(...s), min = Math.min(...s);
  if (max - min < 10) return "Balanced";
  return ["Visionary", "Pragmatist", "Sprinter"][s.indexOf(max)];
}

/* ------------------------------- rendering ------------------------------ */

function completedCount() { return state.completed.filter(Boolean).length; }
function allCompleted() { return completedCount() === TOPICS.length; }

function render() {
  renderTiles();
  renderCenter();
  renderSidebar();
}

/* ---- topic tiles (left grid) ---- */

function renderTiles() {
  TOPICS.forEach((topic, i) => {
    const tile = $("#tile-" + i);
    tile.classList.remove("faded", "selected", "done", "clickable");
    if (state.mode === "home") return; // plain, not clickable

    if (state.mode === "results") { tile.classList.add("faded"); return; }

    if (state.mode === "topic") {
      if (i === state.openTopic) tile.classList.add("selected");
      else tile.classList.add("faded");
      if (state.completed[i]) tile.classList.add("done");
      return;
    }
    // intro / ready — all clickable, completed get a check
    tile.classList.add("clickable");
    if (state.completed[i]) tile.classList.add("done");
  });
}

/* ---- center panel ---- */

function renderCenter() {
  const c = $("#center");
  c.innerHTML = "";

  if (state.mode === "home") {
    c.appendChild(el("div", "title-panel"));
    return;
  }

  if (state.mode === "intro" || state.mode === "ready") {
    const box = el("div", "panel intro-panel");
    const inner = el("div", "intro-text");
    if (state.mode === "ready") {
      inner.appendChild(el("div", "intro-head", "All six topics complete: submit to see your scores."));
    } else {
      inner.appendChild(el("div", "intro-head", "Open each topic, answer its three questions, then submit to see your scores!"));
      inner.appendChild(el("div", "intro-line", "Balance sustainability, cost and speed : there's no single right answer."));
      inner.appendChild(el("div", "intro-line",
        `✈️ ${completedCount()} of 6 topics completed&nbsp;&nbsp;&nbsp;[Submit : enabled when all six are done]`));
    }
    box.appendChild(inner);
    const bar = el("button", "wide-bar" + (allCompleted() ? " enabled" : " disabled"), "Submit");
    bar.title = allCompleted() ? "See your scores" : "Complete all topics to submit";
    bar.disabled = !allCompleted();
    bar.onclick = onSubmit;
    box.appendChild(bar);
    c.appendChild(box);
    return;
  }

  if (state.mode === "topic") {
    const ti = state.openTopic;
    const topic = TOPICS[ti];
    const box = el("div", "panel question-panel");
    box.appendChild(el("div", "q-title", topic.title));

    const row = el("div", "q-row");
    topic.questions.forEach((q, qi) => row.appendChild(buildQuestionBox(ti, qi, q)));
    box.appendChild(row);

    const bar = el("button", "wide-bar", "Next");
    bar.onclick = () => onTopicDone(ti);
    box.appendChild(bar);
    c.appendChild(box);
    updateNextBar();
    return;
  }

  if (state.mode === "results") {
    const box = el("div", "panel intro-panel faded-panel");
    const inner = el("div", "intro-text");
    inner.appendChild(el("div", "verdict-label", "Verdict"));
    inner.appendChild(el("div", "verdict", verdictFor(state.result)));
    inner.appendChild(el("div", "persona", `Profile: <b>${personaFor(state.result)}</b>`));
    box.appendChild(inner);
    c.appendChild(box);
  }
}

function buildQuestionBox(ti, qi, q) {
  const box = el("div", "q-box");
  box.appendChild(el("div", "q-label", q.label.replace(/\n/g, "<br>")));

  if (q.type === "slider") {
    const wrap = el("div", "slider-wrap");
    const ends = el("div", "slider-ends");
    ends.appendChild(el("span", "", q.min));
    const valueLab = el("span", "slider-value", "");
    ends.appendChild(valueLab);
    ends.appendChild(el("span", "", q.max));
    wrap.appendChild(ends);

    const input = document.createElement("input");
    input.type = "range"; input.min = 0; input.max = 100; input.step = 1;
    input.value = state.answers[ti][qi];
    input.className = "slider";
    const showVal = () => {
      const v = Number(input.value);
      valueLab.textContent = /^\d+$/.test(q.min) ? v : ""; // numeric sliders show the value
      input.style.setProperty("--fill", v + "%");
    };
    input.oninput = () => { state.answers[ti][qi] = Number(input.value); showVal(); };
    showVal();
    wrap.appendChild(input);
    box.appendChild(wrap);
  } else {
    const group = el("div", "choice-group");
    q.options.forEach(opt => {
      const b = el("button", "choice-btn" + (state.answers[ti][qi] === opt ? " sel" : ""), opt);
      b.onclick = () => {
        state.answers[ti][qi] = opt;
        group.querySelectorAll(".choice-btn").forEach(x => x.classList.remove("sel"));
        b.classList.add("sel");
        updateNextBar();
      };
      group.appendChild(b);
    });
    box.appendChild(group);
  }
  return box;
}

function topicAnswered(ti) {
  return TOPICS[ti].questions.every((q, qi) =>
    q.type === "slider" ? true : state.answers[ti][qi] !== null);
}

function updateNextBar() {
  const bar = $(".question-panel .wide-bar");
  if (!bar) return;
  const ok = topicAnswered(state.openTopic);
  bar.classList.toggle("enabled", ok);
  bar.classList.toggle("disabled", !ok);
  bar.disabled = !ok;
  bar.title = ok ? "" : "Answer all three questions first";
}

/* ---- right sidebar ---- */

function renderSidebar() {
  const top = $("#sidebar-top");
  const bottom = $("#sidebar-bottom");
  top.innerHTML = ""; bottom.innerHTML = "";

  const inPlay = state.mode !== "home";
  const dimmed = state.mode === "topic";           // sidebar fades while answering
  top.classList.toggle("dim", dimmed);
  bottom.classList.toggle("dim", dimmed && state.mode !== "results");

  top.appendChild(el("div", "sb-head", "Impact / Result"));

  SCORE_ROWS.forEach(rowDef => {
    const row = el("div", "score-row" + (inPlay ? "" : " home-row"));
    const rs = state.result ? stateFor(state.result[rowDef.key + "_score"]) : null;
    const img = el("div", "char-circle");
    img.appendChild(Object.assign(document.createElement("img"), {
      src: `assets/${rowDef.img}_${rs ? rs : "blank"}.png`, alt: rowDef.title,
    }));
    const txt = el("div", "score-text");
    txt.appendChild(el("div", "score-title", rowDef.title));
    if (state.mode === "results") {
      txt.appendChild(el("div", "score-phrase", PHRASES[rowDef.img][rs].replace(/\n/g, "<br>")));
    } else if (inPlay) {
      txt.appendChild(el("div", "dots", "<span></span><span></span><span></span>"));
    } else {
      txt.appendChild(el("div", "score-sub", rowDef.sub));
    }
    if (inPlay) { row.appendChild(img); row.appendChild(txt); }
    else { row.appendChild(txt); row.appendChild(img); }
    top.appendChild(row);
  });

  if (state.mode === "home") {
    bottom.appendChild(imgButton("btn-play", () => startPlay(), "play-btn"));
    bottom.appendChild(imgButton("btn-howto", () => openOverlay("howto")));
    bottom.appendChild(imgButton("btn-about", () => openOverlay("about")));
  } else {
    const score = el("div", "score-card" + (state.result ? "" : " dim"),
      state.result ? `Score : ${Math.round(state.result.composite)}/100` : "Score :");
    bottom.appendChild(score);
    const again = el("button", "sb-btn" + (state.result ? "" : " dim"), "Play Again");
    again.disabled = !state.result;
    again.onclick = resetPlay;
    bottom.appendChild(again);
    const brk = el("button", "sb-btn" + (state.result ? "" : " dim"), "View Breakdown");
    brk.disabled = !state.result;
    brk.onclick = () => { renderBreakdown(); openOverlay("breakdown"); };
    bottom.appendChild(brk);
  }
}

function imgButton(cssClass, onclick, extra = "") {
  const b = el("button", "img-btn " + cssClass + (extra ? " " + extra : ""));
  b.onclick = onclick;
  return b;
}

/* ------------------------------ interactions ---------------------------- */

function startPlay() {
  state.mode = "intro";
  render();
}

function resetPlay() {
  state.answers = TOPICS.map(t => t.questions.map(q => (q.type === "slider" ? 0 : null)));
  state.completed = TOPICS.map(() => false);
  state.result = null;
  state.openTopic = null;
  state.mode = "intro";
  render();
}

function openTopic(i) {
  if (state.mode === "home" || state.mode === "results") return;
  state.openTopic = i;
  state.mode = "topic";
  render();
}

function onTopicDone(i) {
  if (!topicAnswered(i)) return;
  state.completed[i] = true;
  state.openTopic = null;
  state.mode = allCompleted() ? "ready" : "intro";
  render();
}

function onSubmit() {
  if (!allCompleted()) return;
  state.result = sim.evaluate(collectChoices());
  state.mode = "results";
  render();
}

/* ------------------------------- overlays ------------------------------- */

function openOverlay(name) { $("#overlay-" + name).classList.add("open"); }
function closeOverlays() { document.querySelectorAll(".overlay").forEach(o => o.classList.remove("open")); }

function renderBreakdown() {
  const r = state.result;
  const host = $("#breakdown-body");
  host.innerHTML = "";

  const dims = el("div", "bd-dims");
  [["Sustainability", r.climate_score], ["ROI", r.financial_score], ["Timeline", r.time_score], ["Composite", r.composite]]
    .forEach(([n, v]) => dims.appendChild(el("div", "bd-dim", `<b>${n}</b><span>${Math.round(v)}/100</span>`)));
  host.appendChild(dims);

  const byId = Object.fromEntries(r.contributions.map(c => [c.metric_id, c]));
  const fmt = x => x === null ? "—" : Math.round(x);
  const grid = el("div", "bd-grid");
  TOPICS.forEach((topic, ti) => {
    const card = el("div", "bd-card");
    card.appendChild(el("div", "bd-title", topic.title));
    topic.questions.forEach((q, qi) => {
      const a = state.answers[ti][qi];
      const shown = q.type === "slider" && /^\d+$/.test(q.min) ? a + "%" :
                    q.special === "policy" ? `${a} (${a < 50 ? "Mandate" : "Incentive"} side)` : a;
      const ids = q.special === "policy" ? ["nextgen_decarb_commitment", "nextgen_policy_instrument"]
                : q.special === "tech" ? ["nextgen_tech_toggle", "nextgen_tech_priority"]
                : [q.metric];
      const line = el("div", "bd-q");
      line.appendChild(el("div", "bd-qlabel", `${q.label.split("\n")[0]} — <b>${shown}</b>`));
      ids.forEach(id => {
        const c = byId[id];
        if (!c) return;
        line.appendChild(el("div", "bd-impact",
          `${c.label}: C ${fmt(c.impact.climate)} · F ${fmt(c.impact.financial)} · T ${fmt(c.impact.time)}`));
      });
      card.appendChild(line);
    });
    grid.appendChild(card);
  });
  host.appendChild(grid);
  host.appendChild(el("div", "bd-note",
    "C = climate, F = financial, T = time (0–100, higher is better; — means not applicable). " +
    "Values come from the ratings in js/modules.js — fill in the TODO ratings to make them meaningful."));
}

/* --------------------------------- boot --------------------------------- */

function buildTiles() {
  const grid = $("#stage");
  TOPICS.forEach((topic, i) => {
    const t = el("div", "tile", "");
    t.id = "tile-" + i;
    const ring = el("div", "tile-ring");
    ring.appendChild(Object.assign(document.createElement("img"), { src: topic.icon, alt: "" }));
    t.appendChild(ring);
    t.appendChild(el("div", "tile-title", topic.title));
    t.appendChild(el("div", "tile-tag", topic.tagline));
    t.appendChild(el("div", "tile-check", "✓"));
    t.onclick = () => { if (state.mode !== "home" && state.mode !== "results") openTopic(i); };
    grid.appendChild(t);
  });
}

function scaleStage() {
  const s = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
  const st = $("#stage");
  st.style.transform = `translate(-50%, -50%) scale(${s})`;
}

window.addEventListener("resize", scaleStage);
document.addEventListener("DOMContentLoaded", () => {
  buildTiles();
  document.querySelectorAll(".overlay .return-btn").forEach(b => b.onclick = closeOverlays);
  scaleStage();
  render();
});
