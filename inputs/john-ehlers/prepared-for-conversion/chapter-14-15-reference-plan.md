# Chapter 14–15 research master reference plan

Status: all 36 combinations confirmed by the user on 2026-10-22. Twelve cases per master, **36 combinations total**. All use the original 252 closes, export 15 significant digits, and preserve all four OHLC input arrays.

Hilbert exports REAL/IMAGINARY. Fisher adaptive RSI exports VALUE/DOMINANT_CYCLE/LOOKBACK_LENGTH. Inverse Fisher adaptive Stochastic exports VALUE/TRIGGER/DOMINANT_CYCLE/LOOKBACK_LENGTH. There are 108 component arrays per language. Hilbert peak decay .991, Fisher gain 1.5 and clip .999, inverse Fisher gain 3 and trigger attenuation .9 stay fixed at the published design values.

## hilbert-transformer-indicator

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `highpass_period=48.0, smoothing_period=20.0, quadrature_period=10.0, smooth_imaginary=True` | Published listing 14-3 defaults; normalized quadrature is smoothed separately. |
| 2 | `highpass_period=48.0, smoothing_period=20.0, quadrature_period=10.0, smooth_imaginary=False` | Listing 14-2 raw normalized quadrature; no final smoothing. |
| 3 | `highpass_period=48.0, smoothing_period=10.0, quadrature_period=10.0, smooth_imaginary=True` | Faster input smoothing with the published output smoother. |
| 4 | `highpass_period=48.0, smoothing_period=40.0, quadrature_period=10.0, smooth_imaginary=True` | Slower input smoothing with independent quadrature smoothing. |
| 5 | `highpass_period=48.0, smoothing_period=20.5, quadrature_period=10.0, smooth_imaginary=True` | Fractional input SuperSmoother period. |
| 6 | `highpass_period=48.0, smoothing_period=20.0, quadrature_period=10.5, smooth_imaginary=True` | Fractional quadrature SuperSmoother period. |
| 7 | `highpass_period=48.0, smoothing_period=20.0, quadrature_period=2.0, smooth_imaginary=True` | Minimum supported quadrature smoothing period. |
| 8 | `highpass_period=48.0, smoothing_period=20.0, quadrature_period=20.0, smooth_imaginary=True` | Slower quadrature smoothing and added phase delay. |
| 9 | `highpass_period=24.0, smoothing_period=6.0, quadrature_period=6.0, smooth_imaginary=True` | Explicit research variant with shorter roofing and output smoothing. |
| 10 | `highpass_period=80.0, smoothing_period=20.0, quadrature_period=10.0, smooth_imaginary=True` | Explicit research variant with longer high-pass cutoff. |
| 11 | `highpass_period=48.0, smoothing_period=2.0, quadrature_period=10.0, smooth_imaginary=False` | Minimum input smoothing period and raw quadrature. |
| 12 | `highpass_period=48.0, smoothing_period=252.0, quadrature_period=10.0, smooth_imaginary=True` | Input cutoff equals record length; IIR cutoff is not a history window. |

