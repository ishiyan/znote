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
	public class UltimateBand : Indicator
	{
		private UltimateSmoother Smooth; 
		private double Sum, SD, UpprBnd, LowrBnd;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"UltimateBand Indicator as published in the May 2024 Stocks and Commodities article titled ""Ultimate Channels And Ultimate Bands"" by John F. Ehlers.";
				Name				= "UltimateBand";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= true;
				BarsRequiredToPlot	= 20;
				Length				= 20;
				NumSDs				= 1;
				AddPlot(Brushes.Blue, "UpperBand");
				AddPlot(Brushes.Blue, "LowerBand");
			}
			else if (State == State.DataLoaded)
			{
				Smooth = UltimateSmoother(Close, Length);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < BarsRequiredToPlot)
				return;
			
			Sum = 0.0;
			
			for (int count = 0; count < Length - 1; count++)
				Sum = Sum + (Close[count] - Smooth[count]) * (Close[count] - Smooth[count]);
			
			if (Sum.Equals(0.0) == false)
				SD = Math.Sqrt(Sum / Length);
			
			UpprBnd = Smooth[0] + NumSDs*SD;
			LowrBnd = Smooth[0] - NumSDs*SD;
			
			UpperBand[0] = UpprBnd;
			LowerBand[0] = LowrBnd;
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Length", Order=1, GroupName="Parameters")]
		public int Length
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="NumSDs", Order=2, GroupName="Parameters")]
		public int NumSDs
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> UpperBand
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> LowerBand
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
		private UltimateBand[] cacheUltimateBand;
		public UltimateBand UltimateBand(int length, int numSDs)
		{
			return UltimateBand(Input, length, numSDs);
		}

		public UltimateBand UltimateBand(ISeries<double> input, int length, int numSDs)
		{
			if (cacheUltimateBand != null)
				for (int idx = 0; idx < cacheUltimateBand.Length; idx++)
					if (cacheUltimateBand[idx] != null && cacheUltimateBand[idx].Length == length && cacheUltimateBand[idx].NumSDs == numSDs && cacheUltimateBand[idx].EqualsInput(input))
						return cacheUltimateBand[idx];
			return CacheIndicator<UltimateBand>(new UltimateBand(){ Length = length, NumSDs = numSDs }, input, ref cacheUltimateBand);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.UltimateBand UltimateBand(int length, int numSDs)
		{
			return indicator.UltimateBand(Input, length, numSDs);
		}

		public Indicators.UltimateBand UltimateBand(ISeries<double> input , int length, int numSDs)
		{
			return indicator.UltimateBand(input, length, numSDs);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.UltimateBand UltimateBand(int length, int numSDs)
		{
			return indicator.UltimateBand(Input, length, numSDs);
		}

		public Indicators.UltimateBand UltimateBand(ISeries<double> input , int length, int numSDs)
		{
			return indicator.UltimateBand(input, length, numSDs);
		}
	}
}

#endregion
