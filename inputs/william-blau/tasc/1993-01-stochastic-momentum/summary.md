# Summary

William Blau's "Stochastic Momentum" (TASC, January 1993) introduces the Stochastic Momentum Index (SMI), a bipolar reformulation of the double-smoothed stochastic. Instead of referencing the close to the low of the range (as in Lane's %K), the SMI references the close to the midpoint of the range, producing a momentum oscillator that swings between -100 and +100.

## Key Concepts

- **Stochastic Momentum**: SM(q) = Close - 0.5(HH:q + LL:q) — displacement of close from range midpoint
- **SMI Formula**: SMI(q,r,s) = 100 * Es(Er(SM(q))) / (0.5 * Es(Er(HH:q - LL:q)))
- **Double smoothing** via EMA parameters r and s provides low-lag, noise-reduced curves
- **Two-day stochastics** (q=2): sensitive to close position relative to two-bar extremes; good proxy for price with large smoothing
- **One-day stochastics** (q=1): sentiment/trend identification indicator based on close position within the daily bar

## Trading Applications

- Signal line crossovers (SMI above/below its EMA) for entry/exit
- Divergences between SMI and price signal trend reversals
- Combine slow stochastic (entry timing) with SMI (trend definition)
- Increasing the smoothing parameter reveals longer-term trends while maintaining timeliness
