# TRADING SYSTEM CONCEPTS

![Figure 7-3](assets/figure-7.3.png)
*Figure 7-3 Underestimated Cycle Length Speeds Stop Acceleration—*


Resulting Whipsaws Severely Reduce Profits (Stop-Loss Is Solid Line)

between the current low price and the current stop will not be
removed until the age of the trade is 70% of the dominant cycle.
This variation ensures that you will err on the long side of your
cycle input to compute the stops, resulting in fewer whipsaw re-
versals. You can also make the Age/(K + DC) term nonlinear by
multiplying it by itself one or more times, with the result that the
term is square, cubed, and so forth. When you do this, the factor
becomes much smaller when the ratio is less than one and much
larger when the ratio is greater than one, thereby making it more
nonlinear. Another variant on the stop system is to multiply the
measured average daily volatility by a constant to either decrease
or increase the initial risk. Providing flexibility in setting the risk
can alter the overall profits of the system.

I have a high regard for this stop-loss system. This stop
system, combined with the ELI indicator described in Chapter 6,
are the heart of the EPOCH PRO trading program.


8

CYCLE MEASUREMENT

Cycles in the market can be measured in a variety of ways that
involve a range of complexity, with resulting accuracy differ-
ences. In this chapter we discuss the most commonly used ap-
proaches. The most commonly used measurement techniques are
cycle finders, Fast Fourier Transforms (FFT), and Maximum
Entropy Spectral Analysis (MESA).

I do not think FFTs are appropriate for the measurement
of short-term market cycles. The practical application of FFTs
leaves much to be desired because some of the fundamental
constraints are ignored when looking at the market. Cycle find-
ers are nice for historical research, but if cycles are apparent in
real-time trading their existence will be obvious to many
traders. If the majority of traders establish positions on the
basis of the cycle, the cycle is extinguished. As an example,
seasonals are most often discounted at the time the contract
begins trading.


CYCLE FINDERS

The basic idea of cycle finders is to measure the distance be-
tween the same phase on successive cycles. The resultant meas-
urement is necessarily the cycle length of a simple cycle. Any
constant phase point on the cycle can be used, but the measure-
ment is usually made between cycle lows. Cycle lows are used
not only because they are easy to identify but because they tend
to be sharper than cycle highs.

A cycle finder can be as simple as a ruler or dividers that
measure lengths on printed charts. The Ehrlich Cycle Finder’
named after inventor Stan Ehrlich, is basically a pantograph that
allows you mechanically to correlate successive cycles and to
scale cycle periods in the search for more complicated patterns.

Cycle finders are also found on most Toolbox trading
programs such as CompuTrac, N-Squared Computing, and
MetaStock. Typical operation involves placing the screen cur-
sor at a critical time position of interest. When the cycle finder
tool is called, a vertical line is drawn at the cursor position and
other vertical lines are repeated every cycle period to the right
and left of the critical position. The up-arrow and down-arrow
keys typically adjust the cycle length, the length being the
spacing between vertical lines. The left-arrow and right-arrow
keys typically control the time position of all the lines by mov-
ing them together.

Cycle finders are handy devices for a quick inspection of
cyclic activity and estimation of the next cyclic turn of the
market. What the cycle finders have in speed and simplicity is
compromised by their inability to address all but the most obvi-
ous cases.

FAST FOURIER TRANSFORMS (FFT)

A Fourier transform is a procedure to find the frequency re-
sponse of a function whose time domain characteristic is known.


![Figure 8-1](assets/figure-8.1.png)
*Figure 8-1 Spectragram of a Complex Signal*

FAST FOURIER TRANSFORMS (FFT) + 79

As it relates to the market, a Fourier transform measures the
cycles from the bar chart where time is the horizontal axis and
the price is scaled along the vertical axis. The transform pro-
duces a spectragram (see Figure 8-1) where the cycle amplitudes
are displayed as a function of frequency. Engineers and scien-
tists usually prefer the transform to be displayed in terms of
frequency rather than period (cycle length). A fast Fourier trans-
form (FFT) is an algorithm used to speed the calculation because
a large number of mathematical operations are required in tak-
ing the transform. The FFT has particular application when the
length of the data are long.

Fourier transforms are the equivalent of applying the time
data to a bank of filters. Energy input to this bank of filters can
have components at all frequencies. Conceptually, one of these
filters could be tuned to output energy only for a 6-day cycle and

POWER

FREQUENCY


rejecting all other energy. Another filter could be tuned to 7 days,
a third filter could be tuned to 8 days, and so forth. Then the
frequency response of the complex input data is computed by
comparing the amplitude of the energy at the output of each of
the filters in the bank. If we stacked the filters from left to right
so that the X-axis is the cycle frequency and plotted the output
energy of each filter parallel to the Y-axis, the result would be a
discrete spectrum in terms of the cycle frequency. By simple ex-
amination of the spectrum we could see which filter has the
strongest output and therefore what is the dominant cycle in the
data. We could also easily spot secondary cycles of lower ampli-
tude if they were present.

