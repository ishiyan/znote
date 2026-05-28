# Every Little Bit Helps

- **Author**: John F. Ehlers
- **Publication**: Technical Analysis of Stocks & Commodities
- **Volume/Issue**: V41:03 (March 2023)
- **Pages**: 14--15
- **Category**: Digital Signal Processing
- **URL**: <https://technical.traders.com/archive/article.asp?file=\V41\C03\571EHLE.pdf>
- **Traders' Tips URL**: <https://www.traders.com/Documentation/FEEDbk_docs/2023/03/TradersTips.html>

---

## Averaging The Open And Close To Reduce Noise

*It's simple but makes a noticeable improvement: You can reduce noise in the data by using an average of the open and close instead of using only the closing price. Here's how to do it.*

**by John F. Ehlers**

Market data are sampled data. We technicians usually use the closing price of a bar to represent the sampled price for that bar. Sometimes the average of the high, low, and close is used to represent the sampled data for that bar. In this article, I will show you a simple trick that makes a small but measurable improvement in your sample.

### Reducing noise

Using sampled data, the shortest wavelength that can be used has a wavelength of two bars. This is called the Nyquist frequency. The digital signal processing (DSP) trick reduces noise near the Nyquist frequency, but otherwise leaves the signal unchanged in the information band of the signal spectrum.

The trick is to note that the opening price of a bar is virtually synonymous with the closing price of the previous bar, particularly if we are dealing with intraday data. So, averaging the opening price with the closing price of the same bar is almost the same thing as taking a two-bar average of the closes of continuous data. That being the case, we can achieve a 6 dB reduction in noise at Nyquist by using an average of the open and close, compared to using only closing price as our sample. An additional advantage is that the average provides a theoretical half-bar lead along the time axis.

In fact, measured power near Nyquist using the average of the open and the close is nearly 6 dB less than using the close alone. Difference of the measured power in the signal band of the spectrum (for example, at a 30-bar period) using the two sampling techniques is imperceptible. Measured power reduction near Nyquist using the average of the high, low, and close is only on the order of 1 dB, making it hardly worth the effort.

Noise reduction near Nyquist is irrelevant if you are using an indicator with a zero in its transfer function at Nyquist or if you have a well-designed smoothing filter such as a Hann windowed finite impulse response (FIR) filter. This is because these filters already suppress signals near Nyquist. On the other hand, commonly used indicators such as the RSI, MACD, and stochastic do not have zeros at Nyquist in their transfer responses.

### Every little bit

Figure 1 shows a comparison of using a 14-bar RSI on 15-minute bars of the emini S&P futures data. Sampling using closing prices is shown in red. Sampling using the average of the open and close is shown in blue. The blue line is noticeably smoother with regard to the high-frequency wiggle, relative to the red line.

You can reproduce this test using the EasyLanguage code in the sidebar, "Code To Test Data Sampling, In EasyLanguage."

![Figure 1: Sampled Data: Averaging The Open And Close. The example here is a 14-bar RSI on 15-minute bars of emini S&P futures data (ES). Shown in red is the sampling using closing prices. Shown in blue is the sampling using the average of the open and close. You can see that averaging the open and close provides a smoother indicator. The blue line is noticeably smoother than the red line with regard to the high-frequency wiggle.](assets/figure-1-data-sampling.png)
**Figure 1: Sampled Data: Averaging The Open And Close.** The example here is a 14-bar RSI on 15-minute bars of emini S&P futures data (ES). Shown in red is the sampling using closing prices. Shown in blue is the sampling using the average of the open and close. You can see that averaging the open and close provides a smoother indicator. The blue line is noticeably smoother than the red line with regard to the high-frequency wiggle.

## Code To Test Data Sampling, In EasyLanguage

```easylanguage
// Data Sampling Test
// (c) John Ehlers 2022

Vars:
    CTest(0),
    OCTest(0);

CTest = RSI(close, 14);
OCTest = RSI((Open + close) / 2, 14);

Plot1(CTest, "", red, 4, 4);
Plot3(OCTest, "", blue, 4, 4);
```

## Further Reading

- Ehlers, John [2021]. "Windowing," *Technical Analysis of Stocks & Commodities*, Volume 39: September.

## About the Author

*John Ehlers, a Contributing Editor to Stocks & Commodities, is a pioneer in the use of cycles and DSP (digital signal processing) technical analysis. After four decades of dedication to advancing the field of digital signal processing and offering products and services to traders, he is retiring from his company, MESA Software. He can be reached through his website at MESAsoftware.com.*

---

*The code given in this article is available in the Article Code section of our website, Traders.com.*

*See our Traders' Tips section beginning on page 50 for implementation of John Ehlers' technique in various technical analysis programs and trading platforms. Accompanying program code can be found in the Traders' Tips area at Traders.com.*

---

```bibtex
@article{ehlers2023everylittlebit,
  author  = {Ehlers, John F.},
  title   = {Every Little Bit Helps: Averaging The Open And Close To Reduce Noise},
  journal = {Technical Analysis of Stocks \& Commodities},
  volume  = {41},
  number  = {3},
  pages   = {14--15},
  year    = {2023},
  month   = mar,
  url     = {https://technical.traders.com/archive/article.asp?file=\V41\C03\571EHLE.pdf}
}

@misc{traderstips202303,
  title        = {Traders' Tips: Every Little Bit Helps},
  journal      = {Technical Analysis of Stocks \& Commodities},
  volume       = {41},
  number       = {3},
  year         = {2023},
  month        = mar,
  url          = {https://www.traders.com/Documentation/FEEDbk_docs/2023/03/TradersTips.html},
  howpublished = {online},
  note         = {Implementations for various platforms}
}
```
