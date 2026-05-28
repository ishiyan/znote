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
	public class CyberneticOscillator : Indicator
	{
		private HighPassFilter hP;
		private SuperSmoother  lP;
		private RMS            rMS;
		
		protected override void OnStateChange()
		{			
			if (State == State.SetDefaults)
			{
				Description									= @"CyberneticOscillator Indicator as published in the June 2025 Stocks and Commodities article titled Making A Better Oscillator by John F. Ehlers.";
				Name										= "CyberneticOscillator";
				Calculate									= Calculate.OnBarClose;
				IsOverlay									= false;
				HPLength									= 30;
				LPLength									= 20;
				
				AddPlot(Brushes.Red, "CyberneticOscillator");
				AddLine(Brushes.Gray, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				//HP = $HighPass(Close, HPLength);
				hP = HighPassFilter(HPLength);
				//LP = $SuperSmoother(HP, LPLength);
				lP = SuperSmoother(hP,LPLength);
				//RMS = $RMS(LP, 100);
				rMS = RMS(lP,100);
			}
		}

		protected override void OnBarUpdate()
		{
			if (rMS[0] != 0)
				Default[0] = lP[0] / rMS[0];
		}
		
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "HPLength", GroupName = "Parameters", Order = 0)]
		public int HPLength
		{ get; set; }
		
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "LPLength", GroupName = "Parameters", Order = 1)]
		public int LPLength
		{ get; set; }
		
		[Browsable(false)]
		[XmlIgnore()]
		public Series<double> Default
		{ get { return Values[0]; } }
		
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private CyberneticOscillator[] cacheCyberneticOscillator;
		public CyberneticOscillator CyberneticOscillator(int hPLength, int lPLength)
		{
			return CyberneticOscillator(Input, hPLength, lPLength);
		}

		public CyberneticOscillator CyberneticOscillator(ISeries<double> input, int hPLength, int lPLength)
		{
			if (cacheCyberneticOscillator != null)
				for (int idx = 0; idx < cacheCyberneticOscillator.Length; idx++)
					if (cacheCyberneticOscillator[idx] != null && cacheCyberneticOscillator[idx].HPLength == hPLength && cacheCyberneticOscillator[idx].LPLength == lPLength && cacheCyberneticOscillator[idx].EqualsInput(input))
						return cacheCyberneticOscillator[idx];
			return CacheIndicator<CyberneticOscillator>(new CyberneticOscillator(){ HPLength = hPLength, LPLength = lPLength }, input, ref cacheCyberneticOscillator);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.CyberneticOscillator CyberneticOscillator(int hPLength, int lPLength)
		{
			return indicator.CyberneticOscillator(Input, hPLength, lPLength);
		}

		public Indicators.CyberneticOscillator CyberneticOscillator(ISeries<double> input , int hPLength, int lPLength)
		{
			return indicator.CyberneticOscillator(input, hPLength, lPLength);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.CyberneticOscillator CyberneticOscillator(int hPLength, int lPLength)
		{
			return indicator.CyberneticOscillator(Input, hPLength, lPLength);
		}

		public Indicators.CyberneticOscillator CyberneticOscillator(ISeries<double> input , int hPLength, int lPLength)
		{
			return indicator.CyberneticOscillator(input, hPLength, lPLength);
		}
	}
}

#endregion
