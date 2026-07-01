"""
Runnable demo — proves the engine works end to end.

The numbers here are ILLUSTRATIVE ONLY (invented so the demo produces a non-zero
score). They are NOT from any thesis and live only in this file — the real module
config in flight_deck/modules.py keeps its TODO placeholders untouched.

Run it:  python demo.py
"""

from flight_deck import (
    ChoiceMetric,
    Impact,
    LevelMetric,
    Normalization,
    PercentageMetric,
    ScoreWeights,
    Simulation,
)


def build_illustrative_sim() -> Simulation:
    """A tiny 3-metric scenario using each control type, with made-up numbers."""
    metrics = [
        # 1-5 ambition slider: SAF supply-chain reform.
        LevelMetric(
            id="saf_supply_chain",
            label="SAF Supply Chain reform",
            impact_at_min=Impact(),  # level 1: nothing changes
            impact_at_max=Impact(    # level 5: big CO2 win, pricey, slow-ish payoff
                co2_saved_kt=600.0, cost_meur=420.0, returns_meur=520.0, years=9.0
            ),
        ),
        # 0-100% slider: SAF blend ceiling.
        PercentageMetric(
            id="saf_blend_ceiling_pct",
            label="SAF blend ceiling (%)",
            impact_at_0=Impact(),
            impact_at_100=Impact(
                co2_saved_kt=300.0, cost_meur=180.0, returns_meur=210.0, years=5.0
            ),
            default_pct=50.0,
        ),
        # discrete pick: policy instrument.
        ChoiceMetric(
            id="policy_instrument",
            label="Policy instrument",
            options={
                "None": Impact(),
                "Incentive": Impact(co2_saved_kt=80.0, cost_meur=120.0, returns_meur=60.0, years=3.0),
                "Mandate": Impact(co2_saved_kt=160.0, cost_meur=60.0, returns_meur=40.0, years=2.0),
            },
            default_option="None",
        ),
    ]
    return Simulation(
        metrics=metrics,
        weights=ScoreWeights(climate=1.0, financial=1.0, time=1.0),
        normalization=Normalization(
            climate_best_kt=1000.0,
            financial_worst_meur=-500.0,
            financial_best_meur=500.0,
            time_worst_years=25.0,
            time_best_years=0.0,
        ),
    )


def main() -> None:
    sim = build_illustrative_sim()

    print("=" * 60)
    print("Starting board (everything at default):")
    print(sim.evaluate(sim.default_choices()).summary())

    print("=" * 60)
    print("An ambitious playthrough:")
    result = sim.evaluate(
        {
            "saf_supply_chain": 5,          # full ambition
            "saf_blend_ceiling_pct": 70,    # push the blend wall to 70%
            "policy_instrument": "Mandate",
        }
    )
    print(result.summary())

    print("-" * 60)
    print("Per-metric breakdown:")
    for c in result.contributions:
        print(
            f"  {c.label:32s} = {c.rendered:14s} "
            f"| CO2 {c.impact.co2_saved_kt:6.0f} kt "
            f"| net {c.impact.returns_meur - c.impact.cost_meur:7.0f} M "
            f"| {c.impact.years:.0f} yr"
        )


if __name__ == "__main__":
    main()
