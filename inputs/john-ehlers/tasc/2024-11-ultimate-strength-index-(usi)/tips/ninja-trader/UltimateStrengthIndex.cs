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
	public class UltimateStrengthIndex : Indicator
	{
		private Series<double>		sU, sD;
		private UltimateSmoother	uSU, uSD;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description		= @"UltimateSmoother Indicator as published in the November 2024 Stocks and Commodities article titled """"Ultimate Strength Index (USI)"""" by John F. Ehlers.""";
				Name			= "UltimateStrengthIndex";
				Calculate		= Calculate.OnBarClose;
				IsOverlay		= false;
				
				Length			= 14;

                AddPlot(Brushes.Blue, "USI");
                AddLine(Brushes.Black, 0, "ZeroLine");
			}
			else if (State == State.DataLoaded)
			{
				sU = new Series<double>(this, MaximumBarsLookBack.Infinite);	
				sD = new Series<double>(this, MaximumBarsLookBack.Infinite);
				
				uSU = UltimateSmoother(SMA(sU, 4), Length);
				uSD = UltimateSmoother(SMA(sD, 4), Length);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < 1)
				return;

            sU[0]	= (Close[0] > Close[1]) ? (Close[0] - Close[1]) : 0;
            sD[0]	= (Close[0] < Close[1]) ? (Close[1] - Close[0]) : 0;

            if ((uSU[0] + uSD[0] != 0) && (uSU[0] > 0.01) && (uSD[0] > 0.01))
                USI[0] = (uSU[0] - uSD[0]) / (uSU[0] + uSD[0]);
            else
                USI[0] = USI[1];
		}

        [NinjaScriptProperty]
        [Range(1, int.MaxValue), Display(Name = "Length", GroupName = "Parameters", Order = 0)]
        public int Length
		{ get; set; }
		
		[XmlIgnore]
		public Series<double> USI
		{ get { return Values[0]; } }
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private UltimateStrengthIndex[] cacheUltimateStrengthIndex;
		public UltimateStrengthIndex UltimateStrengthIndex(int length)
		{
			return UltimateStrengthIndex(Input, length);
		}

		public UltimateStrengthIndex UltimateStrengthIndex(ISeries<double> input, int length)
		{
			if (cacheUltimateStrengthIndex != null)
				for (int idx = 0; idx < cacheUltimateStrengthIndex.Length; idx++)
					if (cacheUltimateStrengthIndex[idx] != null && cacheUltimateStrengthIndex[idx].Length == length && cacheUltimateStrengthIndex[idx].EqualsInput(input))
						return cacheUltimateStrengthIndex[idx];
			return CacheIndicator<UltimateStrengthIndex>(new UltimateStrengthIndex(){ Length = length }, input, ref cacheUltimateStrengthIndex);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.UltimateStrengthIndex UltimateStrengthIndex(int length)
		{
			return indicator.UltimateStrengthIndex(Input, length);
		}

		public Indicators.UltimateStrengthIndex UltimateStrengthIndex(ISeries<double> input , int length)
		{
			return indicator.UltimateStrengthIndex(input, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.UltimateStrengthIndex UltimateStrengthIndex(int length)
		{
			return indicator.UltimateStrengthIndex(Input, length);
		}

		public Indicators.UltimateStrengthIndex UltimateStrengthIndex(ISeries<double> input , int length)
		{
			return indicator.UltimateStrengthIndex(input, length);
		}
	}
}

#endregion
