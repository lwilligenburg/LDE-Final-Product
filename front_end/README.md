# Sustainable Aviation: Wings of the Future — Front End

The complete working application for the LDE thesis prototype. Pure
HTML/CSS/JS — **no build step, no server, no dependencies**.

## Run it

Double-click `index.html` (or open it in any modern browser). That's it.

The app renders on a fixed 1920×1080 stage (the Figma frame) and scales to
fit any screen or beamer.

## How it fits the repo

```
LDE Product/
├── back_end/          ← your Python engine (engine of record)
│   └── modules.py     ← UPDATED: MOD 04-06 added (Bio-Sensors), MOD 10 removed
└── front_end/         ← this folder
    ├── index.html
    ├── css/style.css
    ├── js/engine.js   ← 1:1 JS port of back_end (impacts/metrics/scoring/engine)
    ├── js/modules.js  ← 1:1 mirror of back_end/modules.py  ✏️ EDIT RATINGS HERE
    ├── js/app.js      ← UI + question→metric wiring
    └── assets/        ← icons, characters, buttons from the Figma design
```

The JS engine has been verified against the Python backend: identical inputs
produce identical scores to 6 decimal places.

## ✏️ Filling in the ratings (the TODOs)

All ratings are placeholders (`_BASE` = all Very Low, `_TODO` = all Medium),
so right now every playthrough scores in a compressed band and you will
mostly see the neutral/sad characters. **This is expected.** To make the
trade-offs real:

1. Open `js/modules.js` — the header explains the `rate(climate, financial,
   time)` format and the 5-point scale.
2. Replace every `// TODO` rating with your judgement.
3. Make the *same* edits in `back_end/modules.py` (the files mirror each
   other module for module), or send the filled Python file back and mirror
   it once.

Score weights (equal thirds) live at the bottom of `js/modules.js` in
`buildSimulation()` and in `back_end/modules.py`.

## Question → module wiring

| Topic | Question | Metric (module) |
|---|---|---|
| SAF | CO₂ cuts % · Time to 100% SAF · WTC | `saf_co2_cuts` · `saf_time_to_100` · `saf_WTC` (MOD 01–03) |
| Bio-Sensors | Maintenance effort · Reliability gain · Certification | `biosensor_maintenance` · `biosensor_reliability` · `biosensor_certification` (MOD 04–06, new) |
| Digital Product Passport | Data depth · Regulatory Support · Industry Adoption | `passport_digital_depth` · `passport_reg_support` · `passport_adoption` (MOD 07–09) |
| Emission Guide & Eco-Label | Who funds it · Global Participation · Market Trust | `funding_split` (MOD 19, replaces MOD 10) · `EGE_participation` (MOD 11) · `EGE_market_trust` (MOD 12) |
| Green Transport | Mode shift % · Carbon tax · Schedule Buffer | `transport_mode_shift` · `transport_carbon_tax` · `transport_buffer` (MOD 13–15) |
| Next-Gen Roadmapping | Mandate↔Incentive slider · Fuel priority · Who's actions | see below (MOD 16a–18) |

Special mappings (documented in `js/app.js`):

* **Low / Medium / High buttons** → `LevelMetric` levels **1 / 3 / 5**.
* **Mandate↔Incentive slider** drives two modules at once:
  `nextgen_decarb_commitment` gets the raw 0–100 value, and
  `nextgen_policy_instrument` becomes **Mandate** below 50, **Incentive** at
  50 or above.
* **Fuel priority (SAF/H2/Electric)** sets `nextgen_tech_toggle` and puts
  `nextgen_tech_priority` at 100 (full priority to the chosen tech — tune in
  `collectChoices()` if you want different behaviour).
* **Who funds it** turns the single choice into a MOD 19 allocation: the
  chosen group gets 100 %, the others 0 % (NGO stays 0 — it has no button in
  the design).
* **Global Participation slider** (0–100) maps to `EGE_participation`
  levels 1–5.

## Character thresholds & verdict

Dimension score ≥ 67 → happy, ≥ 34 → neutral, below → sad. Change
`THRESHOLD_HIGH` / `THRESHOLD_MEDIUM` at the top of `js/app.js`.

The one-line verdict and the Visionary / Pragmatist / Sprinter / Balanced
profile are rule-based — see `verdictFor()` and `personaFor()` in
`js/app.js`.

## Screens

* **Home** — title panel, six topic tiles, Impact/Result sidebar, Play /
  How to Play / About.
* **About** — the six thesis cards from the design (image assets).
* **How to Play** — step-by-step instructions plus the score legend.
* **Play** — click a tile, answer its three questions, press **Next**;
  a ✓ marks completed topics; **Submit** unlocks at 6/6.
* **Results** — characters change expression per score, composite
  `Score : NN/100`, verdict + profile in the centre panel, **Play Again**
  and **View Breakdown**.
* **Breakdown** — the three dimension scores, the composite, and every
  answer with its climate/financial/time contribution.
