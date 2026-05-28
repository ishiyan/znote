# Drunkard's Walk: Theory And Measurement By Autocorrelation

**Solving The Random Variable Problem**

*by John F. Ehlers*

Technical Analysis of STOCKS & COMMODITIES, Volume 43, February 2025, pp. 8–15

- **Article URL:** https://technical.traders.com/archive/article.asp?file=\V43\C02\910EHLE.pdf
- **Traders' Tips URL:** https://www.traders.com/Documentation/FEEDbk_docs/2025/02/TradersTips.html

---

*Here, we look at some of the basic issues that underlie technical analysis itself. And we introduce a new indicator, called "autocorrelation," you can use to test for correlation in the data.*

Drunkard's walk is a rather fanciful name for a random variable problem used to mathematically model financial price data. It is easy to visualize a drunk staggering randomly to the right and left as he takes each step forward. The staggering in two dimensions to the right and left is analogous to prices moving up and down with each sample. Formalism of continuous random variables makes understanding of the resulting partial differential equations a little daunting. So in this article, I will simplify the problem using discrete samples and Z transforms.

## Diffusion Equation, Wave Equation

In this notation, $Z^{-1}$ means one unit of delay. *Z transforms* have evolved from *LaPlace transforms* that are used to solve differential equations as if they were algebra problems.

If the random variable is positioned to the right or left with each step forward, the new position is the current position plus the random variable plus a drift bias. The equation for this problem statement is:

$$X = B + X * Z^{-1} + \varepsilon$$

where $\varepsilon$ is the random variable and $B$ is a constant drift.

This is a first-order polynomial. The partial differential equation form of this equation is called the *diffusion equation*. Perhaps the easiest way to visualize the use of the diffusion equation in the physical world is to imagine a plume of smoke. The tilt of the plume comes from the constant drift component. Then the position of any particle of smoke is described by the random variable departure from the average plume.

Another partial differential equation solution to the continuous variable random walk problem is called the *wave equation*. This equation basically says that the second-order partial derivative with respect to *time* is proportional to the second-order partial derivative with respect to *position*. In the discrete case, the change with respect to time is two units along the horizontal axis. The change in the vertical axis is the position two units ago plus the random variable to establish the position one unit ago, and then another random variable added to that position to get to the current position. So, the equation is:

$$X = B + (X * Z^{-2} + \varepsilon_1 + \varepsilon_2) / 2$$

It is possible to restate the problem where the drunk makes a random decision to step in the same direction as the last step or in the opposite direction. In this case, the random variable is *momentum*, not *position*.

Perhaps the easiest way to understand the difference between the diffusion equation and the wave equation is to run an Excel simulation of the two sampled data equations above. In cell A1 enter `=2*(RAND()-.5)`. This creates a random number between −1 and +1. Then copy cell A1 and paste the copy into cells A1 through A20. Then copy cells A1 through A20 and paste the copy to cells A21, A41, A61, and A81. This creates a random data set that is lightly correlated with a 20-unit cycle. Column C will be the first-order random walk solution. In cell C3 enter `= 0.1 + C2 + A3`. The drift value is fixed at 0.1. Then copy cell C3 and paste the copy into cells C3 through C100. Column D will be the second-order random walk solution. In cell D3 enter `= 0.1 + (D1 + A2 + A3) / 2`. Then copy cell D3 and paste the copy into cells D3 through D100.

When you chart columns C and D you will get a display something like that shown in Figure 1. If you press F9, all the random numbers change and you will get a slightly different display. The interpretation is that the diffusion equation has a continuous slope with a random variation from that slope. This is like the analogy of a smoke plume. There is a major drift, and each particle of smoke varies randomly from the drift. On the other hand, the wave equation loses the impact of the drift. You can start to see the periodicity of the random variable with peaks typically appearing at 20, 40, 60, and 80. The closest physical analogy to the wave equation is the meandering of a river.

