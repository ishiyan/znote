# Lee-Oscillator (PyTorch)

## Overview

PyTorch implementation of the Lee-Oscillator as a drop-in neural network module. Provides two levels of abstraction:

- **`LeeOscillatorCell`** — A single oscillator unit (replaces one neuron)
- **`LeeOscillatorLayer`** — A full layer of oscillators (replaces `nn.Linear` + activation)

Both support:
- Configurable iteration count `n_steps` (controls exploration vs speed tradeoff)
- Optionally learnable parameters (e₁, e₂, i₁, i₂, k, ξ_E, ξ_I)
- Batched operation on GPU
- Full autograd support (gradients flow through the recurrence)

---

## API Reference

### `LeeOscillatorCell`

A single Lee-Oscillator unit. Takes a scalar (or batched) input S and produces a scalar output L after running the recurrence for `n_steps`.

```python
from lee_oscillator import LeeOscillatorCell

cell = LeeOscillatorCell(
    e1=20.0, e2=5.0, i1=1.0, i2=5.0,  # dynamics weights
    k=5.0,                               # output damping
    xi_e=0.0, xi_i=0.0,                 # thresholds
    n_steps=50,                          # iterations per forward pass
    learnable=False,                     # if True, params become nn.Parameter
)

# Forward: input shape (batch_size,) or (batch_size, 1)
output = cell(input_tensor)  # shape: same as input
```

**Use case:** Custom architectures where you want per-neuron control. For example, a single Lee-Oscillator as the final action-selection neuron in an actor network.

### `LeeOscillatorLayer`

A full layer that replaces `nn.Linear(in_features, out_features) + nn.ReLU()`. Internally contains `out_features` independent oscillator units, each receiving a weighted sum of inputs.

```python
from lee_oscillator import LeeOscillatorLayer

layer = LeeOscillatorLayer(
    in_features=64,
    out_features=32,
    n_steps=50,
    learnable_oscillator=False,  # oscillator params learnable?
    bias=True,                   # linear layer bias
    # Oscillator params (shared across all units in layer):
    e1=20.0, e2=5.0, i1=1.0, i2=5.0,
    k=5.0, xi_e=0.0, xi_i=0.0,
)

# Forward: input shape (batch_size, in_features)
output = layer(input_tensor)  # shape: (batch_size, out_features)
```

**Equivalent to:**
```python
nn.Sequential(
    nn.Linear(64, 32),
    LeeOscillatorCell(n_steps=50)  # applied element-wise
)
```

---

## Integration Examples

### Replace ReLU in an MLP Policy (Pure PyTorch)

```python
import torch.nn as nn
from lee_oscillator import LeeOscillatorLayer

class LeePolicy(nn.Module):
    def __init__(self, obs_dim, act_dim, hidden=64):
        super().__init__()
        self.net = nn.Sequential(
            LeeOscillatorLayer(obs_dim, hidden, n_steps=30),
            LeeOscillatorLayer(hidden, hidden, n_steps=30),
            nn.Linear(hidden, act_dim),  # final layer: standard linear
            nn.Tanh(),                   # bound actions
        )

    def forward(self, obs):
        return self.net(obs)
```

### Custom Actor-Critic with Learnable Oscillator Params

```python
class LeeCritic(nn.Module):
    def __init__(self, obs_dim, hidden=64):
        super().__init__()
        self.layer1 = LeeOscillatorLayer(
            obs_dim, hidden, n_steps=50, learnable_oscillator=True
        )
        self.layer2 = LeeOscillatorLayer(
            hidden, hidden, n_steps=50, learnable_oscillator=True
        )
        self.value_head = nn.Linear(hidden, 1)

    def forward(self, obs):
        x = self.layer1(obs)
        x = self.layer2(x)
        return self.value_head(x)
```

### Mixed Architecture (Lee-Oscillator + Standard Layers)

```python
class HybridPolicy(nn.Module):
    """First layers standard (fast), last layer Lee-Oscillator (chaotic exploration)."""
    def __init__(self, obs_dim, act_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(obs_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
        )
        # Only the final hidden→action mapping uses Lee-Oscillator
        self.action_head = LeeOscillatorLayer(64, act_dim, n_steps=30)

    def forward(self, obs):
        features = self.encoder(obs)
        return torch.tanh(self.action_head(features))
```

