using WealthLab.Backtest;
using System;
using WealthLab.Core;
using WealthLab.Indicators;
using WealthLab.TASC;
using System.Drawing;
using System.Collections.Generic;

namespace WealthScript1
{
	public class TASCFeb2022 : UserStrategyBase
	{
		/* create indicators and other objects here, this is executed prior to the main trading loop */
		public override void Initialize(BarHistory bars)
		{
			eo = ElegantOscillator.Series(bars.Close, 20);
			bbLower = BBLower.Series(eo, 100, 1.5);
			bbUpper = BBUpper.Series(eo, 100, 1.5);
			StartIndex = 100;

			PlotIndicatorLine(eo);
			PlotIndicatorLine(bbLower);
			PlotIndicatorLine(bbUpper);
		}

		/* execute the strategy rules here, this is executed once for each bar in the backtest history */
		public override void Execute(BarHistory bars, int idx)
		{
			if (!HasOpenPosition(bars, PositionType.Long))
			{
				/* code your buy conditions here */
				if(eo.CrossesOver(bbLower, idx))
					PlaceTrade(bars, TransactionType.Buy, OrderType.Market);
			}
			else
			{
				/* code your sell conditions here */
				if(eo.CrossesOver(bbUpper, idx))
					PlaceTrade(bars, TransactionType.Sell, OrderType.Market);
				else
					if(LastPosition.ProfitPctAsOf(idx) < -5)
					PlaceTrade(bars, TransactionType.Sell, OrderType.Market, default, "Stop");
			}
		}

		/* declare private variables below */
		ElegantOscillator eo;
		BBLower bbLower;
		BBUpper bbUpper;
	}
}
