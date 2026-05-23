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
	public class UndersampledDoubleMovingAverage : Indicator
	{
		private Series<double> Sample;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The Undersampled Double Moving Average indicator, as discussed in the April 2023 S&C article titled “Undersampling The Data As A Smoothing Technique Just Ignore Them” by John F. Ehlers";
				Name										= "UndersampledDoubleMovingAverage";
				Calculate									= Calculate.OnBarClose;
				IsOverlay									= true;
				DisplayInDataBox							= true;
				DrawOnPricePanel							= true;
				DrawHorizontalGridLines						= true;
				DrawVerticalGridLines						= true;
				PaintPriceMarkers							= true;
				ScaleJustification							= NinjaTrader.Gui.Chart.ScaleJustification.Right;
				//Disable this property if your indicator requires custom values that cumulate with each new market data event. 
				//See Help Guide for additional information.
				IsSuspendedWhileInactive					= true;
				FastLength					= 6;
				SlowLength					= 12;
				AddPlot(Brushes.Fuchsia, "FastAvg");
				AddPlot(Brushes.Blue, "SlowAvg");
			}
			else if (State == State.Configure)
			{
			}
			else if (State == State.DataLoaded)
			{				
				Sample = new Series<double>(this);
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < FastLength || CurrentBar < SlowLength) 
				return;
			
			Sample[0] = Sample[1];
				
			if(CurrentBar % 5 == 0)
			{
				Sample[0] = Close[0];
			}
			
			FastAvg[0] = HannFilter(Sample[0], FastLength);
			SlowAvg[0] = HannFilter(Sample[0], SlowLength);
			
		}
		
		private double HannFilter(double price, int Length)
		{
			double coef = 0;
			double filt = 0;
			
			for(int i = 1; i <= Length; i++)
			{
				filt += (1 - Math.Cos((Math.PI/180) * (360 * i/(Length+1)))) * Close[i-1];
				coef += (1 - Math.Cos((Math.PI/180) * (360 * i/(Length+1))));
			}
			
			if (coef != 0)
				return (filt / coef);
			else
				return -1;
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="FastLength", Order=1, GroupName="Parameters")]
		public int FastLength
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="SlowLength", Order=2, GroupName="Parameters")]
		public int SlowLength
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> FastAvg
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> SlowAvg
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
		private UndersampledDoubleMovingAverage[] cacheUndersampledDoubleMovingAverage;
		public UndersampledDoubleMovingAverage UndersampledDoubleMovingAverage(int fastLength, int slowLength)
		{
			return UndersampledDoubleMovingAverage(Input, fastLength, slowLength);
		}

		public UndersampledDoubleMovingAverage UndersampledDoubleMovingAverage(ISeries<double> input, int fastLength, int slowLength)
		{
			if (cacheUndersampledDoubleMovingAverage != null)
				for (int idx = 0; idx < cacheUndersampledDoubleMovingAverage.Length; idx++)
					if (cacheUndersampledDoubleMovingAverage[idx] != null && cacheUndersampledDoubleMovingAverage[idx].FastLength == fastLength && cacheUndersampledDoubleMovingAverage[idx].SlowLength == slowLength && cacheUndersampledDoubleMovingAverage[idx].EqualsInput(input))
						return cacheUndersampledDoubleMovingAverage[idx];
			return CacheIndicator<UndersampledDoubleMovingAverage>(new UndersampledDoubleMovingAverage(){ FastLength = fastLength, SlowLength = slowLength }, input, ref cacheUndersampledDoubleMovingAverage);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.UndersampledDoubleMovingAverage UndersampledDoubleMovingAverage(int fastLength, int slowLength)
		{
			return indicator.UndersampledDoubleMovingAverage(Input, fastLength, slowLength);
		}

		public Indicators.UndersampledDoubleMovingAverage UndersampledDoubleMovingAverage(ISeries<double> input , int fastLength, int slowLength)
		{
			return indicator.UndersampledDoubleMovingAverage(input, fastLength, slowLength);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.UndersampledDoubleMovingAverage UndersampledDoubleMovingAverage(int fastLength, int slowLength)
		{
			return indicator.UndersampledDoubleMovingAverage(Input, fastLength, slowLength);
		}

		public Indicators.UndersampledDoubleMovingAverage UndersampledDoubleMovingAverage(ISeries<double> input , int fastLength, int slowLength)
		{
			return indicator.UndersampledDoubleMovingAverage(input, fastLength, slowLength);
		}
	}
}

#endregion
