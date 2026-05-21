using System;
using WealthLab.Backtest;
using WealthLab.Core;
using WealthLab.TASC;

namespace WealthScript
{
    public class GriffithSpectrum : UserStrategyBase
    {
		Parameter _ub, _lb, _length;
		
		public GriffithSpectrum()
		{
			_lb = AddParameter("Lowerbound", ParameterType.Int32, 18, 5, 40, 5);
			_ub = AddParameter("Upperbound", ParameterType.Int32, 40, 20, 125, 5);
			_length = AddParameter("Length", ParameterType.Int32, 54, 30, 60, 1);
		}
		
        public override void Initialize(BarHistory bars)
		{			
			TimeSeries ds = bars.Close;
			int ubound = _ub.AsInt;
			if (ubound > ds.Count) ubound = ds.Count;

			//initialize raster series
			SetPaneDrawingOptions("GrSp", 20);
			int nser = ubound - _lb.AsInt + 1;
			TimeSeries[] Raster = new TimeSeries[nser];
			for (int n = 0; n < nser; n++)
			{
				Raster[n] = new TimeSeries(bars.DateTimes, n + _lb.AsInt);
				PlotTimeSeriesLine(Raster[n], "", "GrSp", WLColor.Black, 8, suppressLabels:true);
			}

			double[] XX = new double[_length.AsInt];
			double[] coef = new double[_length.AsInt];
			double[,] Pwr = new double[nser, 2];
			int L1 = _length.AsInt - 1;

			double Mu = 1.0 / _length.AsInt;
			TimeSeries HP = new HighPass(ds, ubound);
			TimeSeries LP = new SuperSmoother(HP, _lb.AsInt);
			TimeSeries Peak = new TimeSeries(ds.DateTimes, 0.1);
			TimeSeries Signal = new TimeSeries(ds.DateTimes, 0);
			
			for (int bar = Math.Max(ubound, _length.AsInt); bar < ds.Count; bar++)
			{
				Peak[bar] = 0.991 * Peak[bar - 1];
				if (Math.Abs(LP[bar]) > Peak[bar])
					Peak[bar] = Math.Abs(LP[bar]);

				Signal[bar] = Peak[bar] != 0 ? LP[bar] / Peak[bar] : Signal[bar - 1];

				for (int count = 0; count < _length.AsInt; count++)
					XX[count] = Signal[bar - (L1 - count)];

				double XBar = 0;
				for (int count = 0; count < _length.AsInt; count++)
					XBar += XX[L1 - count] * coef[count];

				for (int count = 0; count < _length.AsInt; count++)
					coef[count] += Mu * (XX[L1] - XBar) * XX[L1 - count];

				//instantaneous frequency
				for (int pidx = 0; pidx < nser; pidx++)
				{
					double period = pidx + _lb.AsInt;
					Pwr[pidx, 1] = Pwr[pidx, 0];
					double real = 0;
					double imag = 0;

					for (int count = 0; count < _length.AsInt; count++)
					{
						real += coef[count] * Math.Cos(2 * Math.PI * count / period);
						imag += coef[count] * Math.Sin(2 * Math.PI * count / period);
					}
					double denom = (1 - real) * (1 - real) + imag * imag;
					Pwr[pidx, 0] = 0.1 / denom + 0.9 * Pwr[pidx, 1];
				}

				double maxPwr = 0;
				for (int pidx = 0; pidx < nser; pidx++)
					if (Pwr[pidx, 0] > maxPwr) 
						maxPwr = Pwr[pidx, 0];
					
				for (int pidx = 0; pidx < nser; pidx++)
					if (maxPwr != 0) Pwr[pidx, 0] = Pwr[pidx, 0] / maxPwr;

				//convert power to RGB color
				for (int pidx = 0; pidx < nser; pidx++)
				{
					double clr1 = Pwr[pidx, 0] >= 0.5 ? 255 : 255 * 2 * Pwr[pidx, 0]; 
					double clr2 = Pwr[pidx, 0] >= 0.5 ? 255 * (2 * Pwr[pidx, 0] - 1) : 0; 
					SetSeriesBarColor(Raster[pidx], bar, WLColor.FromRgb((byte)clr1, (byte)clr2, 0));
				}				
			}

			//Plot the Dominant Cycle
			GriffithsDC gdc = GriffithsDC.Series(ds, _lb.AsInt, _ub.AsInt, _length.AsInt);
			PlotTimeSeriesLine(gdc, gdc.Description, "GrSp", WLColor.WhiteSmoke, 4);
        }

        public override void Execute(BarHistory bars, int idx)
        {  }
    }
}
