# Flight Deck 2050 — backend logic

Pure-Python engine for the sustainable-aviation policy simulator. Players set a
control on each module; the engine turns those choices into three scores —
**climate** (CO2 saved), **financial** (net value = returns − cost), and **time**
(years to deliver / break even) — and a combined composite.

## Layout

```
flight_deck/
  impacts.py   # Impact vector: the CO2 / cost / returns / years a choice contributes
  metrics.py   # 3 control types: PercentageMetric, ChoiceMetric, LevelMetric
  scoring.py   # normalise each dimension to 0-100 and weight into a composite
  engine.py    # Simulation: choices -> aggregated scores + per-metric breakdown
  modules.py   # the 9 board modules as config  <-- PUT YOUR THESIS NUMBERS HERE
demo.py        # runnable end-to-end demo (illustrative numbers)
test_engine.py # pytest suite for the mechanics
```

## Quick start

```bash
python demo.py            # see it run
python -m pytest -q       # run the tests
```

```python
from flight_deck import build_simulation

sim = build_simulation()
result = sim.evaluate({"saf_supply_chain": 5, "circular_materials": 3})
print(result.summary())
print(result.composite)   # 0-100
```

## The three control types

| Type | Board example | Value you pass |
|------|---------------|----------------|
| `LevelMetric` | "Ambition Level" 1–5 slider | an int `1`–`5` |
| `PercentageMetric` | SAF blend ceiling 0–100% | a number `0`–`100` |
| `ChoiceMetric` | Mandate / Incentive, SAF / H2 / Electric / Other | one of the option strings |

Each choice maps to an `Impact` (CO2 kt, cost M€, returns M€, years). Percentage
and level metrics **interpolate** between a low and high endpoint; choice metrics
carry one `Impact` per option.

## Filling in your numbers

Everything is wired and tested — only the coefficients are placeholders. Edit
`flight_deck/modules.py`: every `0.0` marked `# TODO` is a value to supply. For
each module the key question is *"at full ambition, how much CO2 does this save,
what does it cost, what does it return, and how many years to pay off?"* Set the
scoring reference bands and weights in `flight_deck/scoring.py`.

## Scoring model (recommended)

Each raw total is mapped to 0–100 against an explicit `(worst, best)` band
(linear, clamped; for time `best < worst` so sooner scores higher). The three
sub-scores combine with configurable weights (default: equal thirds). It's
deliberately transparent so a player can see *why* a choice helped — and so the
model is easy to defend in a thesis.
