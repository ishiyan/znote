# QPL-CNON (PyTorch)

## Overview

QPL-CNON (Quantum Price Level — Chaotic Neural Oscillatory Network) is a supervised financial forecasting model that predicts next-bar OHLC prices. It combines:

1. **QPL (Quantum Price Levels)** — Computes 21 discrete support/resistance levels from the quantum anharmonic oscillator model, used as additional "quantum field signal" inputs.
2. **CNON (Chaotic Neural Oscillatory Network)** — A feedforward backpropagation network where every neuron is replaced by a Lee-Oscillator, providing transient-chaotic activation dynamics.

This is a faithful PyTorch reimplementation of the system described in Lee (2021) §4–5 and Lee (2019) Ch.11.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    INPUT LAYER                        │
│  5-day OHLC (20 values) + 21 QPL levels = 41 inputs │
│  Each input node is a Lee-Oscillator                 │
├─────────────────────────────────────────────────────┤
│                   HIDDEN LAYER                        │
│  41 Lee-Oscillator nodes                             │
├─────────────────────────────────────────────────────┤
│                   OUTPUT LAYER                        │
│  4 Lee-Oscillator nodes → next-day O, H, L, C       │
└─────────────────────────────────────────────────────┘
```

### Input Features (41 total)

| Index | Feature | Description |
|-------|---------|-------------|
| 0–3 | OHLC(t) | Today's Open, High, Low, Close |
| 4–7 | OHLC(t-1) | Yesterday's OHLC |
| 8–11 | OHLC(t-2) | 2 days ago |
| 12–15 | OHLC(t-3) | 3 days ago |
| 16–19 | OHLC(t-4) | 4 days ago |
| 20–40 | QPL(0..20) | 21 closest quantum price levels |

All inputs are normalized to [0, 1] using min-max scaling over the lookback window.

### QPL as Input Signals

The 21 QPL levels are computed from the most recent 2048 bars using `QuantumPriceLevels`. They represent discrete support/resistance levels derived from the quantum anharmonic oscillator model. Lee calls these "Quantum Field Signals" (QFS).

For the input vector, we use the 21 NQPR multipliers directly (they're already in a natural [1.0, ~1.1] range and are normalized along with the OHLC data).

---

## Training

- **Loss:** MSE on next-day OHLC (4 outputs)
- **Optimizer:** Adam (Lee uses standard backprop, but Adam converges faster)
- **Normalization:** Min-max over a rolling window or the full training set
- **Epochs:** Typically 100–500 with early stopping
- **Batch size:** 32–128

### Data Pipeline

```
Raw OHLC bars (2048+ history)
    │
    ├─→ QPL computation (lookback=2048) → 21 NQPR multipliers
    │
    ├─→ 5-day sliding window → 20 OHLC values
    │
    └─→ Normalize all 41 features to [0, 1]
         │
         └─→ Target: next-day OHLC (normalized)
```

---

## Files

- `qpl_cnon.py` — Model definition, dataset, training loop, inference
- `description.md` — This file

### Dependencies

- PyTorch >= 1.8
- The `lee_oscillator.py` module (from `lee-oscillator-pytorch/`)
- The `quantum-price-levels.py` module (from `quantum-price-levels/`)

---

## Usage

```python
from qpl_cnon import QPLCNON, QPLCNONDataset, train

# Prepare data: list of OHLC bars (oldest first)
# Each bar: (open, high, low, close)
bars = [...]  # 2048+ bars

# Create dataset
dataset = QPLCNONDataset(bars, qpl_lookback=2048)

# Train
model = QPLCNON(n_steps=50)
train(model, dataset, epochs=200, lr=1e-3)

# Predict next bar
prediction = model.predict(bars[-2048:])  # returns (open, high, low, close)
```

---

## Differences from Lee's Original

| Aspect | Lee (2019/2021) | This implementation |
|--------|----------------|---------------------|
| Framework | QFSDK DLL (C++) | PyTorch |
| Optimizer | Vanilla SGD backprop | Adam (configurable) |
| QPL levels | 20 levels | 21 levels (including n=0) |
| Normalization | Custom per-signal | Min-max over window |
| Lee-oscillator params | Fixed (from QFSDK) | Configurable, optionally learnable |
| Training | Online (1 sample at a time) | Mini-batch |

---

## References

- Lee, R. S. T. (2021). §4–5: QPL-CNON architecture and training algorithm.
- Lee, R. S. T. (2019). Ch.11: TSCNON for financial prediction.
- Lee, R. S. T. (2004). IEEE TNN: Lee-oscillator.
