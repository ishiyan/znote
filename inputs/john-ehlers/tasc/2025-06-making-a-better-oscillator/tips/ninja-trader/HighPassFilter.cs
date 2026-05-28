/// Ported to NinjaTrader 8 by NinjaTrader_ChelseaB
/// 
/// From the author:
/// Highpass Function
/// (C)2004 - 2024 John F. Ehlers

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
using NinjaTrader.Gui.PropertiesTest;
#endregion

//This namespace holds Indicators in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Indicators
{
	public class HighPassFilter : Indicator
	{
		private double	a1, b1, c2, c3, c1;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"HighPassFilter Indicator as published in the April 2024 Stocks and Commodities article titled Making A Better Oscillator by John F. Ehlers.";
				Name				= "HighPassFilter";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= false;
				BarsRequiredToPlot	= 4;

				Period				= 20;	
				
				AddPlot(Brushes.Red, "HighPassFilter");
				AddLine(Brushes.Black, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				// a1 = expvalue(-1.414*3.14159 / Period);
				a1	= Math.Exp(-1.414 * Math.PI / Period);
				// b1 = 2*a1*Cosine(1.414*180 / Period);
				b1	= 2 * a1 * Math.Cos(1.414 * Math.PI / Period); // Math.PI is used instead of 180 at the direction of the author
				// c2 = b1;
				c2	= b1;
				// c3 = -a1*a1;
				c3	= -a1 * a1;
				// c1 = (1 + c2 - c3) / 4;
				c1	= (1 + c2 - c3) / 4;
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar >= 4)
				// $HighPass = c1*(Price - 2*Price[1] + Price[2]) + c2*$HighPass[1] + c3*$HighPass[2];
				Default[0] = c1 * (Input[0] - 2 * Input[1] + Input[2]) + c2 * Default[1] + c3 * Default[2];
			else
				Default[0] = 0;
		}

		[NinjaScriptProperty]
		[Range(1, double.MaxValue)]
		[Display(Name = "Period", GroupName = "Parameters", Order = 0)]
		public double Period
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
		private HighPassFilter[] cacheHighPassFilter;
		public HighPassFilter HighPassFilter(double period)
		{
			return HighPassFilter(Input, period);
		}

		public HighPassFilter HighPassFilter(ISeries<double> input, double period)
		{
			if (cacheHighPassFilter != null)
				for (int idx = 0; idx < cacheHighPassFilter.Length; idx++)
					if (cacheHighPassFilter[idx] != null && cacheHighPassFilter[idx].Period == period && cacheHighPassFilter[idx].EqualsInput(input))
						return cacheHighPassFilter[idx];
			return CacheIndicator<HighPassFilter>(new HighPassFilter(){ Period = period }, input, ref cacheHighPassFilter);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.HighPassFilter HighPassFilter(double period)
		{
			return indicator.HighPassFilter(Input, period);
		}

		public Indicators.HighPassFilter HighPassFilter(ISeries<double> input , double period)
		{
			return indicator.HighPassFilter(input, period);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.HighPassFilter HighPassFilter(double period)
		{
			return indicator.HighPassFilter(Input, period);
		}

		public Indicators.HighPassFilter HighPassFilter(ISeries<double> input , double period)
		{
			return indicator.HighPassFilter(input, period);
		}
	}
}

#endregion