## fisher-adaptive-relative-strength-index

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_period=10, max_period=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.0` | Published defaults and listing-specific periodogram decay. |
| 2 | `min_period=10, max_period=48, averaging_length=0, highpass_period=48.0, smoothing_period=10.0` | Lag-dependent Pearson windows and longer priming history. |
| 3 | `min_period=10, max_period=48, averaging_length=2, highpass_period=48.0, smoothing_period=10.0` | Two-sample Pearson windows with strong sign changes. |
| 4 | `min_period=10, max_period=48, averaging_length=5, highpass_period=48.0, smoothing_period=10.0` | Less reactive fixed correlation window. |
| 5 | `min_period=10, max_period=48, averaging_length=20, highpass_period=48.0, smoothing_period=10.0` | Longer correlation window and delayed tuning. |
| 6 | `min_period=10, max_period=48, averaging_length=100, highpass_period=48.0, smoothing_period=10.0` | Long fixed Pearson history. |
| 7 | `min_period=10, max_period=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.5` | Fractional roofing/output SuperSmoother cutoff. |
| 8 | `min_period=10, max_period=48, averaging_length=3, highpass_period=80.0, smoothing_period=20.0` | Slower independent roofing and output smoothing. |
| 9 | `min_period=6, max_period=24, averaging_length=3, highpass_period=24.0, smoothing_period=6.0` | Compact short-cycle estimator and adaptive windows. |
| 10 | `min_period=20, max_period=20, averaging_length=3, highpass_period=48.0, smoothing_period=10.0` | Single cycle bin, integer-bound window behavior and deterministic tuning. |
| 11 | `min_period=10, max_period=48, averaging_length=204, highpass_period=48.0, smoothing_period=10.0` | 252-observation history boundary: first public result at final close. |
| 12 | `min_period=24, max_period=60, averaging_length=3, highpass_period=60.0, smoothing_period=12.0` | Longer-cycle estimator and adaptive windows. |

## inverse-fisher-adaptive-stochastic

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_period=10, max_period=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.0` | Published defaults and listing-specific periodogram decay. |
| 2 | `min_period=10, max_period=48, averaging_length=0, highpass_period=48.0, smoothing_period=10.0` | Lag-dependent Pearson windows and longer priming history. |
| 3 | `min_period=10, max_period=48, averaging_length=2, highpass_period=48.0, smoothing_period=10.0` | Two-sample Pearson windows with strong sign changes. |
| 4 | `min_period=10, max_period=48, averaging_length=5, highpass_period=48.0, smoothing_period=10.0` | Less reactive fixed correlation window. |
| 5 | `min_period=10, max_period=48, averaging_length=20, highpass_period=48.0, smoothing_period=10.0` | Longer correlation window and delayed tuning. |
| 6 | `min_period=10, max_period=48, averaging_length=100, highpass_period=48.0, smoothing_period=10.0` | Long fixed Pearson history. |
| 7 | `min_period=10, max_period=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.5` | Fractional roofing/output SuperSmoother cutoff. |
| 8 | `min_period=10, max_period=48, averaging_length=3, highpass_period=80.0, smoothing_period=20.0` | Slower independent roofing and output smoothing. |
| 9 | `min_period=6, max_period=24, averaging_length=3, highpass_period=24.0, smoothing_period=6.0` | Compact short-cycle estimator and adaptive windows. |
| 10 | `min_period=20, max_period=20, averaging_length=3, highpass_period=48.0, smoothing_period=10.0` | Single cycle bin, integer-bound window behavior and deterministic tuning. |
| 11 | `min_period=10, max_period=48, averaging_length=204, highpass_period=48.0, smoothing_period=10.0` | 252-observation history boundary: first public result at final close. |
| 12 | `min_period=24, max_period=60, averaging_length=3, highpass_period=60.0, smoothing_period=12.0` | Longer-cycle estimator and adaptive windows. |

## Startup conventions

Every accepted close is processed internally from bar one using zero prehistory. Public startup NaNs never enter recurrence state. Hilbert requires four input closes in raw mode (three leading NaNs) or five in smoothed mode (four leading NaNs), covering explicit lagged input dependencies; recursive cutoff periods are not finite windows or settling guarantees. Adaptive transforms inherit Chapter 11 whole-bank history: defaults have 50 leading NaNs, and A204 exposes only the final row. Inverse Fisher uses the preceding internally computed transform for its trigger, including startup bars; IFish prehistory is zero. No extra NaN row is added for the trigger because this history requirement already exceeds one preceding observation.

## Completed validation

All 32 Python tests passed, including every confirmed combination against independent full-history source transcriptions and streaming edge cases. The three masters export 108 component arrays and 27,216 values per language. Five-language exact rounded fixture verification passed; all fifteen fixture files regenerate byte-for-byte identically. Go/Rust/Zig compiled and ran fixture harnesses, and Node loaded TypeScript with type stripping. Syntax, whitespace and source links passed. Hilbert supports both published quadrature variants; transforms retain the exact Chapter 11 bases, Fisher clipping and previous internal inverse-Fisher trigger.
