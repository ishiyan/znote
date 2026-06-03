"""Schaff Trend Cycle (STC) -- Doug Schaff (developed late 1990s, code 2008).

STC is a cyclical, 0-100 bounded oscillator built by running a MACD line through
**two cascaded stochastics**, each followed by an EMA-style smoothing:

    XMAC_k = EMA(close, fast)_k - EMA(close, slow)_k          (a MACD line)

    # 1st stochastic of the MACD, smoothed:
    LL1 = min(XMAC over tclen);  HH1 = max(XMAC over tclen)
    Frac1_k = 100 * (XMAC_k - LL1) / (HH1 - LL1)   if HH1 > LL1 else Frac1_{k-1}
    PF_k    = PF_{k-1} + factor * (Frac1_k - PF_{k-1})       (EMA, alpha = factor)

    # 2nd stochastic of PF, smoothed -> STC:
    LL2 = min(PF over tclen);  HH2 = max(PF over tclen)
    Frac2_k = 100 * (PF_k - LL2) / (HH2 - LL2)     if HH2 > LL2 else Frac2_{k-1}
    STC_k   = PFF_{k-1} + factor * (Frac2_k - PFF_{k-1})     (EMA, alpha = factor)

The public output is ``STC`` (= ``PFF``), bounded to [0, 100]. Overbought/oversold
bands are conventionally 75/25 (some platforms use 80/20).

=====================================================================
SOURCE-OF-TRUTH / CONFORMANCE  (read this before changing numerics)
=====================================================================
Doug Schaff never published a defining article, white paper, or book giving the
STC formula or its default parameters, so there is **no authorial ground truth**.
Public implementations (pandas-ta-classic, freqtrade/technical, bukosabino/ta,
several MQL5 ports) **do not agree** with one another. This file therefore makes
no claim of *authorial* correctness; it is **byte-for-byte concordant with a
declared reference**:

    ProRealCode "schaff-trend-cycle2" (F. Malagrida, 2017)
    https://www.prorealcode.com/prorealtime-indicators/schaff-trend-cycle2/

Every output we emit is "concordant with that reference at the stated
parameters", nothing more. See description.md Part A for the full verification
argument and the catalogued disagreements.

The reference is the ProBuilder code (verbatim):

    TCLen = 10 ; MA1 = 23 ; MA2 = 50 ; Once Factor = 0.5
    if barindex > MA2 then
      XMAC = ExponentialAverage[MA1](Close) - ExponentialAverage[MA2](Close)
      Value1 = Lowest[TCLen](XMAC)
      Value2 = Highest[TCLen](XMAC) - Value1
      if Value2 > 0 then Frac1 = ((XMAC - Value1)/Value2) * 100 else Frac1 = Frac1[1] endif
      PF = PF[1] + (Factor * (Frac1 - PF[1]))
      Value3 = Lowest[TCLen](PF)
      Value4 = Highest[TCLen](PF) - Value3
      if Value4 > 0 then Frac2 = ((PF - Value3)/Value4) * 100 else Frac2 = Frac2[1] endif
      PFF = PFF[1] + (Factor * (Frac2 - PFF[1]))
    endif
    RETURN PFF

Faithful-port subtleties that materially change the numbers (do NOT "fix"):

  * GATE.  ``XMAC``, ``Frac1``, ``PF``, ``Frac2`` and ``PFF`` are only ASSIGNED
    while ``barindex > MA2`` (= ``slow``). Before that they hold ProRealTime's
    default 0. So XMAC and PF are **0 on bars 0..slow** -- and those zeros DO
    enter the ``Lowest``/``Highest`` windows, biasing the first ~``tclen`` finite
    outputs. We reproduce this exactly (the windows are fed the gated 0s).
  * EMA SEEDING.  ``ExponentialAverage`` runs over the WHOLE history (it is a
    built-in, not gated): both price EMAs accumulate from bar 0. We assume
    ProRealTime seeds the EMA at e_0 = close_0 (standard recursive EMA), which
    matches the embedded Blau EMA below. This is a declared degree of freedom.
  * RECURSION SEED.  ``PF[1]`` / ``PFF[1]`` default to 0 on the first computed
    bar, so PF and PFF seed at 0 (NOT at their first %K). Hence ``factor`` acts
    as the EMA alpha with a zero seed.
  * FLAT-WINDOW GUARD.  guard is on the **range** ``HH - LL > 0`` (NOT on the
    lowest value); when flat, carry the previous **%K** (``Frac``) forward. The
    well-known pandas-ta-classic bug guards the *first* stochastic on
    ``lowest > 0`` instead -- see description.md A.3.

WARM-UP / OUTPUT CONVENTION.  We emit ``stc = NaN`` for bars ``0..slow`` (the
pre-gate region, where ProRealTime would merely show its default 0), and a
finite value from bar ``slow+1`` onward. The intermediate ``macd`` and ``pf``
fields are emitted as their true internal values (0.0 in the pre-gate region),
because those zeros are real state that feeds the stochastic windows.

OUTPUT.  Each :meth:`update` returns a named tuple ``(stc, macd, pf)``:
  * ``stc``  -- the indicator, [0, 100], NaN during warm-up;
  * ``macd`` -- the gated MACD line XMAC (0 pre-gate); for stage testing;
  * ``pf``   -- the first smoothed %D (0 pre-gate); for stage testing.
Exposing the two intermediates lets a porting agent localize a discrepancy to a
specific cascade stage (the reason STC ports disagree -- description.md A.2/A.3).

Standard library only (no numpy/pandas) for a 1:1 port to Rust/Zig/Go.
"""

