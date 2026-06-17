# Correlation as a Cycle Indicator

**By John F. Ehlers**

- **Downloaded from:** [Mesa Software — CORRELATION AS A CYCLE INDICATOR](https://www.mesasoftware.com/papers/CORRELATION%20AS%20A%20CYCLE%20INDICATOR.pdf)

---

The general purpose of correlation is to ascertain the relationship between two functions. I have previously described how a trend indicator can be developed by correlating prices with a straight line having a positive slope.[^1] It turns out that a cycle indicator can be developed by correlating prices to a Cosine wave over the full wavelength of the selected period.

When designing indicators and strategies, it is my approach to first test them using deterministic waveforms. After all, if an indicator doesn't work where you know the correct answer then why would you expect it to work on a noisy waveform of real data? Figure 1 shows the input waveform in blue as a 20 bar sinusoid. When correlated with a 20 bar Cosine wave, the "indicator" output is shown in red. The indicator correlation is so good that its plot covers the plot of the input data. The input data is really there. You can see this by tuning the input data to a 21 bar sinusoid while keeping the Cosine correlation function period at 20 bars, as I have done in Figure 2. The main point is that correlation of price against a Cosine wave gives an indicator that is exactly in phase with the cycle component in the data. In this sense, there is no lag.

![Figure 1: Correlating Data Sinusoid with Cosine Wave](assets/fig-01.png)
**Figure 1. Correlating a Data Sinusoid with a Cosine Wave Produces an Indicator that is In Phase with the Data.**

![Figure 2: Detuning the Input Data](assets/fig-02.png)
**Figure 2. Detuning the Input Data Shows it is Really There**

Market data is neither purely cyclic, nor is it statistically stationary. Therefore the assumption of a fixed cycle period for the indicator is bound to be incorrect to some degree most of the time. Since we are using deterministic waveforms we can perform a stress test on the indicator to see just how bad the results can be if the selected cycle period is in error. Figure 3 shows the results if the data has a 50% longer period than the assumed cycle period. That is, the indicator Cosine period is retained at 20 bars and the period of the input sinusoid is 30 bars. The result is that this indicator results in a leading phase error of less than 45 degrees. The practical ramification is that you will be getting in early on trades where the data cycle period is longer than the assumed cycle period.

![Figure 3: 50% Shorter Tuning Error Phase Lead](assets/fig-03.png)
**Figure 3. 50% Shorter Tuning Error Results in a Phase Lead Less than 45 degrees.**

Continuing the stress test, I set the input cycle period to be 25% shorter than the assumed period of the Cosine. That is, the indicator Cosine period is retained at 20 bars and the period of the input sinusoid is 15 bars. The results of this stress test is shown in Figure 4. In this case the lagging phase error is less than 45 degrees also. For the record, testing with a cycle period 50% shorter doesn't make any sense because a 10 bar cycle is a harmonic of the 20 bar cycle, and one gets a perfect result with this combination.

![Figure 4: 25% Longer Tuning Error Phase Lag](assets/fig-04.png)
**Figure 4. 25% Longer Tuning Error Results in a Phase Lag Less than 45 degrees.**

The main point of the cycle tests is that they prove that the Cycle Correlation Indicator does not fall apart even when the assumed cycle period is in error.

## Rate of Change

When dealing with a cycle indicator, the best trade entry point for a long position is at the exact valley of the waveform. It is often difficult to locate the valley with precision. Mathematically, the valley of the waveform occurs when its rate of change is zero, going from negative to positive. The rate of change is analogous to taking the derivative in calculus, with the result that the rate of change waveform is much noisier than the original waveform. Since we are in the cycle domain, there is a better method to achieve the rate of change function.

Noting that the derivative of a Cosine wave is a negative Sine wave, we can create a de facto Rate-Of-Change Indicator by correlating the input data with a negative Sine wave having the same period as with the original correlation. Figure 5 shows that this Rate-Of-Change Indicator (in green) has an exact 90 degree phase lead compared with the original indicator output. Leading by 90 degrees means that the green line crosses over zero when the original indicator (in red) is at a cycle valley and it crosses under zero when the original indicator is at a cycle peak. Therefore, the zero crossings of the Rate-Of-Change Indicator provide precise timing for entries and exits of cyclic-based trades.

![Figure 5: Rate of Change Zero Crossings Identify Peaks and Valleys](assets/fig-05.png)
**Figure 5. Zero Crossings of the Rate Of Change Indicator Precisely Identify Cycle Peaks and Valleys**

## Real World Example

Performance of the Cycle Indicator and its Rate of Change are shown in Figure 6. The use of real input data is facilitated by setting the Input Period parameter of the Indicator to zero. I used a 14 bar period for the Cosine period because I prefer to have a leading phase error for the cycle components in the real world data. The picture is not nearly as idyllic as the theoretical examples. This is partially because I purposely did not cherry pick a glowing example. However, even with this poor cycle example, the cyclic turning points can be correctly identified by lining up the peaks and valleys of the indicator (the red line) with the short term peaks and valleys in the price.

![Figure 6: Cycle Indicator on One Year SPY Data](assets/fig-06.png)
**Figure 6. Cycle Indicator Applied to One Year of SPY Data**

Most noticeably, the Rate-Of-Change Indicator (in green) fails when the market goes into a trend. It is also worthy of note that the Cycle Indicator is at a peak when the Rate-Of-Change Indicator crosses under zero fail spectacularly at the beginning of the major trends.

Rather than discarding the indicator as a failure in the real world, a new and unique opportunity unfolds.

## Cycle Mode and Trend Mode

Trend indicators typically have substantial lag, so a trader does not get an indication of the trend until the trend is well established. The result of this lag is a loss of potential profit in following that trend. Cycle indicators react rapidly, but as we have seen, they fail when the market goes into a trend. If we construct an idealized model of the market such that it consists of only a trend mode and a cycle mode, then a trend mode can be rapidly identified as a failure of the cycle mode. That will be my objective in the following paragraphs.

One definition of a cycle uses its rate-change of phase. For example, a 20 bar cycle period has an 18 degree rate of change per sample so that it completes 360 degrees of phase rotation each cycle period. It is convenient to think of a cycle in terms of the phasor diagram shown in Figure 7. The phasor arrow is anchored at the origin and sweeps out a cycle over one full counter clockwise rotation, and the next cycle period starts with the next rotation. Where one begins and ends a cycle is a matter of convention, but can occur at any phase angle. The time domain signal in the left half of Figure 7 is shown as the projection of the phasor on its vertical axis.

![Figure 7: Phasor Diagram](assets/fig-07.png)
**Figure 7. A Phasor Describes Cycle Phase in Terms of Orthogonal Components**

The phasor can also be described in terms of its orthogonal components. The projection of the phasor rotating at a constant rate onto the horizontal, or Real, axis is a Cosine. The projection of the phasor onto the vertical, or Imaginary, axis is a Sine. It follows that if we have the correlation of the data to a Cosine and also to Sine we can compute the phase angle of the Phasor. The phase angle is computed as the arctangent of the ratio of the real component to the imaginary component. Since the arctangent works only over a 180 degree span, the 360 degree picture of the phasor must be completed by resolving the ambiguity in two of the four quadrants. The theoretical phase angle for a 20 bar Sine wave is shown in Figure 8. The plot ranges from -180 degrees to +180 degrees, whereupon the phase wraparound is conducted and the next cycle is plotted. In reality, the rate change of phase is continuous, but a continuous rate of change is difficult to plot.

When the phase angle is above zero the theoretical Sine wave is descending from the cycle peak to the cycle valley. That is, at a phase angle of zero the Sine wave is at its maximum. When the phase angle is +180 degrees the Sine wave is at its minimum. Correspondingly, when the phase angle is below zero the theoretical Sine wave is ascending from the cycle valley to the cycle peak. That is, at a phase angle of -180 degrees the Sine wave is at its minimum, and when the phase angle is zero degree the Sine wave is at its maximum. The implication of this is that when the market is in a cycle mode you want to be in a long position if the angle is less than zero and you want to be in a short position if the angle is greater than zero.

![Figure 8: Phasor Angle Range](assets/fig-08.png)
**Figure 8. Phasor Angle Ranges from -180 to +180 degrees.**

Just as time cannot go backwards, the phase angle of the phasor cannot go backwards. Therefore, the computed phase angle is not allowed to regress in the code. In this case the phase angle is held at a constant value to indicate the cycle mode failure. So, when the phase display "flatlines" (i.e. the angle at the current data sample is the same as the angle at the previous data sample) the interpretation is that the cycle mode has failed and therefore the market is now in a trend mode. Further, since the indicator is dead wrong in the case of cycle mode failure, the correct position is to establish a short trend mode position when the phase angle flatlines below zero and to establish a long trend mode position when the phase angle flatlines above zero. An early indication of the end of a trend is given when the phase angle ceases to flatline.

The Phasor Indicator for the real world SPY example is shown in Figure 9. This presentation makes it simple to identify trend modes and cycle modes as well as the correct trade position for the given market conditions.

![Figure 9: Phasor Display](assets/fig-09.png)
**Figure 9. The Phasor Display Provides an Early Indication of Trend Onset and Trend Termination**

## State Variable

The very definition of a trend mode and a cycle mode makes it simple to create a state variable that identifies the market state. If the state is zero, the market is in a cycle mode. If the state is +1 the market is in a trend up. If the state is -1 the market is in a trend down. The state variable for the angle presentation of Figure 9 is given in Figure 10.

A trend can also be declared if the measured cycle period is too long to be traded in the cycle mode. I have arbitrarily decided that cycles having a 40 bar period or longer should be treated as trends. A 40 bar cycle period has a phase rate of change of 9 degrees per bar, so phase rate-changes less than this amount are classified as trends.

![Figure 10: State Variable](assets/fig-10.png)
**Figure 10. The State Variable Shows the Occurrences of the Cycle Mode, Trend up Mode, and Trend Down Mode.**

## Code

In my mind, computer code describes the computational process far more precisely than English, and I try to write code in a straightforward and easy to understand format. The code for all the indicators described in this article are given in Code Listing 1. If a particular display is not desired, simply comment out the display line of code.

## Conclusions

Correlation as a cycle indicator is robust, yielding only relatively small errors even if an incorrect judgement is made in assigning the dominant cycle to the indicator. Orthogonal component correlations can be made to enable precise identification of the correct trade entry and exit points. However, the cycle mode indicator fails when the market enters a trend mode. But that failure can be used to rapidly identify the current market mode. The Phasor angle display indicates the correct trade position for either the cycle mode or the trend mode.

The Phasor angle display is a departure from conventional indicators and requires traders to have situational awareness at the concept level. A further advantage of the Phasor angle display is that two orthogonal (i.e. independent) components are used in its construction. Since it has two independent signal inputs, the resulting indicator has a 6 dB Signal to Noise advantage over conventional squiggly line indicators.

### Code Listing 1. EasyLanguage Code for Correlation Cycle

```easylanguage
{
Correlation Angle Indicator
(C) 2013-2019 John F. Ehlers
}
Inputs:
Period(20),
InputPeriod(20); //Uses price data if InputPeriod is set to 0

Vars:
Length(20), Price(0),
Sx(0), Sy(0), Sxx(0), Sxy(0), Syy(0), count(0), X(0), Y(0),
Real(0), Imag(0),
Angle(0),
State(0);

//Correlate over one full cycle period
Length = Period;
Price = Close;

//Creates a theoretical sinusoid having a period equal to the Input Period as the data input
If InputPeriod <> 0 Then Price = Sine(360*CurrentBar / InputPeriod);

//Correlate Price with Cosine wave having a fixed period
Sx = 0;
Sy = 0;
Sxx = 0;
Sxy = 0;
Syy = 0;
For count = 1 to Length Begin
    X = Price[count - 1];
    Y = Cosine(360*(count - 1) / Period);
    Sx = Sx + X;
    Sy = Sy + Y;
    Sxx = Sxx + X*X;
    Sxy = Sxy + X*Y;
    Syy = Syy + Y*Y;
End;
If (Length*Sxx - Sx*Sx > 0) and (Length*Syy - Sy*Sy > 0) Then
    Real = (Length*Sxy - Sx*Sy) / SquareRoot((Length*Sxx - Sx*Sx)*(Length*Syy - Sy*Sy));

//Correlate with a Negative Sine wave having a fixed period
Sx = 0;
Sy = 0;
Sxx = 0;
Sxy = 0;
Syy = 0;
For count = 1 to Length Begin
    X = Price[count - 1];
    Y = -Sine(360*(count - 1) / Period);
    Sx = Sx + X;
    Sy = Sy + Y;
    Sxx = Sxx + X*X;
    Sxy = Sxy + X*Y;
    Syy = Syy + Y*Y;
End;
If (Length*Sxx - Sx*Sx > 0) and (Length*Syy - Sy*Sy > 0) Then
    Imag = (Length*Sxy - Sx*Sy) / SquareRoot((Length*Sxx - Sx*Sx)*(Length*Syy - Sy*Sy));

//Compute the angle as an arctangent function and resolve ambiguity
If Imag <> 0 Then Angle = 90 + Arctangent(Real / Imag);
If Imag > 0 Then Angle = Angle - 180;

//Do not allow the rate change of angle to go negative
If Angle[1] - Angle < 270 and Angle < Angle[1] Then Angle = Angle[1];

//Plot1(Real);
Plot4(0);
//Plot3(Imag);
Plot2(Angle);
//If InputPeriod <> 0 Then Plot6(Price);

//Compute and plot market state
State = 0;
If AbsValue(Angle - Angle[1]) < 9 and Angle < 0 Then State = -1;
If AbsValue(Angle - Angle[1]) < 9 and Angle >= 0 Then State = 1;
//Plot10(State);
```

[^1]: John F. Ehlers, "Correlation as a Trend Indicator", *Stocks & Commodities Magazine*

---

## BibTeX

```bibtex
@misc{ehlers_correlation_cycle_indicator,
  author       = {John F. Ehlers},
  title        = {Correlation as a Cycle Indicator},
  year         = {2020},
  howpublished = {online},
  url          = {https://www.mesasoftware.com/papers/CORRELATION%20AS%20A%20CYCLE%20INDICATOR.pdf}
}
```
