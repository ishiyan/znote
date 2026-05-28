using WealthLab.Backtest;
using System;
using WealthLab.Core;
using WealthLab.Indicators;
using System.Drawing;
using System.Collections.Generic;
using ScottPlot;

namespace WealthScript1 
{
	public class TASC202207PairsRotationWithEhlersLoops : UserStrategyBase
	{
		/* create indicators and other objects here, this is executed prior to the main trading loop */
		public override void Initialize(BarHistory bars)
		{
			spy = GetHistory(bars, "SPY");
			PlotBarHistory(spy, "SPYPane", WLColor.Silver);

			int LPPeriod = 20, HPPeriod = 125;
			double Deg2Rad = Math.PI / 180.0;
			List<double> lstDates = new List<double>();
			List<double> lstValuesP = new List<double>();
			List<double> lstValuesP2 = new List<double>();

			hpa1 = Math.Exp(-1.414 * Math.PI / HPPeriod);
			hpb1 = 2.0 * hpa1 * Math.Cos((1.414 * 180d / HPPeriod) * Deg2Rad);
			hpc2 = hpb1;
			hpc3 = -hpa1 * hpa1;
			hpc1 = (1 + hpc2 - hpc3) / 4;
			ssa1 = Math.Exp(-1.414 * Math.PI / LPPeriod);
			ssb1 = 2.0 * ssa1 * Math.Cos((1.414 * 180d / LPPeriod) * Deg2Rad);
			ssc2 = ssb1;
			ssc3 = -ssa1 * ssa1;
			ssc1 = 1 - ssc2 - ssc3;

			/* 2 Pole Butterworth Highpass Filter */
			TimeSeries HP1 = new TimeSeries(bars.DateTimes, 0);
			TimeSeries HP2 = new TimeSeries(spy.DateTimes, 0);
			for (int i = 2; i < bars.DateTimes.Count; i++)
			{
				HP1[i] = hpc1 * (bars.Close[i] - 2 * bars.Close[i - 1] + bars.Close[i - 2]) + hpc2 * HP1[i - 1] + hpc3 * HP1[i - 2];
				HP2[i] = hpc1 * (spy.Close[i] - 2 * spy.Close[i - 1] + spy.Close[i - 2]) + hpc2 * HP2[i - 1] + hpc3 * HP2[i - 2];
			}

			/* Smooth with a Super Smoother Filter */
			TimeSeries Price = new TimeSeries(bars.DateTimes, 0);
			TimeSeries Price2 = new TimeSeries(spy.DateTimes, 0);
			for (int i = 2; i < bars.DateTimes.Count; i++)
			{
				Price[i] = ssc1 *(HP1[i] + HP1[i - 1]) / 2 + ssc2 *Price[i - 1] + ssc3 *Price[i - 2];
				Price2[i] = ssc1 *(HP2[i] + HP2[i - 1]) / 2 + ssc2 *Price2[i - 1] + ssc3 *Price2[i - 2];
			}

			/* Scale Price in terms of Standard Deviations */
			TimeSeries PriceMS = new TimeSeries(bars.DateTimes, 0);
			TimeSeries PriceRMS = new TimeSeries(bars.DateTimes, 0);
			TimeSeries Price2MS = new TimeSeries(spy.DateTimes, 0);
			TimeSeries Price2RMS = new TimeSeries(spy.DateTimes, 0);
			for (int i = 0; i < bars.DateTimes.Count; i++)
			{
				if (i < 2)
				{
					PriceMS[i] = Math.Pow(Price[i], 2);
					Price2MS[i] = Math.Pow(Price2[i], 2);
				}
				else
				{
					PriceMS[i] = 0.0242 * Price[i] * Price[i] + 0.9758 * PriceMS[i - 1];
					Price2MS[i] = 0.0242 * Price2[i] * Price2[i] + 0.9758 * Price2MS[i - 1];
				}
			
				if(PriceMS[i] != 0)
					PriceRMS[i] = Price[i] / Math.Sqrt(PriceMS[i]);
				if (Price2MS[i] != 0)
					Price2RMS[i] = Price2[i] / Math.Sqrt(Price2MS[i]);
			
				lstValuesP.Add(PriceRMS[i]);
				lstValuesP2.Add(Price2RMS[i]);
			}

			Bitmap bmp = null;
			Plot plt = new ScottPlot.Plot(800, 600);
			plt.Style(figureBackground: Color.FromArgb(51,53,54), dataBackground: Color.FromArgb(51,53,54), titleLabel: Color.White, grid: Color.White, axisLabel: Color.FromArgb(51,53,54));
		
			plt.Title("Ehlers Loops");
			plt.YLabel(bars.Symbol);
			plt.XLabel(spy.Symbol);

			plt.PlotScatter(lstValuesP2.ToArray(), lstValuesP.ToArray(), Color.Gold);
			bmp = plt.GetBitmap();
			DrawImageAt(bmp, 40, 20);
		}

		public override void Execute(BarHistory bars, int idx)
		{
		}

		double hpa1, hpb1, hpc2, hpc3, hpc1, ssa1, ssb1, ssc2, ssc3, ssc1;
		BarHistory spy;
	}
}
