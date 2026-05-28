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
	public class FMDemodulator : Indicator
	{
		private double Deriv, a1, b1, c1, c2, c3;
		private Series<double> HL, SS;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"FMDemodulator indicator as detailed in the May 2021 Technical Analysis Stocks and Commodities article ‘A Technical Description of Market Data for Traders’ by John F Ehlers.";
				Name										= "FMDemodulator";
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
				BarsRequiredToPlot							= 0;
				Period										= 30;
				AddPlot(Brushes.SteelBlue, "FMPlot");
				AddLine(Brushes.DimGray, 0, "ZeroLine");
			}
			else if (State == State.DataLoaded)
			{
				HL = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				SS = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
			}
		}

		protected override void OnBarUpdate()
		{			
			//Derivative to establish zero mean (Basically the same as Close -
			//Close[1], but removes intraday gap openings)
			Deriv = Close[0] - Open[0];
			
			//Hard limiter to remove AM noise
			HL[0] = 10 * Deriv;
		
			if (HL[0] > 1)
				HL[0] = 1;
			else if (HL[0] < -1)
				HL[0] = -1;
			
			//Integrate with a SuperSmoother
			a1 = Math.Exp(-1.414 * 3.14159 / Period);
			b1 = 2 * a1 * Math.Cos((1.414 / Period) * (Math.PI));
			//b1 = 2 * a1 * Math.Cos((1.414 * (Period * Math.PI/180)));
			c2 = b1;
			c3 = -a1 * a1;
			c1 = 1 - c2 - c3;
			
			if (CurrentBar < 3)
				SS[0] = Deriv;
			else
				SS[0] = c1 * (HL[0] + HL[1]) / 2 + c2 * SS[1] + c3 * SS[2];
			
			FMPlot[0] = SS[0];
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Period", Description="Period", Order=1, GroupName="Parameters")]
		public int Period
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> FMPlot
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
		private FMDemodulator[] cacheFMDemodulator;
		public FMDemodulator FMDemodulator(int period)
		{
			return FMDemodulator(Input, period);
		}

		public FMDemodulator FMDemodulator(ISeries<double> input, int period)
		{
			if (cacheFMDemodulator != null)
				for (int idx = 0; idx < cacheFMDemodulator.Length; idx++)
					if (cacheFMDemodulator[idx] != null && cacheFMDemodulator[idx].Period == period && cacheFMDemodulator[idx].EqualsInput(input))
						return cacheFMDemodulator[idx];
			return CacheIndicator<FMDemodulator>(new FMDemodulator(){ Period = period }, input, ref cacheFMDemodulator);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.FMDemodulator FMDemodulator(int period)
		{
			return indicator.FMDemodulator(Input, period);
		}

		public Indicators.FMDemodulator FMDemodulator(ISeries<double> input , int period)
		{
			return indicator.FMDemodulator(input, period);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.FMDemodulator FMDemodulator(int period)
		{
			return indicator.FMDemodulator(Input, period);
		}

		public Indicators.FMDemodulator FMDemodulator(ISeries<double> input , int period)
		{
			return indicator.FMDemodulator(input, period);
		}
	}
}

#endregion
