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
	public class FIRSMA : Indicator
	{
		private Series<double> Deriv;
		private Series<double> Filt;
		private int coef;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The FIR SMA Indicator was published in the September 2021 Technical Analysis of Stocks and Commodities article titled 'Triangle, Hamming, Hann Windowing' by John F. Ehlers";
				Name										= @"FIR SMA";
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
				Length										= 20;
				
				AddPlot(Brushes.Orange, "FIRSMAPlot");
				AddPlot(Brushes.Transparent, "ROC");
				AddLine(Brushes.RoyalBlue, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				Deriv = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				Filt = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < Length)
				return;
			
			Deriv[0] = Close[0] - Open[0];
			Filt[0] = 0;
			
			for (coef = 0; coef < Length; coef++)
				Filt[0] += Deriv[coef];
			
			if (coef != 0)
				Filt[0] = Filt[0]/coef;
			
			
			ROC[0] = (Length/6.28) * (Filt[0] - Filt[1]);
			
			FIRSMAPlot[0] = Filt[0];

		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Length", Order=1, Description="Period Length", GroupName="Parameters")]
		public int Length
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> FIRSMAPlot
		{
			get { return Values[0]; }
		}
		
		[Browsable(false)]
		[XmlIgnore]
		public Series<double> ROC
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
		private FIRSMA[] cacheFIRSMA;
		public FIRSMA FIRSMA(int length)
		{
			return FIRSMA(Input, length);
		}

		public FIRSMA FIRSMA(ISeries<double> input, int length)
		{
			if (cacheFIRSMA != null)
				for (int idx = 0; idx < cacheFIRSMA.Length; idx++)
					if (cacheFIRSMA[idx] != null && cacheFIRSMA[idx].Length == length && cacheFIRSMA[idx].EqualsInput(input))
						return cacheFIRSMA[idx];
			return CacheIndicator<FIRSMA>(new FIRSMA(){ Length = length }, input, ref cacheFIRSMA);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.FIRSMA FIRSMA(int length)
		{
			return indicator.FIRSMA(Input, length);
		}

		public Indicators.FIRSMA FIRSMA(ISeries<double> input , int length)
		{
			return indicator.FIRSMA(input, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.FIRSMA FIRSMA(int length)
		{
			return indicator.FIRSMA(Input, length);
		}

		public Indicators.FIRSMA FIRSMA(ISeries<double> input , int length)
		{
			return indicator.FIRSMA(input, length);
		}
	}
}

#endregion
