//
// Copyright (C) 2025, NinjaTrader LLC <www.ninjatrader.com>.
//
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

namespace NinjaTrader.NinjaScript.Indicators
{
	public class OneEuroFilter : Indicator
	{
		private HighPass highPass;
		private Series<double> smoothed;
		private Series<double> smoothedDX;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description					= @"One Euro Filter Indicator from 'A Simple Speed-Based Low-Pass Filter For Noisy Input In Interactive Systems' (CHI 2012) by Georges Casiez, Nicolas Roussel, and Daniel Vogel. Adapted by John F. Ehlers.";
				Name						= "OneEuroFilter";
				Calculate					= Calculate.OnBarClose;
				IsOverlay					= true;
				DisplayInDataBox			= true;
				DrawOnPricePanel			= true;
				DrawHorizontalGridLines		= true;
				DrawVerticalGridLines		= true;
				PaintPriceMarkers			= true;
				ScaleJustification			= NinjaTrader.Gui.Chart.ScaleJustification.Right;
				IsSuspendedWhileInactive	= true;
				PeriodMin					= 10;
				Beta						= 0.2;
				UseHighPass					= false;
				HighPassPeriod				= 54;
				AddPlot(new Stroke(Brushes.Green, 4), PlotStyle.Line, "Smoothed");
			}
			else if (State == State.Configure)
			{
				if(UseHighPass)
					highPass = HighPass(HighPassPeriod);
			}
			else if (State == State.DataLoaded)
			{
				smoothed = new Series<double>(this, MaximumBarsLookBack.Infinite);
				smoothedDX = new Series<double>(this, MaximumBarsLookBack.Infinite);
			}
		}

		protected override void OnBarUpdate()
		{
			// Source: One Euro Filter Indicator by John F. Ehlers
			// From 'A Simple Speed-Based Low-Pass Filter For Noisy Input In Interactive Systems' (CHI 2012)
			// By Georges Casiez, Nicolas Roussel, and Daniel Vogel

			double price = 0;
			if(UseHighPass)
				price = highPass[0];
			else
				price = Close[0];
			
			// Initialize on the first bar
			if (CurrentBar == 0)
			{
				smoothedDX[0] = 0;
				smoothed[0] = price;
				return;
			}

			// Minimum cutoff frequency
			double periodDX = 10;

			// Alpha for the DX smoothing
			double alphaDX = 2 * Math.PI / (4 * Math.PI + periodDX);

			// EMA of the Delta Price
			smoothedDX[0] = alphaDX * (price - (UseHighPass ? highPass[1] : Close[1])) + (1 - alphaDX) * smoothedDX[1];

			// Adjust cutoff period based on the fraction of the rate of change
			double cutoff = PeriodMin + Beta * Math.Abs(smoothedDX[0]);

			// Compute adaptive alpha
			double alpha3 = 2 * Math.PI / (4 * Math.PI + cutoff);

			// Adaptive smoothing
			smoothed[0] = alpha3 * price + (1 - alpha3) * smoothed[1];

			// Plot the smoothed value
			Value[0] = smoothed[0];
		}

		#region Properties
		
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="PeriodMin", Description="Minimum cutoff frequency", Order=1, GroupName="Parameters")]
		public int PeriodMin { get; set; }
		
		[NinjaScriptProperty]
		[Range(0.0, double.MaxValue)]
		[Display(Name="Beta", Description="Responsiveness factor", Order=2, GroupName="Parameters")]
		public double Beta { get; set; }

		[NinjaScriptProperty]
		[Display(Name="UseHighPass", Description="Use HighPass indicator as price source", Order=3, GroupName="Parameters")]
		public bool UseHighPass { get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="HighPassPeriod", Description="Period for the HighPass filter", Order=4, GroupName="Parameters")]
		public int HighPassPeriod { get; set; }
		
		#endregion

	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private OneEuroFilter[] cacheOneEuroFilter;
		public OneEuroFilter OneEuroFilter(int periodMin, double beta, bool useHighPass, int highPassPeriod)
		{
			return OneEuroFilter(Input, periodMin, beta, useHighPass, highPassPeriod);
		}

		public OneEuroFilter OneEuroFilter(ISeries<double> input, int periodMin, double beta, bool useHighPass, int highPassPeriod)
		{
			if (cacheOneEuroFilter != null)
				for (int idx = 0; idx < cacheOneEuroFilter.Length; idx++)
					if (cacheOneEuroFilter[idx] != null && cacheOneEuroFilter[idx].PeriodMin == periodMin && cacheOneEuroFilter[idx].Beta == beta && cacheOneEuroFilter[idx].UseHighPass == useHighPass && cacheOneEuroFilter[idx].HighPassPeriod == highPassPeriod && cacheOneEuroFilter[idx].EqualsInput(input))
						return cacheOneEuroFilter[idx];
			return CacheIndicator<OneEuroFilter>(new OneEuroFilter(){ PeriodMin = periodMin, Beta = beta, UseHighPass = useHighPass, HighPassPeriod = highPassPeriod }, input, ref cacheOneEuroFilter);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.OneEuroFilter OneEuroFilter(int periodMin, double beta, bool useHighPass, int highPassPeriod)
		{
			return indicator.OneEuroFilter(Input, periodMin, beta, useHighPass, highPassPeriod);
		}

		public Indicators.OneEuroFilter OneEuroFilter(ISeries<double> input , int periodMin, double beta, bool useHighPass, int highPassPeriod)
		{
			return indicator.OneEuroFilter(input, periodMin, beta, useHighPass, highPassPeriod);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.OneEuroFilter OneEuroFilter(int periodMin, double beta, bool useHighPass, int highPassPeriod)
		{
			return indicator.OneEuroFilter(Input, periodMin, beta, useHighPass, highPassPeriod);
		}

		public Indicators.OneEuroFilter OneEuroFilter(ISeries<double> input , int periodMin, double beta, bool useHighPass, int highPassPeriod)
		{
			return indicator.OneEuroFilter(input, periodMin, beta, useHighPass, highPassPeriod);
		}
	}
}

#endregion
