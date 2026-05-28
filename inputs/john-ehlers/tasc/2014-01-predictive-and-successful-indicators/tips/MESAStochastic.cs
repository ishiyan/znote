
Wealth-Lab 6 strategy code (C#):


using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;
using TASCIndicators;

namespace WealthLab.Strategies
{
	public class Ehlers201401 : WealthScript
	{
		private StrategyParameter paramPeriod;
		
		public Ehlers201401()
		{
			paramPeriod = CreateParameter("MESAStoch.Period",20,5,100,5);
		}
		
		protected override void Execute()
		{
			int period = paramPeriod.ValueInt;
			RoofingFilter rf = RoofingFilter.Series(Close);
			MESAStochastic ms = MESAStochastic.Series(Close,period);
			
			for(int bar = period; bar < Bars.Count; bar++)
			{
				// Detect crossover/crossunder and store state in a variable
				bool maXo = CrossOver(bar, ms, 0.8);
				bool maXu = CrossUnder(bar, ms, 0.2);
					
				// The first trade
				if (Positions.Count == 0){
					if ( maXu ) 
						BuyAtMarket( bar + 1 );
					else if( maXo )
						ShortAtMarket( bar + 1 );
				}
					// Subsequent trades
				else 
				{
					Position p = LastPosition;				
					if ( p.PositionType == PositionType.Long ) 
					{
						if ( maXo ) 
						{
							SellAtMarket( bar + 1, p );
							ShortAtMarket( bar + 1 );
						}
					}
					else if ( maXu ) 
					{
						CoverAtMarket( bar + 1, p );
						BuyAtMarket( bar + 1 );
					}
				}	
			}

			HideVolume();
			ChartPane pMS = CreatePane(40,false,true);
			ChartPane pRF = CreatePane(20,true,true);
			PlotSeries(PricePane,SuperSmoother.Series(Close),Color.Red,LineStyle.Solid,1);
			PlotSeries(pRF,rf,Color.FromArgb(255,0,0,139),LineStyle.Solid,1);
			PlotSeries(pMS,ms,Color.FromArgb(255,255,0,128),LineStyle.Solid,2);
			DrawHorzLine(pMS,0.8,Color.Red,LineStyle.Dashed,1);
			DrawHorzLine(pMS,0.2,Color.DarkGreen,LineStyle.Dashed,1);
		}
	}
}

