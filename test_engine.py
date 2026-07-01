"""
Tests for the Flight Deck engine. Run with:  pytest -q   (or: python -m pytest)

These check the *mechanics* (validation, interpolation, aggregation, scoring),
not the thesis numbers — so they stay valid as you fill in modules.py.
"""

import math

import pytest

from back_end import (
    ChoiceMetric,
    Impact,
    LevelMetric,
    Normalization,
    PercentageMetric,
    ScoreWeights,
    Simulation,
    linear_score,
)


# --- metric validation ------------------------------------------------------

def test_percentage_rejects_out_of_range():
    m = PercentageMetric(id="p", label="p")
    with pytest.raises(ValueError):
        m.impact_of(101)
    with pytest.raises(ValueError):
        m.impact_of(-1)


def test_level_rejects_out_of_range_and_bools():
    m = LevelMetric(id="l", label="l", levels=5)
    with pytest.raises(ValueError):
        m.impact_of(6)
    with pytest.raises(ValueError):
        m.impact_of(0)
    with pytest.raises(ValueError):
        m.impact_of(True)  # bool must not sneak through as int


def test_choice_rejects_unknown_option():
    m = ChoiceMetric(id="c", label="c", options={"A": Impact(), "B": Impact()})
    with pytest.raises(ValueError):
        m.impact_of("Z")


def test_choice_defaults_to_first_option():
    m = ChoiceMetric(id="c", label="c", options={"A": Impact(co2_saved_kt=1), "B": Impact()})
    assert m.default() == "A"


# --- interpolation ----------------------------------------------------------

def test_percentage_interpolates_linearly():
    m = PercentageMetric(
        id="p", label="p",
        impact_at_0=Impact(co2_saved_kt=0.0, cost_meur=0.0),
        impact_at_100=Impact(co2_saved_kt=100.0, cost_meur=200.0),
    )
    half = m.impact_of(50)
    assert math.isclose(half.co2_saved_kt, 50.0)
    assert math.isclose(half.cost_meur, 100.0)


def test_level_endpoints_and_midpoint():
    m = LevelMetric(
        id="l", label="l", levels=5,
        impact_at_min=Impact(co2_saved_kt=0.0),
        impact_at_max=Impact(co2_saved_kt=400.0),
    )
    assert math.isclose(m.impact_of(1).co2_saved_kt, 0.0)
    assert math.isclose(m.impact_of(5).co2_saved_kt, 400.0)
    assert math.isclose(m.impact_of(3).co2_saved_kt, 200.0)  # midpoint


def test_level_per_level_override():
    m = LevelMetric(
        id="l", label="l", levels=5,
        impact_at_min=Impact(co2_saved_kt=0.0),
        impact_at_max=Impact(co2_saved_kt=400.0),
        per_level={3: Impact(co2_saved_kt=999.0)},
    )
    assert math.isclose(m.impact_of(3).co2_saved_kt, 999.0)


# --- scoring ----------------------------------------------------------------

def test_linear_score_clamps_and_inverts():
    # higher-is-better
    assert linear_score(0, 0, 100) == 0
    assert linear_score(100, 0, 100) == 100
    assert linear_score(50, 0, 100) == 50
    assert linear_score(200, 0, 100) == 100  # clamp
    # lower-is-better (best < worst), e.g. time
    assert linear_score(0, 25, 0) == 100
    assert linear_score(25, 25, 0) == 0


def test_weights_are_normalised():
    w = ScoreWeights(climate=2, financial=1, time=1)
    # composite of all-100 sub-scores is 100 regardless of raw weight magnitudes
    assert math.isclose(w.combine(100, 100, 100), 100.0)
    # climate weighted double: 100/0/0 -> 50
    assert math.isclose(w.combine(100, 0, 0), 50.0)


# --- engine aggregation -----------------------------------------------------

def _sim():
    metrics = [
        LevelMetric(
            id="a", label="a", levels=5,
            impact_at_min=Impact(),
            impact_at_max=Impact(co2_saved_kt=600, cost_meur=400, returns_meur=500, years=10),
        ),
        ChoiceMetric(
            id="b", label="b",
            options={
                "off": Impact(),
                "on": Impact(co2_saved_kt=200, cost_meur=100, returns_meur=50, years=2),
            },
            default_option="off",
        ),
    ]
    return Simulation(
        metrics=metrics,
        weights=ScoreWeights(),
        normalization=Normalization(
            climate_best_kt=1000, financial_worst_meur=-500, financial_best_meur=500,
            time_worst_years=25, time_best_years=0,
        ),
    )


def test_default_board_is_all_zero():
    r = _sim().evaluate()
    assert r.climate_kt == 0
    assert r.net_value_meur == 0
    assert r.time_years == 0
    # zero CO2 -> 0, zero net value -> midpoint of [-500,500] = 50, zero years -> 100
    assert math.isclose(r.climate_score, 0.0)
    assert math.isclose(r.financial_score, 50.0)
    assert math.isclose(r.time_score, 100.0)


def test_aggregation_and_net_value():
    r = _sim().evaluate({"a": 5, "b": "on"})
    assert math.isclose(r.climate_kt, 800.0)          # 600 + 200
    assert math.isclose(r.net_value_meur, 50.0)       # (500-400) + (50-100) = 100 + (-50)
    # investment-weighted years: (10*400 + 2*100)/(400+100) = 4200/500 = 8.4
    assert math.isclose(r.time_years, 8.4)


def test_unknown_metric_id_raises():
    with pytest.raises(ValueError):
        _sim().evaluate({"does_not_exist": 3})


def test_real_board_builds_and_runs():
    from back_end import build_simulation
    sim = build_simulation(include_examples=True)
    r = sim.evaluate()  # all defaults; TODO zeros -> should not crash
    assert 0.0 <= r.composite <= 100.0
