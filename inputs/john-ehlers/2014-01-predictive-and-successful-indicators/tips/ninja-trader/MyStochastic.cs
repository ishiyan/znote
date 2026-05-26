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
    [Description("John F. Ehlers : 'Predictive Indicators for effective trading strategies' - TASC January 2014")]
    public class MyStochastic : Indicator
    {
        #region Variables
		
            private int length = 20; 

			private double alpha1;
			private double a1;
			private double b1;
			private double c1;
			private double c2;
			private double c3;
			private double HighestC;
			private double LowestC;
			private double count;
			private double Stoc;
					
			private DataSeries HP;
			private DataSeries Filt;
			private DataSeries Stoc1;
			       	
        #endregion
		
        protected override void Initialize()
        {
			HP     = new DataSeries(this);
			Filt   = new DataSeries(this);
			Stoc1  = new DataSeries(this);
						
            Add(new Plot(Color.FromKnownColor(KnownColor.Red), PlotStyle.Line, "MyStochastics"));
            Add(new Line(Color.DarkBlue, .8, "Overbought"));
            Add(new Line(Color.DarkBlue, .2, "Oversold"));
			
			Plots[0].Pen.Width = 3;
			Lines[0].Pen.Width = 2;
			Lines[1].Pen.Width = 2;
			
            Overlay = false;
        }
		
		protected override void OnStartUp()
		{
			alpha1 = ((Math.Cos(((.707 * 360 / 48) * Math.PI) / 180)) + (Math.Sin(((.707 * 360 / 48) * Math.PI) / 180)) - 1) / (Math.Cos(((.707 * 360 / 48) * Math.PI) / 180));
			a1 = Math.Exp(-1.414 * 3.14159 / 10);
			b1 = 2 * a1 * (Math.Cos(((1.414 * 180 / 10) * Math.PI) / 180));
			c2 = b1;
			c3 = (a1 * -1) * a1;
			c1 = 1 - c2 - c3;
		}
     
        protected override void OnBarUpdate()
        {
			if(CurrentBar < Length)
			{
				MyStochastics.Set(0);
				HP.Set(0);
				Filt.Set(0);
				return;
			}				
			
            HP.Set((1 - alpha1 / 2) * (1 - alpha1 / 2) * (Close[0] - 2 * Close[1] + Close[2]) + 2 * (1 - alpha1) * HP[1] - (1 - alpha1) * (1 - alpha1) * HP[2]);
			Filt.Set(c1 * (HP[0] + HP[1]) / 2 + c2 * Filt[1] + c3 * Filt[2]);
			
			HighestC = Filt[0];
			LowestC = Filt[0];
			
			for(int i = 0; i < Length; i++)
			{
				if(Filt[i] > HighestC)
				{
					HighestC = Filt[i];
				}
				
				if(Filt[i] < LowestC)
				{
					LowestC = Filt[i];
				}
			}
			
			Stoc1.Set((Filt[0] - LowestC) / (HighestC - LowestC));
			
			MyStochastics.Set(c1 * (Stoc1[0] + Stoc1[1]) / 2 + c2 * MyStochastics[1] + c3 * MyStochastics[2]);
            
        }

        #region Properties
		
        [Browsable(false)]	// this line prevents the data series from being displayed in the indicator properties dialog, do not remove
        [XmlIgnore()]		// this line ensures that the indicator can be saved/recovered as part of a chart template, do not remove
        public DataSeries MyStochastics
        {
            get { return Values[0]; }
        }
		
		[Description("Length for the Stochastic")]
		[GridCategory("Parameters")]
		public int Length
		{
			get { return length; }
			set { length = Math.Max(1, value); }
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
        private MyStochastic[] cacheMyStochastic = null;

        private static MyStochastic checkMyStochastic = new MyStochastic();

        /// <summary>
        /// John F. Ehlers : 'Predictive Indicators for effective trading strategies' - TASC January 2014
        /// </summary>
        /// <returns></returns>
        public MyStochastic MyStochastic(int length)
        {
            return MyStochastic(Input, length);
        }

        /// <summary>
        /// John F. Ehlers : 'Predictive Indicators for effective trading strategies' - TASC January 2014
        /// </summary>
        /// <returns></returns>
        public MyStochastic MyStochastic(Data.IDataSeries input, int length)
        {
            if (cacheMyStochastic != null)
                for (int idx = 0; idx < cacheMyStochastic.Length; idx++)
                    if (cacheMyStochastic[idx].Length == length && cacheMyStochastic[idx].EqualsInput(input))
                        return cacheMyStochastic[idx];

            lock (checkMyStochastic)
            {
                checkMyStochastic.Length = length;
                length = checkMyStochastic.Length;

                if (cacheMyStochastic != null)
                    for (int idx = 0; idx < cacheMyStochastic.Length; idx++)
                        if (cacheMyStochastic[idx].Length == length && cacheMyStochastic[idx].EqualsInput(input))
                            return cacheMyStochastic[idx];

                MyStochastic indicator = new MyStochastic();
                indicator.BarsRequired = BarsRequired;
                indicator.CalculateOnBarClose = CalculateOnBarClose;
#if NT7
                indicator.ForceMaximumBarsLookBack256 = ForceMaximumBarsLookBack256;
                indicator.MaximumBarsLookBack = MaximumBarsLookBack;
#endif
                indicator.Input = input;
                indicator.Length = length;
                Indicators.Add(indicator);
                indicator.SetUp();

                MyStochastic[] tmp = new MyStochastic[cacheMyStochastic == null ? 1 : cacheMyStochastic.Length + 1];
                if (cacheMyStochastic != null)
                    cacheMyStochastic.CopyTo(tmp, 0);
                tmp[tmp.Length - 1] = indicator;
                cacheMyStochastic = tmp;
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
        /// John F. Ehlers : 'Predictive Indicators for effective trading strategies' - TASC January 2014
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.MyStochastic MyStochastic(int length)
        {
            return _indicator.MyStochastic(Input, length);
        }

        /// <summary>
        /// John F. Ehlers : 'Predictive Indicators for effective trading strategies' - TASC January 2014
        /// </summary>
        /// <returns></returns>
        public Indicator.MyStochastic MyStochastic(Data.IDataSeries input, int length)
        {
            return _indicator.MyStochastic(input, length);
        }
    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// John F. Ehlers : 'Predictive Indicators for effective trading strategies' - TASC January 2014
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.MyStochastic MyStochastic(int length)
        {
            return _indicator.MyStochastic(Input, length);
        }

        /// <summary>
        /// John F. Ehlers : 'Predictive Indicators for effective trading strategies' - TASC January 2014
        /// </summary>
        /// <returns></returns>
        public Indicator.MyStochastic MyStochastic(Data.IDataSeries input, int length)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.MyStochastic(input, length);
        }
    }
}
#endregion
