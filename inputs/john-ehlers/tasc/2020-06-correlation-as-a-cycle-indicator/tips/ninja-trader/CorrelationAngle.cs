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
	public class CorrelationAngle : Indicator
	{
		private double Sx = 0;
		private double Sy = 0;
		private double Sxx = 0;
		private double Sxy = 0;
		private double Syy = 0;
		private Series<double> price;
		protected override void OnStateChange()
		{	
			if (State == State.SetDefaults)
			{
				Description									= "The Correlation Angle Indicator as published in June 2020 Technical Analysis of Stocks And Commodities article titled \"Correlation as a Cycle Indicator\" by John F. Ehlers.";
				Name										= "CorrelationAngle";
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
				Period										= 20;
				InputPeriod									= 0;
				AddLine(Brushes.Aquamarine, 0, "ZeroLine");
				AddPlot(Brushes.Coral, "Real");
				AddPlot(Brushes.ForestGreen, "Imag");
				AddPlot(Brushes.BlueViolet, "PricePlot");			
			}
			else if (State == State.DataLoaded)
			{
				price = new Series<double>(this);
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < Period) return;
			
			if(InputPeriod != 0)
			{
				price[0] = Math.Sin(6.28 * CurrentBar / InputPeriod);
				PricePlot[0] = price[0];
			}
			else
			{
				price[0] = Close[0];
			}
			
			Sx = 0;
			Sy = 0;
			Sxx = 0;
			Sxy = 0;
			Syy = 0;
			
			for(int i = 1; i <= Period; i++)
			{
				double x = price[i-1];
				double y = Math.Cos(6.28*(i-1)/Period);
				Sx += x;
				Sy += y;
				Sxx += x*x;
				Sxy += x*y;
				Syy += y*y;
			}
			
			if(Period*Sxx - Sx*Sx > 0 && Period*Syy - Sy*Sy > 0)
			{
				Real[0] = (Period*Sxy - Sx*Sy) / Math.Sqrt((Period*Sxx - Sx*Sx) * (Period*Syy - Sy*Sy));
			}	
		
			Sx = 0;
			Sy = 0;
			Sxx = 0;
			Sxy = 0;
			Syy = 0;
			
			for(int i = 1; i <= Period; i++)
			{
				double x = price[i-1];
				double y = -Math.Sin(6.28*(i-1)/Period);
				Sx += x;
				Sy += y;
				Sxx += x*x;
				Sxy += x*y;
				Syy += y*y;
			}
			
			if(Period*Sxx - Sx*Sx > 0 && Period*Syy - Sy*Sy > 0)
			{
				Imag[0] = (Period*Sxy - Sx*Sy) / Math.Sqrt((Period*Sxx - Sx*Sx) * (Period*Syy - Sy*Sy));
			}
			
			
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Period", Order=1, GroupName="Parameters")]
		public int Period
		{ get; set; }

		[NinjaScriptProperty]
		[Range(0, int.MaxValue)]
		[Display(Name="InputPeriod", Order=2, GroupName="Parameters")]
		public int InputPeriod
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Real
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Imag
		{
			get { return Values[1]; }
		}
		
		[Browsable(false)]
		[XmlIgnore]
		public Series<double> PricePlot
		{
			get { return Values[2]; }
		}
		
		
		#endregion

	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private CorrelationAngle[] cacheCorrelationAngle;
		public CorrelationAngle CorrelationAngle(int period, int inputPeriod)
		{
			return CorrelationAngle(Input, period, inputPeriod);
		}

		public CorrelationAngle CorrelationAngle(ISeries<double> input, int period, int inputPeriod)
		{
			if (cacheCorrelationAngle != null)
				for (int idx = 0; idx < cacheCorrelationAngle.Length; idx++)
					if (cacheCorrelationAngle[idx] != null && cacheCorrelationAngle[idx].Period == period && cacheCorrelationAngle[idx].InputPeriod == inputPeriod && cacheCorrelationAngle[idx].EqualsInput(input))
						return cacheCorrelationAngle[idx];
			return CacheIndicator<CorrelationAngle>(new CorrelationAngle(){ Period = period, InputPeriod = inputPeriod }, input, ref cacheCorrelationAngle);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.CorrelationAngle CorrelationAngle(int period, int inputPeriod)
		{
			return indicator.CorrelationAngle(Input, period, inputPeriod);
		}

		public Indicators.CorrelationAngle CorrelationAngle(ISeries<double> input , int period, int inputPeriod)
		{
			return indicator.CorrelationAngle(input, period, inputPeriod);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.CorrelationAngle CorrelationAngle(int period, int inputPeriod)
		{
			return indicator.CorrelationAngle(Input, period, inputPeriod);
		}

		public Indicators.CorrelationAngle CorrelationAngle(ISeries<double> input , int period, int inputPeriod)
		{
			return indicator.CorrelationAngle(input, period, inputPeriod);
		}
	}
}

#endregion
