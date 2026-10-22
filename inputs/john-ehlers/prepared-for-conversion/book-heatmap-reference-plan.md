# Proposed reference cases for three book heatmap masters

Status: all 36 combinations confirmed by the user on 2026-10-22. **36 combinations total**, twelve per folder.

All cases use the original 252 `INPUT_CLOSE` values. The autocorrelation master exports HEATMAP/MIN/MAX. Both spectrum masters also export DOMINANT_CYCLE. Matrix rows are chronological bars; columns are ascending integer lags or periods. Floating literals use 15 significant digits; unavailable public outputs use NaN.

Defaults are explicit in every table row. High-pass and smoothing periods are independent coefficient controls, so reducing a displayed axis does not silently retune the roof. Spectrum AGC decay is the source design constant 0.995. Enhancement cubes the display after the centroid. Comb band-pass recursion begins at standalone CurrentBar=13.

## roofed-autocorrelation-heatmap

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_lag=3, max_lag=48, averaging_length=0, highpass_period=48.0, smoothing_period=10.0` | Published defaults: roofed Pearson map with lag-dependent averaging. |
| 2 | `min_lag=3, max_lag=48, averaging_length=2, highpass_period=48.0, smoothing_period=10.0` | Two-sample reversal window and saturated correlations. |
| 3 | `min_lag=3, max_lag=48, averaging_length=3, highpass_period=48.0, smoothing_period=10.0` | Short fixed Pearson window. |
| 4 | `min_lag=3, max_lag=48, averaging_length=20, highpass_period=48.0, smoothing_period=10.0` | Full nominal-cycle averaging window. |
| 5 | `min_lag=3, max_lag=48, averaging_length=100, highpass_period=48.0, smoothing_period=10.0` | Long fixed averaging history. |
| 6 | `min_lag=3, max_lag=48, averaging_length=1, highpass_period=48.0, smoothing_period=10.0` | Published zero-variance rescaling behavior for a degenerate one-sample window. |
| 7 | `min_lag=3, max_lag=48, averaging_length=0, highpass_period=48.0, smoothing_period=10.5` | Fractional SuperSmoother cutoff without rounding. |
| 8 | `min_lag=3, max_lag=48, averaging_length=0, highpass_period=48.0, smoothing_period=20.0` | Slower roof smoothing. |
| 9 | `min_lag=3, max_lag=48, averaging_length=0, highpass_period=80.0, smoothing_period=10.0` | Independent longer high-pass cutoff. |
| 10 | `min_lag=3, max_lag=24, averaging_length=0, highpass_period=24.0, smoothing_period=10.0` | Compact lag-dependent map and shorter roofing band. |
| 11 | `min_lag=12, max_lag=12, averaging_length=12, highpass_period=48.0, smoothing_period=10.0` | Single displayed nonzero lag. |
| 12 | `min_lag=0, max_lag=0, averaging_length=3, highpass_period=48.0, smoothing_period=10.0` | Lag-zero-only map and perfect self-correlation when variance is positive. |

## discrete-fourier-transform-spectrum

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=True, enhance_resolution=False, window_length=48` | Published compensated DFT, fixed maximum normalization, and dominant period. |
| 2 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=False, enhance_resolution=False, window_length=48` | Uncompensated amplitude spectrum. |
| 3 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=True, enhance_resolution=True, window_length=48` | Cubic display contrast after the unchanged dominant-period calculation. |
| 4 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=False, enhance_resolution=True, window_length=48` | Uncompensated spectrum with cubic display contrast. |
| 5 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=True, enhance_resolution=False, window_length=24` | Short Fourier observation window and end effects. |
| 6 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=True, enhance_resolution=False, window_length=96` | Long Fourier observation window. |
| 7 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=True, enhance_resolution=False, window_length=252` | Record-length boundary: first complete DFT at the final shared close. |
| 8 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.5, spectral_dilation_compensation=True, enhance_resolution=False, window_length=48` | Fractional SuperSmoother cutoff. |
| 9 | `min_period=10, max_period=48, highpass_period=80.0, smoothing_period=20.0, spectral_dilation_compensation=True, enhance_resolution=False, window_length=48` | Slower independent roofing band. |
| 10 | `min_period=6, max_period=24, highpass_period=24.0, smoothing_period=6.0, spectral_dilation_compensation=True, enhance_resolution=False, window_length=24` | Compact spectrum including shorter cycles. |
| 11 | `min_period=20, max_period=20, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=True, enhance_resolution=False, window_length=48` | Single-period spectrum and exact centroid when selected. |
| 12 | `min_period=24, max_period=60, highpass_period=60.0, smoothing_period=12.0, spectral_dilation_compensation=True, enhance_resolution=False, window_length=60` | Shifted longer-cycle spectrum. |

## comb-band-pass-spectrum

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=True, enhance_resolution=False, bandwidth=0.3` | Reconstructed published defaults, delayed bank startup, and dominant period. |
| 2 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=False, enhance_resolution=False, bandwidth=0.3` | Uncompensated band-pass amplitudes before squared-power accumulation. |
| 3 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=True, enhance_resolution=True, bandwidth=0.3` | Cubic display contrast after the unchanged dominant-period calculation. |
| 4 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=False, enhance_resolution=True, bandwidth=0.3` | Uncompensated comb spectrum with cubic display contrast. |
| 5 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=True, enhance_resolution=False, bandwidth=0.1` | Narrower resonators and longer transients. |
| 6 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=True, enhance_resolution=False, bandwidth=0.7` | Broader overlapping resonators. |
| 7 | `min_period=10, max_period=48, highpass_period=48.0, smoothing_period=10.5, spectral_dilation_compensation=True, enhance_resolution=False, bandwidth=0.3` | Fractional SuperSmoother cutoff. |
| 8 | `min_period=10, max_period=48, highpass_period=80.0, smoothing_period=20.0, spectral_dilation_compensation=True, enhance_resolution=False, bandwidth=0.3` | Slower independent roofing band. |
| 9 | `min_period=6, max_period=24, highpass_period=24.0, smoothing_period=6.0, spectral_dilation_compensation=True, enhance_resolution=False, bandwidth=0.3` | Compact shorter-cycle bank. |
| 10 | `min_period=20, max_period=20, highpass_period=48.0, smoothing_period=10.0, spectral_dilation_compensation=True, enhance_resolution=False, bandwidth=0.3` | Single-period bank with a twenty-sample power window. |
| 11 | `min_period=24, max_period=60, highpass_period=60.0, smoothing_period=12.0, spectral_dilation_compensation=True, enhance_resolution=False, bandwidth=0.3` | Shifted longer-cycle bank. |
| 12 | `min_period=10, max_period=240, highpass_period=240.0, smoothing_period=10.0, spectral_dilation_compensation=True, enhance_resolution=False, bandwidth=0.3` | Record-length boundary: twelve gated bars plus 240 genuine band-pass outputs. |