![Figure 1: The trend is lost when the random variable is momentum. The diffusion equation has a continuous slope with a random variation from that slope. You can start to see the periodicity of the random variable with peaks typically appearing at 20, 40, 60, and 80.](assets/figure-1-random-walk-simulations.png)
**Figure 1:** The trend is lost when the random variable is momentum. The diffusion equation has a continuous slope with a random variation from that slope. You can start to see the periodicity of the random variable with peaks typically appearing at 20, 40, 60, and 80.

My opinion is that market data consists of a mixture of the diffusion mode and the wave mode. If the diffusion mode is dominant, trading success is almost a matter of luck. If the wave mode is dominant, indicators can be brought to bear with amazing results.

## Pink Spectrum

There is a plethora of recent academic studies that affirm that market data has a pink spectrum. This means that the power spectral density is proportional to the wavelengths in the spectrum. A random process with a pink spectrum suggests that the values of the random variable are not independent. There are correlations between them over time. Specifically, it means there is a long-range dependence or memory with respect to past values.

## Autocorrelation

A mathematical test for correlation in the data can be done with the autocorrelation function. *Autocorrelation* is performed by choosing a length of data and repeatedly sliding that data segment past the static waveform with increasing lag.

For example, consider a perfect sine wave having a 20-bar wavelength. We first choose a 1-wavelength data sample. When there is zero lag, the two data segments are perfectly correlated. With a lag of 10 bars, the two data segments are perfectly anticorrelated. Increasing the lag to 20 bars, the two data segments are perfectly correlated again. As the lag is further increased, the correlation pattern repeats every 20 bars. The display of this process is called a *periodogram*. Picture *correlation* being green, *anticorrelation* being red, with *lag* scaled on the vertical axis. Time is scaled along the horizontal axis.

Doing this, you get the periodogram shown in Figure 2. Note the green correction at the bottom of the chart where the lag is zero and note that the correlation pattern repeats vertically every 20 bars of lag.

![Figure 2: Periodogram of a 20-bar sine wave using a 20-bar data length. When there is zero lag, the two data segments are perfectly correlated. With a lag of 10 bars, the two data segments are perfectly anticorrelated. With a lag of 20 bars, the two data segments are perfectly correlated again. The correlation pattern repeats every 20 bars, as seen in this periodogram. Here, correlation is in green, anticorrelation is in red. Lag is scaled on the vertical axis, time is scaled on the horizontal axis. Note the green correction at the bottom of the chart where the lag is zero.](assets/figure-2-periodogram-20bar.png)
**Figure 2:** Periodogram of a 20-bar sine wave using a 20-bar data length. When there is zero lag, the two data segments are perfectly correlated. With a lag of 10 bars, the two data segments are perfectly anticorrelated. With a lag of 20 bars, the two data segments are perfectly correlated again. The correlation pattern repeats every 20 bars, as seen in this periodogram. Here, correlation is in green, anticorrelation is in red. Lag is scaled on the vertical axis, time is scaled on the horizontal axis. Note the green correction at the bottom of the chart where the lag is zero.

We get quite a different picture if we reduce the data length to two bars (see Figure 3). Doing this, we are fully correlated most of the time near the zero lag baseline. However, there is a switch to anticorrelation at each peak and valley of the waveform. The turning points can be visually identified along the time axis by the switches between green and red along the vertical axis. Nevertheless, the 20-bar cycle period is still identified by the pattern that repeats with each 20 bars of lag along the vertical axis. The history of the turning points is plotted as the slope in the pattern. The slope of the pattern near the lag baseline identifies the trends.

