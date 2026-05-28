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
	public class RecursiveMedianOscillator : Indicator
	{
		private double a0;
		private double a1;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The Recursive Median Oscillator as described in the March 2018 Technical Analysis Stocks and Commodities article 'Recursive Median Filters'.";
				Name										= "RecursiveMedianOscillator";
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
				LPPeriod									= 12;
				HPPeriod									= 30;
				
				AddPlot(Brushes.Transparent, "RM");
				AddPlot(Brushes.Orange, "RMO");
				AddLine(Brushes.Blue, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				a0 = (Math.Cos(6.28319 / LPPeriod) + Math.Sin(6.28319 / LPPeriod) - 1) / Math.Cos(6.28319 / LPPeriod);
				a1 = (Math.Cos((.707 * 6.28319) / HPPeriod) + Math.Sin((.707 * 6.28319) / HPPeriod) - 1) / Math.Cos((.707 * 6.28319) / HPPeriod); 
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < 5)
				return;
			
			RM[0] 	= (CurrentBar == 0 ? Input[0] : a0 * GetMedian(Input, 5-1) + (1-a0)*RM[1]);
			RMO[0] 	= (CurrentBar == 0 ? Input[0] : (1 - a1 / 2)*(1 - a1 / 2)*(RM[0] - 2*RM[1] + RM[2]) + 2*(1 - a1)*RMO[1] - (1 - a1)*(1 - a1)*RMO[2]);
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="LPPeriod", Description="Low Pass Period", Order=1, GroupName="Parameters")]
		public int LPPeriod
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="HPPeriod", Description="High Pass Period", Order=2, GroupName="Parameters")]
		public int HPPeriod
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> RM
		{
			get { return Values[0]; }
		}
		
		[Browsable(false)]
		[XmlIgnore]
		public Series<double> RMO
		{
			get { return Values[1]; }
		}

		#endregion

	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private RecursiveMedianOscillator[] cacheRecursiveMedianOscillator;
		public RecursiveMedianOscillator RecursiveMedianOscillator(int lPPeriod, int hPPeriod)
		{
			return RecursiveMedianOscillator(Input, lPPeriod, hPPeriod);
		}

		public RecursiveMedianOscillator RecursiveMedianOscillator(ISeries<double> input, int lPPeriod, int hPPeriod)
		{
			if (cacheRecursiveMedianOscillator != null)
				for (int idx = 0; idx < cacheRecursiveMedianOscillator.Length; idx++)
					if (cacheRecursiveMedianOscillator[idx] != null && cacheRecursiveMedianOscillator[idx].LPPeriod == lPPeriod && cacheRecursiveMedianOscillator[idx].HPPeriod == hPPeriod && cacheRecursiveMedianOscillator[idx].EqualsInput(input))
						return cacheRecursiveMedianOscillator[idx];
			return CacheIndicator<RecursiveMedianOscillator>(new RecursiveMedianOscillator(){ LPPeriod = lPPeriod, HPPeriod = hPPeriod }, input, ref cacheRecursiveMedianOscillator);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.RecursiveMedianOscillator RecursiveMedianOscillator(int lPPeriod, int hPPeriod)
		{
			return indicator.RecursiveMedianOscillator(Input, lPPeriod, hPPeriod);
		}

		public Indicators.RecursiveMedianOscillator RecursiveMedianOscillator(ISeries<double> input , int lPPeriod, int hPPeriod)
		{
			return indicator.RecursiveMedianOscillator(input, lPPeriod, hPPeriod);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.RecursiveMedianOscillator RecursiveMedianOscillator(int lPPeriod, int hPPeriod)
		{
			return indicator.RecursiveMedianOscillator(Input, lPPeriod, hPPeriod);
		}

		public Indicators.RecursiveMedianOscillator RecursiveMedianOscillator(ISeries<double> input , int lPPeriod, int hPPeriod)
		{
			return indicator.RecursiveMedianOscillator(input, lPPeriod, hPPeriod);
		}
	}
}

#endregion