---

## Design Decisions

### Stateless per Forward Pass (Mode A)

Each `forward()` call:
1. Initializes E, I, Ω to defaults (0.5, 0.5, σ(S))
2. Runs the recurrence for `n_steps` with the input S held constant
3. Returns the final L(n_steps)

Internal state is NOT maintained between forward calls. This means:
- Each input is processed independently (like a standard activation)
- Suitable for feedforward policies and value functions
- Batch parallelism is straightforward

**When you'd want persistent state:** Time-series RL where you want the oscillator to "remember" across steps. This is a separate mode (RNN-like) not implemented in v1 but architecturally trivial to add.

### Parameter Sharing

All oscillator units in a `LeeOscillatorLayer` share the same parameters (e₁, e₂, i₁, i₂, k, ξ_E, ξ_I). This is intentional:
- Reduces parameter count
- The diversity comes from different input values S (weighted sums differ per unit)
- Learnable parameters tune the "character" of the entire layer's chaotic behavior

For per-unit parameters, use multiple `LeeOscillatorCell` instances manually.

### Gradient Flow

The recurrence is unrolled for `n_steps` — autograd tracks all operations. Considerations:

- **N=10–30:** Fast, gradients stable, mild chaotic benefit
- **N=50:** Good balance of chaos and training stability (recommended)
- **N=100+:** Strong chaos, but risk of gradient explosion/vanishing

**Recommendations:**
- Use `torch.nn.utils.clip_grad_norm_` with max_norm=1.0
- Start with n_steps=30, increase if training stagnates
- Monitor gradient norms; if they explode, reduce n_steps or increase k (more damping)

### n_steps as a Hyperparameter

Think of `n_steps` like temperature in simulated annealing:
- **Low n_steps (10–20):** Less chaotic, faster, more like a standard activation
- **Medium n_steps (30–50):** Moderate chaos, good exploration
- **High n_steps (100+):** Maximum chaos, slow, may destabilize training

You can also schedule n_steps during training: start high (exploration), decrease over time (exploitation).

---

## Computational Cost

For a `LeeOscillatorLayer(in_features=64, out_features=32, n_steps=50)`:

- Linear transform: 64×32 = 2048 multiplies (same as `nn.Linear`)
- Oscillator: 32 units × 50 steps × ~10 ops/step = 16,000 ops
- Total: ~18,000 ops vs 2,048 for `nn.Linear + nn.ReLU`

**~9x more expensive per layer** than standard Linear+ReLU. For typical RL policies (2–3 hidden layers, 64–256 units), this is still negligible compared to environment step time. On GPU, the 50-step loop is the main bottleneck (sequential dependency).

**Optimization opportunities:**
- Reduce n_steps for inference (chaos not needed at eval time — use last converged value)
- JIT compile the recurrence loop with `torch.jit.script`
- For very large networks, consider LCTF lookup table approach (pre-compute, interpolate)

---

## Differences from Reference Implementation

| Aspect | Reference (stdlib) | PyTorch |
|--------|-------------------|---------|
| Precision | float64 | float32 (GPU default) |
| Batch | Loop over inputs | Vectorized tensor ops |
| State | Explicit E, I, Ω fields | Tensors within forward() |
| Gradient | N/A | Autograd through unrolled recurrence |
| Parameters | Fixed | Optionally `nn.Parameter` |

Numerical outputs may differ slightly (float32 vs float64) but the dynamics are identical.

---

## Testing

```bash
python test_lee_oscillator.py
```

Tests verify:
1. **Correctness:** PyTorch output matches reference stdlib implementation (within float32 tolerance)
2. **Gradient flow:** Non-zero gradients propagate through the oscillator
3. **Batch consistency:** Same input in different batch positions gives same output
4. **Learnable params:** Optimizer can update oscillator parameters
5. **Bifurcation:** Oscillation amplitude matches expected behavior for default params
