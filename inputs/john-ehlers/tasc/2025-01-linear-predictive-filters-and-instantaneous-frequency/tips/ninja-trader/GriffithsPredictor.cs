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
	public class GriffithsPredictor : Indicator
	{
		private HighPassFilter	hP;
        private SuperSmoother	lP;
		private double			mu, xPred;
        private double[]		xx, coef;
		private Series<double>	peak;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description			= @"Griffiths Predictor Indicator as published in the January 2025 Stocks and Commodities article titled Linear Predictive Filters And Instantaneous Frequency by John F. Ehlers.";
				Name				= "GriffithsPredictor";
				Calculate			= Calculate.OnBarClose;
				IsOverlay			= false;
				
				BarsFwd				= 2;
				LowerBound			= 18;
				UpperBound			= 40;
				Length				= 18;
				
				AddPlot(Brushes.Blue, "Prediction");
				AddPlot(Brushes.Red, "NormalizedSignal");
				
				AddLine(Brushes.Black, 0, "Zero");
			}
			else if (State == State.DataLoaded)
			{
				xx		= new double[200];
				coef	= new double[200];
				peak	= new Series<double>(this, MaximumBarsLookBack);
				
				hP		= HighPassFilter(UpperBound);
				lP		= SuperSmoother(hP, LowerBound);
				
				mu		= 1.0 / Length;
			}
		}

		protected override void OnBarUpdate()
		{
			peak[0] = (CurrentBar == 0) ? .1 : 0.991 * peak[1];

			if (Math.Abs(lP[0]) > peak[0])
				peak[0] = Math.Abs(lP[0]);

			NormalizedSignal[0] = (peak[0] != 0) ? lP[0] / peak[0] : 0;

			if (CurrentBar < Length)
				return;

			for (int count = 1; count <= Length; count++)
				xx[count] = NormalizedSignal[Length - count];

			double xBar = 0;

			for (int count = 1; count <= Length; count++)
				xBar += xx[Length - count] * coef[count];

			for (int count = 1; count <= Length; count++)
				coef[count] += mu * (xx[Length] - xBar) * xx[Length - count];

			for (int advance = 1; advance <= BarsFwd; advance++)
			{
				xPred = 0;

				for (int count = 1; count <= Length - advance; count++)
					xPred += xx[Length + 1 - count] * coef[count];

				for (int count = 1; count < Length; count++)
					xx[count] = xx[count + 1];

				xx[Length] = xPred;
			}

			Default[0] = xPred;
		}

		[XmlIgnore]
		[Browsable(false)]
		public Series<double> Default
		{ get { return Values[0]; } }

		[XmlIgnore]
		[Browsable(false)]
		public Series<double> NormalizedSignal
		{ get { return Values[1]; } }

		[NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Bars Forward", Order = 1, GroupName = "Parameters")]
        public int BarsFwd { get; set; }

		[NinjaScriptProperty]
		[Range(1, 200)]
		[Display(Name = "Length", Order = 2, GroupName = "Parameters")]
		public int Length { get; set; }

		[NinjaScriptProperty]
        [Range(1, 125)]
        [Display(Name = "Lower Bound", Order = 3, GroupName = "Parameters")]
        public int LowerBound { get; set; }

        [NinjaScriptProperty]
        [Range(1, 125)]
        [Display(Name = "Upper Bound", Order = 4, GroupName = "Parameters")]
        public int UpperBound { get; set; }
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private GriffithsPredictor[] cacheGriffithsPredictor;
		public GriffithsPredictor GriffithsPredictor(int barsFwd, int length, int lowerBound, int upperBound)
		{
			return GriffithsPredictor(Input, barsFwd, length, lowerBound, upperBound);
		}

		public GriffithsPredictor GriffithsPredictor(ISeries<double> input, int barsFwd, int length, int lowerBound, int upperBound)
		{
			if (cacheGriffithsPredictor != null)
				for (int idx = 0; idx < cacheGriffithsPredictor.Length; idx++)
					if (cacheGriffithsPredictor[idx] != null && cacheGriffithsPredictor[idx].BarsFwd == barsFwd && cacheGriffithsPredictor[idx].Length == length && cacheGriffithsPredictor[idx].LowerBound == lowerBound && cacheGriffithsPredictor[idx].UpperBound == upperBound && cacheGriffithsPredictor[idx].EqualsInput(input))
						return cacheGriffithsPredictor[idx];
			return CacheIndicator<GriffithsPredictor>(new GriffithsPredictor(){ BarsFwd = barsFwd, Length = length, LowerBound = lowerBound, UpperBound = upperBound }, input, ref cacheGriffithsPredictor);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.GriffithsPredictor GriffithsPredictor(int barsFwd, int length, int lowerBound, int upperBound)
		{
			return indicator.GriffithsPredictor(Input, barsFwd, length, lowerBound, upperBound);
		}

		public Indicators.GriffithsPredictor GriffithsPredictor(ISeries<double> input , int barsFwd, int length, int lowerBound, int upperBound)
		{
			return indicator.GriffithsPredictor(input, barsFwd, length, lowerBound, upperBound);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.GriffithsPredictor GriffithsPredictor(int barsFwd, int length, int lowerBound, int upperBound)
		{
			return indicator.GriffithsPredictor(Input, barsFwd, length, lowerBound, upperBound);
		}

		public Indicators.GriffithsPredictor GriffithsPredictor(ISeries<double> input , int barsFwd, int length, int lowerBound, int upperBound)
		{
			return indicator.GriffithsPredictor(input, barsFwd, length, lowerBound, upperBound);
		}
	}
}

#endregion
