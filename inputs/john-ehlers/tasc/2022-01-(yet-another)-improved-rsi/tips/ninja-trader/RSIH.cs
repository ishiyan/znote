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
	public class RSIH : Indicator
	{
		private double CU;
		private double CD;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The RSIH - RSI with Hann Windowing indicator was published in the January 2022 Technical Analysis of Stocks and Commodities article titled '(Yet Another) Improved RSI' by John F. Ehlers.";
				Name										= "RSIH";
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
				RSILength									= 14;
				AddPlot(Brushes.Red, "RSIHPlot");
				AddLine(Brushes.RoyalBlue, 0, "ZeroLine");
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < RSILength)
				return;
			
			CU = 0;
			CD = 0;
			
			for(int i = 1; i <= RSILength; i++)
			{
				if(Close[i-1] - Close[i] > 0)
					CU += (1 - Math.Cos((Math.PI/180) * (360 * i/(RSILength + 1)))) * (Close[i-1] - Close[i]);
				if(Close[i] - Close[i-1] > 0)
					CD += (1 - Math.Cos((Math.PI/180) * (360 * i/(RSILength + 1)))) * (Close[i] - Close[i-1]);
			}
			
			if((CU + CD) != 0)
				Value[0] = (CU - CD)/(CU + CD);
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="RSI Length", Description="RSI Period Length", Order=1, GroupName="Parameters")]
		public int RSILength
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> RSIHPlot
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
		private RSIH[] cacheRSIH;
		public RSIH RSIH(int rSILength)
		{
			return RSIH(Input, rSILength);
		}

		public RSIH RSIH(ISeries<double> input, int rSILength)
		{
			if (cacheRSIH != null)
				for (int idx = 0; idx < cacheRSIH.Length; idx++)
					if (cacheRSIH[idx] != null && cacheRSIH[idx].RSILength == rSILength && cacheRSIH[idx].EqualsInput(input))
						return cacheRSIH[idx];
			return CacheIndicator<RSIH>(new RSIH(){ RSILength = rSILength }, input, ref cacheRSIH);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.RSIH RSIH(int rSILength)
		{
			return indicator.RSIH(Input, rSILength);
		}

		public Indicators.RSIH RSIH(ISeries<double> input , int rSILength)
		{
			return indicator.RSIH(input, rSILength);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.RSIH RSIH(int rSILength)
		{
			return indicator.RSIH(Input, rSILength);
		}

		public Indicators.RSIH RSIH(ISeries<double> input , int rSILength)
		{
			return indicator.RSIH(input, rSILength);
		}
	}
}

#endregion
