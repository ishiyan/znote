using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;
using TASCIndicators;

namespace WealthLab.Strategies
{
	public class TASC201709 : WealthScript
	{
		private StrategyParameter paramAlpha;

		public TASC201709()
		{
			paramAlpha = CreateParameter("Alpha", 0.1, 0.05, 0.5, 0.05);
		}
		
		protected override void Execute()
		{
			var re = ReverseEMA.Series(Close, paramAlpha.Value);
			ChartPane rePane = CreatePane( 30,false,false );
			HideVolume();
			PlotSeries( rePane, re, Color.Red, LineStyle.Solid, 2);
			
			//RoofingFilter for comparison
			var rf = RoofingFilter.Series(Close);
			ChartPane rfPane = CreatePane( 25,false,false);
			PlotSeries( rfPane,rf,Color.DarkBlue,LineStyle.Solid,1);
		}
	}
}
