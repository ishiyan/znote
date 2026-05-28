using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;
using TASCIndicators;

namespace WealthLab.Strategies
{
	public class TASC201607 : WealthScript
	{
		private StrategyParameter paramPeriod1;
		private StrategyParameter paramPeriod2;
		private StrategyParameter paramGoShort;

		public TASC201607()
		{
			paramPeriod1 = CreateParameter("Period1", 40, 10, 100, 10);
			paramPeriod2 = CreateParameter("Period2", 60, 20, 300, 10);
			paramGoShort = CreateParameter("Go short?", 0, 0, 1, 1);
		}
		
		protected override void Execute()
		{
			int Period1 = paramPeriod1.ValueInt;
			int Period2 = paramPeriod2.ValueInt;
			bool goShort = paramGoShort.ValueInt == 1 ? true : false;

			var spb = SuperPassband.Series(Close,40,60);
			var rms = SuperPassbandRMS.Series(Close,40,60);
			var mrms = rms*-1;
			
			var pbPane = CreatePane(30,true,true);
			PlotSeries(pbPane,spb,Color.Red,WealthLab.LineStyle.Solid,1);
			DrawHorzLine(pbPane,0,Color.Blue,WealthLab.LineStyle.Solid,1);
			PlotSeriesFillBand(pbPane,rms,mrms,Color.Yellow,Color.Transparent,WealthLab.LineStyle.Solid,1);
			
			for(int bar = Math.Max(Period1,Period2); bar < Bars.Count; bar++)
			{
				SetBackgroundColor(bar,Color.Black);
				
				if (IsLastPositionActive)
				{
					Position p = LastPosition;
					if( p.PositionType == PositionType.Long )
					{
						if( CrossUnder(bar, spb, rms) || CrossUnder(bar, spb, mrms) )
							SellAtMarket(bar+1, p);
					}
					else
					{
						if( CrossOver(bar, spb, mrms) || CrossOver(bar, spb, rms))
							CoverAtMarket(bar+1, p);
					}
				}
				else
				{
					if( CrossOver(bar, spb, mrms))
						BuyAtMarket(bar+1);
					else
						if( CrossUnder(bar, spb, rms) && goShort )
							ShortAtMarket(bar+1);
				}
			}
		}
	}
}
