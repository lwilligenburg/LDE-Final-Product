"""
Impact vectors — the physical quantities every metric choice contributes.

An ``Impact`` is the single unit of currency the whole engine speaks in. Each
option a player can pick (a slider position, a discrete choice, an ambition
level) maps to one ``Impact``. The engine collects the Impacts from every metric
and aggregates them into the three headline scores:

  * climate impact  <- co2_saved_kt
  * financial return <- returns_meur - cost_meur   (net value)
  * time            <- years                       (investment-weighted average)

Keep every field in real-world units. It makes the model auditable while you
tune it, and it means the numbers in ``modules.py`` can come straight out of
your thesis with no hidden conversion.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Impact:
    """The raw contribution of a single metric choice.

    Fields
    ------
    co2_saved_kt:
        Climate benefit, in kilotonnes of CO2e avoided per year. Higher is
        better. Additive across metrics.
    cost_meur:
        Money spent (capex + opex), in millions of EUR. Additive.
    returns_meur:
        Money returned (fuel savings, avoided penalties, new revenue), in
        millions of EUR. Additive.
    years:
        Time to deliver / break even for this option, in years. Lower is
        better. NOT summed across metrics — the engine takes an
        investment-weighted average so parallel projects don't stack.
    investment_meur:
        Capital tied up, used as the weight for the portfolio time average.
        Defaults to ``cost_meur`` when left as ``None``.

    An Impact is immutable; the combinators below return new instances.
    """

    co2_saved_kt: float = 0.0
    cost_meur: float = 0.0
    returns_meur: float = 0.0
    years: float = 0.0
    investment_meur: float | None = None

    @property
    def weight(self) -> float:
        """Weight used for the time average — investment if set, else cost."""
        return self.investment_meur if self.investment_meur is not None else self.cost_meur

    def scaled(self, factor: float) -> "Impact":
        """Scale the additive quantities by ``factor`` (used by linear sliders).

        ``years`` is deliberately left unscaled: a project does not take longer
        because a slider is at 60% rather than 100%. If timing genuinely varies
        with the slider position, model it with ``lerp`` between two endpoint
        Impacts instead of a single scaled one.
        """
        return Impact(
            co2_saved_kt=self.co2_saved_kt * factor,
            cost_meur=self.cost_meur * factor,
            returns_meur=self.returns_meur * factor,
            years=self.years,
            investment_meur=self.weight * factor,
        )

    @staticmethod
    def lerp(a: "Impact", b: "Impact", t: float) -> "Impact":
        """Linearly interpolate every field between ``a`` (t=0) and ``b`` (t=1).

        Used by percentage and ambition-level metrics so that CO2, cost,
        returns AND time can all vary smoothly between the low and high ends.
        """
        t = max(0.0, min(1.0, t))
        return Impact(
            co2_saved_kt=a.co2_saved_kt + (b.co2_saved_kt - a.co2_saved_kt) * t,
            cost_meur=a.cost_meur + (b.cost_meur - a.cost_meur) * t,
            returns_meur=a.returns_meur + (b.returns_meur - a.returns_meur) * t,
            years=a.years + (b.years - a.years) * t,
            investment_meur=a.weight + (b.weight - a.weight) * t,
        )


# A convenient "does nothing" impact, handy as a default / neutral element.
ZERO = Impact()
