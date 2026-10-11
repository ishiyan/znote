"""
The AutoTune Filter - research prototype MASTER REFERENCE implementation.

Source article:
    John F. Ehlers, "The AutoTune Filter: A Rolling Autocorrelation Function",
    Technical Analysis of STOCKS & COMMODITIES, Vol. 44, May 2026, pp. 9-15, 31.
    (MESA Software re-print: https://www.mesasoftware.com/papers/The%20AutoTune%20Filter.pdf)

Also implemented in the May 2026 Traders' Tips section (TradeStation/EasyLanguage,
NinjaTrader/C#, TradingView/Pine Script, Zorro/C, Python, RealTest, Wealth-Lab).

This file is the *master* reference: it is deliberately written using ONLY the
Python standard library (no numpy / pandas) so that it can be ported 1:1 to
Rust, Zig, Go, TypeScript and any other language without having to re-implement
vectorised primitives.

Design contract for ports
-------------------------
* Fully STREAMING: feed one input sample at a time into `AutoTune.update()`.
* No look-ahead, no random access to future data.
* Deterministic, pure floating point (IEEE-754 double), same operation order as
  the EasyLanguage original.
* Outputs that are not "primed" yet are returned as NaN. NaN therefore also
  marks the exact warm-up length, which ports must reproduce.

Outputs (see `AutoTuneResult`):
    filt            - two-pole highpass filtered close series ("Filt")
    min_corr        - minimum of the rolling autocorrelation function
    dominant_cycle  - 2 * argmin_lag(corr), rate limited to +/- 2 bars per bar
    bandpass        - bandpass filter tuned bar-by-bar to the dominant cycle
    roc             - two-bar rate of change of `bandpass` (BP - BP[2]),
                      used by the pro-forma strategy to detect peaks/valleys

Run as a script to regenerate the reference test vectors:

    python3 the-autotune-filter.py            # prints the parameter grid
    python3 the-autotune-filter.py --emit py  # writes the Python arrays
    python3 the-autotune-filter.py --emit go|ts|rs|zig
"""

from __future__ import annotations

import math
import os
from typing import List, NamedTuple, Optional

# =============================================================================
# Small helper containers / constants
# =============================================================================

# Number of bars a Bandpass needs before it is switched on (EasyLanguage:
# "If CurrentBar < 3 Then BP = 0;").
BANDPASS_WARMUP_BARS = 3

# Number of bars the Highpass needs before it is switched on (EasyLanguage:
# "If CurrentBar >= 4 Then $HighPass = ...").
HIGHPASS_WARMUP_BARS = 4

# Maximum absolute change of the dominant cycle period allowed from one bar to
# the next (EasyLanguage: "If DC > DC[1] + 2 Then DC = DC[1] + 2;").
MAX_DC_STEP = 2.0


class AutoTuneResult(NamedTuple):
    """One bar of AutoTune output.

    Every field is a float; a field is NaN while the corresponding computation
    is not yet primed on this bar.
    """

    filt: float
    min_corr: float
    dominant_cycle: float
    bandpass: float
    roc: float


# =============================================================================
# Building blocks
# =============================================================================

def highpass_coefficients(period: int) -> tuple:
    """Coefficients of Ehlers' two-pole highpass filter.

    EasyLanguage ("$Highpass Function" sidebar):

        Q  = expvalue(-1.414*3.14159 / Period);
        c1 = 2*Q*Cosine(1.414*180 / Period);
        c2 = Q*Q;
        a0 = (1 + c1 + c2) / 4;

    `Cosine(x)` in EasyLanguage takes DEGREES, so 1.414*180/Period degrees is
    the same angle as 1.414*pi/Period radians.

    Transfer function (in the z-domain), where H(z) is the output and P(z) the
    input price:

        H(z) = a0*(1 - 2 z^-1 + z^-2) + c1 z^-1 H(z) - c2 z^-2 H(z)

    =>  H(z)/P(z) = a0 * (1 - z^-1)^2 / (1 - c1 z^-1 + c2 z^-2)

    The double zero at z = 1 makes the filter remove all trend / low frequency
    content and gives the output a nominally zero mean, which is exactly what
    the autocorrelation computation needs (a trend would bias the correlation).

    Returns:
        (a0, c1, c2)
    """
    q = math.exp(-1.414 * math.pi / float(period))
    c1 = 2.0 * q * math.cos(1.414 * math.pi / float(period))
    c2 = q * q
    a0 = (1.0 + c1 + c2) / 4.0
    return a0, c1, c2


