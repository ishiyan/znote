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
	public class MAD : Indicator
	{
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The MAD (Moving Average Difference) indicator was published in the October 2021 Technical Analysis of Stocks and Commodities article titled 'Cycle/Trend Analytics and the MAD Indicator' by John F. Ehlers";
				Name										= "MAD";
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
				ShortLength									= 8;
				LongLength									= 23;
				AddPlot(Brushes.Red, "MADPlot");
				AddLine(Brushes.RoyalBlue, 0, "ZeroLine");
			}
		}

		protected override void OnBarUpdate()
		{
			Value[0] = 100 *(SMA(Close,ShortLength)[0] - SMA(Close, LongLength)[0]) / SMA(Close, LongLength)[0]; 
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name=@"Short Length", Order=1, GroupName="Parameters")]
		public int ShortLength
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name=@"Long Length", Order=2, GroupName="Parameters")]
		public int LongLength
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> MADPlot
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
		private MAD[] cacheMAD;
		public MAD MAD(int shortLength, int longLength)
		{
			return MAD(Input, shortLength, longLength);
		}

		public MAD MAD(ISeries<double> input, int shortLength, int longLength)
		{
			if (cacheMAD != null)
				for (int idx = 0; idx < cacheMAD.Length; idx++)
					if (cacheMAD[idx] != null && cacheMAD[idx].ShortLength == shortLength && cacheMAD[idx].LongLength == longLength && cacheMAD[idx].EqualsInput(input))
						return cacheMAD[idx];
			return CacheIndicator<MAD>(new MAD(){ ShortLength = shortLength, LongLength = longLength }, input, ref cacheMAD);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.MAD MAD(int shortLength, int longLength)
		{
			return indicator.MAD(Input, shortLength, longLength);
		}

		public Indicators.MAD MAD(ISeries<double> input , int shortLength, int longLength)
		{
			return indicator.MAD(input, shortLength, longLength);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.MAD MAD(int shortLength, int longLength)
		{
			return indicator.MAD(Input, shortLength, longLength);
		}

		public Indicators.MAD MAD(ISeries<double> input , int shortLength, int longLength)
		{
			return indicator.MAD(input, shortLength, longLength);
		}
	}
}

#endregion
