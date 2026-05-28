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
	public class BandPassFilter : Indicator
	{
		private HighPassFilter	hp;
		private SuperSmoother	ss;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"BandPassFilter Indicator as published in the April 2024 Stocks and Commodities article titled The Ultimate Smoother by John F. Ehlers.";
				Name				= "BandPassFilter";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= false;

				LowerPeriod			= 30;
				UpperPeriod			= 15;
				
				AddPlot(Brushes.Blue, "BandPassFilter");
				AddLine(Brushes.Black, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				hp	= HighPassFilter(Close, UpperPeriod);
				ss	= SuperSmoother(hp, LowerPeriod);
			}
		}

		protected override void OnBarUpdate()
		{
			Default[0]	= ss[0];
		}

		[NinjaScriptProperty]
		[Range(1, double.MaxValue)]
		[Display(Name = "Lower period", Description = "Period for SuperSmoother", GroupName = "NinjaScriptParameters", Order = 1)]
		public double LowerPeriod
		{ get; set; }
		
		[NinjaScriptProperty]
		[Range(1, double.MaxValue)]
		[Display(Name = "Upper period", Description = "Period for HighPassFilter", GroupName = "NinjaScriptParameters", Order = 0)]
		public double UpperPeriod
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
		private BandPassFilter[] cacheBandPassFilter;
		public BandPassFilter BandPassFilter(double lowerPeriod, double upperPeriod)
		{
			return BandPassFilter(Input, lowerPeriod, upperPeriod);
		}

		public BandPassFilter BandPassFilter(ISeries<double> input, double lowerPeriod, double upperPeriod)
		{
			if (cacheBandPassFilter != null)
				for (int idx = 0; idx < cacheBandPassFilter.Length; idx++)
					if (cacheBandPassFilter[idx] != null && cacheBandPassFilter[idx].LowerPeriod == lowerPeriod && cacheBandPassFilter[idx].UpperPeriod == upperPeriod && cacheBandPassFilter[idx].EqualsInput(input))
						return cacheBandPassFilter[idx];
			return CacheIndicator<BandPassFilter>(new BandPassFilter(){ LowerPeriod = lowerPeriod, UpperPeriod = upperPeriod }, input, ref cacheBandPassFilter);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.BandPassFilter BandPassFilter(double lowerPeriod, double upperPeriod)
		{
			return indicator.BandPassFilter(Input, lowerPeriod, upperPeriod);
		}

		public Indicators.BandPassFilter BandPassFilter(ISeries<double> input , double lowerPeriod, double upperPeriod)
		{
			return indicator.BandPassFilter(input, lowerPeriod, upperPeriod);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.BandPassFilter BandPassFilter(double lowerPeriod, double upperPeriod)
		{
			return indicator.BandPassFilter(Input, lowerPeriod, upperPeriod);
		}

		public Indicators.BandPassFilter BandPassFilter(ISeries<double> input , double lowerPeriod, double upperPeriod)
		{
			return indicator.BandPassFilter(input, lowerPeriod, upperPeriod);
		}
	}
}

#endregion
