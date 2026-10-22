# Chapters 4–6 scalar master reference plan

Status: all 48 combinations confirmed by the user on 2026-10-22. **48 combinations total**, twelve for each of four separate masters. All four implementations, standalone descriptions and five-language fixtures are complete and verified.

Sources: Decycler and Decycler Oscillator use Chapter 4 listings 4-1/4-2; Band-Pass Indicator uses **Chapter 5 listing 5-1** (not Chapter 6); Hurst uses Chapter 6 listing 6-1. No matching prepared master or zpano implementation was found.

All cases use the shared 252 INPUT_CLOSE values, retain copied OHLC inputs, and export 15-significant-digit binary64 literals with NaNs for unavailable public history. Decycler, Decycler Oscillator and Hurst export VALUE; Band-Pass exports SIGNAL and TRIGGER. This produces **60 expected component arrays per language** across the four folders.

Source initialization is explicit zero prehistory and bar-one calculation. Public NaN prefixes are one bar for Decycler, two for Decycler Oscillator, three for Band-Pass, and `length` bars for Hurst (the smoother pairs the current and preceding full range windows). These mark input availability, not recursive convergence. Hurst does not clamp the source's dimension or Hurst estimate. The length-two case is deliberately degenerate and retains dimension zero. Band-Pass preserves the printed `1 + alpha/2` high-pass gains and its separate high-pass trigger, not the Chapter 11 delayed trigger.

## decycler

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `cutoff=60.0` | Published 60-bar cutoff. |
| 2 | `cutoff=30.0` | 30-bar cutoff used in the chapter figures. |
| 3 | `cutoff=5.0` | Fast supported cutoff and strong attenuation of Nyquist noise. |
| 4 | `cutoff=6.0` | Short-cycle cutoff near the supported lower range. |
| 5 | `cutoff=10.0` | Short trend filter. |
| 6 | `cutoff=20.0` | Intermediate cutoff. |
| 7 | `cutoff=40.0` | Intermediate-long cutoff. |
| 8 | `cutoff=60.5` | Fractional coefficient period without window rounding. |
| 9 | `cutoff=80.0` | Slower trend filter. |
| 10 | `cutoff=120.0` | Long recursive memory. |
| 11 | `cutoff=252.0` | Cutoff equal to record length; priming remains input-history based. |
| 12 | `cutoff=500.0` | Cutoff longer than the record; finite recursive startup. |

## decycler-oscillator

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `highpass_period1=30.0, highpass_period2=60.0` | Published two-pole high-pass pair and HP2 minus HP1 sign. |
| 2 | `highpass_period1=10.0, highpass_period2=20.0` | Short octave-spaced cancellation band. |
| 3 | `highpass_period1=20.0, highpass_period2=40.0` | Intermediate octave-spaced cancellation band. |
| 4 | `highpass_period1=20.0, highpass_period2=60.0` | Wider separation between cutoff periods. |
| 5 | `highpass_period1=40.0, highpass_period2=80.0` | Slower octave-spaced cancellation band. |
| 6 | `highpass_period1=60.0, highpass_period2=120.0` | Longer recursive high-pass histories. |
| 7 | `highpass_period1=30.5, highpass_period2=60.5` | Fractional periods for both independent coefficient sets. |
| 8 | `highpass_period1=30.0, highpass_period2=30.0` | Equal filters cancel exactly to zero. |
| 9 | `highpass_period1=60.0, highpass_period2=30.0` | Reversed period order reverses the oscillator sign. |
| 10 | `highpass_period1=5.0, highpass_period2=10.0` | Fast supported high-pass pair. |
| 11 | `highpass_period1=120.0, highpass_period2=252.0` | Long cancellation band spanning the record length. |
| 12 | `highpass_period1=252.0, highpass_period2=500.0` | Both periods at or beyond record length; recursive priming. |

## band-pass-indicator

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `period=20.0, bandwidth=0.3` | Published resonator, peak decay and high-pass trigger defaults. |
| 2 | `period=10.0, bandwidth=0.3` | Short center period. |
| 3 | `period=40.0, bandwidth=0.3` | Longer center period. |
| 4 | `period=60.0, bandwidth=0.3` | Slow center period and phase response. |
| 5 | `period=20.0, bandwidth=0.1` | Narrow pass band and prolonged ringing. |
| 6 | `period=20.0, bandwidth=0.7` | Broad pass band and stronger leading trigger. |
| 7 | `period=20.5, bandwidth=0.3` | Fractional center period without integer rounding. |
| 8 | `period=10.0, bandwidth=0.7` | Short, broad resonator with faster response. |
| 9 | `period=6.0, bandwidth=0.3` | Fast supported center period. |
| 10 | `period=6.0, bandwidth=0.7` | Fast, broad resonator and trigger stability. |
| 11 | `period=100.0, bandwidth=0.3` | Long recursive resonator history. |
| 12 | `period=252.0, bandwidth=0.3` | Center period equal to record length; finite startup. |

## hurst-coefficient

| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `length=30, smoothing_period=20.0` | Published range length and SuperSmoother defaults. |
| 2 | `length=20, smoothing_period=20.0` | Shorter range length used in the chapter cycle example. |
| 3 | `length=200, smoothing_period=20.0` | Long range length used in the chapter trend example. |
| 4 | `length=2, smoothing_period=20.0` | Single-sample half windows: dimension guard always holds its zero seed. |
| 5 | `length=4, smoothing_period=20.0` | Shortest nondegenerate pair of half-window ranges. |
| 6 | `length=10, smoothing_period=20.0` | Fast finite-window structure estimate. |
| 7 | `length=60, smoothing_period=20.0` | Medium-long range measurement. |
| 8 | `length=100, smoothing_period=20.0` | Long range measurement. |
| 9 | `length=250, smoothing_period=20.0` | Current and previous full windows become available at bar 251. |
| 10 | `length=252, smoothing_period=20.0` | 253-observation history requirement: all 252 public rows remain NaN. |
| 11 | `length=30, smoothing_period=10.0` | Faster final SuperSmoother; dimension averaging stays fixed at one half. |
| 12 | `length=30, smoothing_period=20.5` | Fractional final smoothing coefficient period. |

## Completed validation

All 32 Python source-oracle/streaming tests passed. The family exports 60 component arrays and 15,120 values per language (12 each for Decycler, Decycler Oscillator and Hurst, 24 for Band-Pass). Five-language fixture verification passed with exact rounded values/comments/NaN masks and preserved OHLC inputs. Go/Rust/Zig fixture compilation and runtime checks and Node TypeScript loading passed. All twenty fixture files regenerate byte-for-byte identically. Hurst length 252 is all NaN on this 252-close record by the explicitly approved history rule.
