using WealthLab.Backtest;
using System;
using WealthLab.Core;
using WealthLab.Indicators;
using WealthLab.TASC;

namespace WealthScript6 
{
    public class DrunkardAutoCorr : UserStrategyBase
    {
		Parameter _period;
		Parameter _testWave;		
			
		public DrunkardAutoCorr()
		{
			_period = AddParameter("Period", ParameterType.Int32, 20, 5, 60, 1);
			_testWave = AddParameter("Sine Test", ParameterType.Int32, 0, 0, 1);
		}

        public override void Initialize(BarHistory bars)
        {
			int length = _period.AsInt;
			double[] corr = new double[101];
			
			TimeSeries[] raster = new TimeSeries[101];
			for (int n = 0; n < 101; n++)
			{
				raster[n] = new TimeSeries(bars.DateTimes, n);
				PlotTimeSeriesLine(raster[n], "", "A/C", WLColor.Black, 4, suppressLabels: true);
			}
			DrawHeaderText($"AutoCorrelation({length})", WLColor.White, 12, "A/C");
			SetPaneDrawingOptions("A/C", 40);
			TimeSeries _filt = UltimateSmoother.Series(bars.Close, _period.AsInt);

			//Cycle test waveform
			if (_testWave.AsInt == 1)
			{
				_filt = new TimeSeries(bars.DateTimes);
				for (int n = 0; n < bars.Count; n++)
					_filt[n] = Math.Sin(2 * Math.PI * n / 20);
				PlotTimeSeriesLine(_filt, "Sine", "Sine");
			}
			
			for (int bar = length + 100; bar < bars.Count; bar++)
			{
				//>>>>>>>>> Correlation >>>>>>>>>>>>				
				for (int lag = 0; lag < 100; lag++)
				{
					double Sx = 0, Sy = 0, Sxx = 0, Sxy = 0, Syy = 0;
					for (int j = 0; j < length; j++)
					{
						double X = _filt[bar - j];
						double Y = _filt[bar - (lag + j)];
						Sx = Sx + X;
						Sy = Sy + Y;
						Sxx = Sxx + X * X;
						Sxy = Sxy + X * Y;
						Syy = Syy + Y * Y;
					}

					if (length * Sxx - Sx * Sx > 0 && length * Syy - Sy * Sy > 0)
						corr[lag + 1] = (length * Sxy - Sx * Sy) / Math.Sqrt((length * Sxx - Sx * Sx) * (length * Syy - Sy * Sy));
				}

				//convert AutoCorrelation to colors
				for (int lag = 1; lag < 100; lag++)
				{
					byte clr1 = 255;
					byte clr2 = 255;
					if (corr[lag + 1] >= 0)
						clr1 = (byte)(255 * (1 - corr[lag + 1]));
					else
						clr2 = (byte)(255 * (1 + corr[lag + 1]));						
					SetSeriesBarColor(raster[lag + 1], bar, WLColor.FromRgb(clr1, clr2, 0));
				}
			}
		}
		
		public override void Execute(BarHistory bars, int idx)
        {  }
    }
}
