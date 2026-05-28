C# Code

using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;
using TASCIndicators;

namespace WealthLab.Strategies
{
	public class UniversalOscSARStrategy : WealthScript
	{
		StrategyParameter be;
		StrategyParameter mode;
		
		public UniversalOscSARStrategy()
		{
			be = CreateParameter("Band edge", 20, 5, 200, 5);
			mode = CreateParameter("Swing/Trend", 0, 0, 1, 1);
		}
		
		protected override void Execute()
		{
			bool swingTrade = mode.ValueInt == 0 ? true : false;
			int period = be.ValueInt;
				
			UniversalOscillator uo = UniversalOscillator.Series(Close,period );
			ChartPane uPane = CreatePane(30,false,true); HideVolume();
			PlotSeries(uPane,uo,Color.IndianRed,LineStyle.Solid,2);
			DrawHorzLine(uPane,0,Color.Blue,LineStyle.Dashed,1);

			for(int bar = GetTradingLoopStartBar(period); bar < Bars.Count; bar++)
			{
				// Detect crossover/crossunder and store state in variable
				bool uXo = CrossOver(bar, uo, 0);
				bool uXu = CrossUnder(bar, uo, 0);

				if( swingTrade ) // Countertrend trading
				{
					// The first trade
					if (Positions.Count == 0){
						if ( uXu )
							BuyAtMarket( bar + 1 );
						else if( uXo )
							ShortAtMarket( bar + 1 );
					}
						// Subsequent trades
					else
					{
						Position p = LastPosition;				
						if ( p.PositionType == PositionType.Long )
						{
							if ( uXo )
							{
								SellAtMarket( bar + 1, p );
								ShortAtMarket( bar + 1 );
							}
						}
						else if ( uXu )
						{
							CoverAtMarket( bar + 1, p );
							BuyAtMarket( bar + 1 );
						}
					}
				}
				else // Trend trading
				{
					if (IsLastPositionActive)
					{
						if ( uXu )
							SellAtMarket( bar + 1, LastPosition );
					}
					else
					{
						if ( uXo )
							BuyAtMarket( bar + 1 );
					}
				}								
			}
		}
	}
}
