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
	public class SimpleStrategy : Strategy
	{
		private Series<double> Deriv;
		private Series<double> Z3;
		private Series<double> Signal;
		private Series<double> ROC_;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"Simple Strategy was published in the June 2021 Technical Analysis of Stocks and Commodities article titled 'Creating More Robust Trading Strategies with the FM Demodulator' by John F. Ehlers.";
				Name										= @"Simple Strategy";
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
				IsOverlay = true;
				// Disable this property for performance gains in Strategy Analyzer optimizations
				// See the Help Guide for additional information
				IsInstantiatedOnEachOptimizationIteration	= true;
				SigPeriod					= 8;
				ROCPeriod					= 1;
				
			}
			else if (State == State.DataLoaded)
			{				
				Deriv = new Series<double>(this);
				Z3 = new Series<double>(this);
				Signal = new Series<double>(this);
				ROC_ = new Series<double>(this);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < SigPeriod || CurrentBar < 3)
				return;
			
			// Derivative of the price wave
			Deriv[0] = Close[0] - Close[2];
			
			//zeros at Nyquist and 2*Nyquist, i.e. Z3 = (1 + Z^-1)*(1 + Z^-2) to integrate derivative
			Z3[0] = Deriv[0] + Deriv[1] + Deriv[2] + Deriv[3];
			
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
