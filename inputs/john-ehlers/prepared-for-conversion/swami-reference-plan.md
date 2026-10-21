# Confirmed Swami master reference plan

Seven self-contained folders have been prepared. The user confirmed all 56 combinations below on 2026-10-21 (8 per folder). Each folder contains its streaming master, complete equations and source notes, independent verification, and generated expected reference data for all five languages. The completed inventory is 216 expected arrays and 1,029,924 scalar values per language across all seven folders. Each folder also includes `validation.md`, `verify_reference_data.py` and `reference_manifest.json`.

## [swami-stochastic](swami-stochastic/description.md)


| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `variant=classic_2012, min_period=6, max_period=48` | Original 2012 price-based default bank and EMA cascade. |
| 2 | `variant=classic_2012, min_period=6, max_period=24` | Compact classic bank and expiration of old extrema. |
| 3 | `variant=classic_2012, min_period=6, max_period=48, range_alpha=1.0, output_alpha=0.5` | Fast classic response with alternate EMA weights. |
| 4 | `variant=classic_2012, min_period=2, max_period=2` | Single classic period and minimum nondegenerate range. |
| 5 | `variant=roofed_2013, min_period=5, max_period=48` | Book 2013 roofed default bank with clipped SuperSmoother history. |
| 6 | `variant=roofed_2013, min_period=5, max_period=24` | Compact roofed bank with shorter rolling windows. |
| 7 | `variant=roofed_2013, min_period=5, max_period=48, shortest_cycle_period=10.5` | Fractional book low-pass coefficient period without rounding. |
| 8 | `variant=roofed_2013, min_period=5, max_period=48, shortest_cycle_period=20.0, longest_cycle_period=80.0` | Slower book roofing band and output smoothing. |

Unlisted parameters retain the configuration-table defaults. Each case exports `HEATMAP`, `MIN` and `MAX`.

## [swami-relative-strength-index](swami-relative-strength-index/description.md)


| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `variant=classic_2012, min_period=12, max_period=48` | Original 2012 Wilder-style changes with fourfold contrast. |
| 2 | `variant=classic_2012, min_period=12, max_period=48, contrast=1.0` | Classic ratio without amplified contrast. |
| 3 | `variant=classic_2012, min_period=12, max_period=24, alpha=0.1` | Compact classic bank with slower output EMA. |
| 4 | `variant=classic_2012, min_period=1, max_period=1` | Single one-change classic RSI boundary. |
| 5 | `variant=roofed_2013, min_period=5, max_period=48` | Book 2013 roofed default bank of finite-window gain/loss ratios. |
| 6 | `variant=roofed_2013, min_period=5, max_period=24` | Compact book bank and correct extra price for P changes. |
| 7 | `variant=roofed_2013, min_period=5, max_period=48, shortest_cycle_period=10.5` | Fractional book low-pass coefficient period without rounding. |
| 8 | `variant=roofed_2013, min_period=5, max_period=48, shortest_cycle_period=20.0, longest_cycle_period=80.0` | Slower book roofing band and output smoothing. |

Unlisted parameters retain the configuration-table defaults. Each case exports `HEATMAP`, `MIN` and `MAX`.

## [swami-aroon](swami-aroon/description.md)


| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_period=8, max_period=48` | TradeStation displayed default and original hidden 4..60 bank. |
| 2 | `min_period=12, max_period=48` | Website advertised display range with literal TradeStation age rules. |
| 3 | `min_period=4, max_period=60` | Entire original computation bank including both endpoints. |
| 4 | `min_period=8, max_period=24` | Compact display must retain original hidden-bank calculations. |
| 5 | `min_period=24, max_period=48` | Long-period display subset and retained extrema ages. |
| 6 | `min_period=4, max_period=4` | Shortest source period as a single displayed bin. |
| 7 | `min_period=60, max_period=60` | Longest source period as a single displayed bin. |
| 8 | `min_period=12, max_period=32` | Intermediate display span and fixed source warm-up. |

Unlisted parameters retain the configuration-table defaults. Each case exports `HEATMAP`, `MIN` and `MAX`.

## [swami-commodity-channel-index](swami-commodity-channel-index/description.md)


| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_period=12, max_period=48, alpha=0.33` | TradeStation CCI default using OHLC typical price. |
| 2 | `min_period=2, max_period=48, alpha=0.33` | Shorter periods expose unbounded CCI normalization before clipping. |
| 3 | `min_period=12, max_period=24, alpha=0.33` | Compact CCI map with identical source smoothing. |
| 4 | `min_period=48, max_period=48, alpha=0.33` | Single long CCI bin. |
| 5 | `min_period=12, max_period=48, alpha=0.1` | Slower CCI color-state smoothing. |
| 6 | `min_period=12, max_period=48, alpha=0.5` | Faster CCI color-state smoothing. |
| 7 | `min_period=12, max_period=48, alpha=1.0` | No CCI EMA memory; normalize then saturate directly. |
| 8 | `min_period=12, max_period=252, alpha=0.33` | Full-record CCI window: only the last bar is public. |

