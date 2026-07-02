"""
Metric types — the controls a player manipulates.

Unchanged from before: PercentageMetric (0-100% slider), ChoiceMetric (discrete
pick), LevelMetric (ordered 1..N ambition slider). They now carry rating-based
Impacts (see impacts.py) but their code is identical — the slider/level classes
interpolate with ``Impact.lerp`` exactly as before, so a rated 'low end' and
'high end' produce a smooth Very Low -> Very High sweep automatically.

New: AllocationMetric — a set of stakeholder shares that must sum to 100%
(Government / Private / NGO / Public). It is NOT a percentage or a choice: the
shares are interdependent. Each group carries its own impact profile and the
engine blends them by share.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .impacts import ZERO, Impact


class Metric(ABC):
    """Base class for every controllable metric."""

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
        """Return the metric's starting value."""

    def describe(self, value: Any) -> str:
        """Human-readable rendering of a chosen value (overridable)."""
        return str(value)


@dataclass
class PercentageMetric(Metric):
    """A continuous 0-100% slider.

    Impact interpolates between ``impact_at_0`` (0%) and ``impact_at_100`` (100%),
    so rate the two ends (e.g. Very Low at 0%, High at 100%) and every position in
    between is handled for you. Pass a ``response`` callable for a non-linear curve.
    """

    id: str
    label: str
    impact_at_0: Impact = ZERO
    impact_at_100: Impact = ZERO
    default_pct: float = 0.0
    unit: str = "%"
    response: Any = None  # optional callable: (pct: float) -> fraction in [0, 1]

    def validate(self, value: Any) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
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
    """An unordered discrete pick — one Impact per named option."""

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
    """The ordered 1..N "Ambition Level" slider (N defaults to 5).

    Impact interpolates from ``impact_at_min`` (level 1) to ``impact_at_max``
    (level N). Override a specific rung with ``per_level={3: rate(...)}``.
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


@dataclass
class AllocationMetric(Metric):
    """Interdependent shares that must sum to 100% (e.g. who funds the transition).

    Each stakeholder group carries an impact *profile* — the impact you'd get if
    that group funded 100% of the transition. The chosen allocation blends those
    profiles by share. Because the shares are coupled (they must total 100), this
    is deliberately its own type rather than several PercentageMetrics.

    A value is a dict ``{group: percent}`` covering exactly the defined groups and
    summing to 100 (within ``tolerance``). Leave a dimension of a group's profile
    as ``None`` (via ``rate``) to make the whole module not-applicable on that
    dimension — e.g. funding is climate-neutral, so every group omits ``climate``.

    Example::

        AllocationMetric(
            id="funding_split",
            label="Who pays for the transition",
            groups={
                "Government": rate(financial="Medium", time="High"),
                "Private":    rate(financial="High",   time="Low"),
                "NGO":        rate(financial="Low",    time="Medium"),
                "Public":     rate(financial="Low",    time="Medium"),
            },
        )
    """

    id: str
    label: str
    groups: dict[str, Impact] = field(default_factory=dict)
    default_allocation: dict[str, float] | None = None
    tolerance: float = 0.5  # how far the shares may stray from summing to 100

    _DIMS = ("climate", "financial", "time")

    def __post_init__(self) -> None:
        if len(self.groups) < 2:
            raise ValueError(f"{self.id}: AllocationMetric needs at least two groups")
        if self.default_allocation is None:
            # Equal split across the groups.
            even = 100.0 / len(self.groups)
            self.default_allocation = {g: even for g in self.groups}
        # Validate the default eagerly so config errors surface at import time.
        self.validate(self.default_allocation)

    @property
    def group_names(self) -> list[str]:
        return list(self.groups)

    def validate(self, value: Any) -> None:
        if not isinstance(value, dict):
            raise ValueError(f"{self.id}: allocation must be a dict of group -> percent")
        if set(value) != set(self.groups):
            raise ValueError(
                f"{self.id}: allocation must cover exactly {self.group_names}, got {list(value)}"
            )
        for g, share in value.items():
            if not isinstance(share, (int, float)) or isinstance(share, bool):
                raise ValueError(f"{self.id}: share for {g!r} must be a number, got {share!r}")
            if share < 0:
                raise ValueError(f"{self.id}: share for {g!r} is negative ({share})")
        total = sum(value.values())
        if abs(total - 100.0) > self.tolerance:
            raise ValueError(f"{self.id}: shares must sum to 100 (got {total:g})")

    def impact_of(self, value: Any) -> Impact:
        self.validate(value)
        total = sum(value.values()) or 100.0  # guard divide-by-zero
        blended: dict[str, float | None] = {}
        for dim in self._DIMS:
            per_group = [(getattr(self.groups[g], dim), value[g]) for g in self.groups]
            defined = [(v, s) for v, s in per_group if v is not None]
            if not defined:
                blended[dim] = None                      # not applicable for every group
            elif len(defined) == len(per_group):
                blended[dim] = sum(v * s for v, s in per_group) / total
            else:
                raise ValueError(
                    f"{self.id}: dimension {dim!r} is set for some groups but not all; "
                    "make it consistent (all rated, or all None)."
                )
        return Impact(**blended)

    def default(self) -> dict[str, float]:
        return dict(self.default_allocation)

    def describe(self, value: Any) -> str:
        return " · ".join(f"{g} {value[g]:g}%" for g in self.groups)
