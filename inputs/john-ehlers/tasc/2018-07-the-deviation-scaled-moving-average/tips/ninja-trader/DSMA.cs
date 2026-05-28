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
	public class DSMA : Indicator
	{
		private double a1, b1, c1, c2, c3;
		private double[] Filt, Zeros;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"Deviation Scaled Moving Average as published in the July 2018 S&C article titled The Deviation-Scaled Moving Average by John F. Ehlers";
				Name										= "DSMA";
				Calculate									= Calculate.OnBarClose;
				IsOverlay									= true;
				DisplayInDataBox							= true;
				DrawOnPricePanel							= true;
				DrawHorizontalGridLines						= true;
				DrawVerticalGridLines						= true;
				PaintPriceMarkers							= true;
				ScaleJustification							= NinjaTrader.Gui.Chart.ScaleJustification.Right;
				//Disable this property if your indicator requires custom values that cumulate with each new market data event. 
				//See Help Guide for additional information.
				IsSuspendedWhileInactive					= true;
				Period										= 40;
				AddPlot(Brushes.Orange, "DSMA_Plot");
			}
			else if (State == State.DataLoaded)
			{
				Filt 	= new double[Period+1];
				Zeros  	= new double[2];
				
				a1 = Math.Exp(-1.414 * 3.14159 / (.5 * (double)Period));
				b1 = 2 * a1 * Math.Cos((1.414 * 180 / (.5 * (double)Period)) * (3.14159 / 180));
				c2 = b1;
				c3 = -a1 * a1;
				c1 = 1 - c2 - c3;
			}
		}

		protected override void OnBarUpdate()
		{
			double ScaledFilt = 0, RMS = 0, alpha1 = 0;
			
			if (CurrentBar < 2)
				return;
			
			Zeros[0] = Close[0] - Close[2];
			
			// SuperSmoother Filter
			Filt[0] = c1 * (Zeros[0] + Zeros[1]) / 2 + c2 * Filt[1] + c3 * Filt[2];
			
			// Compute Standard Deviation
			for (int i = 0; i <= Period-1; i++)
				RMS = RMS + Filt[i] * Filt[i];
			RMS = Math.Sqrt(RMS / (double)Period);
			
			// Rescale Filt in terms of Standard Deviations
			ScaledFilt = Filt[0] / RMS;
			
			alpha1 = Math.Abs(ScaledFilt) * 5 / (double)Period;
			DSMA_Plot[0] = alpha1 * Close[0] + (1 - alpha1) * DSMA_Plot[1];
			
			// Move Filt and Zeros indexes
			for (int i = Period; i > 0; i--)
				Filt[i] = Filt[i-1];
			Zeros[1] = Zeros[0];
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(2, int.MaxValue)]
		[Display(Name="Period", Order=1, GroupName="Parameters")]
		public int Period
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> DSMA_Plot
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
		private DSMA[] cacheDSMA;
		public DSMA DSMA(int period)
		{
			return DSMA(Input, period);
		}

		public DSMA DSMA(ISeries<double> input, int period)
		{
			if (cacheDSMA != null)
				for (int idx = 0; idx < cacheDSMA.Length; idx++)
					if (cacheDSMA[idx] != null && cacheDSMA[idx].Period == period && cacheDSMA[idx].EqualsInput(input))
						return cacheDSMA[idx];
			return CacheIndicator<DSMA>(new DSMA(){ Period = period }, input, ref cacheDSMA);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.DSMA DSMA(int period)
		{
			return indicator.DSMA(Input, period);
		}

		public Indicators.DSMA DSMA(ISeries<double> input , int period)
		{
			return indicator.DSMA(input, period);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.DSMA DSMA(int period)
		{
			return indicator.DSMA(Input, period);
		}

		public Indicators.DSMA DSMA(ISeries<double> input , int period)
		{
			return indicator.DSMA(input, period);
		}
	}
}

#endregion
