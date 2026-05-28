/// Ported to NinjaTrader 8 by NinjaTrader_ChelseaB
/// 
/// From the author:
///  $Ultimate Smoother Function
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
using NinjaTrader.Gui.PropertiesTest;
#endregion

//This namespace holds Indicators in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Indicators
{
	public class UltimateSmoother : Indicator
	{
		private double	a0, q, c2, c1;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"Ultimate Smoother Indicator as published in the September 2025 Stocks and Commodities article titled ""TThe Continuation Index"" by John F. Ehlers.";
				Name				= "UltimateSmoother";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= true;
				BarsRequiredToPlot	= 4;

				Period				= 20;
				
				AddPlot(Brushes.Blue, "UltimateSmoother");
			}
			else if (State == State.DataLoaded)
			{
				// Q = expvalue(-1.414*3.14159 / Period);
				q	= Math.Exp(-1.414 * Math.PI / Period);
				// c1 = 2*Q*Cosine(1.414*180 / Period);
				c1	= 2 * q * Math.Cos(1.414 * Math.PI / Period);
				// c2 = Q*Q;
				c2	= q * q;
				// a0 = (1 + c1 + c2) / 4;
				a0	= (1 + c1 + c2) / 4;
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar >= 4)
				// US = (1 - a0)*Price + (2*a0 - c1)*Price[1] + (c2 - a0)*Price[2] + c1*US[1] - c2*US[2];
				Default[0] = (1 - a0) * Input[0] + (2 * a0 - c1) * Input[1] + (c2 - a0) * Input[2] + c1 * Default[1] - c2 * Default[2];
			else
				Default[0] = Input[0];
		}

		[Browsable(false)]
		[XmlIgnore()]
		public Series<double> Default
		{ get { return Values[0]; } }

		[NinjaScriptProperty]
		[Range(1, double.MaxValue)]
		public double Period
		{ get; set; }
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
