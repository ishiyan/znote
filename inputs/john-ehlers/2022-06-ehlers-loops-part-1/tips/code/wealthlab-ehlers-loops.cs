using WealthLab.Backtest;
using System;
using WealthLab.Core;
using WealthLab.Indicators;
using System.Drawing;
using System.Collections.Generic;
using ScottPlot;

namespace WealthScript1 
{
	public class TASC202206EhlersLoops : UserStrategyBase
	{
		/* create indicators and other objects here, this is executed prior to the main trading loop */
		public override void Initialize(BarHistory bars)
		{
			int LPPeriod = 20, HPPeriod = 125;
			double Deg2Rad = Math.PI / 180.0;
			List<double> lstDates = new List<double>();
			List<double> lstValuesP = new List<double>();
			List<double> lstValuesV = new List<double>();

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
			TimeSeries HP = new TimeSeries(bars.DateTimes, 0);
			for (int i = 2; i < bars.DateTimes.Count; i++)
			{
				HP[i] = hpc1 * (bars.Close[i] - 2 * bars.Close[i - 1] + bars.Close[i - 2]) + hpc2 * HP[i - 1] + hpc3 * HP[i - 2];
			}

			/* Smooth with a Super Smoother Filter */
			TimeSeries Price = new TimeSeries(bars.DateTimes, 0);
			for (int i = 2; i < bars.DateTimes.Count; i++)
			{
				Price[i] = ssc1 *(HP[i] + HP[i - 1]) / 2 + ssc2 *Price[i - 1] + ssc3 *Price[i - 2];
			}

			/* Scale Price in terms of Standard Deviations */
			TimeSeries PriceMS = new TimeSeries(bars.DateTimes, 0);
			TimeSeries PriceRMS = new TimeSeries(bars.DateTimes, 0);
			for (int i = 0; i < bars.DateTimes.Count; i++)
			{
				if(i < 2)
					PriceMS[i] = Math.Pow(Price[i], 2);
				else
					PriceMS[i] = 0.0242 * Price[i] * Price[i] + 0.9758 * PriceMS[i - 1];
				if(PriceMS[i] != 0)
					PriceRMS[i] = Price[i] / Math.Sqrt(PriceMS[i]);
				
				lstValuesP.Add(PriceRMS[i]);
			}

			/* Normalized Roofing Filter for Volume */
			
			/* 2 Pole Butterworth Highpass Filter */
			TimeSeries VolHP = new TimeSeries(bars.DateTimes, 0);
			for (int i = 2; i < bars.DateTimes.Count; i++)
			{
				VolHP[i] = hpc1 * (bars.Volume[i] - 2 * bars.Volume[i - 1] + bars.Volume[i - 2]) + hpc2 * VolHP[i - 1] + hpc3 * VolHP[i - 2];
			}

			/* Smooth with a Super Smoother Filter */
			TimeSeries Vol = new TimeSeries(bars.DateTimes, 0);
			for (int i = 2; i < bars.DateTimes.Count; i++)
			{ 
				Vol[i] = ssc1 * (VolHP[i] + VolHP[i - 1]) / 2 + ssc2 * Vol[i - 1] + ssc3 * Vol[i - 2];
			}
		
			/* Scale Vol in terms of Standard Deviations */
			TimeSeries VolMS = new TimeSeries(bars.DateTimes, 0);
			TimeSeries VolRMS = new TimeSeries(bars.DateTimes, 0);
			for (int i = 0; i < bars.DateTimes.Count; i++)
			{
				lstDates.Add(i);
				
				if (i < 2)
					VolMS[i] = Math.Pow(Vol[i], 2);
				else 
					VolMS[i] = 0.0242 * Vol[i] * Vol[i] + 0.9758 * VolMS[i - 1];

				if (VolMS[i] != 0)
					VolRMS[i] = Vol[i] / Math.Sqrt(VolMS[i]);
					
				lstValuesV.Add(VolRMS[i]);
			}


			Bitmap bmp = null;
			Plot plt = new ScottPlot.Plot(800, 600);
			plt.Title("Ehlers Loops");
			plt.YLabel("Price");
			plt.XLabel("Volume");

			plt.PlotScatter(lstValuesV.ToArray(), lstValuesP.ToArray());
			bmp = plt.GetBitmap();
			DrawImageAt(bmp, 40, 20);
		}

		/* execute the strategy rules here, this is executed once for each bar in the backtest history */
		public override void Execute(BarHistory bars, int idx)
		{
		}

		/* declare private variables below */
		double hpa1, hpb1, hpc2, hpc3, hpc1, ssa1, ssb1, ssc2, ssc3, ssc1;
	}
}
