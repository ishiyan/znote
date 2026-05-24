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
	public class MarketStateVariable : Indicator
	{
		private Phasor _phasor;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= "The Market State Variable Indicator as published in June 2020 Technical Analysis of Stocks And Commodities article titled \"Correlation as a Cycle Indicator\" by John F. Ehlers.";
				Name										= "MarketStateVariable";
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
				AddPlot(Brushes.Orange, "StateVariable");
				AddLine(Brushes.Aquamarine, 0, "ZeroLine");
			}
			else if (State == State.DataLoaded)
			{
				_phasor = Phasor(Period, InputPeriod);
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < Period) return;
			
			StateVariable[0] = 0;
				
			if(Math.Abs(_phasor.Angle[0] - _phasor.Angle[1]) < 9 && _phasor.Angle[0] < 0)
			{
				StateVariable[0] = -1;
			}
			if(Math.Abs(_phasor.Angle[0] - _phasor.Angle[1]) < 9 && _phasor.Angle[0] >= 0)
			{
				StateVariable[0] = 1;
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
		public Series<double> StateVariable
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
		private MarketStateVariable[] cacheMarketStateVariable;
		public MarketStateVariable MarketStateVariable(int period, int inputPeriod)
		{
			return MarketStateVariable(Input, period, inputPeriod);
		}

		public MarketStateVariable MarketStateVariable(ISeries<double> input, int period, int inputPeriod)
		{
			if (cacheMarketStateVariable != null)
				for (int idx = 0; idx < cacheMarketStateVariable.Length; idx++)
					if (cacheMarketStateVariable[idx] != null && cacheMarketStateVariable[idx].Period == period && cacheMarketStateVariable[idx].InputPeriod == inputPeriod && cacheMarketStateVariable[idx].EqualsInput(input))
						return cacheMarketStateVariable[idx];
			return CacheIndicator<MarketStateVariable>(new MarketStateVariable(){ Period = period, InputPeriod = inputPeriod }, input, ref cacheMarketStateVariable);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.MarketStateVariable MarketStateVariable(int period, int inputPeriod)
		{
			return indicator.MarketStateVariable(Input, period, inputPeriod);
		}

		public Indicators.MarketStateVariable MarketStateVariable(ISeries<double> input , int period, int inputPeriod)
		{
			return indicator.MarketStateVariable(input, period, inputPeriod);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.MarketStateVariable MarketStateVariable(int period, int inputPeriod)
		{
			return indicator.MarketStateVariable(Input, period, inputPeriod);
		}

		public Indicators.MarketStateVariable MarketStateVariable(ISeries<double> input , int period, int inputPeriod)
		{
			return indicator.MarketStateVariable(input, period, inputPeriod);
		}
	}
}

#endregion