def bandpass_coefficients(period: float, bandwidth: float) -> tuple:
    """Coefficients of Ehlers' bandpass filter.

    EasyLanguage ("Bandpass Filter Function" sidebar):

        L1 = Cosine(360 / Period);
        G1 = Cosine(Bandwidth*360 / Period);
        S1 = 1/G1 - SquareRoot(1/(G1*G1) - 1);
        BP = .5*(1 - S1)*(Price - Price[2])
             + L1*(1 + S1)*BP[1] - S1*BP[2];

    `Bandwidth` is expressed as a FRACTION of the center period (0.25 == 25%),
    i.e. the two half-power band edges sit at
    Period/(1 +- Bandwidth)... more precisely the ratio G1 = cos(B*2*pi/P) is
    the inverse-Q ratio of the equivalent RC ladder network and S1 is the
    pole real part.

    Requirements: period > 0 and 0 < G1 (i.e. Bandwidth*360/Period < 90 deg),
    otherwise the result is NaN/inf.

    Returns:
        (l1, s1, a0, a2) where the recursion is
            BP = a0*(P - P2) + a1*BP1 + a2*BP2
        with a0 = 0.5*(1 - S1), a1 = L1*(1 + S1), a2 = -S1.
    """
    l1 = math.cos(2.0 * math.pi / float(period))
    g1 = math.cos(float(bandwidth) * 2.0 * math.pi / float(period))
    s1 = 1.0 / g1 - math.sqrt(1.0 / (g1 * g1) - 1.0)
    a0 = 0.5 * (1.0 - s1)
    a1 = l1 * (1.0 + s1)
    a2 = -s1
    return a0, a1, a2


def pearson_correlation(sx: float, sy: float, sxx: float, syy: float,
                        sxy: float, n: int) -> Optional[float]:
    """Pearson correlation coefficient from the raw power sums.

        r = (n*Sxy - Sx*Sy) / sqrt((n*Sxx - Sx^2) * (n*Syy - Sy^2))

    Returns None when either variance-like term is not strictly positive
    (EasyLanguage: "If (Window*Sxx - Sx*Sx > 0) and (Window*Syy - Sy*Sy > 0)"),
    which happens when the windowed sample has zero variance (e.g. all filter
    outputs are still the warm-up zeros).
    """
    den_x = n * sxx - sx * sx
    den_y = n * syy - sy * sy
    if den_x > 0.0 and den_y > 0.0:
        return (n * sxy - sx * sy) / math.sqrt(den_x * den_y)
    return None


# =============================================================================
# The indicator
# =============================================================================

