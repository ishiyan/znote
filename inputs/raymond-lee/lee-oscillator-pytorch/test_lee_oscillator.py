"""
Tests for Lee-Oscillator PyTorch module.

Run: python test_lee_oscillator.py
Requires: torch
"""

import sys
import math

try:
    import torch
except ImportError:
    print("SKIP: PyTorch not installed")
    sys.exit(0)

from lee_oscillator import LeeOscillatorCell, LeeOscillatorLayer

passed = 0
failed = 0


def check(name, condition):
    global passed, failed
    if condition:
        passed += 1
    else:
        print(f"FAIL: {name}")
        failed += 1


# ==========================================================================
# Test 1: Output matches reference implementation
# ==========================================================================

# Reference values computed with the stdlib implementation:
# e1=20, e2=5, i1=1, i2=5, k=5, xi_e=0, xi_i=0, n_steps=100
# S=0.0 -> L oscillates between ~0.901 and ~1.380 (period-2)
# The PyTorch version should match one of these (depends on even/odd n_steps)

cell = LeeOscillatorCell(e1=20.0, e2=5.0, i1=1.0, i2=5.0, k=5.0,
                         xi_e=0.0, xi_i=0.0, n_steps=100)

with torch.no_grad():
    out = cell(torch.tensor([0.0])).item()

# Should be one of the period-2 values
check("reference_match_s0",
      abs(out - 1.3803) < 0.01 or abs(out - 0.9010) < 0.01)

# S=1.0 should be near 0.737 (nearly converged, small oscillation)
with torch.no_grad():
    out = cell(torch.tensor([1.0])).item()
check("reference_match_s1", abs(out - 0.737) < 0.02)

# S=-1.0 should be near 0.273
with torch.no_grad():
    out = cell(torch.tensor([-1.0])).item()
check("reference_match_s_neg1", abs(out - 0.273) < 0.02)

# ==========================================================================
# Test 2: Gradient flow
# ==========================================================================

s = torch.tensor([0.0, 0.5, -0.5], requires_grad=True)
out = cell(s)
loss = out.sum()
loss.backward()

check("gradient_exists", s.grad is not None)
check("gradient_nonzero", s.grad.abs().sum().item() > 1e-6)

# ==========================================================================
# Test 3: Batch consistency
# ==========================================================================

with torch.no_grad():
    batch = torch.tensor([0.3, 0.3, 0.3, 0.3])
    outputs = cell(batch)
    # All should be identical
    check("batch_consistent", (outputs - outputs[0]).abs().max().item() < 1e-6)

# ==========================================================================
# Test 4: Learnable parameters update
# ==========================================================================

cell_learn = LeeOscillatorCell(n_steps=20, learnable=True)
optimizer = torch.optim.SGD(cell_learn.parameters(), lr=0.01)

s = torch.tensor([0.5])
target = torch.tensor([0.0])

initial_e1 = cell_learn.e1.item()
for _ in range(10):
    optimizer.zero_grad()
    out = cell_learn(s)
    loss = (out - target).pow(2).sum()
    loss.backward()
    optimizer.step()

check("learnable_params_updated", abs(cell_learn.e1.item() - initial_e1) > 1e-6)

# ==========================================================================
# Test 5: Layer forward shape
# ==========================================================================

layer = LeeOscillatorLayer(in_features=8, out_features=4, n_steps=20)
x = torch.randn(16, 8)  # batch of 16, 8 features
with torch.no_grad():
    y = layer(x)
check("layer_output_shape", y.shape == (16, 4))

# ==========================================================================
# Test 6: Layer gradient flow
# ==========================================================================

layer = LeeOscillatorLayer(in_features=4, out_features=2, n_steps=20)
x = torch.randn(8, 4, requires_grad=True)
y = layer(x)
loss = y.sum()
loss.backward()
check("layer_gradient_to_input", x.grad is not None and x.grad.abs().sum().item() > 0)

# Check gradients flow to linear weights
linear_grad = layer.linear.weight.grad
check("layer_gradient_to_weights", linear_grad is not None and linear_grad.abs().sum().item() > 0)

# ==========================================================================
# Test 7: Learnable oscillator in layer
# ==========================================================================

layer = LeeOscillatorLayer(4, 2, n_steps=20, learnable_oscillator=True)
x = torch.randn(8, 4)
y = layer(x)
loss = y.sum()
loss.backward()
osc_grad = layer.oscillator.e1.grad
check("layer_learnable_oscillator_grad",
      osc_grad is not None and osc_grad.abs().item() > 0)

# ==========================================================================
# Test 8: Different n_steps produce different outputs (chaos sensitivity)
# ==========================================================================

cell_short = LeeOscillatorCell(n_steps=49)
cell_long = LeeOscillatorCell(n_steps=50)

with torch.no_grad():
    s = torch.tensor([0.0])
    out_short = cell_short(s).item()
    out_long = cell_long(s).item()

# With period-2 oscillation, odd vs even n_steps should give different values
check("n_steps_sensitivity", abs(out_short - out_long) > 0.1)

# ==========================================================================
# Summary
# ==========================================================================

print(f"\n{'='*50}")
print(f"Lee-Oscillator PyTorch tests: {passed} passed, {failed} failed")
print(f"{'='*50}")
sys.exit(0 if failed == 0 else 1)
