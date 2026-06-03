"""Exponential Moving Average (Blau / EasyLanguage ``XAverage``).

This is the single most important *building block* in William Blau's
*Momentum, Direction, and Divergence* (1995) indicator family. Every Blau
indicator (TSI, SMI, DTI, Ergodic, CMI, ...) is constructed by **cascading**
this EMA two or three times. The code below is therefore meant to be **embedded
(inlined) verbatim** into each indicator implementation rather than imported as
a shared dependency -- so it is written to be trivially portable to Go, Rust,
TypeScript, and Zig.

Numerical contract (DO NOT change when porting -- see ``description.md`` §2):

    * Smoothing factor:  alpha = 2 / (period + 1)
    * Seed:              e_0 = x_0   (first output == first input; NO NaN warm-up)
    * Recursion (blend): e_k = alpha * x_k + (1 - alpha) * e_(k-1)
    * period == 1  =>  alpha == 1  =>  pure passthrough (e_k == x_k); this is a
      designed feature Blau uses to "switch off" a cascade stage, not an error.
    * period  < 1  =>  invalid (rejected at construction).

The recursion uses the *blend* form ``alpha*x + (1-alpha)*prev`` -- the literal
floating-point expression evaluated by the MQL5 reference port
(``WilliamBlau.mqh``) -- so that every language reproduces bit-identical values.

Standard library only: no numpy / pandas (keeps the port to Rust/Zig/Go 1:1).
"""

from __future__ import annotations


class ExponentialMovingAverage:
    """Stateful, streaming exponential moving average.

    One instance smooths exactly one series. Feed it one value at a time via
    :meth:`update`, which returns the EMA value for that bar. To build a
    cascade (e.g. ``EMA(EMA(x, r), s)``) create one instance per stage and wire
    each stage's output into the next stage's input.

    Example
    -------
    >>> ema = ExponentialMovingAverage(3)        # period 3 -> alpha = 0.5
    >>> [round(ema.update(x), 4) for x in (10.0, 12.0, 11.0)]
    [10.0, 11.0, 11.0]
    """

    # Instance attributes (declared here for readability / porting clarity):
    #   _alpha  : float  -- smoothing factor 2/(period+1), computed once.
    #   _prev   : float  -- the previous EMA output e_(k-1); valid once primed.
    #   _primed : bool   -- False until the first update() call seeds the state.

    def __init__(self, period: int) -> None:
        """Create an EMA of the given integer ``period`` (must be >= 1).

        ``period == 1`` is explicitly allowed and yields a pure passthrough.
        """
        if period < 1:
            # Matches the MQL5 reference guard ``if(period<1) return(0)``.
            raise ValueError(f"period must be >= 1, got {period!r}")

        # Smoothing factor alpha = 2 / (n + 1). For n == 1 this is exactly 1.0,
        # so the recursion collapses to e_k = x_k (passthrough). Computed once
        # and reused every bar.
        self._alpha: float = 2.0 / (float(period) + 1.0)

        # Previous EMA output. Meaningless until the first value primes it; we
        # initialise to 0.0 only so the attribute always exists.
        self._prev: float = 0.0

        # Whether the seed (e_0 = x_0) has been applied yet.
        self._primed: bool = False

    def update(self, x: float) -> float:
        """Feed one input value ``x`` and return this bar's EMA output.

        The first ever call seeds the EMA with ``x`` itself (``e_0 = x_0``) and
        returns it unchanged -- there is no NaN warm-up period. Every later
        call applies the blend recursion.
        """
        if not self._primed:
            # Seed: e_0 = x_0. First output equals first input.
            self._prev = x
            self._primed = True
            return self._prev

        # Recursion (blend form): e_k = alpha * x_k + (1 - alpha) * e_(k-1).
        # Written exactly like the MQL5 reference to preserve FP op order.
        e = self._alpha * x + (1.0 - self._alpha) * self._prev
        self._prev = e
        return e

    def reset(self) -> None:
        """Return the instance to its un-primed state (reuse on a new series)."""
        self._prev = 0.0
        self._primed = False


def ema_series(values, period):
    """Convenience: run a whole list through a fresh EMA and return the outputs.

    Not used by the indicators (they stream), but handy for demos / testing.
    """
    ema = ExponentialMovingAverage(period)
    return [ema.update(v) for v in values]


# ====================================================================== #
# PHASE 2 -- REFERENCE TEST-DATA GENERATION HARNESS                       #
# ---------------------------------------------------------------------- #
# Running this file as a script regenerates the EXPECTED_N_* reference    #
# arrays and APPENDS them to the five test fixtures in this directory:    #
#   test_testdata.py  testdata_test.go  testdata.ts  testdata.rs  testdata.zig
# Each language gets the same numbers in its own idiomatic literal form,  #
# preceded by two comment lines (what-it-tests + param values).          #
#                                                                         #
# The 252 INPUT_CLOSE values below are embedded verbatim from            #
# test_testdata.py so this harness is fully self-contained.              #
# ====================================================================== #

