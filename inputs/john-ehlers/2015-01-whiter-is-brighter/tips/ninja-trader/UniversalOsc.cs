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
    [Description("John F. Ehlers : 'Whiter Is Brighter' - TASC January 2015")]
    public class UniversalOsc : Indicator
    {
        #region Variables
        private int bandEdge = 20; 
        private double a1, b1, c1, c2, c3;
        private DataSeries WhiteNoise, Filt, Peak;
        private double universal;
        #endregion

        protected override void Initialize()
        {
            Add(new Plot(Color.FromKnownColor(KnownColor.Red), PlotStyle.Line, "UniversalOscValue"));
            Add(new Plot(Color.FromKnownColor(KnownColor.LightBlue), PlotStyle.Line, "ZeroLine"));
            Overlay = false;
            WhiteNoise  = new DataSeries(this);
            Filt 		= new DataSeries(this);
            Peak 		= new DataSeries(this);
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < 2)
            {
                Peak.Set(0.0000001);
                return;
            }
            
			if (CurrentBar == 2) Filt.Set(c1 * 0 * (Close[0] + Close[1]) / 2 + c2 * Filt[1]);
            if (CurrentBar == 3) Filt.Set(c1 * 0 * (Close[0] + Close[1]) / 2 + c2 * Filt[1] + c3 * Filt[2]);

            WhiteNoise.Set((Close[0] - Close[2]) / 2);

            a1 = Math.Exp(-1.414 * Math.PI / BandEdge);
            b1 = 2 * a1 * (Math.Cos(((1.414 * 180 / BandEdge) * Math.PI) / 180));
            c2 = b1;
            c3 = -a1 * a1;
            c1 = 1 - c2 - c3;
            Filt.Set(c1 * (WhiteNoise[0] + WhiteNoise[1]) / 2 + c2 * Filt[1] + c3 * Filt[2]);

            Peak.Set(.991 * Peak[1]);
            
			if (Math.Abs(Filt[0]) > Peak[0])
            {
                Peak.Set(Math.Abs(Filt[0]));
            }
            
			if (Math.Abs(Peak[0]) > 0)
            {
                universal = Filt[0] / Peak[0];
            }
            
			UniversalOscValue.Set(universal);
            ZeroLine.Set(0);
        }

        #region Properties
        [Browsable(false)]
        [XmlIgnore()]
        public DataSeries UniversalOscValue
        {
            get { return Values[0]; }
        }

        [Browsable(false)]
        [XmlIgnore()]
        public DataSeries ZeroLine
        {
            get { return Values[1]; }
        }

        [Description("")]
        [GridCategory("Parameters")]
        public int BandEdge
        {
            get { return bandEdge; }
            set { bandEdge = Math.Max(1, value); }
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
        private UniversalOsc[] cacheUniversalOsc = null;

        private static UniversalOsc checkUniversalOsc = new UniversalOsc();

        /// <summary>
        /// John F. Ehlers : 'Whiter Is Brighter' - TASC January 2015
        /// </summary>
        /// <returns></returns>
        public UniversalOsc UniversalOsc(int bandEdge)
        {
            return UniversalOsc(Input, bandEdge);
        }

        /// <summary>
        /// John F. Ehlers : 'Whiter Is Brighter' - TASC January 2015
        /// </summary>
        /// <returns></returns>
        public UniversalOsc UniversalOsc(Data.IDataSeries input, int bandEdge)
        {
            if (cacheUniversalOsc != null)
                for (int idx = 0; idx < cacheUniversalOsc.Length; idx++)
                    if (cacheUniversalOsc[idx].BandEdge == bandEdge && cacheUniversalOsc[idx].EqualsInput(input))
                        return cacheUniversalOsc[idx];

            lock (checkUniversalOsc)
            {
                checkUniversalOsc.BandEdge = bandEdge;
                bandEdge = checkUniversalOsc.BandEdge;

                if (cacheUniversalOsc != null)
                    for (int idx = 0; idx < cacheUniversalOsc.Length; idx++)
                        if (cacheUniversalOsc[idx].BandEdge == bandEdge && cacheUniversalOsc[idx].EqualsInput(input))
                            return cacheUniversalOsc[idx];

                UniversalOsc indicator = new UniversalOsc();
                indicator.BarsRequired = BarsRequired;
                indicator.CalculateOnBarClose = CalculateOnBarClose;
#if NT7
                indicator.ForceMaximumBarsLookBack256 = ForceMaximumBarsLookBack256;
                indicator.MaximumBarsLookBack = MaximumBarsLookBack;
#endif
                indicator.Input = input;
                indicator.BandEdge = bandEdge;
                Indicators.Add(indicator);
                indicator.SetUp();

                UniversalOsc[] tmp = new UniversalOsc[cacheUniversalOsc == null ? 1 : cacheUniversalOsc.Length + 1];
                if (cacheUniversalOsc != null)
                    cacheUniversalOsc.CopyTo(tmp, 0);
                tmp[tmp.Length - 1] = indicator;
                cacheUniversalOsc = tmp;
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
        /// John F. Ehlers : 'Whiter Is Brighter' - TASC January 2015
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.UniversalOsc UniversalOsc(int bandEdge)
        {
            return _indicator.UniversalOsc(Input, bandEdge);
        }

        /// <summary>
        /// John F. Ehlers : 'Whiter Is Brighter' - TASC January 2015
        /// </summary>
        /// <returns></returns>
        public Indicator.UniversalOsc UniversalOsc(Data.IDataSeries input, int bandEdge)
        {
            return _indicator.UniversalOsc(input, bandEdge);
        }
    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// John F. Ehlers : 'Whiter Is Brighter' - TASC January 2015
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.UniversalOsc UniversalOsc(int bandEdge)
        {
            return _indicator.UniversalOsc(Input, bandEdge);
        }

        /// <summary>
        /// John F. Ehlers : 'Whiter Is Brighter' - TASC January 2015
        /// </summary>
        /// <returns></returns>
        public Indicator.UniversalOsc UniversalOsc(Data.IDataSeries input, int bandEdge)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.UniversalOsc(input, bandEdge);
        }
    }
}
#endregion
