"""Slope Divergence TSI Filter (SD_TSI) -- William Blau (book Ch. 12).

A trend/congestion prefilter built on the True Strength Index. It keeps the TSI
value ONLY when the slope of the TSI agrees in sign with the slope of a separate
double EMA of price; otherwise it outputs 0 (a "slope divergence" / congestion
zone). Self-contained:

    SD_TSI(close, r, s, u, x, y):
        ind = TSI(close, q, r, s, u)             # triple-smoothed bipolar TSI
        ref = DEMA(close, x, y) = EMA(EMA(close, x), y)   # double EMA on price
        keep = (ind rising  AND ref rising)  -> ind
               (ind falling AND ref falling) -> ind
               otherwise                     -> 0.0

This differs in spirit from the Chapter-8 `_Trade` filter (Nonambiguous Trend
Filter): `_Trade` compares an oscillator to ITS OWN slope (single series). SD_TSI
compares the slope of the oscillator against the slope of a SEPARATE price moving
average -- that is what isolates congestion, where the price moving-average keeps
rising while momentum rolls over (their slopes diverge).

Definition source -- EasyLanguage Appendix B Figure B-25 (verbatim logic):

    Value1 = TSI(Price,r,s,u) ;
    Value2 = DXAverage(Price,x,y) ;          { = EMA(EMA(Price,x),y) }
    if Value1 - Value1[1] > 0 AND Value2 - Value2[1] > 0 then Value3 = Value1 else Value3 = 0;
    if Value1 - Value1[1] < 0 AND Value2 - Value2[1] < 0 then Value4 = Value1 else Value4 = 0;
    SD_TSI = Value3 + Value4 ;

The gate is STRICT: a flat slope (delta == 0) on either series is NOT kept (the
two `if` tests use strict `> 0` / `< 0`), so a tie always yields 0.0.

The EMA primitive and the TSI/DEMA machinery are **embedded** (inlined, not
imported) so this file is a self-contained porting unit -- agents porting to
Go/Rust/TS/Zig need only this file and ``description.md``.

Priming / warm-up (Option B, matches the rest of the library):
    * The TSI momentum needs a price q-1 bars back, so the TSI (hence SD_TSI) is
      ``float('nan')`` for bars 0..q-2 and finite from bar q-1. With the book's
      q = 2 (one-bar momentum) that is a single NaN at bar 0.
    * The price DEMA seeds at bar 0 (no NaN) and advances every bar.
    * At the FIRST finite TSI bar there is no prior TSI value -> no slope -> the
      output is 0.0 (you need two finite TSI samples before a slope exists).

TSI division guard: denominator (TEMA of |momentum|) == 0 -> TSI 0.0.

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math
from collections import deque


# ====================================================================== #
# EMBEDDED BUILDING BLOCK: Blau exponential moving average.               #
# Copied verbatim from core/exponential-moving-average. Inlined on        #
# purpose so each indicator is a standalone porting unit. Do NOT change   #
# its numerics -- see core/exponential-moving-average/description.md.     #
# ====================================================================== #
class ExponentialMovingAverage:
    """Stateful streaming EMA: alpha = 2/(period+1), seeds e_0 = x_0.

    period == 1 -> alpha == 1 -> pure passthrough (output == input).
    period  < 1 -> invalid.
    """

    def __init__(self, period: int) -> None:
        if period < 1:
            raise ValueError(f"period must be >= 1, got {period!r}")
        # Smoothing factor alpha = 2/(n+1); for n == 1 this is exactly 1.0.
        self._alpha: float = 2.0 / (float(period) + 1.0)
        self._prev: float = 0.0      # previous output e_(k-1); valid once primed
        self._primed: bool = False   # has the seed been applied yet?

    def update(self, x: float) -> float:
        if not self._primed:
            # Seed: first output equals first input (no NaN warm-up).
            self._prev = x
            self._primed = True
            return self._prev
        # Blend recursion (matches MQL5 FP op order): e = a*x + (1-a)*prev.
        e = self._alpha * x + (1.0 - self._alpha) * self._prev
        self._prev = e
        return e


# ====================================================================== #
# INDICATOR: Slope Divergence TSI Filter.                                 #
# ====================================================================== #
class SlopeDivergenceTsiFilter:
    """Stateful, streaming Slope Divergence TSI Filter (SD_TSI).

    Feed one ``close`` at a time to :meth:`update`, which returns the filtered
    value for that bar: ``float('nan')`` during the TSI momentum warm-up
    (bars 0..q-2), then either the live TSI value (trend retained) or ``0.0``
    (slope divergence / congestion). The output range is [-100, +100].

    Example (book q=2; full passthrough r=s=u=1, x=y=1 -> TSI is +/-100 = the
    sign of one-bar momentum, ref is the close itself):
    >>> sd = SlopeDivergenceTsiFilter(q=2, r=1, s=1, u=1, x=1, y=1)
    >>> import math
    >>> math.isnan(sd.update(10.0))   # bar 0: momentum undefined -> NaN
    True
    >>> sd.update(12.0)               # bar 1: first finite TSI, no slope yet -> 0.0
    0.0
    >>> sd.update(11.0)               # bar 2: TSI -100 falling, price falling -> keep -100
    -100.0
    >>> sd.update(13.0)               # bar 3: TSI +100 rising, price rising -> keep +100
    100.0
    """

    def __init__(self, q: int = 2, r: int = 32, s: int = 32, u: int = 7,
                 x: int = 32, y: int = 7) -> None:
        """Create an SD_TSI.

        ``q`` momentum look-back (book uses q=2, one-bar momentum); ``r,s,u`` are
        the TSI EMA periods; ``x,y`` are the price double-EMA periods. The book's
        recommended noise-cleaned setting is SD_TSI(close, 32, 32, 7, 32, 7)
        (Fig. 12-2); the raw form of Fig. 12-1 is SD_TSI(close, 32, 32, 1, 32, 1).
        """
        if q < 1:
            raise ValueError(f"q must be >= 1, got {q!r}")
        # r, s, u, x, y are validated by the EMA constructors below.
        self._q = q

        # Rolling window of recent prices for the q-period momentum.
        self._history: deque[float] = deque(maxlen=q)

        # --- TSI machinery: two chained 3-stage EMA cascades (TEMA). --------- #
        # Numerator: TEMA(momentum, r, s, u); denominator: TEMA(|momentum|).
        self._num_r = ExponentialMovingAverage(r)
        self._num_s = ExponentialMovingAverage(s)
        self._num_u = ExponentialMovingAverage(u)
        self._den_r = ExponentialMovingAverage(r)
        self._den_s = ExponentialMovingAverage(s)
        self._den_u = ExponentialMovingAverage(u)

        # --- Price reference: DEMA(close, x, y) = EMA(EMA(close, x), y). ----- #
        self._ref_x = ExponentialMovingAverage(x)
        self._ref_y = ExponentialMovingAverage(y)

        # --- Slope state (previous-bar samples for the two series). --------- #
        self._prev_tsi: float = 0.0      # previous finite TSI; valid once primed
        self._have_prev_tsi: bool = False
        self._prev_ref: float = 0.0      # previous-bar price DEMA
        self._have_prev_ref: bool = False

    def update(self, price: float) -> float:
        """Feed one close ``price`` and return this bar's SD_TSI value."""
        # 1) Advance the price DEMA every bar (it never has a NaN warm-up). ---- #
        ref = self._ref_y.update(self._ref_x.update(price))

        # 2) Compute the TSI for this bar (NaN during the momentum warm-up). --- #
        self._history.append(price)
        if len(self._history) < self._q:
            # TSI undefined: propagate NaN. The DEMA keeps advancing so we keep
            # its previous-bar value current for when the TSI comes online.
            self._prev_ref = ref
            self._have_prev_ref = True
            return float("nan")

        # mtm_k = C_k - C_(k-(q-1)); leftmost deque element is C_(k-(q-1)).
        mtm = price - self._history[0]
        abs_mtm = abs(mtm)
        n = self._num_u.update(self._num_s.update(self._num_r.update(mtm)))
        d = self._den_u.update(self._den_s.update(self._den_r.update(abs_mtm)))
        # TSI division guard (Blau_TSI): denominator 0 -> 0.0.
        tsi = 0.0 if d == 0.0 else 100.0 * n / d

        # 3) Slope-divergence gate (Fig. B-25, strict inequalities). ---------- #
        if not self._have_prev_tsi:
            # First finite TSI sample: no prior TSI -> no slope -> output 0.0.
            result = 0.0
        else:
            d_tsi = tsi - self._prev_tsi
            d_ref = ref - self._prev_ref
            # Keep the TSI only when BOTH slopes are strictly same-signed:
            # (rising, rising) or (falling, falling). Ties (delta == 0) -> 0.0.
            if (d_tsi > 0.0 and d_ref > 0.0) or (d_tsi < 0.0 and d_ref < 0.0):
                result = tsi
            else:
                result = 0.0

        # 4) Roll slope state forward (both series are finite from here on). -- #
        self._prev_tsi = tsi
        self._have_prev_tsi = True
        self._prev_ref = ref
        self._have_prev_ref = True
        return result


