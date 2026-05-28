#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.IO;
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
	public class TASCProbabilityDistribution : Indicator
	{
		private string path;
		private string fullpath;
		private StreamWriter sw;
		private double[] Bin;
		private bool error = false;
		
		protected override void OnStateChange()
		{			
			if (State == State.SetDefaults)
			{
				Description									= @"Probablility Distrubtion indicator as described in the October 2018 Stocks and Commodities article titled 'Probability — Probably A Good Thing To Know' by John F Ehlers";
				Name										= "TASCProbabilityDistribution";
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
				
				SelectedIndicator							= TASCProbabilityDistributionSupportedIndicators.MyRSI;
				
				MyRSISmoothLength							= 8;
				MyRSILength									= 14;
				
				RocketRSISmoothLength						= 8;
				RocketRSILength								= 10;
				
				DSMAPeriod									= 40;
				DSMAFisherPeriod							= 40;
			}
			else if (State == State.DataLoaded)
			{
				Bin 	 = new double[62];				
				path 	 = System.IO.Path.Combine(NinjaTrader.Core.Globals.UserDataDir,"ProbabilityDistribution", SelectedIndicator.ToString(), Bars.Instrument.FullName); // Define the Path to our test file
				fullpath = path + "\\ProbabilityDensity.csv";
				
				if(!System.IO.Directory.Exists(path))
					System.IO.Directory.CreateDirectory(path);
			}
			else if (State == State.Terminated)
			{
				if (sw != null)
				{
					sw.Close();
					sw.Dispose();
					sw = null;
				}
			}
		}

		protected override void OnBarUpdate()
		{			
			if(State == State.Historical)
			{
				if (CurrentBar < DSMAFisherPeriod || CurrentBar < DSMAPeriod
					|| CurrentBar < RocketRSISmoothLength || CurrentBar < RocketRSILength
					|| CurrentBar < MyRSISmoothLength || CurrentBar < MyRSILength)
					return;
				
				double currentIndicatorValue = 0;
				
				switch (SelectedIndicator)
				{
					case TASCProbabilityDistributionSupportedIndicators.MyRSI: 		currentIndicatorValue = CalcMyRSI(); 		break;
					case TASCProbabilityDistributionSupportedIndicators.RocketRSI: 	currentIndicatorValue = CalcRocketRSI(); 	break;
					case TASCProbabilityDistributionSupportedIndicators.DSMA: 		currentIndicatorValue = CalcDSMA(); 		break;
					case TASCProbabilityDistributionSupportedIndicators.DSMAFisher: currentIndicatorValue = CalcDSMAFisher(); 	break;
					default: 														currentIndicatorValue = CalcMyRSI(); 		break;
				}
				
				for (int i = 1; i <= 60; i++)
				{
					double j = (double)(i - 31) / 10;
					double k = (double)(i - 30) / 10;
					
					if (currentIndicatorValue > j && currentIndicatorValue <= k)
						Bin[i] = Bin[i] + 1;
				}
				
				if (CurrentBar == Bars.Count - 2)
				{
					try
					{
						sw = File.CreateText(fullpath);
						
						for (int i = 1; i <= 61; i++)
							sw.WriteLine(((double)(i - 31) / 10) + "," + Bin[i]);
						
						sw.Close();
					}
					catch(Exception e)
					{
						error = true;
					}
				}
			}
			if(error)
				Draw.TextFixed(this, "Error", "Something went wrong when writing to file. Please close the file in any programs that have it open.", TextPosition.BottomRight);
			else
				Draw.TextFixed(this, "Error", "File exported to: " + fullpath.ToString(), TextPosition.BottomRight);
		}
		
		private double CalcMyRSI()
		{
			return MyRSI(MyRSISmoothLength, MyRSILength)[0];
		}
		
		private double CalcRocketRSI()
		{
			return RocketRSI(RocketRSISmoothLength, RocketRSILength)[0];
		}
		
		private double CalcDSMA()
		{
			return DSMAPD(DSMAPeriod)[0];
		}
		
		private double CalcDSMAFisher()
		{
			return DSMAFisherPD(DSMAPeriod)[0];
		}
		
		[NinjaScriptProperty]
		[Display(Name="Indicator", Description="Pick an indicator supported by this utility", Order=1, GroupName="Parameters")]
		public TASCProbabilityDistributionSupportedIndicators SelectedIndicator
		{ get; set; }
		
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="SmoothLength", Order=1, GroupName="MyRSI")]
		public int MyRSISmoothLength
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="RSILength", Order=2, GroupName="MyRSI")]
		public int MyRSILength
		{ get; set; }
		
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="SmoothLength", Order=1, GroupName="RocketRSI")]
		public int RocketRSISmoothLength
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="RSILength", Order=2, GroupName="RocketRSI")]
		public int RocketRSILength
		{ get; set; }
		
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Period", Order=1, GroupName="DSMA")]
		public int DSMAPeriod
		{ get; set; }
		
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Period", Order=1, GroupName="DSMAFisher")]
		public int DSMAFisherPeriod
		{ get; set; }
	}
}

