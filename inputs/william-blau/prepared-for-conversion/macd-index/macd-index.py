"""MACD Index (MACD_I) -- William Blau (book ch. 5 / Appendix B-13).

Blau's MACD line is the difference of two EMAs of the close, optionally smoothed
by a third EMA, paired with an EMA signal line (the Ergodic form, Blau ch. 5):

    macd_k   = EMA(close, s)_k - EMA(close, r)_k         (MACD line; s fast, r slow)
    macdi_k  = EMA(macd, u)_k                            (the MACD_I line)
    signal_k = EMA(macdi, ul)_k                          (ul-period EMA)

with the **fast** period ``s`` strictly shorter than the **slow** period ``r``
(``s < r``). The book (ch. 5) defines the pure form
``MACD(close, r, s) = EMA(close, s) - EMA(close, r)``; the MQL5 ``Blau_MACD.mq5``
code adds the third smoothing ``u``, giving the form above. Set ``u = 1`` to
recover the book's pure two-EMA MACD line. Blau notes the MACD and the MDI are
both double-smoothed momentum indicators with nearly interchangeable shapes
(within a scale factor).

**It is NOT normalized.** There is no ``100 * TEMA/TEMA`` ratio and no fixed
range: the output is in the same price units as the input (the classic MACD line)
and can take any sign or magnitude. **Input is a single price series (Close).**

It is a TWO-output indicator: each :meth:`update` returns a named tuple
``(macdi, signal)`` and :func:`macd_i_series` returns two parallel lists.

The EMA primitive is **embedded** below (inlined, not imported) so this file is a
self-contained porting unit -- agents porting to Go/Rust/TS/Zig need only this
file and ``description.md``.

Priming: both price EMAs are defined from bar 0 (they seed at ``close_0``), so the
MACD line is ``0.0`` at bar 0 and finite on every bar. There is therefore NO NaN
warm-up region. The ``u`` smoothing and the signal EMA likewise seed on bar 0.

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math
from collections import namedtuple


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
# INDICATOR: MACD Index (two-output: line + signal).                      #
# ====================================================================== #

# Two-output result. ``macdi`` is the MACD_I line; ``signal`` is its ul-period
# EMA (the Ergodic signal line). Both are finite from bar 0 (no NaN warm-up)
# and both are in raw price units (NOT bounded to any range).
MacdiResult = namedtuple("MacdiResult", ["macdi", "signal"])


class MacdIndex:
    """Stateful, streaming Blau MACD (MACD_I) with an EMA signal line.

    Feed one ``close`` at a time to :meth:`update`, which returns a
    :class:`MacdiResult` ``(macdi, signal)`` for that bar. Both fields are finite
    on EVERY bar (there is no NaN warm-up; bar 0 is 0.0) and in **raw price
    units** (NOT bounded to any range).

    Example (r=2 slow, s=1 fast, u=1 -> book pure MACD line, ul=1 passthrough):
    >>> m = MacdIndex(r=2, s=1, u=1, ul=1)
    >>> o0 = m.update(10.0); (round(o0.macdi, 4), round(o0.signal, 4))  # bar 0
    (0.0, 0.0)
    >>> o1 = m.update(12.0); (round(o1.macdi, 4), round(o1.signal, 4))  # 12-11.3333
    (0.6667, 0.6667)

    Example (s >= r is rejected -- fast must be strictly shorter than slow):
    >>> MacdIndex(r=5, s=5)
    Traceback (most recent call last):
        ...
    ValueError: s (fast) must be < r (slow); got s=5, r=5
    """

    def __init__(self, r: int = 20, s: int = 5, u: int = 3,
                 ul: int = 3) -> None:
        """Create a MACD_I with slow period ``r``, fast period ``s`` (``s < r``),
        smoothing period ``u`` and signal-line period ``ul``.

        Defaults are the MQL5/book defaults (r=20 slow, s=5 fast, u=3) plus the
        Ergodic signal default ul=3. Set ``u=1`` for the book's pure two-EMA
        MACD line ``EMA(close, s) - EMA(close, r)``; set ``ul=1`` for a
        passthrough signal (signal == macdi).

        Raises ``ValueError`` if ``s >= r`` -- the MACD line is fast minus slow,
        so the fast period must be strictly shorter than the slow period
        (``s == r`` gives an identically-zero line; ``s > r`` flips the sign).
        """
        if s >= r:
            raise ValueError(
                f"s (fast) must be < r (slow); got s={s!r}, r={r!r}"
            )
        # r, s, u, ul are validated by the EMA constructors below.

        # The two price EMAs forming the MACD line = EMA(close, s) - EMA(close, r).
        self._ema_fast = ExponentialMovingAverage(s)
        self._ema_slow = ExponentialMovingAverage(r)

        # Third smoothing EMA applied to the MACD line: EMA(macd, u).
        self._smooth_u = ExponentialMovingAverage(u)

        # Signal line: a ul-period EMA of the MACD_I line. The line is finite
        # from bar 0, so this seeds on bar 0 -- no NaN warm-up.
        self._signal_ema = ExponentialMovingAverage(ul)

    def update(self, close: float) -> MacdiResult:
        """Feed one ``close``; return (macdi, signal) for this bar."""
        # MACD line = fast EMA - slow EMA. Both seed at bar 0 (to close_0), so
        # the line is 0.0 on bar 0 and defined on every bar thereafter.
        macd = self._ema_fast.update(close) - self._ema_slow.update(close)

        # Smooth the MACD line: EMA(macd, u). No normalization, no guard.
        macdi = self._smooth_u.update(macd)

        # Signal line = EMA(macdi, ul); seeds on bar 0's line value.
        signal = self._signal_ema.update(macdi)
        return MacdiResult(macdi, signal)


def macd_i_series(values, r=20, s=5, u=3, ul=3):
    """Convenience: run a whole list of closes through a fresh MACD_I.

    Returns two parallel lists: ``(macdi_values, signal_values)``.
    """
    m = MacdIndex(r=r, s=s, u=u, ul=ul)
    out = [m.update(v) for v in values]
    return [o.macdi for o in out], [o.signal for o in out]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_R*_S*_U*         #
    # reference arrays and APPENDS them to the five test fixtures in this     #
    # directory (test_testdata.py, testdata_test.go, testdata.ts,            #
    # testdata.rs, testdata.zig).                                            #
    #                                                                         #
    # MACD_I is close-only. We embed the Close series below (identical to     #
    # INPUT_CLOSE / testInput in the fixtures, bit-for-bit). There is NO NaN  #
    # warm-up region (the MACD line is defined from bar 0, where it is 0.0),  #
    # so every value is finite -- but the output is UNNORMALIZED (raw price   #
    # units, any sign/magnitude), so values may be negative. The Go fixture   #
    # still needs NO "math" import (no NaN ever appears).                     #
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

    # Parameter combinations (r, s, u, what-it-tests). 16 combos -> 32 arrays
    # (each combo emits a MACD line and its ul=3 signal line). r is the SLOW
    # EMA, s the FAST EMA, with s < r REQUIRED; u smooths the MACD line.
    COMBOS = [
        (20, 5, 3, "Catalog/MQL5 default MACD_I(r20,s5,u3)."),
        (20, 5, 1, "Book pure two-EMA MACD line (u=1): EMA(C,s)-EMA(C,r)."),
        (26, 12, 3, "Classic 12/26 MACD periods, triple form."),
        (26, 12, 1, "Classic 12/26 pure MACD line (u=1)."),
        (35, 5, 3, "Wide 5/35 line, default smoothing."),
        (10, 3, 5, "Fast 3/10 line, heavier smoothing."),
        (32, 12, 5, "Slow 32 / fast 12, heavy smoothing."),
        (17, 8, 1, "8/17 line, pure (u=1)."),
        (20, 10, 3, "Round 10/20 line, triple form."),
        (8, 4, 2, "Fast 4/8 line, small smoothing."),
        (30, 15, 1, "Slow 15/30 line, pure (u=1)."),
        (3, 2, 3, "Tiny fastest-ish line and smoothing."),
        (50, 12, 1, "Very slow 12/50 line, pure (u=1)."),
        (19, 6, 3, "6/19 line, default smoothing."),
        (20, 5, 5, "Default line, equal heavier smoothing."),
        (60, 30, 10, "Very long everything."),
    ]

    # Signal-line EMA period for every emitted signal array (Ergodic default).
    UL = 3

    def fmt(x, nan_token):
        """Shortest round-tripping literal, or the language's NaN token."""
        if math.isnan(x):
            return nan_token
        return repr(float(x))

    def wrap(values, indent, nan_token, per_line=4):
        lines = []
        for i in range(0, len(values), per_line):
            chunk = ", ".join(fmt(v, nan_token) for v in values[i:i + per_line])
            lines.append(f"{indent}{chunk},")
        return "\n".join(lines)

    # Compute every series once. Each combo yields two arrays:
    #   * MACD line:   name 'R{r}_S{s}_U{u}'
    #   * signal line: name 'R{r}_S{s}_U{u}_SIG_UL3' (EMA of the line, ul=3)
    # Stored as flat (array_name, description, param_string, values) tuples so
    # the five language emitters stay uniform. MACD_I has no NaN warm-up, so
    # every value (line and signal) is finite (though unnormalized / may be < 0).
    arrays = []
    for r, s, u, desc in COMBOS:
        osc, sig = macd_i_series(INPUT_CLOSE, r=r, s=s, u=u, ul=UL)
        base = f"R{r}_S{s}_U{u}"
        prm = f"r={r}, s={s}, u={u}"
        arrays.append((base, desc, prm, osc))
        arrays.append((
            f"{base}_SIG_UL3",
            f"Signal line: EMA(MACD line, ul={UL}) of {base}.",
            f"{prm}, ul={UL}",
            sig,
        ))

    # ---- Python: EXPECTED_<name> = [ ... ] -------------------------------- #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for nm, desc, prm, vals in arrays:
            f.write(f"# {desc}\n# {prm}\n")
            f.write(f"EXPECTED_{nm} = [\n")
            f.write(wrap(vals, "    ", "float('nan')") + "\n]\n\n")

    # ---- Go: var expected<Name> = []float64{ ... } ----------------------- #
    # (No NaN appears, so NO "math" import is needed in the Go fixture.)
    with open("testdata_test.go", "a") as f:
        f.write("\n")
        for nm, desc, prm, vals in arrays:
            f.write(f"// {desc}\n// {prm}\n")
            f.write(f"var expected{nm} = []float64{{\n")
            f.write(wrap(vals, "\t", "math.NaN()") + "\n}\n\n")

    # ---- TypeScript: export const expected<Name>: number[] = [ ... ] ------ #
    with open("testdata.ts", "a") as f:
        f.write("\n")
        for nm, desc, prm, vals in arrays:
            f.write(f"// {desc}\n// {prm}\n")
            f.write(f"export const expected{nm}: number[] = [\n")
            f.write(wrap(vals, "    ", "NaN") + "\n];\n\n")

    # ---- Rust: pub fn expected_<name>() -> Vec<f64> { vec![ ... ] } ------- #
    with open("testdata.rs", "a") as f:
        f.write("\n")
        for nm, desc, prm, vals in arrays:
            f.write(f"// {desc}\n// {prm}\n")
            f.write(f"pub fn expected_{nm.lower()}() -> Vec<f64> {{\n")
            f.write("    vec![\n")
            f.write(wrap(vals, "        ", "f64::NAN") + "\n    ]\n}\n\n")

    # ---- Zig: pub fn expected<Name>() [252]f64 { return .{ ... }; } ------- #
    with open("testdata.zig", "a") as f:
        f.write("\n")
        for nm, desc, prm, vals in arrays:
            f.write(f"// {desc}\n// {prm}\n")
            f.write(f"pub fn expected{nm}() [{len(vals)}]f64 {{\n")
            f.write("    return .{\n")
            f.write(wrap(vals, "        ", "nan") + "\n    };\n}\n\n")

    print(f"Generated {len(arrays)} arrays x 5 languages "
          f"({len(INPUT_CLOSE)} values each).")

