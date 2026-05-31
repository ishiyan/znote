"""
Test streaming QuantumPriceLevels class against generated test data.

Tests:
1. Streaming output at last bar matches batch output (full-window lookback)
2. Streaming with shorter lookback matches dedicated streaming expected arrays
3. Priming behavior: returns None for first lookback prices

Run: python test_streaming.py
"""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(__file__))
qpl_mod = __import__('quantum-price-levels')
QuantumPriceLevels = qpl_mod.QuantumPriceLevels
compute_qpl = qpl_mod.compute_qpl

from test_testdata import (
    INPUT_CLOSE, INPUT_PRICES_2048,
    EXPECTED_NQPR, EXPECTED_UPPER, EXPECTED_LOWER,
    EXPECTED_NQPR_2K, EXPECTED_UPPER_2K, EXPECTED_LOWER_2K,
    EXPECTED_NQPR_S100, EXPECTED_UPPER_S100, EXPECTED_LOWER_S100,
    EXPECTED_NQPR_S150_B50, EXPECTED_UPPER_S150_B50, EXPECTED_LOWER_S150_B50,
    EXPECTED_NQPR_S200_F0_42, EXPECTED_UPPER_S200_F0_42, EXPECTED_LOWER_S200_F0_42,
)

TOLERANCE = 1e-12
passed = 0
failed = 0


def assert_arrays_equal(name, actual, expected, tol=TOLERANCE):
    global passed, failed
    if len(actual) != len(expected):
        print(f"FAIL {name}: length mismatch {len(actual)} vs {len(expected)}")
        failed += 1
        return
    max_diff = 0.0
    for i in range(len(actual)):
        diff = abs(actual[i] - expected[i])
        if diff > max_diff:
            max_diff = diff
    if max_diff > tol:
        print(f"FAIL {name}: max_diff={max_diff:.3e} > tol={tol:.3e}")
        failed += 1
    else:
        passed += 1


# =========================================================================
# Test 1: Streaming with full-window lookback matches batch (252-bar input)
# =========================================================================

qpl = QuantumPriceLevels(lookback=251, num_levels=21, num_bins=100, scale_factor=0.21)
result = None
for p in INPUT_CLOSE:
    r = qpl.update(p)
    if r is not None:
        result = r

assert result is not None, "Streaming produced no output for 252-bar input"
assert_arrays_equal("batch_match_nqpr", result['nqpr'], EXPECTED_NQPR)
assert_arrays_equal("batch_match_upper", result['qpl_upper'], EXPECTED_UPPER)
assert_arrays_equal("batch_match_lower", result['qpl_lower'], EXPECTED_LOWER)

# =========================================================================
# Test 2: Streaming with full-window lookback matches batch (2048-bar input)
# =========================================================================

qpl = QuantumPriceLevels(lookback=2047, num_levels=21, num_bins=100, scale_factor=0.21)
result = None
for p in INPUT_PRICES_2048:
    r = qpl.update(p)
    if r is not None:
        result = r

assert result is not None, "Streaming produced no output for 2048-bar input"
assert_arrays_equal("batch_match_2k_nqpr", result['nqpr'], EXPECTED_NQPR_2K, tol=1e-9)
assert_arrays_equal("batch_match_2k_upper", result['qpl_upper'], EXPECTED_UPPER_2K, tol=1e-7)
assert_arrays_equal("batch_match_2k_lower", result['qpl_lower'], EXPECTED_LOWER_2K, tol=1e-7)

# =========================================================================
# Test 3: Streaming with lookback=100
# =========================================================================

qpl = QuantumPriceLevels(lookback=100, num_levels=21, num_bins=100, scale_factor=0.21)
result = None
for p in INPUT_CLOSE:
    r = qpl.update(p)
    if r is not None:
        result = r

assert result is not None
assert_arrays_equal("s100_nqpr", result['nqpr'], EXPECTED_NQPR_S100)
assert_arrays_equal("s100_upper", result['qpl_upper'], EXPECTED_UPPER_S100)
assert_arrays_equal("s100_lower", result['qpl_lower'], EXPECTED_LOWER_S100)

# =========================================================================
# Test 4: Streaming with lookback=150, num_bins=50
# =========================================================================

qpl = QuantumPriceLevels(lookback=150, num_levels=21, num_bins=50, scale_factor=0.21)
result = None
for p in INPUT_CLOSE:
    r = qpl.update(p)
    if r is not None:
        result = r

assert result is not None
assert_arrays_equal("s150_b50_nqpr", result['nqpr'], EXPECTED_NQPR_S150_B50)
assert_arrays_equal("s150_b50_upper", result['qpl_upper'], EXPECTED_UPPER_S150_B50)
assert_arrays_equal("s150_b50_lower", result['qpl_lower'], EXPECTED_LOWER_S150_B50)

# =========================================================================
# Test 5: Streaming with lookback=200, scale_factor=0.42
# =========================================================================

qpl = QuantumPriceLevels(lookback=200, num_levels=21, num_bins=100, scale_factor=0.42)
result = None
for p in INPUT_CLOSE:
    r = qpl.update(p)
    if r is not None:
        result = r

assert result is not None
assert_arrays_equal("s200_f042_nqpr", result['nqpr'], EXPECTED_NQPR_S200_F0_42)
assert_arrays_equal("s200_f042_upper", result['qpl_upper'], EXPECTED_UPPER_S200_F0_42)
assert_arrays_equal("s200_f042_lower", result['qpl_lower'], EXPECTED_LOWER_S200_F0_42)

# =========================================================================
# Test 6: Priming behavior — returns None for first lookback prices
# =========================================================================

qpl = QuantumPriceLevels(lookback=100, num_levels=21, num_bins=100, scale_factor=0.21)
none_count = 0
first_output_idx = None
for i, p in enumerate(INPUT_CLOSE):
    r = qpl.update(p)
    if r is None:
        none_count += 1
    elif first_output_idx is None:
        first_output_idx = i

# lookback=100 means we need 100 returns = 101 prices
# First output at index 100 (0-based, the 101st price)
priming_ok = (first_output_idx == 100)
if priming_ok:
    passed += 1
else:
    print(f"FAIL priming: first output at index {first_output_idx}, expected 100")
    failed += 1

# =========================================================================
# Summary
# =========================================================================

print(f"\n{'='*50}")
print(f"Streaming tests: {passed} passed, {failed} failed")
print(f"{'='*50}")
sys.exit(0 if failed == 0 else 1)
