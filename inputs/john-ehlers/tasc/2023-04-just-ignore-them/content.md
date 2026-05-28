# Just Ignore Them

- **Author**: John F. Ehlers
- **Publication**: Technical Analysis of Stocks & Commodities
- **Volume/Issue**: V41:04 (April 2023)
- **Pages**: 8--12, 43
- **Category**: Digital Signal Processing
- **URL**: <https://technical.traders.com/archive/article.asp?file=\V41\C04\594EHLE.pdf>

---

## Undersampling The Data As A Smoothing Technique

*To avoid whipsaw trades, traders smooth the market data to get better and less-frequent trading signals. But smoothing filters have drawbacks, such as introducing lag. Here is an effective solution, and it's simpler than you might expect.*

High-frequency components in the data spectra---that is, "noise" in the data or all the extra wiggles on the chart that distract from price direction---are the bane of traders because they often lead to whipsaw trades. The usual approach is to reduce their effect on trading rules through the use of smoothing filters, such as moving averages. In the past I have introduced more effective smoothing filters, like the SuperSmoother infinite impulse response (IIR) filter and the Hann windowed finite impulse response (FIR) filter.

I now propose to eliminate those high-frequency components with a new approach.

### Data sampling rate

Market data are sampled data. For example, using daily data, we get only one sample per day. Regardless of whether that sample is the close representing the data for that day, the average of the high, low, and close, or any other combination of available statistics. We still only get one sample per day. The sample rate can be increased. For example, trading intraday on 15-minute bars is not uncommon. There is a temptation to increase the sample rate further, using five-minute bars, one-minute bars, or even tick bars. The temptation is caused by confusing resolution with accuracy. More intricate market activity is revealed by the higher sampling rate, but the increased resolution doesn't necessarily lead to greater trading profits. The reason for this is that the market data is fractal and has the spectral density of pink noise. That is, the amplitude of the cycle components in the spectrum are directly correlated with their wavelength. If you shorten the wavelength by a factor of 2, then you can expect the cycle amplitude to be reduced to half amplitude. So, increasing the sampling rate necessarily leads to a lower gross profit per trade because the data swings are less, all other things being equal. When carried far enough, transaction costs of slippage and commission can exceed your average gross profit per trade.

The bottom line is there is a "sweet spot" for sampling rate that depends on the trader's technique.

### A new approach to smoothing

No matter the sampling rate, we still have to get rid of those pesky high-frequency components. My radical proposal is this: Simply *ignore them*. But ignoring the high-frequency components doesn't come for free.

Sampled data is different from continuous data because its shortest possible wavelength has exactly two samples per cycle. This is called the *Nyquist frequency*. Sampled data simply does not contain information whose wavelengths are shorter than that of the Nyquist frequency. Of course, those spectrum components are still there in continuous data. The sampling process handles those shorter wavelength components by *aliasing*. That is, the shorter wavelength components are simply folded back into the observable spectrum.

Figure 1 illustrates the principle of aliasing, where the cyan line is sampled every 1.25 cycles. The wavelength of the cyan line is shorter than the Nyquist frequency, and so it appears that the signal is the blue line. The samples exactly fit both the cyan and blue sine waves, but the blue line has a longer wavelength than the Nyquist frequency. Thus, in this case, the observable spectrum component is the blue line because it is the aliased version of the cyan line.

![Figure 1: Aliasing. The principle of aliasing is demonstrated here. That is, signals become indistinguishable---or aliases of one another---when sampled. Here, the cyan line is sampled every 1.25 cycles of the market data. The samples exactly fit both the cyan and blue sine waves, but the blue line has a longer wavelength than the Nyquist frequency. In sampled data, as opposed to continuous data, the shortest possible wavelength has exactly two samples per cycle.](assets/figure-1-aliasing.png)
**Figure 1: Aliasing.** The principle of aliasing is demonstrated here. That is, signals become indistinguishable---or aliases of one another---when sampled. Here, the cyan line is sampled every 1.25 cycles of the market data. The samples exactly fit both the cyan and blue sine waves, but the blue line has a longer wavelength than the Nyquist frequency. In sampled data, as opposed to continuous data, the shortest possible wavelength has exactly two samples per cycle.  

It is a workable approximation that the cycle amplitude is halved every time the cycle spectrum component wavelength is doubled. So, if we sample once every five days, a five-day cycle period component is aliased back into our observable spectrum at half amplitude, a 2.5-day period component is aliased back into the observable spectrum at one quarter amplitude, and so on. So, the aliased energy falls off rapidly compared to the desired signal energy.

Further, market data is nonstationary and so the aliased energy does not fold back coherently. Rather, it is simply a little more noise added to the already noisy signal. The end result is that aliasing is hardly noticed, as a practical matter.