from __future__ import annotations

import math
from collections import deque, namedtuple


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
# INDICATOR: Schaff Trend Cycle (single output + two stage intermediates).#
# ====================================================================== #

# ``stc`` is the indicator (range [0, 100], NaN during warm-up). ``macd`` and
# ``pf`` are the reference's internal cascade stages, exposed for stage testing
# (both 0.0 in the pre-gate region, where the reference's variables default to 0).
STCResult = namedtuple("STCResult", ["stc", "macd", "pf"])


class SchaffTrendCycle:
    """Stateful, streaming Schaff Trend Cycle (STC).

    Feed one ``close`` at a time to :meth:`update`; it returns an
    :class:`STCResult` ``(stc, macd, pf)`` for that bar. ``stc`` is NaN while the
    pre-gate look-back is unmet (bars 0..slow) and finite, in [0, 100],
    afterward; ``macd``/``pf`` are the internal cascade stages (0.0 pre-gate).

    Example (defaults; warm-up NaN, intermediates 0.0 before the gate opens):
    >>> s = SchaffTrendCycle(fast=23, slow=50, tclen=10, factor=0.5)
    >>> r = s.update(100.0)              # bar 0, deep in the pre-gate region
    >>> (math.isnan(r.stc), r.macd, r.pf)
    (True, 0.0, 0.0)
    """

    def __init__(self, fast: int = 23, slow: int = 50, tclen: int = 10,
                 factor: float = 0.5) -> None:
        """Create an STC with MACD periods ``fast``/``slow``, cycle ``tclen`` and
        EMA smoothing ``factor`` (the %D alpha).

        Defaults are the forex-native ProRealCode reference set
        (fast=23, slow=50, tclen=10, factor=0.5). The generic/library default
        seen in pandas-ta is fast=12, slow=26 (same tclen/factor). The period
        pair is a **declared input**, never an authorial constant.

        Raises ``ValueError`` for non-positive periods or ``factor`` outside
        (0, 1].
        """
        if fast < 1:
            raise ValueError(f"fast must be >= 1, got {fast!r}")
        if slow < 1:
            raise ValueError(f"slow must be >= 1, got {slow!r}")
        if tclen < 1:
            raise ValueError(f"tclen must be >= 1, got {tclen!r}")
        if not (0.0 < factor <= 1.0):
            raise ValueError(f"factor must be in (0, 1], got {factor!r}")

        self._slow = slow
        self._tclen = tclen
        self._factor = factor

        # Two price EMAs forming the MACD line (run EVERY bar; built-ins are not
        # gated in the reference, so they accumulate from bar 0).
        self._ema_fast = ExponentialMovingAverage(fast)
        self._ema_slow = ExponentialMovingAverage(slow)

        # 0-based bar counter (ProRealTime ``barindex``).
        self._bar = -1

        # Rolling windows of the last ``tclen`` XMAC and PF values. These are fed
        # EVERY bar, INCLUDING the pre-gate zeros, so ``Lowest``/``Highest`` see
        # exactly what the reference sees.
        self._macd_win: deque[float] = deque(maxlen=tclen)
        self._pf_win: deque[float] = deque(maxlen=tclen)

        # Carried recursion state. All default to 0.0, matching ProRealTime's
        # default for an as-yet-unassigned variable / ``[1]`` back-reference.
        self._frac1 = 0.0   # 1st-stochastic %K (carried when its range is flat)
        self._frac2 = 0.0   # 2nd-stochastic %K (carried when its range is flat)
        self._pf = 0.0      # 1st smoothed %D  (PF),  seed 0
        self._pff = 0.0     # 2nd smoothed %D  (PFF = STC), seed 0

    def update(self, close: float) -> STCResult:
        """Feed one ``close``; return (stc, macd, pf) for this bar."""
        self._bar += 1
        k = self._bar

        # Price EMAs always advance (they accumulate over the full history).
        ema_fast = self._ema_fast.update(close)
        ema_slow = self._ema_slow.update(close)

        # GATE: XMAC is only assigned while barindex > slow; before that it holds
        # ProRealTime's default 0.0. The window is fed either way.
        gate_open = k > self._slow
        macd = (ema_fast - ema_slow) if gate_open else 0.0
        self._macd_win.append(macd)

        if not gate_open:
            # Pre-gate: PF/PFF stay 0; push the 0 into PF's window too. STC is not
            # a meaningful output yet -> NaN. macd/pf are reported as their true
            # internal values (0.0) for stage testing.
            self._pf_win.append(self._pf)
            return STCResult(float("nan"), macd, self._pf)

        # --- 1st stochastic of the MACD over tclen (guard on the RANGE) -------- #
        ll1 = min(self._macd_win)
        rng1 = max(self._macd_win) - ll1
        if rng1 > 0.0:
            self._frac1 = ((macd - ll1) / rng1) * 100.0
        # else: flat window -> carry the previous %K (self._frac1) unchanged.

        # --- 1st smoothing: PF = EMA(Frac1, alpha=factor), seed 0 ------------- #
        self._pf = self._pf + self._factor * (self._frac1 - self._pf)
        self._pf_win.append(self._pf)

        # --- 2nd stochastic of PF over tclen ---------------------------------- #
        ll2 = min(self._pf_win)
        rng2 = max(self._pf_win) - ll2
        if rng2 > 0.0:
            self._frac2 = ((self._pf - ll2) / rng2) * 100.0
        # else: carry the previous %K (self._frac2) unchanged.

        # --- 2nd smoothing: STC = PFF = EMA(Frac2, alpha=factor), seed 0 ------ #
        self._pff = self._pff + self._factor * (self._frac2 - self._pff)
        return STCResult(self._pff, macd, self._pf)