public enum TASCProbabilityDistributionSupportedIndicators
{
    MyRSI,
    RocketRSI,
	DSMA,
	DSMAFisher
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private TASCProbabilityDistribution[] cacheTASCProbabilityDistribution;
		public TASCProbabilityDistribution TASCProbabilityDistribution(TASCProbabilityDistributionSupportedIndicators selectedIndicator, int myRSISmoothLength, int myRSILength, int rocketRSISmoothLength, int rocketRSILength, int dSMAPeriod, int dSMAFisherPeriod)
		{
			return TASCProbabilityDistribution(Input, selectedIndicator, myRSISmoothLength, myRSILength, rocketRSISmoothLength, rocketRSILength, dSMAPeriod, dSMAFisherPeriod);
		}

		public TASCProbabilityDistribution TASCProbabilityDistribution(ISeries<double> input, TASCProbabilityDistributionSupportedIndicators selectedIndicator, int myRSISmoothLength, int myRSILength, int rocketRSISmoothLength, int rocketRSILength, int dSMAPeriod, int dSMAFisherPeriod)
		{
			if (cacheTASCProbabilityDistribution != null)
				for (int idx = 0; idx < cacheTASCProbabilityDistribution.Length; idx++)
					if (cacheTASCProbabilityDistribution[idx] != null && cacheTASCProbabilityDistribution[idx].SelectedIndicator == selectedIndicator && cacheTASCProbabilityDistribution[idx].MyRSISmoothLength == myRSISmoothLength && cacheTASCProbabilityDistribution[idx].MyRSILength == myRSILength && cacheTASCProbabilityDistribution[idx].RocketRSISmoothLength == rocketRSISmoothLength && cacheTASCProbabilityDistribution[idx].RocketRSILength == rocketRSILength && cacheTASCProbabilityDistribution[idx].DSMAPeriod == dSMAPeriod && cacheTASCProbabilityDistribution[idx].DSMAFisherPeriod == dSMAFisherPeriod && cacheTASCProbabilityDistribution[idx].EqualsInput(input))
						return cacheTASCProbabilityDistribution[idx];
			return CacheIndicator<TASCProbabilityDistribution>(new TASCProbabilityDistribution(){ SelectedIndicator = selectedIndicator, MyRSISmoothLength = myRSISmoothLength, MyRSILength = myRSILength, RocketRSISmoothLength = rocketRSISmoothLength, RocketRSILength = rocketRSILength, DSMAPeriod = dSMAPeriod, DSMAFisherPeriod = dSMAFisherPeriod }, input, ref cacheTASCProbabilityDistribution);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.TASCProbabilityDistribution TASCProbabilityDistribution(TASCProbabilityDistributionSupportedIndicators selectedIndicator, int myRSISmoothLength, int myRSILength, int rocketRSISmoothLength, int rocketRSILength, int dSMAPeriod, int dSMAFisherPeriod)
		{
			return indicator.TASCProbabilityDistribution(Input, selectedIndicator, myRSISmoothLength, myRSILength, rocketRSISmoothLength, rocketRSILength, dSMAPeriod, dSMAFisherPeriod);
		}

		public Indicators.TASCProbabilityDistribution TASCProbabilityDistribution(ISeries<double> input , TASCProbabilityDistributionSupportedIndicators selectedIndicator, int myRSISmoothLength, int myRSILength, int rocketRSISmoothLength, int rocketRSILength, int dSMAPeriod, int dSMAFisherPeriod)
		{
			return indicator.TASCProbabilityDistribution(input, selectedIndicator, myRSISmoothLength, myRSILength, rocketRSISmoothLength, rocketRSILength, dSMAPeriod, dSMAFisherPeriod);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.TASCProbabilityDistribution TASCProbabilityDistribution(TASCProbabilityDistributionSupportedIndicators selectedIndicator, int myRSISmoothLength, int myRSILength, int rocketRSISmoothLength, int rocketRSILength, int dSMAPeriod, int dSMAFisherPeriod)
		{
			return indicator.TASCProbabilityDistribution(Input, selectedIndicator, myRSISmoothLength, myRSILength, rocketRSISmoothLength, rocketRSILength, dSMAPeriod, dSMAFisherPeriod);
		}

		public Indicators.TASCProbabilityDistribution TASCProbabilityDistribution(ISeries<double> input , TASCProbabilityDistributionSupportedIndicators selectedIndicator, int myRSISmoothLength, int myRSILength, int rocketRSISmoothLength, int rocketRSILength, int dSMAPeriod, int dSMAFisherPeriod)
		{
			return indicator.TASCProbabilityDistribution(input, selectedIndicator, myRSISmoothLength, myRSILength, rocketRSISmoothLength, rocketRSILength, dSMAPeriod, dSMAFisherPeriod);
		}
	}
}

#endregion
