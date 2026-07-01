"""
Flight Deck 2050 — backend logic for the sustainable-aviation policy simulator.

Public API::

    from flight_deck import Simulation, build_simulation
    from flight_deck import Impact
    from flight_deck import PercentageMetric, ChoiceMetric, LevelMetric
    from flight_deck import Normalization, ScoreWeights

Typical use::

    sim = build_simulation()
    result = sim.evaluate({"saf_supply_chain": 5, "circular_materials": 3})
    print(result.summary())
"""

from .impacts import ZERO, Impact
from .metrics import ChoiceMetric, LevelMetric, Metric, PercentageMetric
from .scoring import Normalization, ScoreWeights, linear_score
from .engine import MetricContribution, Simulation, SimulationResult
from .modules import MODULES, EXTRA_EXAMPLE_METRICS, build_simulation

__all__ = [
    "Impact",
    "ZERO",
    "Metric",
    "PercentageMetric",
    "ChoiceMetric",
    "LevelMetric",
    "Normalization",
    "ScoreWeights",
    "linear_score",
    "Simulation",
    "SimulationResult",
    "MetricContribution",
    "MODULES",
    "EXTRA_EXAMPLE_METRICS",
    "build_simulation",
]