class AutoTune:
    """Streaming implementation of Ehlers' AutoTune filter.

    Parameters
    ----------
    window:
        Length (in bars) of BOTH the highpass critical period and the rolling
        autocorrelation window.  The measured dominant cycle is roughly
        proportional to this length (pink-noise argument), so the window also
        acts as a "which cycle do I want to trade" selector.
        Practical range 6..100; article default 20.
    bandwidth:
        Bandwidth of the bandpass filter expressed as a fraction of the tuned
        center period.  Article default 0.25 (25%).  Must satisfy
        0 < bandwidth < 0.5 so that G1 = cos(bw*2*pi/period) stays positive.

    Notes
    -----
    * Warm-up length is `2*window - 1` bars: the autocorrelation with the
      largest lag `window` needs `Filt[window + (window - 1)]`, i.e. the
      oldest filter value used is `Filt[2*window-1]`.
    * All outputs are NaN while not primed (see the module docstring).
    """

    def __init__(self, window: int = 20, bandwidth: float = 0.25) -> None:
        if window < 2:
            raise ValueError("window must be >= 2")
        if not (0.0 < bandwidth < 0.5):
            raise ValueError("bandwidth must satisfy 0 < bandwidth < 0.5")

        self.window = int(window)
        self.bandwidth = float(bandwidth)

        # --- highpass state -------------------------------------------------
        self._hp_a0, self._hp_c1, self._hp_c2 = highpass_coefficients(self.window)
        self._price: List[float] = []   # close prices, oldest first
        self._filt: List[float] = []    # highpass outputs, oldest first

        # --- bandpass state -------------------------------------------------
        self._bp: List[float] = []      # bandpass outputs, oldest first

        # --- dominant cycle state -------------------------------------------
        # `dc` is a *series* variable in EasyLanguage: it keeps its previous
        # value until it is assigned, and the rate limiter compares against
        # DC[1] (previous bar). It starts at 0.0.
        self._dc_prev: float = 0.0

        # scratch buffer for the correlation array (lags 1..window)
        self._corr: List[float] = [0.0] * (self.window + 1)

        self._bar_index: int = -1       # index of the *previous* bar

    # -- introspection helpers used by the porting test harness --------------
    @property
    def warmup_bars(self) -> int:
        """Number of leading bars for which every output is NaN."""
        return 2 * self.window - 1

    # -------------------------------------------------------------------------
    # core
    # -------------------------------------------------------------------------
    def update(self, close: float) -> AutoTuneResult:
        """Push one close price and return the AutoTune outputs for this bar.

        Parameters
        ----------
        close : float
            The bar's close price.

        Returns
        -------
        AutoTuneResult(filt, min_corr, dominant_cycle, bandpass, roc)
        """
        self._bar_index += 1
        t = self._bar_index
        self._price.append(float(close))

        # ------------------------------------------------------------------
        # 1) two-pole highpass filter -> "Filt"
        #    If CurrentBar >= 4:
        #        $HighPass = a0*(Price - 2*Price[1] + Price[2])
        #                  + c1*$HighPass[1] - c2*$HighPass[2]
        #    else 0
        # ------------------------------------------------------------------
        if t < HIGHPASS_WARMUP_BARS:
            filt = 0.0
        else:
            # price[t], price[t-1], price[t-2] - the list is oldest first.
            p0 = self._price[-1]
            p1 = self._price[-2]
            p2 = self._price[-3]
            # filt[t-1], filt[t-2] (both are the warm-up 0.0 on bars 4 and 5,
            # which is exactly what EasyLanguage's persistent series holds).
            f1 = self._filt[-1] if len(self._filt) >= 1 else 0.0
            f2 = self._filt[-2] if len(self._filt) >= 2 else 0.0
            filt = self._hp_a0 * (p0 - 2.0 * p1 + p2) + self._hp_c1 * f1 - self._hp_c2 * f2

        self._filt.append(filt)

        # ------------------------------------------------------------------
        # 2) rolling autocorrelation of Filt, for lag = 1 .. window
        #
        #    Sx  = sum_j Filt[j]          j = 0 .. window-1
        #    Sy  = sum_j Filt[lag+j]      j = 0 .. window-1
        #    Sxx = sum_j Filt[j]^2
        #    Sxy = sum_j Filt[j]*Filt[lag+j]
        #    Syy = sum_j Filt[lag+j]^2
        #
        #    Corr[lag] = (window*Sxy - Sx*Sy)
        #                / sqrt((window*Sxx - Sx*Sx)*(window*Syy - Sy*Sy))
        #
        #    j = 0 is the most recent bar, j = window-1 is window-1 bars ago.
        #    The oldest sample touched is Filt[lag + window - 1] which for
        #    lag = window is Filt[2*window - 1]: the warm-up bound.
        # ------------------------------------------------------------------
        min_corr = math.nan
        dc = math.nan

        if t >= 2 * self.window - 1:
            w = self.window
            # Filt[j] with j = 0 .. w-1  ->  self._filt[-1-j]
            # Filt[lag+j]                 ->  self._filt[-1-lag-j]
            for lag in range(1, w + 1):
                sx = 0.0
                sy = 0.0
                sxx = 0.0
                sxy = 0.0
                syy = 0.0
                for j in range(w):
                    x = self._filt[-1 - j]
                    y = self._filt[-1 - lag - j]
                    sx += x
                    sy += y
                    sxx += x * x
                    sxy += x * y
                    syy += y * y
                r = pearson_correlation(sx, sy, sxx, syy, sxy, w)
                # EasyLanguage leaves a stale array element here; every port
                # (and the Zorro reference) stores 0.0 instead.  We store 0.0.
                self._corr[lag] = 0.0 if r is None else r

            # ---- minimum correlation and dominant cycle ------------------
            #   MinCorr = 1;
            #   For Lag = 1 to Window If Corr[Lag] < MinCorr Then
            #       MinCorr = Corr[Lag]; DC = 2*Lag;
            # Strict "<" means the SHORTEST lag wins ties, which is the
            # "shortest lag with the most negative correlation" rule.
            min_corr = 1.0
            dc_raw = self._dc_prev          # series variable keeps old value
            for lag in range(1, w + 1):
                if self._corr[lag] < min_corr:
                    min_corr = self._corr[lag]
                    dc_raw = 2.0 * lag

            # ---- rate limiter: at most +/- 2 bars of period change --------
            #   If DC > DC[1] + 2 Then DC = DC[1] + 2;
            #   If DC < DC[1] - 2 Then DC = DC[1] - 2;
            prev = self._dc_prev
            if dc_raw > prev + MAX_DC_STEP:
                dc_raw = prev + MAX_DC_STEP
            if dc_raw < prev - MAX_DC_STEP:
                dc_raw = prev - MAX_DC_STEP
            self._dc_prev = dc_raw
            dc = dc_raw

        # ------------------------------------------------------------------
        # 3) bandpass filter re-tuned on every bar to the dominant cycle
        #
        #    L1 = Cosine(360/Period);              (radians: cos(2*pi/P))
        #    G1 = Cosine(Bandwidth*360/Period);
        #    S1 = 1/G1 - SquareRoot(1/(G1*G1) - 1);
        #    BP = .5*(1-S1)*(Price - Price[2])
        #          + L1*(1+S1)*BP[1] - S1*BP[2];
        #    If CurrentBar < 3 Then BP = 0;
        # ------------------------------------------------------------------
        bp = math.nan
        if t >= BANDPASS_WARMUP_BARS and not math.isnan(dc):
            p0 = self._price[-1]
            p2 = self._price[-3]
            bp1 = self._bp[-1] if len(self._bp) >= 1 else 0.0
            bp2 = self._bp[-2] if len(self._bp) >= 2 else 0.0
            if dc <= 0.0:
                # Undefined centre period - EasyLanguage would divide by zero.
                bp = 0.0
            else:
                a0, a1, a2 = bandpass_coefficients(dc, self.bandwidth)
                bp = a0 * (p0 - p2) + a1 * bp1 + a2 * bp2
        self._bp.append(0.0 if math.isnan(bp) else bp)

        # ------------------------------------------------------------------
        # 4) two-bar rate of change of the bandpass output (pro-forma rule)
        #    ROC = BP - BP[2];
        # ------------------------------------------------------------------
        roc = math.nan
        if len(self._bp) >= 3 and not math.isnan(bp) and not math.isnan(self._bp[-3]):
            roc = self._bp[-1] - self._bp[-3]

        return AutoTuneResult(filt=filt if t >= HIGHPASS_WARMUP_BARS else math.nan,
                              min_corr=min_corr,
                              dominant_cycle=dc,
                              bandpass=bp,
                              roc=roc)

    # convenience: feed a whole series in one go (used by __main__)
    def run(self, closes) -> List[AutoTuneResult]:
        """Feed an iterable of closes and return the list of per-bar results."""
        return [self.update(c) for c in closes]


