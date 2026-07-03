/* ============================================================================
 * modules.js — scenario configuration, mirroring back_end/modules.py
 *
 * ┌─────────────────────────────────────────────────────────────────────────┐
 * │  ✏️  THE ONLY FILE YOU NEED TO EDIT TO TUNE THE GAME.                    │
 * │                                                                         │
 * │  Ratings use rate(climate, financial, time) — POSITIONAL, unlike the    │
 * │  Python file which allows keywords. Same values, different syntax:      │
 * │                                                                         │
 * │      Python:  impact_at_0=rate(climate="Low", financial="Very High")    │
 * │      JS:      impact_at_0: rate("Low", "Very High"),                    │
 * │                                                                         │
 * │  Order is always climate, financial, time. Leave a trailing dimension   │
 * │  out (or pass null) to mark it "not applicable".                        │
 * │  Scale: "Very Low" 0 · "Low" 25 · "Medium" 50 · "High" 75 ·             │
 * │         "Very High" 100 — or any raw 0-100 number.                      │
 * │  Note the ':' after each property name — '=' breaks JavaScript.         │
 * │  Keep this file and back_end/modules.py in sync.                        │
 * └─────────────────────────────────────────────────────────────────────────┘
 * ========================================================================== */

"use strict";

// Baseline used by the "None"/"Other" options.
const _BASE = rate("Very Low", "Very Low", "Very Low");   // a 'do nothing' low end

