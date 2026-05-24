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
	public class PhasorAnalysis : Indicator
	{
		private CustomEnumNamespace.PhasorAnalysisPlot plotType = CustomEnumNamespace.PhasorAnalysisPlot.Phasor;
		private double count, Sx, Sy, Sxx, Sxy, Syy, X, Y, Real, Imag;
		//Phasor
		private Series<double> Angle;
		//Frequency
		private Series<double> DeltaAngle, DerivedPeriod;
		//Trend State
		private int TrendState;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The Phasor Analysis indicator as published in November 2022 Technical Analysis of Stocks and Commodities article ""Using Phasor Analysis To Identify Market Trend: Recurring Phase Of Cycle Analysis"" by John F. Ehlers";
				Name										= "PhasorAnalysis";
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
				Period										= 28;
				AddPlot(Brushes.Red, "Angle Plot");
				AddPlot(Brushes.White, "Reference");
				AddPlot(Brushes.Aqua, "90 Degree Line");
				AddPlot(Brushes.Aqua, "-90 Degree Line");
				AddPlot(Brushes.Red, "Frequency");
				AddPlot(Brushes.Red, "Trend State");
			}
			else if (State == State.DataLoaded)
			{
				Sx = 0;
				Sy = 0;
				Sxx = 0;
				Sxy = 0;
				Syy = 0;
				X = 0;
				Y = 0;
				Real = 0;
				Imag = 0;
				Angle = new Series<double>(this);
				DeltaAngle = new Series<double>(this);
				DerivedPeriod = new Series<double>(this);
				TrendState = 0;
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar <= Period)
				return;
			//Correlate with Cosine wave having a fixed period
			Sx = 0;
			Sy = 0;
			Sxx = 0;
			Sxy = 0;
			Syy = 0;
			for (int count = 1; count <= Period; count++)
			{
				X = Close[count - 1];
				Y = Math.Cos((360*(count -1) / Period) * Math.PI/180);
				Sx = Sx + X;
				Sy = Sy + Y;
				Sxx = Sxx + X*X;
				Sxy = Sxy + X*Y;
				Syy = Syy + Y*Y;
			}
			if ((Period*Sxx - Sx*Sx > 0) && (Period*Syy - Sy*Sy > 0))
				Real = (Period*Sxy - Sx*Sy) / Math.Sqrt((Period*Sxx - Sx*Sx)*(Period*Syy - Sy*Sy));
			
			//Correlate with a Negative Sine wave having a fixed period
			Sx = 0;
			Sy = 0;
			Sxx = 0;
			Sxy = 0;
			Syy = 0;
			for (int count = 1; count <= Period; count++)
			{
				X = Close[count - 1];
				Y = -Math.Sin((360*(count -1) / Period) * (Math.PI/180));
				Sx = Sx + X;
				Sy = Sy + Y;
				Sxx = Sxx + X*X;
				Sxy = Sxy + X*Y;
				Syy = Syy + Y*Y;
			}
			if ((Period*Sxx - Sx*Sx > 0) && (Period*Syy - Sy*Sy > 0))
				Imag = (Period*Sxy - Sx*Sy) / Math.Sqrt((Period*Sxx - Sx*Sx)*(Period*Syy - Sy*Sy));
			
			//Compute the angle as an arctangent function and resolve ambiguity
			if (Real != 0)
				Angle[0] = 90 - (Math.Atan(Imag / Real)) * (180/Math.PI);
			if (Real < 0)
				Angle[0] = Angle[0] - 180;
			
			//compensate for angle wraparound
			if (Math.Abs(Angle[1]) - Math.Abs(Angle[0] - 360) < Angle[0] - Angle[1] && Angle[0] > 90 && Angle[1] < -90)
				Angle[0] = Angle[0] - 360;
			
			//angle cannot go backwards
			if (Angle[0] < Angle[1] && ((Angle[0] > -135 && Angle[1] < 135) || (Angle[0] < -90 && Angle[1] < -90)))
				Angle[0] = Angle[1];
			
			switch (plotType)
			{
				case CustomEnumNamespace.PhasorAnalysisPlot.Phasor:
				{
					//Phasor Indicator
					AnglePlot[0] = Angle[0];
					Reference[0] = 0;
					Positive90[0] = 90;
					Negative90[0] = -90;
					break;
				}
				
				case CustomEnumNamespace.PhasorAnalysisPlot.Frequency:
				{
					//Frequency derived from rate-change of phase
					DeltaAngle[0] = Angle[0] - Angle[1];
					if (DeltaAngle[0] <= 0)
						DeltaAngle[0] = DeltaAngle[1];
					if (DeltaAngle[0] != 0)
						DerivedPeriod[0] = 360 / DeltaAngle[0];
					if (DerivedPeriod[0] > 60)
						DerivedPeriod[0] = 60;
					Frequency[0] = DerivedPeriod[0];
					break;
				}
				
				case CustomEnumNamespace.PhasorAnalysisPlot.TrendState:
				{
					//Trend State Variable
					TrendState = 0;
					if (Angle[0] - Angle[1] <= 6)
					{
						if (Angle[0] >= 90 || Angle[0] <= -90)
							TrendState = 1;
						else if (Angle[0] > -90 && Angle[0] < 90)
							TrendState = -1;
					}
					TrendStatePlot[0] = TrendState;
					break;
				}
			}
		}

		#region Properties
		[Display(Name="Plot Type", GroupName = "Parameters", Description="Choose a plot type.")]
		public CustomEnumNamespace.PhasorAnalysisPlot PlotType
		{
			get { return plotType; }
			set { plotType = value; }
		}
		
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Period", Description="Period", Order=1, GroupName="Parameters")]
		public int Period
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> AnglePlot
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Reference
		{
			get { return Values[1]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Positive90
		{
			get { return Values[2]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Negative90
		{
			get { return Values[3]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Frequency
		{
			get { return Values[4]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> TrendStatePlot
		{
			get { return Values[5]; }
		}
		#endregion

	}
}

namespace CustomEnumNamespace
{
	public enum PhasorAnalysisPlot
	{
		Phasor,
		Frequency,
		TrendState,
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private PhasorAnalysis[] cachePhasorAnalysis;
		public PhasorAnalysis PhasorAnalysis(int period)
		{
			return PhasorAnalysis(Input, period);
		}

		public PhasorAnalysis PhasorAnalysis(ISeries<double> input, int period)
		{
			if (cachePhasorAnalysis != null)
				for (int idx = 0; idx < cachePhasorAnalysis.Length; idx++)
					if (cachePhasorAnalysis[idx] != null && cachePhasorAnalysis[idx].Period == period && cachePhasorAnalysis[idx].EqualsInput(input))
						return cachePhasorAnalysis[idx];
			return CacheIndicator<PhasorAnalysis>(new PhasorAnalysis(){ Period = period }, input, ref cachePhasorAnalysis);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.PhasorAnalysis PhasorAnalysis(int period)
		{
			return indicator.PhasorAnalysis(Input, period);
		}

		public Indicators.PhasorAnalysis PhasorAnalysis(ISeries<double> input , int period)
		{
			return indicator.PhasorAnalysis(input, period);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.PhasorAnalysis PhasorAnalysis(int period)
		{
			return indicator.PhasorAnalysis(Input, period);
		}

		public Indicators.PhasorAnalysis PhasorAnalysis(ISeries<double> input , int period)
		{
			return indicator.PhasorAnalysis(input, period);
		}
	}
}

#endregion