# =============================================================================
# Reference test vectors
# =============================================================================

# Parameter grid used to generate the EXPECTED_* arrays stored in
# test_testdata.py / testdata_test.go / testdata.ts / testdata.rs / testdata.zig
# (and mirrored in description.md).
WINDOWS = (10, 19, 20, 26)
BANDWIDTHS = (0.20, 0.22, 0.25)

# name used in the generated array identifiers, in output order
OUTPUT_NAMES = ("FILT", "MINCORR", "DC", "BP", "ROC")

# output identifier -> AutoTuneResult field name
OUTPUT_FIELDS = {
    "FILT": "filt",
    "MINCORR": "min_corr",
    "DC": "dominant_cycle",
    "BP": "bandpass",
    "ROC": "roc",
}


def param_tag(window: int, bandwidth: float) -> str:
    """Parameter shortcut used in array names: W19_B0_20."""
    bw = ("%.2f" % bandwidth).replace(".", "_")
    return "W%d_B%s" % (window, bw)


def fmt(v: float) -> str:
    """Format one value with 15 digits after the decimal point (NaN aware)."""
    if v is None or math.isnan(v):
        return "NaN"
    return "%.15f" % v


def compute_all(closes, windows=WINDOWS, bandwidths=BANDWIDTHS):
    """Compute every grid point; returns list of (tag, window, bandwidth, results)."""
    out = []
    for w in windows:
        for b in bandwidths:
            ind = AutoTune(window=w, bandwidth=b)
            res = ind.run(closes)
            out.append((param_tag(w, b), w, b, res))
    return out


