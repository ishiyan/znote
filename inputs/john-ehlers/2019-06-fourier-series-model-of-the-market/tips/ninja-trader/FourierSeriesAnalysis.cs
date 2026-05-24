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
	public class FourierSeriesAnalysis : Indicator
	{
		private int count;
		private double Bandwidth;
		private double G1;
        private double G2;
        private double G3;
        private double S1;
        private double S2;
        private double S3;
        private double L1;
        private double L2;
        private double L3;
		private double P1;
		private double P2;
		private double P3;
        private Series<double> BP1;
        private Series<double> BP2;
        private Series<double> BP3;
        private Series<double> Q1;
        private Series<double> Q2;
        private Series<double> Q3;
		private Series<double> Wave;
		private Series<double> ROC;

		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= "The Fourier Series Analysis indicator as published in the June 2019 Stocks & Commodities articled titled \"Fourier Series Model Of The Market\"";
				Name										= "FourierSeriesAnalysis";
				Calculate									= Calculate.OnBarClose;
				IsOverlay									= false;
				DisplayInDataBox							= true;
				DrawOnPricePanel							= true;
				DrawHorizontalGridLines						= true;
				DrawVerticalGridLines						= true;
				PaintPriceMarkers							= true;
				ScaleJustification							= NinjaTrader.Gui.Chart.ScaleJustification.Right;
				IsSuspendedWhileInactive					= true;
				
				Fundamental									= 20;
				Bandwidth									= 0.1;
				PlotROC										= false;
				
				AddPlot(Brushes.Crimson, "WavePlot");
				AddPlot(Brushes.CadetBlue, "ROCPlot");
				AddLine(Brushes.DarkGray, 0, "ZeroLine");
				
			}
			else if (State == State.Configure)
			{
		        BP1         = new Series<double>(this, MaximumBarsLookBack.Infinite);
		        BP2         = new Series<double>(this, MaximumBarsLookBack.Infinite);
		        BP3         = new Series<double>(this, MaximumBarsLookBack.Infinite);
		        Q1          = new Series<double>(this, MaximumBarsLookBack.Infinite);
		        Q2          = new Series<double>(this, MaximumBarsLookBack.Infinite);
		        Q3          = new Series<double>(this, MaximumBarsLookBack.Infinite);
				Wave		= new Series<double>(this, MaximumBarsLookBack.Infinite);
				ROC			= new Series<double>(this, MaximumBarsLookBack.Infinite);
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < 1)
				return;
			
			if(CurrentBar == 1)
			{
				L1 = Math.Cos(6.28 / Fundamental);
				G1 = Math.Cos(Bandwidth*6.28 / Fundamental);
				S1 = 1 / G1 - Math.Sqrt(1 / (G1*G1) - 1);
				L2 = Math.Cos(6.28 / (Fundamental / 2));
				G2 = Math.Cos(Bandwidth*6.28 / (Fundamental / 2));
				S2 = 1 / G2 - Math.Sqrt(1 / (G2*G2) - 1);
				L3 = Math.Cos(6.28 / (Fundamental / 3));
				G3 = Math.Cos(Bandwidth*6.28 / (Fundamental / 3));
				S3 = 1 / G3 - Math.Sqrt(1 / (G3*G3) - 1);
			}
			
			//Fundamental Band-Pass
			if(CurrentBar <= 3)
				BP1[0] = 0;
			else
				BP1[0] = .5*(1 - S1)*(Close[0] - Close[2]) + L1*(1 + S1)*BP1[1] - S1*BP1[2];
			
			//Fundamental Quadrature
			if(CurrentBar <= 4)
				Q1[0] = 0;
			else
				Q1[0] = (Fundamental / 6.28)*(BP1[0] - BP1[1]);
			
			//Second Harmonic Band-Pass
			if(CurrentBar <= 3)
				BP2[0] = 0;
			else
				BP2[0] = .5*(1 - S2)*(Close[0] - Close[2]) + L2*(1 + S2)*BP2[1] - S2*BP2[2];
			
			//Second Harmonic Quadrature
			if(CurrentBar <= 4)
				Q2[0] = 0;
			else
				Q2[0] = (Fundamental / 6.28)*(BP2[0] - BP2[1]);
			
			//Third Harmonic Band-Pass
			if(CurrentBar <= 3)
				BP3[0] = 0;
			else
				BP3[0] = .5*(1 - S3)*(Close[0] - Close[2]) + L3*(1 + S3)*BP3[1] - S3*BP3[2];
			
			//Third Harmonic Quadrature
			if(CurrentBar <= 4)
				Q3[0] = 0;
			else
				Q3[0] = (Fundamental / 6.28)*(BP3[0] - BP3[1]);
			
			//Sum power of each harmonic at each bar over the Fundamental period
			P1 = 0;
			P2 = 0;
			P3 = 0;
			
			if(CurrentBar >= Fundamental)
			
			{
				for(count = 0; count < Fundamental; count++)
				{
					P1 = P1 + BP1[count]*BP1[count] + Q1[count]*Q1[count];
					P2 = P2 + BP2[count]*BP2[count] + Q2[count]*Q2[count];
					P3 = P3 + BP3[count]*BP3[count] + Q3[count]*Q3[count];
				}
				
				if(P1 != 0)
				{
					Wave[0] = BP1[0] + Math.Sqrt(P2 / P1)*BP2[0] + Math.Sqrt(P3 / P1)*BP3[0];
					WavePlot[0] = Wave[0];
				}
			}
			
			if(PlotROC)
			{
				if(CurrentBar < 3)
					return;
				
				ROC[0] = (Fundamental / 12.57)*(Wave[0] - Wave[2]);
				ROCPlot[0] = ROC[0];
			}
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, double.MaxValue)]
		[Display(Name="Fundamental Cycle Period", Order=1, GroupName="Parameters")]
		public double Fundamental
		{ get; set; }
		
		[NinjaScriptProperty]
		[Display(Name="Plot ROC", Order=2, GroupName="Parameters")]
		public bool PlotROC
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> WavePlot
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> ROCPlot
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
		private FourierSeriesAnalysis[] cacheFourierSeriesAnalysis;
		public FourierSeriesAnalysis FourierSeriesAnalysis(double fundamental, bool plotROC)
		{
			return FourierSeriesAnalysis(Input, fundamental, plotROC);
		}

		public FourierSeriesAnalysis FourierSeriesAnalysis(ISeries<double> input, double fundamental, bool plotROC)
		{
			if (cacheFourierSeriesAnalysis != null)
				for (int idx = 0; idx < cacheFourierSeriesAnalysis.Length; idx++)
					if (cacheFourierSeriesAnalysis[idx] != null && cacheFourierSeriesAnalysis[idx].Fundamental == fundamental && cacheFourierSeriesAnalysis[idx].PlotROC == plotROC && cacheFourierSeriesAnalysis[idx].EqualsInput(input))
						return cacheFourierSeriesAnalysis[idx];
			return CacheIndicator<FourierSeriesAnalysis>(new FourierSeriesAnalysis(){ Fundamental = fundamental, PlotROC = plotROC }, input, ref cacheFourierSeriesAnalysis);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.FourierSeriesAnalysis FourierSeriesAnalysis(double fundamental, bool plotROC)
		{
			return indicator.FourierSeriesAnalysis(Input, fundamental, plotROC);
		}

		public Indicators.FourierSeriesAnalysis FourierSeriesAnalysis(ISeries<double> input , double fundamental, bool plotROC)
		{
			return indicator.FourierSeriesAnalysis(input, fundamental, plotROC);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.FourierSeriesAnalysis FourierSeriesAnalysis(double fundamental, bool plotROC)
		{
			return indicator.FourierSeriesAnalysis(Input, fundamental, plotROC);
		}

		public Indicators.FourierSeriesAnalysis FourierSeriesAnalysis(ISeries<double> input , double fundamental, bool plotROC)
		{
			return indicator.FourierSeriesAnalysis(input, fundamental, plotROC);
		}
	}
}

#endregion
