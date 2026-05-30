# Appendix C: Exponential Moving Average, Moving Average Convergence-Divergence

## C.1 Exponential Moving Average, EMA

The frequency response function of the exponential moving average, $H(\omega)$, is given by

$$
H(\omega) = \frac{\alpha}{1 - (1-\alpha)\exp(-i\omega)} \tag{C.1}
$$

where $\alpha = 2/(M + 1)$

M is a positive integer chosen by the trader and is often called the length of EMA. Thus, $\alpha$ has to be equal or less than 1.

The magnitude of $H(\omega)$ is given by Lyons (1997), Mak (2006, p. 15).

$$
|H(\omega)| = \frac{\alpha}{\left[1 - 2(1-\alpha)\cos\omega + (1-\alpha)^2\right]^{1/2}} \tag{C.2}
$$

The phase is given by

$$
\phi(\omega) = -\tan^{-1}\!\left(\frac{(1-\alpha)\sin\omega}{1 - (1-\alpha)\cos\omega}\right) \tag{C.3}
$$

The bar lag, $b(\omega)$, i.e., the number of bars lagging behind the signal is given by

$$
b(\omega) = \phi(\omega)/\omega \tag{C.4}
$$

As $\omega \to 0$, $b(\omega) \to (1/\alpha - 1) = -(M-1)/2$

This is in consistent with

As $\omega \to 0$, $d\phi(\omega)/d\omega \to -(M-1)/2$

When $\omega = \pi$, $\phi(\omega) = 0$, $b(\omega) = 0$

It can be shown that the slope of $b(\omega)$, i.e., $db(\omega)/d\omega$ when $\omega \to 0$ is 0.

This is in consistent with the slope of the slope of $\phi(\omega)$, i.e., $d^2\phi(\omega)/d\omega^2$ is 0 when $\omega \to 0$.

## C.2 Moving Average Convergence-Divergence, MACD

MACD was created by Gerald Appel in the late 1970's. It is the difference between the fast EMA ($M = 12$) and the slow EMA ($N = 26$).

The frequency response of an EMA can be written as

$$
H(\omega) = \frac{\alpha}{1 - (1-\alpha)\exp(-i\omega)} = \frac{\alpha[1 - (1-\alpha)\exp(i\omega)]}{1 - 2(1-\alpha)\cos(\omega) + (1-\alpha)^2} \tag{C.5}
$$

Defining

$$
\beta = 1 - 2(1-\alpha)\cos(\omega) + (1-\alpha)^2 \tag{C.6}
$$

$$
H_M(\omega) = \frac{\alpha_M[1 - (1-\alpha_M)\exp(-i\omega)]}{\beta_M} \tag{C.7}
$$

$$
H_N(\omega) = \frac{\alpha_N[1 - (1-\alpha_N)\exp(-i\omega)]}{\beta_N} \tag{C.8}
$$

where $\alpha_M = 2/(M + 1)$, $\alpha_N = 2/(N + 1)$

The frequency response of the difference of two EMA's can be written as

$$
H_M(\omega) - H_N(\omega) = \frac{\alpha_M \beta_N [1 - (1-\alpha_M)\exp(-i\omega)] - \alpha_N \beta_M [1 - (1-\alpha_N)\exp(-i\omega)]}{\beta_M \beta_N} \tag{C.9}
$$

And the phase

$$
\phi(\omega) = \tan^{-1}\!\left(\frac{[\alpha_N \beta_M (1-\alpha_N) - \alpha_M \beta_N (1-\alpha_M)]\sin\omega}{\alpha_M \beta_N - \alpha_M \beta_N (1-\alpha_M)\cos\omega - \alpha_N \beta_M + \alpha_N \beta_M (1-\alpha_N)\cos\omega}\right) \tag{C.10}
$$

At $\omega = 0$, both the numerator and denominator of argument of $\tan^{-1}$ are 0. Thus, the phase of $\phi(\omega)$ at $\omega = 0$ is of the indeterminate form. However, using the De l'Hopital's Rule (e.g. Kaplan 1959, p. 27), it can be shown that when

$$
\omega \to 0, \quad \phi(\omega) \to \pi/2
$$

## C.3 Price -- EMA

When the signal (e.g., price) is used instead of the fast EMA, the signal would be equivalent to an EMA with $M = 1$ of the signal, and therefore $\alpha_M = 1$, $\beta_M = 1$.

$$
H_M(\omega) - H_N(\omega) = \frac{\beta_N - \alpha_N[1 - (1-\alpha_N)\exp(-i\omega)]}{\beta_N} \tag{C.11}
$$

And

$$
\phi(\omega) = \tan^{-1}\!\left(\frac{[\alpha_N(1-\alpha_N)\sin\omega]}{\beta_N - \alpha_N + \alpha_N(1-\alpha_N)\cos\omega}\right) \tag{C.12}
$$

## C.4 Comparison of SMA with EMA

In an N period SMA, the weights are equally distributed in the last N bars. To emphasize the influences from the recent data, the M period exponential moving average (EMA) is defined as

$$
y(n) = \alpha x(n) + (1-\alpha)y(n-1)
$$

$$
= \alpha \sum_{k=0}^{\infty} (1-\alpha)^k x(n-k) \tag{C.13}
$$

$$
= \frac{2}{M+1} \sum_{k=0}^{\infty} \left(\frac{M-1}{M+1}\right)^k x(n-k)
$$

where $\alpha = 2/(M + 1)$

Note that, for the EMA, infinite number of data points can be used for $M > 1$. Equation (C.13) is exactly the same as Eq. (4.3) in Chapter 4, but written in a slightly different form.

It can be shown that at $\omega = 0$, if $N = M$, the bar lag of the SMA and EMA is the same and is equal to $(M - 1)/2$. However, while the bar lag remains the same for all $\omega$ for SMA, the bar lag slowly decreases to 0 when $\omega$ approaches $\pi$ for the EMA. Thus, EMA has a definite advantage over SMA.
