"""
Full executable — proves the ratings engine works end to end.

Ratings here are ILLUSTRATIVE. The real board config lives in
back_end/modules.py. Run it:  python final-product.py
"""

from back_end import (
    AllocationMetric,
    ChoiceMetric,
    LevelMetric,
    PercentageMetric,
    ScoreWeights,
    Simulation,
    rate,
)


def build_illustrative_sim() -> Simulation:
    """A small scenario using every control type, rated Very Low -> Very High."""
    metrics = [
        # 1-5 ambition slider.
        LevelMetric(
            id="saf_supply_chain",
            label="SAF Supply Chain reform",
            impact_at_min=rate("Very Low", "Very Low", "Very Low"),
            impact_at_max=rate("Very High", "Medium", "Low"),
        ),
        # 0-100% slider.
        PercentageMetric(
            id="saf_blend_ceiling_pct",
            label="SAF blend ceiling (%)",
            impact_at_0=rate("Very Low", "Low", "High"),
            impact_at_100=rate("High", "Low", "Medium"),
            default_pct=50.0,
        ),
        # discrete pick.
        ChoiceMetric(
            id="policy_instrument",
            label="Policy instrument",
            options={
                "None": rate("Very Low", "Very Low", "Very Low"),
                "Incentive": rate("Medium", "Low", "Medium"),
                "Mandate": rate("High", "Medium", "High"),
            },
            default_option="None",
        ),
        # allocation that must sum to 100 (climate-neutral: only financial + time).
        AllocationMetric(
            id="funding_split",
            label="Who pays for the transition",
            groups={
                "Government": rate(financial="Medium", time="High"),
                "Private": rate(financial="High", time="Low"),
                "NGO": rate(financial="Low", time="Medium"),
                "Public": rate(financial="Low", time="Medium"),
            },
        ),
    ]
    return Simulation(metrics=metrics, weights=ScoreWeights(1.0, 1.0, 1.0))


def main() -> None:
    sim = build_illustrative_sim()

    print("=" * 60)
    print("Starting board (defaults):")
    print(sim.evaluate(sim.default_choices()).summary())

    print("=" * 60)
    print("An ambitious playthrough:")
    result = sim.evaluate(
        {
            "saf_supply_chain": 5,
            "saf_blend_ceiling_pct": 70,
            "policy_instrument": "Mandate",
            "funding_split": {"Government": 40, "Private": 20, "NGO": 10, "Public": 30},
        }
    )
    print(result.summary())

    print("-" * 60)
    print("Per-metric breakdown (climate / financial / time, blank = N/A):")
    for c in result.contributions:
        def cell(v):
            return " -- " if v is None else f"{v:4.0f}"
        print(
            f"  {c.label:34s} = {c.rendered:28s} "
            f"| C {cell(c.impact.climate)} "
            f"| F {cell(c.impact.financial)} "
            f"| T {cell(c.impact.time)}"
        )


if __name__ == "__main__":
    main()
