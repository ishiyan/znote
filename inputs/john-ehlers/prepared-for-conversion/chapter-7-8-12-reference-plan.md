# Chapters 7, 8 and 12 reference plan

Status: all 36 combinations confirmed by the user on 2026-10-22. **36 combinations total**, twelve for each master. All three implementations, standalone descriptions and five-language fixtures are complete and verified.

Numerical sources are Chapter 7 Listing 7-5 (Modified RSI), Chapter 8 Listing 8-4 (Autocorrelation Reversals), and Chapter 12 Listing 12-1 (Even Better Sinewave). All cases use the shared 252 INPUT_CLOSE values and retain the copied OHLC fixture inputs. Full-precision pi/sqrt(2) and 15-significant-digit export follow the established procedure.

Modified RSI and Even Better Sinewave export VALUE; Reversals exports REVERSAL and SIGN_CHANGES. Total: **48 expected component arrays per language**. Reversals' SIGN_CHANGES is an explicit diagnostic of the source SumDeltas. The signal uses strict half-level crossings and strict `count > threshold`.

The printed Reversals HPLength input is unused: `source="book"` preserves the fixed 48-bar high-pass. `source="configured-highpass"` is an explicit research correction honoring highpass_period. Mapped correlations persist and are mapped again when a Pearson denominator is invalid, exactly as in the listing. No hidden correction changes default results.

Zero prehistory and bar-one calculation are explicit. Public leading NaNs are length+1 bars for Modified RSI, max_lag+(averaging_length or max_lag) bars for Reversals (current and preceding full correlation banks), and four bars for Even Better Sinewave (three filtered outputs whose raw-price dependencies are present). Missing NaNs skip state. The Sinewave's undefined zero-power division is extended to a retained previous value, initially zero; ordinary nonzero power follows the printed ratio without clipping.

## modified-relative-strength-index

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `length=10, highpass_period=48.0, smoothing_period=10.0` | Published fixed-window Modified RSI defaults and guarded final smoothing. |
| 2 | `length=1, highpass_period=48.0, smoothing_period=10.0` | One-change RSI window and both-denominator guard. |
| 3 | `length=2, highpass_period=48.0, smoothing_period=10.0` | Short two-change window. |
| 4 | `length=5, highpass_period=48.0, smoothing_period=10.0` | Responsive five-change window. |
| 5 | `length=14, highpass_period=48.0, smoothing_period=10.0` | Traditional fourteen-change length with book roofing. |
| 6 | `length=20, highpass_period=48.0, smoothing_period=10.0` | Longer fixed observation window. |
| 7 | `length=40, highpass_period=48.0, smoothing_period=10.0` | Long fixed-window gain/loss sums. |
| 8 | `length=10, highpass_period=48.0, smoothing_period=10.5` | Fractional period shared by roofing and final SuperSmoother. |
| 9 | `length=10, highpass_period=80.0, smoothing_period=20.0` | Slower independent roofing and output smoothing. |
| 10 | `length=5, highpass_period=24.0, smoothing_period=6.0` | Short-cycle roofing and observation interval. |
| 11 | `length=250, highpass_period=48.0, smoothing_period=10.0` | 252-observation boundary: only the final result is primed. |
| 12 | `length=251, highpass_period=48.0, smoothing_period=10.0` | 253-observation history requirement: all public results remain NaN. |

