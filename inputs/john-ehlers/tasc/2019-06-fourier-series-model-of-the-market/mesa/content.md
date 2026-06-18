# Fourier Series Model of the Market

**By John Ehlers**

- **Downloaded from:** [Mesa Software — FOURIER SERIES MODEL OF THE MARKET](https://www.mesasoftware.com/papers/FOURIER%20SERIES%20MODEL%20OF%20THE%20MARKET.pdf)

---

Even the most casual observer will note that cycles are present in market data. Since this is so obvious, it is natural to try to imbed the analysis of these cycles in trading strategies to make them better and more profitable. The purpose of this article is to describe such analysis.

In his seminal 1970 book "The Profit Magic of Stock Transaction Timing", J.M. Hurst described five principles when dealing with periodic-cyclic motion. These were:

1. The Summation Principle
2. The Commonality Principle
3. The Variation Principle
4. The Nominality Principle
5. The Proportionality Principle

Addressing these principles in reverse order, the proportionality principle simply states that the longer the duration of the cycle component, the larger its magnitude. The modern description of this principle is that the market data is fractal. In fact, this principle causes problems with cycle measurements because most measurements do not account for this effect that I call spectral dilation. This principle is more statistical in nature and is not absolutely true all the time. The Fourier Series model I propose dynamically accounts for the relative amplitudes of the cyclic components.

The Nominality Principle reflects that some cyclic components tend to be consistently present. For example, I have found that most stocks and stock indexes tend to have a monthly, or 20 bar, cycle of daily data. I don't like to assign causality, but it makes sense because all management, from bottom to top, usually have to make their numbers on a monthly basis. It is not hard to imagine that this management imperative is reflected in the stock prices.

The Variation Principle means that the cycles in the data are not absolutely stable. The duration of their cycle periods, their amplitudes, and their phases shift as a function of time. After all, if cycles were consistently present every trader in the world would jump on them. The fact that they are so recognizable, in effect, makes them self destructive.

The Commonality Principle simply means the cyclic components in different stock ticker symbols tend to have similar durations and the highs and lows tend to be in time synchronization. This principle forms the basis of robustness test of a given trading strategy. If a strategy works well on one stock symbol, it should also work well on another similar stock if that strategy is to be robust.

The Summation Principle is a restatement of the theory of Fourier Series. That is, any arbitrary waveshape can be created by a sum of harmonics of sine wave primitives. Hurst goes on in detail on how to synthesize patterns such as double tops, double bottoms, head and shoulders, and flags and pennants from their sine wave primitives.

As a quick review of Fourier Series synthesis of waveshapes I will show a few simple examples. For example, consider the expression y = sin(x) + 0.33*sin(3x), where the angle arguments are in radians. This expression plots out to be alternating double top and double bottom pattern shapes, as shown in Figure 1. So, using the Variation Principle, these patterns can come and go as a function of time.

![Figure 1: Synthesized Double Tops and Double Bottoms](assets/fig-01.png)
**Figure 1. Synthesized Double Tops and Double Bottom Patterns**

Head and Shoulders patterns can be synthesized from sine wave harmonics with a minor variation of the previous expression as y = sin(x) + 0.1*sin(3x) + 0.2*sin(5x). This expression plots the alternating direct and inverse head and shoulders patterns as shown in Figure 2.

![Figure 2: Synthesized Head and Shoulders Patterns](assets/fig-02.png)
**Figure 2. Synthesized Head and Shoulders Patterns**

Even an Elliott Wave pattern can be synthesized from sine wave primitives through the use of the equation y = sin(x) - 0.5*sin(2x) + 0.33*sin(3x). The resulting wave, with the basic wave count is shown in Figure 3.

![Figure 3: Synthesized Elliott Wave Pattern](assets/fig-03.png)
**Figure 3. Synthesized Elliott Wave Pattern**

The synthesized patterns were plotted using a free graphics package that can be downloaded from http://www.graphmatica.com.

Synthesis of patterns using sine wave primitives is relatively easy. All one has to do is to follow the Summation principle using harmonics of various amplitudes and phase angles. Analysis of a pattern by breaking it down to its component sine wave primitives is another thing altogether. In theory there are a triple infinity of parameters to consider for each harmonic component. That is, one must determine the frequency, amplitude, and phase of each one. Further, according to the Variation Principle, the harmonic components are not time invariant. The problem of analyzing patterns in terms of their sine wave primitives seems to be virtually impossible.

However, truth and science again triumphs over ignorance and superstition. The technical tool that isolates each of the primitive components is a Band-Pass filter. A Band-Pass filter passes only the cycle period of interest and rejects all other frequency components that may be present in the data spectrum. The Band-Pass filter and its characteristics are described in Chapter 5 of my book[^1]. The Band-Pass filter isolates each of the harmonic components with their relative phases, and enables further measurement of their relative amplitudes.

There are tradeoffs in the use of the Band-Pass filter, as there are with most technical tools. In this case the tradeoff is between the bandwidth of the filter and the speed of its transient response. That is, if the filter bandwidth is designed to be too narrow, then the filter "rings out" like a bell and is slow to respond to changes in the input data. For this application, a reasonable compromise is to have the filter bandwidth be 10% of its center period. So, if the Band-Pass filter is tuned to a 20 bar cycle period, it will also pass spectral components having periods between 19 and 21 bars.

Since the harmonic components of the data spectrum can be isolated using Band-Pass filters, the seemingly impossible task of analyzing market data using a truncated Fourier Series analysis can be accomplished using a precise algorithmic sequence. The steps of this sequence are:

1. Select a fundamental cycle period.
2. Precisely measure the fundamental, and second and third harmonics in narrow band Band-Pass filters. The relative phases of these sine wave primitives are determined by the measurement.
3. Determine the relative amplitude of the three cyclic components
4. Following the Principle of Summation, add the three harmonic components together using their relative amplitudes.
5. Repeat for each bar across the chart.

These steps will produce a smooth time-variable pattern that describes market activity in direct synchronization with the price action of the market. The waveform is smooth because only the three harmonic sine wave components are used, and the extraneous noisy components are ignored. You can then use this smoothed waveform as the basis for realistic trading strategy rules.

The details of the algorithmic sequence are described in terms of the EasyLanguage code given in Code Listing 1. The Fundamental period is an input and the default value of 20 bars is used. The variables are declared, and then all the filter coefficients are computed on the first bar of the chart for execution efficiency because they do not change across the chart. In the next block of code the Band-Pass filters for the fundamental, and second and third harmonics are computed, as well as the quadrature components.

The quadrature components (Q1, Q2, and Q3) are generated by taking the one bar difference of their respective Band-Pass filter response. This is analogous to taking their derivative in calculus. Recalling that the derivative of a sine wave is a cosine wave as d(sin(omega*t))/dt = (1/omega)*cos(omega*t), then taking the derivative produces a 90 degree shift (i.e. quadrature of a cycle) of the same waveform with an amplitude adjustment. Since the Band-Pass filters have a relatively narrow bandwidth, we can treat this adjustment as the Fundamental period divided by 2*Pi.

The quadrature components are required to measure the amplitudes of the fundamental and two harmonic waves. Using the trigonometric relationship 1 = sin²(x) + cos²(x), we can find the power in the wave as the sum of the squares of the in-phase and quadrature components. The power in the second and third harmonic waves are correctly computed because they are summed over two and three cycle periods, respectively, when the power is averaged over the fundamental cycle period.

Finally, the waveform is synthesized by adding the second and third harmonics at their relative amplitudes to the filtered fundamental signal.

The additional optional code, which is currently commented out, creates a trading signal as the Rate Of Change (ROC) of the Wave. This signal crosses zero each time the wave attains a peak or valley. So, if the amplitude of the swing is adequate, the ROC crossing zero is an excellent time to enter or exit a swing trade.

### Code Listing 1. Fourier Series Analysis

```easylanguage
{
Fourier Series Analysis
(C) 2005-2018 John F. Ehlers
}
Inputs:
Fundamental(20);

Vars:
Bandwidth(.1),
G1(0), S1(0), L1(0), BP1(0), Q1(0), P1(0),
G2(0), S2(0), L2(0), BP2(0), Q2(0), P2(0),
G3(0), S3(0), L3(0), BP3(0), Q3(0), P3(0),
count(0),
Wave(0),
ROC(0);

//compute filter coefficients once
If CurrentBar = 1 Then Begin
    L1 = Cosine(360 / Fundamental);
    G1 = Cosine(Bandwidth*360 / Fundamental);
    S1 = 1 / G1 - SquareRoot(1 / (G1*G1) - 1);

    L2 = Cosine(360 / (Fundamental / 2));
    G2 = Cosine(Bandwidth*360 / (Fundamental / 2));
    S2 = 1 / G2 - SquareRoot(1 / (G2*G2) - 1);

    L3 = Cosine(360 / (Fundamental / 3));
    G3 = Cosine(Bandwidth*360 / (Fundamental / 3));
    S3 = 1 / G3 - SquareRoot(1 / (G3*G3) - 1);
End;

//Fundamental Band-Pass
BP1 = .5*(1 - S1)*(Close - Close[2]) + L1*(1 + S1)*BP1[1] - S1*BP1[2];
If CurrentBar <= 3 Then BP1 = 0;

//Fundamental Quadrature
Q1 = (Fundamental / 6.28)*(BP1 - BP1[1]);
If CurrentBar <= 4 Then Q1 = 0;

//Second Harmonic Band-Pass
BP2 = .5*(1 - S2)*(Close - Close[2]) + L2*(1 + S2)*BP2[1] - S2*BP2[2];
If CurrentBar <= 3 Then BP2 = 0;

//Second Harmonic Quadrature
Q2 = (Fundamental / 6.28)*(BP2 - BP2[1]);
If CurrentBar <= 4 Then Q2 = 0;

//Third Harmonic Band-Pass
BP3 = .5*(1 - S3)*(Close - Close[2]) + L3*(1 + S3)*BP3[1] - S3*BP3[2];
If CurrentBar <= 3 Then BP3 = 0;

//Third Harmonic Quadrature
Q3 = (Fundamental / 6.28)*(BP3 - BP3[1]);
If CurrentBar <= 4 Then Q3 = 0;

//Sum power of each harmonic at each bar over the Fundamental period
P1 = 0;
P2 = 0;
P3 = 0;
For count = 0 to Fundamental - 1 Begin
    P1 = P1 + BP1[count]*BP1[count] + Q1[count]*Q1[count];
    P2 = P2 + BP2[count]*BP2[count] + Q2[count]*Q2[count];
    P3 = P3 + BP3[count]*BP3[count] + Q3[count]*Q3[count];
End;

//Add the three harmonics together using their relative amplitudes
If P1 <> 0 Then
    Wave = BP1 + SquareRoot(P2 / P1)*BP2 + SquareRoot(P3 / P1)*BP3;

Plot1(Wave);
Plot2(0);

{
//Optional cyclic trading signal
//Rate of change crosses zero at cyclic turning points
ROC = (Fundamental / 12.57)*(Wave - Wave[2]);
Plot3(ROC);
}
```

It is imperative that a technical analysis indicator perform as expected on deterministic waveforms before it can be applied to noisy real-world data. Toward that end, I created a data signal consisting of the synthesized Elliott Wave pattern. The test is whether the Fourier Series indicator can accurately recreate that waveform at its output. Figure 4 shows that the Elliott Wave as the blue line is faithfully reproduced by the red line output of the indicator. It's not perfect, but it's pretty good. One potential cause of the error is the half bar of lag in the computation of the quadrature components, but this lag is not correctable. Figure 5 shows that the double tops and double bottoms as the blue line is also faithfully reproduced by the red line output of the indicator even though there is no second harmonic in the original signal.

![Figure 4: Fourier Series Indicator Replicates Elliott Wave](assets/fig-04.png)
**Figure 4. The Fourier Series Indicator Faithfully Replicates the Synthesized Elliott Wave**

![Figure 5: Fourier Series Indicator Replicates Double Tops and Bottoms](assets/fig-05.png)
**Figure 5. The Fourier Series Indicator Faithfully Replicates Double Tops and Double Bottoms**

The fun part is seeing how the Fourier Series Indicator works on real data. Figure 6 shows a little more than one year's worth of daily data on the symbol SPY. The Fourier Series Indicator is shown in the first subgraph below the price chart. From left to right, the market was in a trend mode in the Fall of 2017 into January of 2018. The indicator shows this by having very little swing amplitude. After an erratic period, a strong cycle mode was present from April 2018 through October 2018. Note that the peaks and valleys of the indicator align with the extreme swings in prices, showing there is predictive value in the indicator based on continuation of the cycle. The peaks and valleys of the indicator also tend to line up with the extreme swings during the volatile period in the Fall of 2018.

![Figure 6: Fourier Series Indicator on SPY](assets/fig-06.png)
**Figure 6. The Fourier Series Indicator Accurately Shows Trends As Well As Cyclic Turning Points.**

The Fourier Series Indicator gives a faithful and tradeable picture of market activity based on the five principles established by J.M. Hurst. It is made possible through the use of Band-Pass filters that isolate the fundamental and its second and third harmonics. The filter preserves their relative amplitudes and phases so that a truncated Fourier series can be established using the Summation Principle.

[^1]: John F. Ehlers, "Cycle Analytics for Traders", John Wiley & Sons, New York

---

## BibTeX

```bibtex
@misc{ehlers_fourier_series_model,
  author       = {John F. Ehlers},
  title        = {Fourier Series Model of the Market},
  year         = {2019},
  howpublished = {online},
  url          = {https://www.mesasoftware.com/papers/FOURIER%20SERIES%20MODEL%20OF%20THE%20MARKET.pdf}
}
```
