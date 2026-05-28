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
	public class CTI : Indicator
	{
		private double Sx = 0;
		private double Sy = 0;
		private double Sxx = 0;
		private double Sxy = 0;
		private double Syy = 0;
		private int count = 0;
		private double X = 0;
		private double Y = 0;
		private double corr = 0;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= "Correlation as a Trend Indicator as published in May 2020 Technical Analysis of Stocks And Commodities article titled \"Correlation as a Trend Indicator\" by John F. Ehlers.";
				Name										= "CTI";
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
				Length					= 20;
				AddPlot(Brushes.Red, "CorrelationTrend");
				AddLine(Brushes.Blue, 0, "ZeroLine");
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < Length) return;
			
			Sx = 0;
			Sy = 0;
			Sxx = 0;
			Sxy = 0;
			Syy = 0;
			
			for(count = 0; count < Length; count++)
			{
				X = Close[count];
				Y = -count;
				Sx = Sx + X;
				Sy = Sy + Y;
				Sxx = Sxx + X*X;
				Sxy = Sxy + X*Y;
				Syy = Syy + Y*Y;
			}
			
			if(Length*Sxx - Sx*Sx > 0 && Length*Syy - Sy*Sy > 0)
			{
				corr = (Length*Sxy - Sx*Sy) / Math.Sqrt((Length*Sxx - Sx*Sx)*(Length*Syy - Sy*Sy));
			}
			
			CorrelationTrend[0] = corr;
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Length", Description="The correlation period", Order=1, GroupName="Parameters")]
		public int Length
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> CorrelationTrend
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
		private CTI[] cacheCTI;
		public CTI CTI(int length)
		{
			return CTI(Input, length);
		}

		public CTI CTI(ISeries<double> input, int length)
		{
			if (cacheCTI != null)
				for (int idx = 0; idx < cacheCTI.Length; idx++)
					if (cacheCTI[idx] != null && cacheCTI[idx].Length == length && cacheCTI[idx].EqualsInput(input))
						return cacheCTI[idx];
			return CacheIndicator<CTI>(new CTI(){ Length = length }, input, ref cacheCTI);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.CTI CTI(int length)
		{
			return indicator.CTI(Input, length);
		}

		public Indicators.CTI CTI(ISeries<double> input , int length)
		{
			return indicator.CTI(input, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.CTI CTI(int length)
		{
			return indicator.CTI(Input, length);
		}

		public Indicators.CTI CTI(ISeries<double> input , int length)
		{
			return indicator.CTI(input, length);
		}
	}
}

#endregion
