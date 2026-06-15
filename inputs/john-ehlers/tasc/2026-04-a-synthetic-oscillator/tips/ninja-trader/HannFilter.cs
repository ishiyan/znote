/// Ported to NinjaTrader 8 by NinjaTrader_ChelseaB
/// 
/// From the author:
/// $Hann Windowed Lowpass FIR Filter Function
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
	public class HannFilter : Indicator
	{
		private double	filt, coef;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"Hann Windowed Lowpass FIR Filter as published in the April 2026 Stocks and Commodities article titled ""A Synthetic Oscillator"" by John F. Ehlers.";
				Name				= "HannFilter";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= true;

				Length				= 12;

				AddPlot(Brushes.Blue, "HannFilter");
			}
		}

		protected override void OnBarUpdate()
		{
			// Filt = 0;
			// coef = 0;
			filt	= 0;
			coef	= 0;

			// For count = 1 to Length Begin
			// 		Filt = Filt + (1 - Cosine(360*count / (Length + 1)))*Price[count - 1];
			// 		coef = coef + (1 - Cosine(360*count / (Length + 1)));
			// End;
			int lookback = Math.Min(CurrentBar + 1, Length);
			for (int count = 1; count <= lookback; count++)
			{
				double weight = 1 - Math.Cos(2 * Math.PI * count / (Length + 1));
				filt	+= weight * Input[count - 1];
				coef	+= weight;
			}

			// If coef <> 0 Then $Hann = Filt / coef;
			if (coef != 0)
				Default[0] = filt / coef;
			else
				Default[0] = Input[0];
		}

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "Length", GroupName = "Parameters", Order = 0)]
		public int Length
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
		private HannFilter[] cacheHannFilter;
		public HannFilter HannFilter(int length)
		{
			return HannFilter(Input, length);
		}

		public HannFilter HannFilter(ISeries<double> input, int length)
		{
			if (cacheHannFilter != null)
				for (int idx = 0; idx < cacheHannFilter.Length; idx++)
					if (cacheHannFilter[idx] != null && cacheHannFilter[idx].Length == length && cacheHannFilter[idx].EqualsInput(input))
						return cacheHannFilter[idx];
			return CacheIndicator<HannFilter>(new HannFilter(){ Length = length }, input, ref cacheHannFilter);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.HannFilter HannFilter(int length)
		{
			return indicator.HannFilter(Input, length);
		}

		public Indicators.HannFilter HannFilter(ISeries<double> input , int length)
		{
			return indicator.HannFilter(input, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.HannFilter HannFilter(int length)
		{
			return indicator.HannFilter(Input, length);
		}

		public Indicators.HannFilter HannFilter(ISeries<double> input , int length)
		{
			return indicator.HannFilter(input, length);
		}
	}
}

#endregion
