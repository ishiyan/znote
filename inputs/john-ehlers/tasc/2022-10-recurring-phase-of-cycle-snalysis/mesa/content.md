# Recurring Phase of Cycle Analysis

**By John Ehlers**

> Congratulations to S&C for 40 years of successfully bringing new technical concepts to traders.

- **Downloaded from:** [Mesa Software — Recurring Phase of Cycle Analysis](https://www.mesasoftware.com/papers/RECURRING%20PHASE%20OF%20CYCLE%20ANALYSIS.pdf)

---

## In the Beginning

Cycle Analysis for technical analysis has come a long way since your beginning because it was pretty primitive back then. J.M. Hurst[^1] had established that patterns such as double tops, head and shoulders, and even Elliot waves could be synthesized with just a few harmonics of a fundamental sine wave. Dr. Anthony Warren[^2] wrote some seminal articles in S&C about Fourier Analysis, demonstrating the duality between events in the time domain and their representation in the frequency domain. Engineer Jack Hutson, publisher of S&C, recognized the importance of cycle analysis and Fourier Transforms and encouraged research in this area. At the time, resolution in the frequency domain was relatively poor, but the peaks in the spectrum shapes could discern between long wavelength seasonal periods, intermediate length periods for trading, and short period random variations from the peaks in the spectrum shapes. So, the basic use of cycle analysis was to determine whether it was best to do trend trading or swing trading. Fast Fourier Transforms (FFT) were the technical rage back then, but were just not the right tool for technical analysis because of their resolution.

## Some Evolution of Technical Analysis

Maximum Entropy Spectral Analysis (MESA) was invented in 1976 for use in the exploration of oil. It could provide a high-resolution display from short burst seismic echoes. Recognizing the high-resolution capability had merit, I started using it in my personal Futures trading. Encouraged by Jack Hutson, I wrote several articles describing how MESA worked and what kind of performance it could deliver. As a result, MESA became popular among a few early adaptors. Consequently, I wrote more articles as PCs became more available and more capable.

In retrospect, I recall a funny footnote. MESA is computationally intensive. When programmed in BASIC on an Apple II computer a single analysis would take a very long time. Just to ensure the computer had not locked up, I mapped the computing registers to the display registers so you could watch the Apple II do its work. It was actually kind of cool. Today's computers can handle the MESA algorithm without even breaking sweat.

So MESA raised the bar for performance with regard to swing trading. The evolution through the years involved improved displays and improved timing signals for swing trading. The one constant throughout the evolution was the concept that happenings in the time domain are expressly tied to happenings in the frequency domain. Either description was a full and complete description of market activity. That relationship can be better understood with reference to Figure 1. In simplest terms, the time waveform is represented by a pure sine wave in the left-hand side of the Figure. It is also represented as a phasor in the right-hand side of the Figure. A phasor is a two-dimensional vector, pinned at the origin. Its rate of rotation is the frequency of the sine wave in the time domain. Its rotation starts at -180 degrees and advances to +180 degrees throughout the cycle period, whereupon the next cycle begins. The projection of the tip of the phasor onto the vertical axis as a function of time traces out the sine wave in the left side of the Figure. The projection of the phasor onto the horizontal axis as a function of time traces a cosine wave at the same time the projection onto the vertical axis produces a sine wave. The horizontal axis is called the Real axis and the vertical axis is called the Imaginary axis. It can be shown that the activity on the two axes are orthogonal. That is, they are statistically independent over the period of the cycle. The activity on the Real and Imaginary axes defines the phasor. When the phase angle of the phasor is -90 degrees the cycle is at its valley in the time domain. When the phase of the phasor is +90 degrees the cycle is at its peak in the time domain.

![Figure 1: Events Can Be Equally Represented in the Time Domain or the Frequency Domain](assets/fig-01.png)
**Figure 1. Events Can Be Equally Represented in the Time Domain or the Frequency Domain**

## A Current Approach

We can create the Real and Imaginary components of market data by correlating the market data with cosine and sine, respectively, of fixed cycle period. The wavelength of the fixed cycle period should be about mid-range of the spectrum components in the market data. The phase angle of the phasor is then easily computed as the arctangent of the ratio of the imaginary component to the real component. The computation is repeated for each bar in the data set. The precise computation in EasyLanguage is shown in Code Listing 1.

When the indicator of Code Listing 1 is applied to daily data for the stock symbol RTX, we get the display of Figure 2. The phasor is the red line in the first subgraph. The phasor starts at -180 degrees and advances through the cycle period until it reaches +180 degrees, whereupon it repeats with time. The valleys of the computed waveform are easily identified at -90 degrees, and the timing of the phase angle crossing -90 degrees can be compared to the valleys in the price waveform. Correspondingly, the peaks of the computed waveform are easily identified at +90 degrees, and the timing of the phase angle crossing +90 degrees can be compared to the peaks in the price waveform. Thus, the phase angle crossings of -90 and +90 degrees basically constitute buy and sell signals of a trading algorithm. Of course, these need to be trimmed in the real world. You want to hold a long position when the phase angle is between -90 degrees and +90 degrees. You want to hold a short position (or be out) when the phase angle is greater than +90 degrees or less than -90 degrees when you are swing trading.

![Figure 2: Measured Phasor](assets/fig-02.png)
**Figure 2. Measured Phasor Identifies Peaks and Valleys of Price**

Note that the period of the phasor is not the period of the fixed cycle period using in the correlation process. In fact, there are times when the phase is not advanced at all. When the cycle phase is not advancing the waveform is not cycling. If it is not cycling, it must be trending. Since the slope of the phasor is changing, the frequency of the spectrum must not be constant. Frequency is the rate-change of angle. For example, the dimension of cycles per second can also be expressed in terms of angles as 360\*rotations per second. Therefore, we can express the computed instantaneous period of the data as 360 divided by the rate-change of angle. The resulting derived period is shown in Figure 3. Instantaneous cycle periods are all over the place, which demonstrates the difficulties in cycle analysis. It is much more preferable to perform analyses in terms of phase angle rather than in terms of cycle period.

![Figure 3: Instantaneous Derived Cycle Periods](assets/fig-03.png)
**Figure 3. Instantaneous Derived Cycle Periods Are All Over the Place**

With reference to Code Listing 1, you can replicate the results shown in Figure 3 by commenting out the code block plotting the phase indicator (with curly brackets) and removing the curly brackets around the code block titled "Frequency derived from rate-change of phase".

So, when is the data trending? It is trending when it is not cycling. I have defined trending as occurring when the instantaneous period is longer than 60 days (about three months). This is also when the rate-change of angle is 6 degrees per bar or less. Trend rules are the opposite of swing rules. When trending, you want to be long when the phase angle is greater than +90 degrees or less than -90 degrees. You want to be short or out when the phase angle is between -90 degrees and +90 degrees. These rules can be used to create a state variable that is +1 for long positions, 0 for cycling, and -1 for short positions (or out). This state variable is shown in Figure 4. You can compare the timing of the +1 and -1 states with the trends in the price data.

![Figure 4: Trend State Variable](assets/fig-04.png)
**Figure 4. Trend State is Long (+1) or Short (-1)**

With reference to Code Listing 1, you can replicate the state variable display by removing the curly brackets around the code segment titled "Trend State Variable" and ensuring curly brackets are placed around the other display code segments.

## The Cycle is Complete

In the beginning we used cycle analysis to determine whether the market was trending or whether it was suitable for swing trading. Evolution has occurred. Our computers are far more capable than they were 40 years ago. Our continued research and application of the science of DSP to the art of trading has brought us full circle. We can now use cycle analytics to know when to trade the trend.

It has been a wonderful journey. Thanks to S&C for letting me be a part of it.

---

## Code Listing 1. Phasor Analysis

```easylanguage
{
Phasor Analysis
(C) 2013-2022 John F. Ehlers
}
Inputs:
Period(28);

Vars:
Signal(0),
count(0),
Sx(0),
Sy(0),
Sxx(0),
Sxy(0),
Syy(0),
X(0),
Y(0),
Real(0),
Imag(0),
Angle(0),
DerivedPeriod(0);

Signal = Close;

//Correlate with Cosine wave having a fixed period
Sx = 0;
Sy = 0;
Sxx = 0;
Sxy = 0;
Syy = 0;
For count = 1 to Period Begin
    X = Signal[count - 1];
    Y = Cosine(360*(count - 1) / Period);
    Sx = Sx + X;
    Sy = Sy + Y;
    Sxx = Sxx + X*X;
    Sxy = Sxy + X*Y;
    Syy = Syy + Y*Y;
End;
If (Period*Sxx - Sx*Sx > 0) and (Period*Syy - Sy*Sy > 0) Then
    Real = (Period*Sxy - Sx*Sy) / SquareRoot((Period*Sxx - Sx*Sx)*(Period*Syy - Sy*Sy));

//Correlate with a Negative Sine wave having a fixed period
Sx = 0;
Sy = 0;
Sxx = 0;
Sxy = 0;
Syy = 0;
For count = 1 to Period Begin
    X = Signal[count - 1];
    Y = -Sine(360*(count - 1) / Period);
    Sx = Sx + X;
    Sy = Sy + Y;
    Sxx = Sxx + X*X;
    Sxy = Sxy + X*Y;
    Syy = Syy + Y*Y;
End;
If (Period*Sxx - Sx*Sx > 0) and (Period*Syy - Sy*Sy > 0) Then
    Imag = (Period*Sxy - Sx*Sy) / SquareRoot((Period*Sxx - Sx*Sx)*(Period*Syy - Sy*Sy));

//Compute the angle as an arctangent function and resolve ambiguity
If Real <> 0 Then Angle = 90 - Arctangent(Imag / Real);
If Real < 0 Then Angle = Angle - 180;

//compensate for angle wraparound
If AbsValue(Angle[1]) - AbsValue(Angle - 360) < Angle - Angle[1] and Angle > 90 and Angle[1] < -90 Then Angle = Angle - 360;

//angle cannot go backwards
If Angle < Angle[1] and ((Angle > -135 and Angle[1] < 135) or (Angle < -90 and Angle[1] < -90)) Then Angle = Angle[1];

//Phasor Indicator
Plot1(Angle, "Angle", red, 4, 4);
Plot2(0, "Ref", white, 1, 1);
Plot4(90, "", cyan, 2, 2);
Plot8(-90, "", cyan, 2, 2);

{
//Frequency derived from rate-change of phase
Vars: DeltaAngle(0), AvgPeriod(0);
DeltaAngle = Angle - Angle[1];
If DeltaAngle <= 0 Then DeltaAngle = DeltaAngle[1];
If DeltaAngle <> 0 Then DerivedPeriod = 360 / DeltaAngle;
If DerivedPeriod > 60 Then DerivedPeriod = 60;
Plot9(DerivedPeriod, "", red, 4, 4);
}

{
//Trend State Variable
Vars: State(0);
State = 0;
If Angle - Angle[1] <= 6 Then Begin
    If Angle >= 90 or Angle <= -90 Then State = 1;
    If Angle > -90 and Angle < 90 Then State = -1;
End;
Plot10(State, "", red, 4, 4);
}
```

---

## BibTeX

```bibtex
@misc{ehlers_recurring_phase_cycle_analysis,
  author       = {John F. Ehlers},
  title        = {Recurring Phase of Cycle Analysis},
  year         = {2022},
  howpublished = {online},
  url          = {https://www.mesasoftware.com/papers/RECURRING%20PHASE%20OF%20CYCLE%20ANALYSIS.pdf}
}
```

[^1]: J.M. Hurst, "The Profit Magic of Stock Transaction Timing"
[^2]: Anthony Warren, PhD – S&C
