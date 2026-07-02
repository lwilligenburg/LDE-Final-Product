"""
Scoring — combine the three dimension scores into a composite.

With ratings, each dimension is already on a 0-100 scale, so there is no more
physical-unit normalisation to do (the old ``Normalization`` band is gone). All
that remains is how to weight climate vs financial vs time in the final number.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScoreWeights:
    """Relative importance of each dimension in the composite. Auto-normalised."""

    climate: float = 1.0
    financial: float = 1.0
    time: float = 1.0

    def normalised(self) -> "ScoreWeights":
        total = self.climate + self.financial + self.time
        if total <= 0:
            raise ValueError("Score weights must sum to a positive number")
        return ScoreWeights(self.climate / total, self.financial / total, self.time / total)

    def combine(self, climate_score: float, financial_score: float, time_score: float) -> float:
        w = self.normalised()
        return (
            climate_score * w.climate
            + financial_score * w.financial
            + time_score * w.time
        )
