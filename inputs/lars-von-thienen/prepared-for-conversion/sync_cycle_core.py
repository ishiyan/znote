"""Refresh standalone copies after intentionally editing the shared core.

Run from any directory. Then run both numerical suites and regenerate affected
reference fixtures before verifying. Does not change the original 13 masters.
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
FOLDERS = (
    'complete-cycle-scanner', 'dominant-market-vibration',
    'dynamic-cycle-explorer', 'cycle-phase-score', 'phasing-oscillator',
    'annual-cycle-pattern-decoder', 'harmonic-energy-superposition-wave',
)

if __name__ == '__main__':
    for name in FOLDERS:
        shutil.copyfile(ROOT/'cycle_core.py', ROOT/name/'cycle_core.py')
    print('Updated seven standalone numerical core copies.')
