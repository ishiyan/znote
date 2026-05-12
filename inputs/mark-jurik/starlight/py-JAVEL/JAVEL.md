# JAVEL — Adaptive VEL

## Principle

Wraps JXVEL with automatic depth selection. Same volatility-regime adaptation as JARSX but applied to VEL's depth parameter.

## Mathematical Formulas

```
value1[bar] = |price[bar] - price[bar-1]|

avg1 = SMA(value1, min(bar, 99) + 1)
avg2 = SMA(value1, min(bar, 9) + 1)

eps = 0.001

value2 = Sensitivity * ln((eps + avg1) / (eps + avg2))
value3 = value2 / (1 + |value2|)

adaptive_depth = LoLen + (HiLen - LoLen) * (1 + value3) / 2
```

## Algorithm

1. Compute `value1[bar] = |price[bar] - price[bar-1]|` for each bar.
2. For each bar:
   - Compute `avg1` = SMA of value1 over `min(bar, 99) + 1` bars.
   - Compute `avg2` = SMA of value1 over `min(bar, 9) + 1` bars.
   - `value2 = Sensitivity * ln((eps + avg1) / (eps + avg2))`
   - `value3 = value2 / (1 + |value2|)` — normalized to (-1, 1).
   - `adaptive_depth = LoLen + (HiLen - LoLen) * (1 + value3) / 2` — maps to [LoLen, HiLen].
3. Pass adaptive_depth series + Period to JXVEL:
   - `result = JXVELaux3(JXVELaux1(Series, adaptive_depth), Period)`

## Flow Diagram

```
price series
    │
    ▼
|price[bar] - price[bar-1]| ──► value1
    │
    ├──► SMA(value1, min(bar,99)+1) ──► avg1 ─┐
    │                                          │
    └──► SMA(value1, min(bar,9)+1)  ──► avg2 ─┤
                                               ▼
                              Sensitivity * ln((eps+avg1)/(eps+avg2)) ──► value2
                                               │
                                               ▼
                              value2 / (1 + |value2|) ──► value3
                                               │
                                               ▼
                              LoLen + (HiLen-LoLen)*(1+value3)/2 ──► adaptive_depth
                                               │
                                               ▼
                              JXVEL(Series, adaptive_depth, Period) ──► output
```

## Pseudocode

```
function JAVEL(Series, LoLen, HiLen, Sensitivity, Period):
    eps = 0.001
    N = length(Series)
    value1 = array[N]
    value4 = array[N]  // adaptive_depth

    for bar = 0 to N-1:
        if bar == 0:
            value1[bar] = 0
        else:
            value1[bar] = |Series[bar] - Series[bar-1]|

        len1 = min(bar, 99) + 1
        len2 = min(bar, 9) + 1
        avg1 = SMA(value1[bar-len1+1 .. bar], len1)
        avg2 = SMA(value1[bar-len2+1 .. bar], len2)

        value2 = Sensitivity * ln((eps + avg1) / (eps + avg2))
        value3 = value2 / (1 + |value2|)
        value4[bar] = LoLen + (HiLen - LoLen) * (1 + value3) / 2

    return JXVEL(Series, value4, Period)
```

## Variable Mapping

| Pseudocode / Formula | Code variable    | Description                              |
|----------------------|------------------|------------------------------------------|
| Series               | prices           | Input price array                        |
| LoLen                | lo_len           | Minimum adaptive depth                   |
| HiLen                | hi_len           | Maximum adaptive depth                   |
| Sensitivity          | sensitivity      | Regime detection sensitivity             |
| Period               | period           | JXVEL smoothing period                   |
| value1               | value1           | Absolute bar-to-bar price change         |
| avg1                 | avg1             | Long-window SMA of value1 (up to 100)    |
| avg2                 | avg2             | Short-window SMA of value1 (up to 10)    |
| value2               | value2           | Log ratio scaled by sensitivity          |
| value3               | value3           | Normalized value2 in (-1, 1)             |
| value4 / adaptive_depth | adaptive_depth | Mapped depth for JXVEL in [LoLen, HiLen] |
| eps                  | EPS              | Small constant to avoid log(0) = 0.001   |