![Figure 3: Periodogram of a 2-bar sine wave using a 2-bar data length. If the data length is reduced to two bars, the data plot is fully correlated most of the time near the zero lag baseline. At each peak and valley of the waveform, it switches to anticorrelation. Turning points can be seen at these switches between green and red along the vertical axis. The history of the turning points is plotted as the slope in the pattern. The slope of the pattern near the lag baseline identifies the trends.](assets/figure-3-periodogram-2bar.png)
**Figure 3:** Periodogram of a 2-bar sine wave using a 2-bar data length. If the data length is reduced to two bars, the data plot is fully correlated most of the time near the zero lag baseline. At each peak and valley of the waveform, it switches to anticorrelation. Turning points can be seen at these switches between green and red along the vertical axis. The history of the turning points is plotted as the slope in the pattern. The slope of the pattern near the lag baseline identifies the trends.

Approximately one year of daily data for the emini S&P futures contract is shown in Figure 4. A data length of 20 bars is used for the autocorrelation because it is natural to examine the data for monthly (about 20-bar) cycle periods. You can see the repetitive pattern in the data of about 29 bars in the fall of 2023 and the winter of 2023–2024. Then the trend during the spring of 2024 is noted by the green triangle rising from the zero lag baseline. The green correlation triangle trend pattern is repeated again from May through July 2024.

![Figure 4: Autocorrelation of emini S&P using a 20-bar data length. Since monthly data is about 20 bars, a data length of 20 bars is used for the autocorrelation. You can see the repetitive pattern in the data of about 29 bars in fall 2023 and winter 2023–2024. Then the trend during spring 2024 is noted by the green triangular shape rising from the zero lag baseline. The green correlation triangle trend pattern is repeated again from May through July 2024.](assets/figure-4-autocorrelation-20bar.png)
**Figure 4:** Autocorrelation of emini S&P using a 20-bar data length. Since monthly data is about 20 bars, a data length of 20 bars is used for the autocorrelation. You can see the repetitive pattern in the data of about 29 bars in fall 2023 and winter 2023–2024. Then the trend during spring 2024 is noted by the green triangular shape rising from the zero lag baseline. The green correlation triangle trend pattern is repeated again from May through July 2024.

When we reduce the data length of autocorrelation to 2, we get the pattern shown in Figure 5. You can identify the turning points in the data waveform from the position of the vertical patterns in the autocorrelation. I use my UltimateSmoother (for more on this, see my April 2024 S&C article "The Ultimate Smoother," listed at the end of this article in "Further reading") to smooth the data and the short-term autocorrelation reversals without sacrificing much time lag in the indicator. Better smoothing, at the expense of time lag, can be obtained by using my SuperSmoother or Hann filter (for more on my technique for using the Hann filter, see my September 2021 S&C article "Windowing" listed at end in "Further reading"). You can also reduce the number of trend reversals by slightly increasing the data length used for the calculations.

![Figure 5: Autocorrelation of emini S&P using a 2-bar data length. When the data length of autocorrelation is reduced to 2, you get a pattern such as this. You can identify turning points in the data waveform from the position of the vertical patterns in the autocorrelation.](assets/figure-5-autocorrelation-2bar.png)
**Figure 5:** Autocorrelation of emini S&P using a 2-bar data length. When the data length of autocorrelation is reduced to 2, you get a pattern such as this. You can identify turning points in the data waveform from the position of the vertical patterns in the autocorrelation.

There is a great deal of flexibility in the use of autocorrelation in trading. It is a new type of indicator and probably takes a little time to become familiar with what the indicator is trying to tell you. Give it a try. If it doesn't work out as an indicator for you, you can still use it to create some stunning modern art.

The EasyLanguage code for the autocorrelation indicator is given in the sidebar, "Autocorrelation Indicator, In EasyLanguage Code."

The only reason the correlation array is scaled to 100 is that the number of individual indicator lines in an indicator is limited to 99. For convenience, the UltimateSmoother function code is given in the sidebar, "UltimateSmoother Function, In EasyLanguage Code."

## Conclusions

