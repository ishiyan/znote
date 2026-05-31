# Polynomial Forecast

## Summary

One-step-ahead price forecast using Taylor series expansion based on polynomial fit derivatives. Predicts where price will be on the next bar by extrapolating the current velocity (and optionally acceleration) estimated from a local polynomial fit.

## Source

- Don K. Mak, *The Science of Financial Market Trading* (2003), Chapter 10.2
- F1V = forecast using velocity only (first-order Taylor)
- F1VA = forecast using velocity + acceleration (second-order Taylor)

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| degree | int | 3 | 2–6 | Polynomial degree for the local fit (uses degree+1 bars) |
| order | int | 1 | 1–2 | Taylor expansion order: 1 = velocity only (F1V), 2 = velocity + acceleration (F1VA) |
| smoothing | int | 0 | 0+ | EMA pre-smoothing period applied to price before fitting. 0 = no smoothing. |

## Formula

```
velocity     = PFD(price, degree, derivative_order=1, smoothing)
acceleration = PFD(price, degree, derivative_order=2, smoothing)

order=1:  forecast = price[i] + velocity
order=2:  forecast = price[i] + velocity + 0.5 * acceleration
```

Where PFD computes the k-th derivative of a degree-d polynomial fit to the most recent d+1 (optionally EMA-smoothed) prices.

## Output

| Field | Type | Description |
|-------|------|-------------|
| value | float | 1-bar-ahead price forecast. NaN during priming period. |

## Priming

- Without smoothing: first `degree` bars are NaN (need degree+1 points for the fit)
- With smoothing: additional bars needed for EMA to stabilize (conventionally: degree + smoothing bars are NaN)

## Trading Use

- **Trend confirmation:** When forecast > price, uptrend is expected; forecast < price signals downtrend.
- **Entry timing:** Enter when forecast crosses above/below price (equivalent to velocity zero-crossing but expressed as a price level).
- **Stop/target placement:** The forecast value provides a natural 1-bar price target.
- **Order=2 advantage:** Including acceleration captures curvature — the forecast anticipates deceleration near turning points, pulling the forecast back toward price sooner than order=1.

## Implementation Notes

- Self-contained: embeds PFD coefficient computation (Lagrange basis derivative evaluation).
- Uses only standard library math (no numpy/pandas) for easy porting.
- Coefficients are computed once per parameter set and cached.

## Naming

- Folder: `polynomial-forecast`
- Go package: `polynomialforecast`
- Test data arrays: `EXPECTED_D{degree}_O{order}_S{smoothing}`
