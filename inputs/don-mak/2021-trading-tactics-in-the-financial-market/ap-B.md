# Appendix B: Simple Moving Average

## B.1 Simple Moving Average (SMA)

A simple N-day average is created by adding the prices over N days and dividing by N. It becomes a simple moving average when the next day's weighted price is added to the sum and the weighted first day's price is dropped off (Mak 2003). Thus the unit sample (or impulse) response, $h(k) = 1/N$, where $k = 0, 1, 2, \ldots, N-1$. Day, of course, can be replaced by any time unit. For example, a time unit can be 1 hour.

The frequency response function, $H(\omega)$, can be written as

$$
H(\omega) = \sum_{k=0}^{N-1} h(k) \exp(-ik\omega) \tag{B.1}
$$

Thus, the frequency response function, $H(\omega)$, of an SMA is given by

$$
H(\omega) = \frac{1}{N} \sum_{k=0}^{N-1} \exp[-ik\omega] = \frac{1}{N} \frac{1 - \exp[-iN\omega]}{1 - \exp[-i\omega]} \tag{B.2}
$$

At $\omega = 0$, $H(\omega)$ is indeterminate. However, using the De l'Hopital's Rule (e.g. Kaplan 1959, p. 27), it can be shown that when

$$
\omega \to 0, \quad H(\omega) \to 1
$$

From (B.2), $H(\omega)$ and its magnitude $= 0$, when

$$
\exp[-iN\omega] = \cos(N\omega) - i\sin(N\omega) = 1 \tag{B.3}
$$

i.e., $N\omega = 2m\pi$

And

$$
\omega = 2m\pi / N, \quad \text{where } m = 1, 2, 3, 4, \ldots \tag{B.4}
$$

For N odd,

$$
H(\omega) = \frac{1}{N} \exp\!\left[-i\frac{N-1}{2}\omega\right] \left[1 + 2\cos\omega + \ldots + 2\cos\frac{N-1}{2}\omega\right]
$$

$$
= \frac{1}{N} \exp\!\left[-i\frac{N-1}{2}\omega\right] \left[1 + \sum_{l=1}^{(N-1)/2} 2\cos(l\omega)\right] \tag{B.5}
$$

For N even

$$
H(\omega) = \frac{1}{N} \exp\!\left[-i\frac{N-1}{2}\omega\right] \left[2\cos\frac{\omega}{2} + \ldots + 2\cos\frac{N-1}{2}\omega\right]
$$

$$
= \frac{1}{N} \exp\!\left[-i\frac{N-1}{2}\omega\right] \sum_{l=1}^{N/2} 2\cos\frac{2l-1}{2}\omega \tag{B.6}
$$

Thus, for all N, the unwrapped phase of $H(\omega)$ is given by (Mak 2003)

$$
\phi(\omega) = -\frac{N-1}{2}\omega \tag{B.7}
$$

which is linear with respect to $\omega$.

As mentioned in (B.4), magnitude of $H(\omega) = 0$ when $\omega = 2m\pi/N$, where $m = 1, 2, 3, 4, \ldots$ Thus, using (B.7), at those points

$$
\phi(\omega) = -\frac{N-1}{N} m\pi \tag{B.8}
$$

The larger the number of points, N, the smoother the output response is. However, it will also yield a larger phase lag, according to Eq. (B.7).

The bar lag $b(\omega)$, i.e., the number of bars lagging behind the signal is given by

$$
b(\omega) = \phi(\omega)/\omega = (N - 1)/2 \tag{B.9}
$$

and is independent of $\omega$.

## B.2 SMA(M) -- SMA(N), Fast SMA -- Slow SMA

The difference of two SMA's can form a velocity indicator. From Eqs. (B.5) and (B.6)

$$
H(\omega) = \frac{1}{N} \exp\!\left[-i\frac{N-1}{2}\omega\right] C \tag{B.10}
$$

$$
= \frac{C}{N} \left[\cos\frac{N-1}{2}\omega - i\sin\frac{N-1}{2}\omega\right] \tag{B.11}
$$