Fourier transforms do this filtering mathematically. If the
input data is multiplied by a sine wave and the product of all the
discrete points are added over exactly a complete cycle, only
energy at the frequency of the sine wave results. The energy is
additive over multiple complete cycles. If the input data is also
multiplied by a cosine wave and the product of all the discrete
points are added, another energy term is obtained only for the
frequency of the cosine wave. Adding the two energy terms to-
gether recovers the entire energy in the input data at the fre-
quency of the sine wave. That is, we have mathematically
accomplished the equivalent of filtering.

A very important constraint in the Fourier transform is
that the data must be taken only over an integer number of
cycles.

When taking a Fourier transform, the user obtains a sample
of data to satisfy the integer number of cycle constraint. In the-
ory, this sample of data is perfectly representative of all data
extending in both directions to infinity. That is, data in the win-
dow is replicated over and over again in the complete picture.

A final constraint of the sampled data system is the
Nyquist sampling criterion. The Nyquist criterion states that the
shortest cycle must have at least two samples per cycle. There-
fore, the shortest cycle that can be measured using daily data is
a 2-day cycle.


MAXIMUM ENTROPY SPECTRAL ANALYSIS (MESA) + 81

Let’s see where these constraints lead us if we analyze the
market with a 64-sample FFT. Each sample can be a day’s data,
so we are using about 13 weeks of data on a daily basis. The
longest cycle that fits in this sample window is 64 days. The next
longest cycle fitting an integer number of times is a 32-day cycle.
The next longest cycle is 64/3, or 21.3 days. The fourth longest
cycle is 64/4, or 16 days. Note there is a gap, or lack of resolution
of more than 5 days just in the region we wish to examine for
trading short-term cycles. We have a dilemma. We cannot meas-
ure an 18-day cycle and still have the Fourier transform be valid.
The only way to increase the resolution is to increase the size of
the data window. Suppose we increased the data window to 256
samples (days). Now there are 14 cycles of a signal whose period
is 18.29 days and 15 cycles of a signal whose period is 17.07 days.
We have achieved an approximate 1-day resolution with the 256
data samples, but the penalty is severe.

The only way we can get the FFT resolution we need is to
use more than one year’s data. The short-term 18-day cycle can
only be identified if it has been occurring consistently for the
last 14 or 15 cycles! If we accept the drunkard’s walk formula-
tion as the basis for chart activity, the data-length requirement
is unacceptable. The requirement is similar to demanding that
14 river meanders in a row all be identical to predict the occur-
rence of the next meander. This is so unlikely that the possibil-
ity should be dismissed out of hand.

FFTs lack resolution when the data window is short.
Longer data bases force an unlikely requirement on continued
existence of the cycle. For these reasons we should reject FFTs
for the identification of short-term cycles in the market.

MAXIMUM ENTROPY SPECTRAL ANALYSIS (MESA)

MESA is an outgrowth of the predictive deconvolution filtering
techniques developed by geophysicists for oil exploration.*” Its
specific goal is to obtain high resolution measurements from


minimum length data—precisely the requirement for the identi-
fication of short-term cycles in the market.

If we have a frequency source followed by a filter, the output
of the filter is just those frequency components of the filter that
were allowed to pass through the filter. This is mathematically
expressed as the product of the frequency source and the filter in
the frequency domain. We can find the Fourier series (not to be
confused with the Fourier transform) for both the source and the
filter to obtain a description in the time domain. The process of
taking the product of the two Fourier series is called convolution.
Convolution is the equivalent of sliding the filter time response
past the source time response, taking the product at each time
increment, and summing all the products.

The maximum entropy approach to spectral analysis is a
variation of deconvolution filtering techniques. A deconvolution
filter whitens the spectrum of the signal on which it operates;
that is, when convolved with the original signal it outputs a new
signal with a constant spectrum. A constant spectrum signal is
called white noise because it contains energy at all frequencies.
This approach to spectral analysis is also known as the Markov
spectrum or the autoregressive spectrum. Burg realized that this
approach yields the spectrum having the “maximum entropy” of
all possible spectra that are consistent with the measured auto-
correlation function. Entropy is a term first used in thermody-
namics to describe the degree of disorder and has more recently
been used as a quantitative term in information theory. There-
fore, “maximum entropy” is a case having the least amount of
information, and deconvolution filtering produces an output
having the least amount of information.

The advantage of deconvolution filtering is immediately
obvious. Finding the frequency spectrum does not involve a
convolution in the frequency domain with a cumbersome win-
dow spectrum (the FFT period) that unavoidably destroys spec-
tral resolution. The convolution has already taken place in the
time domain between the input signal and the digital filter.
Therefore, no window sidelobes or serious end effects exist with


MAXIMUM ENTROPY SPECTRAL ANALYSIS (MESA) + 83

the FFT. The truncation of the data set is important only to the
extent that enough data must be available to allow the building
of an efficient whitening filter that can reduce the output data
to a random series, This is routinely done using only about one
cycle’s worth of input data.

The maximum entropy estimate is the optimal choice for
measuring cycles because it is maximally noncommittal with
regard to any missing data and is simultaneously constrained to
be consistent with all available data. The “correct” length of
data to be used for analysis is perhaps the most critical aspect
of using MESA. In any event, the fact that MESA attains its
high-resolution measurement with a short amount of data
makes its use ideal for the market where current measurements
are mandatory for relevant results.
