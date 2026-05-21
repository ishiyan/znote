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
using System.Windows.Forms;
using NinjaTrader.Gui.PropertiesTest;
#endregion

//This namespace holds Indicators in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Indicators
{
	public class GriffithsSpectrum : Indicator
	{
		private HighPassFilter	hP;
		private SuperSmoother	lP;
		private double			mu, real, imag, denom, maxPwr;
		private double[]		xx, coef;
		private double[,]		pwr;
		private Series<double>	normalizedSignal, peak;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description		= @"Griffiths Spectrum Indicator as published in the January 2025 Stocks and Commodities article titled Linear Predictive Filters And Instantaneous Frequency by John F. Ehlers.";
				Name			= "GriffithsSpectrum";
				Calculate		= Calculate.OnBarClose;
				IsOverlay		= false;
				
				Length			= 40;
				LowerBound		= 10;
				UpperBound		= 40;
			}
			else if (State == State.Configure)
			{
				for (int index = 0; index < 100; index++)
					AddPlot(new Stroke(Brushes.White, 2), PlotStyle.Dot, "Spectrum" + index);
			}
			else if (State == State.DataLoaded)
			{
				xx					= new double[200];
				coef				= new double[200];
				pwr					= new double[100, 2];
				peak				= new Series<double>(this, MaximumBarsLookBack);
				normalizedSignal	= new Series<double>(this, MaximumBarsLookBack);
				
				hP					= HighPassFilter(UpperBound);
				lP					= SuperSmoother(hP, LowerBound);

				mu					= 1.0 / Length;
			}
		}

		protected override void OnBarUpdate()
		{
			peak[0] = (CurrentBar == 0) ? .1 : 0.991 * peak[1];

			if (Math.Abs(lP[0]) > peak[0])
				peak[0] = Math.Abs(lP[0]);

			normalizedSignal[0] = (peak[0] != 0) ? lP[0] / peak[0] : 0;

			if (CurrentBar < Length)
				return;

			for (int count = 1; count <= Length; count++)
				xx[count] = normalizedSignal[Length - count];

			double xBar = 0;

			for (int count = 1; count <= Length; count++)
				xBar += xx[Length - count] * coef[count];

			for (int count = 1; count <= Length; count++)
				coef[count] += mu * (xx[Length] - xBar) * xx[Length - count];

			for (int period = LowerBound; period <= UpperBound; period++)
			{
				pwr[period, 1]	= pwr[period, 0];

				real			= 0;
				imag			= 0;

				for (int count = 1; count <= Length; count++)
				{
					real	+= coef[count] * Math.Cos(360 * count / period);
					imag	+= coef[count] * Math.Sin(360 * count / period);
				}

				denom			= (1 - real) * (1 - real) + imag * imag;
				pwr[period, 0]	= .1 / denom + .9 * pwr[period, 1];
			}

			maxPwr = 0;

			for (int period = LowerBound; period <= UpperBound; period++)
				maxPwr = Math.Max(maxPwr, pwr[period, 0]);

			for (int period = LowerBound; period <= UpperBound; period++)
				if (maxPwr != 0)
					pwr[period, 0] = pwr[period, 0] / maxPwr;

			for (int period = LowerBound; period <= UpperBound; period++)
			{
				Values[period][0] = period;

				if (pwr[period, 0] >= .5)
				{
					SolidColorBrush thisBrush = new SolidColorBrush(Color.FromRgb(255, (byte)(255 * (2 * pwr[period, 0] - 1)), 0));
					thisBrush.Freeze();

					PlotBrushes[period][0]	= thisBrush;
				}
				else
				{
					SolidColorBrush thisBrush = new SolidColorBrush(Color.FromRgb((byte)(255 * 2 * pwr[period, 0]), 0, 0));
					thisBrush.Freeze();

					PlotBrushes[period][0]	= thisBrush;
				}
			}
		}

		[NinjaScriptProperty]
		[Range(10, 200)]
		[Display(Name = "Length", Order = 1, GroupName = "Parameters")]
		public int Length { get; set; }

		[NinjaScriptProperty]
		[Range(8, 125)]
		[Display(Name = "Lower Bound", Order = 2, GroupName = "Parameters")]
		public int LowerBound { get; set; }

		[NinjaScriptProperty]
		[Range(8, 125)]
		[Display(Name = "Upper Bound", Order = 3, GroupName = "Parameters")]
		public int UpperBound { get; set; }
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private GriffithsSpectrum[] cacheGriffithsSpectrum;
		public GriffithsSpectrum GriffithsSpectrum(int length, int lowerBound, int upperBound)
		{
			return GriffithsSpectrum(Input, length, lowerBound, upperBound);
		}

		public GriffithsSpectrum GriffithsSpectrum(ISeries<double> input, int length, int lowerBound, int upperBound)
		{
			if (cacheGriffithsSpectrum != null)
				for (int idx = 0; idx < cacheGriffithsSpectrum.Length; idx++)
					if (cacheGriffithsSpectrum[idx] != null && cacheGriffithsSpectrum[idx].Length == length && cacheGriffithsSpectrum[idx].LowerBound == lowerBound && cacheGriffithsSpectrum[idx].UpperBound == upperBound && cacheGriffithsSpectrum[idx].EqualsInput(input))
						return cacheGriffithsSpectrum[idx];
			return CacheIndicator<GriffithsSpectrum>(new GriffithsSpectrum(){ Length = length, LowerBound = lowerBound, UpperBound = upperBound }, input, ref cacheGriffithsSpectrum);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.GriffithsSpectrum GriffithsSpectrum(int length, int lowerBound, int upperBound)
		{
			return indicator.GriffithsSpectrum(Input, length, lowerBound, upperBound);
		}

		public Indicators.GriffithsSpectrum GriffithsSpectrum(ISeries<double> input , int length, int lowerBound, int upperBound)
		{
			return indicator.GriffithsSpectrum(input, length, lowerBound, upperBound);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.GriffithsSpectrum GriffithsSpectrum(int length, int lowerBound, int upperBound)
		{
			return indicator.GriffithsSpectrum(Input, length, lowerBound, upperBound);
		}

		public Indicators.GriffithsSpectrum GriffithsSpectrum(ISeries<double> input , int length, int lowerBound, int upperBound)
		{
			return indicator.GriffithsSpectrum(input, length, lowerBound, upperBound);
		}
	}
}

#endregion
