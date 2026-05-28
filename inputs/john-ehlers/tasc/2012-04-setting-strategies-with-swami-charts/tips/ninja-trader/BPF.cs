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
	/// Enter the description of your new custom indicator here
	/// </summary>
	[Description("Enter the description of your new custom indicator here")]
	public class BPF : Indicator
	{
		private const double rtd = Math.PI / 180;
		private DataSeries den;
		private DataSeries nom;
		private DataSeries filter;
		private int period = 20;

		/// <summary>
		/// This method is used to configure the indicator and is called once before any bar data is loaded.
		/// </summary>
		protected override void Initialize()
		{
			Add(new Plot(Color.FromKnownColor(KnownColor.Orange), PlotStyle.Line, "Filter"));
			Add(new Plot(Color.FromKnownColor(KnownColor.Orange), PlotStyle.Line, "Filter1"));
			Overlay = false;
			den = new DataSeries(this);
			nom = new DataSeries(this);
			filter = new DataSeries(this);
		}

		/// <summary>
		/// Called on each bar update event (incoming tick)
		/// </summary>
		protected override void OnBarUpdate()
		{
			if (CurrentBar < 2)
			{
				Filter.Set(0);
				return;
			}
			const double delta2 = 0.1;
			double beta2 = Math.Cos(rtd * 360 / period);
			double gamma2 = 1 / Math.Cos(rtd * 720 * delta2 / period);
			double alpha2 = gamma2 - Math.Sqrt(gamma2 * gamma2 - 1);

			filter.Set(0.5 * (1 - alpha2) * (Input[0] - Input[2]) + beta2 * (1 + alpha2) * filter[1] - alpha2 * filter[2]);
			nom.Set(filter[0] - MIN(filter, period)[0]);
			den.Set(MAX(filter, period)[0] - MIN(filter, period)[0]);

			if (den[0].Compare(0, 0.000000000001) == 0)
				Filter.Set(CurrentBar == 0 ? 50 : filter[1]);
			else
				Filter.Set(Math.Min(1, Math.Max(0, nom[0] / den[0])));
		}

		#region Properties
		[Browsable(false)]
		[XmlIgnore]
		public DataSeries Filter
		{
			get { return Values[0]; }
		}

		[Description("")]
		[GridCategory("Parameters")]
		public int Period
		{
			get { return period; }
			set { period = Math.Max(1, value); }
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
        private BPF[] cacheBPF = null;

        private static BPF checkBPF = new BPF();

        /// <summary>
        /// Enter the description of your new custom indicator here
        /// </summary>
        /// <returns></returns>
        public BPF BPF(int period)
        {
            return BPF(Input, period);
        }

        /// <summary>
        /// Enter the description of your new custom indicator here
        /// </summary>
        /// <returns></returns>
        public BPF BPF(Data.IDataSeries input, int period)
        {
            if (cacheBPF != null)
                for (int idx = 0; idx < cacheBPF.Length; idx++)
                    if (cacheBPF[idx].Period == period && cacheBPF[idx].EqualsInput(input))
                        return cacheBPF[idx];

            lock (checkBPF)
            {
                checkBPF.Period = period;
                period = checkBPF.Period;

                if (cacheBPF != null)
                    for (int idx = 0; idx < cacheBPF.Length; idx++)
                        if (cacheBPF[idx].Period == period && cacheBPF[idx].EqualsInput(input))
                            return cacheBPF[idx];

                BPF indicator = new BPF();
                indicator.BarsRequired = BarsRequired;
                indicator.CalculateOnBarClose = CalculateOnBarClose;
#if NT7
                indicator.ForceMaximumBarsLookBack256 = ForceMaximumBarsLookBack256;
                indicator.MaximumBarsLookBack = MaximumBarsLookBack;
#endif
                indicator.Input = input;
                indicator.Period = period;
                Indicators.Add(indicator);
                indicator.SetUp();

                BPF[] tmp = new BPF[cacheBPF == null ? 1 : cacheBPF.Length + 1];
                if (cacheBPF != null)
                    cacheBPF.CopyTo(tmp, 0);
                tmp[tmp.Length - 1] = indicator;
                cacheBPF = tmp;
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
        /// Enter the description of your new custom indicator here
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.BPF BPF(int period)
        {
            return _indicator.BPF(Input, period);
        }

        /// <summary>
        /// Enter the description of your new custom indicator here
        /// </summary>
        /// <returns></returns>
        public Indicator.BPF BPF(Data.IDataSeries input, int period)
        {
            return _indicator.BPF(input, period);
        }
    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// Enter the description of your new custom indicator here
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.BPF BPF(int period)
        {
            return _indicator.BPF(Input, period);
        }

        /// <summary>
        /// Enter the description of your new custom indicator here
        /// </summary>
        /// <returns></returns>
        public Indicator.BPF BPF(Data.IDataSeries input, int period)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.BPF(input, period);
        }
    }
}
#endregion
