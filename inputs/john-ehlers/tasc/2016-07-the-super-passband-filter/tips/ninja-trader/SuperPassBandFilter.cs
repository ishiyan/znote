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
    /// 
    /// </summary>
    [Description("")]
    public class SuperPassBandFilter : Indicator
    {
        #region Variables
        private double a1;
		private double a2;
		private double RMS;
		private int count = 50;
		private int period1 = 40;
		private int period2 = 60;
        #endregion

        /// <summary>
        /// This method is used to configure the indicator and is called once before any bar data is loaded.
        /// </summary>
        protected override void Initialize()
        {
            Add(new Plot(Color.FromKnownColor(KnownColor.Orange), PlotStyle.Line, "PB"));
			Add(new Plot(Color.FromKnownColor(KnownColor.Yellow), PlotStyle.Line, "RMS"));
			Add(new Plot(Color.FromKnownColor(KnownColor.Yellow), PlotStyle.Line, "-RMS"));
			Add(new Line(Color.Blue, 0, "zero"));
            Overlay				= false;
        }
		
        protected override void OnBarUpdate()
        {
            a1 = 5 / Convert.ToDouble(period1);
			a2 = 5 / Convert.ToDouble(period2);
			
			if (CurrentBar <= 1)
			{
				PB[0] = Close[0];
				return;
			}

			
			PB[0] = (a1 - a2) * Close[0]
				+ (a2*(1 - a1) - a1*(1-a2)) * Close[1]
				+ ((1 - a1) + (1 - a2)) * PB[1] - (1 - a1) * (1 - a2) * PB[2];

			RMS = 0;
			
			if (PB.Count < count) return;
			for (int i = count-1; i >= 0; i--)
			{
				RMS = RMS + PB[i]*PB[i];
			}

			RMS = Math.Sqrt(RMS/50);
			
			RMSpos[0] = RMS;
			RMSneg[0] = -RMS;
        }

        #region Properties
        [Description("")]
        [GridCategory("Parameters")]
        public int Period1
        {
            get { return period1; }
            set { period1 = Math.Max(1, value); }
        }
		
		[Description("")]
        [GridCategory("Parameters")]
        public int Period2
        {
            get { return period2; }
            set { period2 = Math.Max(1, value); }
        }
		
		[Description("")]
        [GridCategory("Parameters")]
        public int Count
        {
            get { return count; }
            set { count = Math.Max(1, value); }
        }
		
		[Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries PB
        {
            get { return Values[0]; }
        }
		
		[Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries RMSpos
        {
            get { return Values[1]; }
        }
		
		[Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries RMSneg
        {
            get { return Values[2]; }
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
        private SuperPassBandFilter[] cacheSuperPassBandFilter = null;

        private static SuperPassBandFilter checkSuperPassBandFilter = new SuperPassBandFilter();

        /// <summary>
        /// 
        /// </summary>
        /// <returns></returns>
        public SuperPassBandFilter SuperPassBandFilter(int count, int period1, int period2)
        {
            return SuperPassBandFilter(Input, count, period1, period2);
        }

        /// <summary>
        /// 
        /// </summary>
        /// <returns></returns>
        public SuperPassBandFilter SuperPassBandFilter(Data.IDataSeries input, int count, int period1, int period2)
        {
            if (cacheSuperPassBandFilter != null)
                for (int idx = 0; idx < cacheSuperPassBandFilter.Length; idx++)
                    if (cacheSuperPassBandFilter[idx].Count == count && cacheSuperPassBandFilter[idx].Period1 == period1 && cacheSuperPassBandFilter[idx].Period2 == period2 && cacheSuperPassBandFilter[idx].EqualsInput(input))
                        return cacheSuperPassBandFilter[idx];

            lock (checkSuperPassBandFilter)
            {
                checkSuperPassBandFilter.Count = count;
                count = checkSuperPassBandFilter.Count;
                checkSuperPassBandFilter.Period1 = period1;
                period1 = checkSuperPassBandFilter.Period1;
                checkSuperPassBandFilter.Period2 = period2;
                period2 = checkSuperPassBandFilter.Period2;

                if (cacheSuperPassBandFilter != null)
                    for (int idx = 0; idx < cacheSuperPassBandFilter.Length; idx++)
                        if (cacheSuperPassBandFilter[idx].Count == count && cacheSuperPassBandFilter[idx].Period1 == period1 && cacheSuperPassBandFilter[idx].Period2 == period2 && cacheSuperPassBandFilter[idx].EqualsInput(input))
                            return cacheSuperPassBandFilter[idx];

                SuperPassBandFilter indicator = new SuperPassBandFilter();
                indicator.BarsRequired = BarsRequired;
                indicator.CalculateOnBarClose = CalculateOnBarClose;
#if NT7
                indicator.ForceMaximumBarsLookBack256 = ForceMaximumBarsLookBack256;
                indicator.MaximumBarsLookBack = MaximumBarsLookBack;
#endif
                indicator.Input = input;
                indicator.Count = count;
                indicator.Period1 = period1;
                indicator.Period2 = period2;
                Indicators.Add(indicator);
                indicator.SetUp();

                SuperPassBandFilter[] tmp = new SuperPassBandFilter[cacheSuperPassBandFilter == null ? 1 : cacheSuperPassBandFilter.Length + 1];
                if (cacheSuperPassBandFilter != null)
                    cacheSuperPassBandFilter.CopyTo(tmp, 0);
                tmp[tmp.Length - 1] = indicator;
                cacheSuperPassBandFilter = tmp;
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
        /// 
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.SuperPassBandFilter SuperPassBandFilter(int count, int period1, int period2)
        {
            return _indicator.SuperPassBandFilter(Input, count, period1, period2);
        }

        /// <summary>
        /// 
        /// </summary>
        /// <returns></returns>
        public Indicator.SuperPassBandFilter SuperPassBandFilter(Data.IDataSeries input, int count, int period1, int period2)
        {
            return _indicator.SuperPassBandFilter(input, count, period1, period2);
        }
    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// 
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.SuperPassBandFilter SuperPassBandFilter(int count, int period1, int period2)
        {
            return _indicator.SuperPassBandFilter(Input, count, period1, period2);
        }

        /// <summary>
        /// 
        /// </summary>
        /// <returns></returns>
        public Indicator.SuperPassBandFilter SuperPassBandFilter(Data.IDataSeries input, int count, int period1, int period2)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.SuperPassBandFilter(input, count, period1, period2);
        }
    }
}
#endregion
