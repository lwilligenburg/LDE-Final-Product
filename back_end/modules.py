"""
Scenario configuration — the Flight Deck 2050 modules as metric definitions.

Impacts are now RATINGS (Very Low / Low / Medium / High / Very High) on three
dimensions, built with ``rate(...)``:

    rate(climate="High", financial="Medium", time="Low")

Rules of thumb while filling this in:
  * Higher is always better, incl. time (Very High time = fastest to deliver).
  * Omit a dimension to mark it "not applicable" (skipped in scoring) — see the
    funding module, which is climate-neutral.
  * Sliders (Percentage / Level) interpolate between their two rated ends, so you
    only rate the low end and the high end.

Every rating below is a PLACEHOLDER marked # TODO — replace with your judgement.
"""

from __future__ import annotations

from .impacts import rate
from .metrics import AllocationMetric, ChoiceMetric, LevelMetric, PercentageMetric
from .scoring import ScoreWeights

# Handy placeholders. Replace per-dimension as you go.
_BASE = rate("Very Low", "Very Low", "Very Low")            # a 'do nothing' low end
_TODO = rate("Medium", "Medium", "Medium")                  # TODO: set real high-end ratings

MODULES: list = [

    # MOD 01 - CO2 cuts - SAF
    PercentageMetric(
        id="saf_co2_cuts",
        label="SAF CO2 Cuts (%)",
        impact_at_0=_BASE,
        impact_at_100=rate(climate="High", financial="Low", time="Medium"),  # TODO
        default_pct=50.0,
    ),

    # MOD 02 - Time to 100% SAF - SAF
    PercentageMetric(
        id="saf_time_to_100",
        label="Time to 100% SAF (% vol)",
        impact_at_0=_BASE,
        impact_at_100=_TODO,  # TODO
        default_pct=50.0,
    ),

    # MOD 03 - Willingness to contribute financially - SAF
    PercentageMetric(
        id="saf_WTC",
        label="Willingness to contribute financially (% premium accepted)",
        impact_at_0=_BASE,
        impact_at_100=_TODO,  # TODO
        default_pct=50.0,
    ),

    # MOD 04 - PLACEHOLDER
    # MOD 05 - PLACEHOLDER
    # MOD 06 - PLACEHOLDER

    # MOD 07 - Data Depth - Digital Passport
    PercentageMetric(
        id="passport_digital_depth",
        label="Digital Depth (%)",
        impact_at_0=_BASE,
        impact_at_100=_TODO,  # TODO
        default_pct=50.0,
    ),

    # MOD 08 - Regulatory Support - Digital Passport
    LevelMetric(
        id="passport_reg_support",
        label="Regulatory Support",
        impact_at_min=_BASE,
        impact_at_max=_TODO,  # TODO
    ),

    # MOD 09 - Industry Adoption - Materials Digital Passport
    LevelMetric(
        id="passport_adoption",
        label="Industry Adoption",
        impact_at_min=_BASE,
        impact_at_max=_TODO,  # TODO
    ),

    # MOD 10 - Funding payback period - Emission Guide & Eco-label
    LevelMetric(
        id="EGE_payback_period",
        label="Funding Payback Period (years)",
        impact_at_min=_BASE,
        impact_at_max=_TODO,  # TODO
    ),

    # MOD 11 - Global Participation (incl. eco-labels) - Emission Guide & Eco-label
    LevelMetric(
        id="EGE_participation",
        label="Global Participation (incl. Eco-labels)",
        impact_at_min=_BASE,
        impact_at_max=_TODO,  # TODO
    ),

    # MOD 12 - Market trust in label - Emission Guide & Eco-label
    LevelMetric(
        id="EGE_market_trust",
        label="Market Trust in Label",
        impact_at_min=_BASE,
        impact_at_max=_TODO,  # TODO
    ),

    # MOD 13 - Sustainability mode shift - Transport of Aircraft Elements
    PercentageMetric(
        id="transport_mode_shift",
        label="Shift to Low Climate, Resource, and Air-Quality Impact Modes (%)",
        impact_at_0=_BASE,
        impact_at_100=_TODO,  # TODO
        default_pct=50.0,
    ),

    # MOD 14 - Carbon tax - Transport of Aircraft Elements
    PercentageMetric(
        id="transport_carbon_tax",
        label="Carbon Tax (%)",
        impact_at_0=_BASE,
        impact_at_100=_TODO,  # TODO
        default_pct=50.0,
    ),

    # MOD 15 - Schedule buffer - Transport of Aircraft Elements
    LevelMetric(
        id="transport_buffer",
        label="Schedule Buffer",
        impact_at_min=_BASE,
        impact_at_max=_TODO,  # TODO
    ),

    # MOD 16a - Mandates vs. incentives - Next Gen Roadmapping
    ChoiceMetric(
        id="nextgen_policy_instrument",
        label="Policy instrument",
        options={
            "None": _BASE,
            "Incentive": _TODO,  # TODO
            "Mandate": _TODO,    # TODO
        },
        default_option="None",
    ),

    # MOD 16b - Decarbonisation commitment by stakeholders - Next Gen Roadmapping
    PercentageMetric(
        id="nextgen_decarb_commitment",
        label="Decarbonisation Commitment by Stakeholders (%)",
        impact_at_0=_BASE,
        impact_at_100=_TODO,  # TODO
        default_pct=50.0,
    ),

    # MOD 17a - Priority on New Technology Notification - Next Gen Roadmapping
    PercentageMetric(
        id="nextgen_tech_priority",
        label="Priority on New Technology Notification (%)",
        impact_at_0=_BASE,
        impact_at_100=_TODO,  # TODO
        default_pct=50.0,
    ),

    # MOD 17b - Technology toggle - Next Gen Roadmapping
    ChoiceMetric(
        id="nextgen_tech_toggle",
        label="Priority on New Technology Notification",
        options={
            "SAF": _TODO,       # TODO
            "H2": _TODO,        # TODO
            "Electric": _TODO,  # TODO
            "Other": _BASE,
        },
        default_option="SAF",
    ),

    # MOD 18 - Actions needed by stakeholder - Next Gen Roadmapping
    ChoiceMetric(
        id="nextgen_actions",
        label="Actions Needed by Stakeholder",
        options={
            "Airlines": _TODO,     # TODO
            "OEMs": _TODO,         # TODO
            "Government": _TODO,   # TODO
            "Other": _BASE,
        },
        default_option="Airlines",
    ),

    # MOD 19 - Funding by Stakeholder - Extra
    # Shares must sum to 100%. Climate-neutral: only financial & time are rated,
    # so climate is omitted (not applicable) for every group. TODO: tune ratings.
    AllocationMetric(
        id="funding_split",
        label="Who pays for the transition",
        groups={
            "Government": rate(financial="Medium", time="High"),    # TODO
            "Private": rate(financial="High", time="Low"),          # TODO
            "NGO": rate(financial="Low", time="Medium"),            # TODO
            "Public": rate(financial="Low", time="Medium"),         # TODO
        },
        default_allocation={"Government": 25, "Private": 25, "NGO": 25, "Public": 25},
    ),
]


def build_simulation():
    """Return a ready-to-use :class:`~back_end.engine.Simulation` for the board.

    Weights are equal thirds by default — retune in the ScoreWeights below.
    """
    from .engine import Simulation  # local import to avoid a cycle

    return Simulation(
        metrics=list(MODULES),
        weights=ScoreWeights(climate=1.0, financial=1.0, time=1.0),  # TODO: retune
    )
