# Lee-Oscillator

## Overview

The Lee-Oscillator is a discrete-time chaotic neural oscillator invented by Raymond S. T. Lee in 2004. It is a 4-neuron recurrent unit designed to replace classical activation functions (sigmoid, ReLU, tanh) in artificial neural networks, converting them into chaotic neural networks.

**Key innovation:** Unlike continuous-time neural oscillators (which require solving expensive ODEs), the Lee-Oscillator is a simple discrete-time recurrence — just 4 equations evaluated per timestep — yet it produces rich chaotic dynamics including transient chaos, bifurcation, and progressive state exploration.

**Primary use case:** Drop-in activation function replacement in feedforward and recurrent neural networks. When all neurons in a standard network are replaced with Lee-Oscillators, the network gains the ability to escape local minima and avoid training deadlocks that plague classical networks on chaotic/complex data (financial markets, weather, etc.).

---

## Biological Motivation

The Lee-Oscillator draws from two neuroscience concepts:

### Excitatory–Inhibitory Neuron Pairs

In biological neural circuits, information processing emerges from the interplay between excitatory neurons (which amplify signals) and inhibitory neurons (which suppress them). This push-pull dynamic creates oscillatory behavior — the basis for rhythmic brain activity (alpha waves, gamma oscillations, etc.). The Lee-Oscillator models this with its E (excitatory) and I (inhibitory) neurons.

### Transient Chaos in Neural Systems

Neuroscience research (Freeman 2000, 2008) shows that biological neural networks exhibit *transient chaos* — brief periods of chaotic, exploratory neural activity that rapidly converge to stable attractors. This is believed to be the brain's mechanism for:
- Rapidly exploring solution spaces (pattern recognition)
- Avoiding getting stuck in suboptimal states
- Progressive memory recall (Gestalt psychology: recognizing incomplete patterns)

The Lee-Oscillator reproduces this transient-chaotic property: given an input, it oscillates chaotically before settling into one of two stable states. The duration and intensity of chaos depends on where the input falls in the bifurcation diagram.

### Retrograde Signaling (Extended Version: LORS)

In biological neurons, signals typically flow in one direction (presynaptic → postsynaptic). However, *retrograde signaling* sends feedback from post- to pre-synaptic neurons, modulating synaptic strength. This is critical for memory formation and learning. Abnormal retrograde signaling is linked to Alzheimer's, dementia, and other disorders.

