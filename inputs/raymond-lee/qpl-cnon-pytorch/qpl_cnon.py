"""
QPL-CNON: Quantum Price Level Chaotic Neural Oscillatory Network
=================================================================

A supervised financial forecasting model that predicts next-bar OHLC prices
using QPL levels as quantum field signals and Lee-Oscillator activations.

Architecture: 41 → 41 → 4 (all Lee-Oscillator layers)
Input: 5-day OHLC (20) + 21 QPL NQPR multipliers (21) = 41 features
Output: Next-day Open, High, Low, Close (normalized)

References:
    Lee, R. S. T. (2021). IAJER, 4(02), 1-21. §4-5.
    Lee, R. S. T. (2019). Quantum Finance. Springer. Ch.11.

Requires: torch, and the lee_oscillator.py + quantum-price-levels.py modules.
"""

import sys
import os
import math
from typing import List, Tuple, Optional

# ---------------------------------------------------------------------------
# Import sibling modules (adjust path as needed)
# ---------------------------------------------------------------------------
_base = os.path.dirname(os.path.abspath(__file__))
_lee_path = os.path.join(os.path.dirname(_base), 'lee-oscillator-pytorch')
_qpl_path = os.path.join(os.path.dirname(_base), 'prepared-for-conversion', 'quantum-price-levels')

if _lee_path not in sys.path:
    sys.path.insert(0, _lee_path)
if _qpl_path not in sys.path:
    sys.path.insert(0, _qpl_path)

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

# Import QPL (pure stdlib — always works)
_qpl_mod = __import__('quantum-price-levels')
QuantumPriceLevels = _qpl_mod.QuantumPriceLevels

# Import Lee-Oscillator PyTorch module (only if torch available)
if HAS_TORCH:
    from lee_oscillator import LeeOscillatorLayer


# ===========================================================================
# Model
# ===========================================================================

if HAS_TORCH:
    class QPLCNON(nn.Module):
        """
        QPL-CNON forecasting model.

        Parameters
        ----------
        n_steps : int, default 50
            Lee-Oscillator iterations per forward pass.
        hidden_size : int, default 41
            Hidden layer size (Lee uses 41 to match input size).
        learnable_oscillator : bool, default False
            If True, oscillator parameters (e1, e2, ...) are trainable.
        e1, e2, i1, i2, k : float
            Lee-Oscillator parameters for all layers.
        """

        def __init__(self, n_steps=50, hidden_size=41,
                     learnable_oscillator=False,
                     e1=20.0, e2=5.0, i1=1.0, i2=5.0, k=5.0):
            super().__init__()
            self.input_layer = LeeOscillatorLayer(
                41, hidden_size, n_steps=n_steps,
                learnable_oscillator=learnable_oscillator,
                e1=e1, e2=e2, i1=i1, i2=i2, k=k,
            )
            self.hidden_layer = LeeOscillatorLayer(
                hidden_size, 4, n_steps=n_steps,
                learnable_oscillator=learnable_oscillator,
                e1=e1, e2=e2, i1=i1, i2=i2, k=k,
            )

        def forward(self, x: 'torch.Tensor') -> 'torch.Tensor':
            """
            Parameters
            ----------
            x : Tensor of shape (batch_size, 41)
                Normalized input features.

            Returns
            -------
            Tensor of shape (batch_size, 4)
                Predicted next-bar [Open, High, Low, Close] (normalized).
            """
            h = self.input_layer(x)
            return self.hidden_layer(h)

        def predict(self, bars: List[Tuple[float, float, float, float]],
                    qpl_lookback: int = 2048) -> Tuple[float, float, float, float]:
            """
            Convenience method: predict next bar from raw OHLC history.

            Parameters
            ----------
            bars : list of (open, high, low, close)
                At least qpl_lookback + 5 bars, oldest first.
            qpl_lookback : int
                QPL lookback window.

            Returns
            -------
            tuple of (open, high, low, close) — predicted next bar (raw prices).
            """
            self.eval()
            features, norm_min, norm_max = prepare_features(bars, qpl_lookback)
            with torch.no_grad():
                x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
                y_norm = self(x).squeeze(0).numpy()

            # Denormalize
            price_range = norm_max - norm_min
            if price_range == 0:
                price_range = 1.0
            result = tuple(float(y_norm[i]) * price_range + norm_min for i in range(4))
            return result


