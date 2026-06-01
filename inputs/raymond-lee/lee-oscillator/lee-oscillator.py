"""
Lee-Oscillator
==============

A discrete-time chaotic neural oscillator for use as an activation function
in neural networks. Replaces sigmoid/ReLU with a 4-neuron recurrent unit
that exhibits transient chaos.

Reference:
    Lee, R. S. T. (2004). "A transient-chaotic autoassociative network (TCAN)
    based on Lee oscillators." IEEE Transactions on Neural Networks, 15(5).

Dependencies: Python standard library only (math module).
"""

import math


# =============================================================================
# Sigmoid
# =============================================================================

def sigmoid(x):
    """Standard sigmoid: 1 / (1 + exp(-x))."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    else:
        # Numerically stable for negative x
        ex = math.exp(x)
        return ex / (1.0 + ex)


# =============================================================================
# Lee-Oscillator Cell (single unit)
# =============================================================================

class LeeOscillatorCell:
    """
    A single Lee-Oscillator unit.

    4-neuron recurrent system: Excitatory (E), Inhibitory (I), Input (Ω),
    and Output (L). Given an external stimulus S, iterates the recurrence
    for N timesteps and produces output L(t).

    Parameters
    ----------
    e1 : float, default 20.0
        Excitatory self-weight. Controls self-excitation strength.
    e2 : float, default 5.0
        Inhibitory-to-excitatory cross-weight.
    i1 : float, default 1.0
        Excitatory-to-inhibitory cross-weight.
    i2 : float, default 5.0
        Inhibitory self-weight. Controls self-inhibition strength.
    k : float, default 5.0
        Decay constant for the output damping envelope.
        Higher k = faster suppression of oscillation at large |S|.
    xi_e : float, default 0.0
        Excitatory neuron threshold.
    xi_i : float, default 0.0
        Inhibitory neuron threshold.
    n_steps : int, default 50
        Number of recurrence iterations per activation.

    Notes
    -----
    Default parameters produce the characteristic Lee-Oscillator bifurcation:
    - Sigmoid-like behavior for large |S| (oscillation amplitude < 0.01)
    - Period-2 chaotic oscillation near S=0 (amplitude ~0.48)
    - Smooth transition between zones (controlled by k)

    The condition for oscillation is e1*i2 - e2*i1 > 16 (at the symmetric
    fixed point). Defaults give 20*5 - 5*1 = 95 >> 16.
    The exp(-k*S^2) damping envelope suppresses visible oscillation at the
    edges, creating the sigmoid zones.
    """

    def __init__(self, e1=20.0, e2=5.0, i1=1.0, i2=5.0, k=5.0,
                 xi_e=0.0, xi_i=0.0, n_steps=50):
        self.e1 = e1
        self.e2 = e2
        self.i1 = i1
        self.i2 = i2
        self.k = k
        self.xi_e = xi_e
        self.xi_i = xi_i
        self.n_steps = n_steps

        # Internal state
        self.E = 0.5
        self.I = 0.5
        self.omega = 0.5
        self.L = 0.0

    def reset(self, e=0.5, i=0.5):
        """Reset internal state."""
        self.E = e
        self.I = i
        self.omega = 0.5
        self.L = 0.0

    def step(self, s):
        """
        Advance one timestep given input stimulus s.

        Parameters
        ----------
        s : float
            External input stimulus.

        Returns
        -------
        float
            Output L(t) after this timestep.
        """
        e_new = sigmoid(self.e1 * self.E - self.e2 * self.I + s - self.xi_e)
        i_new = sigmoid(self.i1 * self.E - self.i2 * self.I - self.xi_i)
        omega_new = sigmoid(s)

        self.L = (self.E - self.I) * math.exp(-self.k * s * s) + self.omega
        self.E = e_new
        self.I = i_new
        self.omega = omega_new

        return self.L

    def run(self, s, n_steps=None):
        """
        Run the oscillator for n_steps with fixed input s.
        Returns the final output L(t).

        Parameters
        ----------
        s : float
            External input stimulus (held constant).
        n_steps : int or None
            Number of timesteps. If None, uses self.n_steps.

        Returns
        -------
        float
            Final output after n_steps iterations.
        """
        if n_steps is None:
            n_steps = self.n_steps
        for _ in range(n_steps):
            self.step(s)
        return self.L

    def run_trajectory(self, s, n_steps=None):
        """
        Run the oscillator and return the full trajectory of L(t).

        Parameters
        ----------
        s : float
            External input stimulus (held constant).
        n_steps : int or None
            Number of timesteps.

        Returns
        -------
        list of float
            L(t) for t = 0, 1, ..., n_steps-1.
        """
        if n_steps is None:
            n_steps = self.n_steps
        trajectory = []
        for _ in range(n_steps):
            self.step(s)
            trajectory.append(self.L)
        return trajectory


# =============================================================================
# LORS Cell (Lee-Oscillator with Retrograde Signaling)
# =============================================================================

class LORSCell:
    """
    Lee-Oscillator with Retrograde Signaling (LORS).

    Extended version that feeds output back into E and I neurons.
    Produces richer bifurcation patterns (8 categories).

    Parameters
    ----------
    a1, a2, a3, a4 : float
        Weights for excitatory neuron (retrograde, self, inhibitory, input).
    b1, b2, b3, b4 : float
        Weights for inhibitory neuron (retrograde, excitatory, self, input).
    k : float
        Decay constant.
    xi_e, xi_i : float
        Thresholds.
    n_steps : int
        Iterations per activation.
    """

    # Pre-defined parameter sets for the 8 LORS categories
    PRESETS = {
        0: dict(a1=0.0, a2=5.0, a3=5.0, a4=1.0,
                b1=0.0, b2=-1.0, b3=1.0, b4=0.0,
                k=1.0, xi_e=0.0, xi_i=0.0),
        1: dict(a1=-0.5, a2=0.55, a3=0.55, a4=0.5,
                b1=-0.5, b2=-0.55, b3=-0.55, b4=0.5,
                k=1.0, xi_e=0.0, xi_i=0.0),
        2: dict(a1=-0.5, a2=0.55, a3=0.55, a4=0.5,
                b1=0.5, b2=-0.55, b3=-0.55, b4=-0.5,
                k=1.0, xi_e=0.0, xi_i=0.0),
        3: dict(a1=0.5, a2=0.55, a3=0.55, a4=0.5,
                b1=0.5, b2=-0.55, b3=-0.55, b4=-0.5,
                k=1.0, xi_e=0.0, xi_i=0.0),
        4: dict(a1=0.9, a2=0.9, a3=0.9, a4=0.9,
                b1=-0.9, b2=-0.9, b3=-0.9, b4=-0.9,
                k=1.0, xi_e=0.0, xi_i=0.0),
        5: dict(a1=0.9, a2=0.9, a3=0.9, a4=0.9,
                b1=-0.9, b2=-0.9, b3=-0.9, b4=-0.9,
                k=1.0, xi_e=0.0, xi_i=0.0),
        6: dict(a1=5.0, a2=5.0, a3=5.0, a4=5.0,
                b1=-1.0, b2=-1.0, b3=-1.0, b4=-1.0,
                k=1.0, xi_e=0.0, xi_i=0.0),
        7: dict(a1=5.0, a2=5.0, a3=5.0, a4=5.0,
                b1=-1.0, b2=-1.0, b3=-1.0, b4=-1.0,
                k=1.0, xi_e=0.0, xi_i=0.0),
    }

    def __init__(self, a1=0.0, a2=5.0, a3=5.0, a4=1.0,
                 b1=0.0, b2=-1.0, b3=1.0, b4=0.0,
                 k=1.0, xi_e=0.0, xi_i=0.0, n_steps=50):
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.b1 = b1
        self.b2 = b2
        self.b3 = b3
        self.b4 = b4
        self.k = k
        self.xi_e = xi_e
        self.xi_i = xi_i
        self.n_steps = n_steps

        # Internal state
        self.E = 0.5
        self.I = 0.5
        self.omega = 0.5
        self.L = 0.0

    @classmethod
    def from_preset(cls, category, n_steps=50):
        """
        Create a LORS cell from one of the 8 predefined categories (0–7).

        Parameters
        ----------
        category : int
            LORS category number (0 = original Lee-oscillator, 1–7 = retrograde variants).
        n_steps : int
            Iterations per activation.
        """
        if category not in cls.PRESETS:
            raise ValueError(f"Unknown LORS category: {category}. Must be 0–7.")
        params = cls.PRESETS[category]
        return cls(**params, n_steps=n_steps)

    def reset(self, e=0.5, i=0.5):
        """Reset internal state."""
        self.E = e
        self.I = i
        self.omega = 0.5
        self.L = 0.0

    def step(self, s):
        """
        Advance one timestep given input stimulus s.

        Returns
        -------
        float
            Output LORS(t) after this timestep.
        """
        # Compute output first (uses current state)
        self.L = (self.E - self.I) * math.exp(-self.k * s * s) + self.omega

        # Update neurons (uses retrograde signal = current L)
        e_new = sigmoid(self.a1 * self.L + self.a2 * self.E
                        - self.a3 * self.I + self.a4 * s - self.xi_e)
        i_new = sigmoid(self.b1 * self.L - self.b2 * self.E
                        - self.b3 * self.I + self.b4 * s - self.xi_i)
        omega_new = sigmoid(s)

        self.E = e_new
        self.I = i_new
        self.omega = omega_new

        return self.L

    def run(self, s, n_steps=None):
        """Run for n_steps with fixed input s. Returns final output."""
        if n_steps is None:
            n_steps = self.n_steps
        for _ in range(n_steps):
            self.step(s)
        return self.L

    def run_trajectory(self, s, n_steps=None):
        """Run and return full trajectory of outputs."""
        if n_steps is None:
            n_steps = self.n_steps
        trajectory = []
        for _ in range(n_steps):
            self.step(s)
            trajectory.append(self.L)
        return trajectory


# =============================================================================
# Batch computation (functional API)
# =============================================================================

def compute_lee_oscillator(inputs, n_steps=50, e1=20.0, e2=5.0, i1=1.0, i2=5.0,
                           k=5.0, xi_e=0.0, xi_i=0.0):
    """
    Compute Lee-Oscillator activation for a list of inputs (batch mode).

    Each input is treated independently: oscillator state resets between inputs.

    Parameters
    ----------
    inputs : list of float
        Input stimulus values.
    n_steps : int
        Timesteps per input.
    e1, e2, i1, i2, k, xi_e, xi_i : float
        Oscillator parameters.

    Returns
    -------
    list of float
        Output L(t) for each input after n_steps iterations.
    """
    cell = LeeOscillatorCell(e1=e1, e2=e2, i1=i1, i2=i2, k=k,
                             xi_e=xi_e, xi_i=xi_i, n_steps=n_steps)
    outputs = []
    for s in inputs:
        cell.reset()
        outputs.append(cell.run(s))
    return outputs


def compute_bifurcation(s_min=-1.0, s_max=1.0, s_steps=1000,
                        n_total=600, n_discard=500,
                        e1=20.0, e2=5.0, i1=1.0, i2=5.0,
                        k=5.0, xi_e=0.0, xi_i=0.0):
    """
    Compute bifurcation diagram data for the Lee-Oscillator.

    For each input value S, runs the oscillator n_total steps, discards
    the first n_discard (transient), and records the remaining outputs.

    Parameters
    ----------
    s_min, s_max : float
        Range of input stimulus to sweep.
    s_steps : int
        Number of input values to sample.
    n_total : int
        Total timesteps per input.
    n_discard : int
        Timesteps to discard (transient period).
    e1, e2, i1, i2, k, xi_e, xi_i : float
        Oscillator parameters.

    Returns
    -------
    list of tuple (s, outputs)
        For each S value, a tuple of (s_value, list_of_steady_state_L_values).
    """
    cell = LeeOscillatorCell(e1=e1, e2=e2, i1=i1, i2=i2, k=k,
                             xi_e=xi_e, xi_i=xi_i)
    n_record = n_total - n_discard
    ds = (s_max - s_min) / s_steps

    diagram = []
    for step in range(s_steps + 1):
        s = s_min + step * ds
        cell.reset()
        # Discard transient
        for _ in range(n_discard):
            cell.step(s)
        # Record steady state
        outputs = []
        for _ in range(n_record):
            cell.step(s)
            outputs.append(cell.L)
        diagram.append((s, outputs))

    return diagram


def compute_lctf(s_min=-1.0, s_max=1.0, s_steps=1000,
                 n_total=600, t_start=500, t_end=600,
                 e1=20.0, e2=5.0, i1=1.0, i2=5.0,
                 k=5.0, xi_e=0.0, xi_i=0.0):
    """
    Compute the Lee Chaotic Transfer Function (LCTF) table.

    Returns a 2D array: LCTF[i][t] = output at timestep t for input i.

    Parameters
    ----------
    s_min, s_max : float
        Input range.
    s_steps : int
        Number of input values (rows in table).
    n_total : int
        Total timesteps to run.
    t_start, t_end : int
        Range of timesteps to record (columns in table).
    e1, e2, i1, i2, k, xi_e, xi_i : float
        Oscillator parameters.

    Returns
    -------
    tuple (s_values, lctf_table)
        s_values: list of float (length s_steps+1)
        lctf_table: list of list of float (s_steps+1 × (t_end-t_start))
    """
    cell = LeeOscillatorCell(e1=e1, e2=e2, i1=i1, i2=i2, k=k,
                             xi_e=xi_e, xi_i=xi_i)
    ds = (s_max - s_min) / s_steps
    n_record = t_end - t_start

    s_values = []
    lctf_table = []

    for step in range(s_steps + 1):
        s = s_min + step * ds
        s_values.append(s)
        cell.reset()
        # Run to t_start
        for _ in range(t_start):
            cell.step(s)
        # Record t_start to t_end
        row = []
        for _ in range(n_record):
            cell.step(s)
            row.append(cell.L)
        lctf_table.append(row)

    return s_values, lctf_table


# =============================================================================
# Example / demo
# =============================================================================

if __name__ == '__main__':
    print("=== Lee-Oscillator Bifurcation Demo ===")
    print()
    print("Default params: e1=20, e2=5, i1=1, i2=5, k=5")
    print("Condition for oscillation: e1*i2 - e2*i1 = 95 >> 16")
    print()

    cell = LeeOscillatorCell()  # uses new defaults

    test_inputs = [-1.0, -0.7, -0.5, -0.3, -0.1, 0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

    print(f"{'S':>6} | {'Unique L values (last 100 of 600 steps)':}")
    print("-" * 80)

    for s in test_inputs:
        cell.reset()
        trajectory = cell.run_trajectory(s, n_steps=600)
        last100 = trajectory[-100:]
        unique = sorted(set(round(v, 4) for v in last100))
        n_states = len(unique)
        amp = unique[-1] - unique[0] if n_states > 1 else 0.0

        if n_states == 1:
            print(f"{s:>6.2f} | converged: {unique[0]:.4f}")
        elif n_states == 2:
            print(f"{s:>6.2f} | period-2: [{unique[0]:.4f}, {unique[1]:.4f}] amp={amp:.4f}")
        else:
            print(f"{s:>6.2f} | chaotic ({n_states} states): [{unique[0]:.4f}..{unique[-1]:.4f}] amp={amp:.4f}")

    print()
    print("=== Batch Activation (using final L after 100 steps) ===")
    inputs = [i * 0.1 for i in range(-10, 11)]
    outputs = compute_lee_oscillator(inputs, n_steps=100)
    for s, out in zip(inputs, outputs):
        print(f"  S={s:>5.2f} → L={out:>7.4f}")

    print()
    print("=== LORS Presets (S=0.0, t=200) ===")
    for cat in range(8):
        lors = LORSCell.from_preset(cat, n_steps=200)
        lors.reset()
        trajectory = lors.run_trajectory(0.0, n_steps=600)
        last100 = trajectory[-100:]
        unique = sorted(set(round(v, 4) for v in last100))
        n_states = len(unique)
        if n_states == 1:
            print(f"  LORS#{cat}: converged to {unique[0]:.6f}")
        else:
            print(f"  LORS#{cat}: {n_states} states [{unique[0]:.4f}..{unique[-1]:.4f}]")
