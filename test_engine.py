"""
Tests for the ratings-based Flight Deck engine. Run:  pytest -q

These check mechanics (rating resolution, interpolation, allocation blending,
averaging, validation), so they stay valid as you fill in real ratings.
"""

import math

import pytest

from back_end import (
    AllocationMetric,
    ChoiceMetric,
    Impact,
    LevelMetric,
    PercentageMetric,
    ScoreWeights,
    Simulation,
    rate,
    rating_value,
)


# --- rating scale -----------------------------------------------------------

def test_rating_value_labels_numbers_and_none():
    assert rating_value("Very Low") == 0.0
    assert rating_value("Medium") == 50.0
    assert rating_value("Very High") == 100.0
    assert rating_value(42) == 42.0
    assert rating_value(None) is None


def test_rating_value_rejects_unknown_label():
    with pytest.raises(ValueError):
        rating_value("Enormous")


def test_rate_omitted_dimension_is_not_applicable():
    imp = rate(financial="High", time="Low")
    assert imp.climate is None
    assert imp.financial == 75.0
    assert imp.time == 25.0


# --- interpolation ----------------------------------------------------------

def test_percentage_interpolates_ratings():
    m = PercentageMetric(
        id="p", label="p",
        impact_at_0=rate("Very Low", "Very Low", "Very Low"),
        impact_at_100=rate("Very High", "Medium", "Very Low"),
    )
    half = m.impact_of(50)
    assert math.isclose(half.climate, 50.0)     # 0 -> 100 at t=.5
    assert math.isclose(half.financial, 25.0)   # 0 -> 50 at t=.5


def test_lerp_keeps_none_across_range():
    a = rate(financial="Low")            # climate/time None
    b = rate(financial="High")
    mid = Impact.lerp(a, b, 0.5)
    assert mid.climate is None
    assert math.isclose(mid.financial, 50.0)


def test_level_endpoints_and_midpoint():
    m = LevelMetric(
        id="l", label="l", levels=5,
        impact_at_min=rate("Very Low", "Very Low", "Very Low"),
        impact_at_max=rate("Very High", "Very High", "Very High"),
    )
    assert math.isclose(m.impact_of(1).climate, 0.0)
    assert math.isclose(m.impact_of(3).climate, 50.0)
    assert math.isclose(m.impact_of(5).climate, 100.0)


# --- allocation metric ------------------------------------------------------

def _funding():
    return AllocationMetric(
        id="funding_split",
        label="Who pays",
        groups={
            "Government": rate(financial="Medium", time="High"),   # 50 / 75
            "Private": rate(financial="High", time="Low"),         # 75 / 25
            "NGO": rate(financial="Low", time="Medium"),           # 25 / 50
            "Public": rate(financial="Low", time="Medium"),        # 25 / 50
        },
    )


def test_allocation_default_is_equal_split():
    assert _funding().default() == {"Government": 25, "Private": 25, "NGO": 25, "Public": 25}


def test_allocation_blends_by_share_and_climate_is_na():
    imp = _funding().impact_of({"Government": 100, "Private": 0, "NGO": 0, "Public": 0})
    assert imp.climate is None                 # every group omits climate
    assert math.isclose(imp.financial, 50.0)   # 100% Government
    assert math.isclose(imp.time, 75.0)


def test_allocation_weighted_blend():
    imp = _funding().impact_of({"Government": 50, "Private": 50, "NGO": 0, "Public": 0})
    assert math.isclose(imp.financial, (50 * 50 + 75 * 50) / 100)  # 62.5
    assert math.isclose(imp.time, (75 * 50 + 25 * 50) / 100)       # 50.0


def test_allocation_rejects_non_100_sum():
    with pytest.raises(ValueError):
        _funding().impact_of({"Government": 40, "Private": 30, "NGO": 10, "Public": 10})  # 90


def test_allocation_rejects_wrong_groups():
    with pytest.raises(ValueError):
        _funding().impact_of({"Government": 100})


def test_allocation_rejects_negative_share():
    with pytest.raises(ValueError):
        _funding().impact_of({"Government": 110, "Private": -10, "NGO": 0, "Public": 0})


# --- engine averaging -------------------------------------------------------

def _sim():
    return Simulation(
        metrics=[
            LevelMetric(
                id="a", label="a", levels=5,
                impact_at_min=rate("Very Low", "Very Low", "Very Low"),
                impact_at_max=rate("Very High", "High", "Low"),
            ),
            ChoiceMetric(
                id="b", label="b",
                options={
                    "off": rate("Very Low", "Very Low", "Very Low"),
                    "on": rate("High", "Medium", "High"),
                },
                default_option="off",
            ),
            _funding(),
        ],
        weights=ScoreWeights(),
    )


def test_scores_average_only_applicable_dimensions():
    r = _sim().evaluate({"a": 5, "b": "on", "funding_split": {"Government": 100, "Private": 0, "NGO": 0, "Public": 0}})
    # climate: metric a=100, b=75, funding=N/A -> mean(100,75) = 87.5
    assert math.isclose(r.climate_score, 87.5)
    # financial: a=75, b=50, funding=50 -> mean = 58.333...
    assert math.isclose(r.financial_score, (75 + 50 + 50) / 3)
    # time: a=25, b=75, funding=75 -> mean = 58.333...
    assert math.isclose(r.time_score, (25 + 75 + 75) / 3)


def test_composite_in_range_and_weighted():
    r = _sim().evaluate()
    assert 0.0 <= r.composite <= 100.0


def test_unknown_metric_id_raises():
    with pytest.raises(ValueError):
        _sim().evaluate({"nope": 1})


# --- the real board ---------------------------------------------------------

def test_real_board_builds_and_runs():
    from back_end import build_simulation
    sim = build_simulation()
    r = sim.evaluate()  # all defaults
    assert 0.0 <= r.composite <= 100.0
