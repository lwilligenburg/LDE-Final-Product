"""
Flight Deck 2050 — backend logic for the sustainable-aviation policy simulator.

Public API::

    from back_end import Simulation, build_simulation
    from back_end import Impact
    from back_end import PercentageMetric, ChoiceMetric, LevelMetric
    from back_end import Normalization, ScoreWeights

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
