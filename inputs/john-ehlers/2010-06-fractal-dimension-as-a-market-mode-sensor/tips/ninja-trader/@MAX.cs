// 
// Copyright (C) 2006, NinjaTrader LLC <www.ninjatrader.com>.
// NinjaTrader reserves the right to modify or overwrite this NinjaScript component with each release.
//

#region Using declarations
using System;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.ComponentModel;
using System.Xml.Serialization;
using NinjaTrader.Data;
using NinjaTrader.Gui.Chart;
#endregion

// This namespace holds all indicators and is required. Do not change it.
namespace NinjaTrader.Indicator
{
	/// <summary>
	/// The Maximum shows the maximum of the last n bars.
	/// </summary>
	[Description("The Maximum shows the maximum of the last n bars.")]
	public class MAX : Indicator
	{
		#region Variables
		private int		period	= 14;
		#endregion

		/// <summary>
		/// This method is used to configure the indicator and is called once before any bar data is loaded.
		/// </summary>
		protected override void Initialize()
		{
			Add(new Plot(Color.Green, "MAX"));

			Overlay				= true;
			PriceTypeSupported	= true;
		}
		
		/// <summary>
		/// Called on each bar update event (incoming tick)
		/// </summary>
		protected override void OnBarUpdate()
		{
			double val = double.MinValue;
			for (int barsBack = Math.Min(CurrentBar, Period - 1); barsBack >= 0; barsBack--)
				val = Math.Max(val, Input[barsBack]);
			Value.Set(val);
		}

		#region Properties
		/// <summary>
		/// </summary>
		[Description("Numbers of bars used for calculations")]
		[Category("Parameters")]
		public int Period
		{
			get { return period; }
			set	{ period = Math.Max(1, value); }
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
        private MAX[] cacheMAX = null;
        private static MAX checkMAX = new MAX();

        /// <summary>
        /// The Maximum shows the maximum of the last n bars.
        /// </summary>
        /// <returns></returns>
        public MAX MAX(int period)
        {
            return MAX(Input, period);
        }

        /// <summary>
        /// The Maximum shows the maximum of the last n bars.
        /// </summary>
        /// <returns></returns>
        public MAX MAX(Data.IDataSeries input, int period)
        {
            checkMAX.Period = period;
            period = checkMAX.Period;

            if (cacheMAX != null)
                for (int idx = 0; idx < cacheMAX.Length; idx++)
                    if (cacheMAX[idx].Period == period && cacheMAX[idx].EqualsInput(input))
                        return cacheMAX[idx];

            MAX indicator = new MAX();
			indicator.BarsRequired = BarsRequired;
            indicator.CalculateOnBarClose = CalculateOnBarClose;
            indicator.Input = input;
            indicator.Period = period;
            indicator.SetUp();

            MAX[] tmp = new MAX[cacheMAX == null ? 1 : cacheMAX.Length + 1];
            if (cacheMAX != null)
                cacheMAX.CopyTo(tmp, 0);
            tmp[tmp.Length - 1] = indicator;
            cacheMAX = tmp;
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
        /// The Maximum shows the maximum of the last n bars.
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.MAX MAX(int period)
        {
            return _indicator.MAX(Input, period);
        }

        /// <summary>
        /// The Maximum shows the maximum of the last n bars.
        /// </summary>
        /// <returns></returns>
        public Indicator.MAX MAX(Data.IDataSeries input, int period)
        {
            return _indicator.MAX(input, period);
        }
    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// The Maximum shows the maximum of the last n bars.
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.MAX MAX(int period)
        {
            return _indicator.MAX(Input, period);
        }

        /// <summary>
        /// The Maximum shows the maximum of the last n bars.
        /// </summary>
        /// <returns></returns>
        public Indicator.MAX MAX(Data.IDataSeries input, int period)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.MAX(input, period);
        }
    }
}
#endregion
