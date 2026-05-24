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
	public class REMA : Indicator
	{
		private double				Constant;
		private double[][] 			RE;
		private Series<double>  	myEMA; // Alpha is handled differently than Period, so we will make our own EMA
		private Series<double>  	myREMA; // Reversal
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"Revesrse EMA indicator as described in the Septermber 2017 Technical Analysis Stocks and Commodities article: The Reverse EMA Indicator";
				Name										= "REMA";
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
				Alpha										= 0.1;
				AddPlot(Brushes.Orange, "REMA");
				AddPlot(Brushes.Green, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				Constant 	= 0;
				RE 			= new double[8][];
				for(int i = 0; i < 8; i++)
					RE[i] 	= new double[2];
				myEMA		= new Series<double>(this, MaximumBarsLookBack.Infinite);
				myREMA 		= new Series<double>(this, MaximumBarsLookBack.Infinite);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar == 0)
			{
				myEMA[0] = Input[0];
				return;
			}
			
			// Compute EMA
			Constant = 1 - Alpha;
			myEMA[0] = Alpha * Input[0] + Constant * myEMA[1];
			
			// Compute Reverse EMA
			RE[0][0] = Constant					* myEMA[0] + myEMA[1];
			RE[1][0] = Math.Pow(Constant, 2) 	* RE[0][0] + RE[0][1];
			RE[2][0] = Math.Pow(Constant, 4) 	* RE[1][0] + RE[1][1];
			RE[3][0] = Math.Pow(Constant, 8) 	* RE[2][0] + RE[2][1];
			RE[4][0] = Math.Pow(Constant, 16) 	* RE[3][0] + RE[3][1];
			RE[5][0] = Math.Pow(Constant, 32) 	* RE[4][0] + RE[4][1];
			RE[6][0] = Math.Pow(Constant, 64) 	* RE[5][0] + RE[5][1];
			RE[7][0] = Math.Pow(Constant, 128) 	* RE[6][0] + RE[6][1];
			
			// Move current RE values to RE[i][1]
			for(int i = 0; i < 8; i++)
				RE[i][1] = RE[i][0];
			
			// Calculate distance
			myREMA[0] = myEMA[0] - Alpha * RE[7][0];
			
			// Plot values
			Values[0][0] = myREMA[0];
			Values[1][0] = 0;
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(0, double.MaxValue)]
		[Display(Name="Alpha", Description="Modifies the coefficient used in the EMA. Lower shows more Trend Response, Higher shows more Cycle Response", Order=1, GroupName="Parameters")]
		public double Alpha
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> MYREMA
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
		private REMA[] cacheREMA;
		public REMA REMA(double alpha)
		{
			return REMA(Input, alpha);
		}

		public REMA REMA(ISeries<double> input, double alpha)
		{
			if (cacheREMA != null)
				for (int idx = 0; idx < cacheREMA.Length; idx++)
					if (cacheREMA[idx] != null && cacheREMA[idx].Alpha == alpha && cacheREMA[idx].EqualsInput(input))
						return cacheREMA[idx];
			return CacheIndicator<REMA>(new REMA(){ Alpha = alpha }, input, ref cacheREMA);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.REMA REMA(double alpha)
		{
			return indicator.REMA(Input, alpha);
		}

		public Indicators.REMA REMA(ISeries<double> input , double alpha)
		{
			return indicator.REMA(input, alpha);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.REMA REMA(double alpha)
		{
			return indicator.REMA(Input, alpha);
		}

		public Indicators.REMA REMA(ISeries<double> input , double alpha)
		{
			return indicator.REMA(input, alpha);
		}
	}
}

#endregion
