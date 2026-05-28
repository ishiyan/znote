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
	public class BandPassFilter : Indicator
	{
		private double L1, G1, S1;
		private double[] Trunc;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"BandPassFilter indicator as described in the July 2020 Stocks and Commodities article titled 'Truncated Indicators' by John F. Ehlers";
				Name										= "BandPassFilter";
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
				Period										= 20;
				Bandwidth									= 0.1;
				Length										= 10;
				AddPlot(Brushes.Red, "BP");
				AddPlot(Brushes.RoyalBlue, "BPT");
				AddLine(Brushes.Gray, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{				
				L1 = Math.Cos((360 * (Math.PI/180)) / Period);
				G1 = Math.Cos(Bandwidth * (360 * (Math.PI/180)) / Period);
				S1 = 1 / G1 - Math.Sqrt(1 / (G1*G1) -1);
				
				Trunc = new double[100];
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < 2 || CurrentBar < Length + 1)
			{
				BP[0] = 0;
				return;
			}
			
			BP[0] = .5*(1 - S1)*(Input[0] - Input[2]) + L1*(1 + S1)*BP[1] - S1*BP[2];
			
			//Stack the Trunc Array
			for ( int count = 99; count >= 2; count--)
				Trunc[count] = Trunc[count - 1];
			
			//Truncated Bandpass
			Trunc[Length + 2] = 0;
			Trunc[Length + 1] = 0;
			
			for ( int count = Length; count >= 1; count--)
			{
				Trunc[count] = .5*(1 - S1)*(Input[count - 1] - Input[count + 1]) +
				L1*(1 + S1)*Trunc[count + 1] - S1*Trunc[count + 2];
			}
			
			BPT[0] = Trunc[1];
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Period", Order=1, GroupName="Parameters")]
		public int Period
		{ get; set; }

		[NinjaScriptProperty]
		[Range(0.001, double.MaxValue)]
		[Display(Name="Bandwidth", Order=2, GroupName="Parameters")]
		public double Bandwidth
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Length", Order=3, GroupName="Parameters")]
		public int Length
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> BP
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> BPT
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
		private BandPassFilter[] cacheBandPassFilter;
		public BandPassFilter BandPassFilter(int period, double bandwidth, int length)
		{
			return BandPassFilter(Input, period, bandwidth, length);
		}

		public BandPassFilter BandPassFilter(ISeries<double> input, int period, double bandwidth, int length)
		{
			if (cacheBandPassFilter != null)
				for (int idx = 0; idx < cacheBandPassFilter.Length; idx++)
					if (cacheBandPassFilter[idx] != null && cacheBandPassFilter[idx].Period == period && cacheBandPassFilter[idx].Bandwidth == bandwidth && cacheBandPassFilter[idx].Length == length && cacheBandPassFilter[idx].EqualsInput(input))
						return cacheBandPassFilter[idx];
			return CacheIndicator<BandPassFilter>(new BandPassFilter(){ Period = period, Bandwidth = bandwidth, Length = length }, input, ref cacheBandPassFilter);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.BandPassFilter BandPassFilter(int period, double bandwidth, int length)
		{
			return indicator.BandPassFilter(Input, period, bandwidth, length);
		}

		public Indicators.BandPassFilter BandPassFilter(ISeries<double> input , int period, double bandwidth, int length)
		{
			return indicator.BandPassFilter(input, period, bandwidth, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.BandPassFilter BandPassFilter(int period, double bandwidth, int length)
		{
			return indicator.BandPassFilter(Input, period, bandwidth, length);
		}

		public Indicators.BandPassFilter BandPassFilter(ISeries<double> input , int period, double bandwidth, int length)
		{
			return indicator.BandPassFilter(input, period, bandwidth, length);
		}
	}
}

#endregion
