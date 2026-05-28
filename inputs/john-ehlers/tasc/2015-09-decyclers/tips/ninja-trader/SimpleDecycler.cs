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
    /// Simple Decycler by John F. Ehlers
    /// </summary>
    [Description("Simple Decycler by John F. Ehlers")]
    public class SimpleDecycler : Indicator
    {
        #region Variables
        private int hPPeriod = 125;
		private double alpha1 = 0;
		private double decycle = 0;
		private DataSeries hp;
        #endregion

        /// <summary>
        /// This method is used to configure the indicator and is called once before any bar data is loaded.
        /// </summary>
        protected override void Initialize()
        {
            Add(new Plot(Color.FromKnownColor(KnownColor.Red), PlotStyle.Line, "Decycle"));
            Add(new Plot(Color.FromKnownColor(KnownColor.Yellow), PlotStyle.Line, "DecycleOffsetUp"));
            Add(new Plot(Color.FromKnownColor(KnownColor.Yellow), PlotStyle.Line, "DecycleOffsetDown"));
			
            Overlay				= true;
			
			hp = new DataSeries(this);
        }

		protected override void OnStartUp()
		{
			alpha1 = (Math.Cos(((.707*360/HPPeriod)*Math.PI)/180) + Math.Sin(((.707*360/HPPeriod)*Math.PI)/180) -1) / Math.Cos(((.707*360/HPPeriod)*Math.PI)/180);
		}
		
        protected override void OnBarUpdate()
        {
			if(CurrentBar <= 2)
			{
				hp[0] = 0;
				return;
			}
			
			hp[0] = (1-alpha1/2)*(1-alpha1/2)*(Close[0]-2*Close[1]+Close[2])+2*(1-alpha1)*hp[1]-(1-alpha1)*(1-alpha1)*hp[2];
			
			decycle = Close[0] - hp[0];
			
            Decycle.Set(decycle);
            DecycleOffsetUp.Set(1.005*decycle);
            DecycleOffsetDown.Set(.995*decycle);
        }

        #region Properties
        [Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries Decycle
        {
            get { return Values[0]; }
        }

        [Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries DecycleOffsetUp
        {
            get { return Values[1]; }
        }

        [Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries DecycleOffsetDown
        {
            get { return Values[2]; }
        }

        [Description("")]
        [GridCategory("Parameters")]
        public int HPPeriod
        {
            get { return hPPeriod; }
            set { hPPeriod = Math.Max(1, value); }
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
        private SimpleDecycler[] cacheSimpleDecycler = null;

        private static SimpleDecycler checkSimpleDecycler = new SimpleDecycler();

        /// <summary>
        /// Simple Decycler by John F. Ehlers
        /// </summary>
        /// <returns></returns>
        public SimpleDecycler SimpleDecycler(int hPPeriod)
        {
            return SimpleDecycler(Input, hPPeriod);
        }

        /// <summary>
        /// Simple Decycler by John F. Ehlers
        /// </summary>
        /// <returns></returns>
        public SimpleDecycler SimpleDecycler(Data.IDataSeries input, int hPPeriod)
        {
            if (cacheSimpleDecycler != null)
                for (int idx = 0; idx < cacheSimpleDecycler.Length; idx++)
                    if (cacheSimpleDecycler[idx].HPPeriod == hPPeriod && cacheSimpleDecycler[idx].EqualsInput(input))
                        return cacheSimpleDecycler[idx];

            lock (checkSimpleDecycler)
            {
                checkSimpleDecycler.HPPeriod = hPPeriod;
                hPPeriod = checkSimpleDecycler.HPPeriod;

                if (cacheSimpleDecycler != null)
                    for (int idx = 0; idx < cacheSimpleDecycler.Length; idx++)
                        if (cacheSimpleDecycler[idx].HPPeriod == hPPeriod && cacheSimpleDecycler[idx].EqualsInput(input))
                            return cacheSimpleDecycler[idx];

                SimpleDecycler indicator = new SimpleDecycler();
                indicator.BarsRequired = BarsRequired;
                indicator.CalculateOnBarClose = CalculateOnBarClose;
#if NT7
                indicator.ForceMaximumBarsLookBack256 = ForceMaximumBarsLookBack256;
                indicator.MaximumBarsLookBack = MaximumBarsLookBack;
#endif
                indicator.Input = input;
                indicator.HPPeriod = hPPeriod;
                Indicators.Add(indicator);
                indicator.SetUp();

                SimpleDecycler[] tmp = new SimpleDecycler[cacheSimpleDecycler == null ? 1 : cacheSimpleDecycler.Length + 1];
                if (cacheSimpleDecycler != null)
                    cacheSimpleDecycler.CopyTo(tmp, 0);
                tmp[tmp.Length - 1] = indicator;
                cacheSimpleDecycler = tmp;
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
        /// Simple Decycler by John F. Ehlers
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.SimpleDecycler SimpleDecycler(int hPPeriod)
        {
            return _indicator.SimpleDecycler(Input, hPPeriod);
        }

        /// <summary>
        /// Simple Decycler by John F. Ehlers
        /// </summary>
        /// <returns></returns>
        public Indicator.SimpleDecycler SimpleDecycler(Data.IDataSeries input, int hPPeriod)
        {
            return _indicator.SimpleDecycler(input, hPPeriod);
        }
    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// Simple Decycler by John F. Ehlers
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.SimpleDecycler SimpleDecycler(int hPPeriod)
        {
            return _indicator.SimpleDecycler(Input, hPPeriod);
        }

        /// <summary>
        /// Simple Decycler by John F. Ehlers
        /// </summary>
        /// <returns></returns>
        public Indicator.SimpleDecycler SimpleDecycler(Data.IDataSeries input, int hPPeriod)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.SimpleDecycler(input, hPPeriod);
        }
    }
}
#endregion
