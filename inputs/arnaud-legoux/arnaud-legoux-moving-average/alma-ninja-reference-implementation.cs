// https://www.sierrachart.com/SupportBoard.php?PostID=231318#P231318
//
// Post From: Arnaud Legoux Moving Average
// 2020-08-24 16:34:00]Link To Thread - Link To Post[Go To First Post]
// cmet - Posts: 723
// The original Ninjatrader study released for free on Legoux's website:

#region Using declarations 
using System;
using System.ComponentModel;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.Gui.Chart;
#endregion

// Copyright 2010 Arnaud Legoux / Dimitris Kouzis-Loukas / Anthony Cascino 

// This namespace holds all indicators and is required. Do not change it. 

namespace NinjaTrader.Indicator
{
    /// <summary> 
    /// ALMA (Arnaud Legoux MA) 
    /// </summary> 
    [Description("ALMA (contact@arnaudlegoux.com) by Arnaud Legoux / Dimitris Kouzis-Loukas / Anthony Cascino")]
    public class ALMA : Indicator
    {
        private int iWindowSize = 9;
        private double iM_Sigma = 6.0;
        private double iP_Sample = 0.5;
        private double[] aALMA;

        /// <summary> 
        /// This method is used to configure the indicator and is called once before any bar data is loaded. 
        /// </summary> 
        protected override void Initialize()
        {
            Add(new Plot(Color.FromKnownColor(KnownColor.LightSkyBlue), PlotStyle.Line, "ALMA_Plot"));
            CalculateOnBarClose = true;
            Overlay = true;
            PriceTypeSupported = false;
            BarsRequired = 3;

            aALMA = new double[iWindowSize];

            ResetWindow();
        }

        /// <summary> 
        /// Called on each bar update event (incoming tick) 
        /// </summary> 
        protected override void OnBarUpdate()
        {
            if (CurrentBar < iWindowSize)
                return;

            int pt = 0;
            double agr = 0;
            double norm = 0;

            for (int i = 0; i < iWindowSize; i++)
            {
                if (i < iWindowSize - pt)
                {
                    agr += aALMA[i] * Close[iWindowSize - pt - 1 - i];
                    norm += aALMA[i];
                }
            }

            // Normalize the result 
            if (norm != 0) agr /= norm;

            // Set the approrpiate bar. 
            ALMA_Plot.Set(agr);
        }

        #region helper 
        private void ResetWindow()
        {
            double m = (int)Math.Floor(iP_Sample * (double)(iWindowSize - 1));
            double s = iWindowSize;
            s /= iM_Sigma;

            for (int i = 0; i < iWindowSize; i++)
            {
                aALMA[i] = Math.Exp(-((((double)i) - m) * (((double)i) - m)) / (2 * s * s));
            }
        }
        #endregion
        #region Properties 

        [Browsable(false)]  // this line prevents the data series from being displayed in the indicator properties dialog, do not remove 
        [XmlIgnore()]    // this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove 
        public DataSeries ALMA_Plot
        {
            get { return Values[0]; }
        }

        [Description("Sample point. Where in terms of the window should we take the current value (0-1)")]
        [Category("Parameters")]
        public double SamplePoint
        {
            get { return iP_Sample; }
            set { iP_Sample = Math.Min(Math.Max(0.0, value), 1.0); }
        }

        [Description("ALMA period. Must be an odd number.")]
        [Category("Parameters")]
        public int WindowSize
        {
            get { return iWindowSize; }
            set
            {
                iWindowSize = Math.Min(Math.Max(1, value), 50);

                // Only odd sizes 
                if ((iWindowSize & 1) == 0)
                {
                    iWindowSize++;
                }

                //ResetWindow(); 
            }
        }

        [Description("Precision / Smoothing")]
        [Category("Parameters")]
        public double Sigma
        {
            get { return iM_Sigma; }
            set
            {
                iM_Sigma = Math.Min(Math.Max(0.01, value), 50.0); //ResetWindow(); 
            }
        }
        #endregion
    }
}

#region NinjaScript generated code. Neither change nor remove. 

