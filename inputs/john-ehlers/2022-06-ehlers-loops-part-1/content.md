# Ehlers Loops, Part 1

**Rotation In Motion**

*by John F. Ehlers*

> Introducing a new way to discretionarily predict bullish and bearish moves in the market.

## Introduction

"Volume leads price" is a philosophical dogma that has been part of technical analysis forever. In this article, I will examine the relationship between volume and price of a stock to see if there is any predictive value gained by including volume in the analysis.

I, frankly, have had a hard time seeing a relationship between volume and price. Perhaps that is because I have been primarily a commodity and futures trader, and futures are used for hedging as well as for speculation. Or perhaps it is because I have seen a greater correlation on the price of intraday futures to time of day rather than to volume. Ben Crocker invented Crocker charts in the 1950s to try to make some sense of volume-price relationships. These charts plotted price on the vertical axis versus volume on the horizontal axis, and the points were connected as a function of time. The result was a jumble of scratches that have been described to look like a child's Etch-A-Sketch. However, the charts often resembled a jumbled pile of "pick-up sticks" and were difficult to interpret. Crocker charts never became popular because of the difficulty in interpreting them.

## Volume Relationships

There are many mind-numbing descriptions of the relationships between volume and price. Most descriptions follow the principles of supply and demand, and many of the descriptions are contradictory. There are four conditions where there is general agreement. These are:

1. **Increasing volume and increasing price is bullish.** Generally, this is considered a trend continuation condition. Plotted as price versus volume, this would be a vector from lower left to upper right.
2. **Decreasing volume and increasing price is bearish.** This is generally considered an extinguishing of demand. Plotted as price versus volume, this would be a vector from lower right to upper left.
3. **Decreasing volume and decreasing price is bullish.** This is generally considered an extinguishing of supply. Plotted as price versus volume, this would be a vector from upper right to lower left — exactly the opposite of the condition above.
4. **Increasing volume and decreasing price is bearish.** This is generally considered a continuation of a downtrend. Plotted as price versus volume, this would be a vector from upper left to lower right.

I don't necessarily ascribe to the rationale, but if these conditions are plotted sequentially 1-2-3-4 in a Crocker chart as a bull-bear type of cycle, the plot would be a diamond that has a counterclockwise rotation as a function of time, as shown in Figure 1. On the other hand, if the bull-bear cycle is plotted in the 1-4-3-2 vector sequence, the plot would be a diamond that has a clockwise rotation as a function of time, as shown in Figure 2.

![Figure 1: Crocker Chart, Counterclockwise Diamond Plot](assets/figure-1-crocker-counterclockwise.png)

**FIGURE 1: CROCKER CHART, COUNTERCLOCKWISE DIAMOND PLOT.** If you plot the bull and bear conditions from the above list in sequential order in a Crocker-style chart, you get a counterclockwise diamond shape. The direction of rotation is easily discernable and its motion is a predictor of future prices. However, Crocker charts are difficult to use.

![Figure 2: Crocker Chart, Clockwise Diamond Plot](assets/figure-2-crocker-clockwise.png)

**FIGURE 2: CROCKER CHART, CLOCKWISE DIAMOND PLOT.** If you plot the bull and bear conditions given in the list earlier in this article in the 1-4-3-2 sequence in a Crocker-style chart, you get a clockwise diamond shape. As in Figure 1, the direction of rotation is easily discernable and its motion is a predictor of future prices. However, Crocker charts are hard to use.

These directions of rotation are easily discernable, and further, their motion is a predictor of future prices. The problem is that the jumbled Crocker charts are hard to read.

## Introducing Ehlers Loops

Fortunately, modern computer technology and digital signal processing (DSP) make volume-price charts easy to read and enable these charts to be predictive of future prices. First, both price and volume are filtered to be band-limited signals (oscillators having a nominal zero mean). This is done by limiting the spectral content by filtering in a roofing filter. The roofing filter is comprised of a high-pass filter and a low-pass SuperSmoother filter. The high-pass filter conceptually eliminates all spectrum components whose wavelengths are longer than HPPeriod and passes all spectrum components whose wavelengths are shorter than HPPeriod. The low-pass SuperSmoother filter conceptually passes all spectrum components whose wavelengths are longer than LPPeriod and eliminates all spectrum components whose wavelengths are shorter than LPPeriod. The result is a relatively wide bandwidth carrying the desired data wavelengths appropriate for trading.

The price- and volume-filtered data are both scaled in terms of standard deviations by dividing each by their respective RMS values. The resultant price-volume plots are *Ehlers Loops*, where the trader can trace the history of their relationship and can extend the direction of the plots to form a prediction.

## How They Work

Since both price and volume are plotted in standard deviations, the plots are consistently interpreted when the trader moves from one symbol to another. It is worthy of note there is a 68% probability of reversal at one standard deviation, 95% probability of reversal at two standard deviations, and a 99.7% probability of reversal at three standard deviations. Recognizing these probabilities will help you predict upcoming reversals in either volume or price.