### Market data is fractal

The reason that we can ignore the high-frequency components in market data is because market data is fractal.

> **Undersampling removes the high-frequency components in price data. Elimination of these components is done with less lag than that of conventional smoothing filters.**

### Less lag

The *undersampled* data also undergoes a quantization lag that is half the quantization step size. ("Quantization" means to subdivide into small but measurable increments.) If daily data is sampled every five days, the induced lag is 2.5 days. This lag is much shorter than that of smoothing filters that reject cyclic components longer than the Nyquist rate (10 days) if we were using daily samples.

A practical application of smoothing by undersampling is shown in Figure 2. The undersampled data is further smoothed by a six-period Hann filter and a 12-period Hann filter to be the equivalent of a double moving average. It is apparent that the high-frequency components in the data have been removed by the combination of undersampling and Hann-windowed FIR filters.

![Figure 2: Smoothing by undersampling (daily market data). The data is sampled here every five bars, effectively. The undersampled data are further smoothed by a six-period Hann filter and a 12-period Hann filter to be the equivalent of a double moving average. The high-frequency components in the data are removed by the combination of undersampling and Hann-windowed FIR filters. You can see that the two moving averages, the blue and indigo lines, are very smooth.](assets/figure-2-daily-smoothing.png)
**Figure 2: Smoothing by undersampling (daily market data).** The data is sampled here every five bars, effectively. The undersampled data are further smoothed by a six-period Hann filter and a 12-period Hann filter to be the equivalent of a double moving average. The high-frequency components in the data are removed by the combination of undersampling and Hann-windowed FIR filters. You can see that the two moving averages, the blue and indigo lines, are very smooth.

### Implementing the concept

EasyLanguage code to produce the double MA indicator is given in the sidebar, "Code For Undersampled Double Moving Average, In EasyLanguage."

The sampled value is the same as the previous sampled value except when the integer portion of the current bar divided by 5 is exactly equal to the current bar divided by 5. In this case, the sampled value is assigned the value of the closing price. Thus, the data is effectively sampled every five bars. The Hann filter is written as a function, and the function is given in the sidebar, "Code For $Hann Function, In EasyLanguage." Note that the dollar sign in naming of the function is important.

Intraday data can also be smoothed by undersampling. The method to do this is described with reference to the sidebar, "Code For Undersampled Intraday Double Moving Average, In EasyLanguage." Intraday data for index futures is available as a "day session" that runs from 6:30 am to 1:15 pm Pacific Time (you will need to adjust for your time zone). I have assumed 15-minute bars are used, so the first bar of the day is 645. At the close of the first bar of the day, the *gap* value is computed as the difference of the closing price and the previous value of *degap*.

> **More intricate market activity is revealed by the higher sampling rate, but the increased resolution doesn't necessarily lead to greater trading profits.**

Then, that gap value is mathematically removed from every sample during the day. This technique removes the opening price gap from the overnight period and provides a more continuous function for analysis. The sampling is conducted only on the hour and at the session closing time. Otherwise, the previous value of *degap* is held. So the data is effectively sampled every four bars. The little jitter in the sampling clock due to the time offset of the first and last bar of the day doesn't matter much because the data are not coherent.

The beginning date for the indicator is provided as an input. This is required because the impact of the opening gap is cumulative, and the degapped undersampled data can drift from the absolute values of the prices.

Just to demonstrate the smoothing process of undersampling, a double moving average type indicator is shown in Figure 3, using Hann windowed FIR filters.

![Figure 3: Smoothing by undersampling (intraday market data). The undersampling technique can also be used for intraday data, as demonstrated here. The data is sampled here every four bars, effectively. Because opening gaps are removed from the data and the gap removal is cumulative, the intraday undersampled data is offset from prices.](assets/figure-3-intraday-smoothing.png)
**Figure 3: Smoothing by undersampling (intraday market data).** The undersampling technique can also be used for intraday data, as demonstrated here. The data is sampled here every four bars, effectively. Because opening gaps are removed from the data and the gap removal is cumulative, the intraday undersampled data is offset from prices.

### Conclusion

I have shown that undersampling removes the high-frequency components in price data. Elimination of these components is done with less lag than that of conventional smoothing filters. Quantization lag is only half the undersampling step size. This magic is possible because the market data is fractal, so the aliased components have a small amplitude relative to the desired signal components. Further, the folding of the aliased component into the observable spectrum is performed noncoherently.

Undersampling can also be applied to intraday data, removing the overnight gap openings as well.

The degree of undersampling is designer's choice. However, care should be taken not to get carried away and start folding desired signals back onto the observable spectrum.

