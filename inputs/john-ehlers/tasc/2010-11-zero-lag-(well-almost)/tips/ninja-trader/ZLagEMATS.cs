#region Using declarations
using System;
using System.ComponentModel;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.Indicator;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Strategy;
#endregion

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    /// <summary>
    /// S&C magainze November 2010. Zero Lag (Well, almost)
    /// </summary>
    [Description("S&C magainze November 2010. Zero Lag (Well, almost)")]
    public class ZLagEMATS : Strategy
    {
        #region Variables
        // Wizard generated variables
        private double length = 20; // Default setting for Length
        private double gainLimit = 50; // Default setting for GainLimit
        private double thresh = 1; // Default setting for Thresh
        // User defined variables (add any user defined variables below)
        #endregion

        /// <summary>
        /// This method is used to configure the strategy and is called once before any strategy method is called.
        /// </summary>
        protected override void Initialize()
        {
            CalculateOnBarClose = true;
        }

        /// <summary>
        /// Called on each bar update event (incoming tick)
        /// </summary>
        protected override void OnBarUpdate()
        {
			if (CrossAbove(ZLagEMA(Length, GainLimit).EC, ZLagEMA(Length, GainLimit).EMA, 1) && 100 * ZLagEMA(Length, GainLimit).LeastError / Close[0] > Thresh)
				EnterLong();
			
			if (CrossBelow(ZLagEMA(Length, GainLimit).EC, ZLagEMA(Length, GainLimit).EMA, 1) && 100 * ZLagEMA(Length, GainLimit).LeastError / Close[0] > Thresh)
				EnterShort();			
        }

        #region Properties
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

        [Description("")]
        [Category("Parameters")]
        public double Thresh
        {
            get { return thresh; }
            set { thresh = Math.Max(0, value); }
        }
        #endregion
    }
}