Ehlers Loops are best explained by example. Figure 3 shows the progress of the price-volume Ehlers Loops of FedEx for three months in 2021. The LPPeriod was set to 10 to obtain minimum lag with just a little smoothing. The HPPeriod was set to 125 (a half year) to capture the longer-term moves. The loop plot starts on September 1. By September 9 there was a sharp volume reversal, starting a clockwise loop. However, there was no clear price direction. By September 20 the clockwise rotation continued, giving a bearish outlook. By September 27 the volume reverses at a value over three standard deviations. But the clockwise rotation continues, signaling a continued bearish outlook. By October 1, prices were near negative two standard deviations, giving a bullish outlook because of the continued clockwise rotation. Prices did, indeed, increase through October. But by November 3 there was a small whifferdill where a counterclockwise rotation had started. This put up flags that a price top was in the near future. However, the clockwise rotation resumed, giving a bearish outlook on November 12. Indeed, prices continued to fall through the rest of November.

From this brief description, and by comparing the Ehlers Loop to the actual FedEx prices for the three-month period, you can see that the Ehlers Loop is predictive of future prices.

![Figure 3: Ehlers Loop, FDX](assets/figure-3-ehlers-loop-fdx.png)

**FIGURE 3: EHLERS LOOP.** This shows an example of an Ehlers Loop of FedEx (FDX) for three months in 2021. The loop plot starts on September 1. By September 9 there was a sharp volume reversal, starting a clockwise loop.

## Charting Ehlers Loops

Ehlers Loops are created by first filtering, scaling, and plotting price and volume as conventional indicators. In addition, the date of each data point, the price, and the volume are output to a text file. That text file is then read by Excel. The volume and price in columns B and C, respectively, are then plotted as a scatterplot for the selected timespan. The appearance of the Ehlers Loops can be altered by changing the LPPeriod and HPPeriod input parameters. If the difference between the two inputs is large, then a wide range of data cycle components are included in the analysis. This can result in whifferdills in the loops because of the multiple frequencies in the data. This effect can be reduced by reducing the difference between HPPeriod and LPPeriod. I suggest making the difference more than 20 percent of their average value because a too-narrow bandwidth can cause "tunnel vision" at a single component of the spectrum. Reducing the value of LPPeriod reduces the lag of the indicator, but it also reduces its smoothness. Increasing the value of HPPeriod includes more of the longer wavelength trending components.

The values of HPPeriod and LPPeriod can be customized to your trading style. For example, if your desired holding time for a trade position is 20 days (about one month) you would want the average of HPPeriod and LPPeriod to be about 40 bars. That is because the time between a 40-bar cycle valley and its peak is 20 bars. 20% of 40 bars is 8 bars, so setting LPPeriod to 35 and HPPeriod to 45 is in the right ballpark for your trading style.

The code to generate the Ehlers Loops is shown in the sidebar "Ehlers Loops, In EasyLanguage." After declaration of variables, the coefficients for the high-pass and SuperSmoother filters are calculated only on the first bar of data for computational efficiency. Then, both price and volume are filtered individually in identical filters. As a result, both are band-limited signals having a nominal zero mean. Their RMS (root mean square) values are computed as EMAs of their squares, and the EMA coefficient of 0.0242 corresponds to a critical period of one year. Dividing each by their RMS values scales them to both be plotted in terms of standard deviations.

The filtered and scaled values of volume and price are conventionally plotted. In addition, their values are exported to a text file so that the Ehlers Loops can be plotted using Excel. Several precautions regarding the text file should be taken. First, your computer must have a C:\Temp folder to contain the exported text file. Second, the Excel file cannot be open during live trading because trying to write to an open file will crash the indicator.

To plot Ehlers Loops in Excel, simply highlight columns B and C for the desired date range and click on *insert* and choose "scatter plot with smooth lines and indicators."

## Predicting With Ehlers Loops

So there you have it. Ehlers Loops are a new way to discretionarily predict bullish and bearish moves based on the curvature and direction of rotation of motion as a function of time in the price-volume chart. It is worth remembering that a price move greater than one or two standard deviations means there is a high probability of a reversal.

Next time, I'll provide an example of using Ehlers Loops with a pairs trading method. Stay tuned!

## Takeaways

1. Ehlers Loops are a tool to discretionarily predict price movement based on the curvature and direction of rotation in a price versus volume chart.
2. Both volume and price are individually filtered in identical highpass and SuperSmoother filters to become band-limited signals with a nominal zero mean.
3. Both volume and price are scaled in terms of standard deviations.
4. The shape of the Ehlers Loops can be modified by changing the LPPeriod and HPPeriod of the data filters.
5. Decreasing the value of LPPeriod reduces lag and also reduces the smoothness of the filtered output.
6. Increasing the value of HPPeriod increases the contribution of longer wave components in the data.
7. The difference between HPPeriod and LPPeriod should not be less than 20 percent of their average value.

---

