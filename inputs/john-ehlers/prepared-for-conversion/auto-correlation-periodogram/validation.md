# Master preparation validation

Validated on 2026-10-21 using Python 3.14, Go 1.27.1, Node 24.15.0,
Rust 1.98.1, and Zig 0.16.0.

The master uses the 2016 article by default and exposes a corrected-book profile.
Every accepted input returns a heatmap and dominant-cycle value. Mathematical
constants use full precision, and fixture text uses 15 significant digits.

## Reference dataset

- 64 confirmed parameter combinations.
- 252 original `INPUT_CLOSE` values, embedded in the executable example.
- Four expected arrays per combination: dominant cycle, complete heatmap,
  heatmap minimum, heatmap maximum.
- 256 expected arrays in each of the five language fixture files.
- Heatmap width is `max_period - min_period + 1`; all 252 time rows are stored.
- Matching NaN masks, numeric literals, and two-line parameter comments across
  Python, Go, TypeScript, Rust, and Zig.
- Original shared Python OHLC inputs preserved and checked for equality.
- All five files regenerate byte for byte without duplicate generated sections.

## Checks performed

| Check | Result |
| --- | --- |
| Eight Python unit tests | Passed |
| Every combination versus independent complete-record source transcription | Passed, including finite internal startup state and all public outputs |
| Source-specific enhancement order and book hold behavior | Passed |
| Zero power, retained zero-variance correlation, NaN skips, overflow rejection, reset replay | Passed |
| Deterministic 20-bar sine signal | Peak at 20 bars; dominant cycle within 18–22 bars |
| Reopened Python expected data: dimensions, masks, 15-digit rounding | Passed |
| Exact four-language numeric and comment parity with Python arrays | Passed |
| Go compile and test instantiating all 256 expected declarations | Passed |
| TypeScript load under Node, every exported array and matrix row checked | Passed |
| Rust `rustc --test`, every expected function called | Passed |
| Zig test, every expected function instantiated and called | Passed |
| Second generation: SHA-256 comparison of all five fixture files | Byte-identical |
| Documentation local source links and master/test Python syntax | Passed |

Run the reusable Python checks from this directory:

```sh
python3 -m unittest test_auto_correlation_periodogram.py
python3 auto-correlation-periodogram.py --generate-reference-data
```

The language compile harnesses were created in `/tmp/acp-master-validation`.
They check the supplied data declarations; indicator implementations in those
languages belong to the later conversion project. TypeScript was executed with
Node's native type stripping, not a separate `tsc` type-check. There is no
TradeStation runtime comparison: source-equation fidelity is verified against
an independent standard-library transcription with the documented precision,
Fourier correction, startup, and degeneracy conventions.
