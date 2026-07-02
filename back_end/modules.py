"""
Scenario configuration — the nine Flight Deck 2050 modules as metric definitions.

This is the ONE file you edit to plug in your thesis numbers. Every impact value
here is a placeholder set to 0.0 and marked ``# TODO``. The mechanics in the rest
of the package are complete and tested; only these coefficients are missing.

How to fill it in
-----------------
Each module below is the "Ambition Level" 1-5 slider from the board. The engine
interpolates linearly from level 1 (``impact_at_min``) to level 5
(``impact_at_max``). So for each module you mainly need to answer:

    "At FULL ambition (level 5), how much CO2e does this save, what does it cost,
     what does it return, and how many years until it delivers / breaks even?"

Fill those into ``impact_at_max``. Level 1 is left as a near-baseline zero, which
is usually right for 'minimal ambition'; adjust ``impact_at_min`` if not. If a
level in the middle behaves oddly (not on the straight line), pin it explicitly
via ``per_level={3: Impact(...)}``.

Units (see impacts.py): co2_saved_kt = kt CO2e/yr, cost/returns = M EUR,
years = years to deliver / break even.

At the bottom, ``EXTRA_EXAMPLE_METRICS`` shows how to encode the OTHER control
types you mentioned — a 0-100% slider and discrete dropdowns
(Mandate/Incentive, SAF/H2/Electric/Other) — in case some modules use those
instead of the 1-5 ambition slider.
"""

from __future__ import annotations

from .impacts import Impact
from .metrics import ChoiceMetric, LevelMetric, PercentageMetric
from .scoring import Normalization, ScoreWeights

# ---------------------------------------------------------------------------
# The nine ambition sliders from the board. Endpoints (from the screenshot) are
# noted in each comment. Replace every 0.0 marked TODO with your figures.
# ---------------------------------------------------------------------------

# PERCENTAGE METRIC
# A continuous 0-100% slider
# Impact interpolates from 0% to 100%; 
# Everything scales from nothing at 0% up to the level you set for 100%.

# LEVEL METRIC
# A metric for a discrete set of options, e.g. Low / Med / High

# CHOICE METRIC
# Pick: An unordered discrete pick — e.g. the policy instrument used to drive change.
# Dropdown: A technology-choice dropdown — e.g. SAF / H2 / Electric / Other.

# ---------------------------------------------------------------------------

