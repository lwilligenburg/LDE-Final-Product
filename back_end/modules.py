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

MODULES: list[LevelMetric] = [
    # MOD 01 · Circular Materials · Materials Digital Passport
    # slider: Pilot -> EU Mandate  |  target metric: EOL recovery rate <= 20%
    LevelMetric(
        id="circular_materials",
        label="Circular Materials — Materials Digital Passport",
        impact_at_min=Impact(),  # level 1 (Pilot): baseline
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO: CO2e avoided at EU-Mandate level
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO: years to deliver / break even
        ),
    ),
    # MOD 02 · SAF Supply Chain · EU SAF Feedstock Regulation
    # slider: Status Quo -> Full Reform  |  target: verified SAF feedstock < 40%
    LevelMetric(
        id="saf_supply_chain",
        label="SAF Supply Chain — EU SAF Feedstock Regulation",
        impact_at_min=Impact(),
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO
        ),
    ),
    # MOD 03 · SAF Blend Limits · SAF Blend Limit Strategy
    # slider: Blend Wall -> Full Certification  |  target: SAF blend ceiling 50%
    LevelMetric(
        id="saf_blend_limits",
        label="SAF Blend Limits — SAF Blend Limit Strategy",
        impact_at_min=Impact(),
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO
        ),
    ),
    # MOD 04 · TRM Guideline · Dynamic Technology Roadmap
    # slider: Static Roadmap -> Adaptive TRM  |  target: policy adoption rate < 10%
    LevelMetric(
        id="trm_guideline",
        label="TRM Guideline — Dynamic Technology Roadmap",
        impact_at_min=Impact(),
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO
        ),
    ),
    # MOD 05 · TRM Application · DTRM Platform
    # slider: Siloed Tools -> Unified Platform  |  target: stakeholder integration < 10%
    LevelMetric(
        id="trm_application",
        label="TRM Application — DTRM Platform",
        impact_at_min=Impact(),
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO
        ),
    ),
    # MOD 06 · Transition Framework · Participatory Backcasting
    # slider: Uncoordinated -> Sector-Wide  |  target: sector coordination < 15%
    LevelMetric(
        id="transition_framework",
        label="Transition Framework — Participatory Backcasting",
        impact_at_min=Impact(),
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO
        ),
    ),
    # MOD 07 · Predictive Maintenance · Bio-Inspired SHM Systems
    # slider: Passive Sensors -> Predictive AI  |  target: maintenance prediction rate < 5%
    LevelMetric(
        id="predictive_maintenance",
        label="Predictive Maintenance — Bio-Inspired SHM Systems",
        impact_at_min=Impact(),
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO
        ),
    ),
    # MOD 08 · Freight Sustainability · Environmental Freight Metrics
    # slider: Cost/Time Only -> Full ESG Weight  |  target: green mode shift < 5%
    LevelMetric(
        id="freight_sustainability",
        label="Freight Sustainability — Environmental Freight Metrics",
        impact_at_min=Impact(),
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO
        ),
    ),
    # MOD 09 · Competition Law · EU Level Playing Field
    # slider: Distorted Market -> Level Playing Field  |  target: market equity index < 20%
    LevelMetric(
        id="competition_law",
        label="Competition Law — EU Level Playing Field",
        impact_at_min=Impact(),
        impact_at_max=Impact(
            co2_saved_kt=0.0,     # TODO
            cost_meur=0.0,        # TODO
            returns_meur=0.0,     # TODO
            years=0.0,            # TODO
        ),
    ),
]


# ---------------------------------------------------------------------------
# Examples of the OTHER control types, in case a module is a slider or dropdown
# rather than the 1-5 ambition control. Copy the pattern into MODULES as needed.
# ---------------------------------------------------------------------------

EXTRA_EXAMPLE_METRICS = [
    # A continuous 0-100% slider — e.g. how high to push the SAF blend ceiling.
    # Impact interpolates from 0% to 100%; here everything scales from nothing at
    # 0% up to the level you set for 100%.
    PercentageMetric(
        id="saf_blend_ceiling_pct",
        label="SAF blend ceiling (%)",
        impact_at_0=Impact(),
        impact_at_100=Impact(
            co2_saved_kt=0.0,   # TODO: CO2e avoided at a 100% blend ceiling
            cost_meur=0.0,      # TODO
            returns_meur=0.0,   # TODO
            years=0.0,          # TODO
        ),
        default_pct=50.0,       # board shows the wall at 50%
    ),
    # An unordered discrete pick — e.g. the policy instrument used to drive change.
    ChoiceMetric(
        id="policy_instrument",
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
    # A technology-choice dropdown — the classic SAF / H2 / Electric / Other.
    ChoiceMetric(
        id="energy_carrier",
        label="Primary energy carrier",
        options={
            "SAF": Impact(co2_saved_kt=0.0, cost_meur=0.0, returns_meur=0.0, years=0.0),       # TODO
            "H2": Impact(co2_saved_kt=0.0, cost_meur=0.0, returns_meur=0.0, years=0.0),        # TODO
            "Electric": Impact(co2_saved_kt=0.0, cost_meur=0.0, returns_meur=0.0, years=0.0),  # TODO
            "Other": Impact(),
        },
        default_option="SAF",
    ),
]


def build_simulation(include_examples: bool = False):
    """Return a ready-to-use :class:`~flight_deck.engine.Simulation` for the board.

    Set ``include_examples=True`` to also include the slider/dropdown demos above.
    Weights and normalisation use the defaults in ``scoring.py`` — tune there.
    """
    from .engine import Simulation  # local import to avoid a cycle

    metrics = list(MODULES)
    if include_examples:
        metrics = metrics + list(EXTRA_EXAMPLE_METRICS)
    return Simulation(
        metrics=metrics,
        weights=ScoreWeights(climate=1.0, financial=1.0, time=1.0),  # TODO: retune
        normalization=Normalization(),  # TODO: set reference bands in scoring.py
    )
