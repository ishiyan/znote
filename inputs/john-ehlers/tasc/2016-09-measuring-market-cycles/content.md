# Measuring Market Cycles

- **Author:** John Ehlers
- **Publication:** Technical Analysis of STOCKS & COMMODITIES, Volume 34, September 2016, pp. 11--16
- **Article URL:** [Article PDF](https://technical.traders.com/archive/article.asp?file=\V34\C09\280EHLE.pdf)
- **Traders' Tips URL:** [Traders' Tips, September 2016](https://www.traders.com/Documentation/FEEDbk_docs/2016/09/TradersTips.html)

---

If you haven't given much thought to why certain parameters are used in indicators, you may be interested to know that it has a lot to do with measured cycle periods. Here's how you can use these measured periods and apply them to your indicators.

Why does the relative strength index (RSI) use 14 bars in its calculation? That was the question I asked when I first used technical analysis. The best answer my broker could give me was "because Welles Wilder says so." You have no idea how dissatisfying that answer is to an engineer! So I began my quest for a better explanation. I discovered that the correct answer to this question is about measuring the cycle periods that are obvious in the data, and then tuning indicators to the measured cycle periods. In this article, I will show you measured cycles in the equity indexes that occurred in 2015 and give some tips on how to use these measurements in your indicators. I'll also give some advice on how to measure the cycle periods yourself.

## It's No Easy Feat

Even the most casual inspection of price charts makes it clear that there are cycles in the data. The problem is they are frustratingly difficult to measure because they are ephemeral. That is, the cycles come and go, and their periods are constantly changing. And to make things more complicated, market data is noisy, and a low signal-to-noise ratio can cause cycle measurements to be wildly inaccurate. In addition, the market data is fractal. You can look at a chart of daily data and then look at a chart of weekly data, and the charts basically look the same if the scales are removed. In other words, the amplitude of the cyclic swings scales in direct proportion to the cycle period. I call this effect *spectral dilation* because longer cycle periods have larger swings.

Short-term measurement techniques such as the phase accumulator, dual differentiator, or homodyne attempt to measure the bar-to-bar phase shift and then infer the cycle period from these measurements because there are 360 degrees in one complete cycle period. So if the phase shift is 20 degrees between two bars, then the cycle period must be $360/20 = 18$ bars. All such techniques fail because the market data is so noisy.

Averaging over a longer data length increases the signal-to-noise ratio. Thus, a longer sampling of data is required to make a valid cycle period measurement. Some digital signal processing (DSP) techniques, such as the Pisarenko harmonic decomposition or Goertzel algorithms, simply don't converge to a good solution because the market cycle period lengths are always changing. Fast Fourier and discrete Fourier transforms average the data and provide a measured result but because the data length used must be relatively short, the resolution is poor. Wavelets are another way to use a small amount of data to obtain a valid measurement, but their resolution is also poor.

The real kicker is that none of the listed techniques or their cousins account for the effects of spectral dilation (that is, fractal nature) of market data, and therefore these techniques give answers that are skewed toward the longer cycle periods. I know of only two DSP techniques that consider all of the constraints and provide reasonable results. These are the autocorrelation periodogram and MESA.

## Autocorrelation Periodogram

Just as the name implies, the autocorrelation periodogram is computed by first taking the autocorrelation of the market data and then taking a Fourier transform of the autocorrelation results. For the moment, consider the market data as a pure cycle. If the data is compared to itself a full cycle period back, the result would be a perfect correlation. If the data is compared to itself a half cycle period back, the result would be a perfect anticorrelation. Thus, the autocorrelation swings between the limits of $-1$ and $+1$, regardless of the length of the cycle period. This limited swing strips away all of the spectral dilation in the original market data while retaining its periodicity. Then, taking the Fourier transform of the autocorrelation function gives a true measure of the relative amplitude of all the cycle periods present in the data without bias. The EasyLanguage code to compute the autocorrelation periodogram and to display the spectral results is given in the sidebar "EasyLanguage Code For The Autocorrelation Periodogram" and is also available at http://traders.com/files/Ehlers1609.html.

## And Now MESA

MESA is an acronym for maximum entropy spectral analysis and is a technique I developed more than 30 years ago. It is no longer a product I offer; rather, it is embedded into indicators I now use to make them adaptive to current market conditions.

MESA works by selecting a short segment of data and tuning a filter to it so the filter is an accurate replica of the data within the constraints of the size of the filter. The technique is called maximum entropy because the tuning method basically squeezes out all the cyclic information it can from that data sample with the residual having maximum noise, or entropy. Then the filter is examined offline to test its cyclic response. This technique enables the use of very short segments of data so that the cycle information is relatively stable within that sample. Thus, each measurement maximally responds to only that data sample and rejects all data outside that sample. Further, the cyclic measurement has a high resolution because the display is made independently from the data length.

## The Past Can Be Useful

The measured market cycles for SPY in 2015 are shown in Figure 1, where I used the autocorrelation periodogram for the measurement. The spectral display is shown below the bar chart. The horizontal scale of the spectral display is exactly the same as the scale for the bar chart. The vertical scale is the length of the cyclic components in the spectrum. The color on the display indicates the amplitude of the spectrum components as a continuum at every location of time and cycle period. The color ranges from white hot (yellow) at the maximum amplitude, through red hot, to ice cold (black) over a 20-decibel range. The autocorrelation periodogram uses a 48-bar block of data for each day on the chart because the vertical scale has a maximum of a 48-bar cycle period and it is necessary to use at least one full cycle period of the longest cycle for the measurement. If the scale were limited to 24 bars, for example, the length of the data used could be halved.

![Figure 1: Measured market cycles for SPY in 2015. Here you see the dominant cycle periods and periods where there were no useful cycles. The color ranges from white hot (yellow) at the maximum amplitude, through red hot, to ice cold (black) over a 20-decibel range.](assets/figure-01.png)
**Figure 1: Measured market cycles for SPY in 2015.** Here you see the dominant cycle periods and periods where there were no useful cycles. The color ranges from white hot (yellow) at the maximum amplitude, through red hot, to ice cold (black) over a 20-decibel range.

With reference to Figure 1, the year starts with a dominant cycle period of about 22 bars, decreasing to about 18 bars by the end of January. The cycle period drops to be about 10 bars during February when the prices had the short trend up. In March through May, the cyclic components were all over the place. The smearing, or fuzziness, of the spectral display means there just was no useful cycle during that timeframe. The dominant cycle period early in June was about 24 bars, declining to about 18 bars in mid-August when the price drop occurred. The sharp drop basically destroyed any hope of a rational cycle measurement for a while, and the autocorrelation periodogram responded by displaying a dominant 10-bar cycle for about two months. Then, starting in mid-October, the measured dominant cycle period ranged between 18 and 22 bars for the remainder of the year.

The picture of spectral activity can be enhanced by using MESA with the same conditions---using 48 bars of data to make the measurements. The result is shown in Figure 2, where each spectral line is shown with higher resolution because the width of the yellow area is much thinner. Without going into details, there is an approximate 20-bar (monthly) cycle period present most of the time, with longer cycles also present in the April and September timeframes. I glean from this, as well as from many other measurements, that there is a relatively consistent monthly cycle present in the equity index futures and exchange traded funds (ETFs). I do not ascribe causality to market cycles, but this certainly makes sense from a fundamental perspective. That is, from the middle managers on up, everyone has to make their numbers by the month in corporate America. Other contracts, such as bonds, gold, and oil futures have different spectral signatures, and, since they are more complex, traders can explore these using the autocorrelation periodogram code in the sidebar.

![Figure 2: Enhancing the spectral chart. Using MESA with the same conditions (48 bars of data), each spectral line is shown with higher resolution than in Figure 1 because the width of the yellow area is much thinner. There is an approximate 20-bar (monthly) cycle period present most of the time.](assets/figure-02.png)
**Figure 2: Enhancing the spectral chart.** Using MESA with the same conditions (48 bars of data), each spectral line is shown with higher resolution than in Figure 1 because the width of the yellow area is much thinner. There is an approximate 20-bar (monthly) cycle period present most of the time.

## Indicator Tuning

Just knowing the cycle period in market data is not very helpful by itself. On the other hand, most indicators are sensitive to the length of data used in their calculation. Therefore, the value of knowing the dominant cycle period is the ability to adapt the data length of an indicator to the measurement of the cycle.

A stochastic indicator basically plots the current price relative to the lowest price over the computation period. In the case of a pure sine wave, the maximum response extends from the cycle valley to the cycle peak, a period of a half cycle. If too short a time is used, the indicator saturates and is stuck at the top extreme or the bottom extreme over an extended time. If too long a time is used, the stochastic is sluggish and does not respond well to shorter-term movements. Therefore, if the dominant cycle period is known, the best data length to use in calculating a stochastic is half the dominant cycle period.

An RSI is computed by basically taking the difference of the sum of increasing price deltas less the sum of decreasing price deltas over the length of the data sample. In the case of a pure sinewave, all of the price deltas from the valley of the waveform to its peak are increasing and there are no decreasing price deltas. Similarly, in the next half alternation, there are no increasing price deltas and all the price deltas are decreasing. Therefore, the best data length to use in the computation of the RSI is half the measured dominant cycle.

If you use a data length that is too long, the RSI just averages the price deltas up and price deltas down, and is basically nonresponsive near the middle of the chart.

The commodity channel index (CCI) measures the variation of the prices from the mean over the period of the cycle. Clearly, the full length of the measured dominant cycle period is the correct length to be used in this indicator.

While synthesizing output waveforms from the multiple major measured cycles is theoretically possible, I do not find the process to be practical. There are a triple infinity of parameters describing cycles (period, phase, and amplitude). Of them, only the period is known with reasonable accuracy through spectral analysis, and adjusting the other two parameters for several different cycle periods is, at best, impractical. However, it is relatively simple to recover the phase of the dominant cycle by correlation after its period has been measured. Just knowing the period of the dominant cycle is often "good enough" for trading purposes.

## Tips On Using Indicators

Traders don't necessarily have to know or measure the dominant cycle period to improve the usefulness of their indicators. As Yogi Berra famously said, "You can see a lot just by looking." Here are a few useful rules of thumb to know when your indicators are working properly.

1. If the indicator gets stuck at the top or bottom of its range, then you know the data length used in calculating the indicator is too short.

2. If the indicator is lethargic and does not swing fully between the lower limit and the upper limit, then you know the data length used in calculating the indicator is too long.

3. Using a shorter data length causes the indicator to have more of a leading function relative to the market cycle. Conversely, using a longer data length causes the indicator to have more of a lagging function relative to the market cycle. Therefore, an effective composite indicator can be created using the same indicator twice: one with the optimum computation length and the other with a computation length of about 60% of the optimum length. The line crossings can be a clear indication of effective buy and sell points.

4. Oscillator-type indicators are used to find the trade entry and exit points for swing trading or reversion-to-the-mean strategy algorithms. Conventional wisdom has the trader waiting for confirmation of the turn before making the trade. I have shown that the most effective swing trading technique is to anticipate the cyclic turning point.

5. Market cycles are ephemeral. Don't count on them being there all the time. In particular, when the market is in a trend, your cycles-based indicator will typically suggest entering a countertrend position. It is prudent to not get run over by that train.

6. Major moves in the market, such as what occurred in August 2015, virtually destroy useful trading cycles in the data. In this case, the only action a trader can take is to wait until that major move falls outside the computation window of his indicator.

## Cycles Can Be Measured

There are many techniques to measure market cycles that have been adapted from the sciences. Most perform poorly because they fall apart in the low signal-to-noise environments, either because they require too much stationary data, or because they cannot converge to a useful solution in the presence of the ephemeral cycles. Further, only the autocorrelation periodogram has the capacity to handle the spectral dilation of the market cycles due to the fractal nature of the data. I have provided the autocorrelation periodogram code with this article so you can measure the spectrum of your preferred trading instrument.

While measuring the dominant cycle is useful for maximizing the performance of indicators and filters, you can improve the performance of your indicators just by being observant regarding the indicator performance itself and noting if the data length being used is too short or too long. If so, you don't have to stick to a fixed-length solution.

---

*S&C Contributing Editor John Ehlers is a pioneer in the use of cycles and DSP technical analysis. He is president of MESA Software. MESASoftware.com offers the MESA Phasor and MESA intraday futures strategies.*

---

## EasyLanguage Code For The Autocorrelation Periodogram

```easylanguage
Inputs:
  EnhanceResolution(False);

Vars:
  AvgLength(3),
  M(0),
  N(0),
  X(0),
  Y(0),
  alpha1(0),
  HP(0),
  a1(0),
  b1(0),
  c1(0),
  c2(0),
  c3(0),
  Filt(0),
  Lag(0),
  count(0),
  Sx(0),
  Sy(0),
  Sxx(0),
  Syy(0),
  Sxy(0),
  Period(0),
  Sp(0),
  Spx(0),
  MaxPwr(0),
  PeakPwr(0),
  DominantCycle(0),
  Color1(0),
  Color2(0),
  Color3(0);

Arrays:
  Corr[70](0),
  CosinePart[70](0),
  SinePart[70](0),
  SqSum[70](0),
  R[70, 2](0),
  Pwr[70](0);

// Highpass Filter and SuperSmoother Filter together form a Roofing Filter

// Highpass Filter
alpha1 = (1 - Sine(360 / 48)) / Cosine(360 / 48);
HP = .5*(1 + alpha1)*(Close - Close[1]) + alpha1*HP[1];

// Smooth with a SuperSmoother Filter
a1 = expvalue(-1.414*3.14159 / 8);
b1 = 2*a1*Cosine(1.414*180 / 8);
c2 = b1;
c3 = -a1*a1;
c1 = 1 - c2 - c3;
Filt = c1*(HP + HP[1]) / 2 + c2*Filt[1] + c3*Filt[2];

// Pearson correlation for each value of lag
For Lag = 0 to 48 Begin
  // Set the averaging length as M
  M = AvgLength;
  If AvgLength = 0 Then M = Lag;
  Sx = 0;
  Sy = 0;
  Sxx = 0;
  Syy = 0;
  Sxy = 0;
  For count = 0 to M - 1 Begin
    X = Filt[count];
    Y = Filt[Lag + count];
    Sx = Sx + X;
    Sy = Sy + Y;
    Sxx = Sxx + X*X;
    Sxy = Sxy + X*Y;
    Syy = Syy + Y*Y;
  End;
  If (M*Sxx - Sx*Sx)*(M*Syy - Sy*Sy) > 0 Then
    Corr[Lag] = (M*Sxy - Sx*Sy) / SquareRoot((M*Sxx - Sx*Sx)*(M*Syy - Sy*Sy));
End;

// Compute the Fourier Transform for each Correlation
For Period = 8 to 48 Begin
  CosinePart[Period] = 0;
  SinePart[Period] = 0;
  For N = 3 to 48 Begin
    CosinePart[Period] = CosinePart[Period] + Corr[N]*Cosine(360*N / Period);
    SinePart[Period] = SinePart[Period] + Corr[N]*Sine(360*N / Period);
  End;
  SqSum[Period] = CosinePart[Period]*CosinePart[Period] + SinePart[Period]*SinePart[Period];
End;

For Period = 8 to 48 Begin
  R[Period, 2] = R[Period, 1];
  R[Period, 1] = .2*SqSum[Period]*SqSum[Period] + .8*R[Period, 2];
End;

// Find Maximum Power Level for Normalization
MaxPwr = 0;
For Period = 8 to 48 Begin
  If R[Period, 1] > MaxPwr Then MaxPwr = R[Period, 1];
End;

For Period = 8 to 48 Begin
  Pwr[Period] = R[Period, 1] / MaxPwr;
End;

// Optionally increase Display Resolution by raising the NormPwr to a higher
// mathematical power (since the maximum amplitude is unity, cubing all
// amplitudes further reduces the smaller ones).
If EnhanceResolution = True Then Begin
  For Period = 8 to 48 Begin
    Pwr[Period] = Power(Pwr[Period], 3);
  End;
End;

// Compute the dominant cycle using the CG of the spectrum
DominantCycle = 0;
PeakPwr = 0;
For Period = 8 to 48 Begin
  If Pwr[Period] > PeakPwr Then PeakPwr = Pwr[Period];
End;

Spx = 0;
Sp = 0;
For Period = 8 to 48 Begin
  If PeakPwr >= .25 and Pwr[Period] >= .25 Then Begin
    Spx = Spx + Period*Pwr[Period];
    Sp = Sp + Pwr[Period];
  End;
End;
If Sp <> 0 Then DominantCycle = Spx / Sp;
If Sp < .25 Then DominantCycle = DominantCycle[1];

// Plot as a Heatmap
Color3 = 0;
For Period = 8 to 48 Begin
  If Pwr[Period] > .5 Then Begin
    Color1 = 255;
    Color2 = 255*(2*Pwr[Period] - 1);
  End
  Else Begin
    Color1 = 2*255*Pwr[Period];
    Color2 = 0;
  End;
  If Period = 8 Then Plot8[0](8, "S8", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 9 Then Plot9[0](9, "S9", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 10 Then Plot10[0](10, "S10", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 11 Then Plot11[0](11, "S11", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 12 Then Plot12[0](12, "S12", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 13 Then Plot13[0](13, "S13", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 14 Then Plot14[0](14, "S14", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 15 Then Plot15[0](15, "S15", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 16 Then Plot16[0](16, "S16", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 17 Then Plot17[0](17, "S17", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 18 Then Plot18[0](18, "S18", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 19 Then Plot19[0](19, "S19", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 20 Then Plot20[0](20, "S20", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 21 Then Plot21[0](21, "S21", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 22 Then Plot22[0](22, "S22", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 23 Then Plot23[0](23, "S23", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 24 Then Plot24[0](24, "S24", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 25 Then Plot25[0](25, "S25", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 26 Then Plot26[0](26, "S26", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 27 Then Plot27[0](27, "S27", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 28 Then Plot28[0](28, "S28", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 29 Then Plot29[0](29, "S29", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 30 Then Plot30[0](30, "S30", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 31 Then Plot31[0](31, "S31", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 32 Then Plot32[0](32, "S32", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 33 Then Plot33[0](33, "S33", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 34 Then Plot34[0](34, "S34", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 35 Then Plot35[0](35, "S35", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 36 Then Plot36[0](36, "S36", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 37 Then Plot37[0](37, "S37", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 38 Then Plot38[0](38, "S38", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 39 Then Plot39[0](39, "S39", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 40 Then Plot40[0](40, "S40", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 41 Then Plot41[0](41, "S41", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 42 Then Plot42[0](42, "S42", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 43 Then Plot43[0](43, "S43", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 44 Then Plot44[0](44, "S44", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 45 Then Plot45[0](45, "S45", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 46 Then Plot46[0](46, "S46", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 47 Then Plot47[0](47, "S47", RGB(Color1, Color2, Color3), 0, 4);
  If Period = 48 Then Plot48[0](48, "S48", RGB(Color1, Color2, Color3), 0, 4);
End;
```

---

## Further Reading

- Ehlers, John [2013]. *Cycle Analytics For Traders*, Wiley.
- Ehlers, John [2016]. "Whiter Is Brighter," *Technical Analysis of STOCKS & COMMODITIES*, Volume 34: January.
- Ehlers, John [2014]. "Predictive And Successful Indicators," *Technical Analysis of STOCKS & COMMODITIES*, Volume 32: January.

---

## BibTeX

```bibtex
@article{ehlers_measuring_cycles_2016,
  author = {Ehlers, John F.},
  title = {Measuring Market Cycles},
  journal = {Technical Analysis of STOCKS \& COMMODITIES},
  volume = {34},
  number = {9},
  pages = {11--16},
  year = {2016},
  month = sep,
  url = {https://technical.traders.com/archive/article.asp?file=\V34\C09\280EHLE.pdf}
}

@misc{traders_tips_2016_09,
  author = {{Technical Analysis of STOCKS \& COMMODITIES}},
  title = {Traders' Tips: Measuring Market Cycles},
  year = {2016},
  month = sep,
  howpublished = {online},
  url = {https://www.traders.com/Documentation/FEEDbk_docs/2016/09/TradersTips.html}
}
```
