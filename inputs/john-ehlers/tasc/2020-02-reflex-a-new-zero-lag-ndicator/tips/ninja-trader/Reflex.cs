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
	public class Reflex : Indicator
	{
		private Series<double> MS;
		private Series<double> Filter;
		double a1, b1, c1, c2, c3, Slope, sum;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"Reflex indicator as published in February 2020 Technical Analysis of Stocks and Commodities article Reflex: A New Zero-Lag Indicator by John F. Ehlers.";
				Name										= "Reflex";
				Calculate									= Calculate.OnBarClose;
				IsOverlay									= false;
				DisplayInDataBox							= true;
				DrawOnPricePanel							= true;
				DrawHorizontalGridLines						= true;
				DrawVerticalGridLines						= true;
				PaintPriceMarkers							= true;
				ScaleJustification							= NinjaTrader.Gui.Chart.ScaleJustification.Right;
				//Disable this property if your indicator requires custom values that cumulate with each new market data event. 
				//See Help Guide for additional information.
				IsSuspendedWhileInactive					= true;
				Length					= 20;
				AddPlot(Brushes.Red, "ReflexPlot");
				AddLine(Brushes.Gray, 0, "ZLine");
			}
			else if (State == State.Configure)
			{
				a1 = Math.Exp(-1.414*Math.PI/(0.5*Length));
				b1 = 2*a1*Math.Cos(1.414*Math.PI/(0.5*Length));
				c2 = b1;
				c3 = -a1*a1;
				c1 = 1-c2-c3;
			}
			else if (State == State.DataLoaded)
			{				
				MS = new Series<double>(this);
				Filter = new Series<double>(this);
			}
		}

		protected override void OnBarUpdate()
		{
			
			if(CurrentBar < 2)
			{
				Filter[0] = 0;
				return;
			}
			
			Filter[0] = c1*(Close[0] + Close[1])/2 + c2*Filter[1]+c3*Filter[2];
			MS[0] = 0;
			
			if(CurrentBar < Length)
				return;						
			
			Slope = (Filter[Length] - Filter[0])/Length;
			
			for(int i = 1; i <= Length; i++)
				sum += (Filter[0] + i*Slope) - Filter[i];
			
			sum /= Length;
			
			MS[0] = 0.04*sum*sum + 0.96*MS[1];
			
			
			if(MS[0] != 0)
				ReflexPlot[0] = sum/Math.Sqrt(MS[0]);
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Length", Order=1, GroupName="Parameters")]
		public int Length
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> ReflexPlot
		{
			get { return Values[0]; }
		}
		#endregion

	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private Reflex[] cacheReflex;
		public Reflex Reflex(int length)
		{
			return Reflex(Input, length);
		}

		public Reflex Reflex(ISeries<double> input, int length)
		{
			if (cacheReflex != null)
				for (int idx = 0; idx < cacheReflex.Length; idx++)
					if (cacheReflex[idx] != null && cacheReflex[idx].Length == length && cacheReflex[idx].EqualsInput(input))
						return cacheReflex[idx];
			return CacheIndicator<Reflex>(new Reflex(){ Length = length }, input, ref cacheReflex);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.Reflex Reflex(int length)
		{
			return indicator.Reflex(Input, length);
		}

		public Indicators.Reflex Reflex(ISeries<double> input , int length)
		{
			return indicator.Reflex(input, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.Reflex Reflex(int length)
		{
			return indicator.Reflex(Input, length);
		}

		public Indicators.Reflex Reflex(ISeries<double> input , int length)
		{
			return indicator.Reflex(input, length);
		}
	}
}

#endregion
