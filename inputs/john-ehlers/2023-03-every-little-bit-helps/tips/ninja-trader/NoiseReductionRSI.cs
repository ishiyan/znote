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

/// Traders' Tips Stocks & Commodities March 2023 by John Ehlers, titled “Every Little Bit Helps: Averaging The Open And Close To Reduce Noise.”
namespace NinjaTrader.NinjaScript.Indicators
{
	public class NoiseReductionRSI : Indicator
	{
		private Series<double> openCloseSeries;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= "\"Every Little Bit Helps: Averaging The Open And Close To Reduce Noise.\" Displays an example of filtering out noise using the average of the Open and Close series. The Red plot (CTest) shows an RSI value and the Blue plot (OCTest) shows the Open Close average RSI value.";
				Name										= "Noise Reduction RSI";
				Calculate									= Calculate.OnBarClose;
				IsOverlay									= false;
				DisplayInDataBox							= true;
				DrawOnPricePanel							= true;
				DrawHorizontalGridLines						= true;
				DrawVerticalGridLines						= true;
				PaintPriceMarkers							= true;
				ScaleJustification							= NinjaTrader.Gui.Chart.ScaleJustification.Right;
				IsSuspendedWhileInactive					= true;
				RSIPeriod					= 14;
				AddPlot(Brushes.Red, "CTest");
				AddPlot(Brushes.Blue, "OCTest");
			}
			else if (State == State.DataLoaded)
			{				
				openCloseSeries = new Series<double>(this);
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < RSIPeriod) return;
            CTest[0] = RSI(RSIPeriod, 1)[0];
			openCloseSeries[0] = (Open[0] + Close[0]) / 2;
            OCTest[0] = RSI(openCloseSeries, RSIPeriod, 1)[0];        
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="RSI Period", Order=1, GroupName="Parameters")]
		public int RSIPeriod
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> CTest
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> OCTest
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
		private NoiseReductionRSI[] cacheNoiseReductionRSI;
		public NoiseReductionRSI NoiseReductionRSI(int rSIPeriod)
		{
			return NoiseReductionRSI(Input, rSIPeriod);
		}

		public NoiseReductionRSI NoiseReductionRSI(ISeries<double> input, int rSIPeriod)
		{
			if (cacheNoiseReductionRSI != null)
				for (int idx = 0; idx < cacheNoiseReductionRSI.Length; idx++)
					if (cacheNoiseReductionRSI[idx] != null && cacheNoiseReductionRSI[idx].RSIPeriod == rSIPeriod && cacheNoiseReductionRSI[idx].EqualsInput(input))
						return cacheNoiseReductionRSI[idx];
			return CacheIndicator<NoiseReductionRSI>(new NoiseReductionRSI(){ RSIPeriod = rSIPeriod }, input, ref cacheNoiseReductionRSI);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.NoiseReductionRSI NoiseReductionRSI(int rSIPeriod)
		{
			return indicator.NoiseReductionRSI(Input, rSIPeriod);
		}

		public Indicators.NoiseReductionRSI NoiseReductionRSI(ISeries<double> input , int rSIPeriod)
		{
			return indicator.NoiseReductionRSI(input, rSIPeriod);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.NoiseReductionRSI NoiseReductionRSI(int rSIPeriod)
		{
			return indicator.NoiseReductionRSI(Input, rSIPeriod);
		}

		public Indicators.NoiseReductionRSI NoiseReductionRSI(ISeries<double> input , int rSIPeriod)
		{
			return indicator.NoiseReductionRSI(input, rSIPeriod);
		}
	}
}

#endregion
