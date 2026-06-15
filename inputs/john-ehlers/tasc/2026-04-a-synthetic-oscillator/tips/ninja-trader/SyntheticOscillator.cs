/// Ported to NinjaTrader 8 by NinjaTrader_ChelseaB
/// 
/// From the author:
/// Synthetic Oscillator Indicator
/// (C) 2025 John F. Ehlers

#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

//This namespace holds Indicators in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Indicators
{
	public class SyntheticOscillator : Indicator
	{
		private HannFilter			hannFilter;
		private HighPassFilter		highPassFilter;
		private SuperSmoother		superSmoother;
		private RMS					rms;
		private HighPassFilter		highPassFilter2;
		private UltimateSmoother 	ultimateSmoother;

		private Series<double>		realSeries;
		private Series<double>		imagSeries;
		private Series<double>		bpSeries;
		private Series<double>		synthSeries;
		private double				phase;
		private double				mid;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"Synthetic Oscillator as published in the April 2026 Stocks and Commodities article titled ""A Synthetic Oscillator"" by John F. Ehlers.";
				Name				= "SyntheticOscillator";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= false;
				BarsRequiredToPlot	= 4;

				LowerBound			= 15;
				UpperBound			= 25;
				HannLength			= 12;

				AddPlot(Brushes.Blue, "Synth");
				AddLine(Brushes.DarkGray, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				// Mid = SquareRoot(LowerBound*UpperBound);
				mid					= Math.Sqrt(LowerBound * UpperBound);

				// Price = $Hann(Close, 12);
				hannFilter			= HannFilter(Input, HannLength);
				// HP = $HighPass(Price, UpperBound);
				highPassFilter		= HighPassFilter(hannFilter.Default, UpperBound);
				// LP = $SuperSmoother(HP, LowerBound);
				superSmoother		= SuperSmoother(highPassFilter.Default, LowerBound);
				// RMS = $RMS(LP, 100);
				rms					= RMS(superSmoother.Default, 100);

				// HP2 = $Highpass(Close, Mid);
				highPassFilter2		= HighPassFilter(Input, mid);
				// BP = $UltimateSmoother(HP2, Mid);
				ultimateSmoother	= UltimateSmoother(highPassFilter2.Default, mid);

				realSeries			= new Series<double>(this);
				imagSeries			= new Series<double>(this);
				bpSeries			= new Series<double>(this);
				synthSeries			= new Series<double>(this);
				phase				= 0;
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < 4)
			{
				realSeries[0]	= 0;
				imagSeries[0]	= 0;
				bpSeries[0]		= 0;
				synthSeries[0]	= 0;
				Default[0]		= 0;
				return;
			}

			double lp = superSmoother.Default[0];
			double rmsVal = rms.Default[0];

			// If RMS <> 0 Then Real = LP / RMS;
			realSeries[0] = rmsVal != 0 ? lp / rmsVal : 0;

			// ROC = Real - Real[1];
			double roc = realSeries[0] - realSeries[1];

			// Compute QRMS inline for the ROC series since we need a rolling calculation
			// QRMS = $RMS(ROC, 100);
			double sumSq = 0;
			int lookback = Math.Min(CurrentBar, 100);
			for (int i = 0; i < lookback; i++)
			{
				double rocVal = realSeries[i] - (CurrentBar > i + 1 ? realSeries[i + 1] : 0);
				sumSq += rocVal * rocVal;
			}
			double qrmsVal = sumSq != 0 ? Math.Sqrt(sumSq / 100) : 0;

			// If QRMS <> 0 Then Imag = ROC / QRMS;
			imagSeries[0] = qrmsVal != 0 ? roc / qrmsVal : 0;

			// Denom = (Real - Real[1])*Imag - (Imag - Imag[1])*Real;
			double denom = (realSeries[0] - realSeries[1]) * imagSeries[0] - (imagSeries[0] - imagSeries[1]) * realSeries[0];

			// If Denom <> 0 Then DC = 6.28*(Real*Real + Imag*Imag) / Denom;
			double dc = LowerBound; // default value
			if (denom != 0)
				dc = 2 * Math.PI * (realSeries[0] * realSeries[0] + imagSeries[0] * imagSeries[0]) / denom;

			// If DC < LowerBound Then DC = LowerBound;
			if (dc < LowerBound) dc = LowerBound;
			// If DC > UpperBound Then DC = UpperBound;
			if (dc > UpperBound) dc = UpperBound;

			// BP = $UltimateSmoother(HP2, Mid);
			bpSeries[0] = ultimateSmoother.Default[0];

			// Phase = Phase + 360 / DC;
			phase = phase + 360 / dc;

			// If BP Crosses Over 0 Then Phase = 180 / DC;
			if (CrossAbove(bpSeries, 0, 1))
				phase = 180 / dc;

			// If BP Crosses Under 0 Then Phase = 180 + 180 / DC;
			if (CrossBelow(bpSeries, 0, 1))
				phase = 180 + 180 / dc;

			// Synth = Sine(Phase);
			double synth = Math.Sin(phase * Math.PI / 180);

			// Remove reset glitch if continuity falls in the same quadrant
			// If Phase > 0 and Phase < 90 and Synth < Synth[1] Then Synth = Synth[1];
			if (phase > 0 && phase < 90 && synth < synthSeries[1])
				synth = synthSeries[1];

			// If Phase > 180 and Phase < 270 and Synth > Synth[1] Then Synth = Synth[1];
			if (phase > 180 && phase < 270 && synth > synthSeries[1])
				synth = synthSeries[1];

			synthSeries[0]	= synth;
			Default[0]		= synth;
		}

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "Lower Bound", Description = "Lower bound for dominant cycle period", GroupName = "NinjaScriptParameters", Order = 0)]
		public int LowerBound
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "Upper Bound", Description = "Upper bound for dominant cycle period", GroupName = "NinjaScriptParameters", Order = 1)]
		public int UpperBound
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "Hann Length", Description = "Length for Hann windowed lowpass filter", GroupName = "NinjaScriptParameters", Order = 2)]
		public int HannLength
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore()]
		public Series<double> Default
		{ get { return Values[0]; } }
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private SyntheticOscillator[] cacheSyntheticOscillator;
		public SyntheticOscillator SyntheticOscillator(int lowerBound, int upperBound, int hannLength)
		{
			return SyntheticOscillator(Input, lowerBound, upperBound, hannLength);
		}

		public SyntheticOscillator SyntheticOscillator(ISeries<double> input, int lowerBound, int upperBound, int hannLength)
		{
			if (cacheSyntheticOscillator != null)
				for (int idx = 0; idx < cacheSyntheticOscillator.Length; idx++)
					if (cacheSyntheticOscillator[idx] != null && cacheSyntheticOscillator[idx].LowerBound == lowerBound && cacheSyntheticOscillator[idx].UpperBound == upperBound && cacheSyntheticOscillator[idx].HannLength == hannLength && cacheSyntheticOscillator[idx].EqualsInput(input))
						return cacheSyntheticOscillator[idx];
			return CacheIndicator<SyntheticOscillator>(new SyntheticOscillator(){ LowerBound = lowerBound, UpperBound = upperBound, HannLength = hannLength }, input, ref cacheSyntheticOscillator);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.SyntheticOscillator SyntheticOscillator(int lowerBound, int upperBound, int hannLength)
		{
			return indicator.SyntheticOscillator(Input, lowerBound, upperBound, hannLength);
		}

		public Indicators.SyntheticOscillator SyntheticOscillator(ISeries<double> input , int lowerBound, int upperBound, int hannLength)
		{
			return indicator.SyntheticOscillator(input, lowerBound, upperBound, hannLength);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.SyntheticOscillator SyntheticOscillator(int lowerBound, int upperBound, int hannLength)
		{
			return indicator.SyntheticOscillator(Input, lowerBound, upperBound, hannLength);
		}

		public Indicators.SyntheticOscillator SyntheticOscillator(ISeries<double> input , int lowerBound, int upperBound, int hannLength)
		{
			return indicator.SyntheticOscillator(input, lowerBound, upperBound, hannLength);
		}
	}
}

#endregion
