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

namespace NinjaTrader.Indicator
{
    [Description("John F. Ehlers : 'Early Trend Detection, The Quotient Transform' - TASC August 2014")]
    public class QuotientTransform : Indicator
    {
        #region Variables
		
            private double alpha1;
			private double a1;
			private double b1;
			private double c1;
			private double c2;
			private double c3;
			private double x;
			private double quotientFastLong;
			private double quotientSlowLong;
			private double quotientFastShort;
			private double quotientSlowShort;
			private double kFastLong  = 0.40;
			private double kSlowLong  = 0.90;
			private double kFastShort = - 0.40;
			private double kSlowShort = - 0.90;
			private int lPPeriod = 20;
			private DataSeries HP;
			private DataSeries Filt;
			private DataSeries Peak;		
			       	
        #endregion
		
        protected override void Initialize()
        {
			HP     = new DataSeries(this);
			Filt   = new DataSeries(this);
			Peak   = new DataSeries(this);
						
            Add(new Plot(Color.FromKnownColor(KnownColor.GreenYellow), PlotStyle.Line, "QTFastLong"));
			Add(new Plot(Color.FromKnownColor(KnownColor.Green), PlotStyle.Line, "QTSlowLong"));
			Add(new Plot(Color.FromKnownColor(KnownColor.Tomato), PlotStyle.Line, "QTFastShort"));
			Add(new Plot(Color.FromKnownColor(KnownColor.Red), PlotStyle.Line, "QTSlowShort"));
            Add(new Line(Color.DarkBlue, 0.0, "Zero"));
            
			for (int index = 0; index < 4; index++) 
			{
				Plots[index].Pen.Width = 3;
			}
			
			Lines[0].Pen.Width = 2;
			Overlay = false;
        }
		
		protected override void OnStartUp()
		{
			alpha1 = ((Math.Cos(((.707 * 360 / 100) * Math.PI) / 180)) + (Math.Sin(((.707 * 360 / 100) * Math.PI) / 180)) - 1) / (Math.Cos(((.707 * 360 / 100) * Math.PI) / 180));
			a1 = Math.Exp(-1.414 * 3.14159 / LPPeriod);
			b1 = 2 * a1 * (Math.Cos(((1.414 * 180 / LPPeriod) * Math.PI) / 180));
			c2 = b1;
			c3 = (a1 * -1) * a1;
			c1 = 1 - c2 - c3;
		}
     
        protected override void OnBarUpdate()
        {
			if (CurrentBar < LPPeriod)
			{
				HP.Set(0);
				Filt.Set(0);
				Peak.Set(0);
				return;
			}				
			
            HP.Set((1 - alpha1 / 2) * (1 - alpha1 / 2) * (Input[0] - 2 * Input[1] + Input[2]) + 2 * (1 - alpha1) * HP[1] - (1 - alpha1) * (1 - alpha1) * HP[2]);
			Filt.Set(c1 * (HP[0] + HP[1]) / 2 + c2 * Filt[1] + c3 * Filt[2]);
			
			Peak.Set(Peak[1] * 0.991);
			
			if (Math.Abs(Filt[0]) > Peak[0])
				Peak.Set(Math.Abs(Filt[0]));
			
			if (Peak[0] < 0.0 || Peak[0] > 0.0)
				x = (Filt[0] / Peak[0]);
				
			quotientFastLong = (x + KFastLong) / (KFastLong * x + 1);
			quotientSlowLong = (x + KSlowLong) / (KSlowLong * x + 1);
			quotientFastShort = (x + KFastShort) / (KFastShort * x + 1);
			quotientSlowShort = (x + KSlowShort) / (KSlowShort * x + 1);
			
			QTFastLong.Set(quotientFastLong);
			QTSlowLong.Set(quotientSlowLong);
			QTFastShort.Set(quotientFastShort);
			QTSlowShort.Set(quotientSlowShort);
		}

        #region Properties
		