## About the Author

John Ehlers, a Contributing Editor to Stocks & Commodities, is a pioneer in the use of cycles and DSP (digital signal processing) technical analysis. He is president of MESA Software. He can be reached through his website at [MESAsoftware.com](http://www.mesasoftware.com).

The code given in this article is available in the Article Code section of our website, Traders.com.

See our Traders' Tips section beginning on page 48 for implementation of John Ehlers' technique in various technical analysis programs and trading platforms. Accompanying program code can be found in the Traders' Tips area at Traders.com.

## Further Reading

- Ehlers, John F. [2014]. "Predictive And Successful Indicators," *Technical Analysis of Stocks & Commodities*, Volume 32: January.

---

## Ehlers Loops, In EasyLanguage

```easylanguage
{
    Ehlers Loops
    (C) 2005-2022 John F. Ehlers
}

Inputs:
    LPPeriod(20),
    HPPeriod(125);

Vars:
    hpa1(0),
    hpb1(0),
    hpc1(0),
    hpc2(0),
    hpc3(0),
    ssa1(0),
    ssb1(0),
    ssc1(0),
    ssc2(0),
    ssc3(0),
    HP(0), VolHP(0),
    Price(0), PriceMS(0), PriceRMS(0),
    Vol(0), VolMS(0), VolRMS(0);

If CurrentBar = 1 Then Begin
    hpa1 = expvalue(-1.414*3.14159 / HPPeriod);
    hpb1 = 2*hpa1*Cosine(1.414*180 / HPPeriod);
    hpc2 = hpb1;
    hpc3 = -hpa1*hpa1;
    hpc1 = (1 + hpc2 - hpc3) / 4;
    ssa1 = expvalue(-1.414*3.14159 / LPPeriod);
    ssb1 = 2*ssa1*Cosine(1.414*180 / LPPeriod);
    ssc2 = ssb1;
    ssc3 = -ssa1*ssa1;
    ssc1 = 1 - ssc2 - ssc3;
End;

//Normalized Roofing Filter for Price
// 2 Pole Butterworth Highpass Filter
HP = hpc1*(Close - 2*Close[1] + Close[2]) + hpc2*HP[1] +
    hpc3*HP[2];
If CurrentBar < 3 Then HP = 0;

// Smooth with a Super Smoother Filter
Price = ssc1*(HP + HP[1]) / 2 + ssc2*Price[1] + ssc3*Price[2];
If CurrentBar < 3 Then Price = 0;

//Scale Price in terms of Standard Deviations
If CurrentBar = 1 then PriceMS = Price*Price Else PriceMS =
    .0242*Price*Price + .9758*PriceMS[1];
If PriceMS <> 0 Then PriceRMS = Price / SquareRoot(PriceMS);

//Normalized Roofing Filter for Volume
// 2 Pole Butterworth Highpass Filter
VolHP = hpc1*(Volume - 2*Volume[1] + Volume[2]) +
    hpc2*VolHP[1] + hpc3*VolHP[2];
If CurrentBar < 3 Then VolHP = 0;

// Smooth with a Super Smoother Filter
Vol = ssc1*(VolHP + VolHP[1]) / 2 + ssc2*Vol[1] + ssc3*Vol[2];
If CurrentBar < 3 Then Vol = 0;

//Scale Vol in terms of Standard Deviations
If CurrentBar = 1 then VolMS = Vol*Vol Else VolMS =
    .0242*Vol*Vol + .9758*VolMS[1];
If VolMS <> 0 Then VolRMS = Vol / SquareRoot(VolMS);

//Conventional Plots
Plot1(PriceRMS, "", red, 4, 4);
Plot2(0, "", white, 1, 1);
Plot3(VolRMS, "", yellow, 4, 4);

//Output to Text File
Print(File("c:\Temp\EhlersLoops.csv"), Date, ",", VolRMS, ",",
    PriceRMS);
```

---

## References

- **Article URL:** <https://technical.traders.com/archive/article.asp?file=\V40\C06\435EHLE.pdf>
- **Traders' Tips URL:** <https://www.traders.com/Documentation/FEEDbk_docs/2022/06/TradersTips.html>

```bibtex
@article{ehlers2022ehlers_loops,
  author    = {Ehlers, John F.},
  title     = {Ehlers Loops, Part 1},
  journal   = {Technical Analysis of Stocks \& Commodities},
  volume    = {40},
  number    = {6},
  pages     = {8--13},
  year      = {2022},
  month     = jun,
  url       = {https://technical.traders.com/archive/article.asp?file=\V40\C06\435EHLE.pdf}
}

@misc{ehlers2022ehlers_loops_tips,
  author    = {Ehlers, John F.},
  title     = {Traders' Tips: Ehlers Loops},
  year      = {2022},
  month     = jun,
  howpublished = {Technical Analysis of Stocks \& Commodities},
  url       = {https://www.traders.com/Documentation/FEEDbk_docs/2022/06/TradersTips.html}
}
```
