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
	public class MADH : Indicator
	{
		private double LongLength;
		private double Filt1;
		private double Filt2;
		private double coef;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The MADH (Moving Average Difference - Hann) indicator was published in the November 2021 Technical Analysis of Stocks and Commodities article titled 'The MAD Indicator, Enhanced' by John F. Ehlers";
				Name										= "MADH";
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
				DominantCycle								= 27;
				AddLine(Brushes.RoyalBlue, 0, "ZeroLine");
				AddPlot(Brushes.Gold, "MADHPlot");
			}
			else if (State == State.Configure)
			{
			}
		}

		protected override void OnBarUpdate()
		{
			LongLength = Math.Truncate((double)ShortLength + (double)DominantCycle / 2);
			
			if (CurrentBar < LongLength)
				return;
			
			Filt1 = 0;
			coef = 0;
			
			for (int i = 1; i <= ShortLength; i++)
			{
				Filt1 += (1 - Math.Cos((Math.PI/180) * (360 * i/(ShortLength+1)))) * Close[i-1];
				coef += (1 - Math.Cos((Math.PI/180) * (360 * i/(ShortLength+1))));
			}
			
			if (coef != 0)
				Filt1 = Filt1 / coef;
			
			Filt2 = 0;
			coef = 0;
			
			for (int i = 1; i <= LongLength; i++)
			{
				Filt2 += (1 - Math.Cos((Math.PI/180) * (360 * i/(LongLength+1)))) * Close[i-1];
				coef += (1 - Math.Cos((Math.PI/180) * (360 * i/(LongLength+1))));
			}

			if (coef != 0)
				Filt2 = Filt2 / coef;
			
			if (Filt2 != 0)
				Value[0] = 100 * (Filt1 - Filt2) / Filt2;
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name=@"Short Length", Description="Short Length", Order=1, GroupName="Parameters")]
		public int ShortLength
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name=@"Dominant Cycle", Description="Dominant Cycle", Order=2, GroupName="Parameters")]
		public int DominantCycle
		{ get; set; }


		[Browsable(false)]
		[XmlIgnore]
		public Series<double> MADHPlot
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
		private MADH[] cacheMADH;
		public MADH MADH(int shortLength, int dominantCycle)
		{
			return MADH(Input, shortLength, dominantCycle);
		}

		public MADH MADH(ISeries<double> input, int shortLength, int dominantCycle)
		{
			if (cacheMADH != null)
				for (int idx = 0; idx < cacheMADH.Length; idx++)
					if (cacheMADH[idx] != null && cacheMADH[idx].ShortLength == shortLength && cacheMADH[idx].DominantCycle == dominantCycle && cacheMADH[idx].EqualsInput(input))
						return cacheMADH[idx];
			return CacheIndicator<MADH>(new MADH(){ ShortLength = shortLength, DominantCycle = dominantCycle }, input, ref cacheMADH);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.MADH MADH(int shortLength, int dominantCycle)
		{
			return indicator.MADH(Input, shortLength, dominantCycle);
		}

		public Indicators.MADH MADH(ISeries<double> input , int shortLength, int dominantCycle)
		{
			return indicator.MADH(input, shortLength, dominantCycle);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.MADH MADH(int shortLength, int dominantCycle)
		{
			return indicator.MADH(Input, shortLength, dominantCycle);
		}

		public Indicators.MADH MADH(ISeries<double> input , int shortLength, int dominantCycle)
		{
			return indicator.MADH(input, shortLength, dominantCycle);
		}
	}
}

#endregion
