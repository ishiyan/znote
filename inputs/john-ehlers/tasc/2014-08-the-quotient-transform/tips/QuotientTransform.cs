C# Strategy code:

using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;
using TASCIndicators;

namespace WealthLab.Strategies
{
	public class QuotientTransformTASC201408 : WealthScript
	{
		private StrategyParameter paramPeriod;
		private StrategyParameter paramK1;
		private StrategyParameter paramK2;
		
		public QuotientTransformTASC201408()
		{
			paramPeriod = CreateParameter("Low-pass period",20,2,300,20);
			paramK1 = CreateParameter("K for entries",0.8,-1,1,1);
			paramK2 = CreateParameter("K for exits",0.4,-1,1,1);
		}
		
		protected override void Execute()
		{
			QuotientTransform qtEn = QuotientTransform.Series(Close,paramPeriod.ValueInt,paramK1.Value);
			QuotientTransform qtEx = QuotientTransform.Series(Close,paramPeriod.ValueInt,paramK2.Value);
			
			for(int bar = 2; bar < Bars.Count; bar++)
			{
				if (IsLastPositionActive)
				{
					if( CrossUnder( bar, qtEx, 0 ) )
						SellAtMarket( bar+1, LastPosition );
				}
				else
				{
					if( CrossOver( bar, qtEn, 0 ) )
						if( BuyAtMarket( bar+1 ) != null )
							LastPosition.Priority = -Close[bar];
				}
			}

			HideVolume();
			LineStyle ls = LineStyle.Solid;
			ChartPane pQT = CreatePane(40,true,true);
			PlotSeries(pQT,qtEx,Color.DarkCyan,ls,1);
			PlotSeries(pQT,qtEn,Color.FromArgb(255,255,140,0),ls,2);

			RSI rsi = RSI.Series(Close,14);
			DataSeries qrsi = (rsi - 50) / 50;
			ChartPane rp = CreatePane(40,false,true);
			qrsi.Description = "RSI Constrained";			
			DataSeries qr = QuotientTransform.Series( qrsi, paramPeriod.ValueInt, paramK1.Value);			
			PlotSeries(rp,qr,Color.Plum,ls,2);
		}
	}
}
