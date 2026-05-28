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
	public class SuperSmoother : Indicator
	{
		private double	a1, b1, c2, c3, c1;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"SuperSmoother Indicator as published in the April 2024 Stocks and Commodities article titled The Ultimate Smoother by John F. Ehlers.";
				Name				= "SuperSmoother";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= true;
				BarsRequiredToPlot	= 4;

				Period				= 20;
				
				AddPlot(Brushes.Red, "SuperSmoother");
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
				// c1 = 1 - c2 - c3;
				c1	= 1 - c2 - c3;
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar >= 4)
				// n $SuperSmoother = c1 * (Price + Price[1]) / 2 + c2 *$SuperSmoother[1] + c3 *$SuperSmoother[2];
				Default[0] = c1 * (Input[0] + Input[1]) / 2 + c2 * Default[1] + c3 * Default[2];
			else
				Default[0] = Input[0];
		}

		[NinjaScriptProperty]
		[Range(1, double.MaxValue)]
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
		private SuperSmoother[] cacheSuperSmoother;
		public SuperSmoother SuperSmoother(double period)
		{
			return SuperSmoother(Input, period);
		}

		public SuperSmoother SuperSmoother(ISeries<double> input, double period)
		{
			if (cacheSuperSmoother != null)
				for (int idx = 0; idx < cacheSuperSmoother.Length; idx++)
					if (cacheSuperSmoother[idx] != null && cacheSuperSmoother[idx].Period == period && cacheSuperSmoother[idx].EqualsInput(input))
						return cacheSuperSmoother[idx];
			return CacheIndicator<SuperSmoother>(new SuperSmoother(){ Period = period }, input, ref cacheSuperSmoother);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.SuperSmoother SuperSmoother(double period)
		{
			return indicator.SuperSmoother(Input, period);
		}

		public Indicators.SuperSmoother SuperSmoother(ISeries<double> input , double period)
		{
			return indicator.SuperSmoother(input, period);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.SuperSmoother SuperSmoother(double period)
		{
			return indicator.SuperSmoother(Input, period);
		}

		public Indicators.SuperSmoother SuperSmoother(ISeries<double> input , double period)
		{
			return indicator.SuperSmoother(input, period);
		}
	}
}

#endregion
