"""
Flight Deck 2050 — backend logic for the sustainable-aviation policy simulator.

Public API::

    from back_end import build_simulation, Simulation
    from back_end import Impact, rate, RATING_SCALE
    from back_end import PercentageMetric, ChoiceMetric, LevelMetric, AllocationMetric
    from back_end import ScoreWeights

Typical use::

    sim = build_simulation()
    result = sim.evaluate({
        "saf_co2_cuts": 80,
        "passport_reg_support": 5,
        "funding_split": {"Government": 40, "Private": 30, "NGO": 10, "Public": 20},
    })
    print(result.summary())
"""

from .impacts import ZERO, Impact, RATING_SCALE, rate, rating_value
from .metrics import (
    AllocationMetric,
    ChoiceMetric,
    LevelMetric,
    Metric,
    PercentageMetric,
)
from .scoring import ScoreWeights
from .engine import MetricContribution, Simulation, SimulationResult
from .modules import MODULES, build_simulation

__all__ = [
    "Impact",
    "ZERO",
    "RATING_SCALE",
    "rate",
    "rating_value",
    "Metric",
    "PercentageMetric",
    "ChoiceMetric",
    "LevelMetric",
    "AllocationMetric",
    "ScoreWeights",
    "Simulation",
    "SimulationResult",
    "MetricContribution",
    "MODULES",
    "build_simulation",
]
