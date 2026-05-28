/// Ported to NinjaTrader 8 by NinjaTrader_Eduardo
/// 
/// From the author:
/// Laguerre Filter
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
	public class LaguerreFilter : Indicator
	{
		private UltimateSmoother	l0;
		private Series<double>		l1, l2, l3, l4;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description		= @"LaguerreFilter Indicator as published in the April 2025 Stocks and Commodities article titled ""Laguerre Filters"" by John F. Ehlers.";
				Name			= "LaguerreFilter";
				Calculate		= Calculate.OnBarClose;
				IsOverlay		= true;

				Gama			= 0.8;
				Length			= 40;

				AddPlot(Brushes.Blue, "Laguerre Filter");
				AddPlot(Brushes.Orange, "Ultimate Smoother");
			}
			else if (State == State.DataLoaded)
			{
				l0	= UltimateSmoother(Input, Length);
				l1	= new Series<double>(this);
				l2	= new Series<double>(this);
				l3	= new Series<double>(this);
				l4	= new Series<double>(this);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < 1)
				return;

			// L1 = -gama*L0[1] + L0[1] + gama*L1[1];
			l1[0]			= -Gama * l0[1] + l0[1] + Gama * l1[1];
			// L2 = -gama * L1[1] + L1[1] + gama * L2[1];
			l2[0]			= -Gama * l1[1] + l1[1] + Gama * l2[1];
			// L3 = -gama*L2[1] + L2[1] + gama*L3[1];
			l3[0]			= -Gama * l2[1] + l2[1] + Gama * l3[1];
			// L4 = -gama*L3[1] + L3[1] + gama*L4[1];
			l4[0]			= -Gama * l3[1] + l3[1] + Gama * l4[1];
			// Laguerre = (L0 + 4*L1 + 6*L2 + 4*L3 + L5) / 16;
			Default[0]		= (l0[0] + 4 * l1[0] + 6 * l2[0] + 4 * l3[0] + l4[0]) / 16;
			Ultimate[0]		= l0[0];
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
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Ultimate
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
		private LaguerreFilter[] cacheLaguerreFilter;
		public LaguerreFilter LaguerreFilter(double gama, int length)
		{
			return LaguerreFilter(Input, gama, length);
		}

		public LaguerreFilter LaguerreFilter(ISeries<double> input, double gama, int length)
		{
			if (cacheLaguerreFilter != null)
				for (int idx = 0; idx < cacheLaguerreFilter.Length; idx++)
					if (cacheLaguerreFilter[idx] != null && cacheLaguerreFilter[idx].Gama == gama && cacheLaguerreFilter[idx].Length == length && cacheLaguerreFilter[idx].EqualsInput(input))
						return cacheLaguerreFilter[idx];
			return CacheIndicator<LaguerreFilter>(new LaguerreFilter(){ Gama = gama, Length = length }, input, ref cacheLaguerreFilter);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.LaguerreFilter LaguerreFilter(double gama, int length)
		{
			return indicator.LaguerreFilter(Input, gama, length);
		}

		public Indicators.LaguerreFilter LaguerreFilter(ISeries<double> input , double gama, int length)
		{
			return indicator.LaguerreFilter(input, gama, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.LaguerreFilter LaguerreFilter(double gama, int length)
		{
			return indicator.LaguerreFilter(Input, gama, length);
		}

		public Indicators.LaguerreFilter LaguerreFilter(ISeries<double> input , double gama, int length)
		{
			return indicator.LaguerreFilter(input, gama, length);
		}
	}
}

#endregion
