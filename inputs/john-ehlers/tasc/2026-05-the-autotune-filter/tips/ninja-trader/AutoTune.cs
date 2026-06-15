/// Ported to NinjaTrader 8 by NinjaTrader_Eduardo
/// 
/// From the author:
/// AutoTune Indicator
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

namespace NinjaTrader.NinjaScript.Indicators
{
	public class AutoTune : Indicator
	{
		private HighPassFilter	hpFilter;
		private Series<double>	bpSeries;
		private Series<double>	dcSeries;
		private Series<double>	minCorrSeries;
		private double[]		corr;
		private AutoTuneEnums.AutoTunePlotType plotType = AutoTuneEnums.AutoTunePlotType.Bandpass;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"AutoTune Filter Indicator as published in the May 2026 Stocks and Commodities article titled ""The AutoTune Filter"" by John F. Ehlers.";
				Name				= "AutoTune";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= false;
				BarsRequiredToPlot	= 4;

				PlotType			= AutoTuneEnums.AutoTunePlotType.HighpassFilter;
				Window				= 20;
				Bandwidth			= 0.25;

				AddPlot(Brushes.Blue, "Bandpass");
				AddLine(Brushes.DarkGray, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				hpFilter		= HighPassFilter(Close, Window);
				bpSeries		= new Series<double>(this);
				dcSeries		= new Series<double>(this);
				minCorrSeries	= new Series<double>(this);
				corr			= new double[Window + 1];
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < 2 * Window)
			{
				bpSeries[0]			= 0;
				dcSeries[0]			= 0;
				minCorrSeries[0]	= 0;
				Default[0]			= 0;
				return;
			}

			// Filt = $Highpass(Close, Window);
			// hpFilter values are computed automatically as a sub-indicator

			// Correlation computation
			Array.Clear(corr, 0, corr.Length);

			for (int lag = 1; lag <= Window; lag++)
			{
				double sx = 0, sy = 0, sxx = 0, sxy = 0, syy = 0;

				for (int j = 0; j < Window; j++)
				{
					double x = hpFilter[j];
					double y = hpFilter[lag + j];
					sx	+= x;
					sy	+= y;
					sxx	+= x * x;
					sxy	+= x * y;
					syy	+= y * y;
				}

				double denomX = Window * sxx - sx * sx;
				double denomY = Window * syy - sy * sy;

				if (denomX > 0 && denomY > 0)
					corr[lag] = (Window * sxy - sx * sy) / Math.Sqrt(denomX * denomY);
			}

			// Find minimum correlation and dominant cycle
			double minCorr	= 1;
			double dc		= 0;

			for (int lag = 1; lag <= Window; lag++)
			{
				if (corr[lag] < minCorr)
				{
					minCorr	= corr[lag];
					dc		= 2 * lag;
				}
			}

			// Limit DC change to +/- 2 per bar
			double prevDC = dcSeries[1];
			if (prevDC > 0)
			{
				if (dc > prevDC + 2) dc = prevDC + 2;
				if (dc < prevDC - 2) dc = prevDC - 2;
			}

			dcSeries[0]		= dc;
			minCorrSeries[0]	= minCorr;

			// Inline bandpass filter with dynamic DC period
			// BP = $Bandpass(Close, DC, Bandwidth);
			if (dc >= 2)
			{
				double l1 = Math.Cos(2 * Math.PI / dc);
				double g1 = Math.Cos(Bandwidth * 2 * Math.PI / dc);

				if (g1 != 0)
				{
					double s1 = 1.0 / g1 - Math.Sqrt(1.0 / (g1 * g1) - 1);
					bpSeries[0] = 0.5 * (1 - s1) * (Close[0] - Close[2]) + l1 * (1 + s1) * bpSeries[1] - s1 * bpSeries[2];
				}
				else
					bpSeries[0] = 0;
			}
			else
				bpSeries[0] = 0;

			switch (plotType)
			{
				case AutoTuneEnums.AutoTunePlotType.HighpassFilter:
					Default[0] = hpFilter[0];
					Plots[0].Name = "Highpass Filter";
					break;
				case AutoTuneEnums.AutoTunePlotType.MinCorrelation:
					Default[0] = minCorr;
					Plots[0].Name = "Min Correlation";
					break;
				case AutoTuneEnums.AutoTunePlotType.DominantCycle:
					Default[0] = dc;
					Plots[0].Name = "Dominant Cycle";
					break;
				case AutoTuneEnums.AutoTunePlotType.Bandpass:
					Default[0] = bpSeries[0];
					Plots[0].Name = "Bandpass";
					break;
			}
		}

		#region Properties

		[NinjaScriptProperty]
		[Range(2, 100)]
		[Display(Name = "Window", Description = "Autocorrelation window / highpass filter period", GroupName = "Parameters", Order = 0)]
		public int Window
		{ get; set; }

		[NinjaScriptProperty]
		[Range(0.01, 1.0)]
		[Display(Name = "Bandwidth", Description = "Bandpass filter bandwidth as a fraction of the dominant cycle period", GroupName = "Parameters", Order = 1)]
		public double Bandwidth
		{ get; set; }

		[Display(Name = "Plot type", Description = "Select which output value to plot", GroupName = "Parameters", Order = 2)]
		public AutoTuneEnums.AutoTunePlotType PlotType
		{
			get { return plotType; }
			set { plotType = value; }
		}

		[Browsable(false)]
		[XmlIgnore()]
		public Series<double> Default
		{ get { return Values[0]; } }

		[Browsable(false)]
		[XmlIgnore()]
		public Series<double> Bandpass
		{ get { return bpSeries; } }

		[Browsable(false)]
		[XmlIgnore()]
		public Series<double> DominantCycle
		{ get { return dcSeries; } }

		[Browsable(false)]
		[XmlIgnore()]
		public Series<double> MinCorrelation
		{ get { return minCorrSeries; } }

		[Browsable(false)]
		[XmlIgnore()]
		public Series<double> HighPassFiltered
		{ get { return hpFilter.Default; } }

		#endregion
	}
}

namespace AutoTuneEnums
{
	public enum AutoTunePlotType
	{
		HighpassFilter,
		MinCorrelation,
		DominantCycle,
		Bandpass,
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private AutoTune[] cacheAutoTune;
		public AutoTune AutoTune(int window, double bandwidth)
		{
			return AutoTune(Input, window, bandwidth);
		}

		public AutoTune AutoTune(ISeries<double> input, int window, double bandwidth)
		{
			if (cacheAutoTune != null)
				for (int idx = 0; idx < cacheAutoTune.Length; idx++)
					if (cacheAutoTune[idx] != null && cacheAutoTune[idx].Window == window && cacheAutoTune[idx].Bandwidth == bandwidth && cacheAutoTune[idx].EqualsInput(input))
						return cacheAutoTune[idx];
			return CacheIndicator<AutoTune>(new AutoTune(){ Window = window, Bandwidth = bandwidth }, input, ref cacheAutoTune);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.AutoTune AutoTune(int window, double bandwidth)
		{
			return indicator.AutoTune(Input, window, bandwidth);
		}

		public Indicators.AutoTune AutoTune(ISeries<double> input , int window, double bandwidth)
		{
			return indicator.AutoTune(input, window, bandwidth);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.AutoTune AutoTune(int window, double bandwidth)
		{
			return indicator.AutoTune(Input, window, bandwidth);
		}

		public Indicators.AutoTune AutoTune(ISeries<double> input , int window, double bandwidth)
		{
			return indicator.AutoTune(input, window, bandwidth);
		}
	}
}

#endregion
