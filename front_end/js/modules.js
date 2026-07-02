/* ============================================================================
 * modules.js — scenario configuration, mirroring back_end/modules.py
 *
 * ┌─────────────────────────────────────────────────────────────────────────┐
 * │  ✏️  THE ONLY FILE YOU NEED TO EDIT TO TUNE THE GAME.                    │
 * │                                                                         │
 * │  Every rating below is a PLACEHOLDER marked // TODO — exactly like the  │
 * │  # TODO markers in back_end/modules.py. Fill them in the same way:      │
 * │                                                                         │
 * │      rate("High", "Low", "Medium")                                      │
 * │            │       │       └── time      (Very High = fastest payoff)   │
 * │            │       └────────── financial (higher = better financially)  │
 * │            └────────────────── climate   (higher = better for climate)  │
 * │                                                                         │
 * │  Scale: "Very Low" 0 · "Low" 25 · "Medium" 50 · "High" 75 ·             │
 * │         "Very High" 100 — or any raw 0-100 number, or null = N/A.       │
 * │  Keep this file and back_end/modules.py in sync.                        │
 * └─────────────────────────────────────────────────────────────────────────┘
 * ========================================================================== */

"use strict";

// Handy placeholders. Replace per-dimension as you go.
const _BASE = rate("Very Low", "Very Low", "Very Low");   // a 'do nothing' low end
const _TODO = rate("Medium", "Medium", "Medium");          // TODO: set real high-end ratings