def stc_series(closes, fast=23, slow=50, tclen=10, factor=0.5):
    """Convenience: run a whole list of closes through a fresh STC.

    Returns three parallel lists: ``(stc_values, macd_values, pf_values)``.
    """
    s = SchaffTrendCycle(fast=fast, slow=slow, tclen=tclen, factor=factor)
    out = [s.update(c) for c in closes]
    return [o.stc for o in out], [o.macd for o in out], [o.pf for o in out]


if __name__ == "__main__":
    # ====================================================================== #
    # PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
    # ---------------------------------------------------------------------- #
    # Running this file as a script regenerates the EXPECTED_* reference      #
    # arrays and APPENDS them to the five test fixtures in this directory     #
    # (test_testdata.py, testdata_test.go, testdata.ts, testdata.rs,          #
    # testdata.zig). STC is close-only; the Close series is embedded below    #
    # (identical to INPUT_CLOSE / testInput in the fixtures, bit-for-bit).    #
    #                                                                         #
    # Per combo we always emit the STC line (NaN in the bars 0..slow warm-up  #
    # region). For a few representative combos we ALSO emit the ``macd`` and  #
    # ``pf`` intermediate stages (no NaN -- 0.0 in the pre-gate region) so a  #
    # porting agent can localize a discrepancy to a specific cascade stage.   #
    # Because the STC arrays contain NaN, the Go fixture DOES need "math".     #
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

    # Parameter combinations. Tuple = (fast, slow, tclen, factor, emit_stages,
    # what-it-tests). ``emit_stages`` adds the macd + pf intermediate arrays for
    # that combo (used on a representative few to keep within the array budget).
    COMBOS = [
        (23, 50, 10, 0.5, True,  "Reference forex default STC(23,50,10,0.5)."),
        (12, 26, 10, 0.5, True,  "Generic/pandas-ta default STC(12,26,10,0.5)."),
        (5, 10, 5, 0.5, True,    "Small periods: gate opens early (bar 11)."),
        (3, 7, 3, 0.5, False,    "Tiny everything; gate at bar 8, fast cascade."),
        (8, 21, 10, 0.5, False,  "Alt fast/slow 8/21, default cycle."),
        (10, 30, 10, 0.5, False, "Round 10/30 periods."),
        (15, 40, 14, 0.5, False, "Slow 15/40, longer cycle 14."),
        (6, 13, 8, 0.6, False,   "6/13 periods, faster smoothing factor 0.6."),
        (23, 50, 23, 0.5, False, "Default periods, long cycle tclen=23."),
        (23, 50, 5, 0.5, False,  "Default periods, short cycle tclen=5."),
        (12, 26, 10, 0.25, False,"Generic periods, slow smoothing factor 0.25."),
        (12, 26, 10, 0.8, False, "Generic periods, fast smoothing factor 0.8."),
        (12, 26, 10, 1.0, False, "factor=1.0 edge: PF=Frac1, PFF=Frac2 (no smooth)."),
        (20, 40, 10, 0.5, False, "Round 20/40 periods, default cycle/factor."),
    ]

    def name(fast, slow, tclen, factor):
        """Param shortcut, e.g. (23,50,10,0.5) -> 'F23_S50_T10_C50'."""
        return f"F{fast}_S{slow}_T{tclen}_C{int(round(factor * 100))}"

    def params(fast, slow, tclen, factor):
        return f"fast={fast}, slow={slow}, tclen={tclen}, factor={factor}"

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

    # Compute every series once. ``outputs`` is a flat list of records:
    #   (kind_upper, kind_camel, kind_snake, label, shortcut, paramline, vals)
    # ``stc`` is emitted for every combo; ``macd``/``pf`` only when emit_stages.
    outputs = []
    for fast, slow, tclen, factor, emit_stages, desc in COMBOS:
        stc_vals, macd_vals, pf_vals = stc_series(
            INPUT_CLOSE, fast=fast, slow=slow, tclen=tclen, factor=factor)
        sc = name(fast, slow, tclen, factor)
        pl = params(fast, slow, tclen, factor)
        outputs.append(("STC", "Stc", "stc", f"STC oscillator: {desc}", sc, pl, stc_vals))
        if emit_stages:
            outputs.append(("MACD", "Macd", "macd",
                            f"MACD stage (XMAC, gated): {desc}", sc, pl, macd_vals))
            outputs.append(("PF", "Pf", "pf",
                            f"1st smoothed %D stage (PF): {desc}", sc, pl, pf_vals))

    # ---- Python: EXPECTED_STC_<name> / _MACD_ / _PF_ = [ ... ] ------------ #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"# {label}\n# {pl}\n")
            f.write(f"EXPECTED_{ku}_{sc} = [\n")
            f.write(wrap(vals, "    ", "float('nan')") + "\n]\n\n")

    # ---- Go: var expectedStc<Name> / expectedMacd / expectedPf = []float64 - #
    with open("testdata_test.go", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"// {label}\n// {pl}\n")
            f.write(f"var expected{kc}{sc} = []float64{{\n")
            f.write(wrap(vals, "\t", "math.NaN()") + "\n}\n\n")

    # ---- TypeScript: export const expectedStc<Name>: number[] = [ ... ] ---- #
    with open("testdata.ts", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"// {label}\n// {pl}\n")
            f.write(f"export const expected{kc}{sc}: number[] = [\n")
            f.write(wrap(vals, "    ", "NaN") + "\n];\n\n")

    # ---- Rust: pub fn expected_stc_<name>() -> Vec<f64> { vec![ ... ] } ---- #
    with open("testdata.rs", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"// {label}\n// {pl}\n")
            f.write(f"pub fn expected_{ks}_{sc.lower()}() -> Vec<f64> {{\n")
            f.write("    vec![\n")
            f.write(wrap(vals, "        ", "f64::NAN") + "\n    ]\n}\n\n")

    # ---- Zig: pub fn expectedStc<Name>() [252]f64 { return .{ ... }; } ----- #
    with open("testdata.zig", "a") as f:
        f.write("\n")
        for ku, kc, ks, label, sc, pl, vals in outputs:
            f.write(f"// {label}\n// {pl}\n")
            f.write(f"pub fn expected{kc}{sc}() [{len(vals)}]f64 {{\n")
            f.write("    return .{\n")
            f.write(wrap(vals, "        ", "nan") + "\n    };\n}\n\n")

    print(f"Generated {len(outputs)} arrays x 5 languages "
          f"({len(INPUT_CLOSE)} values each, {len(COMBOS)} combos).")
