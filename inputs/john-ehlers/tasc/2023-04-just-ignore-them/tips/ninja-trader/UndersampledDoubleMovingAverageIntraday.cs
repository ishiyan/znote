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
	public class UndersampledDoubleMovingAverageIntraday : Indicator
	{
		private double gap;
		private Series<double> Degap;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"Enter the description for your new custom Indicator here.";
				Name										= "UndersampledDoubleMovingAverageIntraday";
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
				BeginningDate								= DateTime.Now;
				FastLength									= 20;
				SlowLength									= 40;
				AddPlot(Brushes.Fuchsia, "FastAvg");
				AddPlot(Brushes.Blue, "SlowAvg");
			}

			else if (State == State.DataLoaded)
			{				
				Degap = new Series<double>(this);
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < FastLength || CurrentBar < SlowLength) 
				return;
			
			Degap[0] = Degap[1];
			
			if (Times[0][0].TimeOfDay == new TimeSpan(6, 45, 0))
			{
				gap = Close[0] - Degap[1];
				Degap[0] = Close[0] - gap;
			}
			
			if (Times[0][0].TimeOfDay == new TimeSpan(8, 00, 0) ||
				Times[0][0].TimeOfDay == new TimeSpan(9, 00, 0) ||
				Times[0][0].TimeOfDay == new TimeSpan(10, 00, 0) ||
				Times[0][0].TimeOfDay == new TimeSpan(11, 00, 0) ||
				Times[0][0].TimeOfDay == new TimeSpan(13, 15, 0)
				) 
			{
				Degap[0] = Close[0]-gap;
			}
			
			if(DateTime.Compare(Time[0], BeginningDate) < 0)
				Degap[0] = Close[0];
			
			FastAvg[0] = HannFilter(Degap[0], FastLength);
			SlowAvg[0] = HannFilter(Degap[0], SlowLength);
			
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
		[Display(Name="BeginningDate")]
		public DateTime BeginningDate { get; set; }
		
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
		private UndersampledDoubleMovingAverageIntraday[] cacheUndersampledDoubleMovingAverageIntraday;
		public UndersampledDoubleMovingAverageIntraday UndersampledDoubleMovingAverageIntraday(DateTime beginningDate, int fastLength, int slowLength)
		{
			return UndersampledDoubleMovingAverageIntraday(Input, beginningDate, fastLength, slowLength);
		}

		public UndersampledDoubleMovingAverageIntraday UndersampledDoubleMovingAverageIntraday(ISeries<double> input, DateTime beginningDate, int fastLength, int slowLength)
		{
			if (cacheUndersampledDoubleMovingAverageIntraday != null)
				for (int idx = 0; idx < cacheUndersampledDoubleMovingAverageIntraday.Length; idx++)
					if (cacheUndersampledDoubleMovingAverageIntraday[idx] != null && cacheUndersampledDoubleMovingAverageIntraday[idx].BeginningDate == beginningDate && cacheUndersampledDoubleMovingAverageIntraday[idx].FastLength == fastLength && cacheUndersampledDoubleMovingAverageIntraday[idx].SlowLength == slowLength && cacheUndersampledDoubleMovingAverageIntraday[idx].EqualsInput(input))
						return cacheUndersampledDoubleMovingAverageIntraday[idx];
			return CacheIndicator<UndersampledDoubleMovingAverageIntraday>(new UndersampledDoubleMovingAverageIntraday(){ BeginningDate = beginningDate, FastLength = fastLength, SlowLength = slowLength }, input, ref cacheUndersampledDoubleMovingAverageIntraday);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.UndersampledDoubleMovingAverageIntraday UndersampledDoubleMovingAverageIntraday(DateTime beginningDate, int fastLength, int slowLength)
		{
			return indicator.UndersampledDoubleMovingAverageIntraday(Input, beginningDate, fastLength, slowLength);
		}

		public Indicators.UndersampledDoubleMovingAverageIntraday UndersampledDoubleMovingAverageIntraday(ISeries<double> input , DateTime beginningDate, int fastLength, int slowLength)
		{
			return indicator.UndersampledDoubleMovingAverageIntraday(input, beginningDate, fastLength, slowLength);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.UndersampledDoubleMovingAverageIntraday UndersampledDoubleMovingAverageIntraday(DateTime beginningDate, int fastLength, int slowLength)
		{
			return indicator.UndersampledDoubleMovingAverageIntraday(Input, beginningDate, fastLength, slowLength);
		}

		public Indicators.UndersampledDoubleMovingAverageIntraday UndersampledDoubleMovingAverageIntraday(ISeries<double> input , DateTime beginningDate, int fastLength, int slowLength)
		{
			return indicator.UndersampledDoubleMovingAverageIntraday(input, beginningDate, fastLength, slowLength);
		}
	}
}

#endregion
