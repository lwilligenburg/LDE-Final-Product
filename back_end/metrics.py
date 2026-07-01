"""
Metric types — the controls a player actually manipulates.

Every metric knows three things:

  * how to validate a raw value coming from the UI,
  * how to turn a valid value into an :class:`~flight_deck.impacts.Impact`,
  * what its default (starting) value is.

Three concrete types cover everything on the Flight Deck board:

  * :class:`PercentageMetric` — a 0-100% slider (EOL recovery rate, SAF blend,
    verified feedstock, ...). Impact interpolates between a 0% end and a 100% end.
  * :class:`ChoiceMetric` — an unordered discrete pick (Mandate / Incentive,
    SAF / H2 / Electric / Other, Low / Medium / High). Each option carries its
    own Impact.
  * :class:`LevelMetric` — the ordered 1-5 "Ambition Level" slider. Impact
    interpolates between the minimum and maximum ambition, or you can pin an
    explicit Impact per level.

Add a new metric type by subclassing :class:`Metric` and implementing the three
abstract methods; the engine will treat it like any other.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .impacts import ZERO, Impact


class Metric(ABC):
    """Base class for every controllable metric.

    Subclasses set ``id`` (a stable machine key used in the choices dict) and
    ``label`` (human text for the UI), and implement the three methods below.
    """

    id: str
    label: str

    @abstractmethod
    def validate(self, value: Any) -> None:
        """Raise ``ValueError`` if ``value`` is not a legal setting for this metric."""

    @abstractmethod
    def impact_of(self, value: Any) -> Impact:
        """Return the :class:`Impact` produced by a (valid) ``value``."""

    @abstractmethod
    def default(self) -> Any:
        """Return the metric's starting value (used when a player leaves it untouched)."""

    def describe(self, value: Any) -> str:
        """Human-readable rendering of a chosen value (overridable)."""
        return str(value)


@dataclass
class PercentageMetric(Metric):
    """A continuous 0-100% slider.

    The Impact is a linear interpolation between ``impact_at_0`` (slider at 0%)
    and ``impact_at_100`` (slider at 100%). That lets cost, CO2, returns and even
    delivery time all differ between the low and high ends of the slider.

    If your relationship is non-linear, pass a ``response`` callable that maps the
    raw 0-100 value to a 0-1 interpolation fraction (e.g. ``lambda p: (p/100)**2``).
    """

    id: str
    label: str
    impact_at_0: Impact = ZERO
    impact_at_100: Impact = ZERO
    default_pct: float = 0.0
    unit: str = "%"
    response: Any = None  # optional callable: (pct: float) -> fraction in [0, 1]

    def validate(self, value: Any) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError(f"{self.id}: expected a number, got {value!r}")
        if not 0.0 <= float(value) <= 100.0:
            raise ValueError(f"{self.id}: {value} out of range 0-100")

    def impact_of(self, value: Any) -> Impact:
        self.validate(value)
        t = self.response(float(value)) if self.response else float(value) / 100.0
        return Impact.lerp(self.impact_at_0, self.impact_at_100, t)

    def default(self) -> float:
        return self.default_pct

    def describe(self, value: Any) -> str:
        return f"{float(value):g}{self.unit}"


@dataclass
class ChoiceMetric(Metric):
    """An unordered discrete pick — one Impact per named option.

    Example::

        ChoiceMetric(
            id="policy_instrument",
            label="Policy instrument",
            options={
                "Mandate":   Impact(...),
                "Incentive": Impact(...),
                "None":      Impact(),
            },
            default_option="None",
        )
    """

    id: str
    label: str
    options: dict[str, Impact] = field(default_factory=dict)
    default_option: str = ""

    def __post_init__(self) -> None:
        if not self.options:
            raise ValueError(f"{self.id}: ChoiceMetric needs at least one option")
        if self.default_option == "":
            self.default_option = next(iter(self.options))
        if self.default_option not in self.options:
            raise ValueError(
                f"{self.id}: default_option {self.default_option!r} is not one of "
                f"{list(self.options)}"
            )

    @property
    def choices(self) -> list[str]:
        return list(self.options)

    def validate(self, value: Any) -> None:
        if value not in self.options:
            raise ValueError(
                f"{self.id}: {value!r} is not a valid option; choose from {self.choices}"
            )

    def impact_of(self, value: Any) -> Impact:
        self.validate(value)
        return self.options[value]

    def default(self) -> str:
        return self.default_option


@dataclass
class LevelMetric(Metric):
    """The ordered 1..N "Ambition Level" slider from the board (N defaults to 5).

    By default the Impact interpolates linearly from ``impact_at_min`` (level 1)
    to ``impact_at_max`` (level N). If a particular level needs a bespoke Impact,
    put it in ``per_level`` and it overrides the interpolation for that level.

    ``level_names`` mirrors the labels under the slider (e.g. Pilot ... EU Mandate)
    and is used only for display.
    """

    id: str
    label: str
    levels: int = 5
    impact_at_min: Impact = ZERO
    impact_at_max: Impact = ZERO
    per_level: dict[int, Impact] = field(default_factory=dict)
    level_names: list[str] = field(default_factory=list)
    default_level: int = 1

    def __post_init__(self) -> None:
        if self.levels < 2:
            raise ValueError(f"{self.id}: need at least 2 levels")
        for lvl in self.per_level:
            if not 1 <= lvl <= self.levels:
                raise ValueError(f"{self.id}: per_level key {lvl} out of range 1-{self.levels}")

    def validate(self, value: Any) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{self.id}: level must be an int, got {value!r}")
        if not 1 <= value <= self.levels:
            raise ValueError(f"{self.id}: level {value} out of range 1-{self.levels}")

    def impact_of(self, value: Any) -> Impact:
        self.validate(value)
        if value in self.per_level:
            return self.per_level[value]
        t = (value - 1) / (self.levels - 1)
        return Impact.lerp(self.impact_at_min, self.impact_at_max, t)

    def default(self) -> int:
        return self.default_level

    def describe(self, value: Any) -> str:
        if self.level_names and 1 <= value <= len(self.level_names):
            return f"L{value} · {self.level_names[value - 1]}"
        return f"L{value}"