where

$$
C = \left[1 + \sum_{l=1}^{\frac{N-1}{2}} 2\cos(l\omega)\right] \quad \text{for } N \text{ odd} \tag{B.12}
$$

$$
= \sum_{l=1}^{N/2} 2\cos\frac{2l-1}{2}\omega \quad \text{for } N \text{ even} \tag{B.13}
$$

The frequency response of the difference between two SMA's is given by

$$
H_M(\omega) - H_N(\omega) = \frac{1}{M}\exp\!\left[-i\frac{M-1}{2}\omega\right] C_M - \frac{1}{N}\exp\!\left[-i\frac{N-1}{2}\omega\right] C_N
$$

$$
= \frac{C_M}{M}\cos\frac{M-1}{2}\omega - \frac{C_N}{N}\cos\frac{N-1}{2}\omega - i\left[\frac{C_M}{M}\sin\frac{M-1}{2}\omega - \frac{C_N}{N}\sin\frac{N-1}{2}\omega\right] \tag{B.14}
$$

At $\omega = 0$, since both $H_M(\omega)$ and $H_N(\omega) = 1$, $H_M(\omega) - H_N(\omega) = 0$.

The phase of $H_M(\omega) - H_N(\omega)$ is given by

$$
\phi(\omega) = \tan^{-1}\!\left(\frac{\frac{C_N}{N}\sin\frac{N-1}{2}\omega - \frac{C_M}{M}\sin\frac{M-1}{2}\omega}{\frac{C_M}{M}\cos\frac{M-1}{2}\omega - \frac{C_N}{N}\cos\frac{N-1}{2}\omega}\right) \tag{B.15}
$$

At $\omega = 0$, both the numerator and denominator of argument of $\tan^{-1}$ are 0. Thus, the phase of $\phi(\omega)$ at $\omega = 0$ is of the indeterminate form. However, using the De l'Hopital's Rule (e.g. Kaplan 1959, p. 27), it can be shown that when

$$
\omega \to 0, \quad \phi(\omega) \to \pi/2
$$

An example of the fast SMA minus the slow SMA is the Awesome Oscillator, where the length of the fast SMA is 5, and that of the slow SMA is 34. Equation (B.15) yields the wrapped phase of $H_M(\omega) - H_N(\omega)$. The unwrapped phase can be different from the wrapped phase. Both the wrapped phase and unwrapped phase of the Awesome Oscillator are shown in Chapter 5.

## B.3 Price -- SMA

When the signal (e.g., price) is used instead of the fast SMA, the signal would be equivalent to an SMA with $M = 1$ of the signal, and therefore $C_M = 1$. Equation (B.14) becomes

$$
1 - H_N(\omega) = 1 - \frac{C_N}{N}\cos\frac{N-1}{2}\omega + i\frac{C_N}{N}\sin\frac{N-1}{2}\omega \tag{B.16}
$$

And Eq. (B.15) becomes

$$
\phi(\omega) = \tan^{-1}\!\left(\frac{\frac{C_N}{N}\sin\frac{N-1}{2}\omega}{1 - \frac{C_N}{N}\cos\frac{N-1}{2}\omega}\right) \tag{B.17}
$$

When $(N-1)\omega/2 = \pi, 2\pi, 3\pi, \ldots$, $\sin[(N-1)\omega/2] = 0$. From Eq. (B.11), the phase of $H_N(\omega) = 0$. From Eq. (B.16), the phase of $1 - H_N(\omega)$, i.e., $\phi(\omega)$ in Eq. (B.17), would thus also equal to 0.

When the amplitude of $H_N(\omega) = 0$, from Eq. (B.11), it would imply that both $\cos((N-1)\omega/2)$ and $\sin((N-1)\omega/2)$ equals 0. From Eq. (B.16), the phase of $1 - H_N(\omega)$, i.e., $\phi(\omega)$ in Eq. (B.17), would thus also equal to 0.
