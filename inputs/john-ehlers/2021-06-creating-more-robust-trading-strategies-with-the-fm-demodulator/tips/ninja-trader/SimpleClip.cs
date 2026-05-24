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
using NinjaTrader.NinjaScript.Indicators;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

//This namespace holds Strategies in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Strategies
{
	public class SimpleClip : Strategy
	{
		private Series<double> Deriv;
		private Series<double> Z3;
		private Series<double> Clip;
		private Series<double> Signal;
		private Series<double> ROC_;


		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"Simple Clip was published in the June 2021 Technical Analysis of Stocks and Commodities article titled 'Creating More Robust Trading Strategies with the FM Demodulator' by John F. Ehlers.";
				Name										= @"Simple Clip";
				Calculate									= Calculate.OnBarClose;
				EntriesPerDirection							= 1;
				EntryHandling								= EntryHandling.AllEntries;
				IsExitOnSessionCloseStrategy				= true;
				ExitOnSessionCloseSeconds					= 30;
				IsFillLimitOnTouch							= false;
				MaximumBarsLookBack							= MaximumBarsLookBack.TwoHundredFiftySix;
				OrderFillResolution							= OrderFillResolution.Standard;
				Slippage									= 0;
				StartBehavior								= StartBehavior.WaitUntilFlat;
				TimeInForce									= TimeInForce.Gtc;
				TraceOrders									= false;
				RealtimeErrorHandling						= RealtimeErrorHandling.StopCancelClose;
				StopTargetHandling							= StopTargetHandling.PerEntryExecution;
				BarsRequiredToTrade							= 20;
				// Disable this property for performance gains in Strategy Analyzer optimizations
				// See the Help Guide for additional information
				IsInstantiatedOnEachOptimizationIteration	= true;
				SigPeriod					= 22;
				ROCPeriod					= 10;
				
			}
			else if (State == State.DataLoaded)
			{				
				Deriv = new Series<double>(this);
				Z3 = new Series<double>(this);
				Clip = new Series<double>(this);
				Signal = new Series<double>(this);
				ROC_ = new Series<double>(this);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < SigPeriod || CurrentBar < 49)
				return;
			
			// Derivative of the price wave
			Deriv[0] = Close[0] - Close[2];
			
			//Normalize Degap to half RMS and hard limit at +/- 1
			double RMS = 0;
			for (int count = 0; count < 50; count++)
				RMS += Deriv[count] * Deriv[count];
			
			if (RMS != 0)
				Clip[0] = 2 * Deriv[0] / Math.Sqrt(RMS / 50);
			
			Clip[0] = Clip[0] > 1 ? 1 : Clip[0] < -1 ? -1: Clip[0];		
			
			//zeros at Nyquist and 2*Nyquist, i.e. Z3 = (1 + Z^-1)*(1 + Z^-2) to integrate derivative
			Z3[0] = Clip[0] + Clip[1] + Clip[2] + Clip[3];
			
			//Smooth Z3 for trading signal
			Signal[0] = SMA(Z3, SigPeriod)[0];
			
			//Use Rate of Change to identify entry point
			ROC_[0] = Signal[0] - Signal[ROCPeriod];
			
			if(CrossAbove(ROC_, 0, 1))
				EnterLong();
			
			if (CrossBelow(Signal, 0, 1))
				ExitLong();
			
			
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Signal Period", Order=1, GroupName="Parameters")]
		public int SigPeriod
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="ROC Period", Order=2, GroupName="Parameters")]
		public int ROCPeriod
		{ get; set; }
		#endregion

	}
}
