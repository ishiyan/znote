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
    /// S&C magainze November 2010. Zero Lag (Well, almost)
    /// </summary>
    [Description("S&C magainze November 2010. Zero Lag (Well, almost)")]
    public class ZLagEMA : Indicator
    {
       #region Variables
        // Wizard generated variables
            private double length = 20; // Default setting for Length
            private double gainLimit = 50; // Default setting for GainLimit
        // User defined variables (add any user defined variables below)
			private double 		alpha;
			private double 		gain;
			private double 		bestGain;
			private double 		error;
			private double 		leastError;
			private double 		currEC;
			private	double		prevEC;
        #endregion

        /// <summary>
        /// This method is used to configure the indicator and is called once before any bar data is loaded.
        /// </summary>
        protected override void Initialize()
        {
            Add(new Plot(Color.FromKnownColor(KnownColor.Blue), PlotStyle.Line, "EC"));
			Add(new Plot(Color.FromKnownColor(KnownColor.Red), PlotStyle.Line, "EMA"));
            Overlay				= true;
        }

        /// <summary>
        /// Called on each bar update event (incoming tick)
        /// </summary>
        protected override void OnBarUpdate()
        {           
			if (CurrentBar < 1)
				return;
			
			alpha = 2 / (Length + 1);
			EMA.Set(alpha * Close[0] + (1 - alpha) * EMA[1]);
			leastError = 1000000;
			
			for (double x = GainLimit * -1; x <= GainLimit; x++)
			{	
				gain = x / 10;
				currEC = alpha * (EMA[0] + gain * (Close[0] - prevEC)) + (1 - alpha) * prevEC;
				error = Close[0] - currEC;
				
				if (Math.Abs (error) < leastError)
				{
					leastError  = Math.Abs (error);
					bestGain 	= gain;		
				}
			}
			prevEC = currEC;
			EC.Set(currEC);
			
		}

        #region Properties
        [Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries EC
        {
            get { return Values[0]; }
        }
		
		[Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries EMA
        {
            get { return Values[1]; }
        }

        [Description("")]
        [Category("Parameters")]
        public double Length
        {
            get { return length; }
            set { length = Math.Max(1, value); }
        }

        [Description("")]
        [Category("Parameters")]
        public double GainLimit
        {
            get { return gainLimit; }
            set { gainLimit = Math.Max(1, value); }
        }
		
		[Browsable(false)]
        [XmlIgnore()]
        public double LeastError
        {
			
            get { Update(); return leastError; }
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
        private ZLagEMA[] cacheZLagEMA = null;

        private static ZLagEMA checkZLagEMA = new ZLagEMA();

        /// <summary>
        /// S&C magainze November 2010. Zero Lag (Well, almost)
        /// </summary>
        /// <returns></returns>
        public ZLagEMA ZLagEMA(double gainLimit, double length)
        {
            return ZLagEMA(Input, gainLimit, length);
        }

        /// <summary>
        /// S&C magainze November 2010. Zero Lag (Well, almost)
        /// </summary>
        /// <returns></returns>
        public ZLagEMA ZLagEMA(Data.IDataSeries input, double gainLimit, double length)
        {
            checkZLagEMA.GainLimit = gainLimit;
            gainLimit = checkZLagEMA.GainLimit;
            checkZLagEMA.Length = length;
            length = checkZLagEMA.Length;

            if (cacheZLagEMA != null)
                for (int idx = 0; idx < cacheZLagEMA.Length; idx++)
                    if (Math.Abs(cacheZLagEMA[idx].GainLimit - gainLimit) <= double.Epsilon && Math.Abs(cacheZLagEMA[idx].Length - length) <= double.Epsilon && cacheZLagEMA[idx].EqualsInput(input))
                        return cacheZLagEMA[idx];

            ZLagEMA indicator = new ZLagEMA();
            indicator.BarsRequired = BarsRequired;
            indicator.CalculateOnBarClose = CalculateOnBarClose;
            indicator.Input = input;
            indicator.GainLimit = gainLimit;
            indicator.Length = length;
            indicator.SetUp();

            ZLagEMA[] tmp = new ZLagEMA[cacheZLagEMA == null ? 1 : cacheZLagEMA.Length + 1];
            if (cacheZLagEMA != null)
                cacheZLagEMA.CopyTo(tmp, 0);
            tmp[tmp.Length - 1] = indicator;
            cacheZLagEMA = tmp;
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
        /// S&C magainze November 2010. Zero Lag (Well, almost)
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.ZLagEMA ZLagEMA(double gainLimit, double length)
        {
            return _indicator.ZLagEMA(Input, gainLimit, length);
        }

        /// <summary>
        /// S&C magainze November 2010. Zero Lag (Well, almost)
        /// </summary>
        /// <returns></returns>
        public Indicator.ZLagEMA ZLagEMA(Data.IDataSeries input, double gainLimit, double length)
        {
            return _indicator.ZLagEMA(input, gainLimit, length);
        }

    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// S&C magainze November 2010. Zero Lag (Well, almost)
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.ZLagEMA ZLagEMA(double gainLimit, double length)
        {
            return _indicator.ZLagEMA(Input, gainLimit, length);
        }

        /// <summary>
        /// S&C magainze November 2010. Zero Lag (Well, almost)
        /// </summary>
        /// <returns></returns>
        public Indicator.ZLagEMA ZLagEMA(Data.IDataSeries input, double gainLimit, double length)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.ZLagEMA(input, gainLimit, length);
        }

    }
}
#endregion