def _rows(vals, indent, nan_token):
    """Format a value list into indented rows of 10 comma separated literals."""
    out = []
    for i in range(0, len(vals), 10):
        cells = []
        for v in vals[i:i + 10]:
            cells.append(nan_token if (v is None or math.isnan(v)) else fmt(v))
        out.append(indent + ", ".join(cells) + ",")
    return "\n".join(out)


def _header(name, w, b, comment_prefix=""):
    """The two comment lines that describe every generated array."""
    return ("%s%s - AutoTune filter output series\n"
            "%swindow=%d, bandwidth=%.2f" % (comment_prefix, name, comment_prefix, w, b))


def render_python(grid) -> str:
    """Python: EXPECTED_<Wnn_B0_xx>_<OUT> = [ ... ]  (NaN literal)."""
    blocks = []
    for tag, w, b, res in grid:
        for name in OUTPUT_NAMES:
            vals = [getattr(r, OUTPUT_FIELDS[name]) for r in res]
            body = _rows(vals, "    ", "NaN")
            blocks.append("%s\nEXPECTED_%s_%s = [\n%s\n]"
                          % (_header(name, w, b, "# "), tag, name, body))
    return "\n\n".join(blocks)


def render_go(grid) -> str:
    """Go: var expectedW20_B0_25FILT = []float64{ ... }  (math.NaN())."""
    blocks = []
    for tag, w, b, res in grid:
        for name in OUTPUT_NAMES:
            vals = [getattr(r, OUTPUT_FIELDS[name]) for r in res]
            var = "expected%s_%s" % (tag[0].upper() + tag[1:], name)
            body = _rows(vals, "\t", "math.NaN()")
            blocks.append("%s\nvar %s = []float64{\n%s\n}"
                          % (_header(name, w, b, "// "), var, body))
    return "\n\n".join(blocks)


def render_ts(grid) -> str:
    """TypeScript: export const expectedW20_B0_25FILT: number[] = [ ... ]."""
    blocks = []
    for tag, w, b, res in grid:
        for name in OUTPUT_NAMES:
            vals = [getattr(r, OUTPUT_FIELDS[name]) for r in res]
            var = "expected%s_%s" % (tag[0].upper() + tag[1:], name)
            body = _rows(vals, "    ", "NaN")
            blocks.append("%s\nexport const %s: number[] = [\n%s\n];"
                          % (_header(name, w, b, "// "), var, body))
    return "\n\n".join(blocks)


def render_rs(grid) -> str:
    """Rust: pub fn expected_w20_b0_25filt() -> Vec<f64> { vec![ ... ] }."""
    blocks = []
    for tag, w, b, res in grid:
        for name in OUTPUT_NAMES:
            vals = [getattr(r, OUTPUT_FIELDS[name]) for r in res]
            fn = "expected_%s_%s" % (tag.lower(), name.lower())
            body = _rows(vals, "            ", "f64::NAN")
            blocks.append("%s\n    pub fn %s() -> Vec<f64> {\n        vec![\n%s\n        ]\n    }"
                          % (_header(name, w, b, "// "), fn, body))
    return "\n\n".join(blocks)


