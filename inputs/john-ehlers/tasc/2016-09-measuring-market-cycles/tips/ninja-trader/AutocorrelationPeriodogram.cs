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
    /// The Autocorrelation Periodogram as detailed in the September 2016 Trader's Tips article Measuring Market Cycles.
    /// </summary>
    [Description("The Autocorrelation Periodogram as detailed in the September 2016 Trader's Tips article Measuring Market Cycles.")]
    public class AutocorrelationPeriodogram : Indicator
    {
        #region Variables
		private bool enhanceResolution = false;
		
		private int AvgLength		= 3;
		private int M				= 0;
		private int N				= 0;
		private double X			= 0;
		private double Y			= 0;
		private double alpha1		= 0;
		private double a1			= 0;
		private double b1			= 0;
		private double c1 			= 0;
		private double c2 			= 0;
		private double c3 			= 0;
		private int Lag 			= 0;
		private int count 			= 0;
		private double Sx 			= 0;
		private double Sy 			= 0;
		private double Sxx 			= 0;
		private double Syy 			= 0;
		private double Sxy 			= 0;
		private int Period 			= 0;
		private double Sp			= 0;
		private double Spx 			= 0;
		private double MaxPwr 		= 0;
		private double PeakPwr 		= 0;
		private int Color1 			= 0;
		private int Color2 			= 0;
		private int Color3 			= 0;
		
		private double[] Corr 		= new double[70];
		private double[] CosinePart = new double[70];
		private double[] SinePart 	= new double[70];
		private double[] SqSum 		= new double[70];
		private double[,] R 		= new double[70,3];
		private double[] Pwr	 	= new double[70];
		
		private DataSeries HP;
		private DataSeries Filt;
		private DataSeries DominantCycle;
		
        #endregion
		
        protected override void Initialize()
        {
			HP				= new DataSeries(this);
			Filt			= new DataSeries(this);
			DominantCycle	= new DataSeries(this);
			
			PaintPriceMarkers = false;
			Overlay	= false;
			BarsRequired = 0;
			
			#region Plots
			
			Add(new Plot(Color.Black, "Plot08"));
			Add(new Plot(Color.Black, "Plot09"));
			Add(new Plot(Color.Black, "Plot10"));
			Add(new Plot(Color.Black, "Plot11"));
			Add(new Plot(Color.Black, "Plot12"));
			Add(new Plot(Color.Black, "Plot13"));
			Add(new Plot(Color.Black, "Plot14"));
			Add(new Plot(Color.Black, "Plot15"));
			Add(new Plot(Color.Black, "Plot16"));
			Add(new Plot(Color.Black, "Plot17"));
			Add(new Plot(Color.Black, "Plot18"));
			Add(new Plot(Color.Black, "Plot19"));
			Add(new Plot(Color.Black, "Plot20"));
			Add(new Plot(Color.Black, "Plot21"));
			Add(new Plot(Color.Black, "Plot22"));
			Add(new Plot(Color.Black, "Plot23"));
			Add(new Plot(Color.Black, "Plot24"));
			Add(new Plot(Color.Black, "Plot25"));
			Add(new Plot(Color.Black, "Plot26"));
			Add(new Plot(Color.Black, "Plot27"));
			Add(new Plot(Color.Black, "Plot28"));
			Add(new Plot(Color.Black, "Plot29"));
			Add(new Plot(Color.Black, "Plot30"));
			Add(new Plot(Color.Black, "Plot31"));
			Add(new Plot(Color.Black, "Plot32"));
			Add(new Plot(Color.Black, "Plot33"));
			Add(new Plot(Color.Black, "Plot34"));
			Add(new Plot(Color.Black, "Plot35"));
			Add(new Plot(Color.Black, "Plot36"));
			Add(new Plot(Color.Black, "Plot37"));
			Add(new Plot(Color.Black, "Plot38"));
			Add(new Plot(Color.Black, "Plot39"));
			Add(new Plot(Color.Black, "Plot40"));
			Add(new Plot(Color.Black, "Plot41"));
			Add(new Plot(Color.Black, "Plot42"));
			Add(new Plot(Color.Black, "Plot43"));
			Add(new Plot(Color.Black, "Plot44"));
			Add(new Plot(Color.Black, "Plot45"));
			Add(new Plot(Color.Black, "Plot46"));
			Add(new Plot(Color.Black, "Plot47"));
			Add(new Plot(Color.Black, "Plot48"));
			
			#endregion
        }
		
        protected override void OnBarUpdate()
        {
			if (CurrentBar <= 1)
			{
				HP[0] = 0;
				return;
			}
				
			DominantCycle[0] 	= 0;
			PeakPwr 			= 0;
			Spx 				= 0;
			Sp 					= 0;
			
			//Highpass Filter and SuperSmoother Filter together form a Roofing Filter
			
			//Highpass Filter
			HP[0]		= Math.Round(0.94*(Close[0] - Close[1]) + 0.88*HP[1], 2);
			
			//Smooth with a SuperSmoother Filter
			Filt[0] 	= Math.Round(0.35*(HP[0] + HP[1]) / 2 + 0.98*Filt[1] + -0.33*Filt[2], 2);
			
			//Pearson correlation for each value of lag
			for (Lag = 0; Lag <= 48; Lag++)
			{
				//Set the averaging length as M
				M 	= AvgLength != 0 ? AvgLength : Lag;
				
				Sx 	= 0; Sy = 0; Sxx = 0; Syy = 0; Sxy = 0;
				for (count = 0; count < M; count++)
				{
					X 	= Filt[count];
					Y 	= Filt[Lag + count];
					Sx 	= Sx + X;
					Sy 	= Sy + Y;
					Sxx = Sxx + X*X;
					Sxy = Sxy + X*Y;
					Syy = Syy + Y*Y;
				}
				
				if ((M*Sxx - Sx*Sx)*(M*Syy - Sy*Sy) > 0)
				{
					Corr[Lag] = Math.Round((M*Sxy - Sx*Sy)/Math.Sqrt((M*Sxx - Sx*Sx)*(M*Syy - Sy*Sy)), 2);
				}
			}
			
			//Compute the Fourier Transform for each Correlation
			for (Period = 8; Period <= 48; Period++)
			{
					
				CosinePart[Period] 	= 0;
				SinePart[Period] 	= 0;
				
				for (N = 3; N <= 48; N++)
				{
					CosinePart[Period] 	= Math.Round(CosinePart[Period] + Corr[N]*Math.Cos(((360*N / Period) * Math.PI) / 180), 2);
					SinePart[Period] 	= Math.Round(SinePart[Period] + Corr[N]*Math.Sin(((360*N / Period) * Math.PI) / 180), 2);
				}
				SqSum[Period] = Math.Round(CosinePart[Period]*CosinePart[Period] + SinePart[Period]*SinePart[Period], 2);
			}
			for (Period = 7; Period < 48; Period++)
			{
				R[Period, 1] = R[Period, 0];
				R[Period, 0] = Math.Round(.2*SqSum[Period]*SqSum[Period] + .8*R[Period, 1], 2);
			}
				
			//Find Maximum Power Level for Normalization
			MaxPwr = 0;
			for (Period = 7; Period < 48; Period++)
			{
				if (R[Period, 0] > MaxPwr)
					MaxPwr = R[Period, 0];
			}
			for (Period = 7; Period < 48; Period++)
			{
				Pwr[Period] = R[Period, 0] / MaxPwr;
			}
				
			//Optionally increase Display Resolution by raising the NormPwr to a higher mathematically power (since the maximum amplitude is unity, cubing all amplitudes further reduces the smaller ones).
			if (enhanceResolution)
			{
				for (Period = 8; Period < 48; Period++)
				{
					Pwr[Period] = Math.Pow(Pwr[Period], 3);
				}
			}

			//Compute the dominant cycle using the CG of the spectrum
			for (Period = 7; Period < 48; Period++)
			{
				if (Pwr[Period] > PeakPwr)
					PeakPwr = Pwr[Period];
			}
			
			for (Period = 7; Period < 48; Period++)
			{				
				if (PeakPwr >= .25 && Pwr[Period] >= .25)
				{
					Spx = Spx + Period*Pwr[Period];
					Sp = Sp + Pwr[Period];
				}
			}
			
			//Plot as a Heatmap
			for (Period = 7; Period < 48; Period++)
			{
				if (double.IsNaN(Pwr[Period])) return;
				double holdColor = 0;
				Color3 = 0;
				if (Pwr[Period] > .5)
				{
					Color1 = 255;
					holdColor = 255*(2*Pwr[Period] - 1);
					Color2 = Convert.ToInt32(holdColor);
				}
				else
				{
					holdColor = 2*255*Pwr[Period];
					Color1 = Convert.ToInt32(holdColor);
					Color2 = 0;
				}
				
				Values[Period-7][0] 	= Period+1;
				PlotColors[Period-7][0] = Color.FromArgb(Color1, Color2, Color3);
				Plots[Period-7].PlotStyle = PlotStyle.Dot;
				Plots[Period-7].Pen.Width = 3;
			}
			
			if (Sp != 0)
				DominantCycle[0] = Spx / Sp;
			if (Sp < .25)
				DominantCycle[0] = DominantCycle[1];
			
        }

        #region Properties
		[Description("Increase Display Resolution")]
		[GridCategory("Parameters")]
		public bool EnhanceResolution
		{
			get { return enhanceResolution; }
			set { enhanceResolution = value; }
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
        private AutocorrelationPeriodogram[] cacheAutocorrelationPeriodogram = null;

        private static AutocorrelationPeriodogram checkAutocorrelationPeriodogram = new AutocorrelationPeriodogram();

        /// <summary>
        /// The Autocorrelation Periodogram as detailed in the September 2016 Trader's Tips article Measuring Market Cycles.
        /// </summary>
        /// <returns></returns>
        public AutocorrelationPeriodogram AutocorrelationPeriodogram(bool enhanceResolution)
        {
            return AutocorrelationPeriodogram(Input, enhanceResolution);
        }

        /// <summary>
        /// The Autocorrelation Periodogram as detailed in the September 2016 Trader's Tips article Measuring Market Cycles.
        /// </summary>
        /// <returns></returns>
        public AutocorrelationPeriodogram AutocorrelationPeriodogram(Data.IDataSeries input, bool enhanceResolution)
        {
            if (cacheAutocorrelationPeriodogram != null)
                for (int idx = 0; idx < cacheAutocorrelationPeriodogram.Length; idx++)
                    if (cacheAutocorrelationPeriodogram[idx].EnhanceResolution == enhanceResolution && cacheAutocorrelationPeriodogram[idx].EqualsInput(input))
                        return cacheAutocorrelationPeriodogram[idx];

            lock (checkAutocorrelationPeriodogram)
            {
                checkAutocorrelationPeriodogram.EnhanceResolution = enhanceResolution;
                enhanceResolution = checkAutocorrelationPeriodogram.EnhanceResolution;

                if (cacheAutocorrelationPeriodogram != null)
                    for (int idx = 0; idx < cacheAutocorrelationPeriodogram.Length; idx++)
                        if (cacheAutocorrelationPeriodogram[idx].EnhanceResolution == enhanceResolution && cacheAutocorrelationPeriodogram[idx].EqualsInput(input))
                            return cacheAutocorrelationPeriodogram[idx];

                AutocorrelationPeriodogram indicator = new AutocorrelationPeriodogram();
                indicator.BarsRequired = BarsRequired;
                indicator.CalculateOnBarClose = CalculateOnBarClose;
#if NT7
                indicator.ForceMaximumBarsLookBack256 = ForceMaximumBarsLookBack256;
                indicator.MaximumBarsLookBack = MaximumBarsLookBack;
#endif
                indicator.Input = input;
                indicator.EnhanceResolution = enhanceResolution;
                Indicators.Add(indicator);
                indicator.SetUp();

                AutocorrelationPeriodogram[] tmp = new AutocorrelationPeriodogram[cacheAutocorrelationPeriodogram == null ? 1 : cacheAutocorrelationPeriodogram.Length + 1];
                if (cacheAutocorrelationPeriodogram != null)
                    cacheAutocorrelationPeriodogram.CopyTo(tmp, 0);
                tmp[tmp.Length - 1] = indicator;
                cacheAutocorrelationPeriodogram = tmp;
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
        /// The Autocorrelation Periodogram as detailed in the September 2016 Trader's Tips article Measuring Market Cycles.
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.AutocorrelationPeriodogram AutocorrelationPeriodogram(bool enhanceResolution)
        {
            return _indicator.AutocorrelationPeriodogram(Input, enhanceResolution);
        }

        /// <summary>
        /// The Autocorrelation Periodogram as detailed in the September 2016 Trader's Tips article Measuring Market Cycles.
        /// </summary>
        /// <returns></returns>
        public Indicator.AutocorrelationPeriodogram AutocorrelationPeriodogram(Data.IDataSeries input, bool enhanceResolution)
        {
            return _indicator.AutocorrelationPeriodogram(input, enhanceResolution);
        }
    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// The Autocorrelation Periodogram as detailed in the September 2016 Trader's Tips article Measuring Market Cycles.
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.AutocorrelationPeriodogram AutocorrelationPeriodogram(bool enhanceResolution)
        {
            return _indicator.AutocorrelationPeriodogram(Input, enhanceResolution);
        }

        /// <summary>
        /// The Autocorrelation Periodogram as detailed in the September 2016 Trader's Tips article Measuring Market Cycles.
        /// </summary>
        /// <returns></returns>
        public Indicator.AutocorrelationPeriodogram AutocorrelationPeriodogram(Data.IDataSeries input, bool enhanceResolution)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.AutocorrelationPeriodogram(input, enhanceResolution);
        }
    }
}
#endregion
