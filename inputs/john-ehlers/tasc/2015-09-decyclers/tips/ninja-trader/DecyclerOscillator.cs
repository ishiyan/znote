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

// This namespace holds all indicators and is required. Do not change it.
namespace NinjaTrader.Indicator
{
    /// <summary>
    /// Decycler Osciallator by John F. Ehlers
    /// </summary>
    [Description("Decycler Osciallator by John F. Ehlers")]
    public class DecyclerOscillator : Indicator
    {
        #region Variables
        private int hPPeriod = 125;
        private double k = 1;
		private double alpha1 = 0;
		private double alpha2 = 0;
		private DataSeries hp;
		private DataSeries decycle;
		private DataSeries decycleOsc;
        #endregion

        /// <summary>
        /// This method is used to configure the indicator and is called once before any bar data is loaded.
        /// </summary>
        protected override void Initialize()
        {
            Add(new Plot(Color.FromKnownColor(KnownColor.Red), PlotStyle.Line, "Plot0"));
            Add(new Line(Color.FromKnownColor(KnownColor.Blue), 0, "Zero"));
			
            Overlay				= false;
			
			hp = new DataSeries(this);
			decycle = new DataSeries(this);
			decycleOsc = new DataSeries(this);
        }

        protected override void OnStartUp()
		{
			alpha1 = (Math.Cos(((.707*360/HPPeriod)*Math.PI)/180) + Math.Sin(((.707*360/HPPeriod)*Math.PI)/180) -1) / Math.Cos(((.707*360/HPPeriod)*Math.PI)/180);
			alpha2 = (Math.Cos(((.707*360/(.5*HPPeriod))*Math.PI)/180) + Math.Sin(((.707*360/(.5*HPPeriod))*Math.PI)/180) -1) / Math.Cos(((.707*360/(.5*HPPeriod))*Math.PI)/180);
		}
		
        protected override void OnBarUpdate()
        {
            if(CurrentBar <= 2)
			{
				hp[0] = 0;
				decycle[0] = Close[0];
				decycleOsc[0] = Close[0];
				return;
			}
			
			hp[0] = (1-alpha1/2)*(1-alpha1/2)*(Close[0]-2*Close[1]+Close[2])+2*(1-alpha1)*hp[1]-(1-alpha1)*(1-alpha1)*hp[2];
			
			decycle[0] = Close[0] - hp[0];
						
			decycleOsc[0] = (1-alpha2/2)*(1-alpha2/2)*(decycle[0]-2*decycle[1]+decycle[2])+2*(1-alpha2)*decycleOsc[1]-(1-alpha2)*(1-alpha2)*decycleOsc[2];
			
			Value[0] = 100*K*decycleOsc[0]/Close[0];
        }

        #region Properties
        [Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries Plot0
        {
            get { return Values[0]; }
        }

        [Description("")]
        [GridCategory("Parameters")]
        public int HPPeriod
        {
            get { return hPPeriod; }
            set { hPPeriod = Math.Max(1, value); }
        }

        [Description("")]
        [GridCategory("Parameters")]
        public double K
        {
            get { return k; }
            set { k = Math.Max(1, value); }
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
        private DecyclerOscillator[] cacheDecyclerOscillator = null;

        private static DecyclerOscillator checkDecyclerOscillator = new DecyclerOscillator();

        /// <summary>
        /// Decycler Osciallator by John F. Ehlers
        /// </summary>
        /// <returns></returns>
        public DecyclerOscillator DecyclerOscillator(int hPPeriod, double k)
        {
            return DecyclerOscillator(Input, hPPeriod, k);
        }

        /// <summary>
        /// Decycler Osciallator by John F. Ehlers
        /// </summary>
        /// <returns></returns>
        public DecyclerOscillator DecyclerOscillator(Data.IDataSeries input, int hPPeriod, double k)
        {
            if (cacheDecyclerOscillator != null)
                for (int idx = 0; idx < cacheDecyclerOscillator.Length; idx++)
                    if (cacheDecyclerOscillator[idx].HPPeriod == hPPeriod && Math.Abs(cacheDecyclerOscillator[idx].K - k) <= double.Epsilon && cacheDecyclerOscillator[idx].EqualsInput(input))
                        return cacheDecyclerOscillator[idx];

            lock (checkDecyclerOscillator)
            {
                checkDecyclerOscillator.HPPeriod = hPPeriod;
                hPPeriod = checkDecyclerOscillator.HPPeriod;
                checkDecyclerOscillator.K = k;
                k = checkDecyclerOscillator.K;

                if (cacheDecyclerOscillator != null)
                    for (int idx = 0; idx < cacheDecyclerOscillator.Length; idx++)
                        if (cacheDecyclerOscillator[idx].HPPeriod == hPPeriod && Math.Abs(cacheDecyclerOscillator[idx].K - k) <= double.Epsilon && cacheDecyclerOscillator[idx].EqualsInput(input))
                            return cacheDecyclerOscillator[idx];

                DecyclerOscillator indicator = new DecyclerOscillator();
                indicator.BarsRequired = BarsRequired;
                indicator.CalculateOnBarClose = CalculateOnBarClose;
#if NT7
                indicator.ForceMaximumBarsLookBack256 = ForceMaximumBarsLookBack256;
                indicator.MaximumBarsLookBack = MaximumBarsLookBack;
#endif
                indicator.Input = input;
                indicator.HPPeriod = hPPeriod;
                indicator.K = k;
                Indicators.Add(indicator);
                indicator.SetUp();

                DecyclerOscillator[] tmp = new DecyclerOscillator[cacheDecyclerOscillator == null ? 1 : cacheDecyclerOscillator.Length + 1];
                if (cacheDecyclerOscillator != null)
                    cacheDecyclerOscillator.CopyTo(tmp, 0);
                tmp[tmp.Length - 1] = indicator;
                cacheDecyclerOscillator = tmp;
                return indicator;
            }
        }
    }
}

// This namespace holds all market analyzer column definitions and is required. Do not change it.
namespace NinjaTrader.MarketAnalyzer
{
    public partial class Column : ColumnBase
    {
        /// <summary>
        /// Decycler Osciallator by John F. Ehlers
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.DecyclerOscillator DecyclerOscillator(int hPPeriod, double k)
        {
            return _indicator.DecyclerOscillator(Input, hPPeriod, k);
        }

        /// <summary>
        /// Decycler Osciallator by John F. Ehlers
        /// </summary>
        /// <returns></returns>
        public Indicator.DecyclerOscillator DecyclerOscillator(Data.IDataSeries input, int hPPeriod, double k)
        {
            return _indicator.DecyclerOscillator(input, hPPeriod, k);
        }
    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// Decycler Osciallator by John F. Ehlers
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.DecyclerOscillator DecyclerOscillator(int hPPeriod, double k)
        {
            return _indicator.DecyclerOscillator(Input, hPPeriod, k);
        }

        /// <summary>
        /// Decycler Osciallator by John F. Ehlers
        /// </summary>
        /// <returns></returns>
        public Indicator.DecyclerOscillator DecyclerOscillator(Data.IDataSeries input, int hPPeriod, double k)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.DecyclerOscillator(input, hPPeriod, k);
        }
    }
}
#endregion