## Code: Undersampled Double MA Indicator (EasyLanguage)

The high-frequency components in the market data, which contribute to noisiness to the data, can be effectively removed by a combination of undersampling and Hann-windowed finite impulse response (FIR) filters. This code samples the data every five bars, effectively. This undersampled data is further smoothed by a sixperiod Hann filter and a 12-period Hann filter to be the equivalent of a double moving average.
The Hann filter referenced here is written as a function, and that function is provided in the next sidebar titled “Code For $Hann Function, In EasyLanguage.”

```easylanguage
{
    Undersampled Double MA Indicator
    (c) 2022 John F. Ehlers
}

Inputs:
    Fast Length(6),
    Slow Length(12);

Vars:
    Sample(0),
    Fasting(0),
    Slowing(0);

Sample = Sample[1];

//Sample every five days
If CurrentBar / 5 = IntPortion(CurrentBar / 5) Then Sample = Close;

//Find Fast Average using Hann FIR filter
FastAvg = $Hann(Sample, FastLength);
//Find Slow Average using Hann FIR filter
SlowAvg = $Hann(Sample, SlowLength);

Plot1(FastAvg, "", magenta, 6, 6);
Plot2(SlowAvg, "", blue, 6, 6);
```

## Code: $Hann Function (EasyLanguage)

The Hann filter is written here as a function, referenced in the code elsewhere in this article. Note that the dollar sign in naming of the function is important.

```easylanguage
{
    Function: Hann Windowed Lowpass FIR Filter
    (c) 2021-2022 John F. Ehlers
}

Inputs:
    Price(numericseries),
    Length(numericsimple);

Vars:
    count(0),
    coef(0),
    Filt(0);

Filt = 0;
coef = 0;
For count = 1 to Length Begin
    Filt = Filt + (1 - Cosine(360*count / (Length + 1)))*Price[count - 1];
    coef = coef + (1 - Cosine(360*count / (Length + 1)));
End;
If coef <> 0 Then $Hann = Filt / coef;
```

## Code: Undersampled Intraday Double MA Indicator (EasyLanguage)

The technique of smoothing data by undersampling the data can be applied to intraday data as well as to daily data. The code to do that is provided here. The data is sampled here every four bars, effectively.

```easylanguage
{
    Undersampled Intraday Double MA Indicator
    (c) 2022 John F. Ehlers
}

Inputs:
    BegDate(1221117),
    FastLength(20),
    SlowLength(40);

Vars:
    Gap(0),
    Degap(0),
    FastAvg(0),
    SlowAvg(0);

Degap = Degap[1];

If Time = 645 Then Begin
    Gap = Close - Degap[1];
    Degap = Close - Gap;
End;
If Time = 800 or Time = 900 or Time = 1000 or Time = 1100
or Time = 1200 or Time = 1315 Then Degap = Close - Gap;

If Date < BegDate Then Degap = Close;

//Find Fast Average using Hann FIR filter
FastAvg = $Hann(Degap, FastLength);
//Find Slow Average using Hann FIR filter
SlowAvg = $Hann(Degap, SlowLength);

Plot1(FastAvg, "", magenta, 6, 6);
Plot2(SlowAvg, "", blue, 6, 6);
```

## Further Reading

- Ehlers, John F. [2014]. "Predictive And Successful Indicators," *Technical Analysis of Stocks & Commodities*, Volume 32: January.
- Ehlers, John F. [2021]. "Windowing," *Technical Analysis of Stocks & Commodities*, Volume 39: September.

## About the Author

*John Ehlers, a Contributing Editor to Stocks & Commodities, is a pioneer in the use of cycles and DSP (digital signal processing) technical analysis. After four decades of dedication to advancing the field of digital signal processing and offering products and services to traders, he is retiring from the company he founded, MESA Software. An interview with him highlighting some of his important research and developments in quantitative and technical analysis appears elsewhere in this issue. Ehlers can be reached through his website at MESAsoftware.com.*

---

*The code given in this article is available in the Article Code section of our website, Traders.com.*

*See our Traders' Tips section beginning on page 44 for implementation of John Ehlers technique in various technical analysis programs and trading platforms. Accompanying program code can be found in the Traders' Tips area at Traders.com.*

---

```bibtex
@article{ehlers2023justignore,
  author  = {Ehlers, John F.},
  title   = {Just Ignore Them: Undersampling The Data As A Smoothing Technique},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume  = {41},
  number  = {4},
  pages   = {8--12, 43},
  year    = {2023},
  month   = apr,
  url     = {https://technical.traders.com/archive/article.asp?file=\V41\C04\594EHLE.pdf}
}
```
