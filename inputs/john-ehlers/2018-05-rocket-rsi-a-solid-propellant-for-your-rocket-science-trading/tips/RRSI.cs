Wealth-Lab strategy code C#

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
		StrategyParameter slider1;
		StrategyParameter slider2;
		StrategyParameter paramExitDays;

		public MyStrategy()
		{
			slider1 = CreateParameter("Smoothing Length", 8, 2, 20, 2);
			slider2 = CreateParameter("RSI Length", 10, 2, 20, 2);
			paramExitDays = CreateParameter("Exit after", 10, 5, 30, 5);
		}

		protected override void Execute()
		{
			var rr = RocketRSI.Series(Close,slider1.ValueInt,slider2.ValueInt);
			var fixedBars = paramExitDays.ValueInt;
			
			for(int bar = GetTradingLoopStartBar(1); bar < Bars.Count; bar++)
			{
				if (IsLastPositionActive)
				{
					Position p = LastPosition;
					if ( bar+1 - p.EntryBar >= fixedBars )
						SellAtMarket( bar+1, p, "Exit after N bars" ); 
				}
				else
				{
					if( rr[bar] <= -2.0 )
						BuyAtMarket(bar+1);
				}
			}

			var ls = LineStyle.Solid;
			ChartPane paneRocketRSI = CreatePane(40,true,true);
			PlotSeries(paneRocketRSI,rr,Color.Black,ls,2);
			DrawHorzLine(paneRocketRSI,0,Color.Violet,ls,2);
			DrawHorzLine(paneRocketRSI,2,Color.Red,ls,1);
			DrawHorzLine(paneRocketRSI,-2,Color.Blue,ls,1);
		}
	}
}
