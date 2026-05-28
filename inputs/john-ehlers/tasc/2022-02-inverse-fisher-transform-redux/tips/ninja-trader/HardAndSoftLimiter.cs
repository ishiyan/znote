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
	public class HardAndSoftLimiter : Indicator
	{
		private Series<double> Deriv, Clip, IFish;
		private double RMS, NDeriv = 0;
		private const int MAXPERIOD = 50;
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The HardSoftLimiter indicator as published in February 2022 Technical Analysis of Stocks and Commodities article “An Elegant Oscillator Inverse Fisher Transform Redux” by John F. Ehlers";
				Name										= "HardAndSoftLimiter";
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
				AddPlot(Brushes.Tomato, "Integ");
				AddPlot(Brushes.SteelBlue, "IntegClip");
				AddLine(Brushes.White, 0, "ZeroLine");
			}
			else if(State == State.DataLoaded)
			{
				Deriv = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				Clip = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				IFish = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < 5)
			{
				return;
			}
			
			Deriv[0] = Close[0] - Close[2];
			
			RMS = 0;
			
			if(CurrentBar < MAXPERIOD)
			{
				for(int i = 0; i < CurrentBar; i++)
				{
					RMS += Math.Pow(Deriv[i], 2);
				}
			} 
			else
			{
				for(int i = 0; i < MAXPERIOD; i++)
				{
					RMS += Math.Pow(Deriv[i], 2);
				}
			}	
			
			if(RMS != 0)
				RMS = Math.Sqrt(RMS/50);
			NDeriv = Deriv[0]/RMS;
			
			IFish[0] = (Math.Exp(2*NDeriv)-1)/(Math.Exp(2*NDeriv)+1);
			Integ[0] = (IFish[0] + 2*IFish[1] + 3*IFish[2] + 3*IFish[3] + 2*IFish[4] + IFish[5]) / 12;
			
			Clip[0] = Deriv[0];
			if(Clip[0] > 1)
				Clip[0] = 1;
			else if(Clip[0] < -1)
				Clip[0] = -1;
			IntegClip[0] = (Clip[0] + 2*Clip[1] + 3*Clip[2] + 3*Clip[3] + 2*Clip[4] + Clip[5]) / 12;
		}

		#region Properties

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Integ
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> IntegClip
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
		private HardAndSoftLimiter[] cacheHardAndSoftLimiter;
		public HardAndSoftLimiter HardAndSoftLimiter()
		{
			return HardAndSoftLimiter(Input);
		}

		public HardAndSoftLimiter HardAndSoftLimiter(ISeries<double> input)
		{
			if (cacheHardAndSoftLimiter != null)
				for (int idx = 0; idx < cacheHardAndSoftLimiter.Length; idx++)
					if (cacheHardAndSoftLimiter[idx] != null &&  cacheHardAndSoftLimiter[idx].EqualsInput(input))
						return cacheHardAndSoftLimiter[idx];
			return CacheIndicator<HardAndSoftLimiter>(new HardAndSoftLimiter(), input, ref cacheHardAndSoftLimiter);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.HardAndSoftLimiter HardAndSoftLimiter()
		{
			return indicator.HardAndSoftLimiter(Input);
		}

		public Indicators.HardAndSoftLimiter HardAndSoftLimiter(ISeries<double> input )
		{
			return indicator.HardAndSoftLimiter(input);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.HardAndSoftLimiter HardAndSoftLimiter()
		{
			return indicator.HardAndSoftLimiter(Input);
		}

		public Indicators.HardAndSoftLimiter HardAndSoftLimiter(ISeries<double> input )
		{
			return indicator.HardAndSoftLimiter(input);
		}
	}
}

#endregion
