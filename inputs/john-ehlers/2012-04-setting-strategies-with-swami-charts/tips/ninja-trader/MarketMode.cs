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
    /// The Empirical Mode Decomposition as described in the April 2012 issue of Stocks & Commodities.
    /// </summary>
    [Description("The Empirical Mode Decomposition as described in the April 2012 issue of Stocks & Commodities.")]
    public class MarketMode : Indicator
    {
        #region Variables
        private int period = 20; // Default setting for Period
        private double delta = 0.5; // Default setting for Delta
        private double fraction = 0.1; // Default setting for Fraction
		private double alpha, beta, gamma, avgPeak, avgValley, mean;
		private DataSeries BP, Peak, Valley;
        #endregion

        /// <summary>
        /// This method is used to configure the indicator and is called once before any bar data is loaded.
        /// </summary>
        protected override void Initialize()
        {
			Add(new Plot(new Pen(Color.RoyalBlue, 2), PlotStyle.Line, "UpperBand"));
			Add(new Plot(new Pen(Color.RoyalBlue, 2), PlotStyle.Line, "LowerBand"));
			Add(new Plot(new Pen(Color.Red, 2), PlotStyle.Line, "MainPlot"));
            CalculateOnBarClose	= true;
            Overlay				= false;
            PriceTypeSupported	= false;
			BP = new DataSeries(this);
			Peak = new DataSeries(this);
			Valley = new DataSeries(this);
        }

        /// <summary>
        /// Called on each bar update event (incoming tick)
        /// </summary>
        protected override void OnBarUpdate()
        {
			if (CurrentBar == 0)
			{
				beta = Math.Cos(360 / Period);
				gamma = 1 / Math.Cos(720 * Delta / Period);
				alpha = gamma - Math.Sqrt(Math.Pow(gamma, 2) - 1);
			}
			
			if (CurrentBar < 51)
			{
				BP.Set(0);
				Peak.Set(0);
				Valley.Set(0);
				return;
			}

            BP.Set(0.5 * (1 - alpha) * (((High[0] + Low[0]) / 2) - ((High[2] + Low[2]) / 2)) + beta * (1 + alpha) * BP[1] - alpha * BP[2]);
			
			mean = SMA(BP, 2*Period)[0];
			
			Peak.Set(Peak[1]);
			Valley.Set(Valley[1]);
			
			if (BP[1] > BP[0] && BP[1] > BP[2])
				Peak.Set(BP[1]);
			if (BP[1] < BP[0] && BP[1] < BP[2])
				Valley.Set(BP[1]);
			
			avgPeak = SMA(Peak, 50)[0];
			avgValley = SMA(Valley, 50)[0];
			
            UpperBand.Set(avgPeak * Fraction);
            LowerBand.Set(avgValley * Fraction);
            MainPlot.Set(mean);
        }

        #region Properties
        [Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries UpperBand
        {
            get { return Values[0]; }
        }

        [Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries LowerBand
        {
            get { return Values[1]; }
        }

        [Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries MainPlot
        {
            get { return Values[2]; }
        }

        [Description("Period")]
        [Category("Parameters")]
        public int Period
        {
            get { return period; }
            set { period = Math.Max(1, value); }
        }

        [Description("Delta")]
        [Category("Parameters")]
        public double Delta
        {
            get { return delta; }
            set { delta = Math.Max(0.000, value); }
        }

        [Description("Fraction")]
        [Category("Parameters")]
        public double Fraction
        {
            get { return fraction; }
            set { fraction = Math.Max(0, value); }
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
        private MarketMode[] cacheMarketMode = null;

        private static MarketMode checkMarketMode = new MarketMode();

        /// <summary>
        /// The Empirical Mode Decomposition as described in the April 2012 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        public MarketMode MarketMode(double delta, double fraction, int period)
        {
            return MarketMode(Input, delta, fraction, period);
        }

        /// <summary>
        /// The Empirical Mode Decomposition as described in the April 2012 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        public MarketMode MarketMode(Data.IDataSeries input, double delta, double fraction, int period)
        {
            if (cacheMarketMode != null)
                for (int idx = 0; idx < cacheMarketMode.Length; idx++)
                    if (Math.Abs(cacheMarketMode[idx].Delta - delta) <= double.Epsilon && Math.Abs(cacheMarketMode[idx].Fraction - fraction) <= double.Epsilon && cacheMarketMode[idx].Period == period && cacheMarketMode[idx].EqualsInput(input))
                        return cacheMarketMode[idx];

            lock (checkMarketMode)
            {
                checkMarketMode.Delta = delta;
                delta = checkMarketMode.Delta;
                checkMarketMode.Fraction = fraction;
                fraction = checkMarketMode.Fraction;
                checkMarketMode.Period = period;
                period = checkMarketMode.Period;

                if (cacheMarketMode != null)
                    for (int idx = 0; idx < cacheMarketMode.Length; idx++)
                        if (Math.Abs(cacheMarketMode[idx].Delta - delta) <= double.Epsilon && Math.Abs(cacheMarketMode[idx].Fraction - fraction) <= double.Epsilon && cacheMarketMode[idx].Period == period && cacheMarketMode[idx].EqualsInput(input))
                            return cacheMarketMode[idx];

                MarketMode indicator = new MarketMode();
                indicator.BarsRequired = BarsRequired;
                indicator.CalculateOnBarClose = CalculateOnBarClose;
#if NT7
                indicator.ForceMaximumBarsLookBack256 = ForceMaximumBarsLookBack256;
                indicator.MaximumBarsLookBack = MaximumBarsLookBack;
#endif
                indicator.Input = input;
                indicator.Delta = delta;
                indicator.Fraction = fraction;
                indicator.Period = period;
                Indicators.Add(indicator);
                indicator.SetUp();

                MarketMode[] tmp = new MarketMode[cacheMarketMode == null ? 1 : cacheMarketMode.Length + 1];
                if (cacheMarketMode != null)
                    cacheMarketMode.CopyTo(tmp, 0);
                tmp[tmp.Length - 1] = indicator;
                cacheMarketMode = tmp;
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
        /// The Empirical Mode Decomposition as described in the April 2012 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.MarketMode MarketMode(double delta, double fraction, int period)
        {
            return _indicator.MarketMode(Input, delta, fraction, period);
        }

        /// <summary>
        /// The Empirical Mode Decomposition as described in the April 2012 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        public Indicator.MarketMode MarketMode(Data.IDataSeries input, double delta, double fraction, int period)
        {
            return _indicator.MarketMode(input, delta, fraction, period);
        }
    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// The Empirical Mode Decomposition as described in the April 2012 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.MarketMode MarketMode(double delta, double fraction, int period)
        {
            return _indicator.MarketMode(Input, delta, fraction, period);
        }

        /// <summary>
        /// The Empirical Mode Decomposition as described in the April 2012 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        public Indicator.MarketMode MarketMode(Data.IDataSeries input, double delta, double fraction, int period)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.MarketMode(input, delta, fraction, period);
        }
    }
}
#endregion
