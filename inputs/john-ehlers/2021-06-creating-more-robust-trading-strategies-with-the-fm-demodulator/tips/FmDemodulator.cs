using WealthLab.Backtest;
using System;
using WealthLab.Core;
using WealthLab.Indicators;
using System.Drawing;
using System.Collections.Generic;

namespace TASCStrategies
{
	public class TASC202106 : UserStrategyBase
	{
		public override void Initialize(BarHistory bars)
		{
			roc = new TimeSeries( bars.DateTimes, 0);
			signal = new TimeSeries( bars.DateTimes, 0);
			clip = new TimeSeries( bars.DateTimes, 0);
			Z3 = new TimeSeries( bars.DateTimes, 0);
			RMS = new TimeSeries( bars.DateTimes, 0);

			/* Derivative of the price wave */
			var Deriv = bars.Close - (bars.Close >> 2);
			Deriv[0] = Deriv[1] = 0;

			for (int bar = 0; bar < bars.Count; bar++)
			{
				if (bar >= period)
				{
					for (int count = 0; count < period - 1; count++)
					{
						if (bar > period)
							rms += Math.Pow(Deriv[bar - count], 2);
					}

					RMS[bar] = rms;

					double _clip = 0;
					if (RMS[bar] != 0)
						_clip = 2 * Deriv[bar] / Math.Sqrt(RMS[bar] / 50);
					if (_clip > 1) _clip = 1;
					if (_clip < -1) _clip = -1;
					clip[bar] = _clip;

					/* zeros at Nyquist and 2*Nyquist, i.e. Z3 = (1 + Z^-1)*(1 + Z^-2) to integrate derivative */
					Z3[bar] = clip[bar] + clip[bar - 1] + clip[bar - 2] + clip[bar - 3];
				}
			}

			/* Smooth Z2 for trading signal */
			signal = SMA.Series(Z3, SigPeriod);
			/* Use Rate of Change to identify entry point */
			roc = signal - (signal >>ROCPeriod);

			PlotTimeSeries( signal, "Signal", "FMD", Color.Red);
			PlotTimeSeries( roc, "RoC", "FMD");
			DrawHorzLine( 0, Color.Violet, 2, LineStyles.Dashed, "FMD");
			
			StartIndex = Math.Max(ROCPeriod, Math.Max(SigPeriod, period));
		}

		public override void Execute(BarHistory bars, int idx)
		{
			if (!HasOpenPosition(bars, PositionType.Long))
			{
				/* If ROC Crosses Over 0 Then Buy Next Bar on Open;*/ 
				if (roc.CrossesOver(0, idx))
					PlaceTrade( bars, TransactionType.Buy, OrderType.Market);
			}
			else
			{
				/* If Signal Crosses Under 0 Then Sell Next Bar on Open; */
				if (signal.CrossesUnder(0, idx))
					ClosePosition( LastPosition, OrderType.Market);
			}
		}

		/* declare private variables below */
		TimeSeries roc, signal, clip, Z3, RMS;
		int SigPeriod = 22, ROCPeriod = 10, period = 49; /* Normalize Degap to half RMS and hard limit at +/- 1 */
		double rms = 0;
	}
}
