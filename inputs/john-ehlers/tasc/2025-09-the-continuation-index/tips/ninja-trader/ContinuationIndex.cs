/// Ported to NinjaTrader 8 by NinjaTrader_ChelseaB
/// 
/// From the author:
///  Continuation Index
///  (C)2025 John F. Ehlers

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
	public class ContinuationIndex : Indicator
	{
		private Series<double>		absDiff;
		private LaguerreFilter		laguerreFilterIndy;
		private UltimateSmoother	ultimateSmootherIndy;		
		private double				refVal, variance;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description		= @"Continuation Index Indicator as published in the September 2025 Stocks and Commodities article titled ""TThe Continuation Index"" by John F. Ehlers.";
				Name			= "Continuation Index";
				Calculate		= Calculate.OnBarClose;

				Gama			=.8;
				Sequence		= 8;
				Period			= 40;

				AddPlot(Brushes.Blue, "Continuation Index");
			}
			else if (State == State.DataLoaded)
			{
				// Ultimate Smoother
				// US = $UltimateSmoother(Close, Length / 2);
				ultimateSmootherIndy	= UltimateSmoother(Close, (int)(Period/2));
				// Laguerre Filter
				// LG = $Laguerre(Close, gama, order, Length);
				laguerreFilterIndy		= LaguerreFilter(Close, Gama, Period, Sequence);
				absDiff					= new Series<double>(this);
			}
		}

		protected override void OnBarUpdate()
		{
			// Average the filter difference
			// Variance = Average(AbsValue(US - LG), Length);
			absDiff[0]	= Math.Abs(ultimateSmootherIndy[0] - laguerreFilterIndy[0]);
			variance	= Average(absDiff, Period);

			// Double the normalized variance
			// If Variance<> 0 Then Ref = 2 * (US - LG) / Variance;
			if (variance != 0)
				refVal = 2 * (ultimateSmootherIndy[0] - laguerreFilterIndy[0]) / variance;

			// Compress using an Inverse Fisher Transform
			// CI = (ExpValue(2 * Ref) - 1) / (ExpValue(2 * Ref) + 1);
			Default[0] = (Math.Exp(2 * refVal) - 1) / (Math.Exp(2 * refVal) + 1);
		}

		private double Average(Series<double> inputSeries, int bars)
		{
			double sum = 0;

			for (int index = 0; index < Math.Min(CurrentBar, bars); index++)
				sum += inputSeries[index];

			return sum / Math.Min(CurrentBar, bars);
		}

		[Browsable(false)]
		public Series<double> Default
		{ get { return Values[0]; } }

		[NinjaScriptProperty]
		[Range(0, .9999)]
		[Display(Name = "Gama", GroupName = "NinjaScriptParameters", Order = 1)]
		public double Gama
		{ get; set; }

		[NinjaScriptProperty]
		[Display(Name = "Period", GroupName = "NinjaScriptParameters", Order = 0)]
		public int Period
		{ get; set; }

		[NinjaScriptProperty]
		[Range(0, 10)]
		[Display(Name = "Order", GroupName = "NinjaScriptParameters", Order = 2)]
		public int Sequence
		{ get; set; }
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private ContinuationIndex[] cacheContinuationIndex;
		public ContinuationIndex ContinuationIndex(double gama, int period, int sequence)
		{
			return ContinuationIndex(Input, gama, period, sequence);
		}

		public ContinuationIndex ContinuationIndex(ISeries<double> input, double gama, int period, int sequence)
		{
			if (cacheContinuationIndex != null)
				for (int idx = 0; idx < cacheContinuationIndex.Length; idx++)
					if (cacheContinuationIndex[idx] != null && cacheContinuationIndex[idx].Gama == gama && cacheContinuationIndex[idx].Period == period && cacheContinuationIndex[idx].Sequence == sequence && cacheContinuationIndex[idx].EqualsInput(input))
						return cacheContinuationIndex[idx];
			return CacheIndicator<ContinuationIndex>(new ContinuationIndex(){ Gama = gama, Period = period, Sequence = sequence }, input, ref cacheContinuationIndex);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.ContinuationIndex ContinuationIndex(double gama, int period, int sequence)
		{
			return indicator.ContinuationIndex(Input, gama, period, sequence);
		}

		public Indicators.ContinuationIndex ContinuationIndex(ISeries<double> input , double gama, int period, int sequence)
		{
			return indicator.ContinuationIndex(input, gama, period, sequence);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.ContinuationIndex ContinuationIndex(double gama, int period, int sequence)
		{
			return indicator.ContinuationIndex(Input, gama, period, sequence);
		}

		public Indicators.ContinuationIndex ContinuationIndex(ISeries<double> input , double gama, int period, int sequence)
		{
			return indicator.ContinuationIndex(input, gama, period, sequence);
		}
	}
}

#endregion