1. The drunkard's walk is a mathematical model of market data using random variables. There are two solutions: the diffusion equation and the wave equation.
2. The diffusion equation is associated with market trends.
3. The wave equation is associated with cycles in the market.
4. The autocorrelation indicator identifies market cycles by a repetitive pattern periodogram.
5. The autocorrelation indicator identifies market reversals by the vertical pattern across all lag periods when a short data length is used.
6. The autocorrelation indicator identifies trends by increasing correlation area from the baseline as a function of time.

## Autocorrelation Indicator, In EasyLanguage Code

```easylanguage
{
    AutoCorrelation Indicator
    (C) 2024 John F. Ehlers
}
Inputs:
    Length(20);

Vars:
    Filt(0),
    Lag(0),
    J(0),
    Sx(0),
    Sy(0),
    Sxx(0),
    Sxy(0),
    Syy(0),
    X(0),
    Y(0),
    Color1(0), Color2(0);

Arrays:
    Corr[100](0);

Filt = $UltimateSmoother(Close, 20);

//Cycle test waveform
//Filt = Sine(360*CurrentBar / 20);

//>>>>>>>>> Correlation >>>>>>>>>>>>
For Lag = 0 to 99 Begin
    Sx = 0;
    Sy = 0;
    Sxx = 0;
    Sxy = 0;
    Syy = 0;
    For J = 0 to Length - 1 Begin
        X = Filt[J];
        Y = Filt[Lag + J];
        Sx = Sx + X;
        Sy = Sy + Y;
        Sxx = Sxx + X*X;
        Sxy = Sxy + X*Y;
        Syy = Syy + Y*Y;
    End;
    If (Length*Sxx - Sx*Sx > 0) and (Length*Syy - Sy*Sy > 0) Then
        Corr[Lag + 1] = (Length*Sxy - Sx*Sy) /
            SquareRoot((Length*Sxx - Sx*Sx)*(Length*Syy - Sy*Sy));
End;

//Plot the AutoCorrelation as a Heatmap
For Lag = 1 to 99 Begin
    //Convert Power to RGB Color for Display
    If Corr[Lag + 1] >= 0 Then Begin
        Color2 = 255;
        Color1 = 255*(1 - Corr[Lag + 1]);
    End;
    If Corr[Lag + 1] < 0 Then Begin
        Color2 = 255*(1 + Corr[Lag + 1]);
        Color1 = 255;
    End;

    If Lag = 0 Then Plot1(0, "S0", RGB(Color1, Color2, 0),0,4);
    If Lag = 1 Then Plot2(1, "S1", RGB(Color1, Color2, 0),0,4);
    If Lag = 2 Then Plot3(2, "S2", RGB(Color1, Color2, 0),0,4);
    If Lag = 3 Then Plot4(3, "S3", RGB(Color1, Color2, 0),0,4);
    If Lag = 4 Then Plot5(4, "S4", RGB(Color1, Color2, 0),0,4);
    If Lag = 5 Then Plot6(5, "S5", RGB(Color1, Color2, 0),0,4);
    If Lag = 6 Then Plot7(6, "S6", RGB(Color1, Color2, 0),0,4);
    If Lag = 7 Then Plot8(7, "S7", RGB(Color1, Color2, 0),0,4);
    If Lag = 8 Then Plot9(8, "S8", RGB(Color1, Color2, 0),0,4);
    If Lag = 9 Then Plot10(9, "S9", RGB(Color1, Color2, 0),0,4);
    If Lag = 10 Then Plot11(10, "S10", RGB(Color1, Color2, 0),0,4);
    If Lag = 11 Then Plot12(11, "S11", RGB(Color1, Color2, 0),0,4);
    If Lag = 12 Then Plot13(12, "S12", RGB(Color1, Color2, 0),0,4);
    If Lag = 13 Then Plot14(13, "S13", RGB(Color1, Color2, 0),0,4);
    If Lag = 14 Then Plot15(14, "S14", RGB(Color1, Color2, 0),0,4);
    If Lag = 15 Then Plot16(15, "S15", RGB(Color1, Color2, 0),0,4);
    If Lag = 16 Then Plot17(16, "S16", RGB(Color1, Color2, 0),0,4);
    If Lag = 17 Then Plot18(17, "S17", RGB(Color1, Color2, 0),0,4);
    If Lag = 18 Then Plot19(18, "S18", RGB(Color1, Color2, 0),0,4);
    If Lag = 19 Then Plot20(19, "S19", RGB(Color1, Color2, 0),0,4);
    If Lag = 20 Then Plot21(20, "S20", RGB(Color1, Color2, 0),0,4);
    If Lag = 21 Then Plot22(21, "S21", RGB(Color1, Color2, 0),0,4);
    If Lag = 22 Then Plot23(22, "S22", RGB(Color1, Color2, 0),0,4);
    If Lag = 23 Then Plot24(23, "S23", RGB(Color1, Color2, 0),0,4);
    If Lag = 24 Then Plot25(24, "S24", RGB(Color1, Color2, 0),0,4);
    If Lag = 25 Then Plot26(25, "S25", RGB(Color1, Color2, 0),0,4);
    If Lag = 26 Then Plot27(26, "S26", RGB(Color1, Color2, 0),0,4);
    If Lag = 27 Then Plot28(27, "S27", RGB(Color1, Color2, 0),0,4);
    If Lag = 28 Then Plot29(28, "S28", RGB(Color1, Color2, 0),0,4);
    If Lag = 29 Then Plot30(29, "S29", RGB(Color1, Color2, 0),0,4);
    If Lag = 30 Then Plot31(30, "S30", RGB(Color1, Color2, 0),0,4);
    If Lag = 31 Then Plot32(31, "S31", RGB(Color1, Color2, 0),0,4);
    If Lag = 32 Then Plot33(32, "S32", RGB(Color1, Color2, 0),0,4);
    If Lag = 33 Then Plot34(33, "S33", RGB(Color1, Color2, 0),0,4);
    If Lag = 34 Then Plot35(34, "S34", RGB(Color1, Color2, 0),0,4);
    If Lag = 35 Then Plot36(35, "S35", RGB(Color1, Color2, 0),0,4);
    If Lag = 36 Then Plot37(36, "S36", RGB(Color1, Color2, 0),0,4);
    If Lag = 37 Then Plot38(37, "S37", RGB(Color1, Color2, 0),0,4);
    If Lag = 38 Then Plot39(38, "S38", RGB(Color1, Color2, 0),0,4);
    If Lag = 39 Then Plot40(39, "S39", RGB(Color1, Color2, 0),0,4);
    If Lag = 40 Then Plot41(40, "S40", RGB(Color1, Color2, 0),0,4);
    If Lag = 41 Then Plot42(41, "S41", RGB(Color1, Color2, 0),0,4);
    If Lag = 42 Then Plot43(42, "S42", RGB(Color1, Color2, 0),0,4);
    If Lag = 43 Then Plot44(43, "S43", RGB(Color1, Color2, 0),0,4);
    If Lag = 44 Then Plot45(44, "S44", RGB(Color1, Color2, 0),0,4);
    If Lag = 45 Then Plot46(45, "S45", RGB(Color1, Color2, 0),0,4);
    If Lag = 46 Then Plot47(46, "S46", RGB(Color1, Color2, 0),0,4);
    If Lag = 47 Then Plot48(47, "S47", RGB(Color1, Color2, 0),0,4);
    If Lag = 48 Then Plot49(48, "S48", RGB(Color1, Color2, 0),0,4);
    If Lag = 49 Then Plot50(49, "S49", RGB(Color1, Color2, 0),0,4);
    If Lag = 50 Then Plot51(50, "S50", RGB(Color1, Color2, 0),0,4);
    If Lag = 51 Then Plot52(51, "S51", RGB(Color1, Color2, 0),0,4);
    If Lag = 52 Then Plot53(52, "S52", RGB(Color1, Color2, 0),0,4);
    If Lag = 53 Then Plot54(53, "S53", RGB(Color1, Color2, 0),0,4);
    If Lag = 54 Then Plot55(54, "S54", RGB(Color1, Color2, 0),0,4);
    If Lag = 55 Then Plot56(55, "S55", RGB(Color1, Color2, 0),0,4);
    If Lag = 56 Then Plot57(56, "S56", RGB(Color1, Color2, 0),0,4);
    If Lag = 57 Then Plot58(57, "S57", RGB(Color1, Color2, 0),0,4);
    If Lag = 58 Then Plot59(58, "S58", RGB(Color1, Color2, 0),0,4);
    If Lag = 59 Then Plot60(59, "S59", RGB(Color1, Color2, 0),0,4);
    If Lag = 60 Then Plot61(60, "S60", RGB(Color1, Color2, 0),0,4);
    If Lag = 61 Then Plot62(61, "S61", RGB(Color1, Color2, 0),0,4);
    If Lag = 62 Then Plot63(62, "S62", RGB(Color1, Color2, 0),0,4);
    If Lag = 63 Then Plot64(63, "S63", RGB(Color1, Color2, 0),0,4);
    If Lag = 64 Then Plot65(64, "S64", RGB(Color1, Color2, 0),0,4);
    If Lag = 65 Then Plot66(65, "S65", RGB(Color1, Color2, 0),0,4);
    If Lag = 66 Then Plot67(66, "S66", RGB(Color1, Color2, 0),0,4);
    If Lag = 67 Then Plot68(67, "S67", RGB(Color1, Color2, 0),0,4);
    If Lag = 68 Then Plot69(68, "S68", RGB(Color1, Color2, 0),0,4);
    If Lag = 69 Then Plot70(69, "S69", RGB(Color1, Color2, 0),0,4);
    If Lag = 70 Then Plot71(70, "S70", RGB(Color1, Color2, 0),0,4);
    If Lag = 71 Then Plot72(71, "S71", RGB(Color1, Color2, 0),0,4);
    If Lag = 72 Then Plot73(72, "S72", RGB(Color1, Color2, 0),0,4);
    If Lag = 73 Then Plot74(73, "S73", RGB(Color1, Color2, 0),0,4);
    If Lag = 74 Then Plot75(74, "S74", RGB(Color1, Color2, 0),0,4);
    If Lag = 75 Then Plot76(75, "S75", RGB(Color1, Color2, 0),0,4);
    If Lag = 76 Then Plot77(76, "S76", RGB(Color1, Color2, 0),0,4);
    If Lag = 77 Then Plot78(77, "S77", RGB(Color1, Color2, 0),0,4);
    If Lag = 78 Then Plot79(78, "S78", RGB(Color1, Color2, 0),0,4);
    If Lag = 79 Then Plot80(79, "S79", RGB(Color1, Color2, 0),0,4);
    If Lag = 80 Then Plot81(80, "S80", RGB(Color1, Color2, 0),0,4);
    If Lag = 81 Then Plot82(81, "S81", RGB(Color1, Color2, 0),0,4);
    If Lag = 82 Then Plot83(82, "S82", RGB(Color1, Color2, 0),0,4);
    If Lag = 83 Then Plot84(83, "S83", RGB(Color1, Color2, 0),0,4);
    If Lag = 84 Then Plot85(84, "S84", RGB(Color1, Color2, 0),0,4);
    If Lag = 85 Then Plot86(85, "S85", RGB(Color1, Color2, 0),0,4);
    If Lag = 86 Then Plot87(86, "S86", RGB(Color1, Color2, 0),0,4);
    If Lag = 87 Then Plot88(87, "S87", RGB(Color1, Color2, 0),0,4);
    If Lag = 88 Then Plot89(88, "S88", RGB(Color1, Color2, 0),0,4);
    If Lag = 89 Then Plot90(89, "S89", RGB(Color1, Color2, 0),0,4);
    If Lag = 90 Then Plot91(90, "S90", RGB(Color1, Color2, 0),0,4);
    If Lag = 91 Then Plot92(91, "S91", RGB(Color1, Color2, 0),0,4);
    If Lag = 92 Then Plot93(92, "S92", RGB(Color1, Color2, 0),0,4);
    If Lag = 93 Then Plot94(93, "S93", RGB(Color1, Color2, 0),0,4);
    If Lag = 94 Then Plot95(94, "S94", RGB(Color1, Color2, 0),0,4);
    If Lag = 95 Then Plot96(95, "S95", RGB(Color1, Color2, 0),0,4);
    If Lag = 96 Then Plot97(96, "S96", RGB(Color1, Color2, 0),0,4);
    If Lag = 97 Then Plot98(97, "S97", RGB(Color1, Color2, 0),0,4);
    If Lag = 98 Then Plot99(98, "S98", RGB(Color1, Color2, 0),0,4);
End;
```

