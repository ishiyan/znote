using WealthLab.Backtest;
using System;
using WealthLab.Core;
using WealthLab.Indicators;
using WealthLab.TASC;
using System.Drawing;
using System.Collections.Generic;

namespace WealthScript1 
{
    public class MyStrategy : UserStrategyBase
    {
        /* create indicators and other objects here, this is executed prior to the main trading loop */
        public override void Initialize(BarHistory bars)
        {
		fs = FIRSMA.Series(bars, 20);
		ft = FIRTriangle.Series(bars, 20);
		fh1 = FIRHamming.Series(bars, 20,10);
		fh2 = FIRHann.Series(bars, 20);

		PlotIndicator(fs, Color.DarkRed, PlotStyles.Line, false, "fSMA");
		PlotIndicator(ft, Color.DarkRed, PlotStyles.Line, false, "fTriangle");
		PlotIndicator(fh1, Color.DarkRed, PlotStyles.Line, false, "fHamming");
		PlotIndicator(fh2, Color.DarkRed, PlotStyles.Line, false, "fHann");

		SetPaneDrawingOptions("fSMA", 20, 50);
		SetPaneDrawingOptions("fTriangle", 20, 51);
		SetPaneDrawingOptions("fHamming", 20, 52);
		SetPaneDrawingOptions("fHann", 20, 53);
        }

        /* execute the strategy rules here, this is executed once for each bar in the backtest history */
        public override void Execute(BarHistory bars, int idx)
        {
        }

		/* declare private variables below */
		FIRSMA fs; FIRTriangle ft; FIRHamming fh1; FIRHann fh2;
	}
}