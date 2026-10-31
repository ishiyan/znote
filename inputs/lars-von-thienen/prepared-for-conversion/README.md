# Lars von Thienen research prototype masters

All 20 candidates are prepared: 18 price-input streaming masters, seven
local CLI workflows, and two frozen-model readers for annual fitting and
historical superposition. Each has a complete description with equations,
physical analogies, Mermaid flows, source distinctions and BibTeX, plus
Python, Go, TypeScript, Rust and Zig input/expected fixtures. Each master
entry point has the same basename as its folder.

| Requested candidate | Master folder and documentation | Cases | Expected arrays per language |
|---|---|---:|---:|
| cyclic-smoothed-rsi | [cyclic-smoothed-relative-strength-index](cyclic-smoothed-relative-strength-index/description.md) | 9 | 27 |
| cycle-swing | [cycle-swing-momentum](cycle-swing-momentum/description.md) | 8 | 32 |
| detrended-rhythm-oscillators | [detrended-rhythm-oscillators](detrended-rhythm-oscillators/description.md) | 8 | 40 |
| zero-lag-ema | [zero-lag-exponential-moving-average](zero-lag-exponential-moving-average/description.md) | 9 | 9 |
| hodrick-prescott-smoothing-and-detrending | [hodrick-prescott-smoothing-and-detrending](hodrick-prescott-smoothing-and-detrending/description.md) | 9 | 18 |
| goertzel-cycle-spectrum | [goertzel-cycle-spectrum](goertzel-cycle-spectrum/description.md) | 8 | 246 |
| bartels-periodicity-score | [bartels-periodicity-score](bartels-periodicity-score/description.md) | 8 | 24 |
| cycle-strength | [cycle-strength](cycle-strength/description.md) | 8 | 24 |
| composite cycle | [composite-cycle](composite-cycle/description.md) | 8 | 24 |
| cycle-polarity | [cycle-polarity](cycle-polarity/description.md) | 8 | 40 |
| metonic-sentiment-index | [metonic-sentiment-index](metonic-sentiment-index/description.md) | 9 | 36 |
| metonic-rsi | [metonic-relative-strength-index](metonic-relative-strength-index/description.md) | 8 | 16 |
| metonic-williams-r | [metonic-williams-percent-r](metonic-williams-percent-r/description.md) | 8 | 16 |
| complete-cycle-scanner | [complete-cycle-scanner](complete-cycle-scanner/description.md) | 4 | 358 |
| dominant-market-vibration | [dominant-market-vibration](dominant-market-vibration/description.md) | 4 | 48 |
| dynamic-cycle-explorer | [dynamic-cycle-explorer](dynamic-cycle-explorer/description.md) | 4 | 32 |
| cycle-phase-score / ccycle-phase-score | [cycle-phase-score](cycle-phase-score/description.md) | 4 | 12 |
| phasing-oscillator | [phasing-oscillator](phasing-oscillator/description.md) | 4 | 20 |
| annual-cycle-pattern-decoder | [annual-cycle-pattern-decoder](annual-cycle-pattern-decoder/description.md) | 4 | 12 |
| harmonic-energy-superposition-wave | [harmonic-energy-superposition-wave](harmonic-energy-superposition-wave/description.md) | 4 | 4 |
| **Total** | **20 masters** | **136** | **1038** |

Every expected array contains 252 outputs, with separate arrays for multiple
outputs and each spectrum bin. All five languages copy the same saved
15-significant-digit Python decimal references and matching NaN masks:
1,307,880 expected values across five languages, excluding input data.
The original parent input fixtures, including the C file, are preserved.

## Source and architecture choices

- cRSI follows the Pine dominant-cycle/half-length meaning, with explicit
  lag flooring, deterministic seeds, complete band windows and extrema repairs.
- CSI is the available source's difference of HP endpoints. Divergence
  chart annotations are outside its base scalar oscillator.
- DRO uses the supplied PPO detrending calculation and exposes provisional
  pivots separately from its completed-cycle median. Chart-label dependence
  and zero-extremum truthiness are repaired explicitly.
- HP publishes the current endpoint of a fixed-window solve. Its standalone
  `hp_trend` helper also supplies complete retrospective batch filtering.
- Goertzel emits the disclosed fixed-grid GDFT spectrum. Its phase origin
  is the start of the current window. It is not a full proprietary scanner.
- Bartels emits the harmonic-segment score. Missing evidence and zero energy
  are unavailable, rather than 100% genuine. Its percentage is a diagnostic,
  not a calibrated probability.
- Strength, composite and polarity offer their disclosed feature/model
  helpers plus price-input wrappers using configured periods and rolling
  Goertzel fits. No undisclosed automatic dominant-cycle selection is inferred.
- Metonic indicators require a complete daily calendar. Original sentiment
  uses actual open and close; Williams %R uses actual high, low and close.
  Matching auxiliary OHLC is included in the copied fixtures. The documented
  close-change sentiment variant is available explicitly as `mode=1`.

The Metonic production delays are **6939, 4016 and 2922 calendar days**.
Their default composite outputs correctly remain NaN on the 252-sample
fixture. Additional short delays are labeled synthetic port-checking cases,
not substitutes for Metonic years. Reference dates are artificial consecutive
days used only to exercise indexing. Independent numerical tests separately
run enough history to verify the real production delays and startup boundaries.

## Use and regeneration