## UltimateSmoother Function, In EasyLanguage Code

```easylanguage
{
    Ultimate Smoother Function
    (C) 2004-2024 John F. Ehlers
}
Inputs:
    Price(numericseries),
    Period(numericsimple);

Vars:
    a1(0),
    b1(0),
    c1(0),
    c2(0),
    c3(0),
    US(0);

a1 = expvalue(-1.414*3.14159 / Period);
b1 = 2*a1*Cosine(1.414*180 / Period);
c2 = b1;
c3 = -a1*a1;
c1 = (1 + c2 - c3) / 4;

If CurrentBar >= 4 Then
    US = (1 - c1)*Price + (2*c1 - c2)*Price[1] - (c1 + c3)*Price[2] + c2*US[1] + c3*US[2];
If CurrentBar < 4 Then US = Price;

$UltimateSmoother = US;
```

## About the Author

John Ehlers is a retired electrical engineer and a retired technical analyst, specializing in the application of DSP (digital signal processing) to trading. For more information, see [www.mesasoftware.com](www.mesasoftware.com).

## Further Reading

- Ehlers, John [2024]. "The Ultimate Smoother," *Technical Analysis of STOCKS & COMMODITIES*, Volume 42: April.
- Ehlers, John [2021]. "Windowing," *Technical Analysis of STOCKS & COMMODITIES*, Volume 39: September.
- Ehlers, John [2004]. *Cybernetic Analysis For Stocks And Futures*, John Wiley & Sons.
- Ehlers, John [2013]. *Cycle Analytics For Traders*, John Wiley & Sons.

---

The code given in this article is available in the Article Code section of the Traders.com website. See the Traders' Tips coding section of the magazine beginning on page 44 for implementation of John Ehlers' technique in various technical analysis programs and trading platforms.

---

## BibTeX

```bibtex
@article{ehlers2025drunkards,
  author  = {Ehlers, John F.},
  title   = {Drunkard's Walk: Theory and Measurement by Autocorrelation},
  journal = {Technical Analysis of Stocks \& Commodities},
  year    = {2025},
  volume  = {43},
  number  = {2},
  pages   = {8--15},
  month   = feb,
  url     = {https://technical.traders.com/archive/article.asp?file=\V43\C02\910EHLE.pdf}
}

@misc{traderstips2025feb,
  title        = {Traders' Tips},
  year         = {2025},
  month        = feb,
  journal      = {Technical Analysis of Stocks \& Commodities},
  volume       = {43},
  number       = {2},
  howpublished = {Online},
  url          = {https://www.traders.com/Documentation/FEEDbk_docs/2025/02/TradersTips.html},
  note         = {Implementations of Ehlers' Autocorrelation indicator in various platforms}
}
```
