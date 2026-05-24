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
	public class RecursiveMedianFilter : Indicator
	{
		private double a;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The Recursive Median Filter as described in the March 2018 Technical Analysis Stocks and Commodities article 'Recursive Median Filters'.";
				Name										= "RecursiveMedianFilter";
				Calculate									= Calculate.OnBarClose;
				IsOverlay									= false;
				DisplayInDataBox							= true;
				DrawOnPricePanel							= true;
				DrawHorizontalGridLines						= true;
				DrawVerticalGridLines						= true;
				PaintPriceMarkers							= true;
				ScaleJustification							= NinjaTrader.Gui.Chart.ScaleJustification.Right;
				//Disable this property if your indicator requires custom values that cumulate with each new market data event. 
				//See Help Guide for additional information.
				IsSuspendedWhileInactive					= true;
				Period										= 12;
				
				AddPlot(Brushes.Orange, "RM");
			}
			else if (State == State.DataLoaded)
			{
				a = (Math.Cos(6.28319/Period) + Math.Sin(6.28319/Period) - 1) / Math.Cos(6.28319/Period);
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < 5)
				return;
			
			RM[0] = (CurrentBar == 0 ? Input[0] : a * GetMedian(Input, 5-1) + (1-a)*RM[1]);
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Period", Description="Period", Order=1, GroupName="Parameters")]
		public int Period
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> RM
		{
			get { return Values[0]; }
		}
		#endregion

	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private RecursiveMedianFilter[] cacheRecursiveMedianFilter;
		public RecursiveMedianFilter RecursiveMedianFilter(int period)
		{
			return RecursiveMedianFilter(Input, period);
		}

		public RecursiveMedianFilter RecursiveMedianFilter(ISeries<double> input, int period)
		{
			if (cacheRecursiveMedianFilter != null)
				for (int idx = 0; idx < cacheRecursiveMedianFilter.Length; idx++)
					if (cacheRecursiveMedianFilter[idx] != null && cacheRecursiveMedianFilter[idx].Period == period && cacheRecursiveMedianFilter[idx].EqualsInput(input))
						return cacheRecursiveMedianFilter[idx];
			return CacheIndicator<RecursiveMedianFilter>(new RecursiveMedianFilter(){ Period = period }, input, ref cacheRecursiveMedianFilter);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.RecursiveMedianFilter RecursiveMedianFilter(int period)
		{
			return indicator.RecursiveMedianFilter(Input, period);
		}

		public Indicators.RecursiveMedianFilter RecursiveMedianFilter(ISeries<double> input , int period)
		{
			return indicator.RecursiveMedianFilter(input, period);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.RecursiveMedianFilter RecursiveMedianFilter(int period)
		{
			return indicator.RecursiveMedianFilter(Input, period);
		}

		public Indicators.RecursiveMedianFilter RecursiveMedianFilter(ISeries<double> input , int period)
		{
			return indicator.RecursiveMedianFilter(input, period);
		}
	}
}

#endregion