def sd_tsi_series(values, q=2, r=32, s=32, u=7, x=32, y=7):
    """Convenience: run a whole list of closes through a fresh SD_TSI."""
    sd = SlopeDivergenceTsiFilter(q=q, r=r, s=s, u=u, x=x, y=y)
    return [sd.update(v) for v in values]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_R*_S*_U*_X*_Y*    #
    # reference arrays and APPENDS them to the five test fixtures in this      #
    # directory (test_testdata.py, testdata_test.go, testdata.ts,            #
    # testdata.rs, testdata.zig).                                            #
    #                                                                         #
    # SD_TSI consumes a single close series (INPUT_CLOSE below, identical to   #
    # INPUT_CLOSE in the fixtures). All combos use the book momentum q=2, so   #
    # there is exactly ONE NaN warm-up value (bar 0); the Go fixture therefore #
    # imports "math". Every finite value lies in [-100, 100].                  #
    # ====================================================================== #

    INPUT_CLOSE = [
        91.500000, 94.815000, 94.375000, 95.095000, 93.780000, 94.625000, 92.530000, 92.750000, 90.315000, 92.470000,
        96.125000, 97.250000, 98.500000, 89.875000, 91.000000, 92.815000, 89.155000, 89.345000, 91.625000, 89.875000,
        88.375000, 87.625000, 84.780000, 83.000000, 83.500000, 81.375000, 84.440000, 89.250000, 86.375000, 86.250000,
        85.250000, 87.125000, 85.815000, 88.970000, 88.470000, 86.875000, 86.815000, 84.875000, 84.190000, 83.875000,
        83.375000, 85.500000, 89.190000, 89.440000, 91.095000, 90.750000, 91.440000, 89.000000, 91.000000, 90.500000,
        89.030000, 88.815000, 84.280000, 83.500000, 82.690000, 84.750000, 85.655000, 86.190000, 88.940000, 89.280000,
        88.625000, 88.500000, 91.970000, 91.500000, 93.250000, 93.500000, 93.155000, 91.720000, 90.000000, 89.690000,
        88.875000, 85.190000, 83.375000, 84.875000, 85.940000, 97.250000, 99.875000, 104.940000, 106.000000, 102.500000,
        102.405000, 104.595000, 106.125000, 106.000000, 106.065000, 104.625000, 108.625000, 109.315000, 110.500000, 112.750000,
        123.000000, 119.625000, 118.750000, 119.250000, 117.940000, 116.440000, 115.190000, 111.875000, 110.595000, 118.125000,
        116.000000, 116.000000, 112.000000, 113.750000, 112.940000, 116.000000, 120.500000, 116.620000, 117.000000, 115.250000,
        114.310000, 115.500000, 115.870000, 120.690000, 120.190000, 120.750000, 124.750000, 123.370000, 122.940000, 122.560000,
        123.120000, 122.560000, 124.620000, 129.250000, 131.000000, 132.250000, 131.000000, 132.810000, 134.000000, 137.380000,
        137.810000, 137.880000, 137.250000, 136.310000, 136.250000, 134.630000, 128.250000, 129.000000, 123.870000, 124.810000,
        123.000000, 126.250000, 128.380000, 125.370000, 125.690000, 122.250000, 119.370000, 118.500000, 123.190000, 123.500000,
        122.190000, 119.310000, 123.310000, 121.120000, 123.370000, 127.370000, 128.500000, 123.870000, 122.940000, 121.750000,
        124.440000, 122.000000, 122.370000, 122.940000, 124.000000, 123.190000, 124.560000, 127.250000, 125.870000, 128.860000,
        132.000000, 130.750000, 134.750000, 135.000000, 132.380000, 133.310000, 131.940000, 130.000000, 125.370000, 130.130000,
        127.120000, 125.190000, 122.000000, 125.000000, 123.000000, 123.500000, 120.060000, 121.000000, 117.750000, 119.870000,
        122.000000, 119.190000, 116.370000, 113.500000, 114.250000, 110.000000, 105.060000, 107.000000, 107.870000, 107.000000,
        107.120000, 107.000000, 91.000000, 93.940000, 93.870000, 95.500000, 93.000000, 94.940000, 98.250000, 96.750000,
        94.810000, 94.370000, 91.560000, 90.250000, 93.940000, 93.620000, 97.000000, 95.000000, 95.870000, 94.060000,
        94.620000, 93.750000, 98.000000, 103.940000, 107.870000, 106.060000, 104.500000, 105.000000, 104.190000, 103.060000,
        103.420000, 105.270000, 111.870000, 116.000000, 116.620000, 118.280000, 113.370000, 109.000000, 109.700000, 109.250000,
        107.000000, 109.190000, 110.000000, 109.200000, 110.120000, 108.000000, 108.620000, 109.750000, 109.810000, 109.000000,
        108.750000, 107.870000,
    ]

    # Parameter combinations (r, s, u, x, y, what-it-tests). q is fixed at the
    # book value 2 for every combo (one NaN warm-up at bar 0). 16 arrays.
    COMBOS = [
        (32, 32, 7, 32, 7, "Book noise-cleaned default SD_TSI(32,32,7,32,7) (Fig 12-2)."),
        (32, 32, 1, 32, 1, "Book raw double-smoothed SD_TSI(32,32,1,32,1) (Fig 12-1)."),
        (32, 32, 7, 32, 1, "Cleaned TSI (u=7), single-EMA price ref (y=1)."),
        (32, 32, 1, 32, 7, "Raw TSI (u=1), double-EMA price ref (y=7)."),
        (1, 1, 1, 1, 1, "Full passthrough: TSI=+/-100, ref=close."),
        (20, 5, 3, 20, 3, "MQL5-style TSI periods with matching price DEMA."),
        (32, 13, 3, 32, 7, "TSI_Trade-like TSI periods, cleaned price ref."),
        (12, 12, 1, 12, 1, "Fast double-smoothed both."),
        (25, 13, 1, 25, 1, "Alternate book periods, raw."),
        (64, 64, 7, 32, 7, "Very slow TSI, medium price ref."),
        (32, 32, 7, 16, 3, "Default TSI, faster price ref."),
        (5, 5, 5, 5, 5, "Equal short triple smoothing throughout."),
        (10, 10, 1, 10, 1, "Medium double-smoothed both."),
        (40, 20, 5, 32, 7, "Asymmetric TSI, cleaned price ref."),
        (32, 5, 1, 32, 1, "Ergodic-style TSI(32,5), single price EMA."),
        (50, 25, 1, 50, 1, "Very slow double-smoothed both."),
    ]

    def name(r, s, u, x, y):
        """Param shortcut, e.g. (32,32,7,32,7) -> 'R32_S32_U7_X32_Y7'."""
        return f"R{r}_S{s}_U{u}_X{x}_Y{y}"

    def params(r, s, u, x, y):
        return f"q=2, r={r}, s={s}, u={u}, x={x}, y={y}"

    def fmt(v, nan_token):
        """Shortest round-tripping literal, or the language's NaN token."""
        if math.isnan(v):
            return nan_token
        return repr(float(v))

    def wrap(values, indent, nan_token, per_line=4):
        lines = []
        for i in range(0, len(values), per_line):
            chunk = ", ".join(fmt(v, nan_token) for v in values[i:i + per_line])
            lines.append(f"{indent}{chunk},")
        return "\n".join(lines)

    # Compute all series once (q fixed at the book value 2).
    results = [
        (r, s, u, x, y, desc,
         sd_tsi_series(INPUT_CLOSE, q=2, r=r, s=s, u=u, x=x, y=y))
        for (r, s, u, x, y, desc) in COMBOS
    ]

    # ---- Python: EXPECTED_<name> = [ ... ] -------------------------------- #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for r, s, u, x, y, desc, vals in results:
            f.write(f"# {desc}\n# {params(r,s,u,x,y)}\n")
            f.write(f"EXPECTED_{name(r,s,u,x,y)} = [\n")
            f.write(wrap(vals, "    ", "float('nan')") + "\n]\n\n")

    # ---- Go: var expected<Name> = []float64{ ... } ----------------------- #
    # (One NaN at bar 0, so the fixture imports "math".)
    with open("testdata_test.go", "a") as f:
        f.write("\n")
        for r, s, u, x, y, desc, vals in results:
            f.write(f"// {desc}\n// {params(r,s,u,x,y)}\n")
            f.write(f"var expected{name(r,s,u,x,y)} = []float64{{\n")
            f.write(wrap(vals, "\t", "math.NaN()") + "\n}\n\n")

    # ---- TypeScript: export const expected<Name>: number[] = [ ... ] ------ #
    with open("testdata.ts", "a") as f:
        f.write("\n")
        for r, s, u, x, y, desc, vals in results:
            f.write(f"// {desc}\n// {params(r,s,u,x,y)}\n")
            f.write(f"export const expected{name(r,s,u,x,y)}: number[] = [\n")
            f.write(wrap(vals, "    ", "NaN") + "\n];\n\n")

    # ---- Rust: pub fn expected_<name>() -> Vec<f64> { vec![ ... ] } ------- #
    with open("testdata.rs", "a") as f:
        f.write("\n")
        for r, s, u, x, y, desc, vals in results:
            f.write(f"// {desc}\n// {params(r,s,u,x,y)}\n")
            f.write(f"pub fn expected_{name(r,s,u,x,y).lower()}() -> Vec<f64> {{\n")
            f.write("    vec![\n")
            f.write(wrap(vals, "        ", "f64::NAN") + "\n    ]\n}\n\n")

    # ---- Zig: pub fn expected<Name>() [252]f64 { return .{ ... }; } ------- #
    with open("testdata.zig", "a") as f:
        f.write("\n")
        for r, s, u, x, y, desc, vals in results:
            f.write(f"// {desc}\n// {params(r,s,u,x,y)}\n")
            f.write(f"pub fn expected{name(r,s,u,x,y)}() [{len(vals)}]f64 {{\n")
            f.write("    return .{\n")
            f.write(wrap(vals, "        ", "nan") + "\n    };\n}\n\n")

    print(f"Generated {len(results)} arrays x 5 languages "
          f"({len(INPUT_CLOSE)} values each).")