def render_zig(grid) -> str:
    """Zig: pub fn expectedW20_B0_25FILT() [252]f64 { return .{ ... }; }."""
    blocks = []
    for tag, w, b, res in grid:
        for name in OUTPUT_NAMES:
            vals = [getattr(r, OUTPUT_FIELDS[name]) for r in res]
            fn = "expected%s_%s" % (tag[0].upper() + tag[1:], name)
            body = _rows(vals, "        ", "nan")
            blocks.append("%s\npub fn %s() [%d]f64 {\n    return .{\n%s\n    };\n}"
                          % (_header(name, w, b, "// "), fn, len(vals), body))
    return "\n\n".join(blocks)


def emit(closes, grid, fmt_name: str, out_path: Optional[str]) -> None:
    renderers = {"py": render_python, "go": render_go,
                 "ts": render_ts, "rs": render_rs, "zig": render_zig}
    if fmt_name not in renderers:
        raise SystemExit("unknown target language: %s" % fmt_name)
    text = renderers[fmt_name](grid)
    if out_path:
        with open(out_path, "w") as fh:
            fh.write(text + "\n")
        print("wrote %s (%d bytes)" % (out_path, len(text)))
    else:
        print(text)


# =============================================================================
# Example usage / reference generation
# =============================================================================

if __name__ == "__main__":
    import sys

    here = os.path.dirname(os.path.abspath(__file__))

    # ---- 252 bar synthetic close series used by all five test-data files ----
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
    assert len(INPUT_CLOSE) == 252, "INPUT_CLOSE must contain 252 values"

    # ------------------------------------------------------------------
    # 1) minimal example: article defaults (window = 20, bandwidth = 0.25)
    # ------------------------------------------------------------------
    ind = AutoTune(window=20, bandwidth=0.25)
    print("AutoTune, window=20 bandwidth=0.25, warm-up = %d bars" % ind.warmup_bars)
    print("bar   close        filt          min_corr   dc       bp")
    for i, c in enumerate(INPUT_CLOSE):
        r = ind.update(c)
        if i < ind.warmup_bars + 6 or i > len(INPUT_CLOSE) - 3:
            print("%3d %9.3f %12.6f %11.6f %5.1f %9.6f %9.6f"
                  % (i, c, r.filt, r.min_corr, r.dominant_cycle, r.bandpass, r.roc))

    # ------------------------------------------------------------------
    # 2) pro-forma style peak/valley detection on the same outputs
    # ------------------------------------------------------------------
    print("\nPro-forma signal check (ROC crosses zero, MinCorr < -0.3):")
    ind = AutoTune(window=19, bandwidth=0.2)
    prev_roc = None
    for i, c in enumerate(INPUT_CLOSE):
        r = ind.update(c)
        if prev_roc is not None and not math.isnan(r.roc) and not math.isnan(prev_roc):
            if prev_roc <= 0.0 < r.roc and r.min_corr < -0.3:
                print("  bar %3d BUY  (close %.3f, dc %.1f)" % (i, c, r.dominant_cycle))
            if prev_roc >= 0.0 > r.roc and r.min_corr < -0.3 and r.filt > 0.0:
                print("  bar %3d SELL (close %.3f, dc %.1f)" % (i, c, r.dominant_cycle))
        prev_roc = r.roc

    # ------------------------------------------------------------------
    # 3) reference test vectors
    # ------------------------------------------------------------------
    grid = compute_all(INPUT_CLOSE)

    argv = sys.argv[1:]
    if "--emit" in argv:
        idx = argv.index("--emit")
        lang = argv[idx + 1] if len(argv) > idx + 1 else "py"
        out = os.path.join(here, "generated_%s.txt" % lang)
        emit(INPUT_CLOSE, grid, lang, out)
    else:
        print("\nparameter grid: windows=%s bandwidths=%s -> %d combinations, %d arrays"
              % (list(WINDOWS), list(BANDWIDTHS), len(grid),
                 len(grid) * len(OUTPUT_NAMES)))
        print("use  --emit py|go|ts|rs|zig  to regenerate the reference vectors")