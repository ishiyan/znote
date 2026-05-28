//
// Copyright (C) 2025, NinjaTrader LLC <www.ninjatrader.com>
// NinjaTrader reserves the right to modify or overwrite this NinjaScript component
// Coded by NinjaTrader_Jesse
//
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

/// Note from the author:
/// Slope is provided as an output of the $PMA function.
/// Slope is used to demonstrate a generalized oscillator and its generalized prediction

//This namespace holds Indicators in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Indicators
{
	public class PMASlope : Indicator
	{
		private PMA	pma;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description		= @"PMASlope indicator as published in the March 2025 Stocks and Commodities article titled ""Removing Moving Average Lag"" by John F. Ehlers.";
				Name			= "PMASlope";
				Calculate		= Calculate.OnBarClose;
				IsOverlay		= false;
				Length			= 20;

				AddPlot(Brushes.Blue, "Slope");
				AddPlot(Brushes.Red, "Predict");
			}
			else if (State == State.DataLoaded)
			{
				// ReturnValue = $PMA(Close, Length, PMA, Slope, SMA);
				pma = PMA(Length);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < Length)
				return;

			// Plot Slope
			Default[0]	= pma.Slope[0];

			// Calculate and plot Slope Predict
			if (CurrentBar >= 4)
				// Predict = 1.5*Slope - .5*Slope[4];
				Predict[0] = 1.5 * pma.Slope[0] - 0.5 * pma.Slope[4];
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "Length", Order = 5, GroupName = "Parameters")]
		public int Length
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Default
		{ get { return Values[0]; } }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Predict
		{ get { return Values[1]; } }
		#endregion
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private PMASlope[] cachePMASlope;
		public PMASlope PMASlope(int length)
		{
			return PMASlope(Input, length);
		}

		public PMASlope PMASlope(ISeries<double> input, int length)
		{
			if (cachePMASlope != null)
				for (int idx = 0; idx < cachePMASlope.Length; idx++)
					if (cachePMASlope[idx] != null && cachePMASlope[idx].Length == length && cachePMASlope[idx].EqualsInput(input))
						return cachePMASlope[idx];
			return CacheIndicator<PMASlope>(new PMASlope(){ Length = length }, input, ref cachePMASlope);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.PMASlope PMASlope(int length)
		{
			return indicator.PMASlope(Input, length);
		}

		public Indicators.PMASlope PMASlope(ISeries<double> input , int length)
		{
			return indicator.PMASlope(input, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.PMASlope PMASlope(int length)
		{
			return indicator.PMASlope(Input, length);
		}

		public Indicators.PMASlope PMASlope(ISeries<double> input , int length)
		{
			return indicator.PMASlope(input, length);
		}
	}
}

#endregion
