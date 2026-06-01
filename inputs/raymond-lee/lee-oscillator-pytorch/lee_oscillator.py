"""
Lee-Oscillator PyTorch Module
==============================

Drop-in replacement for standard activation functions (ReLU, Sigmoid, Tanh)
using a discrete-time chaotic neural oscillator.

Provides:
- LeeOscillatorCell: Single oscillator unit
- LeeOscillatorLayer: Full layer (Linear + Lee-Oscillator activation)

Reference:
    Lee, R. S. T. (2004). IEEE Transactions on Neural Networks, 15(5).

Requires: PyTorch >= 1.8
"""

import torch
import torch.nn as nn
import math


class LeeOscillatorCell(nn.Module):
    """
    Single Lee-Oscillator unit as a PyTorch module.

    Takes input tensor S and runs the 4-neuron recurrence for n_steps,
    returning the final output L(t). Operates element-wise on input tensors.

    Parameters
    ----------
    e1, e2, i1, i2 : float
        Dynamics weights (excitatory/inhibitory coupling).
    k : float
        Output damping decay constant.
    xi_e, xi_i : float
        Neuron thresholds.
    n_steps : int
        Number of recurrence iterations per forward pass.
    learnable : bool
        If True, oscillator parameters become trainable nn.Parameters.
    """

    def __init__(self, e1=20.0, e2=5.0, i1=1.0, i2=5.0, k=5.0,
                 xi_e=0.0, xi_i=0.0, n_steps=50, learnable=False):
        super().__init__()
        self.n_steps = n_steps

        if learnable:
            self.e1 = nn.Parameter(torch.tensor(e1))
            self.e2 = nn.Parameter(torch.tensor(e2))
            self.i1 = nn.Parameter(torch.tensor(i1))
            self.i2 = nn.Parameter(torch.tensor(i2))
            self.k = nn.Parameter(torch.tensor(k))
            self.xi_e = nn.Parameter(torch.tensor(xi_e))
            self.xi_i = nn.Parameter(torch.tensor(xi_i))
        else:
            self.register_buffer('e1', torch.tensor(e1))
            self.register_buffer('e2', torch.tensor(e2))
            self.register_buffer('i1', torch.tensor(i1))
            self.register_buffer('i2', torch.tensor(i2))
            self.register_buffer('k', torch.tensor(k))
            self.register_buffer('xi_e', torch.tensor(xi_e))
            self.register_buffer('xi_i', torch.tensor(xi_i))

    def forward(self, s: torch.Tensor) -> torch.Tensor:
        """
        Run Lee-Oscillator recurrence on input.

        Parameters
        ----------
        s : Tensor
            Input stimulus, any shape. Each element is processed independently.

        Returns
        -------
        Tensor
            Output L(t) after n_steps, same shape as input.
        """
        # Initialize internal state (same shape as input)
        E = torch.full_like(s, 0.5)
        I = torch.full_like(s, 0.5)
        omega = torch.sigmoid(s)

        for _ in range(self.n_steps):
            # Output (computed from current state)
            L = (E - I) * torch.exp(-self.k * s * s) + omega

            # Update neurons
            E_new = torch.sigmoid(self.e1 * E - self.e2 * I + s - self.xi_e)
            I_new = torch.sigmoid(self.i1 * E - self.i2 * I - self.xi_i)

            E = E_new
            I = I_new
            # omega is constant (depends only on s, which is fixed)

        # Final output
        L = (E - I) * torch.exp(-self.k * s * s) + omega
        return L

    def extra_repr(self) -> str:
        return (f'e1={self.e1.item():.1f}, e2={self.e2.item():.1f}, '
                f'i1={self.i1.item():.1f}, i2={self.i2.item():.1f}, '
                f'k={self.k.item():.1f}, n_steps={self.n_steps}')


class LeeOscillatorLayer(nn.Module):
    """
    Full Lee-Oscillator layer: Linear transform + Lee-Oscillator activation.

    Replaces nn.Sequential(nn.Linear(in, out), nn.ReLU()) with a single module
    that uses Lee-Oscillator dynamics as the activation function.

    Parameters
    ----------
    in_features : int
        Input dimension.
    out_features : int
        Output dimension (number of oscillator units).
    n_steps : int
        Recurrence iterations per forward pass.
    learnable_oscillator : bool
        If True, oscillator params (e1, e2, ...) are trainable.
    bias : bool
        If True, the linear transform includes a bias term.
    e1, e2, i1, i2, k, xi_e, xi_i : float
        Oscillator parameters (shared across all units in layer).
    """

    def __init__(self, in_features: int, out_features: int, n_steps: int = 50,
                 learnable_oscillator: bool = False, bias: bool = True,
                 e1=20.0, e2=5.0, i1=1.0, i2=5.0, k=5.0,
                 xi_e=0.0, xi_i=0.0):
        super().__init__()
        self.linear = nn.Linear(in_features, out_features, bias=bias)
        self.oscillator = LeeOscillatorCell(
            e1=e1, e2=e2, i1=i1, i2=i2, k=k,
            xi_e=xi_e, xi_i=xi_i,
            n_steps=n_steps, learnable=learnable_oscillator,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        x : Tensor of shape (batch_size, in_features)

        Returns
        -------
        Tensor of shape (batch_size, out_features)
        """
        s = self.linear(x)
        return self.oscillator(s)

    def extra_repr(self) -> str:
        return f'in={self.linear.in_features}, out={self.linear.out_features}'
