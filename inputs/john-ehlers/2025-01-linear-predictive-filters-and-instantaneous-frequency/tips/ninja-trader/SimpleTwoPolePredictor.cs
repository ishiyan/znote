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
	public class SimpleTwoPolePredictor : Indicator
	{
		private HighPassFilter	hP;
		private SuperSmoother	lP;
		private double			c0, c1, c2, sum;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description		= @"Simple Two Pole Predictor Indicator as published in the January 2025 Stocks and Commodities article titled Linear Predictive Filters And Instantaneous Frequency by John F. Ehlers.";
				Name			= "SimpleTwoPolePredictor";
				Calculate		= Calculate.OnBarClose;
				IsOverlay		= false;
				
				Q				= 0.35;
				
				AddPlot(Brushes.Blue, "Prediction");
				AddPlot(Brushes.Red, "SuperSmootherHighPass");			
				
				AddLine(Brushes.Black, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				hP	= HighPassFilter(15);
				lP	= SuperSmoother(hP, 30);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < 2)
				return;
			
			// Calculate constants for predictive filter
			c0		= 1;
			c1		= 1.8 * Q;
			c2		= -Q * Q;
			sum		= 1 - c1 - c2;
			c0		/= sum;
			c1		/= sum;
			c2		/= sum;
			
			Default[0]			= c0 * lP[0] - c1 * lP[1] - c2 * lP[2];
			SuperSmoother[0]	= lP[0];
		}
		
		[XmlIgnore]
		[Browsable(false)]
		public Series<double> Default
		{ get { return Values[0]; } }
		
		[XmlIgnore]
		[Browsable(false)]
		public Series<double> SuperSmoother
		{ get { return Values[1]; } }
		
		[NinjaScriptProperty]
		[Range(0, double.MaxValue)]
		[Display(Name = "Q", GroupName = "Parameters", Order = 0)]
		public double Q
		{ get; set; }
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private SimpleTwoPolePredictor[] cacheSimpleTwoPolePredictor;
		public SimpleTwoPolePredictor SimpleTwoPolePredictor(double q)
		{
			return SimpleTwoPolePredictor(Input, q);
		}

		public SimpleTwoPolePredictor SimpleTwoPolePredictor(ISeries<double> input, double q)
		{
			if (cacheSimpleTwoPolePredictor != null)
				for (int idx = 0; idx < cacheSimpleTwoPolePredictor.Length; idx++)
					if (cacheSimpleTwoPolePredictor[idx] != null && cacheSimpleTwoPolePredictor[idx].Q == q && cacheSimpleTwoPolePredictor[idx].EqualsInput(input))
						return cacheSimpleTwoPolePredictor[idx];
			return CacheIndicator<SimpleTwoPolePredictor>(new SimpleTwoPolePredictor(){ Q = q }, input, ref cacheSimpleTwoPolePredictor);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.SimpleTwoPolePredictor SimpleTwoPolePredictor(double q)
		{
			return indicator.SimpleTwoPolePredictor(Input, q);
		}

		public Indicators.SimpleTwoPolePredictor SimpleTwoPolePredictor(ISeries<double> input , double q)
		{
			return indicator.SimpleTwoPolePredictor(input, q);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.SimpleTwoPolePredictor SimpleTwoPolePredictor(double q)
		{
			return indicator.SimpleTwoPolePredictor(Input, q);
		}

		public Indicators.SimpleTwoPolePredictor SimpleTwoPolePredictor(ISeries<double> input , double q)
		{
			return indicator.SimpleTwoPolePredictor(input, q);
		}
	}
}

#endregion