MODULES: list[LevelMetric, PercentageMetric, ChoiceMetric] = [

    # MOD 01 - CO2 cuts - SAF
    PercentageMetric(
        id="saf_co2_cuts",
        label="SAF CO2 Cuts (%)",
        impact_at_0=Impact(),
        impact_at_100=Impact(
            co2_saved_kt=0.0,   # TODO: CO2e avoided at a 100% blend ceiling
            cost_meur=0.0,      # TODO
            returns_meur=0.0,   # TODO
            years=0.0,          # TODO
        ),
        default_pct=50.0,       # board shows the cuts at 50%
    ),

    # MOD 02 - Time to 100% SAF  - SAF
    PercentageMetric(
        id="saf_time_to_100",
        label="Time to 100% SAF (% vol)",
        impact_at_0=Impact(),
        impact_at_100=Impact(
            co2_saved_kt=0.0,   # TODO: CO2e avoided at a 100% blend ceiling
            cost_meur=0.0,      # TODO
            returns_meur=0.0,   # TODO
            years=0.0,          # TODO
        ),
        default_pct=50.0,       # board shows the cuts at 50%
    ),

    # MOD 03 - Willngness to contribute financially  - SAF
    PercentageMetric(
        id="saf_WTC",
        label="Willingness to contribute financially (% premium accepted)",
        impact_at_0=Impact(),
        impact_at_100=Impact(
            co2_saved_kt=0.0,   # TODO: CO2e avoided at a 100% blend ceiling
            cost_meur=0.0,      # TODO
            returns_meur=0.0,   # TODO
            years=0.0,          # TODO
        ),
        default_pct=50.0,       # board shows the cuts at 50%
    ),

    # MOD 04 - PLACEHOLDER
    # MOD 05 - PLACEHOLDER
    # MOD 06 - PLACEHOLDER

    # MOD 07 - Data Depth  - Digital Passport
    PercentageMetric(
        id="passport_digital_depth",
        label="Digital Deptth (%)",
        impact_at_0=Impact(),
        impact_at_100=Impact(
            co2_saved_kt=0.0,   # TODO: CO2e avoided at a 100% blend ceiling
            cost_meur=0.0,      # TODO
            returns_meur=0.0,   # TODO
            years=0.0,          # TODO
        ),
        default_pct=50.0,       # board shows the cuts at 50%
    ),
    
    # MOD 08 - Regulatory Support - Digital Passport
    LevelMetric(
        id="passport_reg_support",
        label="Regulatory Support",
        impact_at_min=Impact(),  # level 1 (Pilot): baseline
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO: CO2e avoided at EU-Mandate level
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO: years to deliver / break even
        ),
    ),

    # MOD 09 - Industry Adoption - Materials Digital Passport
    LevelMetric(
        id="passport_adoption",
        label="Industry Adoption",
        impact_at_min=Impact(),  # level 1 (Pilot): baseline
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO: CO2e avoided at EU-Mandate level
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO: years to deliver / break even
        ),
    ),

    # MOD 10 - Funding payback period - Emission Guide & Eco-label
    LevelMetric(
        id="EGE_payback_period",
        label="Funding Payback Period (years)",
        impact_at_min=Impact(),  # level 1 (Pilot): baseline
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO: CO2e avoided at EU-Mandate level
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO: years to deliver / break even
        ),
    ),

    # MOD 11 - Global Participation (incl. eco-labels) - Emission Guide & Eco-label
    LevelMetric(
        id="EGE_participation",
        label="Global Participation (incl. Eco-labels)",
        impact_at_min=Impact(),  # level 1 (Pilot): baseline
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO: CO2e avoided at EU-Mandate level
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO: years to deliver / break even
        ),
    ),

    # MOD 12 - Market trust in label - Emission Guide & Eco-label
    LevelMetric(
        id="EGE_market_trust",
        label="Market Trust in Label",
        impact_at_min=Impact(),  # level 1 (Pilot): baseline
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO: CO2e avoided at EU-Mandate level
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO: years to deliver / break even
        ),
    ),

    # MOD 13 - Sustainability mode shift  - Transport of Aircraft Elements
    PercentageMetric(
        id="transport_mode_shift",
        label="Shift to Low Climate, Resource, and Air-Quality Impact Modes (%)",
        impact_at_0=Impact(),
        impact_at_100=Impact(
            co2_saved_kt=0.0,   # TODO: CO2e avoided at a 100% blend ceiling
            cost_meur=0.0,      # TODO
            returns_meur=0.0,   # TODO
            years=0.0,          # TODO
        ),
        default_pct=50.0,       # board shows the cuts at 50%
    ),

    # MOD 14 - Carbon tax  - Transport of Aircraft Elements
    PercentageMetric(
        id="transport_carbon_tax",
        label="Carbon Tax (%)",
        impact_at_0=Impact(),
        impact_at_100=Impact(
            co2_saved_kt=0.0,   # TODO: CO2e avoided at a 100% blend ceiling
            cost_meur=0.0,      # TODO
            returns_meur=0.0,   # TODO
            years=0.0,          # TODO
        ),
        default_pct=50.0,       # board shows the cuts at 50%
    ),

    # MOD 15 - Schedule buffer - Transport of Aircraft Elements
    LevelMetric(
        id="transport_buffer",
        label="Schedule Buffer",
        impact_at_min=Impact(),  # level 1 (Pilot): baseline
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO: CO2e avoided at EU-Mandate level
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO: years to deliver / break even
        ),
    ),

    # MOD 16a - Mandates vs. incentives - Next Gen Roadmapping
    ChoiceMetric(
        id="nextgen_policy_instrument",
        label="Policy instrument",
        options={
            "None": Impact(),
            "Incentive": Impact(
                co2_saved_kt=0.0, cost_meur=0.0, returns_meur=0.0, years=0.0  # TODO
            ),
            "Mandate": Impact(
                co2_saved_kt=0.0, cost_meur=0.0, returns_meur=0.0, years=0.0  # TODO
            ),
        },
        default_option="None",
    ),

    # MOD 16b - Decarbonisation commitment by stakeholders - Next Gen Roadmapping
    PercentageMetric(
        id="nextgen_decarb_commitment",
        label="Decarbonisation Commitment by Stakeholders (%)",
        impact_at_0=Impact(),
        impact_at_100=Impact(
            co2_saved_kt=0.0,   # TODO: CO2e avoided at a 100% blend ceiling
            cost_meur=0.0,      # TODO
            returns_meur=0.0,   # TODO
            years=0.0,          # TODO
        ),
        default_pct=50.0,       # board shows the cuts at 50%
    ),

    # MOD 17a - Priority on New Technology Notification - Next Gen Roadmapping
    PercentageMetric(
        id="nextgen_tech_priority",
        label="Priority on New Technology Notification (%)",
        impact_at_0=Impact(),
        impact_at_100=Impact(
            co2_saved_kt=0.0,   # TODO: CO2e avoided at a 100% blend ceiling
            cost_meur=0.0,      # TODO
            returns_meur=0.0,   # TODO
            years=0.0,          # TODO
        ),
        default_pct=50.0,       # board shows the cuts at 50%
    ),

    # MOD 17b - Priority on New Technology Notification - Next Gen Roadmapping
    ChoiceMetric(
        id="nextgen_tech_toggle",
        label="Priority on New Technology Notification",
        options={
            "SAF": Impact(co2_saved_kt=0.0, cost_meur=0.0, returns_meur=0.0, years=0.0),       # TODO
            "H2": Impact(co2_saved_kt=0.0, cost_meur=0.0, returns_meur=0.0, years=0.0),        # TODO
            "Electric": Impact(co2_saved_kt=0.0, cost_meur=0.0, returns_meur=0.0, years=0.0),  # TODO
            "Other": Impact(),
        },
        default_option="SAF",
    ),

    # MOD 18 - Actions needed by stakeholer - Next Gen Roadmapping
    ChoiceMetric(
        id="nextgen_actions",
        label="Actions Needed by Stakeholder",
        options={
            "Airlines": Impact(co2_saved_kt=0.0, cost_meur=0.0, returns_meur=0.0, years=0.0),       # TODO
            "OEMs": Impact(co2_saved_kt=0.0, cost_meur=0.0, returns_meur=0.0, years=0.0),        # TODO
            "Government": Impact(co2_saved_kt=0.0, cost_meur=0.0, returns_meur=0.0, years=0.0),  # TODO
            "Other": Impact(),
        },
        default_option="Airlines",
    )

    # MOD 19 - Funding by Stakeholder - Extra
    # PLACEHOLDER

]


# ---------------------------------------------------------------------------
# Examples of the OTHER control types, in case a module is a slider or dropdown
# rather than the 1-5 ambition control. Copy the pattern into MODULES as needed.
# ---------------------------------------------------------------------------


def build_simulation(include_examples: bool = False):
    """Return a ready-to-use :class:`~flight_deck.engine.Simulation` for the board.

    Set ``include_examples=True`` to also include the slider/dropdown demos above.
    Weights and normalisation use the defaults in ``scoring.py`` — tune there.
    """
    from .engine import Simulation  # local import to avoid a cycle

    metrics = list(MODULES)
    
    return Simulation(
        metrics=metrics,
        weights=ScoreWeights(climate=1.0, financial=1.0, time=1.0),  # TODO: retune
        normalization=Normalization(),  # TODO: set reference bands in scoring.py
    )
