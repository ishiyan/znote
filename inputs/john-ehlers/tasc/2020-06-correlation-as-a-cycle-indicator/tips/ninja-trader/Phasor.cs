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
	public class Phasor : Indicator
	{
		private CorrelationAngle _correlation;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= "The Phasor Indicator as published in June 2020 Technical Analysis of Stocks And Commodities article titled \"Correlation as a Cycle Indicator\" by John F. Ehlers.";
				Name										= "Phasor";
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
				AddPlot(Brushes.DodgerBlue, "Angle");
			}
			else if (State == State.Configure)
			{
			}
			else if(State == State.DataLoaded)
			{
				_correlation = CorrelationAngle(Period, InputPeriod);
			}
		}
		
		public static double ToDegrees(double radians)
		{
		    double degrees = (180 / Math.PI) * radians;
		    return (degrees);
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < Period) return;
			
			if(_correlation.Imag[0] != 0)
			{
				Angle[0] = (ToDegrees(1.57 + Math.Atan(_correlation.Real[0]/_correlation.Imag[0])));
			}
			if(_correlation.Imag[0] > 0)
			{
				Angle[0] -= 180;
			}
			
			if(Angle[1] - Angle[0] < 270 && Angle[0] < Angle[1])
			{
				Angle[0] = Angle[1];
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
		public Series<double> Angle
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
		private Phasor[] cachePhasor;
		public Phasor Phasor(int period, int inputPeriod)
		{
			return Phasor(Input, period, inputPeriod);
		}

		public Phasor Phasor(ISeries<double> input, int period, int inputPeriod)
		{
			if (cachePhasor != null)
				for (int idx = 0; idx < cachePhasor.Length; idx++)
					if (cachePhasor[idx] != null && cachePhasor[idx].Period == period && cachePhasor[idx].InputPeriod == inputPeriod && cachePhasor[idx].EqualsInput(input))
						return cachePhasor[idx];
			return CacheIndicator<Phasor>(new Phasor(){ Period = period, InputPeriod = inputPeriod }, input, ref cachePhasor);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.Phasor Phasor(int period, int inputPeriod)
		{
			return indicator.Phasor(Input, period, inputPeriod);
		}

		public Indicators.Phasor Phasor(ISeries<double> input , int period, int inputPeriod)
		{
			return indicator.Phasor(input, period, inputPeriod);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.Phasor Phasor(int period, int inputPeriod)
		{
			return indicator.Phasor(Input, period, inputPeriod);
		}

		public Indicators.Phasor Phasor(ISeries<double> input , int period, int inputPeriod)
		{
			return indicator.Phasor(input, period, inputPeriod);
		}
	}
}

#endregion
