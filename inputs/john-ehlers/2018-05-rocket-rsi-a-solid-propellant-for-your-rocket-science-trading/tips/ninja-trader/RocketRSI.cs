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
	public class RocketRSI : Indicator
	{
		private double a1, b1, c1, c2, c3, CU, CD, MyRSI;
		private double[] Filt, Mom;
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"RocketRSI indicator as discussed in the May 2018 Stocks and Commodities Magazine by John F. Ehlers";
				Name										= "RocketRSI";
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
				SmoothLength								= 8;
				RSILength									= 10;
				AddPlot(Brushes.Orange, "RSI");
				AddLine(Brushes.Blue, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				Filt = new double[RSILength+1];
				Mom = new double[2];
				
				a1 = Math.Exp(-1.414*3.14159 / (double)(SmoothLength));
				b1 = 2*a1*Math.Cos((1.414*180 / (double)(SmoothLength))*3.14159/180);
				c2 = b1;
				c3 = -a1*a1;
				c1 = 1 - c2 - c3;
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < RSILength)
				return;
			
			Mom[0] = Close[0] - Close[RSILength - 1];
			
			//SuperSmoother Filter
			Filt[0] = c1*(Mom[0] + Mom[1]) / 2 + c2*Filt[1] + c3*Filt[2];
			
			Print("Time: " + Time[0] + " Filt: " + Filt[0]);
			
			//Accumulate “Closes Up” and “Closes Down”
			CU = 0;
			CD = 0;
			for(int i = 0; i <= RSILength-1; i++)
			{
				if (Filt[i] - Filt[i + 1] > 0)
					CU = CU + Filt[i] - Filt[i + 1];
				if (Filt[i] - Filt[i + 1] < 0)
					CD = CD + Filt[i + 1] - Filt[i];
			}
			
			// Move Filt and Mom indexes
			for (int i = RSILength; i > 0; i--)
				Filt[i] = Filt[i-1];
			Mom[1] = Mom[0];
			
			if (CU + CD != 0) 
				MyRSI = (CU - CD) / (CU + CD);
			Print("Time: " + Time[0] + " MyRSI: " + MyRSI);
			
			//Limit RocketRSI output to +/- 3 Standard Deviations
			if (MyRSI > .999) 
				MyRSI = .999;
			if (MyRSI < -.999)
				MyRSI = -.999;
			
			//Apply Fisher Transform to establish Gaussian Probability Distribution
			RSI[0] = .5*Math.Log((1 + MyRSI) / (1 - MyRSI));
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="SmoothLength", Order=1, GroupName="Parameters")]
		public int SmoothLength
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="RSILength", Order=2, GroupName="Parameters")]
		public int RSILength
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> RSI
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
		private RocketRSI[] cacheRocketRSI;
		public RocketRSI RocketRSI(int smoothLength, int rSILength)
		{
			return RocketRSI(Input, smoothLength, rSILength);
		}

		public RocketRSI RocketRSI(ISeries<double> input, int smoothLength, int rSILength)
		{
			if (cacheRocketRSI != null)
				for (int idx = 0; idx < cacheRocketRSI.Length; idx++)
					if (cacheRocketRSI[idx] != null && cacheRocketRSI[idx].SmoothLength == smoothLength && cacheRocketRSI[idx].RSILength == rSILength && cacheRocketRSI[idx].EqualsInput(input))
						return cacheRocketRSI[idx];
			return CacheIndicator<RocketRSI>(new RocketRSI(){ SmoothLength = smoothLength, RSILength = rSILength }, input, ref cacheRocketRSI);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.RocketRSI RocketRSI(int smoothLength, int rSILength)
		{
			return indicator.RocketRSI(Input, smoothLength, rSILength);
		}

		public Indicators.RocketRSI RocketRSI(ISeries<double> input , int smoothLength, int rSILength)
		{
			return indicator.RocketRSI(input, smoothLength, rSILength);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.RocketRSI RocketRSI(int smoothLength, int rSILength)
		{
			return indicator.RocketRSI(Input, smoothLength, rSILength);
		}

		public Indicators.RocketRSI RocketRSI(ISeries<double> input , int smoothLength, int rSILength)
		{
			return indicator.RocketRSI(input, smoothLength, rSILength);
		}
	}
}

#endregion
