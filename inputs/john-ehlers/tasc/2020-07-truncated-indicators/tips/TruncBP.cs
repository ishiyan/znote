using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;
using TASCIndicators;

namespace WealthLab.Strategies
{
	public class TASC2020_07 : WealthScript	
	{		
		protected override void Execute()
		{
			var tbp = TruncatedBandPass.Series(Close, 20, 0.10, 10);

			HideVolume();
			ChartPane pane1 = CreatePane( 25,true,true);
			PlotSeries( pane1,tbp,Color.MidnightBlue,LineStyle.Solid,1);

			for(int bar = GetTradingLoopStartBar( 21); bar < Bars.Count; bar++)
			{
				if (IsLastPositionActive)
				{
					Position p = LastPosition;
					
					if (CrossUnder(bar, tbp, 0))
						SellAtMarket( bar + 1, p);
				}
				else
				{
					if (CrossOver(bar, tbp, 0))
						BuyAtMarket( bar + 1);
				}
			}
		}
	}
}
