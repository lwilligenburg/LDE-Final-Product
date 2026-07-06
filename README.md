# Sustainable Aviation: Wings of the Future

A scenario game for the LDE Thesis Labs programme (also referred to as
*Flight Deck 2050* in the backend). Players open six sustainable-aviation
topics, set sliders and choices on nineteen underlying modules, and receive
three scores — **Sustainability** (climate), **ROI** (financial) and
**Timeline Impact** (time) — plus a composite, a verdict and a per-metric
breakdown.

The project has two halves that implement the *same* model:

* `back_end/` — a pure-Python engine, the **engine of record**. Use it for
  analysis, testing and thesis documentation.
* `front_end/` — the playable game: pure HTML/CSS/JS with a 1:1 JavaScript
  port of the engine. No build step, no server, no dependencies.

The two are verified to produce identical scores to 6 decimal places for
identical inputs.

## Repo layout

```
LDE Product/
├── back_end/              # Python engine (engine of record)
│   ├── impacts.py         #   rating scale + Impact vectors (climate/financial/time)
│   ├── metrics.py         #   control types: Percentage, Choice, Level, Allocation
│   ├── scoring.py         #   dimension averaging + weighted composite
│   ├── engine.py          #   Simulation: choices -> scores + per-metric breakdown
│   └── modules.py         #   the 19 modules + their ratings  ← edit ratings here
├── front_end/             # the playable game
│   ├── index.html         #   open this to play
│   ├── css/style.css
│   ├── js/engine.js       #   1:1 JS port of back_end
│   ├── js/modules.js      #   1:1 mirror of back_end/modules.py  ← keep in sync!
│   ├── js/explanations.js #   texts behind the (?) help bubbles
│   ├── js/app.js          #   UI + question→metric wiring
│   └── assets/            #   icons, characters, buttons from the Figma design
├── demo.py                # runnable end-to-end backend demo
├── run_tests_nodeps.py    # backend test suite (no pytest needed)
└── test_engine.py         # same suite, pytest style
```

## Quick start

**Play the game:** double-click `front_end/index.html` (any modern
browser). It renders on a fixed 1920×1080 stage — the Figma frame — and
scales to fit any screen or beamer.

**Run the backend:**

```bash
python demo.py               # end-to-end demo
python run_tests_nodeps.py   # 16 mechanics tests, no dependencies
```

```python
from back_end import build_simulation

sim = build_simulation()
result = sim.evaluate({"saf_co2_cuts": 80, "transport_buffer": 5})
print(result.summary())
print(result.composite)      # 0-100
```

## The model

Every module maps a player choice to an **Impact**: a rating per dimension
(climate, financial, time) on a 5-point scale — Very Low 0 · Low 25 ·
Medium 50 · High 75 · Very High 100 — or `None`/`null` when a dimension is
not applicable. Four control types:

| Type | Example in the game | Value passed |
|------|--------------------|--------------|
| `PercentageMetric` | CO₂ cuts 0–100 % slider | number `0`–`100` (interpolates between the two endpoint ratings) |
| `LevelMetric` | Low / Medium / High buttons | int `1`–`5` (UI buttons map to 1 / 3 / 5) |
| `ChoiceMetric` | Mandate / Incentive · SAF / H2 / Electric | one option string |
| `AllocationMetric` | Who funds it | shares per group summing to 100 % |

Each dimension score is the average of all applicable metric impacts
(N/A skipped); the composite combines the three with configurable weights
(default: equal thirds, in `build_simulation()` / `buildSimulation()`).

**Keeping the two sides in sync:** if you edit ratings, edit
`back_end/modules.py` and `front_end/js/modules.js` together — they mirror
each other module for module. Mind the syntax difference: `rate()` takes
keyword arguments in Python but *positional* arguments in JS (order:
climate, financial, time; `null` skips a dimension).

## Question → module wiring

