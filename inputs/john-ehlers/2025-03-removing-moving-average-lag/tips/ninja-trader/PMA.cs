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
/// The prediction is a second-order prediction, using the rate change of slope for the calculation

//This namespace holds Indicators in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Indicators
{
    public class PMA : Indicator
    {
        private Series<double>	smaVal, slopeVal;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description		= @"PMA indicator as published in the March 2025 Stocks and Commodities article titled ""Removing Moving Average Lag"" by John F. Ehlers.";
                Name			= "PMA";
                Calculate		= Calculate.OnBarClose;
                IsOverlay		= true;
                Length			= 20;

                AddPlot(Brushes.Blue, "PMA");
                AddPlot(Brushes.Red, "Predict");
            }
            else if (State == State.DataLoaded)
            {
                smaVal		= new Series<double>(this, MaximumBarsLookBack.Infinite);
                slopeVal	= new Series<double>(this, MaximumBarsLookBack.Infinite);
            }
        }

        private void CalculatePMA(ISeries<double> prices, int length)
        {
            double	Sx = 0, Sy = 0, Sxx = 0, Syy = 0, Sxy = 0;

			// For count = 1 to Length Begin
			for (int count = 1; count <= length; count++)
            {
				// Sx = Sx + count;
                Sx	+= count;
				// Sy = Sy + Price[count - 1];
                Sy	+= prices[count - 1];
				// Sxx = Sxx + count*count;
                Sxx	+= count * count;
				// Syy = Syy + Price[count - 1]*Price[count - 1];
                Syy	+= prices[count - 1] * prices[count - 1];
				// Sxy = Sxy + count*Price[count - 1];
                Sxy	+= count * prices[count - 1];
            }

			// Slope = -(Length*Sxy - Sx*Sy) / (Length*Sxx - Sx*Sx);
            slopeVal[0]	= -(length * Sxy - Sx * Sy) / (length * Sxx - Sx * Sx);
			// SMA = Sy / Length;
			smaVal[0]	= Sy / length;
			// Plot PMA
			// PMA = SMA + Slope*Length / 2;
			Default[0] = smaVal[0] + slopeVal[0] * length / 2;
		}

        protected override void OnBarUpdate()
        {
            if (CurrentBar < Length)
                return;

            // Calculate PMA
            CalculatePMA(Input, Length);
			
			// Calculate and plot Predict
			if (CurrentBar >= 2)
                Predict[0] = Default[0] + 0.5 * (slopeVal[0] - slopeVal[2]) * Length;
        }

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "Length", Order = 1, GroupName = "Parameters")]
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

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Slope
		{ get { return slopeVal; } }
		#endregion

	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private PMA[] cachePMA;
		public PMA PMA(int length)
		{
			return PMA(Input, length);
		}

		public PMA PMA(ISeries<double> input, int length)
		{
			if (cachePMA != null)
				for (int idx = 0; idx < cachePMA.Length; idx++)
					if (cachePMA[idx] != null && cachePMA[idx].Length == length && cachePMA[idx].EqualsInput(input))
						return cachePMA[idx];
			return CacheIndicator<PMA>(new PMA(){ Length = length }, input, ref cachePMA);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.PMA PMA(int length)
		{
			return indicator.PMA(Input, length);
		}

		public Indicators.PMA PMA(ISeries<double> input , int length)
		{
			return indicator.PMA(input, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.PMA PMA(int length)
		{
			return indicator.PMA(Input, length);
		}

		public Indicators.PMA PMA(ISeries<double> input , int length)
		{
			return indicator.PMA(input, length);
		}
	}
}

#endregion
