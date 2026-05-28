using System;
using WealthLab.Indicators;
using System.Collections;
using System.Drawing;
using WealthLab.Backtest;
using WealthLab.Core;
using WealthLab.TASC;

namespace WealthScript1
{
    public class May2021 : UserStrategyBase
    {
        public May2021() : base()
        {
            AddParameter("Reversal", ParameterTypes.Double, 0.25, 0.25, 1.0, 0.25);
        }

        public override void Initialize(BarHistory bars)
        {
            reversal = Parameters[0].AsDouble;
            fmd = FMDemodulator.Series(bars, 30);
            amd = AMDetector.Series(bars, 4, 8);
            ptc = new PeakTroughCalculator( fmd, reversal, PeakTroughReversalTypes.Point);

            PlotTimeSeries( fmd, "FM Demodulator", "FMD", Color.BlueViolet);
            PlotTimeSeries( amd, "AM Detector", "AMD", Color.Violet);
            RenderPeakTroughs(ptc, Color.Red, "FMD");

            /* Dominant Cycle */
            TimeSeries dc;
            DominantCycle(bars, bars.AveragePriceHL, out dc);
        }

        /* execute the strategy rules here, this is executed once for each bar in the backtest history*/
        public override void Execute(BarHistory bars, int idx)
        {
            if (ptc.TroughState(idx) == 1 && ptc.TroughState(idx - 1) != 1)
            {
                PlaceTrade( bars, TransactionType.Buy, OrderType.Market);
            }
        }

        /* render peaks and troughs in a pane */
        private void RenderPeakTroughs(PeakTroughCalculator ptc, Color color, string paneTag)
        {
            if (ptc.PeakTroughs.Count < 2)
                return;

            for (int n = 1; n < ptc.PeakTroughs.Count; n++)
            {
                int x1 = ptc.PeakTroughs[n - 1].PeakTroughIndex;
                double y1 = ptc.PeakTroughs[n - 1].Value;
                int x2 = ptc.PeakTroughs[n].PeakTroughIndex;
                double y2 = ptc.PeakTroughs[n].Value;
                DrawLine( x1, y1, x2, y2, Color.Red, 2, LineStyles.Solid, paneTag);
            }
        }

        FMDemodulator fmd;
        AMDetector amd;
        PeakTroughCalculator ptc;
        double reversal;
        const double twoPi = 2 * Math.PI;
        const double fourPi = 4 * Math.PI;

        public class ArrayHolder
        {   /* current, old, older */
            internal double I, I2, I3;
            internal double Q, Q2, Q3;
            internal double R, R2, R3;
            internal double Im, Im2, Im3;
            internal double A;
            internal double dB, dB2;
        }

        public void DominantCycle(BarHistory bars, TimeSeries ds, out TimeSeries domCycMdn)
        {
            /* Initialize arrays */
            ArrayHolder[] ah = new ArrayHolder[52];
            for (int n = 12; n < 52; n++)
                ah[n] = new ArrayHolder();

            double domCycle = 0d;
            string s = ds.Description + ")";
            TimeSeries[] DB = new TimeSeries[52];
            TimeSeries domCyc = new TimeSeries(ds.DateTimes, 0); domCyc.Description = "DC(" + s;
            domCycMdn = new TimeSeries(ds.DateTimes, 0); domCycMdn.Description = "DomCyc(" + s;

            /* Create and plot the decibel series - change the colors later */
            for ( int n = 12; n < 52; n++)
            {
                double d = n / 2.0;
                DB[n] = domCyc + d;
                DB[n].Description = "Cycle." + d.ToString();
                PlotTimeSeriesLine( DB[n], "", "dbPane", Color.Black, 4, LineStyles.Solid, true);
            }

            /* Convert decibels to RGB color for display */
            Color[] color = new Color[21];
            for (int n = 0; n <= 10; n++)       /* yellow to red: 0 to 10 dB */
                color[n] = Color.FromArgb(255, (int)(255 - (255 * n / 10)), 0);
            for (int n = 11; n <= 20; n++)      /* red to black: 11 to 20 db */
                color[n] = Color.FromArgb((int)(255 * (20 - n) / 10), 0, 0);

            /* Detrend data by High Pass Filtering with a 40 Period cutoff */
            TimeSeries HP = domCyc;
            double alpha = (1 - Math.Sin(twoPi / 30)) / Math.Cos(twoPi / 30);
            for (int bar = 1; bar < ds.Count; bar++)
                HP[bar] = 0.5 * (1 + alpha) * Momentum.Series(ds, 1)[bar] + alpha * HP[bar - 1];
            FIRSmoother smoothHP = new FIRSmoother(HP);  //FIR.Series(HP, "1,2,3,3,2,1");

            ArrayList fifoList = new ArrayList(51);
            ArrayList fifoPsn = new ArrayList(21);

            for (int bar = 51; bar < ds.Count; bar++)
            {
                double maxAmpl = 0d;
                double delta = -0.015 * bar + 0.5;
                delta = delta < 0.1 ? 0.1 : delta;
                for (int n = 12; n < 52; n++)
                {
                    double beta = Math.Cos(fourPi / n);
                    double g = 1 / Math.Cos(2 * fourPi * delta / n);
                    double a = g - Math.Sqrt(g * g - 1);
                    ah[n].Q = Momentum.Series(smoothHP, 1)[bar] * n / fourPi;
                    ah[n].I = smoothHP[bar];
                    ah[n].R = 0.5 * (1 - a) * (ah[n].I - ah[n].I3) + beta * (1 + a) * ah[n].R2 - a * ah[n].R3;
                    ah[n].Im = 0.5 * (1 - a) * (ah[n].Q - ah[n].Q3) + beta * (1 + a) * ah[n].Im2 - a * ah[n].Im3;
                    ah[n].A = ah[n].R * ah[n].R + ah[n].Im * ah[n].Im;
                    maxAmpl = ah[n].A > maxAmpl ? ah[n].A : maxAmpl;
                }

                double num = 0; double den = 0;
                for (int n = 12; n < 52; n++)
                {
                    ah[n].I3 = ah[n].I2;
                    ah[n].I2 = ah[n].I;
                    ah[n].Q3 = ah[n].Q2;
                    ah[n].Q2 = ah[n].Q;
                    ah[n].R3 = ah[n].R2;
                    ah[n].R2 = ah[n].R;
                    ah[n].Im3 = ah[n].Im2;
                    ah[n].Im2 = ah[n].Im;
                    ah[n].dB2 = ah[n].dB;

                    if (maxAmpl != 0 && ah[n].A / maxAmpl > 0)
                        ah[n].dB = 10 * Math.Log10((1 - 0.99 * ah[n].A / maxAmpl) / 0.01);
                    ah[n].dB = 0.33 * ah[n].dB + 0.67 * ah[n].dB2;
                    ah[n].dB = ah[n].dB > 20 ? 20 : ah[n].dB;
                    SetSeriesBarColor( DB[n], bar, color[(int)Math.Round(ah[n].dB)]);

                    if (ah[n].dB <= 6)
                    {
                        num += n * (20 - ah[n].dB);
                        den += (20 - ah[n].dB);
                    }
                    if (den != 0) domCycle = 0.5 * num / den;
                }
                domCycMdn[bar] = Median.Value(bar, domCyc, 5);
                domCycMdn[bar] = domCycle < 6 ? 6 : domCycle;
            }
        }
    }
}
