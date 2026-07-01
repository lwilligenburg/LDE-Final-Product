"""
Simulation engine — glue the metrics and scoring together.

Give it the list of metrics that make up a scenario. Call :meth:`Simulation.evaluate`
with a dict of the player's choices ``{metric_id: value}`` and it returns a
:class:`SimulationResult` holding the three headline totals, their 0-100
sub-scores, the weighted composite, and a per-metric breakdown for the UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .impacts import Impact
from .metrics import Metric
from .scoring import Normalization, ScoreWeights


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
    """The full outcome of one set of player choices."""

    # Raw aggregated totals (real-world units).
    climate_kt: float
    net_value_meur: float
    time_years: float

    # 0-100 sub-scores.
    climate_score: float
    financial_score: float
    time_score: float

    # Weighted 0-100 composite.
    composite: float

    contributions: list[MetricContribution] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "Flight Deck 2050 — outcome",
            f"  Climate    : {self.climate_kt:9.1f} kt CO2e/yr   -> {self.climate_score:5.1f}/100",
            f"  Financial  : {self.net_value_meur:9.1f} M EUR net    -> {self.financial_score:5.1f}/100",
            f"  Time       : {self.time_years:9.1f} yrs to payoff -> {self.time_score:5.1f}/100",
            f"  COMPOSITE  : {self.composite:5.1f}/100",
        ]
        return "\n".join(lines)


class Simulation:
    """A configured scenario: a set of metrics + how to score them."""

    def __init__(
        self,
        metrics: list[Metric],
        weights: ScoreWeights | None = None,
        normalization: Normalization | None = None,
    ) -> None:
        self.metrics: dict[str, Metric] = {}
        for m in metrics:
            if m.id in self.metrics:
                raise ValueError(f"Duplicate metric id: {m.id!r}")
            self.metrics[m.id] = m
        self.weights = weights or ScoreWeights()
        self.normalization = normalization or Normalization()

    # -- helpers ---------------------------------------------------------------

    def default_choices(self) -> dict[str, Any]:
        """The starting board — every metric at its default value."""
        return {mid: m.default() for mid, m in self.metrics.items()}

    # -- the main entry point --------------------------------------------------

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
        total_co2 = 0.0
        total_cost = 0.0
        total_returns = 0.0
        weighted_years = 0.0
        total_weight = 0.0
        plain_years: list[float] = []  # fallback when nothing carries investment

        for mid, metric in self.metrics.items():
            value = choices.get(mid, metric.default())
            impact = metric.impact_of(value)

            total_co2 += impact.co2_saved_kt
            total_cost += impact.cost_meur
            total_returns += impact.returns_meur

            if impact.years > 0:
                w = impact.weight
                if w > 0:
                    weighted_years += impact.years * w
                    total_weight += w
                plain_years.append(impact.years)

            contributions.append(
                MetricContribution(
                    metric_id=mid,
                    label=metric.label,
                    value=value,
                    rendered=metric.describe(value),
                    impact=impact,
                )
            )

        net_value = total_returns - total_cost

        # Portfolio time: investment-weighted average of the options that take
        # time. If nothing carries an investment weight, fall back to a plain
        # mean; if nothing takes time at all, the horizon is 0.
        if total_weight > 0:
            time_years = weighted_years / total_weight
        elif plain_years:
            time_years = sum(plain_years) / len(plain_years)
        else:
            time_years = 0.0

        climate_score = self.normalization.climate_score(total_co2)
        financial_score = self.normalization.financial_score(net_value)
        time_score = self.normalization.time_score(time_years)
        composite = self.weights.combine(climate_score, financial_score, time_score)

        return SimulationResult(
            climate_kt=total_co2,
            net_value_meur=net_value,
            time_years=time_years,
            climate_score=climate_score,
            financial_score=financial_score,
            time_score=time_score,
            composite=composite,
            contributions=contributions,
        )