## autocorrelation-reversals

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_lag=3, max_lag=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.0, sign_change_threshold=24, source=book` | Published defaults, strict half-level crossings and more-than-24 decision. |
| 2 | `min_lag=3, max_lag=48, averaging_length=0, highpass_period=48.0, smoothing_period=10.0, sign_change_threshold=24, source=book` | Lag-dependent Pearson windows and longer history. |
| 3 | `min_lag=3, max_lag=48, averaging_length=1, highpass_period=48.0, smoothing_period=10.0, sign_change_threshold=24, source=book` | Degenerate Pearson windows and repeated mapping of retained stored correlations. |
| 4 | `min_lag=3, max_lag=48, averaging_length=2, highpass_period=48.0, smoothing_period=10.0, sign_change_threshold=24, source=book` | Two-sample Pearson windows and rapid correlation sign changes. |
| 5 | `min_lag=3, max_lag=48, averaging_length=5, highpass_period=48.0, smoothing_period=10.0, sign_change_threshold=24, source=book` | Longer fixed Pearson average. |
| 6 | `min_lag=3, max_lag=48, averaging_length=100, highpass_period=48.0, smoothing_period=10.0, sign_change_threshold=24, source=book` | Long fixed correlation history and fewer rapid decisions. |
| 7 | `min_lag=3, max_lag=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.5, sign_change_threshold=24, source=book` | Fractional input SuperSmoother cutoff. |
| 8 | `min_lag=3, max_lag=48, averaging_length=3, highpass_period=48.0, smoothing_period=20.0, sign_change_threshold=24, source=book` | 20-bar smoothing example discussed in Chapter 8. |
| 9 | `min_lag=3, max_lag=48, averaging_length=3, highpass_period=80.0, smoothing_period=10.0, sign_change_threshold=24, source=book` | Printed unused HPLength input: book mode still calculates with 48 bars. |
| 10 | `min_lag=3, max_lag=48, averaging_length=3, highpass_period=80.0, smoothing_period=10.0, sign_change_threshold=24, source=configured-highpass` | Explicit research correction that honors the configured high-pass period. |
| 11 | `min_lag=3, max_lag=24, averaging_length=3, highpass_period=48.0, smoothing_period=10.0, sign_change_threshold=12, source=book` | Compact lag bank and explicitly configured strict threshold. |
| 12 | `min_lag=3, max_lag=48, averaging_length=203, highpass_period=48.0, smoothing_period=10.0, sign_change_threshold=24, source=book` | 252-observation boundary including the previous full correlation bank. |

## even-better-sinewave

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `duration=40.0, smoothing_period=10.0` | Published one-pole high-pass and three-bar RMS normalization defaults. |
| 2 | `duration=20.0, smoothing_period=10.0` | Shorter duration example discussed in Chapter 12. |
| 3 | `duration=5.0, smoothing_period=10.0` | Minimum supported duration and fast high-pass decay. |
| 4 | `duration=10.0, smoothing_period=10.0` | Short duration without a cycle estimator. |
| 5 | `duration=60.0, smoothing_period=10.0` | Longer retained trend components. |
| 6 | `duration=80.0, smoothing_period=10.0` | Slow high-pass normalization behavior. |
| 7 | `duration=40.5, smoothing_period=10.0` | Fractional duration coefficient period. |
| 8 | `duration=40.0, smoothing_period=10.5` | Fractional input SuperSmoother cutoff. |
| 9 | `duration=40.0, smoothing_period=6.0` | Faster input smoothing with fixed three-bar power average. |
| 10 | `duration=40.0, smoothing_period=20.0` | Slower input smoothing with fixed three-bar normalization. |
| 11 | `duration=252.0, smoothing_period=10.0` | Duration equal to record length; priming follows required input history. |
| 12 | `duration=500.0, smoothing_period=10.0` | Duration longer than the record and long recursive startup. |

## Completed validation

All 30 Python source-oracle/streaming tests passed. The family exports 48 component arrays or 12,096 values per language (12 each for Modified RSI and Even Better Sinewave; 24 for Autocorrelation Reversals). Exact rounded five-language fixture verification passed, including comments, names, NaN placement and preserved OHLC input. Go/Rust/Zig fixture compilation and runtime checks and Node TypeScript loading passed. All fifteen fixture files regenerate byte-for-byte identically. Reversals keeps the printed fixed-48 high-pass in book mode and tests configured-highpass separately; the exact 24/25 threshold is verified with constructed source states.
