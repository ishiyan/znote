/// Ported to NinjaTrader 8 by NinjaTrader_ChelseaB
/// 
/// From the author:
/// RMS Function
/// (C)2015 - 2022 John F. Ehlers

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
	public class RMS : Indicator
	{
		private double	sumSq;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description		= @"Root Mean Square (RMS) Indicator as published in the April 2025 Stocks and Commodities article titled The Ultimate Oscillator by John F. Ehlers.";
				Name			= "RMS";
				Calculate		= Calculate.OnBarClose;
				IsOverlay		= false;
				Length			= 100;

				AddPlot(Brushes.Red, "RMS");
			}
		}

		protected override void OnBarUpdate()
		{
			// SumSq = 0;
			sumSq	= 0;

			// for count = 0 to Length - 1 Begin
			// 		SumSq = SumSq + Price[count] * Price[count];
			//	End;
			for (int index = 0; index < Math.Min(CurrentBar, Length); index++)
				sumSq	+= Input[index] * Input[index];

			// If SumSq<> 0 Then $RMS = SquareRoot(SumSq / Length);
			if (sumSq != 0)
				Default[0] = Math.Sqrt(sumSq / Length);
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
		private RMS[] cacheRMS;
		public RMS RMS(int length)
		{
			return RMS(Input, length);
		}

		public RMS RMS(ISeries<double> input, int length)
		{
			if (cacheRMS != null)
				for (int idx = 0; idx < cacheRMS.Length; idx++)
					if (cacheRMS[idx] != null && cacheRMS[idx].Length == length && cacheRMS[idx].EqualsInput(input))
						return cacheRMS[idx];
			return CacheIndicator<RMS>(new RMS(){ Length = length }, input, ref cacheRMS);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.RMS RMS(int length)
		{
			return indicator.RMS(Input, length);
		}

		public Indicators.RMS RMS(ISeries<double> input , int length)
		{
			return indicator.RMS(input, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.RMS RMS(int length)
		{
			return indicator.RMS(Input, length);
		}

		public Indicators.RMS RMS(ISeries<double> input , int length)
		{
			return indicator.RMS(input, length);
		}
	}
}

#endregion
