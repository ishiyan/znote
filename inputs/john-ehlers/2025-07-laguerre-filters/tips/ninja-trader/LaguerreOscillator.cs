/// Ported to NinjaTrader 8 by NinjaTrader_Eduardo
/// 
/// From the author:
/// Laguerre Oscillator
/// (C)2015 - 2022 John F. Ehlers
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
	public class LaguerreOscillator : Indicator
	{
		private UltimateSmoother	l0;
		private Series<double>		l1, difference;
		private RMS					rms;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description		= @"LaguerreOscillator Indicator as published in the April 2025 Stocks and Commodities article titled ""Laguerre Filters"" by John F. Ehlers.";
				Name			= "LaguerreOscillator";
				Calculate		= Calculate.OnBarClose;
				IsOverlay		= false;
				Gama			= 0.5;
				Length			= 30;

				AddPlot(Brushes.Tomato, "LaguerreOscillator");
				AddLine(Brushes.Black, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				difference 		= new Series<double>(this);
				// L0 = $UltimateSmoother(Close, Length);
				l0 				= UltimateSmoother(Input, Length);
				l1 				= new Series<double>(this);
				// RMS = $RMS(L0 - L1, 100);
				rms				= RMS(difference, 100);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < 1)
				return;

			// L1 = -gama *L0 + L0[1] + gama *L1[1];
			l1[0]			= -Gama * l0[1] + l0[1] + Gama * l1[1];
			difference[0]	= l0[0] - l1[0];

			// If RMS<> 0 Then LaguerreOsc = (L0 - L1) / RMS;
			if (rms[0] != 0)
				Default[0] = difference[0] / rms[0];
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(0, double.MaxValue)]
		[Display(Name = "Gamma", Order = 1, GroupName = "Parameters")]
		public double Gama
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "Length", Order = 2, GroupName = "Parameters")]
		public int Length
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Default
		{ get { return Values[0]; } }
		#endregion
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private LaguerreOscillator[] cacheLaguerreOscillator;
		public LaguerreOscillator LaguerreOscillator(double gama, int length)
		{
			return LaguerreOscillator(Input, gama, length);
		}

		public LaguerreOscillator LaguerreOscillator(ISeries<double> input, double gama, int length)
		{
			if (cacheLaguerreOscillator != null)
				for (int idx = 0; idx < cacheLaguerreOscillator.Length; idx++)
					if (cacheLaguerreOscillator[idx] != null && cacheLaguerreOscillator[idx].Gama == gama && cacheLaguerreOscillator[idx].Length == length && cacheLaguerreOscillator[idx].EqualsInput(input))
						return cacheLaguerreOscillator[idx];
			return CacheIndicator<LaguerreOscillator>(new LaguerreOscillator(){ Gama = gama, Length = length }, input, ref cacheLaguerreOscillator);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.LaguerreOscillator LaguerreOscillator(double gama, int length)
		{
			return indicator.LaguerreOscillator(Input, gama, length);
		}

		public Indicators.LaguerreOscillator LaguerreOscillator(ISeries<double> input , double gama, int length)
		{
			return indicator.LaguerreOscillator(input, gama, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.LaguerreOscillator LaguerreOscillator(double gama, int length)
		{
			return indicator.LaguerreOscillator(Input, gama, length);
		}

		public Indicators.LaguerreOscillator LaguerreOscillator(ISeries<double> input , double gama, int length)
		{
			return indicator.LaguerreOscillator(input, gama, length);
		}
	}
}

#endregion
