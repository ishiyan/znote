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
	public class UltimateChannel : Indicator
	{
		private double TH, TL, STR, UpprChnnl, LwrChnnl;
		private Series<double> diffSeries;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"UltimateChannel Indicator as published in the May 2024 Stocks and Commodities article titled ""Ultimate Channels And Ultimate Bands"" by John F. Ehlers.";
				Name				= "UltimateChannel";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= true;
				BarsRequiredToPlot	= 20;
				STRLength			= 20;
				Length				= 20;
				NumSTRs				= 1;
				AddPlot(Brushes.Blue, "UpperChannel");
				AddPlot(Brushes.Blue, "LowerChannel");
			}
			else if (State == State.DataLoaded)
			{
				diffSeries = new Series<double>(this);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < BarsRequiredToPlot)
				return;
			
			TH = (Close[1] > High[0]) ? Close[0] : High[0];
			TL = (Close[1] < Low[0]) ? Close[1] : Low[0];
			
			diffSeries[0] = TH - TL;
			
			STR = UltimateSmoother(diffSeries, STRLength)[0];
			
			UpprChnnl = UltimateSmoother(Close, Length)[0] + NumSTRs*STR;
			LwrChnnl = UltimateSmoother(Close, Length)[0] - NumSTRs*STR;
			
			UpperChannel[0] = UpprChnnl;
			LowerChannel[0] = LwrChnnl;
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="STRLength", Order=1, GroupName="Parameters")]
		public int STRLength
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Length", Order=2, GroupName="Parameters")]
		public int Length
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="NumSTRs", Order=3, GroupName="Parameters")]
		public int NumSTRs
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> UpperChannel
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> LowerChannel
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
		private UltimateChannel[] cacheUltimateChannel;
		public UltimateChannel UltimateChannel(int sTRLength, int length, int numSTRs)
		{
			return UltimateChannel(Input, sTRLength, length, numSTRs);
		}

		public UltimateChannel UltimateChannel(ISeries<double> input, int sTRLength, int length, int numSTRs)
		{
			if (cacheUltimateChannel != null)
				for (int idx = 0; idx < cacheUltimateChannel.Length; idx++)
					if (cacheUltimateChannel[idx] != null && cacheUltimateChannel[idx].STRLength == sTRLength && cacheUltimateChannel[idx].Length == length && cacheUltimateChannel[idx].NumSTRs == numSTRs && cacheUltimateChannel[idx].EqualsInput(input))
						return cacheUltimateChannel[idx];
			return CacheIndicator<UltimateChannel>(new UltimateChannel(){ STRLength = sTRLength, Length = length, NumSTRs = numSTRs }, input, ref cacheUltimateChannel);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.UltimateChannel UltimateChannel(int sTRLength, int length, int numSTRs)
		{
			return indicator.UltimateChannel(Input, sTRLength, length, numSTRs);
		}

		public Indicators.UltimateChannel UltimateChannel(ISeries<double> input , int sTRLength, int length, int numSTRs)
		{
			return indicator.UltimateChannel(input, sTRLength, length, numSTRs);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.UltimateChannel UltimateChannel(int sTRLength, int length, int numSTRs)
		{
			return indicator.UltimateChannel(Input, sTRLength, length, numSTRs);
		}

		public Indicators.UltimateChannel UltimateChannel(ISeries<double> input , int sTRLength, int length, int numSTRs)
		{
			return indicator.UltimateChannel(input, sTRLength, length, numSTRs);
		}
	}
}

#endregion
