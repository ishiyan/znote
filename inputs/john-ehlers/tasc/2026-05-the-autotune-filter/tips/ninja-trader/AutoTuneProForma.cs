/// Ported to NinjaTrader 8 by NinjaTrader_Eduardo
/// 
/// From the author:
/// AutoTune Pro Forma Strategy
/// (C) 2025 John F. Ehlers

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
using NinjaTrader.NinjaScript.Indicators;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
	public class AutoTuneProForma : Strategy
	{
		private AutoTune		autoTune;
		private Series<double>	rocSeries;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description					= @"AutoTune Pro Forma Strategy as published in the May 2026 Stocks and Commodities article titled ""The AutoTune Filter"" by John F. Ehlers.";
				Name						= "AutoTuneProForma";
				Calculate					= Calculate.OnBarClose;
				EntriesPerDirection			= 1;
				EntryHandling				= EntryHandling.AllEntries;
				IsExitOnSessionCloseStrategy = true;
				ExitOnSessionCloseSeconds	= 30;
				IsFillLimitOnTouch			= false;
				MaximumBarsLookBack			= MaximumBarsLookBack.TwoHundredFiftySix;
				OrderFillResolution			= OrderFillResolution.Standard;
				Slippage					= 0;
				StartBehavior				= StartBehavior.WaitUntilFlat;
				TimeInForce					= TimeInForce.Gtc;
				TraceOrders					= false;
				RealtimeErrorHandling		= RealtimeErrorHandling.StopCancelClose;
				StopTargetHandling			= StopTargetHandling.PerEntryExecution;
				BarsRequiredToTrade			= 20;
				IsInstantiatedOnEachOptimizationIteration = true;

				Window						= 26;
				Bandwidth					= 0.22;
				Threshold					= -0.22;
			}
			else if (State == State.DataLoaded)
			{
				autoTune	= AutoTune(Window, Bandwidth);
				rocSeries	= new Series<double>(this);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < 2 * Window + 2)
			{
				rocSeries[0] = 0;
				return;
			}

			double bp		= autoTune.Bandpass[0];
			double bpPrev2	= autoTune.Bandpass[2];
			double minCorr	= autoTune.MinCorrelation[0];
			double filt		= autoTune.HighPassFiltered[0];

			// ROC = BP - BP[2];
			rocSeries[0] = bp - bpPrev2;

			double rocCurr = rocSeries[0];
			double rocPrev = rocSeries[1];

			// If ROC Crosses Over 0 and MinCorr < Thresh Then Buy Next Bar On Open;
			if (rocPrev <= 0 && rocCurr > 0 && minCorr < Threshold)
				EnterLong("AutoTuneLong");

			// If ROC Crosses Under 0 and MinCorr < Thresh and Filt > 0 Then Sell Short Next Bar on Open;
			if (rocPrev >= 0 && rocCurr < 0 && minCorr < Threshold && filt > 0)
				EnterShort("AutoTuneShort");
		}

		#region Properties

		[NinjaScriptProperty]
		[Range(2, 100)]
		[Display(Name = "Window", Description = "Autocorrelation window / highpass filter period", GroupName = "Parameters", Order = 0)]
		public int Window
		{ get; set; }

		[NinjaScriptProperty]
		[Range(0.01, 1.0)]
		[Display(Name = "Bandwidth", Description = "Bandpass filter bandwidth as a fraction of the dominant cycle period", GroupName = "Parameters", Order = 1)]
		public double Bandwidth
		{ get; set; }

		[NinjaScriptProperty]
		[Range(-1.0, 0.0)]
		[Display(Name = "Threshold", Description = "Minimum correlation threshold for trade entry (negative value)", GroupName = "Parameters", Order = 2)]
		public double Threshold
		{ get; set; }

		#endregion
	}
}
