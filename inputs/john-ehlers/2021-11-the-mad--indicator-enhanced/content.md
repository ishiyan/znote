# The MAD Indicator, Enhanced

*The MADH*

**by John F. Ehlers**

- **Article URL:** <https://technical.traders.com/archive/article.asp?file=\V39\C11\330EHLE.pdf>
- **Traders' Tips URL:** <https://www.traders.com/Documentation/FEEDbk_docs/2021/11/TradersTips.html>

---

> Here, the MAD indicator introduced last month is made even better for technical traders. We'll explain how the MADH is created and how you can put it to use.

Last month in my October 2021 article, "Cycle/Trend Analytics And The MAD Indicator," I introduced the MAD indicator as a "thinking man's" MACD. I shared this indicator that I developed because I found it to be robust yet elegant in its simplicity.

In this article, I will apply an improvement to the MAD indicator to create a new version of it, which I call the *MADH*. I'll show both indicators on a chart for comparison, and I'll explain why this improvement makes it even more useful for technical traders. I'll also provide code to display the MADH.

## A quick review of the MAD indicator

The MAD indicator is comprised of the difference of two simple moving averages. The length of the shorter moving average is determined by the desired smoothness of the indicator, and the length of the longer moving average is the length of the shorter plus the half-period of the dominant cycle in the data. (If the dominant cycle is unknown, make the length of the longer moving average twice the length of the shorter one.)

The MAD and MADH oscillators came out of a research project I've been undertaking to further my understanding of cycles data and improve the use of digital signal processing techniques for traders. I explain some of my reasons and goals for pursuing that research in several recent articles in this magazine, including in last month's article and in my May 2021 S&C article, "A Technical Description Of Market Data For Traders," as well as several others (see "Further reading" at end). The research has led me to update my outlook and to change my approach to preprocessing data for the technical indicators I use.

In my research project, I wanted to display an oscillator in a way that would demonstrate how it would behave as the length of the moving average was varied. I felt this could provide some of the insights into the characteristics of cycles that I was looking for.

The idea with the MAD oscillator is to show the trend by taking the difference of two simple moving averages. The high-frequency components are canceled when the difference is taken. If the difference of the length of the two moving averages is one half the period of the dominant cycle, then the resultant will be exactly in phase with the input price.

The MAD offers an improvement over the classic, well-known MACD indicator developed several decades ago by Gerald Appel because the MAD offers a rationale for establishing the lengths of the moving averages.

## A quick review of windowing

In my September 2021 article "Windowing," I showed that a simple moving average (SMA), while being ubiquitous in technical analysis, is not a particularly good filter. The simple moving average uses a rectangular window in its generation, and the Fourier transform of the sharp edges of this window led to "sidelobe leakage" in its filter response. The solution to making a better average is to soften the sharp corners of the window.

For that, I nominated the *Hann window*, which has a cosine squared-shape coefficient amplitude distribution across the length of the filter. (This distribution envelope starts at zero at one end of the filter and smoothly rises to a maximum at the middle in a lazy "S"-shaped pattern, and then declines symmetrically to the other end.) I had reviewed several windowing functions—which are commonly used functions in statistics and digital filtering—and ended up choosing the Hann filter, which seems to me to be the best compromise for technical traders.

## And now for the improved MAD: MADH

The improved MAD filter—the MADH—is just a combination of the two above concepts. That is, instead of taking the difference of two simple moving averages, the improved version takes the difference of two finite impulse response (FIR) filters that employ Hann windowing. For simplicity, I call this new improved indicator the MADH (that is, MAD with Hann windowing).

A comparison of the original MAD indicator and the improved MADH indicator is shown in Figure 1. The same parameter values are used for both indicators. The original MAD is in the first subgraph (in red), and the MADH is in the second subgraph (in yellow). Both have about the same overall response, but the MADH is smoother.

Excellent buy and sell indications are at the valleys and peaks, respectively, of the indicators. The valleys and peaks are determined when the rate of change of the indicators are zero, so when the one-bar difference of the indicators cross zero, these are the buy and sell timing signals. Since the one-bar difference is analogous to the derivative in calculus, and since taking the derivative always increases the noise level, the MADH indicator will have fewer false signals that are due to noise.

I provide EasyLanguage code for the MADH indicator in the sidebar, "MADH Indicator, EasyLanguage Code."

