# Correlation as a Trend Indicator

**By John F. Ehlers**

- **Downloaded from:** [Mesa Software — CORRELATION AS A TREND INDICATOR](https://www.mesasoftware.com/papers/CORRELATION%20AS%20A%20TREND%20INDICATOR.pdf)

---

While straightforward, I have not seen a description of using correlation directly as an indicator. Just imagine correlating prices with a straight line having a positive slope. If the price trend is up, the correlation is nearly +1. If the price trend is down, there is anticorrelation and the correlation is nearly -1. If the price trend is sideways, or if prices are oscillating, there is no correlation over the span of the correlation period. These conditions pretty much describe an ideal trend indicator. The indicator output is even limited in its range between -1 and +1, so it can be applied universally to any security symbol.

If the correlation period is shortened to be approximately a half cycle length, then the correlation indicator can also be used to extract the cyclic component. This is because the correlation is positive during the upswing part of the cycle and is negative during the downswing part. However, similar to a moving average, the lag of a correlation indicator is approximately half the correlation length. So, if the correlation length is half of a cycle period, the lag will be at least a quarter of cycle. In the case of band limited signals, this lag can be mitigated by using the rate of change of the correlation as being the real indicator, but there are other cycle indicators that work better.

The correlation trend indicator can be adjusted to accommodate the expected trade holding period. For example, if you want to hold a trade for about a month you could use a 20 bar correlation period. If your expected holding period is on the order of a quarter year you could use a 40 to 60 bar correlation period. Since the lag of the correlation indicator is approximately half the correlation period, a trader could identify the onset of a trend with a shorter correlation period and then extend the correlation period as the trend develops. Correspondingly, a trader could detect the failure of the trend sooner by decreasing the correlation period.

Figure 1 shows the Correlation Trend Indicator with a 20 bar correlation period applied to approximately one year's worth of daily data on SPY. The action of the indicator is self-explanatory. The indicator can be further smoothed by using a 40 bar correlation period as shown in Figure 2. While the indicator is smoother than in Figure 1, the increased lag is apparent. The lag can be reduced to 10 bars or less for the decision regarding the onset or failure of the trend. The shorter correlation period response is shown in Figure 3.

![Figure 1: 20 bar Correlation Period](assets/fig-01.png)
**Figure 1. Trends Are Clearly Identified Using a 20 bar Correlation Period**

![Figure 2: 40 bar Correlation Period](assets/fig-02.png)
**Figure 2. The Correlation Trend Indicator is Smoother Using a 40 bar Correlation Period**

![Figure 3: 10 bar Correlation Period](assets/fig-03.png)
**Figure 3. Trend Onsets and Failures Are More Quickly Identified Using a 10 bar Correlation Period**

The EasyLanguage code for the Correlation Trend Indicator is given in Code Listing 1. The indicator is a Spearman Correlation of closing prices against a straight line with a positive slope. That straight line is created at the variable Y. It has a negative value in the code because the counting in the code goes backwards in time, i.e. from right to left. The rest of the code is almost directly out of a textbook.

### Code Listing 1. EasyLanguage Code for the Correlation Trend Indicator

```easylanguage
{
Correlation Trend Indicator
(c) 2013-2019 John F. Ehlers
}
Inputs:
Length(20);

Vars:
Sx(0),
Sy(0),
Sxx(0),
Sxy(0),
Syy(0),
count(0),
X(0),
Y(0),
Corr(0);

Sx = 0;
Sy = 0;
Sxx = 0;
Sxy = 0;
Syy = 0;
For count = 0 to Length - 1 Begin
    X = Close[count];
    Y = -count;
    Sx = Sx + X;
    Sy = Sy + Y;
    Sxx = Sxx + X*X;
    Sxy = Sxy + X*Y;
    Syy = Syy + Y*Y;
End;
If (Length*Sxx - Sx*Sx > 0) and (Length*Syy - Sy*Sy > 0) Then
    Corr = (Length*Sxy - Sx*Sy) / SquareRoot((Length*Sxx - Sx*Sx)*(Length*Syy - Sy*Sy));

Plot1(Corr);
Plot2(0);
```

---

## BibTeX

```bibtex
@misc{ehlers_correlation_trend_indicator,
  author       = {John F. Ehlers},
  title        = {Correlation as a Trend Indicator},
  year         = {2020},
  howpublished = {online},
  url          = {https://www.mesasoftware.com/papers/CORRELATION%20AS%20A%20TREND%20INDICATOR.pdf}
}
```
