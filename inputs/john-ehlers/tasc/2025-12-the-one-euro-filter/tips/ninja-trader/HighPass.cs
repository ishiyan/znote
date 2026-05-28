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

namespace NinjaTrader.NinjaScript.Indicators
{
    public class HighPass : Indicator
    {
        private double a1;
        private double b1;
        private double c1;
        private double c2;
        private double c3;
        private Series<double> filt; 

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description 				= "2-pole HighPass filter by John F. Ehlers";
                Name 						= "HighPass";
                IsOverlay 					= false; 
                Calculate 					= Calculate.OnBarClose;
                Period 						= 48;
				
                AddPlot(new Stroke(Brushes.Green, 4), PlotStyle.Line, "HighPassFilter");
            }
            else if (State == State.DataLoaded)
            {
                filt = new Series<double>(this);
            }
        }

        protected override void OnBarUpdate()
        {
            // Source: https://www.mesasoftware.com/easylanguage/PredictiveIndicators.pdf (Page 4, Code Listing 2)

			// Calculate 'a1' coefficient
            a1 = Math.Exp(-1.414 * Math.PI / Period);

            // Calculate 'b1' coefficient
            b1 = 2 * a1 * Math.Cos(1.414 * 180 / Period * Math.PI / 180);

            // Assign 'c2' coefficient
            c2 = b1;

            // Assign 'c3' coefficient
            c3 = -a1 * a1;

            // Calculate 'c1' coefficient
            c1 = 1 - c2 - c3;

            if (CurrentBar < 2)
            {
                filt[0] = Input[0];
                Value[0] = Input[0];
                return;
            }

            // Calculate the current filtered value using the 2-pole HighPass filter formula.
            filt[0] = c1 * (Input[0] + Input[1]) / 2 + c2 * filt[1] + c3 * filt[2];
            Value[0] = filt[0];
        }
		
		#region Properties
		
		[Range(1, int.MaxValue)]
        [Display(Name="Period", Description="Period for the HighPass filter", Order=5, GroupName="Parameters")]
		[NinjaScriptProperty]
        public int Period { get; set; }
		
		#endregion
    }
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private HighPass[] cacheHighPass;
		public HighPass HighPass(int period)
		{
			return HighPass(Input, period);
		}

		public HighPass HighPass(ISeries<double> input, int period)
		{
			if (cacheHighPass != null)
				for (int idx = 0; idx < cacheHighPass.Length; idx++)
					if (cacheHighPass[idx] != null && cacheHighPass[idx].Period == period && cacheHighPass[idx].EqualsInput(input))
						return cacheHighPass[idx];
			return CacheIndicator<HighPass>(new HighPass(){ Period = period }, input, ref cacheHighPass);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.HighPass HighPass(int period)
		{
			return indicator.HighPass(Input, period);
		}

		public Indicators.HighPass HighPass(ISeries<double> input , int period)
		{
			return indicator.HighPass(input, period);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.HighPass HighPass(int period)
		{
			return indicator.HighPass(Input, period);
		}

		public Indicators.HighPass HighPass(ISeries<double> input , int period)
		{
			return indicator.HighPass(input, period);
		}
	}
}

#endregion
