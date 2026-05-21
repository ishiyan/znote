/// Ported to NinjaTrader 8 by NinjaTrader_HelomS
/// 
/// From the author:
/// Laguerre Filter
/// (C)2025 John F. Ehlers

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
	public class ReversionIndex : Indicator
	{
		
		//
		
		private double dSum,absDSum;
		private Series<double> ratio;
		private SuperSmootherFunction smooth;
		private SuperSmootherFunction trigger;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @" Reversion Index as published in the January 2026 Stocks and Commodities article titled ""The Reversion Index"" by John F. Ehlers.";
				Name										= "ReversionIndex";
				Calculate									= Calculate.OnBarClose;
				IsOverlay									= false;
				
				// Length(20)
				Length										= 20;
				
				//Plot1(Smooth);
				//Plot3(Trigger);
				//Plot2(0);
				
				AddPlot(Brushes.Red, "Smooth");
				AddPlot(Brushes.Blue, "Trigger");
				AddLine(Brushes.Gray, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				ratio		= new Series<double>(this);
				
				// Smooth = $SuperSmoother(Ratio, 8);
				smooth		= SuperSmootherFunction(ratio, 8);
				
				// Trigger = $SuperSmoother(Ratio, 4);
				trigger		= SuperSmootherFunction(ratio, 4);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < Length + 1)
				return;
			
			// DeltaSum(0)
			// AbsDeltaSum(0)
			double dSum = 0;
			double absDSum = 0;
			
			// For count = 0 to Length - 1 Begin DeltaSum = DeltaSum + Close[count] - Close[count + 1];
			for (int count = 0; count < Length - 1; count++)
			{
				
				// AbsDeltaSum = AbsDeltaSum + AbsValue(Close[count] - Close[count + 1]);
				double delta = Close[count] - Close[count + 1];
				
				dSum += delta;
				absDSum += Math.Abs(delta);
			}

			// If AbsDeltaSum <> 0 Then Ratio = DeltaSum / AbsDeltaSum;
			if (absDSum != 0)
				ratio[0] = dSum / absDSum;
			else
				ratio[0] = 0;

			Values[0][0] = smooth[0];	// Plot1(Smooth);
			Values[1][0] = trigger[0];	// Plot3(Trigger);
		}
		
		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "Length", Order = 1, GroupName = "Parameters")]
		public int Length
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Smooth
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Trigger
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
		private ReversionIndex[] cacheReversionIndex;
		public ReversionIndex ReversionIndex(int length)
		{
			return ReversionIndex(Input, length);
		}

		public ReversionIndex ReversionIndex(ISeries<double> input, int length)
		{
			if (cacheReversionIndex != null)
				for (int idx = 0; idx < cacheReversionIndex.Length; idx++)
					if (cacheReversionIndex[idx] != null && cacheReversionIndex[idx].Length == length && cacheReversionIndex[idx].EqualsInput(input))
						return cacheReversionIndex[idx];
			return CacheIndicator<ReversionIndex>(new ReversionIndex(){ Length = length }, input, ref cacheReversionIndex);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.ReversionIndex ReversionIndex(int length)
		{
			return indicator.ReversionIndex(Input, length);
		}

		public Indicators.ReversionIndex ReversionIndex(ISeries<double> input , int length)
		{
			return indicator.ReversionIndex(input, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.ReversionIndex ReversionIndex(int length)
		{
			return indicator.ReversionIndex(Input, length);
		}

		public Indicators.ReversionIndex ReversionIndex(ISeries<double> input , int length)
		{
			return indicator.ReversionIndex(input, length);
		}
	}
}

#endregion
