# Corona master validation

The four streaming masters and shared estimator are implemented. The user
confirmed64 total parameter cases,16 per indicator. Every leaf has a master
Python script, self-contained theory/description, the five input/expected-data
files, and a manifest of configurations, output fields, geometry, first
availability, and SHA256 hashes. Generation uses252 original Close values;
SNR also uses corresponding original High/Low ranges.

## Numerical and state checks

```sh
python3 -m unittest discover -s inputs/john-ehlers/prepared-for-conversion/corona -v
```

Eleven research checks pass:

- Common estimator agreement with the independent reconstruction of the later
  readable Corona source on both Close and median-price data, including startup,
  power normalization, median cycle, and centroid holds.
- Literal first-bank-sample13 gate and persistence of the centroid when no
  channels qualify.
- Identical standalone and shared-snapshot consumer outputs for every price,
  and rejection of duplicate shared snapshots.
- NaN skips without bar-count advance, and independent owned output arrays.
- Parameter/stability validation, nonfinite-input rejection, engine overflow
  rejection before commit, and reset.
- Full-cycle trend subtraction cancels a stationary sine wave and retains
  the exact directional displacement of a linear trend.
- Quadrature/60-degree phase rotation uses current BP and full-precision
  `sqrt(3)/2`.
- Constant-input behavior includes explicit no-cycle/degenerate diagnostics.
- Physical SNR follows20log10 of amplitude ratio; preserved source signal
  recurrence has DC gain2; zero-noise and zero-signal cases never divide by zero.
- SNR validates range inputs atomically and agrees between High/Low and
  explicit bar-range interfaces.
- Source raster geometry, included upper endpoint, and explicit half-up marker
  rounding at a tie.

The separate investigation harness still records the12 existing copied-code
checks and their source differences. Passing those external snapshots does not
establish equality to the reconstructed master, whose documented corrections
deliberately change several outputs.

## Complete fixture verification

```sh
python3 inputs/john-ehlers/prepared-for-conversion/corona/verify_reference.py
```

| Master | Cases | Arrays per language | Scalar/cell values per language |
| --- | --- | --- | --- |
| Corona Spectrum |16|176|624,960|
| Corona Swing Position |16|224|203,616|
| Corona Trend Vigor |16|240|207,648|
| Corona Signal-to-Noise Ratio |16|240|207,648|
| Total |64|880|1,243,872|

Expected outputs are formatted to15 significant decimal digits. Verification
checks each Python output against freshly computed full-precision streaming
outputs, then compares **every actual exported literal** in Go, TypeScript,
Rust, and Zig to the parsed Python value. It also checks matrix shapes, all252
rows, unavailable-row NaNs, output names, the two per-array comment lines,
unchanged original input prefixes, and file hashes. Source input arrays are
copied rather than synthesized or replaced with the external median fixtures.

The reference input has no infinite expected values. Degenerate-runtime SNR
infinities/NaNs are checked separately and its serializer supports those values.
NaNs compare by classification rather than ordinary equality. Cross-language
binary64 ports should use both relative and absolute tolerances5e−12 to allow
15-digit rounding and small libm differences. No claim of bitwise equality
across math libraries is made.

Regeneration is deterministic: the full family generator replaces only the
marked generated sections, and the leaf `__main__` generation path preserves
identical fixture/manifest hashes. All four examples execute from their own
indicator working directories. The shared example processes252 bars for all
four consumers using only252 estimator updates.

## Supplementary language checks

Go fixtures compile in their stripped folder-name packages with
`go test testdata_test.go` from each leaf directory. This compiles the fixture
declarations; there is no Go indicator implementation in this preparation repo,
so Go reports no test functions to run. The correct standard-library spelling
is `math.NaN()`, correcting the spelling in the user procedure.

Rust fixtures compile with the test configuration enabled, for example:

```sh
rustc --edition=2021 --crate-type lib --cfg test --emit=metadata \
  inputs/john-ehlers/prepared-for-conversion/corona-spectrum/testdata.rs \
  -o /tmp/corona-spectrum.rmeta
```

Zig0.16 fixtures compile and run a temporary harness invoking **every** exported
input/expected function, including all matrix functions. This forces lazy
function bodies to be analyzed, unlike a bare `zig test testdata.zig` that
could leave them unused. The harness uses the leaf data file as module `data`,
and checks that every function returns252 rows. Cache/artifacts stay in `/tmp`.

TypeScript fixtures execute successfully through Node24's built-in TypeScript
stripping. No `tsc` compiler is available in this environment, so this is a
syntax/execution check, not a full TypeScript type-check. Array values and
matrix dimensions are independently covered by the complete literal verifier.

## Source parity limits and adopted corrections

The original November2008 EasyLanguage sidebars/ELD are not in the supplied
article folder. The common estimator agrees with the independently reconstructed
later local listing; this does not certify the unavailable original executable.
Full-precision constants also intentionally differ from truncated listings.

The implemented contract is explicit: sample13 bank/public gate; seeded first
price; zero adaptive BP on standalone samples1/2; source centroid hold;
current BP in Swing phase lead; inclusive51/21 windows; full-cycle Trend lag
`floor(median_cycle)` by default; conditional Trend ratio hold; zero-width
guards; source logical1..R raster positions; SNR physical and calibrated values
separate from the existing mapped scalar; explicit finite/degenerate noise
inputs. Trend's original lookback/width and SNR clipping are not recoverable
unambiguously from the damaged supplied listings, so their choices are
documented interpretations, not silent purported source equivalence.

No external framework imports were repaired and no five-language indicator
implementations were written. The completed deliverables are the requested
Python conversion masters, descriptions, and five-language reference datasets.
