Buy at market when the 20-day CorrelationTrend crosses above zero
Exit long when the indicator crosses below zero.

using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;
using TASCIndicators;

namespace WealthLab.Strategies
{
	public class MyStrategy : WealthScript
	{		
		protected override void Execute()
		{
			var ct = CorrelationTrend.Series(Close, 20);

			ChartPane pane1 = CreatePane( 35,true,true);
			PlotSeries( pane1,ct,Color.DarkRed,LineStyle.Solid,2);
			DrawHorzLine( pane1, 0, Color.DarkBlue, LineStyle.Solid, 1);

			for(int bar = GetTradingLoopStartBar(1); bar < Bars.Count; bar++)
			{
				if (IsLastPositionActive)
				{
					Position p = LastPosition;
					if (CrossUnder(bar, ct, 0))
						SellAtMarket( bar + 1, p);
				}
				else
				{
					if (CrossOver(bar, ct, 0))
						BuyAtMarket( bar + 1);
				}
			}
		}
	}
}
