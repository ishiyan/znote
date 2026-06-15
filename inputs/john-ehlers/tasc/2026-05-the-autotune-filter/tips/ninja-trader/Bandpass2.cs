/// Ported to NinjaTrader 8 by NinjaTrader_ChelseaB
/// 
/// From the author:
/// Bandpass Function
/// (C) 2005-2022 John F. Ehlers

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
	public class Bandpass2 : Indicator
	{
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"Ehlers Bandpass Filter as published in the May 2026 Stocks and Commodities article titled ""The AutoTune Filter"" by John F. Ehlers.";
				Name				= "Bandpass2";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= false;
				BarsRequiredToPlot	= 3;

				Period				= 20;
				Bandwidth			= 0.25;

				AddPlot(Brushes.Blue, "Bandpass");
				AddLine(Brushes.DarkGray, 0, "Zero");
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < 3)
			{
				Default[0] = 0;
				return;
			}

			// L1 = Cosine(360 / Period);
			double l1 = Math.Cos(2 * Math.PI / Period);
			// G1 = Cosine(Bandwidth*360 / Period);
			double g1 = Math.Cos(Bandwidth * 2 * Math.PI / Period);

			if (g1 == 0)
			{
				Default[0] = 0;
				return;
			}

			// S1 = 1 / G1 - SquareRoot( 1 / (G1*G1) - 1);
			double s1 = 1.0 / g1 - Math.Sqrt(1.0 / (g1 * g1) - 1);

			// BP = .5*(1 - S1)*(Price - Price[2]) + L1*(1 + S1)*BP[1] - S1*BP[2];
			Default[0] = 0.5 * (1 - s1) * (Input[0] - Input[2]) + l1 * (1 + s1) * Default[1] - s1 * Default[2];
		}

		[NinjaScriptProperty]
		[Range(2, int.MaxValue)]
		[Display(Name = "Period", Description = "Center period of the bandpass filter", GroupName = "Parameters", Order = 0)]
		public int Period
		{ get; set; }

		[NinjaScriptProperty]
		[Range(0.01, 1.0)]
		[Display(Name = "Bandwidth", Description = "Bandwidth as a fraction of the center period", GroupName = "Parameters", Order = 1)]
		public double Bandwidth
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
		private Bandpass2[] cacheBandpass2;
		public Bandpass2 Bandpass2(int period, double bandwidth)
		{
			return Bandpass2(Input, period, bandwidth);
		}

		public Bandpass2 Bandpass2(ISeries<double> input, int period, double bandwidth)
		{
			if (cacheBandpass2 != null)
				for (int idx = 0; idx < cacheBandpass2.Length; idx++)
					if (cacheBandpass2[idx] != null && cacheBandpass2[idx].Period == period && cacheBandpass2[idx].Bandwidth == bandwidth && cacheBandpass2[idx].EqualsInput(input))
						return cacheBandpass2[idx];
			return CacheIndicator<Bandpass2>(new Bandpass2(){ Period = period, Bandwidth = bandwidth }, input, ref cacheBandpass2);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.Bandpass2 Bandpass2(int period, double bandwidth)
		{
			return indicator.Bandpass2(Input, period, bandwidth);
		}

		public Indicators.Bandpass2 Bandpass2(ISeries<double> input , int period, double bandwidth)
		{
			return indicator.Bandpass2(input, period, bandwidth);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.Bandpass2 Bandpass2(int period, double bandwidth)
		{
			return indicator.Bandpass2(Input, period, bandwidth);
		}

		public Indicators.Bandpass2 Bandpass2(ISeries<double> input , int period, double bandwidth)
		{
			return indicator.Bandpass2(input, period, bandwidth);
		}
	}
}

#endregion
