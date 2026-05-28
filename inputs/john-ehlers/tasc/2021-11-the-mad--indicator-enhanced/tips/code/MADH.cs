using WealthLab.Backtest;
using System;
using WealthLab.Core;
using WealthLab.Indicators;
using WealthLab.TASC;
using System.Drawing;
using System.Collections.Generic;

namespace WealthScript1 
{
	public class MyStrategy1 : UserStrategyBase
	{
		/* create indicators and other objects here, this is executed prior to the main trading loop */
		public override void Initialize(BarHistory bars)
		{
			mad = MAD.Series(bars.Close, 8, 20);
			madh = MADH.Series(bars.Close, 8, 20);

			PlotIndicator(mad, Color.Red, PlotStyles.Line, false, "MAD");
			PlotIndicator(madh, Color.Yellow, PlotStyles.Line, false, "MADH");

			ChartDisplaySettings cds = new ChartDisplaySettings();
			cds.ColorGridLines = Color.Transparent;
			cds.ColorWatermark = Color.White;
			cds.ColorUpBar = Color.Green;
			cds.ColorDownBar = Color.Red;
			cds.ColorBackground = Color.Black;
			SetChartDrawingOptions(cds);

			SetPaneDrawingOptions("MAD", 20, 50);
			SetPaneDrawingOptions("MADH", 20, 51);
		}

		/* execute the strategy rules here, this is executed once for each bar in the backtest history */
		public override void Execute(BarHistory bars, int idx)
		{
			if(madh.TurnsUp(idx))
				PlaceTrade(bars, TransactionType.Buy, OrderType.Market);
			if (madh.TurnsDown(idx))
				ClosePosition(LastPosition, OrderType.Market);
		}

		/* declare private variables below */
		MAD mad; MADH madh;
	}
}
