Wealth-Lab 6 code (C#):

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
			// Decycler and oscillator
			SimpleDecycler sd = SimpleDecycler.Series(Close,125);
            DecyclerOscillator do1 = DecyclerOscillator.Series(Close,125,1.0);
			// Hysteresis band 0.5%
			DecyclerOscillator do2 = DecyclerOscillator.Series(Close,(int)(125 * 0.8),1.0 * 1.2);

			HideVolume();
			ChartPane paneDecyclerOsc = CreatePane(30,false,true);
			PlotSeries(paneDecyclerOsc,do1,Color.Red,LineStyle.Solid,2);
			PlotSeries(paneDecyclerOsc,do2,Color.Goldenrod,LineStyle.Solid,2);
			PlotSeries(PricePane,sd,Color.Red,LineStyle.Solid,2);
			PlotSeriesFillBand(PricePane, sd * 1.005, sd * 0.995, Color.Goldenrod, Color.Transparent, LineStyle.Solid, 2);

			for(int bar = GetTradingLoopStartBar(125); bar < Bars.Count; bar++)
			{
				if ( Close[bar] > (sd[bar] * 1.005) )
					SetPaneBackgroundColor( PricePane, bar, Color.FromArgb(30,Color.Green) );

				else
					if ( Close[bar] < (sd[bar] * 0.995) )
                    SetPaneBackgroundColor( PricePane, bar, Color.FromArgb(30,Color.Red) );

				bool reverse2Uptrend = CrossOver( bar, do2, do1 );
				bool reverse2Downtrend = CrossUnder( bar, do2, do1 );
				
				if (IsLastPositionActive)
				{
					if ( !reverse2Downtrend || reverse2Uptrend )
						SetPaneBackgroundColor( paneDecyclerOsc, bar, Color.FromArgb(30,Color.Green) );
					
					if( reverse2Downtrend )
						SellAtMarket(bar+1, LastPosition);
				}
				else
				{
					if ( reverse2Downtrend || !reverse2Uptrend )
						SetPaneBackgroundColor( paneDecyclerOsc, bar, Color.FromArgb(30,Color.Red) );
					

					if( reverse2Uptrend )
						BuyAtMarket(bar+1);
				}
			}
		}
	}
}
