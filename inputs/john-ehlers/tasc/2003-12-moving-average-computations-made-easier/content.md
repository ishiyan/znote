# Moving Average Computations, Made Easier

- **Author:** John F. Ehlers
- **Publication:** Technical Analysis of STOCKS & COMMODITIES, Volume 21, December 2003, pp. 82–83
- **Article URL:** [Article PDF](https://technical.traders.com/archive/article.asp?file=\V21\C12\270EHLR.pdf)

---

## Simplifying Your Life

*Presenting programming tricks to simplify coding indicators and strategies.*

A simple moving average of length *N* is computed by adding *N* values and dividing the sum by *N*. The process is repeated on a bar-by-bar basis. What could be easier? While conceptually simple, coding for long moving averages can quickly become wearisome because there are so many terms.

This tedium can be reduced by putting the summation in a loop, but looping is difficult to achieve in some applications, such as Excel. Another simplifying approach is to drop off the oldest value and add a new value to the moving average. However, this requires computing the initial value of the long moving average at least once. Here are two ways to compute the simple moving average (SMA) with ease.

In Z-transform notation, a unit delay is represented by $Z^{-1}$. The transfer response is the output of the filter divided by its input. Thus, the transfer response of an eight-bar simple moving average would be written as:

**Equation 1:**

$$H(z) = (1 + Z^{-1} + Z^{-2} + Z^{-3} + Z^{-4} + Z^{-5} + Z^{-6} + Z^{-7})/8$$

This same expression, written in EasyLanguage where a delay of *N* bars is represented in square brackets as [*N*], is written as equation 2:

**Equation 2:**

```
SMA = (Price + Price[1] + Price[2] + Price[3] + Price[3] +
Price[4] + Price[5] + Price[6] + Price[7])/8
```

Equation 1 is a simple finite series that can be written most generally in fractional form as where Y(z) is the filter output and X(z) is the filter input:

**Equation 3:**

$$H(z) = \frac{Y(z)}{X(z)} = \left(\frac{1 - z^{-N}}{1 - z^{-1}}\right) / (N + 1)$$

Equation 3 is identically equivalent to equation 1 if *N*=7, and is therefore a simple moving average. When we carry out the crossmultiplication of equation 3, we obtain:

**Equation 4:**

$$Y(z) = (X(z)(1 - z^{-N}) + Y(z)z^{-1}) / (N + 1)$$

Equation 4 provides the means to program an arbitrarily long SMA using just a few terms. The EasyLanguage equivalent of equation 4 is:

**Equation 5:**

```
SMA = (Price – Price[N] + SMA[1]) / (N+1)
```

Another SMA programming trick can be accomplished by recognizing that we don't have to do the filtering all at once. Rather, we can *cascade* filters. That means we can filter the output of a previous filter that takes the output of a previous filter. Cascading filters is represented by multiplication in Z transforms. The SMA transfer response of cascaded filters can be written as:

**Equation 6:**

$$H(z) = \frac{(1 + z^{-1})(1 + z^{-2})(1 + z^{-4}) \cdots (1 + z^{-2^{K-1}})}{2^K}$$

For example, if K=3, we would have an eight-bar SMA. As a test, we can expand equation 6 to:

**Equation 7:**

$$H(z) = (1 + z^{-1})(1 + z^{-2})(1 + z^{-4}) / 8$$
$$= (1 + z^{-1} + z^{-2} + z^{-3})(1 + z^{-4}) / 8$$
$$= (1 + z^{-1} + z^{-2} + z^{-3} + z^{-4} + z^{-5} + z^{-6} + z^{-7}) / 8$$

Thus, equation 7 shows that the cascaded filters expand to be identical with an SMA. In EasyLanguage, the cascaded filters would be written as:

```easylanguage
Value1 = Price + Price[1]
Value2 = Value1 + Value1[2]
Value3 = Value2 + Value2[4]
SMA = Value3 / 8
```

These programming tricks should simplify the coding of your indicators and strategies.

---

*A pioneer in introducing maximum entropy spectral analysis to technical analysis, John Ehlers is president of MESA Software. Watch for his new book,* Cybernetic Analysis For Stocks And Commodities, *coming in March 2004.*

## Suggested Reading

- Ehlers, John F. [2001]. *Rocket Science For Traders*, John Wiley & Sons.

## BibTeX

```bibtex
@article{ehlers2003movingaverage,
  author    = {Ehlers, John F.},
  title     = {Moving Average Computations, Made Easier},
  journal   = {Technical Analysis of Stocks \& Commodities},
  volume    = {21},
  number    = {12},
  pages     = {82--83},
  year      = {2003},
  month     = dec,
  url       = {https://technical.traders.com/archive/article.asp?file=\V21\C12\270EHLR.pdf}
}
```
