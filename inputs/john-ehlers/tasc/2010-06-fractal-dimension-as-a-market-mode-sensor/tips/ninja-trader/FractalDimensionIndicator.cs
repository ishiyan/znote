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
    /// This is the Fractal Dimension Indicator as described in the May 2010 issue of Stocks & Commodities.
    /// </summary>
    [Description("This is the Fractal Dimension Indicator as described in the May 2010 issue of Stocks & Commodities.")]
    public class FractalDimensionIndicator : Indicator
    {
        #region Variables
        private int n = 30; // Default setting for N
		private DataSeries smooth, price, ratio;
		private double n1, n2, n3, hh, ll = 0;
        #endregion

        /// <summary>
        /// This method is used to configure the indicator and is called once before any bar data is loaded.
        /// </summary>
        protected override void Initialize()
        {
            Add(new Plot(Color.FromKnownColor(KnownColor.Red), PlotStyle.Line, "Dimension_Plot"));
            Add(new Line(Color.FromKnownColor(KnownColor.DodgerBlue), 1.6, "FuzzyUpper"));
            Add(new Line(Color.FromKnownColor(KnownColor.DodgerBlue), 1.4, "FuzzyLower"));
            CalculateOnBarClose	= true;
            Overlay				= false;
            PriceTypeSupported	= false;
			
			smooth	= new DataSeries(this);
			price	= new DataSeries(this);
			ratio	= new DataSeries(this);
        }

        /// <summary>
        /// Called on each bar update event (incoming tick)
        /// </summary>
        protected override void OnBarUpdate()
        {
            price.Set((High[0] + Low[0]) / 2);
			
			if (CurrentBar == 0)
				smooth.Set(price[0]);
			else if (CurrentBar == 1)
				smooth.Set((price[0] + 2 * price[1]) / 3);
			else if (CurrentBar == 2)
				smooth.Set((price[0] + 2 * price[1] + 2 * price[2]) / 5);
			else
				smooth.Set((price[0] + 2 * price[1] + 2 * price[2] + price[3]) / 6);
			
			if (CurrentBar < n)
				return;			
			
			n3 = (MAX(smooth, n)[0] - MIN(smooth, n)[0]) / n;
			hh = smooth[0];
			ll = smooth[0];
			
			for (int index = 0; index <= (n / 2 - 1); index++) 
			{
				if (smooth[index] > hh)
					hh = smooth[index];
				if (smooth[index] < ll)
					ll = smooth[index];
			}
						
			n1 = (hh - ll) / (n / 2);
			hh = smooth[n / 2];
			ll = smooth[n / 2];
			
			for (int index = (n / 2); index <= (n - 1); index++)
			{
				if (smooth[index] > hh)
					hh = smooth[index];
				if (smooth[index] < ll)
					ll = smooth[index];
			}
						
			n2 = (hh - ll) / (n / 2);
			
			if (n1 > 0 && n2 > 0 && n3 > 0)
				ratio.Set(0.5 * ((Math.Log10(n1 + n2) - Math.Log10(n3)) / Math.Log10(2) + Dimension_Plot[1]));
			
            Dimension_Plot.Set(SMA(ratio, 20)[0]);
        }

        #region Properties
        [Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries Dimension_Plot
        {
            get { return Values[0]; }
        }

        [Description("Number of bars to average. Must be an even number.")]
        [Category("Parameters")]
        public int N
        {
            get { return n; }
            set { n = Math.Max(2, value); }
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
        private FractalDimensionIndicator[] cacheFractalDimensionIndicator = null;

        private static FractalDimensionIndicator checkFractalDimensionIndicator = new FractalDimensionIndicator();

        /// <summary>
        /// This is the Fractal Dimension Indicator as described in the May 2010 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        public FractalDimensionIndicator FractalDimensionIndicator(int n)
        {
            return FractalDimensionIndicator(Input, n);
        }

        /// <summary>
        /// This is the Fractal Dimension Indicator as described in the May 2010 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        public FractalDimensionIndicator FractalDimensionIndicator(Data.IDataSeries input, int n)
        {
            checkFractalDimensionIndicator.N = n;
            n = checkFractalDimensionIndicator.N;

            if (cacheFractalDimensionIndicator != null)
                for (int idx = 0; idx < cacheFractalDimensionIndicator.Length; idx++)
                    if (cacheFractalDimensionIndicator[idx].N == n && cacheFractalDimensionIndicator[idx].EqualsInput(input))
                        return cacheFractalDimensionIndicator[idx];

            FractalDimensionIndicator indicator = new FractalDimensionIndicator();
            indicator.BarsRequired = BarsRequired;
            indicator.CalculateOnBarClose = CalculateOnBarClose;
            indicator.Input = input;
            indicator.N = n;
            indicator.SetUp();

            FractalDimensionIndicator[] tmp = new FractalDimensionIndicator[cacheFractalDimensionIndicator == null ? 1 : cacheFractalDimensionIndicator.Length + 1];
            if (cacheFractalDimensionIndicator != null)
                cacheFractalDimensionIndicator.CopyTo(tmp, 0);
            tmp[tmp.Length - 1] = indicator;
            cacheFractalDimensionIndicator = tmp;
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
        /// This is the Fractal Dimension Indicator as described in the May 2010 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.FractalDimensionIndicator FractalDimensionIndicator(int n)
        {
            return _indicator.FractalDimensionIndicator(Input, n);
        }

        /// <summary>
        /// This is the Fractal Dimension Indicator as described in the May 2010 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        public Indicator.FractalDimensionIndicator FractalDimensionIndicator(Data.IDataSeries input, int n)
        {
            return _indicator.FractalDimensionIndicator(input, n);
        }

    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// This is the Fractal Dimension Indicator as described in the May 2010 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.FractalDimensionIndicator FractalDimensionIndicator(int n)
        {
            return _indicator.FractalDimensionIndicator(Input, n);
        }

        /// <summary>
        /// This is the Fractal Dimension Indicator as described in the May 2010 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        public Indicator.FractalDimensionIndicator FractalDimensionIndicator(Data.IDataSeries input, int n)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.FractalDimensionIndicator(input, n);
        }

    }
}
#endregion
