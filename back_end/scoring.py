"""
Scoring — turn raw aggregated impacts into a player-facing outcome.

Recommended model (and why)
---------------------------
A policy-simulation game needs the final number to be *legible*: a player should
understand why a choice helped or hurt. So the model here is deliberately simple
and transparent — no black-box formula.

1. Aggregate the raw impacts into three real-world totals:
     climate   = total CO2e avoided        (kt/yr,   higher better)
     financial = net value = returns - cost (M EUR,   higher better)
     time      = investment-weighted years  (years,   LOWER better)

2. Normalise each total to a 0-100 sub-score using an explicit
   (worst, best) reference band. Anything at/below ``worst`` scores 0, anything
   at/above ``best`` scores 100, linear in between, clamped. The same linear map
   handles "higher is better" (climate, financial) and "lower is better" (time):
   for time you simply set best < worst.

   Using a fixed reference band — rather than normalising against the current
   run — means a score is comparable across playthroughs and can't be gamed by
   making every option equally bad.

3. Combine the three sub-scores into one composite with configurable weights
   (default: equal thirds). Weights let you or the assignment emphasise, say,
   climate over financial return.

Everything with a real number that belongs to *your thesis* is marked TODO in
``modules.py`` / the ``Normalization`` defaults — the mechanics here are complete.
"""

from __future__ import annotations

from dataclasses import dataclass


def linear_score(value: float, worst: float, best: float) -> float:
    """Map ``value`` onto 0-100 where ``worst`` -> 0 and ``best`` -> 100 (clamped).

    Works in both directions: if ``best > worst`` higher values score higher; if
    ``best < worst`` (time) lower values score higher.
    """
    if best == worst:
        return 50.0
    s = (value - worst) / (best - worst) * 100.0
    return max(0.0, min(100.0, s))


@dataclass
class Normalization:
    """Reference bands mapping each raw total to a 0-100 sub-score.

    TODO: replace these placeholder bands with figures grounded in your thesis
    scenario (e.g. the realistic min/max CO2e a full policy portfolio could move).
    They are the dials that decide how "hard" the game is.
    """

    # climate: kilotonnes CO2e avoided per year. worst = do-nothing, best = stretch target.
    climate_worst_kt: float = 0.0
    climate_best_kt: float = 1000.0   # TODO: set to your scenario's ambitious ceiling

    # financial: net value in M EUR. worst = biggest tolerable loss, best = strong return.
    financial_worst_meur: float = -500.0   # TODO
    financial_best_meur: float = 500.0     # TODO

    # time: years to deliver / break even. Note best < worst (sooner is better).
    time_worst_years: float = 25.0   # TODO: slowest acceptable horizon -> 0
    time_best_years: float = 0.0     # immediate payoff -> 100

    def climate_score(self, kt: float) -> float:
        return linear_score(kt, self.climate_worst_kt, self.climate_best_kt)

    def financial_score(self, meur: float) -> float:
        return linear_score(meur, self.financial_worst_meur, self.financial_best_meur)

    def time_score(self, years: float) -> float:
        return linear_score(years, self.time_worst_years, self.time_best_years)


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
