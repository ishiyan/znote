# Identifying Peaks And Valleys In Ranging Markets: The Reversion Index

*The reversion index can provide timely buy and sell signals for reversion-to-the-mean strategies. Find out how to calculate and plot it.*

**by John F. Ehlers**

- Article URL: <https://technical.traders.com/archive/article.asp?file=\V44\C01\066EHLE.pdf>
- Traders' Tips URL: <https://www.traders.com/Documentation/FEEDbk_docs/2026/01/TradersTips.html>

---

The basic idea of the *reversion index* is simple: It is the short-term sum of the bar-to-bar price differences normalized to the sum of the absolute values of those price differences. In an ideal world, the reversion index swings from −1 to +1.

I came up with the idea for this indicator after developing the *continuation index*, which I presented in the September 2025 issue. The continuation index, based on the Laguerre filter, can provide timely indication of trend onset, trend continuation, and trend exhaustion.

Following that research, it occurred to me that if the continuation index is a good indicator of trend and proved useful in trend trading, what about mean-reversion trading? Why not try to create an indicator useful for mean-reversion trading? So I put one together and I will present it here.

## A Representation of Swings in the Data

From a mathematical perspective, the sample-to-sample differences in sampled data is analogous to *differentiation* in calculus. The short-term sum of those differences is analogous to *integration* in calculus. Since the opposite operations of differentiation and integration are employed, the operations cancel each other, and the result is that the reversion index is an accurate representation of price movement.

From a cycles perspective, the summation is maximum during the upswing segment of the cycle period. But the sum is referenced to the right-hand side of the data window, which lags the middle of that window by 90 degrees. The result is the same. The peak of the reversion index occurs at the peak swing in the data. Similarly, the valley of the reversion index occurs at the cycle valley of the data. The ideal length of the data window is half the cycle period of the data so that the summation is conducted over the range from the cycle valley to the cycle peak. For example, you expect a monthly cycle (20 trading days) in the stock indexes, so you would select a summation period of 10 in this case.

Of course, if the summation is conducted over a large number of samples, the index fails to identify the cyclic peaks and valleys. Rather, it can be described as an estimate of the trend over the longer period. That is not the intended use of the reversion index.

## Adding the SuperSmoother Filter

Since a short data window is used, the normalized sum of price differences is very irregular, making identification of the peaks and valleys difficult. For example, using the zero rate of change to sense the peaks and valleys is out of the question. The solution is to further smooth the summation with two SuperSmoother filters having different calculation lengths.

Since the lag of the filters are proportional to their calculation lengths, the two filter plots cross almost exactly at the peaks and valleys in the price data. The suggested lengths of the SuperSmoother filters for this use are 4 bars and 8 bars.

The reversion index using a data window length of 10 is shown in Figure 1 on approximately one year of emini S&P futures data. The SuperSmoother crossings beyond thresholds of, say, +/− 0.3 provide excellent buy and sell short (or sell to exit) trading signals.

![FIGURE 1: REVERSION INDEX. The reversion index is demonstrated here using a data window length of 10 on approximately one year of emini S&P futures data. The reversion index consists of two SuperSmoothers of different calculation lengths that smooth the initial reversion index calculation. Peaks and valleys in the price data are identified by crossings of the two SuperSmoother plot lines. The crossings can provide timely buy and sell short (or sell to exit) trading signals.](assets/figure-01.png)
**FIGURE 1: REVERSION INDEX.** The reversion index is demonstrated here using a data window length of 10 on approximately one year of emini S&P futures data. The reversion index consists of two SuperSmoothers of different calculation lengths that smooth the initial reversion index calculation. Peaks and valleys in the price data are identified by crossings of the two SuperSmoother plot lines. The crossings can provide timely buy and sell short (or sell to exit) trading signals.

EasyLanguage code for the reversion index is given in the sidebar, "Reversion Index, In EasyLanguage Code," and code for the SuperSmoother function is given in the sidebar, "SuperSmoother Function, In EasyLanguage Code."

## In a Nutshell

The reversion index provides timely buy and sell signals for reversion-to-the-mean types of strategies. It is computed as the summation of bar-to-bar price differences normalized to the summation of the absolute amplitudes of those differences. The summation is conducted over approximately half the period of the dominant cycle contained within the data. Identification of the peaks and valleys is accomplished by the crossings of two SuperSmoothers having different calculation lengths.

---

*John Ehlers is a retired electrical engineer and a retired technical analyst, specializing in the application of DSP (digital signal processing) to trading. His latest book is* Cybernetic Trading Indicators (2025), *which presents and updates the market analysis techniques he developed over four decades of trading. For more information, see www.mesasoftware.com.*

## Reversion Index, In EasyLanguage Code

```easylanguage
{
    Reversion Index
    (C) 2025  John F. Ehlers
}

Inputs:
    Length(20);

Vars:
    DeltaSum(0),
    AbsDeltaSum(0),
    count(0),
    Ratio(0),
    Smooth(0),
    Trigger(0);

DeltaSum = 0;
AbsDeltaSum = 0;
For count = 0 to Length - 1 Begin
    DeltaSum = DeltaSum + Close[count] - Close[count + 1];
    AbsDeltaSum = AbsDeltaSum + AbsValue(Close[count] - Close[count + 1]);
End;

If AbsDeltaSum <> 0 Then Ratio = DeltaSum / AbsDeltaSum;
Smooth = $SuperSmoother(Ratio, 8);
Trigger = $SuperSmoother(Ratio, 4);

Plot1(Smooth);
Plot2(0);
Plot3(Trigger);
```

## SuperSmoother Function, In EasyLanguage Code

```easylanguage
{
    $SuperSmoother Function
    (C) 2025  John F. Ehlers
}

Inputs:
    Price(numericseries),
    Period(numericsimple);

Vars:
    a0(0),
    Q(0),
    c1(0),
    c2(0);

Q = expvalue(-1.414*3.14159 / Period);
c1 = 2*Q*Cosine(1.414*180 / Period);
c2 = Q*Q;
a0 = (1 - c1 + c2) / 2;

If CurrentBar >= 4 Then $SuperSmoother = a0*(Price + Price[1]) + c1*$SuperSmoother[1] - c2*$SuperSmoother[2];
If Currentbar < 4 Then $SuperSmoother = Price;
```

## Further Reading

- Ehlers, John [2025]. *Cybernetic Trading Indicators*, Amazon.
- ——— [2004]. *Cybernetic Analysis For Stocks And Futures*, John Wiley & Sons.
- ——— [2013]. *Cycle Analytics For Traders*, John Wiley & Sons.
- ——— [2025]. "The Continuation Index: Trend Onset And Trend Exhaustion," *Technical Analysis of* Stocks & Commodities, Volume 43: September.

---

## BibTeX

```bibtex
@article{ehlers2026reversionIndex,
  author  = {Ehlers, John F.},
  title   = {The Reversion Index},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {2026},
  volume  = {44},
  number  = {1},
  pages   = {16--18},
  url     = {https://technical.traders.com/archive/article.asp?file=\V44\C01\066EHLE.pdf}
}

@misc{traderstips2026jan,
  title        = {Traders' Tips --- January 2026},
  howpublished = {Technical Analysis of Stocks \& Commodities},
  year         = {2026},
  month        = jan,
  url          = {https://www.traders.com/Documentation/FEEDbk_docs/2026/01/TradersTips.html},
  note         = {Implementations of John F. Ehlers' Reversion Index in various platforms}
}
```
