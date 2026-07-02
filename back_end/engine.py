"""
Simulation engine — glue the metrics and scoring together.

Give it the list of metrics for a scenario. Call :meth:`Simulation.evaluate` with
the player's choices ``{metric_id: value}`` and it returns a
:class:`SimulationResult`: the three dimension scores (each the AVERAGE rating
across the metrics that touch that dimension), the weighted composite, and a
per-metric breakdown for the UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .impacts import Impact
from .metrics import Metric
from .scoring import ScoreWeights

_DIMENSIONS = ("climate", "financial", "time")


@dataclass
class MetricContribution:
    """What one metric contributed, kept for display / debugging / tooltips."""

    metric_id: str
    label: str
    value: Any
    rendered: str
    impact: Impact


@dataclass
class SimulationResult:
    """The full outcome of one set of player choices (all scores 0-100)."""

    climate_score: float
    financial_score: float
    time_score: float
    composite: float

    contributions: list[MetricContribution] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "Flight Deck 2050 — outcome (0-100, higher is better)",
            f"  Climate    : {self.climate_score:5.1f}/100",
            f"  Financial  : {self.financial_score:5.1f}/100",
            f"  Time       : {self.time_score:5.1f}/100   (higher = faster to deliver)",
            f"  COMPOSITE  : {self.composite:5.1f}/100",
        ]
        return "\n".join(lines)


class Simulation:
    """A configured scenario: a set of metrics + how to weight them."""

    def __init__(self, metrics: list[Metric], weights: ScoreWeights | None = None) -> None:
        self.metrics: dict[str, Metric] = {}
        for m in metrics:
            if m.id in self.metrics:
                raise ValueError(f"Duplicate metric id: {m.id!r}")
            self.metrics[m.id] = m
        self.weights = weights or ScoreWeights()

    def default_choices(self) -> dict[str, Any]:
        """The starting board — every metric at its default value."""
        return {mid: m.default() for mid, m in self.metrics.items()}

    def evaluate(self, choices: dict[str, Any] | None = None) -> SimulationResult:
        """Score a set of player choices.

        Unspecified metrics fall back to their default. Unknown metric ids and
        out-of-range values raise ``ValueError`` so the UI can flag bad input.
        """
        choices = choices or {}

        unknown = set(choices) - set(self.metrics)
        if unknown:
            raise ValueError(f"Unknown metric id(s): {sorted(unknown)}")

        contributions: list[MetricContribution] = []
        # Collect each dimension's applicable ratings, then average them.
        buckets: dict[str, list[float]] = {dim: [] for dim in _DIMENSIONS}

        for mid, metric in self.metrics.items():
            value = choices.get(mid, metric.default())
            impact = metric.impact_of(value)
            for dim in _DIMENSIONS:
                rating = getattr(impact, dim)
                if rating is not None:  # None = 'not applicable', skip it
                    buckets[dim].append(rating)
            contributions.append(
                MetricContribution(
                    metric_id=mid,
                    label=metric.label,
                    value=value,
                    rendered=metric.describe(value),
                    impact=impact,
                )
            )

        def mean(values: list[float]) -> float:
            return sum(values) / len(values) if values else 0.0

        climate_score = mean(buckets["climate"])
        financial_score = mean(buckets["financial"])
        time_score = mean(buckets["time"])
        composite = self.weights.combine(climate_score, financial_score, time_score)

        return SimulationResult(
            climate_score=climate_score,
            financial_score=financial_score,
            time_score=time_score,
            composite=composite,
            contributions=contributions,
        )
