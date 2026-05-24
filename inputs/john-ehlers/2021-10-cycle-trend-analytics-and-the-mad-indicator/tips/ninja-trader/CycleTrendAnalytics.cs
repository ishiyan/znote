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
	public class CycleTrendAnalytics : Indicator
	{
		private CustomCycleTrend.indiSetting ctMode			= CustomCycleTrend.indiSetting.Cycle;
		private bool Cycle;
		private int Length;
		private int NormalLength;
		private byte Color1;
		private byte Color2;
		private byte Color3;
		private Series<double> Price;
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The Cycle/Trend Analytics indicator was published in the October 2021 Technical Analysis of Stocks and Commodities article titled 'Cycle/Trend Analytics and the MAD Indicator' by John F. Ehlers";
				Name										= @"Cycle/Trend Analytics";
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
				Length										= 0;
				NormalLength								= 0;
				Color1										= 255;
				Color2										= 0;
				Color3										= 0;
				AddLine(Brushes.RoyalBlue, 0, "Plot1");
				for (int i = 0; i < 27; i++)
				{
					string PlotName = "Plot" + (i+4).ToString();
					AddPlot(Brushes.Transparent, PlotName);
				}
				AddPlot(Brushes.Aqua, "Plot2");
				AddPlot(Brushes.Green, "Plot3");

			}
			else if (State == State.Configure)
			{
				switch (ctMode)
				{
					case CustomCycleTrend.indiSetting.Cycle:
					{
						Cycle = true;
						break;
					}
					case CustomCycleTrend.indiSetting.Trend:
					{
						Cycle = false;
						break;
					}
				}
			}
			else if ( State == State.DataLoaded)
			{
				Price = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
			}
		}

		protected override void OnBarUpdate()
		{
			Price[0] = Close[0];
			if(Cycle == true)
			{
				Price[0] = Math.Sin((Math.PI/180) * (360 * CurrentBar/30));
				Values[27][0] = Price[0];
				Values[28][0] = SMA(Price,5)[0] - SMA(Price,30)[0];
			}

			for (Length = 5; Length <=30; Length++)
			{
				Color2 = (byte)(306 - 10.2 * Length);
				Values[Length-4][0] = Price[0] - SMA(Price, Length)[0];
				
				Brush myBrush = new SolidColorBrush(Color.FromRgb(Color1, Color2, Color3));
				myBrush.Freeze();
				Plots[Length - 4].Brush = myBrush;
			}
			
		}

		#region Properties
		// Creates the user definable parameter for the CT type.
		[NinjaScriptProperty]
		[Display(Name=@"CT Mode", GroupName = "Parameters", Description="Choose a Cycle/Trend Type.")]
		public CustomCycleTrend.indiSetting CTMode
		{
			get { return ctMode; }
			set { ctMode = value; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Plot2
		{
			get { return Values[27]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Plot3
		{
			get { return Values[28]; }
		}
		#endregion

	}
}

namespace CustomCycleTrend
{
	public enum indiSetting
	{
		Cycle,
		Trend,
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private CycleTrendAnalytics[] cacheCycleTrendAnalytics;
		public CycleTrendAnalytics CycleTrendAnalytics(CustomCycleTrend.indiSetting cTMode)
		{
			return CycleTrendAnalytics(Input, cTMode);
		}

		public CycleTrendAnalytics CycleTrendAnalytics(ISeries<double> input, CustomCycleTrend.indiSetting cTMode)
		{
			if (cacheCycleTrendAnalytics != null)
				for (int idx = 0; idx < cacheCycleTrendAnalytics.Length; idx++)
					if (cacheCycleTrendAnalytics[idx] != null && cacheCycleTrendAnalytics[idx].CTMode == cTMode && cacheCycleTrendAnalytics[idx].EqualsInput(input))
						return cacheCycleTrendAnalytics[idx];
			return CacheIndicator<CycleTrendAnalytics>(new CycleTrendAnalytics(){ CTMode = cTMode }, input, ref cacheCycleTrendAnalytics);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.CycleTrendAnalytics CycleTrendAnalytics(CustomCycleTrend.indiSetting cTMode)
		{
			return indicator.CycleTrendAnalytics(Input, cTMode);
		}

		public Indicators.CycleTrendAnalytics CycleTrendAnalytics(ISeries<double> input , CustomCycleTrend.indiSetting cTMode)
		{
			return indicator.CycleTrendAnalytics(input, cTMode);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.CycleTrendAnalytics CycleTrendAnalytics(CustomCycleTrend.indiSetting cTMode)
		{
			return indicator.CycleTrendAnalytics(Input, cTMode);
		}

		public Indicators.CycleTrendAnalytics CycleTrendAnalytics(ISeries<double> input , CustomCycleTrend.indiSetting cTMode)
		{
			return indicator.CycleTrendAnalytics(input, cTMode);
		}
	}
}

#endregion