        [Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries QTFastLong
        {
            get { return Values[0]; }
        }
		
		[Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries QTSlowLong
        {
            get { return Values[1]; }
        }
		
		[Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries QTFastShort
        {
            get { return Values[2]; }
        }
		
		[Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries QTSlowShort
        {
            get { return Values[3]; }
        }
		
		[Description("Fast quotient K value")]
		[GridCategory("Parameters")]
		public double KFastLong
		{
			get { return kFastLong; }
			set { kFastLong = Math.Max(0.01, Math.Min(value, 0.999)); }
		}
		
		[Description("Slow quotient K value")]
		[GridCategory("Parameters")]
		public double KSlowLong
		{
			get { return kSlowLong; }
			set { kSlowLong = Math.Max(0.01, Math.Min(value, 0.999)); }
		}
		
		[Description("Fast quotient K value")]
		[GridCategory("Parameters")]
		public double KFastShort
		{
			get { return kFastShort; }
			set { kFastShort = Math.Min(-0.01, Math.Max(value, -0.999)); }
		}
		
		[Description("Slow quotient K value")]
		[GridCategory("Parameters")]
		public double KSlowShort
		{
			get { return kSlowShort; }
			set { kSlowShort = Math.Min(-0.01, Math.Max(value, -0.999)); }
		}
		
		[Description("Low Pass filter Period")]
		[GridCategory("Parameters")]
		public int LPPeriod
		{
			get { return lPPeriod; }
			set { lPPeriod = Math.Max(1, value); }
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
        private QuotientTransform[] cacheQuotientTransform = null;

        private static QuotientTransform checkQuotientTransform = new QuotientTransform();

        /// <summary>
        /// John F. Ehlers : 'Early Trend Detection, The Quotient Transform' - TASC August 2014
        /// </summary>
        /// <returns></returns>
        public QuotientTransform QuotientTransform(double kFastLong, double kFastShort, double kSlowLong, double kSlowShort, int lPPeriod)
        {
            return QuotientTransform(Input, kFastLong, kFastShort, kSlowLong, kSlowShort, lPPeriod);
        }

        /// <summary>
        /// John F. Ehlers : 'Early Trend Detection, The Quotient Transform' - TASC August 2014
        /// </summary>
        /// <returns></returns>
        public QuotientTransform QuotientTransform(Data.IDataSeries input, double kFastLong, double kFastShort, double kSlowLong, double kSlowShort, int lPPeriod)
        {
            if (cacheQuotientTransform != null)
                for (int idx = 0; idx < cacheQuotientTransform.Length; idx++)
                    if (Math.Abs(cacheQuotientTransform[idx].KFastLong - kFastLong) <= double.Epsilon && Math.Abs(cacheQuotientTransform[idx].KFastShort - kFastShort) <= double.Epsilon && Math.Abs(cacheQuotientTransform[idx].KSlowLong - kSlowLong) <= double.Epsilon && Math.Abs(cacheQuotientTransform[idx].KSlowShort - kSlowShort) <= double.Epsilon && cacheQuotientTransform[idx].LPPeriod == lPPeriod && cacheQuotientTransform[idx].EqualsInput(input))
                        return cacheQuotientTransform[idx];

            lock (checkQuotientTransform)
            {
                checkQuotientTransform.KFastLong = kFastLong;
                kFastLong = checkQuotientTransform.KFastLong;
                checkQuotientTransform.KFastShort = kFastShort;
                kFastShort = checkQuotientTransform.KFastShort;
                checkQuotientTransform.KSlowLong = kSlowLong;
                kSlowLong = checkQuotientTransform.KSlowLong;
                checkQuotientTransform.KSlowShort = kSlowShort;
                kSlowShort = checkQuotientTransform.KSlowShort;
                checkQuotientTransform.LPPeriod = lPPeriod;
                lPPeriod = checkQuotientTransform.LPPeriod;

                if (cacheQuotientTransform != null)
                    for (int idx = 0; idx < cacheQuotientTransform.Length; idx++)
                        if (Math.Abs(cacheQuotientTransform[idx].KFastLong - kFastLong) <= double.Epsilon && Math.Abs(cacheQuotientTransform[idx].KFastShort - kFastShort) <= double.Epsilon && Math.Abs(cacheQuotientTransform[idx].KSlowLong - kSlowLong) <= double.Epsilon && Math.Abs(cacheQuotientTransform[idx].KSlowShort - kSlowShort) <= double.Epsilon && cacheQuotientTransform[idx].LPPeriod == lPPeriod && cacheQuotientTransform[idx].EqualsInput(input))
                            return cacheQuotientTransform[idx];

                QuotientTransform indicator = new QuotientTransform();
                indicator.BarsRequired = BarsRequired;
                indicator.CalculateOnBarClose = CalculateOnBarClose;
#if NT7
                indicator.ForceMaximumBarsLookBack256 = ForceMaximumBarsLookBack256;
                indicator.MaximumBarsLookBack = MaximumBarsLookBack;
#endif
                indicator.Input = input;
                indicator.KFastLong = kFastLong;
                indicator.KFastShort = kFastShort;
                indicator.KSlowLong = kSlowLong;
                indicator.KSlowShort = kSlowShort;
                indicator.LPPeriod = lPPeriod;
                Indicators.Add(indicator);
                indicator.SetUp();

                QuotientTransform[] tmp = new QuotientTransform[cacheQuotientTransform == null ? 1 : cacheQuotientTransform.Length + 1];
                if (cacheQuotientTransform != null)
                    cacheQuotientTransform.CopyTo(tmp, 0);
                tmp[tmp.Length - 1] = indicator;
                cacheQuotientTransform = tmp;
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
        /// John F. Ehlers : 'Early Trend Detection, The Quotient Transform' - TASC August 2014
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.QuotientTransform QuotientTransform(double kFastLong, double kFastShort, double kSlowLong, double kSlowShort, int lPPeriod)
        {
            return _indicator.QuotientTransform(Input, kFastLong, kFastShort, kSlowLong, kSlowShort, lPPeriod);
        }

        /// <summary>
        /// John F. Ehlers : 'Early Trend Detection, The Quotient Transform' - TASC August 2014
        /// </summary>
        /// <returns></returns>
        public Indicator.QuotientTransform QuotientTransform(Data.IDataSeries input, double kFastLong, double kFastShort, double kSlowLong, double kSlowShort, int lPPeriod)
        {
            return _indicator.QuotientTransform(input, kFastLong, kFastShort, kSlowLong, kSlowShort, lPPeriod);
        }
    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// John F. Ehlers : 'Early Trend Detection, The Quotient Transform' - TASC August 2014
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.QuotientTransform QuotientTransform(double kFastLong, double kFastShort, double kSlowLong, double kSlowShort, int lPPeriod)
        {
            return _indicator.QuotientTransform(Input, kFastLong, kFastShort, kSlowLong, kSlowShort, lPPeriod);
        }

        /// <summary>
        /// John F. Ehlers : 'Early Trend Detection, The Quotient Transform' - TASC August 2014
        /// </summary>
        /// <returns></returns>
        public Indicator.QuotientTransform QuotientTransform(Data.IDataSeries input, double kFastLong, double kFastShort, double kSlowLong, double kSlowShort, int lPPeriod)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.QuotientTransform(input, kFastLong, kFastShort, kSlowLong, kSlowShort, lPPeriod);
        }
    }
}
#endregion