| Topic | Question | Metric (module) |
|---|---|---|
| SAF | CO₂ cuts % · Time to 100% SAF · WTC | `saf_co2_cuts` · `saf_time_to_100` · `saf_WTC` (MOD 01–03) |
| Bio-Sensors | Maintenance effort · Reliability gain · Certification | `biosensor_maintenance` · `biosensor_reliability` · `biosensor_certification` (MOD 04–06) |
| Digital Product Passport | Data depth · Regulatory Support · Industry Adoption | `passport_digital_depth` · `passport_reg_support` · `passport_adoption` (MOD 07–09) |
| Emission Guide & Eco-Label | Who funds it · Global Participation · Market Trust | `funding_split` (MOD 19, replaces MOD 10) · `EGE_participation` (MOD 11) · `EGE_market_trust` (MOD 12) |
| Green Transport | Mode shift % · Carbon tax · Schedule Buffer | `transport_mode_shift` · `transport_carbon_tax` · `transport_buffer` (MOD 13–15) |
| Next-Gen Roadmapping | see below | MOD 16a/16b · 17a/17b · 18 |

The Next-Gen panel has two **combo boxes**, each driving two modules:

* Box 1 — Mandate/Incentive buttons → `nextgen_policy_instrument`
  (MOD 16a) + a 0–100 slider → `nextgen_decarb_commitment` (MOD 16b).
* Box 2 — a 0–100 slider → `nextgen_tech_priority` (MOD 17a) +
  SAF/H2/Electric buttons → `nextgen_tech_toggle` (MOD 17b).
* Box 3 — Airline/OEM/Government → `nextgen_actions` (MOD 18, mapped to
  the engine's Airlines/OEMs/Government options).

Other special mappings (all in `collectChoices()` in `front_end/js/app.js`):

* **Low / Medium / High buttons** → `LevelMetric` levels **1 / 3 / 5**.
* **Who funds it** turns the single choice into a MOD 19 allocation: the
  chosen group gets 100 %, the others 0 % (NGO has no button, stays 0).
* **Global Participation slider** (0–100) maps to `EGE_participation`
  levels 1–5.

## Ratings & balance (current state)

All ratings are filled in and balance-checked against the UI-reachable
choice space:

* Attainable ranges: climate 17–88, financial 25–81, time 11–89
  (face thresholds: ≥67 happy, ≥34 neutral, below sad — constants at the
  top of `front_end/js/app.js`).
* Best possible composite ≈ 74; a triple-happy outcome is achievable but
  demanding.
* Archetype strategies: all-out green ≈ 88/60/58, all-out profit ≈
  49/81/48, all-out speed ≈ 42/56/89.
* No anti-sustainability optima: pushing CO₂ cuts, decarbonisation
  commitment, etc. is net-positive; the carbon tax is a deliberate
  climate-versus-cost-and-speed sacrifice.
* Known (accepted) quirks: *Airlines* (MOD 18) and *Public* funding
  (MOD 19) are strictly dominated options, and H2/Electric share
  identical ratings.

## The game

* **Home** — title panel, six topic tiles, Impact/Result sidebar, Play /
  How to Play / About.
* **About** — the six thesis cards from the design.
* **How to Play** — instructions plus the score legend.
* **Play** — click a tile, answer its questions (button questions must all
  be answered before **Next** unlocks); a ✓ marks completed topics;
  **Submit** unlocks at 6/6.
* **Results** — the Earth / aircraft / stopwatch characters change
  expression per score, composite `Score : NN/100`, verdict + player
  profile (Visionary / Pragmatist / Sprinter / Balanced — rule-based in
  `verdictFor()` / `personaFor()`), **Play Again** and **View Breakdown**.
* **Breakdown** — the three dimension scores, the composite, and every
  answer with its climate/financial/time contribution.

**Help bubbles:** every question box and every Breakdown metric line has a
(?) button. Texts live in `front_end/js/explanations.js`, one entry per
metric with `question` (shown while playing) and `impact` (shown in the
Breakdown) fields; an empty string hides that button (currently the case
where the source document says N/A: MOD 11 and 12 entirely, plus the
metric texts of MOD 01, 02 and the funding choice).

## Credits
Sudharshan SS and Luke Willigenburg