Run each master without flags for complete example update loops, or with
`--generate-reference-data` to regenerate and verify all five fixture files:

```sh
python3 zero-lag-exponential-moving-average/zero-lag-exponential-moving-average.py
python3 zero-lag-exponential-moving-average/zero-lag-exponential-moving-average.py --generate-reference-data
```

Each master uses only its folder’s Python code and copied input fixture. It embeds
the exact requested `INPUT_CLOSE` and reads auxiliary OHLC locally when needed.
No sibling master, parent helper, dependency installation, or network is
required. The original 13 masters contain their numerical code before fixture
tooling; the seven additions load a complete colocated cycle_core.py.
Copy either entire folder independently for conversion.

The five fixture shapes are conventional Python lists, Go `[]float64`,
TypeScript `number[]` exports, Rust `Vec<f64>` functions inside the copied
test module, and Zig `[252]f64` functions. Correct language NaNs are
`math.nan`, `math.NaN()`, `NaN`, `f64::NAN` and `nan`, respectively. The
immediately finite ZLEMA fixture retains Go's requested `math` import with
an explicit blank reference so it compiles without fabricated NaNs.

## Verification

From this folder:

```sh
python3 test_research_masters.py
python3 test_optional_masters.py
python3 verify_references.py
python3 verify_references.py --native
```

The numerical suite checks independent HP normal equations, direct complex
DFT sums at fractional periods, coherent sine phase/amplitude, analytic
superposition, Bartels vector cancellation and consistency ceilings,
completed rhythm distances, RSI/ZLEMA startup, calendar filling, actual
production Metonic delays, and reset/NaN/input contracts for all 18 live masters.
The additional suite checks scanner reconstruction, delayed centered means,
exhaustive annual subsets, calendar completeness, source-only normalization
and CLI/model round trips. Together the suites contain 48 independent checks.

The fixture verifier checks all input/expected arrays, saved Python precision,
the master's regenerated values, required comments, and exact cross-language
decimal/NaN equality. With `--native`, it invokes every fixture array using
Go tests, Rust tests, Zig tests and Node's TypeScript stripping. Native
probes use installed compilers and isolated temporary caches with no downloads.
They validate fixture syntax and exposure, not independently ported indicators.

Generator blocks are replaceable and idempotent. Validation does not change
the fixture files. The descriptions distinguish numeric reproduction and
documented research adaptations from the books' broader forecasting claims.


## Seven additional candidates: delivery and reconstruction rules

The scanner, dominant vibration, explorer, phase score and phasing oscillator
each provide update(price) and a local analyze CLI. The annual decoder fits a
complete past trading year; the superposition builder imports or fits six
historical annual models. Their readers use update() for frozen wave playback.
They do not pretend to fit complete years from each new price.

The common pipeline uses fixed HP smoothing, an integer GDFT sweep,
one-sided/local amplitude peaks, Bartels validation on the latest complete
raw-price segments, strict G>49 by default, A/P strength ranking, and
explicit period-distance suppression. Recent phase uses a separately
detrended suffix of two cycles by default. Dominant vibration is the
highest-strength accepted period. Each description contains full
equations and a configuration contract.

Phase score uses the explicitly reconstructed continuous 100*sin(phase)
mapping. Phasing sums independently detected short/long scores and exposes
the book's -150/+150 thresholds. This does not reproduce the book's
undisclosed discrete status boundaries. Explorer emits current fitted values
and ETAs plus a centered highlighter approximately half a cycle late, with a
separate index. Changing selected periods can change that delayed index.

Annual fitting checks every subset of up to seven waves within a bounded
accepted-cycle pool (default ten), maximizing signed Pearson correlation.
It uses full-year phase fits, requires a completed year, and accepts an
exact supplied trading calendar or a recorded explicit completeness assertion.
Because Bartels requires two full cycles, this reconstruction cannot accept
a period longer than half its year's sample count. In particular, the book's
229-bar component for a roughly 252-session year cannot be reproduced under
that rule; additional validation context or conventions are undisclosed.

Superposition uses exactly target years minus 8,11,19,27,30,38, aligns at
trading-day ordinal zero, and averages six frozen waves. Default source-year
mean/RMS normalization and mathematical extension across unequal calendar
lengths are documented choices; raw/strict alternatives and manual inversion
are available. Target prices never enter fitting or normalization.

These are working research reconstructions, with **no claim of exact WTT
platform or appendix equivalence**. CLI packaging makes the retrospective
workflows usable while retaining those specification limits.

Each additional folder includes runnable CSV/JSON examples, saved
outputs and example-notes.md. Dates are artificial. Annual references assign
the supplied closes a synthetic complete year; superposition references
derive six rotated/scaled synthetic years from them. Frozen-model reference
waves are finite at ordinal zero because fitting has already finished.

From an additional folder, see --help, analyze --help, fit --help or
build --help as appropriate. For example:

~~~sh
python3 complete-cycle-scanner.py analyze --input example-prices.csv --json-out scan.json
python3 annual-cycle-pattern-decoder.py fit --input example-prices.csv --calendar example-calendar.csv --year 2020 --as-of 2021-01-01 --model-out model.json --wave-out wave.csv
~~~

The parent cycle_core.py is the maintenance authority for the seven complete
standalone copies. After editing it, run sync_cycle_core.py, rerun numerical
tests, regenerate affected references, and run verify_references.py. The
verifier rejects out-of-sync copies.
