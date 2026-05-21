/// Ported to NinjaTrader 8 by NinjaTrader_ChelseaB
/// 
/// From the author:
///  Laguerre Filter Function
///  (C)2005 - 2022 John F. Ehlers

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
	public class LaguerreFilter : Indicator
	{
		private double				fir;
		private double[,]			lg;
		private UltimateSmoother	ultimateSmoother;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"Laguerre Filter Indicator as published in the September 2025 Stocks and Commodities article titled ""TThe Continuation Index"" by John F. Ehlers.";
				Name				= "Laguerre Filter";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= true;

				Gama				=.8;
				Sequence			= 8;
				Period				= 40;

				AddPlot(Brushes.Blue, "Laguerre Filter");
			}
			else if (State == State.DataLoaded)
			{
				ultimateSmoother	= UltimateSmoother(Input, Period);
				lg					= new double[10,2];
			}
		}

		protected override void OnBarUpdate()
		{
			// load the current values of the arrays to be the values one
			// bar ago
			// For count = 1 to order Begin
			// LG[count, 2] = LG[count, 1];
			// End;
			for (int index = 0; index < Sequence; ++index)
				lg[index, 1] = lg[index, 0];
			
			// compute the Laguerre components for the current bar
			// For count = 2 to order Begin
			// LG[count, 1] = -gama * LG[count - 1, 2] + LG[count - 1, 2] + gama * LG[count, 2];
			// End;
			for (int index = 1; index < Sequence; ++index)
				lg[index, 0] = -Gama * lg[index - 1, 1] + lg[index - 1, 1] + Gama * lg[index, 1];

			//LG[1, 1] = $UltimateSmoother(Price, Length);
			lg[0, 0] = ultimateSmoother[0];

			// sum the Laguerre components
			// FIR = 0;
			// For count = 1 to order Begin
			// FIR = FIR + LG[count, 1];
			// End;
			fir = 0;
			for (int index = 0; index < Sequence; ++index)
				fir += lg[index, 0];

			// $Laguerre = FIR / order;
			Default[0] = fir / Sequence;
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
		private LaguerreFilter[] cacheLaguerreFilter;
		public LaguerreFilter LaguerreFilter(double gama, int period, int sequence)
		{
			return LaguerreFilter(Input, gama, period, sequence);
		}

		public LaguerreFilter LaguerreFilter(ISeries<double> input, double gama, int period, int sequence)
		{
			if (cacheLaguerreFilter != null)
				for (int idx = 0; idx < cacheLaguerreFilter.Length; idx++)
					if (cacheLaguerreFilter[idx] != null && cacheLaguerreFilter[idx].Gama == gama && cacheLaguerreFilter[idx].Period == period && cacheLaguerreFilter[idx].Sequence == sequence && cacheLaguerreFilter[idx].EqualsInput(input))
						return cacheLaguerreFilter[idx];
			return CacheIndicator<LaguerreFilter>(new LaguerreFilter(){ Gama = gama, Period = period, Sequence = sequence }, input, ref cacheLaguerreFilter);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.LaguerreFilter LaguerreFilter(double gama, int period, int sequence)
		{
			return indicator.LaguerreFilter(Input, gama, period, sequence);
		}

		public Indicators.LaguerreFilter LaguerreFilter(ISeries<double> input , double gama, int period, int sequence)
		{
			return indicator.LaguerreFilter(input, gama, period, sequence);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.LaguerreFilter LaguerreFilter(double gama, int period, int sequence)
		{
			return indicator.LaguerreFilter(Input, gama, period, sequence);
		}

		public Indicators.LaguerreFilter LaguerreFilter(ISeries<double> input , double gama, int period, int sequence)
		{
			return indicator.LaguerreFilter(input, gama, period, sequence);
		}
	}
}

#endregion