Unlisted parameters retain the configuration-table defaults. Each case exports `HEATMAP`, `MIN` and `MAX`.

## [swami-convolution](swami-convolution/description.md)


| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_period=3, max_period=48, shortest_cycle_period=40.0, longest_cycle_period=80.0` | Book default 40/80 filters and full folded-window map. |
| 2 | `min_period=3, max_period=48, shortest_cycle_period=10.0, longest_cycle_period=48.0` | Faster smoothing exposes short reversal structures. |
| 3 | `min_period=3, max_period=48, shortest_cycle_period=20.0, longest_cycle_period=80.0` | Intermediate smoothing with unchanged long-wave rejection. |
| 4 | `min_period=3, max_period=48, shortest_cycle_period=40.5, longest_cycle_period=80.0` | Fractional smoother period retains real coefficient arithmetic. |
| 5 | `min_period=3, max_period=24, shortest_cycle_period=40.0, longest_cycle_period=80.0` | Compact folded-window map. |
| 6 | `min_period=3, max_period=3, shortest_cycle_period=10.0, longest_cycle_period=48.0` | Shortest supported convolution window as one bin. |
| 7 | `min_period=24, max_period=48, shortest_cycle_period=40.0, longest_cycle_period=80.0` | Long-window-only plume display. |
| 8 | `min_period=3, max_period=48, shortest_cycle_period=40.0, longest_cycle_period=160.0` | Longer high-pass memory preserves the book angle factor. |

Unlisted parameters retain the configuration-table defaults. Each case exports `HEATMAP`, `MIN` and `MAX`. It also exports `CORRELATION`, `STRENGTH` and `DIRECTION` matrices.

## [swami-swing-wave](swami-swing-wave/description.md)


| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_period=8, max_period=40, delta=0.1` | NinjaTrader default band-pass bank and rolling normalization. |
| 2 | `min_period=16, max_period=48, delta=0.1` | Website advertised cycle span with NinjaTrader numerical variant. |
| 3 | `min_period=3, max_period=12, delta=0.1` | Fast short-cycle research extension. |
| 4 | `min_period=8, max_period=24, delta=0.1` | Compact bank and expiring filtered extrema. |
| 5 | `min_period=8, max_period=40, delta=0.25` | Broader passband than the original narrow filter. |
| 6 | `min_period=8, max_period=40, delta=0.5` | Wide passband and fast decay. |
| 7 | `min_period=40, max_period=40, delta=0.1` | Single-cycle normalization and filter state. |
| 8 | `min_period=8, max_period=250, delta=0.1` | Full-record boundary: longest bin first appears on the last bar. |

Unlisted parameters retain the configuration-table defaults. Each case exports `HEATMAP`, `MIN` and `MAX`.

## [swami-market-mode](swami-market-mode/description.md)


| Case | Parameters | What it tests |
| --- | --- | --- |
| 1 | `min_period=4, max_period=48, delta=0.25, fraction=0.25, peak_average_length=50` | OmniTrader heatmap defaults with exact coefficient-table reconstruction. |
| 2 | `min_period=12, max_period=48, delta=0.5, fraction=0.1, peak_average_length=50` | Article scalar defaults across the advertised Swami cycle span. |
| 3 | `min_period=4, max_period=24, delta=0.25, fraction=0.25, peak_average_length=50` | Compact market-mode bank with shorter trend averages. |
| 4 | `min_period=4, max_period=48, delta=0.1, fraction=0.25, peak_average_length=50` | Narrower band-pass than the optimized heatmap table. |
| 5 | `min_period=4, max_period=48, delta=0.25, fraction=0.1, peak_average_length=50` | Lower cycle threshold favors trend classification. |
| 6 | `min_period=4, max_period=48, delta=0.25, fraction=0.5, peak_average_length=50` | Higher cycle threshold favors cycle classification. |
| 7 | `min_period=4, max_period=48, delta=0.25, fraction=0.25, peak_average_length=20` | Shorter averaging of persistent detected extrema. |
| 8 | `min_period=4, max_period=48, delta=0.25, fraction=0.25, peak_average_length=251` | Insufficient record for peak averaging: every public result is NaN. |

Unlisted parameters retain the configuration-table defaults. Each case exports `HEATMAP`, `MIN` and `MAX`. It also exports `MEAN`, `UPPER` and `LOWER` matrices.