# ===========================================================================
# Data preparation
# ===========================================================================

def compute_qpl_levels(prices: List[float], lookback: int = 2048,
                       num_levels: int = 21) -> Optional[List[float]]:
    """
    Compute QPL NQPR multipliers from a price series using streaming class.

    Parameters
    ----------
    prices : list of float
        Price series (at least lookback+1 values).
    lookback : int
        QPL lookback window.
    num_levels : int
        Number of quantum levels.

    Returns
    -------
    list of float (length num_levels) or None if not enough data.
    """
    qpl = QuantumPriceLevels(lookback=lookback, num_levels=num_levels)
    result = None
    for p in prices:
        r = qpl.update(p)
        if r is not None:
            result = r
    if result is None:
        return None
    return result['nqpr']


def prepare_features(bars: List[Tuple[float, float, float, float]],
                     qpl_lookback: int = 2048) -> Tuple[List[float], float, float]:
    """
    Prepare the 41-element input feature vector from raw OHLC bars.

    Parameters
    ----------
    bars : list of (open, high, low, close)
        At least qpl_lookback + 5 bars, oldest first.
    qpl_lookback : int
        QPL lookback window.

    Returns
    -------
    tuple of (features, norm_min, norm_max)
        features: 41-element normalized [0, 1] list
        norm_min, norm_max: normalization bounds (for denormalization)
    """
    n = len(bars)
    if n < qpl_lookback + 5:
        raise ValueError(f"Need at least {qpl_lookback + 5} bars, got {n}")

    # Extract close prices for QPL
    closes = [bar[3] for bar in bars]

    # Compute QPL NQPR multipliers
    nqpr = compute_qpl_levels(closes[-qpl_lookback - 1:], lookback=qpl_lookback)
    if nqpr is None:
        raise ValueError("QPL computation failed")

    # 5-day OHLC (most recent 5 bars including today)
    ohlc_5day = []
    for i in range(5):
        bar = bars[-(5 - i)]
        ohlc_5day.extend([bar[0], bar[1], bar[2], bar[3]])

    # Raw feature vector (41 elements)
    raw_features = ohlc_5day + nqpr  # 20 + 21 = 41

    # Min-max normalization
    # For OHLC features, use the price range over the 5-day window
    all_prices = ohlc_5day  # 20 price values
    norm_min = min(all_prices)
    norm_max = max(all_prices)
    price_range = norm_max - norm_min
    if price_range == 0:
        price_range = 1.0

    # Normalize OHLC to [0, 1]
    features = [(v - norm_min) / price_range for v in ohlc_5day]

    # Normalize NQPR: they're in range [1.0, ~1.1], normalize to [0, 1]
    nqpr_min = min(nqpr)
    nqpr_max = max(nqpr)
    nqpr_range = nqpr_max - nqpr_min
    if nqpr_range == 0:
        nqpr_range = 1.0
    features.extend([(v - nqpr_min) / nqpr_range for v in nqpr])

    return features, norm_min, norm_max


# ===========================================================================
# Dataset
# ===========================================================================

