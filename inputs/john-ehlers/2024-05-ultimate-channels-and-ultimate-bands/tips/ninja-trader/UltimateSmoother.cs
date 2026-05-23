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
	public class UltimateSmoother : Indicator
	{
		private double	a1, b1, c2, c3, c1;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"UltimateSmoother Indicator as published in the April 2024 Stocks and Commodities article titled ""The Ultimate Smoother"" by John F. Ehlers.";
				Name				= "UltimateSmoother";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= true;
				BarsRequiredToPlot	= 4;

				Period				= 20;
				
				AddPlot(Brushes.Blue, "UltimateSmoother");
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
				// US = (1 - c1)*Price + (2*c1 - c2)*Price[1] - (c1 + c3) * Price[2] + c2 * US[1] + c3 * US[2];
				Default[0] = (1 - c1) * Input[0] + (2 * c1 - c2) * Input[1] - (c1 + c3) * Input[2] + c2 * Default[1] + c3 * Default[2];
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
		private UltimateSmoother[] cacheUltimateSmoother;
		public UltimateSmoother UltimateSmoother(double period)
		{
			return UltimateSmoother(Input, period);
		}

		public UltimateSmoother UltimateSmoother(ISeries<double> input, double period)
		{
			if (cacheUltimateSmoother != null)
				for (int idx = 0; idx < cacheUltimateSmoother.Length; idx++)
					if (cacheUltimateSmoother[idx] != null && cacheUltimateSmoother[idx].Period == period && cacheUltimateSmoother[idx].EqualsInput(input))
						return cacheUltimateSmoother[idx];
			return CacheIndicator<UltimateSmoother>(new UltimateSmoother(){ Period = period }, input, ref cacheUltimateSmoother);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.UltimateSmoother UltimateSmoother(double period)
		{
			return indicator.UltimateSmoother(Input, period);
		}

		public Indicators.UltimateSmoother UltimateSmoother(ISeries<double> input , double period)
		{
			return indicator.UltimateSmoother(input, period);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.UltimateSmoother UltimateSmoother(double period)
		{
			return indicator.UltimateSmoother(Input, period);
		}

		public Indicators.UltimateSmoother UltimateSmoother(ISeries<double> input , double period)
		{
			return indicator.UltimateSmoother(input, period);
		}
	}
}

#endregion