![Figure 1: The MADH. The MADH indicator offers an improvement over the MAD indicator through the use of the Hann windowing technique. The original MAD is shown in the first subgraph in red; the MADH is in the second subgraph in yellow. The same parameter values are used for both indicators. The improvement comes from the use of the Hann windowing technique. That is, instead of taking the difference of two simple moving averages, the MADH takes the difference of two finite impulse response filters that employ Hann windowing. The result is equally good timing signals but a smoother curve, which means fewer false signals.](assets/figure-01.png)
**Figure 1: The MADH.** The MADH indicator offers an improvement over the MAD indicator through the use of the Hann windowing technique. The original MAD is shown in the first subgraph in red; the MADH is in the second subgraph in yellow. The same parameter values are used for both indicators. The improvement comes from the use of the Hann windowing technique. That is, instead of taking the difference of two simple moving averages, the MADH takes the difference of two finite impulse response filters that employ Hann windowing. The result is equally good timing signals but a smoother curve, which means fewer false signals.

## Simply MAD about market data

My recent research into the nature of market data and the characteristics of cycles that occur in data has led me to make some significant improvements in the indicators and oscillators I use for trading. My goal is to share some of this work with you as well as to explain my rationale for it. The research has evolved my outlook on market data and on trend/cycle analytics. It has also led me to update many indicators used for trading. One of these newly updated indicators is the MADH presented here (the moving average difference–Hann).

In upcoming articles, I will share additional updated indicators based on this research.

See our Traders' Tips section beginning on page 48 for implementation of John Ehlers' technique in various technical analysis programs and trading platforms. Accompanying program code can be found in the Traders' Tips area at Traders.com.

## MADH Indicator, EasyLanguage Code

```easylanguage
{
    MADH (Moving Average Difference - Hann) Indicator
    (C) 2021 John F. Ehlers
}

Inputs:
    ShortLength(8),
    DominantCycle(27);

Vars:
    LongLength(20),
    Filt1(0),
    Filt2(0),
    coef(0),
    count(0),
    MADH(0);

LongLength = IntPortion(ShortLength + DominantCycle / 2);

Filt1 = 0;
coef = 0;
For count = 1 to ShortLength Begin
    Filt1 = Filt1 + (1 - Cosine(360*count / (ShortLength + 1)))*Close[count - 1];
    coef = coef + (1 - Cosine(360*count / (ShortLength + 1)));
End;
If coef <> 0 Then Filt1 = Filt1 / coef;

Filt2 = 0;
coef = 0;
For count = 1 to LongLength Begin
    Filt2 = Filt2 + (1 - Cosine(360*count / (LongLength + 1)))*Close[count - 1];
    coef = coef + (1 - Cosine(360*count / (LongLength + 1)));
End;
If coef <> 0 Then Filt2 = Filt2 / coef;

//Computed as percentage of price
If Filt2 <> 0 Then MADH = 100*(Filt1 - Filt2) / Filt2;

Plot1(MADH, "", yellow, 4, 4);
Plot2(0, "", white, 1, 1);
```

## Further reading

- Ehlers, John F. [2021]. "Windowing," *Technical Analysis of Stocks & Commodities*, Volume 39: September.
- Ehlers, John F. [2021]. "Cycle/Trend Analytics And The MAD Indicator," *Technical Analysis of Stocks & Commodities*, Volume 39: October.
- Ehlers, John F. [2013]. *Cycle Analytics For Traders*, John Wiley & Sons.

---

*John Ehlers, a Contributing Editor to Stocks & Commodities, is a pioneer in the use of cycles and DSP (digital signal processing) technical analysis. He is president of MESA Software. He can be reached through his website at MESAsoftware.com.*

*Originally published in the November 2021 issue of Technical Analysis of Stocks & Commodities magazine, Volume 39, pp. 24–26. All rights reserved.*

---

## BibTeX

```bibtex
@article{ehlers2021madh,
  author       = {Ehlers, John F.},
  title        = {The {MAD} Indicator, Enhanced},
  journal      = {Technical Analysis of Stocks \& Commodities},
  year         = {2021},
  month        = nov,
  volume       = {39},
  number       = {11},
  pages        = {24--26},
  url          = {https://technical.traders.com/archive/article.asp?file=\V39\C11\330EHLE.pdf}
}

@misc{tasc2021traderstips11,
  author       = {{Technical Analysis of Stocks \& Commodities}},
  title        = {Traders' Tips, November 2021},
  year         = {2021},
  month        = nov,
  url          = {https://www.traders.com/Documentation/FEEDbk_docs/2021/11/TradersTips.html},
  note         = {Traders' Tips implementations for ``The MAD Indicator, Enhanced'' by John F. Ehlers}
}
```