if HAS_TORCH:
    class QPLCNONDataset(Dataset):
        """
        Dataset for QPL-CNON training.

        Converts raw OHLC bars into (input, target) pairs where:
        - input: 41-element normalized feature vector
        - target: 4-element normalized next-bar OHLC

        Parameters
        ----------
        bars : list of (open, high, low, close)
            Full price history, oldest first. Needs qpl_lookback + 5 + n_samples.
        qpl_lookback : int, default 2048
            QPL computation window.
        """

        def __init__(self, bars: List[Tuple[float, float, float, float]],
                     qpl_lookback: int = 2048):
            self.bars = bars
            self.qpl_lookback = qpl_lookback

            # Pre-compute QPL for all valid positions
            # A sample at index i uses bars[0:i+qpl_lookback+5] for input
            # and bars[i+qpl_lookback+5] as target
            min_bars_needed = qpl_lookback + 5 + 1  # +1 for target
            if len(bars) < min_bars_needed:
                raise ValueError(
                    f"Need at least {min_bars_needed} bars, got {len(bars)}")

            self.samples = []
            self._build_samples()

        def _build_samples(self):
            """Pre-compute all (input, target) pairs."""
            bars = self.bars
            qpl_lookback = self.qpl_lookback
            closes = [bar[3] for bar in bars]

            # Run QPL streaming over the full series
            qpl = QuantumPriceLevels(lookback=qpl_lookback, num_levels=21)
            qpl_results = []
            for i, p in enumerate(closes):
                r = qpl.update(p)
                qpl_results.append(r)

            # Build samples: for each position where we have QPL + 5 days history + next day
            # QPL first produces output at index qpl_lookback (0-based)
            # We need 5 days before the "current" day, so earliest current day = 4
            # And we need a next day as target, so current day < len(bars) - 1

            first_qpl_idx = qpl_lookback  # First index where QPL is available
            first_valid = max(first_qpl_idx, 4)  # Need 5 days of history (indices i-4..i)

            for i in range(first_valid, len(bars) - 1):
                if qpl_results[i] is None:
                    continue

                nqpr = qpl_results[i]['nqpr']

                # 5-day OHLC: bars[i-4], bars[i-3], bars[i-2], bars[i-1], bars[i]
                ohlc_5day = []
                for j in range(i - 4, i + 1):
                    ohlc_5day.extend([bars[j][0], bars[j][1], bars[j][2], bars[j][3]])

                # Normalization (per-sample, using 5-day price range)
                norm_min = min(ohlc_5day)
                norm_max = max(ohlc_5day)
                price_range = norm_max - norm_min
                if price_range == 0:
                    price_range = 1.0

                # Input features
                features = [(v - norm_min) / price_range for v in ohlc_5day]

                # NQPR normalization
                nqpr_min = min(nqpr)
                nqpr_max = max(nqpr)
                nqpr_range = nqpr_max - nqpr_min
                if nqpr_range == 0:
                    nqpr_range = 1.0
                features.extend([(v - nqpr_min) / nqpr_range for v in nqpr])

                # Target: next-day OHLC normalized with same price range
                target_bar = bars[i + 1]
                target = [(target_bar[j] - norm_min) / price_range for j in range(4)]

                self.samples.append((features, target, norm_min, norm_max))

        def __len__(self):
            return len(self.samples)

        def __getitem__(self, idx):
            features, target, _, _ = self.samples[idx]
            return (torch.tensor(features, dtype=torch.float32),
                    torch.tensor(target, dtype=torch.float32))


# ===========================================================================
# Training loop
# ===========================================================================