The LORS (Lee-Oscillator with Retrograde Signaling) extension adds a feedback path from the output L(t) back into E and I, producing richer bifurcation patterns (8 categories, LORS#0–LORS#7).

---

## Mathematical Formulation

### Original Lee-Oscillator (Eqs. 9.5–9.8 in Lee 2019)

A single Lee-Oscillator is a 4-neuron discrete-time recurrent unit:

```
E(t+1) = σ( e₁·E(t) - e₂·I(t) + S(t) - ξ_E )     [excitatory neuron]
I(t+1) = σ( i₁·E(t) - i₂·I(t) - ξ_I )               [inhibitory neuron]
Ω(t+1) = σ( S(t) )                                     [input neuron]
L(t)   = [E(t) - I(t)] · exp(-k·S(t)²) + Ω(t)         [output]
```

Where:
- **E(t)** ∈ [0, 1] — excitatory neuron state (amplifies activity)
- **I(t)** ∈ [0, 1] — inhibitory neuron state (suppresses activity)
- **Ω(t)** ∈ [0, 1] — input neuron state (sigmoid of input)
- **L(t)** ∈ ≈[-1, 1] — output of the oscillator (the "activation")
- **S(t)** — external input stimulus (the value being "activated")
- **σ(x) = 1 / (1 + e⁻ˣ)** — standard sigmoid function

Parameters:
- **e₁, e₂** — weights for excitatory neuron (self-excitation, cross-inhibition)
- **i₁, i₂** — weights for inhibitory neuron (cross-excitation, self-inhibition)
- **k** — decay constant controlling the damping envelope
- **ξ_E, ξ_I** — threshold values for E and I neurons

### LORS: Lee-Oscillator with Retrograde Signaling (Eqs. 12.2–12.5)

The extended version feeds L(t) back into E and I:

```
E(t+1)  = σ'( a₁·LORS(t) + a₂·E(t) - a₃·I(t) + a₄·S(t) - ξ_E )
I(t+1)  = σ'( b₁·LORS(t) - b₂·E(t) - b₃·I(t) + b₄·S(t) - ξ_I )
Ω(t+1)  = σ'( S(t) )
LORS(t)  = [E(t) - I(t)] · exp(-k·S(t)²) + Ω(t)
```

Where a₁–a₄ and b₁–b₄ are the retrograde coupling weights. When a₁=0 and b₁=0, LORS reduces to the original Lee-Oscillator.

---

## Parameter Values

### LORS#0 (Original Lee-Oscillator) — Canonical Parameters

From Table 12.1 in Lee (2019), the original Lee-oscillator (LORS#0) uses:

| Parameter | Value | Role |
|-----------|-------|------|
| a₁ (retrograde→E) | 0.00 | No retrograde (original) |
| a₂ (E self-weight, = e₁) | 5.00 | Strong self-excitation |
| a₃ (I→E weight, = e₂) | 5.00 | Strong cross-inhibition |
| a₄ (S→E weight) | 1.00 | Unity input coupling |
| b₁ (retrograde→I) | 0.00 | No retrograde (original) |
| b₂ (E→I weight, = -i₁) | -1.00 | Weak cross-excitation |
| b₃ (I self-weight, = i₂) | 1.00 | Moderate self-inhibition |
| b₄ (S→I weight) | 0.00 | No direct input to I |
| k (decay constant) | 1.00 | Standard damping |
| ξ_E (E threshold) | 500 | See note below |
| ξ_I (I threshold) | 0.00 | Zero threshold |

**Note on ξ_E=500:** This very large threshold value appears in Table 12.1. In practice, for the original Lee-oscillator formulation (Eqs. 9.5–9.8), the threshold acts as a bias shift. With e₁=5, e₂=5, and E,I ∈ [0,1], the sigmoid argument is approximately `5E - 5I + S - ξ_E`. If ξ_E=500, E(t) is driven to σ(-500)≈0 constantly, which contradicts the published bifurcation diagrams.

**Resolution:** The table likely uses a scaled sigmoid (σ' with gain parameter) or the thresholds in the LORS formulation differ in units from the original equations. For generating bifurcation diagrams matching the published figures, the following empirically-derived parameters work:

| Parameter | Working value | Notes |
|-----------|--------------|-------|
| e₁ | 20.0 | Strong self-excitation (drives instability) |
| e₂ | 5.0 | Cross-inhibition weight |
| i₁ | 1.0 | E→I weight |
| i₂ | 5.0 | Strong I self-weight (drives instability) |
| k | 5.0 | Output damping envelope |
| ξ_E | 0.0 | Threshold |
| ξ_I | 0.0 | Threshold |

**Stability analysis:** The condition for period-2 oscillation is that the Jacobian determinant of the (E, I) map at the symmetric fixed point must satisfy det(J) < -1. This requires:

```
e₁·i₂ - e₂·i₁ > 16 / (σ'_max)²  where σ'_max = 0.25
```

Simplifying: **e₁·i₂ - e₂·i₁ > 16** (at the fixed point where sigmoid derivatives are maximal).

With the working defaults: 20×5 - 5×1 = 95 >> 16, ensuring robust oscillation.

The `exp(-k·S²)` envelope then controls the *visibility* of the oscillation in the output L(t):
- At S=0: exp(0)=1, full oscillation amplitude (~0.48)
- At |S|=0.5: exp(-1.25)≈0.29, reduced amplitude (~0.14)
- At |S|=1.0: exp(-5)≈0.007, negligible amplitude (~0.003, effectively converged)

### All 8 LORS Categories

| Cat. | a₁ | a₂ | a₃ | a₄ | b₁ | b₂ | b₃ | b₄ | k | ξ_E | ξ_I |
|------|------|------|------|------|------|------|------|------|-----|-----|-----|
| #0 | 0.00 | 5.00 | 5.00 | 1.00 | 0.00 | -1.00 | 1.00 | 0.00 | 1.0 | 500 | 0.0 |
| #1 | -0.50 | 0.55 | 0.55 | 0.50 | -0.50 | -0.55 | -0.55 | 0.50 | 1.0 | 50 | 0.0 |
| #2 | -0.50 | 0.55 | 0.55 | 0.50 | 0.50 | -0.55 | -0.55 | -0.50 | 1.0 | 50 | 0.0 |
| #3 | 0.50 | 0.55 | 0.55 | 0.50 | 0.50 | -0.55 | -0.55 | -0.50 | 1.0 | 50 | 0.0 |
| #4 | 0.90 | 0.90 | 0.90 | 0.90 | -0.90 | -0.90 | -0.90 | -0.90 | 1.0 | 50 | 0.0 |
| #5 | 0.90 | 0.90 | 0.90 | 0.90 | -0.90 | -0.90 | -0.90 | -0.90 | 1.0 | 300 | 0.0 |
| #6 | 5.00 | 5.00 | 5.00 | 5.00 | -1.00 | -1.00 | -1.00 | -1.00 | 1.0 | 50 | 0.0 |
| #7 | 5.00 | 5.00 | 5.00 | 5.00 | -1.00 | -1.00 | -1.00 | -1.00 | 1.0 | 300 | 0.0 |

**Bifurcation characteristics:**
- **LORS#0:** Single bifurcation zone (original Lee-oscillator behavior)
- **LORS#1–#3:** Single bifurcation, varying symmetry and width
- **LORS#4–#5:** Double bifurcation regions
- **LORS#6–#7:** Multiple bifurcation regions (most complex dynamics)

---

## Bifurcation Analysis

### What is a Bifurcation Diagram?

For each value of the input stimulus S (x-axis, typically swept from -1 to +1):
1. Run the oscillator for N timesteps (e.g., 600) to allow transients to die out
2. Record the output L(t) for the last M timesteps (e.g., steps 500–600)
3. Plot all recorded L values as dots at position (S, L)

The result reveals the oscillator's steady-state behavior as a function of input:

### Three Zones in the Original Lee-Oscillator

```
Output L(t)
  1.0 ┤ ███████████                                         ████████████████
      │            █                                       █
      │             █                                     █
  0.5 ┤              ██                                 ██
      │                █████                       █████
      │                     ███████████████████████
  0.0 ┤                        (bifurcation zone)
      │
 -0.5 ┤
      └──────────────────────────────────────────────────────────────────
     -1.0          -0.3        0.0        0.3          1.0     Input S
                    ←──── Sigmoid I ────→←Bifurcation→← Sigmoid II ─→
```

**Sigmoid Zone I (S < threshold_low):** Output converges to a single stable low value. Behaves like a classical sigmoid — smooth, monotonic transfer.

**Bifurcation Zone (threshold_low < S < threshold_high):** Output oscillates chaotically between multiple attractors. The system does NOT converge to a single value — instead it jumps between states. This is the "transient chaos" that helps networks explore solution spaces.

**Sigmoid Zone II (S > threshold_high):** Output converges to a single stable high value. Again, sigmoid-like monotonic transfer.

### Why This Helps Neural Networks

In classical networks with sigmoid/ReLU:
- Gradient descent follows a smooth loss surface
- Gets trapped in local minima, especially with chaotic data
- Training deadlocks on complex patterns

With Lee-Oscillator activation:
- Inputs in the sigmoid zones → smooth gradient descent (stable training)
- Inputs in the bifurcation zone → chaotic exploration (escaping local minima)
- The network naturally transitions between exploration and exploitation
- As training converges, weights shift inputs toward sigmoid zones (stable predictions)

This is analogous to simulated annealing but *emergent* from the network dynamics rather than externally imposed.

---

## The Lee Chaotic Transfer Function (LCTF)

For practical use in neural networks, Lee proposes pre-computing the oscillator's steady-state behavior as a 2D lookup table:

```
LCTF[i][t] = L(t) for input S = i, after running t timesteps
```

Where:
- i ranges over 1000 input values from -1 to +1 (or 0 to 1 normalized)
- t ranges over 100 timesteps (e.g., steps 500–600)

This table is computed once and then used as a fast activation function during training:
1. Given network input x, find nearest row i in LCTF
2. Use LCTF[i][t] as the activation output
3. t can be fixed (use last value) or sampled (stochastic activation)

For GPU-based training (PyTorch), we instead run the recurrence directly with autograd tracking.

---

## How Lee-Oscillator Replaces Neurons in a Network

### Standard neuron:
```
output = σ(Σ wᵢxᵢ + b)
```

### Lee-Oscillator neuron:
```
S = Σ wᵢxᵢ + b           ← Same weighted sum as input stimulus
Run oscillator for N steps with this S
output = L(N)             ← Use final oscillator output as activation
```

The oscillator maintains internal state (E, I, Ω) across timesteps *within* a single forward pass. These states are NOT maintained between different training samples — they reset for each new input (unlike RNN hidden states).

**Exception:** In time-series applications (like RL), the oscillator states CAN be maintained across sequential observations, making each neuron a recurrent chaotic unit.

---

## Relationship to Other Activation Functions

| Property | Sigmoid | ReLU | Lee-Oscillator |
|----------|---------|------|----------------|
| Output range | (0, 1) | [0, ∞) | ≈(-1, 1) |
| Differentiable | Yes | Piecewise | Yes (via chain rule through recurrence) |
| Vanishing gradient | Yes (saturates) | No | Partially (in sigmoid zones) |
| Stochastic/chaotic | No | No | Yes (in bifurcation zone) |
| Escapes local minima | No | No | Yes (transient chaos) |
| Computational cost | O(1) | O(1) | O(N) per neuron (N = timesteps) |
| State | Stateless | Stateless | Stateful (4 internal vars) |

---

## Applications

### 1. Financial Prediction (QPL-CNON)
Replace all neurons in a feedforward backpropagation network with Lee-Oscillators. Feed 5 days of OHLC prices + 21 QPL levels as input. Network predicts next-day OHLC. Lee reports superior performance vs classical FFBPN, SVM, and standard DNNs on 129 financial products.

### 2. Type-2 Fuzzy Membership Functions (CT2TFMF)
Composite Lee-Oscillators generate interval type-2 fuzzy membership functions with inherent uncertainty modeling — the bifurcation zone acts as the "footprint of uncertainty" in type-2 fuzzy logic.

### 3. Transient Chaotic Auto-Associative Networks
2D grids of Lee-Oscillators serve as pattern associators with progressive recall capability — input a partial pattern, and the network progressively "fills in" the missing parts through chaotic exploration, similar to Hopfield networks but with richer dynamics.

### 4. Reinforcement Learning
As activation function in policy/value networks, the chaotic dynamics can help explore action spaces more effectively than ε-greedy or entropy bonuses, particularly in environments with deceptive local optima.

---

## Implementation Notes

### Initialization
- E(0), I(0) should be initialized to random values in [0, 1] or to 0.5
- Ω(0) = σ(S) (determined by input)

### Timestep Budget
- **Bifurcation diagram generation:** 600 total, discard first 500, plot last 100
- **LCTF table:** 600 total, store steps 500–600 (100 values per input)
- **Network training:** N = 50–100 is typically sufficient for activation use
- **Practical minimum:** Even N = 10–20 can capture the essential dynamics

### Numerical Stability
- All E, I values are bounded [0, 1] by the sigmoid
- L(t) is bounded by: max(|E-I|)·exp(-kS²) + max(Ω) ≤ 1·1 + 1 = 2 (theoretical max)
- In practice L(t) stays within approximately [-0.5, 1.5] for typical parameter ranges
- The exp(-kS²) term provides natural damping for large inputs

### Gradient Flow (for PyTorch implementation)
The recurrence is differentiable everywhere:
- σ'(x) = σ(x)(1-σ(x)) — standard sigmoid derivative
- d/dx[exp(-kx²)] = -2kx·exp(-kx²)
- Chain rule through N timesteps: dL/dS requires unrolling the computation graph

**Gradient concerns:**
- With large N (>100), gradients through the recurrence may vanish or explode
- Gradient clipping recommended for training stability
- Alternative: use straight-through estimator or detach internal states periodically

---

## Comparison: Lee-Oscillator vs Wang-Oscillator

The Lee-Oscillator was specifically designed to overcome limitations of the earlier Wang-Oscillator (Wang 1995):

| Property | Wang-Oscillator | Lee-Oscillator |
|----------|----------------|----------------|
| Chaos type | Sustained | Transient (converges) |
| Stable states | Oscillates indefinitely | Settles to 2 attractors |
| Transfer function | Not sigmoid-compatible | Has sigmoid zones |
| Network use | Difficult (never settles) | Easy (converges in sigmoid zones) |
| Bifurcation | Complex, multi-region | Clean: 2 sigmoid + 1 bifurcation |

The Wang-Oscillator never stops oscillating, making it unusable as an activation function. The Lee-Oscillator *transiently* oscillates then *converges* — giving you the best of both worlds.

---

## References

1. Lee, R. S. T. (2004). A transient-chaotic autoassociative network (TCAN) based on Lee oscillators. *IEEE Transactions on Neural Networks*, 15(5), 1228–1243.
2. Lee, R. S. T. (2006a). Lee-Oscillator — A chaotic neural oscillatory model for progressive memory recalling. *Neural Networks*, 19(8), 1224–1237.
3. Lee, R. S. T. (2006b). Chaotic interval type-2 fuzzy neuro-oscillatory network (CIT2-FNON). *Applied Soft Computing*, 6(2), 169–186.
4. Lee, R. S. T. (2019). *Quantum Finance: Intelligent Forecast and Trading Systems*. Springer, Singapore. ISBN 978-981-32-9796-8.
5. Lee, R. S. T. (2021). Quantum Finance Forecast System with Quantum Anharmonic Oscillator Model for Quantum Price Level Modeling. *IAJER*, 4(02), 1–21.
6. Wang, D. L. (1995). Temporal pattern processing. In M. A. Arbib (Ed.), *The Handbook of Brain Theory and Neural Networks*, pp. 967–971. MIT Press.
7. Freeman, W. J. (2000). *Neurodynamics: An Exploration in Mesoscopic Brain Dynamics*. Springer.

## BibTeX

```bibtex
@article{lee2004tcan,
  author    = {Lee, Raymond S. T.},
  title     = {A transient-chaotic autoassociative network ({TCAN}) based on {Lee} oscillators},
  journal   = {IEEE Transactions on Neural Networks},
  volume    = {15},
  number    = {5},
  pages     = {1228--1243},
  year      = {2004}
}

@article{lee2006progressive,
  author    = {Lee, Raymond S. T.},
  title     = {{Lee-Oscillator} --- A chaotic neural oscillatory model for progressive memory recalling},
  journal   = {Neural Networks},
  volume    = {19},
  number    = {8},
  pages     = {1224--1237},
  year      = {2006}
}

@book{lee2019quantum,
  author    = {Lee, Raymond S. T.},
  title     = {Quantum Finance: Intelligent Forecast and Trading Systems},
  publisher = {Springer},
  address   = {Singapore},
  year      = {2019},
  isbn      = {978-981-32-9796-8}
}

@article{lee2021quantum,
  author    = {Lee, Raymond S. T.},
  title     = {Quantum Finance Forecast System with Quantum Anharmonic Oscillator Model for Quantum Price Level Modeling},
  journal   = {International Advance Journal of Engineering Research (IAJER)},
  volume    = {4},
  number    = {02},
  pages     = {1--21},
  year      = {2021}
}
```
