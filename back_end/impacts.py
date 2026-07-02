"""
Impact vectors — now expressed as qualitative RATINGS instead of physical units.

Rather than quantifying CO2 in kt, money in EUR, and time in years, every metric
choice is rated Very Low -> Very High on three dimensions:

  * climate   — how much this helps decarbonisation
  * financial — how good this is financially (net of cost)
  * time      — how QUICKLY it delivers / pays off  (Very High = fastest)

Each rating maps to a 0-100 number (see ``RATING_SCALE``) so the engine can
average and weight them. Higher is always better on all three dimensions — that
keeps data entry simple: you just ask "how good is this option for X?"

A dimension may also be ``None`` = "not applicable". Such a dimension is skipped
when averaging, so a metric that only affects, say, financial and time does not
drag the climate score toward zero. (Contrast with a rating of "Very Low" = 0,
which DOES count as a poor score.)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

# The 5-point scale. Edit the numbers here to re-shape how ratings map to points;
# every metric in the game reads from this one table.
RATING_SCALE: dict[str, float] = {
    "Very Low": 0.0,
    "Low": 25.0,
    "Medium": 50.0,
    "High": 75.0,
    "Very High": 100.0,
}

# What you can pass wherever a rating is expected: a scale label, a raw 0-100
# number, or None for "not applicable".
Rating = Union[str, float, int, None]


def rating_value(r: Rating) -> Optional[float]:
    """Resolve a rating to a 0-100 number (or ``None`` for not-applicable)."""
    if r is None:
        return None
    if isinstance(r, (int, float)) and not isinstance(r, bool):
        return float(r)
    try:
        return RATING_SCALE[r]
    except KeyError:
        raise ValueError(
            f"Unknown rating {r!r}. Use one of {list(RATING_SCALE)}, a 0-100 number, or None."
        )


@dataclass(frozen=True)
class Impact:
    """A choice's rating on each dimension, as 0-100 points (or None = N/A).

    Build one directly with numbers, or — more readably — with :func:`rate`.
    Defaults are 0.0 (Very Low) so a bare ``Impact()`` is a valid 'does nothing'
    baseline that still counts as a poor score.
    """

    climate: Optional[float] = 0.0
    financial: Optional[float] = 0.0
    time: Optional[float] = 0.0

    @staticmethod
    def lerp(a: "Impact", b: "Impact", t: float) -> "Impact":
        """Interpolate each dimension between ``a`` (t=0) and ``b`` (t=1).

        Used by the percentage and level sliders. If a dimension is ``None`` at
        either end it stays ``None`` across the whole slider (not applicable).
        """
        t = max(0.0, min(1.0, t))

        def mix(x: Optional[float], y: Optional[float]) -> Optional[float]:
            if x is None or y is None:
                return None
            return x + (y - x) * t

        return Impact(mix(a.climate, b.climate), mix(a.financial, b.financial), mix(a.time, b.time))


def rate(climate: Rating = None, financial: Rating = None, time: Rating = None) -> Impact:
    """Readable builder for an :class:`Impact` from ratings.

    Any dimension you omit is left ``None`` = not applicable (skipped in scoring).
    Examples::

        rate("High", "Medium", "Low")        # all three dimensions rated
        rate(financial="High", time="Low")   # climate not applicable (e.g. funding)
    """
    return Impact(rating_value(climate), rating_value(financial), rating_value(time))


# 'Does nothing' baseline — all three dimensions at Very Low (0), all applicable.
ZERO = Impact()
