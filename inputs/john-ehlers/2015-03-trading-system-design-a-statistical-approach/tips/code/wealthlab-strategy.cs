Wealth-Lab 6 strategy code (C#)

using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;

namespace WealthLab.Strategies
{
	public class EhlersMar2015 : WealthScript
	{
		private StrategyParameter paramStoc;
		private StrategyParameter paramThresh;
		private StrategyParameter paramLength;
		private StrategyParameter paramLoss;

		public EhlersMar2015()
		{
			paramStoc = CreateParameter("StocLength", 8, 1, 100, 1);
			paramThresh = CreateParameter("Threshold", 0.3, 0.1, 0.9, 0.1);			
			paramLength = CreateParameter("TradeLength", 14, 1, 50, 1);
			paramLoss = CreateParameter("PctLoss", 3.8, 0.5, 15.0, 0.5);
		}
		
		protected override void Execute()
		{
			int StocLength = paramStoc.ValueInt, TradeLength = paramStoc.ValueInt;
			double Threshold = paramThresh.Value, PctLoss = paramLoss.Value;

			Highest HiC = Highest.Series(Close, StocLength);
			Lowest LoC = Lowest.Series(Close, StocLength);
			DataSeries Stoc = (Close - LoC) / (HiC - LoC);
			
			for(int bar = GetTradingLoopStartBar(1); bar < Bars.Count; bar++)
			{
				if (IsLastPositionActive)
				{
					Position p = LastPosition;
					if ( bar+1 - p.EntryBar >= TradeLength )
						SellAtMarket( bar+1, p, "Timed" );
					else
						if( Low[bar] < p.EntryPrice*(1.0 - PctLoss /100d) )
						SellAtMarket(bar+1, p, "Stop");

				}
				else
				{
					if( CrossOver( bar, Stoc, Threshold ) )
						BuyAtMarket( bar+1 );
				}
			}
		}
	}
}