// This namespace holds all indicators and is required. Do not change it. 
namespace NinjaTrader.Indicator
{
    public partial class Indicator : IndicatorBase
    {
        private ALMA[] cacheALMA = null;
        private static ALMA checkALMA = new ALMA();

        /// <summary> 
        /// ALMA (contact@arnaudlegoux.com) by Arnaud Legoux / Dimitris Kouzis-Loukas / Anthony Cascino 
        /// </summary> 
        /// <returns></returns> 
        public ALMA ALMA(double samplePoint, double sigma, int windowSize)
        {
            return ALMA(Input, samplePoint, sigma, windowSize);
        }

        /// <summary> 
        /// ALMA (contact@arnaudlegoux.com) by Arnaud Legoux / Dimitris Kouzis-Loukas / Anthony Cascino 
        /// </summary> 
        /// <returns></returns> 
        public ALMA ALMA(Data.IDataSeries input, double samplePoint, double sigma, int windowSize)
        {
            checkALMA.SamplePoint = samplePoint;
            samplePoint = checkALMA.SamplePoint;
            checkALMA.Sigma = sigma;
            sigma = checkALMA.Sigma;
            checkALMA.WindowSize = windowSize;
            windowSize = checkALMA.WindowSize;

            if (cacheALMA != null)
                for (int idx = 0; idx < cacheALMA.Length; idx++)
                    if (Math.Abs(cacheALMA[idx].SamplePoint - samplePoint) <= double.Epsilon && Math.Abs(cacheALMA[idx].Sigma - sigma) <= double.Epsilon && cacheALMA[idx].WindowSize == windowSize && cacheALMA[idx].EqualsInput(input))
                        return cacheALMA[idx];

            ALMA indicator = new ALMA();
            indicator.BarsRequired = BarsRequired;
            indicator.CalculateOnBarClose = CalculateOnBarClose;
            indicator.Input = input;
            indicator.SamplePoint = samplePoint;
            indicator.Sigma = sigma;
            indicator.WindowSize = windowSize;
            indicator.SetUp();

            ALMA[] tmp = new ALMA[cacheALMA == null ? 1 : cacheALMA.Length + 1];

            if (cacheALMA != null)
                cacheALMA.CopyTo(tmp, 0);

            tmp[tmp.Length - 1] = indicator;
            cacheALMA = tmp;
            Indicators.Add(indicator);

            return indicator;
        }
    }
}

// This namespace holds all market analyzer column definitions and is required. Do not change it. 
namespace NinjaTrader.MarketAnalyzer
{
    public partial class Column : ColumnBase
    {
        /// <summary> 
        /// ALMA (contact@arnaudlegoux.com) by Arnaud Legoux / Dimitris Kouzis-Loukas / Anthony Cascino 
        /// </summary> 
        /// <returns></returns> 
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.ALMA ALMA(double samplePoint, double sigma, int windowSize)
        {
            return _indicator.ALMA(Input, samplePoint, sigma, windowSize);
        }

        /// <summary> 
        /// ALMA (contact@arnaudlegoux.com) by Arnaud Legoux / Dimitris Kouzis-Loukas / Anthony Cascino 
        /// </summary> 
        /// <returns></returns> 
        public Indicator.ALMA ALMA(Data.IDataSeries input, double samplePoint, double sigma, int windowSize)
        {
            return _indicator.ALMA(input, samplePoint, sigma, windowSize);
        }
    }
}

// This namespace holds all strategies and is required. Do not change it. 
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary> 
        /// ALMA (contact@arnaudlegoux.com) by Arnaud Legoux / Dimitris Kouzis-Loukas / Anthony Cascino 
        /// </summary> 
        /// <returns></returns> 
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.ALMA ALMA(double samplePoint, double sigma, int windowSize)
        {
            return _indicator.ALMA(Input, samplePoint, sigma, windowSize);
        }

        /// <summary> 
        /// ALMA (contact@arnaudlegoux.com) by Arnaud Legoux / Dimitris Kouzis-Loukas / Anthony Cascino 
        /// </summary> 
        /// <returns></returns> 
        public Indicator.ALMA ALMA(Data.IDataSeries input, double samplePoint, double sigma, int windowSize)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.ALMA(input, samplePoint, sigma, windowSize);
        }
    }
}

#endregion
