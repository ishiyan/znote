/// Ported to NinjaTrader 8 by NinjaTrader_ChelseaB
/// 
/// From the author:
/// RMS Function
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
	public class EhlersUltimateOscillator : Indicator
	{
		private HighPassFilter		highPassFilter1, highPassFilter2;
		private RMS					rMS;
		private Series<double>		signal;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description		= @"Ehlers Ultimate Oscillator (RMS) Indicator as published in the April 2025 Stocks and Commodities article titled The Ultimate Oscillator by John F. Ehlers.";
				Name			= "EhlersUltimateOscillator";
				Calculate		= Calculate.OnBarClose;
				IsOverlay		= false;
				BandEdge		= 20;
				Bandwidth		= 2;

				AddPlot(Brushes.Red, "Ultimate Oscillator");
				AddLine(Brushes.Gray, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				signal = new Series<double>(this);

				// HP1 = $HighPass(Close, Bandwidth*BandEdge);
				highPassFilter1	= HighPassFilter(BandEdge * Bandwidth);
				// HP2 = $HighPass(Close, BandEdge);
				highPassFilter2 = HighPassFilter(BandEdge);
				rMS				= RMS(signal, 100);
			}
		}

		protected override void OnBarUpdate()
		{
			// Signal = HP1 - HP2
			signal[0] = highPassFilter1[0] - highPassFilter2[0];

			// If RMS<> 0 Then UltimateOsc = Signal / RMS;
			if (rMS[0] != 0)
				Default[0] = signal[0] / rMS[0];
		}

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "BandEdge", GroupName = "Parameters", Order = 0)]
		public int BandEdge
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "Bandwidth", GroupName = "Parameters", Order = 1)]
		public int Bandwidth
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
		private EhlersUltimateOscillator[] cacheEhlersUltimateOscillator;
		public EhlersUltimateOscillator EhlersUltimateOscillator(int bandEdge, int bandwidth)
		{
			return EhlersUltimateOscillator(Input, bandEdge, bandwidth);
		}

		public EhlersUltimateOscillator EhlersUltimateOscillator(ISeries<double> input, int bandEdge, int bandwidth)
		{
			if (cacheEhlersUltimateOscillator != null)
				for (int idx = 0; idx < cacheEhlersUltimateOscillator.Length; idx++)
					if (cacheEhlersUltimateOscillator[idx] != null && cacheEhlersUltimateOscillator[idx].BandEdge == bandEdge && cacheEhlersUltimateOscillator[idx].Bandwidth == bandwidth && cacheEhlersUltimateOscillator[idx].EqualsInput(input))
						return cacheEhlersUltimateOscillator[idx];
			return CacheIndicator<EhlersUltimateOscillator>(new EhlersUltimateOscillator(){ BandEdge = bandEdge, Bandwidth = bandwidth }, input, ref cacheEhlersUltimateOscillator);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.EhlersUltimateOscillator EhlersUltimateOscillator(int bandEdge, int bandwidth)
		{
			return indicator.EhlersUltimateOscillator(Input, bandEdge, bandwidth);
		}

		public Indicators.EhlersUltimateOscillator EhlersUltimateOscillator(ISeries<double> input , int bandEdge, int bandwidth)
		{
			return indicator.EhlersUltimateOscillator(input, bandEdge, bandwidth);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.EhlersUltimateOscillator EhlersUltimateOscillator(int bandEdge, int bandwidth)
		{
			return indicator.EhlersUltimateOscillator(Input, bandEdge, bandwidth);
		}

		public Indicators.EhlersUltimateOscillator EhlersUltimateOscillator(ISeries<double> input , int bandEdge, int bandwidth)
		{
			return indicator.EhlersUltimateOscillator(input, bandEdge, bandwidth);
		}
	}
}

#endregion