# 252 daily closes -- identical to INPUT_CLOSE / testInput / test_input in the
# fixtures. Embedded here so the generator needs no imports.
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

# Period set for the reference corpus (17 arrays, well within the <=64 budget):
#   n = 1            -> passthrough sanity check
#   n = 2..10        -> fast-response smoothing (dense coverage)
#   n = 12,15,20,25,30,40,50 -> progressively longer memory / more lag
PERIODS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50]


def _fmt(x: float) -> str:
    """Shortest decimal literal that round-trips to this exact float.

    ``repr`` guarantees the emitted text parses back to the identical IEEE-754
    double in Python, and the same literal parses identically in Go/Rust/TS/Zig.
    This is what keeps all five languages bit-identical to the reference.
    """
    return repr(float(x))


def _wrap(values, indent, per_line=4):
    """Format a list of floats as wrapped, indented literal lines."""
    lines = []
    for i in range(0, len(values), per_line):
        chunk = ", ".join(_fmt(v) for v in values[i:i + per_line])
        lines.append(f"{indent}{chunk},")
    return "\n".join(lines)


def _what_it_tests(n: int) -> str:
    if n == 1:
        return ("EMA period N=1 -> alpha=1.0 -> PURE PASSTHROUGH; "
                "every output must equal the corresponding input close.")
    return (f"EMA of close, period N={n} (alpha=2/(N+1)); seeded e_0=x_0, "
            f"finite from bar 0 (no NaN warm-up).")


def _params(n: int) -> str:
    return f"N (period) = {n}"


def generate():
    """Compute outputs and append fixtures in all five languages."""
    results = [(n, ema_series(INPUT_CLOSE, n)) for n in PERIODS]

    # ---- Python: EXPECTED_N_<n> = [ ... ] -------------------------------- #
    with open("test_testdata.py", "a") as f:
        f.write("\n")
        for n, vals in results:
            f.write(f"# {_what_it_tests(n)}\n")
            f.write(f"# {_params(n)}\n")
            f.write(f"EXPECTED_N_{n} = [\n")
            f.write(_wrap(vals, "    ") + "\n")
            f.write("]\n\n")

    # ---- Go: var expectedN<n> = []float64{ ... } ------------------------- #
    with open("testdata_test.go", "a") as f:
        f.write("\n")
        for n, vals in results:
            f.write(f"// {_what_it_tests(n)}\n")
            f.write(f"// {_params(n)}\n")
            f.write(f"var expectedN{n} = []float64{{\n")
            f.write(_wrap(vals, "\t") + "\n")
            f.write("}\n\n")

    # ---- TypeScript: export const expectedN<n>: number[] = [ ... ] ------- #
    with open("testdata.ts", "a") as f:
        f.write("\n")
        for n, vals in results:
            f.write(f"// {_what_it_tests(n)}\n")
            f.write(f"// {_params(n)}\n")
            f.write(f"export const expectedN{n}: number[] = [\n")
            f.write(_wrap(vals, "    ") + "\n")
            f.write("];\n\n")

    # ---- Rust: pub fn expected_n<n>() -> Vec<f64> { vec![ ... ] } -------- #
    with open("testdata.rs", "a") as f:
        f.write("\n")
        for n, vals in results:
            f.write(f"// {_what_it_tests(n)}\n")
            f.write(f"// {_params(n)}\n")
            f.write(f"pub fn expected_n{n}() -> Vec<f64> {{\n")
            f.write("    vec![\n")
            f.write(_wrap(vals, "        ") + "\n")
            f.write("    ]\n")
            f.write("}\n\n")

    # ---- Zig: pub fn expectedN<n>() [252]f64 { return .{ ... }; } -------- #
    with open("testdata.zig", "a") as f:
        f.write("\n")
        for n, vals in results:
            f.write(f"// {_what_it_tests(n)}\n")
            f.write(f"// {_params(n)}\n")
            f.write(f"pub fn expectedN{n}() [{len(vals)}]f64 {{\n")
            f.write("    return .{\n")
            f.write(_wrap(vals, "        ") + "\n")
            f.write("    };\n")
            f.write("}\n\n")

    print(f"Generated {len(results)} arrays x 5 languages "
          f"({len(INPUT_CLOSE)} values each).")


if __name__ == "__main__":
    # Sanity assertions before emitting anything.
    assert len(INPUT_CLOSE) == 252, "expected 252 input closes"
    assert ema_series(INPUT_CLOSE, 1) == INPUT_CLOSE, "period 1 must be passthrough"
    generate()
