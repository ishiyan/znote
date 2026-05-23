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
	public class ROCStrategy : Strategy
	{
		private SuperSmoother lP;
		private HighPassFilter bp1,bp2;
		private double roc1,roc2;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @" ROC Strategy as published in the June 2025 Stocks and Commodities article titled Making A Better Oscillator by John F. Ehlers.";
				Name										= "ROCStrategy";
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
				
				LPLength									= 20;
				FastHPLength 								= 55;
				SlowHPLength 								= 156;
			}
			else if (State == State.DataLoaded)
			{
				//LP = $SuperSmoother(Close, LPLength);
				lP = SuperSmoother(LPLength);
				//BP1 = $HighPass(LP, FastHPLength);
				bp1 = HighPassFilter(lP,FastHPLength);
				//BP2 = $HighPass(LP, SlowHPLength);
				bp2 = HighPassFilter(lP,SlowHPLength);
				
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBars[0] < BarsRequiredToTrade)
				return;
			//ROC1 = BP1 - BP1[1];
				roc1 = bp1[0] - bp1[1];
			//ROC2 = BP2 - BP2[2];
				roc2 = bp2[0] - bp2[1];
			//If MarketPosition <> 1 and ROC1 > 0 and ROC2 > 0 Then Buy Next Bar on Open;
			if (Position.MarketPosition == MarketPosition.Flat && roc1 > 0 && roc2 > 0)
				EnterLong();
			//If MarketPosition = 1 and (ROC1 < 0 OR ROC2 < 0) Then Sell Next Bar on Open;
			if (Position.MarketPosition != MarketPosition.Flat && (roc1 < 0 || roc2 < 0))
				ExitLong();
		}
		
		
		
		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue), Display(Name = "LPLength", Order = 1, GroupName = "Parameters")]
		public int LPLength { get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue), Display(Name = "FastHPLength", Order = 2, GroupName = "Parameters")]
		public int FastHPLength { get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue), Display(Name = "SlowHPLength", Order = 3, GroupName = "Parameters")]
		public int SlowHPLength { get; set; }
		#endregion
	}
}