const MODULES = [

  // MOD 01 - CO2 cuts - SAF
  new PercentageMetric({
    id: "saf_co2_cuts",
    label: "SAF CO2 Cuts (%)",
    impact_at_0: rate("Low", "Very High"),    // time not applicable
    impact_at_100: rate("Very High", "Medium"),  // time not applicable
    default_pct: 50.0,
  }),

  // MOD 02 - Time to 100% SAF - SAF
  new PercentageMetric({
    id: "saf_time_to_100",
    label: "Time to 100% SAF (% vol)",
    impact_at_0: rate("Very Low", "Medium", "Very Low"),
    impact_at_100: rate("Very High", "Medium", "Very High"),
    default_pct: 50.0,
  }),

  // MOD 03 - Willingness to contribute financially - SAF
  new PercentageMetric({
    id: "saf_WTC",
    label: "Willingness to contribute financially (% premium accepted)",
    impact_at_0: rate("Low", "Low"),          // time not applicable
    impact_at_100: rate("High", "High"),      // time not applicable
    default_pct: 50.0,
  }),

  // MOD 04 - System maintenance effort - Bio-Sensors
  // Level 1 = Low effort … Level 5 = High effort. Rate what each end MEANS
  // for climate / financial / time in the ratings below.
  new LevelMetric({
    id: "biosensor_maintenance",
    label: "System Maintenance Effort",
    impact_at_min: rate("Very Low", "Low"),   // time not applicable
    impact_at_max: rate("Very High", "High"), // time not applicable
  }),

  // MOD 05 - Reliability gain vs. current sensors - Bio-Sensors
  new PercentageMetric({
    id: "biosensor_reliability",
    label: "Reliability Gain vs. Current Sensors (% more reliable)",
    impact_at_0: rate("Very Low", "Very Low", "High"),
    impact_at_100: rate("Very High", "Very High", "Low"),
    default_pct: 50.0,
  }),

  // MOD 06 - Certification support - Bio-Sensors
  new LevelMetric({
    id: "biosensor_certification",
    label: "Certification Support",
    impact_at_min: rate("Very Low", null, "Very Low"),   // financial not applicable
    impact_at_max: rate("Very High", null, "Very High"), // financial not applicable
  }),

  // MOD 07 - Data Depth - Digital Passport
  new PercentageMetric({
    id: "passport_digital_depth",
    label: "Digital Depth (%)",
    impact_at_0: rate("Low", "High", "Low"),
    impact_at_100: rate("High", "Medium", "High"),
    default_pct: 50.0,
  }),

  // MOD 08 - Regulatory Support - Digital Passport
  new LevelMetric({
    id: "passport_reg_support",
    label: "Regulatory Support",
    impact_at_min: rate("Medium", "Very Low", "Very Low"),
    impact_at_max: rate("High", "Very High", "Very High"),
  }),

  // MOD 09 - Industry Adoption - Materials Digital Passport
  new LevelMetric({
    id: "passport_adoption",
    label: "Industry Adoption",
    impact_at_min: rate("Low", "Low", "Very Low"),
    impact_at_max: rate("High", "High", "Very High"),
  }),

  // MOD 10 - Funding payback period — REMOVED: replaced by MOD 19 (funding_split)
  // in the Emission Guide & Eco-Label group, per design decision.

  // MOD 11 - Global Participation (incl. eco-labels) - Emission Guide & Eco-label
  new LevelMetric({
    id: "EGE_participation",
    label: "Global Participation (incl. Eco-labels)",
    impact_at_min: rate("Very Low", "Very Low", "Very High"),
    impact_at_max: rate("Very High", "Very High", "Very Low"),
  }),

  // MOD 12 - Market trust in label - Emission Guide & Eco-label
  new LevelMetric({
    id: "EGE_market_trust",
    label: "Market Trust in Label",
    impact_at_min: rate("Low", null, "Very Low"),   // financial not applicable
    impact_at_max: rate("High", null, "Very High"), // financial not applicable
  }),

  // MOD 13 - Sustainability mode shift - Transport of Aircraft Elements
  new PercentageMetric({
    id: "transport_mode_shift",
    label: "Shift to Low Climate, Resource, and Air-Quality Impact Modes (%)",
    impact_at_0: rate("Very Low", "Very Low", "Very Low"),
    impact_at_100: rate("Very High", "Very High", "Very High"),
    default_pct: 50.0,
  }),

  // MOD 14 - Carbon tax - Transport of Aircraft Elements
  new PercentageMetric({
    id: "transport_carbon_tax",
    label: "Carbon Tax (%)",
    impact_at_0: rate("Low", "High", "Very High"),
    impact_at_100: rate("High", "Low", "Very Low"),
    default_pct: 50.0,
  }),

  // MOD 15 - Schedule buffer - Transport of Aircraft Elements
  new LevelMetric({
    id: "transport_buffer",
    label: "Schedule Buffer",
    impact_at_min: rate("Very Low", null, "High"),  // financial not applicable
    impact_at_max: rate("High", null, "Low"),       // financial not applicable
  }),

  // MOD 16a - Mandates vs. incentives - Next Gen Roadmapping
  new ChoiceMetric({
    id: "nextgen_policy_instrument",
    label: "Policy instrument",
    options: {
      "None": _BASE,
      "Incentive": rate("Medium", "Low", "High"),
      "Mandate": rate("High", "Medium", "Low"),
    },
    default_option: "None",
  }),

  // MOD 16b - Decarbonisation commitment by stakeholders - Next Gen Roadmapping
  new PercentageMetric({
    id: "nextgen_decarb_commitment",
    label: "Decarbonisation Commitment by Stakeholders (%)",
    impact_at_0: rate("Very Low", "High"),      // time not applicable
    impact_at_100: rate("Very High", "Medium"), // time not applicable
    default_pct: 50.0,
  }),

  // MOD 17a - Priority on New Technology Notification - Next Gen Roadmapping
  new PercentageMetric({
    id: "nextgen_tech_priority",
    label: "Priority on New Technology Notification (%)",
    impact_at_0: rate("Very Low", "Very High", "Very High"),
    impact_at_100: rate("Very High", "Very Low", "Very Low"),
    default_pct: 50.0,
  }),

  // MOD 17b - Technology toggle - Next Gen Roadmapping
  new ChoiceMetric({
    id: "nextgen_tech_toggle",
    label: "Priority on New Technology Notification",
    options: {
      "SAF": rate("Medium", "High", "High"),
      "H2": rate("Very High", "Medium", "Low"),
      "Electric": rate("Very High", "Medium", "Low"),
      "Other": _BASE,
    },
    default_option: "SAF",
  }),

  // MOD 18 - Actions needed by stakeholder - Next Gen Roadmapping
  new ChoiceMetric({
    id: "nextgen_actions",
    label: "Actions Needed by Stakeholder",
    options: {
      "Airlines": rate("Low", "Low", "High"),
      "OEMs": rate("High", "Low", "High"),
      "Government": rate("High", "High", "Low"),
      "Other": _BASE,
    },
    default_option: "Airlines",
  }),

  // MOD 19 - Funding by Stakeholder - Extra
  // Shares must sum to 100%. Climate-neutral: only financial & time are rated,
  // so climate is omitted (null / not applicable) for every group.
  new AllocationMetric({
    id: "funding_split",
    label: "Who pays for the transition",
    groups: {
      "Government": rate(null, "Medium", "High"),
      "Private":    rate(null, "High",   "Low"),
      "NGO":        rate(null, "Low",    "Medium"),
      "Public":     rate(null, "Low",    "Medium"),
    },
    default_allocation: { "Government": 25, "Private": 25, "NGO": 25, "Public": 25 },
  }),
];

// Weights are equal thirds by default — retune here.  // TODO: retune
function buildSimulation() {
  return new Simulation(MODULES, new ScoreWeights(1.0, 1.0, 1.0));
}
