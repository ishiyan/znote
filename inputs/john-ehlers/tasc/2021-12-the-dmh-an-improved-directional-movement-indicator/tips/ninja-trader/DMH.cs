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
	public class DMH : Indicator
	{
		#region Variables
			private double SF, UpperMove, LowerMove, DMSum, coef;
			private Series<double> PlusDM, MinusDM, Ema, Dmh;
			private int count;
		#endregion
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The DMH indicator, as detailed in the December 2021 S&C article titled ‘The DMH: An Improved Directional Movement Indicator’ by John F. Ehlers.";
				Name										= "DMH";
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
				Length										= 14;
				AddPlot(Brushes.Red, "DMHPlot");
				AddLine(Brushes.White, 0, "ZeroLine");
			}
			else if (State == State.DataLoaded)
			{
				PlusDM = new Series<double>(this);
				MinusDM = new Series<double>(this);
				Ema = new Series<double>(this);
				Dmh = new Series<double>(this);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < 1)
				return;
			
			SF = 1 / (double)Length;
			
			UpperMove = High[0] - High[1];
			LowerMove = Low[1] - Low[0];
			
			PlusDM[0] = 0;
			MinusDM[0] = 0;
			
			if (UpperMove > LowerMove && UpperMove > 0)
				PlusDM[0] = UpperMove;
			else if (LowerMove > UpperMove && LowerMove > 0)
				MinusDM[0] = LowerMove;
			
			Ema[0] = SF * (PlusDM[0] - MinusDM[0]) + (1 - SF) * Ema[1];
			
			//Smooth Directional Movements with Hann Windowed FIR filter
			DMSum = 0;
			coef = 0;
			
			for (count = 1; count < Length; count++)
			{
				DMSum = DMSum + (1 - Math.Cos((360 * Math.PI / 180) * count / ((double)Length + 1))) * Ema[count -1];
				coef = coef + (1 - Math.Cos((360 * Math.PI / 180) * count / ((double)Length + 1)));
			}
			
			if (coef != 0)
				Dmh[0] = DMSum / coef;
			
			DMHPlot[0] = Dmh[0];
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(0, int.MaxValue)]
		[Display(Name="Length", Order=1, GroupName="Parameters")]
		public int Length
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> DMHPlot
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
		private DMH[] cacheDMH;
		public DMH DMH(int length)
		{
			return DMH(Input, length);
		}

		public DMH DMH(ISeries<double> input, int length)
		{
			if (cacheDMH != null)
				for (int idx = 0; idx < cacheDMH.Length; idx++)
					if (cacheDMH[idx] != null && cacheDMH[idx].Length == length && cacheDMH[idx].EqualsInput(input))
						return cacheDMH[idx];
			return CacheIndicator<DMH>(new DMH(){ Length = length }, input, ref cacheDMH);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.DMH DMH(int length)
		{
			return indicator.DMH(Input, length);
		}

		public Indicators.DMH DMH(ISeries<double> input , int length)
		{
			return indicator.DMH(input, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.DMH DMH(int length)
		{
			return indicator.DMH(Input, length);
		}

		public Indicators.DMH DMH(ISeries<double> input , int length)
		{
			return indicator.DMH(input, length);
		}
	}
}

#endregion
