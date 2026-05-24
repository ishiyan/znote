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
	public class NETMyRSI : Indicator
	{
		private double CU;
		private double CD;
		private double[] X;
		private double[] Y;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"NETMyRSI indicator as detailed in the December 2020 Stocks and Commodities article titled ‘Clarify Your Indicators Using Kendall Correlation – Noise Elimination Technology’ by John F. Ehlers";
				Name										= "NETMyRSI";
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
				NETLength									= 14;
				AddPlot(Brushes.Red, "MyRSI");
				AddPlot(Brushes.Blue, "NET");
				AddLine(Brushes.DarkTurquoise, 0, "ZeroLine");			
			}
			else if (State == State.DataLoaded)
			{
				X = new double[NETLength];
				Y = new double[NETLength];
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < RSILength || CurrentBar < NETLength)
   				return;

			if (BarsInProgress != 0)
				return;

			CU = CD = 0;
			for (int count = 0; count < RSILength - 1; count++)
			{
				if (Close[count] - Close[count + 1] > 0)
					CU = CU + Close[count] - Close[count + 1];
				
				if (Close[count] - Close[count + 1] < 0)
					CD = CD + Close[count + 1] - Close[count];
			}
			
			if (CU + CD < 0 || CU + CD > 0)
				MyRSI[0] = (CU - CD) / (CU + CD);
			
			for (int count = 1; count < NETLength; count++)
			{
				X[count] = MyRSI[count - 1];
				Y[count] = -count;
			}
			
			double Num = 0;
			for (int count = 2; count < NETLength; count++)
			{
				for (int K = 1; K < count - 1; K++)
					Num = Num - Math.Sign(X[count] - X[K]);
			}
			
			double Denom = .5 * NETLength * (NETLength - 1);
			NET[0] = Num / Denom;
		}
		
		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="RSILength", Order=1, GroupName="Parameters")]
		public int RSILength
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="NETLength", Order=2, GroupName="Parameters")]
		public int NETLength
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> MyRSI
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> NET
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
		private NETMyRSI[] cacheNETMyRSI;
		public NETMyRSI NETMyRSI(int rSILength, int nETLength)
		{
			return NETMyRSI(Input, rSILength, nETLength);
		}

		public NETMyRSI NETMyRSI(ISeries<double> input, int rSILength, int nETLength)
		{
			if (cacheNETMyRSI != null)
				for (int idx = 0; idx < cacheNETMyRSI.Length; idx++)
					if (cacheNETMyRSI[idx] != null && cacheNETMyRSI[idx].RSILength == rSILength && cacheNETMyRSI[idx].NETLength == nETLength && cacheNETMyRSI[idx].EqualsInput(input))
						return cacheNETMyRSI[idx];
			return CacheIndicator<NETMyRSI>(new NETMyRSI(){ RSILength = rSILength, NETLength = nETLength }, input, ref cacheNETMyRSI);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.NETMyRSI NETMyRSI(int rSILength, int nETLength)
		{
			return indicator.NETMyRSI(Input, rSILength, nETLength);
		}

		public Indicators.NETMyRSI NETMyRSI(ISeries<double> input , int rSILength, int nETLength)
		{
			return indicator.NETMyRSI(input, rSILength, nETLength);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.NETMyRSI NETMyRSI(int rSILength, int nETLength)
		{
			return indicator.NETMyRSI(Input, rSILength, nETLength);
		}

		public Indicators.NETMyRSI NETMyRSI(ISeries<double> input , int rSILength, int nETLength)
		{
			return indicator.NETMyRSI(input, rSILength, nETLength);
		}
	}
}

#endregion