if HAS_TORCH:
    def train(model: 'QPLCNON', dataset: 'QPLCNONDataset',
              epochs: int = 200, lr: float = 1e-3, batch_size: int = 32,
              val_split: float = 0.1, patience: int = 20,
              verbose: bool = True) -> dict:
        """
        Train the QPL-CNON model.

        Parameters
        ----------
        model : QPLCNON
        dataset : QPLCNONDataset
        epochs : int
        lr : float
        batch_size : int
        val_split : float
            Fraction of data for validation (taken from the end, time-ordered).
        patience : int
            Early stopping patience (epochs without improvement).
        verbose : bool
            Print progress.

        Returns
        -------
        dict with 'train_losses', 'val_losses', 'best_epoch'.
        """
        # Time-ordered train/val split
        n = len(dataset)
        n_val = max(1, int(n * val_split))
        n_train = n - n_val

        train_indices = list(range(n_train))
        val_indices = list(range(n_train, n))

        train_subset = torch.utils.data.Subset(dataset, train_indices)
        val_subset = torch.utils.data.Subset(dataset, val_indices)

        train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False)

        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        criterion = nn.MSELoss()

        train_losses = []
        val_losses = []
        best_val_loss = float('inf')
        best_epoch = 0
        best_state = None

        for epoch in range(epochs):
            # Train
            model.train()
            epoch_loss = 0.0
            n_batches = 0
            for x, y in train_loader:
                optimizer.zero_grad()
                pred = model(x)
                loss = criterion(pred, y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                epoch_loss += loss.item()
                n_batches += 1

            avg_train_loss = epoch_loss / max(n_batches, 1)
            train_losses.append(avg_train_loss)

            # Validate
            model.eval()
            val_loss = 0.0
            n_val_batches = 0
            with torch.no_grad():
                for x, y in val_loader:
                    pred = model(x)
                    loss = criterion(pred, y)
                    val_loss += loss.item()
                    n_val_batches += 1

            avg_val_loss = val_loss / max(n_val_batches, 1)
            val_losses.append(avg_val_loss)

            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                best_epoch = epoch
                best_state = {k: v.clone() for k, v in model.state_dict().items()}

            if verbose and (epoch % 10 == 0 or epoch == epochs - 1):
                print(f"  Epoch {epoch:4d}: train_loss={avg_train_loss:.6f}, "
                      f"val_loss={avg_val_loss:.6f}")

            # Early stopping
            if epoch - best_epoch >= patience:
                if verbose:
                    print(f"  Early stopping at epoch {epoch} "
                          f"(best was epoch {best_epoch})")
                break

        # Restore best model
        if best_state is not None:
            model.load_state_dict(best_state)

        return {
            'train_losses': train_losses,
            'val_losses': val_losses,
            'best_epoch': best_epoch,
        }


# ===========================================================================
# Demo / main
# ===========================================================================

if __name__ == '__main__':
    import random

    # Generate synthetic OHLC data (random walk)
    random.seed(42)
    n_bars = 2200  # 2048 for QPL + ~150 training samples
    price = 100.0
    bars = []
    for _ in range(n_bars):
        open_ = price
        change = random.gauss(0.0, 0.01)
        close = open_ * (1 + change)
        high = max(open_, close) * (1 + abs(random.gauss(0, 0.003)))
        low = min(open_, close) * (1 - abs(random.gauss(0, 0.003)))
        bars.append((open_, high, low, close))
        price = close

    print(f"Generated {len(bars)} synthetic OHLC bars")
    print(f"Price range: {min(b[3] for b in bars):.2f} - {max(b[3] for b in bars):.2f}")
    print()

    if not HAS_TORCH:
        print("PyTorch not installed. Testing data pipeline only.")
        print()

        # Test QPL computation
        closes = [b[3] for b in bars]
        nqpr = compute_qpl_levels(closes, lookback=2048)
        if nqpr:
            print(f"QPL NQPR (21 levels): [{nqpr[0]:.8f} .. {nqpr[20]:.8f}]")
        else:
            print("QPL failed!")

        # Test feature preparation
        features, norm_min, norm_max = prepare_features(bars, qpl_lookback=2048)
        print(f"Feature vector: {len(features)} elements")
        print(f"  OHLC features [0:5]: {features[0:5]}")
        print(f"  QPL features [20:25]: {features[20:25]}")
        print(f"  Norm range: [{norm_min:.4f}, {norm_max:.4f}]")
    else:
        print("=== QPL-CNON Training Demo ===")
        print()

        # Build dataset
        print("Building dataset...")
        dataset = QPLCNONDataset(bars, qpl_lookback=2048)
        print(f"  {len(dataset)} training samples from {len(bars)} bars")
        print()

        # Check shapes
        x, y = dataset[0]
        print(f"  Input shape: {x.shape}")  # (41,)
        print(f"  Target shape: {y.shape}")  # (4,)
        print()

        # Create model
        model = QPLCNON(n_steps=30)  # n_steps=30 for faster demo
        print(f"Model:\n{model}")
        n_params = sum(p.numel() for p in model.parameters())
        print(f"  Total parameters: {n_params}")
        print()

        # Quick training (few epochs for demo)
        print("Training (20 epochs)...")
        result = train(model, dataset, epochs=20, lr=1e-3, batch_size=16,
                       patience=50, verbose=True)
        print(f"\n  Best epoch: {result['best_epoch']}")
        print(f"  Final val loss: {result['val_losses'][-1]:.6f}")
        print()

        # Predict
        pred = model.predict(bars)
        actual = bars[-1]
        print(f"  Last bar (actual):    O={actual[0]:.4f} H={actual[1]:.4f} "
              f"L={actual[2]:.4f} C={actual[3]:.4f}")
        print(f"  Next bar (predicted): O={pred[0]:.4f} H={pred[1]:.4f} "
              f"L={pred[2]:.4f} C={pred[3]:.4f}")
