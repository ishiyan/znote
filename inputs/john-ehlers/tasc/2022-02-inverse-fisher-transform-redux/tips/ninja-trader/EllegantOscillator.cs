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
	public class EllegantOscillator : Indicator
	{
		private Series<double> Deriv, IFish;
		private int count = 0;
		private double RMS, NDeriv, a1, b1, c1, c2, c3 = 0;
		private const int MAXPERIOD = 50;
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The EllegantOscillator indicator as published in February 2022 Technical Analysis of Stocks and Commodities article “An Elegant Oscillator Inverse Fisher Transform Redux” by John F. Ehlers";
				Name										= "EllegantOscillator";
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
				BandEdge					= 20;
				AddPlot(Brushes.Tomato, "SS");
				AddLine(Brushes.White, 0, "ZeroLine");
			}
			else if(State == State.DataLoaded)
			{
				Deriv = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				IFish = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar < 2)
			{
				SS[0] = 0;
				return;
			}
			
			Deriv[0] = Close[0] - Close[2];
			
			RMS = 0;
			
			if(CurrentBar < MAXPERIOD)
			{
				for(int i = 0; i < CurrentBar; i++)
				{
					RMS += Math.Pow(Deriv[i], 2);
				}
			} 
			else
			{
				for(int i = 0; i < MAXPERIOD; i++)
				{
					RMS += Math.Pow(Deriv[i], 2);
				}
			}	
			
			if(RMS != 0)
				RMS = Math.Sqrt(RMS/50);
			NDeriv = Deriv[0]/RMS;
			
			//Compute the Inverse Fisher Transform
			IFish[0] = (Math.Exp(2*NDeriv)-1)/(Math.Exp(2*NDeriv)+1);
			
			//Integrate with SuperSmoother
			a1 = Math.Exp(-1.414*Math.PI/BandEdge);
			b1 = 2*a1*Math.Cos(1.414*(Math.PI/2)/BandEdge);
			c2 = b1;
			c3 = -a1*a1;
			c1 = 1 - c2 - c3;
			
			SS[0] = c1*(IFish[0] + IFish[1]) / 2 + c2*SS[1] + c3*SS[2];
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Band Edge", Order=1, GroupName="Parameters")]
		public int BandEdge
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> SS
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
		private EllegantOscillator[] cacheEllegantOscillator;
		public EllegantOscillator EllegantOscillator(int bandEdge)
		{
			return EllegantOscillator(Input, bandEdge);
		}

		public EllegantOscillator EllegantOscillator(ISeries<double> input, int bandEdge)
		{
			if (cacheEllegantOscillator != null)
				for (int idx = 0; idx < cacheEllegantOscillator.Length; idx++)
					if (cacheEllegantOscillator[idx] != null && cacheEllegantOscillator[idx].BandEdge == bandEdge && cacheEllegantOscillator[idx].EqualsInput(input))
						return cacheEllegantOscillator[idx];
			return CacheIndicator<EllegantOscillator>(new EllegantOscillator(){ BandEdge = bandEdge }, input, ref cacheEllegantOscillator);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.EllegantOscillator EllegantOscillator(int bandEdge)
		{
			return indicator.EllegantOscillator(Input, bandEdge);
		}

		public Indicators.EllegantOscillator EllegantOscillator(ISeries<double> input , int bandEdge)
		{
			return indicator.EllegantOscillator(input, bandEdge);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.EllegantOscillator EllegantOscillator(int bandEdge)
		{
			return indicator.EllegantOscillator(Input, bandEdge);
		}

		public Indicators.EllegantOscillator EllegantOscillator(ISeries<double> input , int bandEdge)
		{
			return indicator.EllegantOscillator(input, bandEdge);
		}
	}
}

#endregion
