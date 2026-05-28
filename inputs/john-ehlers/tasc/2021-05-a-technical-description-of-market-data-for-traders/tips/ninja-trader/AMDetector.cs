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
	public class AMDetector : Indicator
	{
		private double Deriv;
		private Series<double> derivAbsVal, Envel, Volatil;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"AMDetector indicator as detailed in the May 2021 Technical Analysis Stocks and Commodities article ‘A Technical Description of Market Data for Traders’ by John F Ehlers.";
				Name										= "AMDetector";
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
				AddPlot(Brushes.DarkOrange, "AMPlot");
				AddLine(Brushes.DimGray, 0, "ZeroLine");
			}
			else if (State == State.DataLoaded)
			{
				derivAbsVal = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				Envel = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				Volatil = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
			}
		}

		protected override void OnBarUpdate()
		{
			Deriv = Close[0] - Open[0];
			derivAbsVal[0] = Math.Abs(Deriv); 
			Envel[0] = MAX(derivAbsVal, 4)[0];
			Volatil[0] = SMA(Envel, 8)[0];
			
			AMPlot[0] = Volatil[0];
		}

		#region Properties

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> AMPlot
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
		private AMDetector[] cacheAMDetector;
		public AMDetector AMDetector()
		{
			return AMDetector(Input);
		}

		public AMDetector AMDetector(ISeries<double> input)
		{
			if (cacheAMDetector != null)
				for (int idx = 0; idx < cacheAMDetector.Length; idx++)
					if (cacheAMDetector[idx] != null &&  cacheAMDetector[idx].EqualsInput(input))
						return cacheAMDetector[idx];
			return CacheIndicator<AMDetector>(new AMDetector(), input, ref cacheAMDetector);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.AMDetector AMDetector()
		{
			return indicator.AMDetector(Input);
		}

		public Indicators.AMDetector AMDetector(ISeries<double> input )
		{
			return indicator.AMDetector(input);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.AMDetector AMDetector()
		{
			return indicator.AMDetector(Input);
		}

		public Indicators.AMDetector AMDetector(ISeries<double> input )
		{
			return indicator.AMDetector(input);
		}
	}
}

#endregion
