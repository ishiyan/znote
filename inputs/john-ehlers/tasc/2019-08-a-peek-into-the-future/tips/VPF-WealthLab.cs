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
			var voss = VossPredictor.Series( Close, 20,3 );
			var bandpass = BandPass.Series( Close, 20 );
			var adx = ADX.Series( Bars, 14 );
			
			for(int bar = GetTradingLoopStartBar( 21 ); bar < Bars.Count; bar++)
			{
				if (IsLastPositionActive)
				{
					Position p = LastPosition;
					if (CrossUnder(bar, voss, bandpass))
						SellAtMarket( bar + 1, p);
				}
				else
				{
					if (CrossOver(bar, voss, bandpass))					
						if (adx[bar] < 30)
							BuyAtMarket( bar + 1);
				}
			}
			
			ChartPane pane1 = CreatePane( 25,true,true );
			PlotSeries( pane1,voss,Color.BlueViolet,LineStyle.Solid,1);
			PlotSeries( pane1,bandpass,Color.IndianRed,LineStyle.Solid,1);
			ChartPane pane2 = CreatePane( 25,true,true );
			PlotSeries( pane2,adx,Color.Purple,LineStyle.Solid,3);

		}
	}
}