const MODULES = [

  // MOD 01 - CO2 cuts - SAF
  new PercentageMetric({
    id: "saf_co2_cuts",
    label: "SAF CO2 Cuts (%)",
    impact_at_0: _BASE,
    impact_at_100: rate("High", "Low", "Medium"),  // TODO
    default_pct: 50.0,
  }),

  // MOD 02 - Time to 100% SAF - SAF
  new PercentageMetric({
    id: "saf_time_to_100",
    label: "Time to 100% SAF (% vol)",
    impact_at_0: _BASE,
    impact_at_100: _TODO,  // TODO
    default_pct: 50.0,
  }),

  // MOD 03 - Willingness to contribute financially - SAF
  new PercentageMetric({
    id: "saf_WTC",
    label: "Willingness to contribute financially (% premium accepted)",
    impact_at_0: _BASE,
    impact_at_100: _TODO,  // TODO
    default_pct: 50.0,
  }),

  // MOD 04 - System maintenance effort - Bio-Sensors
  // Level 1 = Low effort … Level 5 = High effort. Rate what each end MEANS
  // for climate / financial / time in the ratings below.
  new LevelMetric({
    id: "biosensor_maintenance",
    label: "System Maintenance Effort",
    impact_at_min: _BASE,
    impact_at_max: _TODO,  // TODO
  }),

  // MOD 05 - Reliability gain vs. current sensors - Bio-Sensors
  new PercentageMetric({
    id: "biosensor_reliability",
    label: "Reliability Gain vs. Current Sensors (% more reliable)",
    impact_at_0: _BASE,
    impact_at_100: _TODO,  // TODO
    default_pct: 50.0,
  }),

  // MOD 06 - Certification support - Bio-Sensors
  new LevelMetric({
    id: "biosensor_certification",
    label: "Certification Support",
    impact_at_min: _BASE,
    impact_at_max: _TODO,  // TODO
  }),

  // MOD 07 - Data Depth - Digital Passport
  new PercentageMetric({
    id: "passport_digital_depth",
    label: "Digital Depth (%)",
    impact_at_0: _BASE,
    impact_at_100: _TODO,  // TODO
    default_pct: 50.0,
  }),

  // MOD 08 - Regulatory Support - Digital Passport
  new LevelMetric({
    id: "passport_reg_support",
    label: "Regulatory Support",
    impact_at_min: _BASE,
    impact_at_max: _TODO,  // TODO
  }),

  // MOD 09 - Industry Adoption - Materials Digital Passport
  new LevelMetric({
    id: "passport_adoption",
    label: "Industry Adoption",
    impact_at_min: _BASE,
    impact_at_max: _TODO,  // TODO
  }),

  // MOD 10 - Funding payback period — REMOVED: replaced by MOD 19 (funding_split)
  // in the Emission Guide & Eco-Label group, per design decision.

  // MOD 11 - Global Participation (incl. eco-labels) - Emission Guide & Eco-label
  new LevelMetric({
    id: "EGE_participation",
    label: "Global Participation (incl. Eco-labels)",
    impact_at_min: _BASE,
    impact_at_max: _TODO,  // TODO
  }),

  // MOD 12 - Market trust in label - Emission Guide & Eco-label
  new LevelMetric({
    id: "EGE_market_trust",
    label: "Market Trust in Label",
    impact_at_min: _BASE,
    impact_at_max: _TODO,  // TODO
  }),

  // MOD 13 - Sustainability mode shift - Transport of Aircraft Elements
  new PercentageMetric({
    id: "transport_mode_shift",
    label: "Shift to Low Climate, Resource, and Air-Quality Impact Modes (%)",
    impact_at_0: _BASE,
    impact_at_100: _TODO,  // TODO
    default_pct: 50.0,
  }),

  // MOD 14 - Carbon tax - Transport of Aircraft Elements
  new PercentageMetric({
    id: "transport_carbon_tax",
    label: "Carbon Tax (Euro/tonne)",
    impact_at_0: _BASE,
    impact_at_100: _TODO,  // TODO
    default_pct: 50.0,
  }),

  // MOD 15 - Schedule buffer - Transport of Aircraft Elements
  new LevelMetric({
    id: "transport_buffer",
    label: "Schedule Buffer",
    impact_at_min: _BASE,
    impact_at_max: _TODO,  // TODO
  }),

  // MOD 16a - Mandates vs. incentives - Next Gen Roadmapping
  new ChoiceMetric({
    id: "nextgen_policy_instrument",
    label: "Policy instrument",
    options: {
      "None": _BASE,
      "Incentive": _TODO,  // TODO
      "Mandate": _TODO,    // TODO
    },
    default_option: "None",
  }),

  // MOD 16b - Decarbonisation commitment by stakeholders - Next Gen Roadmapping
  new PercentageMetric({
    id: "nextgen_decarb_commitment",
    label: "Decarbonisation Commitment by Stakeholders (%)",
    impact_at_0: _BASE,
    impact_at_100: _TODO,  // TODO
    default_pct: 50.0,
  }),

  // MOD 17a - Priority on New Technology Notification - Next Gen Roadmapping
  new PercentageMetric({
    id: "nextgen_tech_priority",
    label: "Priority on New Technology Notification (%)",
    impact_at_0: _BASE,
    impact_at_100: _TODO,  // TODO
    default_pct: 50.0,
  }),

  // MOD 17b - Technology toggle - Next Gen Roadmapping
  new ChoiceMetric({
    id: "nextgen_tech_toggle",
    label: "Priority on New Technology Notification",
    options: {
      "SAF": _TODO,       // TODO
      "H2": _TODO,        // TODO
      "Electric": _TODO,  // TODO
      "Other": _BASE,
    },
    default_option: "SAF",
  }),

  // MOD 18 - Actions needed by stakeholder - Next Gen Roadmapping
  new ChoiceMetric({
    id: "nextgen_actions",
    label: "Actions Needed by Stakeholder",
    options: {
      "Airlines": _TODO,     // TODO
      "OEMs": _TODO,         // TODO
      "Government": _TODO,   // TODO
      "Other": _BASE,
    },
    default_option: "Airlines",
  }),

  // MOD 19 - Funding by Stakeholder (replaces MOD 10 in Emission Guide & Eco-Label)
  // Shares must sum to 100%. Climate-neutral: only financial & time are rated,
  // so climate is omitted (null / not applicable) for every group. TODO: tune ratings.
  new AllocationMetric({
    id: "funding_split",
    label: "Who pays for the transition",
    groups: {
      "Government": rate(null, "Medium", "High"),   // TODO
      "Private":    rate(null, "High",   "Low"),    // TODO
      "NGO":        rate(null, "Low",    "Medium"), // TODO
      "Public":     rate(null, "Low",    "Medium"), // TODO
    },
    default_allocation: { "Government": 25, "Private": 25, "NGO": 25, "Public": 25 },
  }),
];

// Weights are equal thirds by default — retune here.  // TODO: retune
function buildSimulation() {
  return new Simulation(MODULES, new ScoreWeights(1.0, 1.0, 1.0));
}
