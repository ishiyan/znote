# Raymond Lee — Implementable Indicators & Utilities

## Summary

| # | Name | Type | Self-contained? | Difficulty | Priority |
|---|------|------|-----------------|------------|----------|
| 1 | **Quantum Price Levels (QPL)** | Indicator (S&R levels) | YES — full algorithm + code | Easy | High |
| 2 | **Lee-Oscillator** | Activation function | YES — equations complete | Easy | Medium |
| 3 | **QPL-CNON** | Forecast network | Mostly — architecture known, backprop derivable | Hard | Low |

---

## 1. Quantum Price Levels (QPL)

**Sources:** 2021 paper §3.5–3.6, MQ4 code, Python code (qffc.uic.edu.cn)

**What it produces:** 21 discrete price levels above and below today's open — quantum-derived support/resistance.

**Algorithm:**

1. Compute daily price returns: $r(t) = \text{Close}(t) / \text{Close}(t-1)$
2. Compute $\mu$, $\sigma$ of returns over 2048 days
3. Build wavefunction histogram: 100 bins, width $dr = 3\sigma/50$, centered at $r=1$
4. Normalize histogram → $NQ[i]$
5. Find peak bin (ground state, `maxQno`)
6. Evaluate anharmonic coefficient $\lambda$:
   $$\lambda = \left|\frac{r_{-1}^2 \cdot NQ[\text{maxQno}-1] - r_{+1}^2 \cdot NQ[\text{maxQno}+1]}{r_{+1}^4 \cdot NQ[\text{maxQno}+1] - r_{-1}^4 \cdot NQ[\text{maxQno}-1]}\right|$$
7. Compute $K_0(n)$:
   $$K_0(n) = \left[\frac{1.1924 + 33.2383n + 56.2169n^2}{1 + 43.6196n}\right]^{1/3}$$
8. Solve depressed cubic (Cardano) for each energy level $n = 0..20$:
   $$E^3 - (2n+1)^2 E - \lambda(2n+1)^3 K_0(n)^3 = 0$$
9. Quantum Price Return: $QPR(n) = QFEL(n) / QFEL(0)$
10. Normalized: $NQPR(n) = 1 + 0.21 \cdot \sigma \cdot QPR(n)$
11. Daily levels: $QPL_{+n} = \text{Open} \times NQPR(n)$, $QPL_{-n} = \text{Open} / NQPR(n)$

**Parameters:** lookback (default 2048), num_levels (default 21)

**Dependencies:** None. Pure math — arithmetic, histogramming, Cardano's formula.

**Notes:** The MQ4 and Python implementations on qffc.uic.edu.cn are fully standalone. The Python version uses numpy/pandas for data loading but the core math is stdlib-portable. The MQ4 version does NOT use any DLL for QPL computation itself.

---

## 2. Lee-Oscillator

**Sources:** 2021 paper §4, Book Ch.9

**What it is:** A 4-neuron chaotic oscillatory unit used as activation function replacement for sigmoid/ReLU in neural networks.

**Equations:**

$$E(t+1) = \sigma(e_1 \cdot E(t) - e_2 \cdot I(t) + S(t) - \theta_E)$$
$$I(t+1) = \sigma(i_1 \cdot E(t) - i_2 \cdot I(t) - \theta_I)$$
$$\Omega(t+1) = \sigma(S(t))$$
$$L(t) = [E(t) - I(t)] \cdot \exp(-k \cdot S(t)^2) + \Omega(t)$$

Where $\sigma(x) = 1/(1+e^{-x})$ and $e_1, e_2, i_1, i_2, k, \theta_E, \theta_I$ are parameters.

**Properties:** Exhibits transient chaos — rapid exploration of state space followed by convergence. Used as drop-in activation replacement in feedforward backpropagation networks.

**Dependencies:** None.

**Notes:** Interesting as a standalone utility module. Could be useful for any neural-network-based indicator. The key novelty is that it's a recurrent 4-state unit that produces chaotic dynamics, potentially escaping local minima faster than standard activations.

---

## 3. QPL-CNON (Time Series Chaotic Neural Oscillatory Network)

**Sources:** 2021 paper §4–5, Book Ch.11

**What it is:** A forecasting network that takes 5 days of OHLC + 21 QPL levels as input and predicts next-day OHLC.

**Architecture:**
- Input: 20 Lee-oscillators (5-day × OHLC) + 21 Lee-oscillators (QPL) = 41 nodes
- Hidden: 41 Lee-oscillators
- Output: 4 Lee-oscillators (next-day O, H, L, C)
- Training: feedforward backprop with Lee-oscillator transfer function

**Dependencies:** The practical implementation uses `maxnet.dll` (closed-source Windows DLL from QFSDK), but the architecture and all math are published. The DLL is a convenience library packaging standard backprop with Lee-oscillator activation — replaceable.

**Difficulty:** The main challenge is computing gradients through the recurrent Lee-oscillator unit. The equations are differentiable so it's doable, but non-trivial to implement correctly. Lower priority since it's a full training system rather than a simple indicator.

---

## On the Closed-Source DLLs

The `.mq4` files in the `qffc.uic.edu.cn/` subfolders depend on:
- `maxnet.dll` — Neural network training/inference (standard backprop + Lee-oscillator)
- `QFSDKv1.dll` — Higher-level wrapper

**These are needed ONLY for the neural network portion (training QPL-CNON).** The QPL indicator computation itself is fully self-contained — no DLL dependency.

**Is the Python code DLL-dependent?** No. The Python QPL code on the website uses only numpy/pandas/PyTorch. PyTorch is used only if you want to train the neural network; the QPL computation itself is pure numpy. So the Python code is fully portable.

**Are the MQ4 files still useful?** Yes — they document the exact QPL algorithm implementation clearly in procedural code. The DLL calls are only in the separate neural network training scripts, not in the QPL computation itself.

---

## Recommendation

**Implement QPL first** — it's a novel, fully-documented indicator producing discrete support/resistance levels from first principles (quantum mechanics analogy). No machine learning required. The output is directly usable as a trading indicator (21 price levels above and below current price, recomputed daily).

**Lee-Oscillator second** — as a standalone utility module, useful if we later want to build neural network indicators.

**QPL-CNON** — skip for now. It's a full forecast system requiring training infrastructure. The QPL levels themselves are the novel contribution; feeding them into any ML model (not necessarily Lee-oscillator based) would work.
