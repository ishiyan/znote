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
    public class UltimateSmoother : Indicator
    {
        private double a1, b1, c1, c2, c3;
        private Series<double> us;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = @"";
                Name = "UltimateSmoother";
                Calculate = Calculate.OnBarClose;
                IsOverlay = false;
                DisplayInDataBox = true;
                DrawOnPricePanel = true;
                DrawHorizontalGridLines = true;
                DrawVerticalGridLines = true;
                PaintPriceMarkers = true;
                ScaleJustification = NinjaTrader.Gui.Chart.ScaleJustification.Right;
                //Disable this property if your indicator requires custom values that cumulate with each new market data event. 
                //See Help Guide for additional information.
                IsSuspendedWhileInactive = true;
                AddPlot(Brushes.Red, "UltimateSmooth");
                Period = 20;
            }
            else if (State == State.DataLoaded)
            {
                us = new Series<double>(this, MaximumBarsLookBack.Infinite);
            }
        }

        protected override void OnBarUpdate()
        {
            a1 = Math.Exp(-1.414 * Math.PI / Period);
            b1 = 2 * a1 * Math.Cos(1.414 * Math.PI / Period);
            c2 = b1;
            c3 = -a1 * a1;
            c1 = (1 + c2 - c3) / 4;

            double result = Close[0];
            if (CurrentBar >= 4)
            {
                us[0] = (1 - c1) * Close[0] + (2 * c1 - c2) * Close[1] - (c1 + c3) * Close[2] + c2 * us[1] + c3 * us[2];
            }
            else
            {
                us[0] = Close[0];
            }

            Value[0] = us[0];
        }

        [Range(1, int.MaxValue), NinjaScriptProperty]
        [Display(Name = "Period", GroupName = "NinjaScriptParameters", Order = 0)]
        public int Period { get; set; }
    }
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private UltimateSmoother[] cacheUltimateSmoother;
		public UltimateSmoother UltimateSmoother(int period)
		{
			return UltimateSmoother(Input, period);
		}

		public UltimateSmoother UltimateSmoother(ISeries<double> input, int period)
		{
			if (cacheUltimateSmoother != null)
				for (int idx = 0; idx < cacheUltimateSmoother.Length; idx++)
					if (cacheUltimateSmoother[idx] != null && cacheUltimateSmoother[idx].Period == period && cacheUltimateSmoother[idx].EqualsInput(input))
						return cacheUltimateSmoother[idx];
			return CacheIndicator<UltimateSmoother>(new UltimateSmoother(){ Period = period }, input, ref cacheUltimateSmoother);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.UltimateSmoother UltimateSmoother(int period)
		{
			return indicator.UltimateSmoother(Input, period);
		}

		public Indicators.UltimateSmoother UltimateSmoother(ISeries<double> input , int period)
		{
			return indicator.UltimateSmoother(input, period);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.UltimateSmoother UltimateSmoother(int period)
		{
			return indicator.UltimateSmoother(Input, period);
		}

		public Indicators.UltimateSmoother UltimateSmoother(ISeries<double> input , int period)
		{
			return indicator.UltimateSmoother(input, period);
		}
	}
}

#endregion
