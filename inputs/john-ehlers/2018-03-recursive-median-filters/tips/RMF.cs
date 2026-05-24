using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;
using TASCIndicators;

namespace WealthLab.Strategies
{
	public class TASC201803: WealthScript
	{
		private StrategyParameter slider1;
		private StrategyParameter slider2;
		private StrategyParameter slider3;
		private StrategyParameter slider4;
		private StrategyParameter slider5;

		public TASC201803()
		{
			slider1 = CreateParameter("RMO LPPeriod",16,2,300,20);
			slider2 = CreateParameter("RMO HPPeriod",40,2,300,20);
			slider3 = CreateParameter("RMO Median",5,2,300,20);
			
			slider4 = CreateParameter("RSI Period",14,2,200,20);
			slider5 = CreateParameter("EMA(RSI) Period",16,2,200,20);
		}
		
		protected override void Execute()
		{
			var rmf = RMF.Series( Close, slider1.ValueInt,slider3.ValueInt);
			var rmo = RMO.Series( Close, slider1.ValueInt,slider2.ValueInt,slider3.ValueInt);
			var rsi = EMA.Series(RSI.Series( Close, slider4.ValueInt),slider5.ValueInt,EMACalculation.Modern) / 100d;

			ChartPane paneRSI = CreatePane( 30,false,true);
			ChartPane paneRMO = CreatePane( 30,false,true);
			HideVolume();
			PlotSeries( paneRSI,rsi,Color.Blue,LineStyle.Solid,2);
			PlotSeries( paneRMO,rmo,Color.Red,LineStyle.Solid,2);
			PlotSeries( PricePane, rmf,Color.Black,LineStyle.Solid,2);
		}
	}
}
