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
    /// The Empirical Mode Decomposition as described in the March 2010 issue of Stocks & Commodities.
    /// </summary>
    [Description("The Empirical Mode Decomposition as described in the March 2010 issue of Stocks & Commodities.")]
    public class EmpiricalModeDecomposition : Indicator
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
				beta = Math.Cos(2 * Math.PI / Period);
				gamma = 1 / Math.Cos(4 * Math.PI * Delta / Period);
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

        [Description("")]
        [Category("Parameters")]
        public int Period
        {
            get { return period; }
            set { period = Math.Max(1, value); }
        }

        [Description("")]
        [Category("Parameters")]
        public double Delta
        {
            get { return delta; }
            set { delta = Math.Max(0.000, value); }
        }

        [Description("")]
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
        private EmpiricalModeDecomposition[] cacheEmpiricalModeDecomposition = null;

        private static EmpiricalModeDecomposition checkEmpiricalModeDecomposition = new EmpiricalModeDecomposition();

        /// <summary>
        /// The Empirical Mode Decomposition as described in the March 2010 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        public EmpiricalModeDecomposition EmpiricalModeDecomposition(double delta, double fraction, int period)
        {
            return EmpiricalModeDecomposition(Input, delta, fraction, period);
        }

        /// <summary>
        /// The Empirical Mode Decomposition as described in the March 2010 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        public EmpiricalModeDecomposition EmpiricalModeDecomposition(Data.IDataSeries input, double delta, double fraction, int period)
        {
            checkEmpiricalModeDecomposition.Delta = delta;
            delta = checkEmpiricalModeDecomposition.Delta;
            checkEmpiricalModeDecomposition.Fraction = fraction;
            fraction = checkEmpiricalModeDecomposition.Fraction;
            checkEmpiricalModeDecomposition.Period = period;
            period = checkEmpiricalModeDecomposition.Period;

            if (cacheEmpiricalModeDecomposition != null)
                for (int idx = 0; idx < cacheEmpiricalModeDecomposition.Length; idx++)
                    if (Math.Abs(cacheEmpiricalModeDecomposition[idx].Delta - delta) <= double.Epsilon && Math.Abs(cacheEmpiricalModeDecomposition[idx].Fraction - fraction) <= double.Epsilon && cacheEmpiricalModeDecomposition[idx].Period == period && cacheEmpiricalModeDecomposition[idx].EqualsInput(input))
                        return cacheEmpiricalModeDecomposition[idx];

            EmpiricalModeDecomposition indicator = new EmpiricalModeDecomposition();
            indicator.BarsRequired = BarsRequired;
            indicator.CalculateOnBarClose = CalculateOnBarClose;
            indicator.Input = input;
            indicator.Delta = delta;
            indicator.Fraction = fraction;
            indicator.Period = period;
            indicator.SetUp();

            EmpiricalModeDecomposition[] tmp = new EmpiricalModeDecomposition[cacheEmpiricalModeDecomposition == null ? 1 : cacheEmpiricalModeDecomposition.Length + 1];
            if (cacheEmpiricalModeDecomposition != null)
                cacheEmpiricalModeDecomposition.CopyTo(tmp, 0);
            tmp[tmp.Length - 1] = indicator;
            cacheEmpiricalModeDecomposition = tmp;
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
        /// The Empirical Mode Decomposition as described in the March 2010 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.EmpiricalModeDecomposition EmpiricalModeDecomposition(double delta, double fraction, int period)
        {
            return _indicator.EmpiricalModeDecomposition(Input, delta, fraction, period);
        }

        /// <summary>
        /// The Empirical Mode Decomposition as described in the March 2010 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        public Indicator.EmpiricalModeDecomposition EmpiricalModeDecomposition(Data.IDataSeries input, double delta, double fraction, int period)
        {
            return _indicator.EmpiricalModeDecomposition(input, delta, fraction, period);
        }

    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// The Empirical Mode Decomposition as described in the March 2010 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.EmpiricalModeDecomposition EmpiricalModeDecomposition(double delta, double fraction, int period)
        {
            return _indicator.EmpiricalModeDecomposition(Input, delta, fraction, period);
        }

        /// <summary>
        /// The Empirical Mode Decomposition as described in the March 2010 issue of Stocks & Commodities.
        /// </summary>
        /// <returns></returns>
        public Indicator.EmpiricalModeDecomposition EmpiricalModeDecomposition(Data.IDataSeries input, double delta, double fraction, int period)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.EmpiricalModeDecomposition(input, delta, fraction, period);
        }

    }
}
#endregion
