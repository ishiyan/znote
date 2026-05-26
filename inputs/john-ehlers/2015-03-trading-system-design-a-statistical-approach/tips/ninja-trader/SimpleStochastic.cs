#region Using declarations
using System;
using System.ComponentModel;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.Indicator;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Strategy;
#endregion

namespace NinjaTrader.Strategy
{
    [Description("John F. Ehlers and Ric Way: 'Judging by the numbers' - TASC March 2015")]
    public class SimpleStochastic : Strategy
    {
        #region Variables
        
		private int stochPer = 8;
        private int threshold = 30; 
        private int tradeLength = 14; 
		private int idleBars = 25;
        private double pctLoss = 0.038;
		private bool origEntryLogic = true;
				        
        #endregion

        protected override void Initialize()
        {
            CalculateOnBarClose = true;
			SetStopLoss(CalculationMode.Percent, PctLoss);
			EntryHandling = EntryHandling.UniqueEntries;
		}
		
		protected override void OnBarUpdate()
        {
			if (CrossBelow(StochasticsFast(1, StochPer).K, Threshold, 1))
			{
				if (OrigEntryLogic)
					EnterLong(DefaultQuantity, "Long1");
				
				else if (Position.MarketPosition == MarketPosition.Flat && (BarsSinceExit("") == -1 || BarsSinceEntry("Long1") > IdleBars || BarsSinceExit("Long2") > IdleBars))
				{
					EnterLong(DefaultQuantity, "Long1");
					EnterLong(DefaultQuantity, "Long2");
				}
			}
						
			if (BarsSinceEntry() >= TradeLength - 2)
            	if (!OrigEntryLogic && Position.GetProfitLoss(Close[0], PerformanceUnit.Currency) < 0)
				{
					ExitLong("BarsExit", "Long1");
					ExitLong("BarsExit", "Long2");
				}
				else
					ExitLong("BarsExit", "Long1");
			
			if (!OrigEntryLogic && Position.MarketPosition == MarketPosition.Long && BarsSinceEntry() >= TradeLength - 2)
				if (CrossBelow(Close, ParabolicSAR(0.02, 0.2, 0.02), 1))
					ExitLong("RunnerExit", "Long2");
		}

        #region Properties
        [Description("Threshold below which to enter long")]
        [GridCategory("Parameters")]
        public int Threshold
        {
            get { return threshold; }
            set { threshold = Math.Max(1, value); }
        }

        [Description("Number of bars to hold position before closing")]
        [GridCategory("Parameters")]
        public int TradeLength
        {
            get { return tradeLength; }
            set { tradeLength = Math.Max(1, value); }
        }
		
		[Description("Number of bars for Stochastic K")]
        [GridCategory("Parameters")]
        public int StochPer
        {
            get { return stochPer; }
            set { stochPer = Math.Max(1, value); }
        }
		
		[Description("Number of bars to wait for new entry")]
        [GridCategory("Parameters")]
        public int IdleBars
        {
            get { return idleBars; }
            set { idleBars = Math.Max(1, value); }
        }
		
		[Description("Default true uses original single position logic per article, set to false to allow for a runner to be considered as well")]
        [GridCategory("Parameters")]
        public bool OrigEntryLogic
        {
            get { return origEntryLogic; }
            set { origEntryLogic = value; }
        }

        [Description("Allowable loss percentage")]
        [GridCategory("Parameters")]
        public double PctLoss
        {
            get { return pctLoss; }
            set { pctLoss = Math.Max(0.001, value); }
        }
        #endregion
    }
}
