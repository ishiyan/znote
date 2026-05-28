using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.Design;

namespace NinjaTrader.Indicator
{
	/// <summary>
	/// SwamiNT. 
	/// </summary>
	[Description("Stocks and Commodities - April 2012 - Setting Strategies with SwamiCharts")]
	public class SwamiWave : Indicator
	{
		private int minLength = 8;
		private int maxLength = 40;
		private DataSeries[] iValues;

		private Color bulishColor = Color.Orange;
		private Color bearishColor = Color.Blue;
		private Color neutralColor = Color.Empty;
		delegate byte ComponentSelector(Color color);

		private static ComponentSelector redSelector = color => color.R;
		private static ComponentSelector greenSelector = color => color.G;
		private static ComponentSelector blueSelector = color => color.B;

		protected override void Initialize()
		{
			Name = "SwamiWave";
			Overlay = false;
			PriceTypeSupported = false;
			PlotsConfigurable = false;
			ChartOnly = true;
		}

		protected override void OnStartUp()
		{
			iValues = new DataSeries[maxLength - minLength + 1];
			for (int i = 0; i < iValues.Length; i++)
				iValues[i] = new DataSeries(this, MaximumBarsLookBack.Infinite);
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < maxLength) return;
			for (int x = 0; x < iValues.Length; x++)
				iValues[x].Set(BPF(x + minLength)[0]);
		}

		public override void Plot(Graphics graphics, Rectangle bounds, double min, double max)
		{
			if (ChartControl == null || Bars == null)
				return;
			try
			{
				for (int idx = LastBarIndexPainted; idx >= FirstBarIndexPainted; idx--)
				{
					if (idx - Displacement < 0 || idx - Displacement >= Bars.Count || (!ChartControl.ShowBarsRequired && idx - Displacement < BarsRequired))
						continue;

					int x = Math.Max(1, ChartControl.GetXByBarIdx(BarsArray[0], idx));
					for (int cIdx = 0; cIdx < iValues.Length; cIdx++)
					{
						float y = ChartControl.GetYByValue(this, cIdx + minLength - 0.5);
						float ymed = ChartControl.GetYByValue(this, cIdx + minLength);
						float y1 = ChartControl.GetYByValue(this, cIdx + minLength + 0.5);
						float height = y - y1;
						PointF[] ptsF = 	{ 		
												new PointF(x - ChartControl.BarSpace * 0.5F , y), 
												new PointF(x, y), 
												new PointF(x + ChartControl.BarSpace * 0.5F , y), 
												new PointF(x + ChartControl.BarSpace * 0.5F , ymed), 
												new PointF(x + ChartControl.BarSpace * 0.5F , y1), 
												new PointF(x , y1),
												new PointF(x - ChartControl.BarSpace * 0.5F , y1), 
												new PointF(x - ChartControl.BarSpace * 0.5F , ymed), 
											};
						PathGradientBrush pBrush = new PathGradientBrush(ptsF);
						double curVal = iValues[cIdx].Get(idx);
						double prevVal = iValues[cIdx].Get(Math.Max(0, idx - 1));
						double curAbove = cIdx == iValues.Length - 1 ? curVal : iValues[cIdx + 1].Get(idx);
						double prevAbove = cIdx == iValues.Length - 1 ? prevVal : iValues[cIdx + 1].Get(Math.Max(0, idx - 1));
						Color mainColor = InterpolateBetween(bearishColor, bulishColor, neutralColor, curVal);
						Color aboveColor = InterpolateBetween(bearishColor, bulishColor, neutralColor, curAbove);
						Color prevColor = InterpolateBetween(bearishColor, bulishColor, neutralColor, prevVal);
						Color prevAboveColor = InterpolateBetween(bearishColor, bulishColor, neutralColor, prevAbove);
						pBrush.CenterColor = mainColor;

						Color[] colors = {	
							prevColor, 
							mainColor, 
							mainColor, 
							mainColor, 
							aboveColor, 
							aboveColor, 
							prevAboveColor, 
							prevColor, 
						};
						pBrush.SurroundColors = colors;
						graphics.FillRectangle(pBrush, x - (ChartControl.BarSpace / 2 + 1), y1, ChartControl.BarSpace + 1, height);
						pBrush.Dispose();
					}
				}
			}
			catch { }
		}

		public override void GetMinMaxValues(ChartControl chartControl, ref double min, ref double max)
		{
			max = maxLength + 1;
			min = minLength - 1;
		}

		private static Color InterpolateBetween(Color downPoint, Color upPoint, Color midPoint, double lambda)
		{
			if (lambda < 0 || lambda > 1)
				throw new ArgumentOutOfRangeException("lambda");
			if (midPoint == Color.Transparent || midPoint == Color.Empty)
				return Color.FromArgb(
					InterpolateComponent(downPoint, upPoint, lambda, redSelector),
					InterpolateComponent(downPoint, upPoint, lambda, greenSelector),
					InterpolateComponent(downPoint, upPoint, lambda, blueSelector));
			if (lambda < 0.5)
				return Color.FromArgb(
					InterpolateComponent(downPoint, midPoint, lambda * 2, redSelector),
					InterpolateComponent(downPoint, midPoint, lambda * 2, greenSelector),
					InterpolateComponent(downPoint, midPoint, lambda * 2, blueSelector));
			return Color.FromArgb(
				InterpolateComponent(midPoint, upPoint, lambda * 2 - 1, redSelector),
				InterpolateComponent(midPoint, upPoint, lambda * 2 - 1, greenSelector),
				InterpolateComponent(midPoint, upPoint, lambda * 2 - 1, blueSelector));
		}

		private static byte InterpolateComponent(Color endPoint1, Color endPoint2, double lambda, ComponentSelector selector)
		{
			return (byte)(selector(endPoint1) + (selector(endPoint2) - selector(endPoint1)) * lambda);
		}

		#region Properties

		[Description("Min Period Length")]
		[GridCategory("Parameters")]
		[Gui.Design.DisplayName("Period Min Length")]
		public int MinLength
		{
			get { return minLength; }
			set { minLength = Math.Min(Math.Max(8, value), 24); }
		}

		[Description("Max Period Length")]
		[GridCategory("Parameters")]
		[Gui.Design.DisplayName("Period Max Length")]
		public int MaxLength
		{
			get { return maxLength; }
			set { maxLength = Math.Min(Math.Max(32, value), 48); }
		}

		[Description("Bearish Color")]
		[GridCategory("Parameters")]
		[Gui.Design.DisplayName("Bearish Color")]
		public Color BearishColor
		{
			get { return bearishColor; }
			set { bearishColor = value; }
		}

		[Description("Bulish Color")]
		[GridCategory("Parameters")]
		[Gui.Design.DisplayName("Bulish Color")]
		public Color BulishColor
		{
			get { return bulishColor; }
			set { bulishColor = value; }
		}

		[Description("Neutral Color")]
		[GridCategory("Parameters")]
		[Gui.Design.DisplayName("Neutral Color")]
		public Color NeutralColor
		{
			get { return neutralColor; }
			set { neutralColor = value; }
		}

		[Browsable(false)]
		public string BearishColorSerialize
		{
			get { return SerializableColor.ToString(bearishColor); }
			set { bearishColor = SerializableColor.FromString(value); }
		}

		[Browsable(false)]
		public string BulishColorSerialize
		{
			get { return SerializableColor.ToString(bulishColor); }
			set { bulishColor = SerializableColor.FromString(value); }
		}

		[Browsable(false)]
		public string NeutralColorSerialize
		{
			get { return SerializableColor.ToString(neutralColor); }
			set { neutralColor = SerializableColor.FromString(value); }
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
        private SwamiWave[] cacheSwamiWave = null;

        private static SwamiWave checkSwamiWave = new SwamiWave();

        /// <summary>
        /// Stocks and Commodities - April 2012 - Setting Strategies with SwamiCharts
        /// </summary>
        /// <returns></returns>
        public SwamiWave SwamiWave(Color bearishColor, Color bulishColor, int maxLength, int minLength, Color neutralColor)
        {
            return SwamiWave(Input, bearishColor, bulishColor, maxLength, minLength, neutralColor);
        }

        /// <summary>
        /// Stocks and Commodities - April 2012 - Setting Strategies with SwamiCharts
        /// </summary>
        /// <returns></returns>
        public SwamiWave SwamiWave(Data.IDataSeries input, Color bearishColor, Color bulishColor, int maxLength, int minLength, Color neutralColor)
        {
            if (cacheSwamiWave != null)
                for (int idx = 0; idx < cacheSwamiWave.Length; idx++)
                    if (cacheSwamiWave[idx].BearishColor == bearishColor && cacheSwamiWave[idx].BulishColor == bulishColor && cacheSwamiWave[idx].MaxLength == maxLength && cacheSwamiWave[idx].MinLength == minLength && cacheSwamiWave[idx].NeutralColor == neutralColor && cacheSwamiWave[idx].EqualsInput(input))
                        return cacheSwamiWave[idx];

            lock (checkSwamiWave)
            {
                checkSwamiWave.BearishColor = bearishColor;
                bearishColor = checkSwamiWave.BearishColor;
                checkSwamiWave.BulishColor = bulishColor;
                bulishColor = checkSwamiWave.BulishColor;
                checkSwamiWave.MaxLength = maxLength;
                maxLength = checkSwamiWave.MaxLength;
                checkSwamiWave.MinLength = minLength;
                minLength = checkSwamiWave.MinLength;
                checkSwamiWave.NeutralColor = neutralColor;
                neutralColor = checkSwamiWave.NeutralColor;

                if (cacheSwamiWave != null)
                    for (int idx = 0; idx < cacheSwamiWave.Length; idx++)
                        if (cacheSwamiWave[idx].BearishColor == bearishColor && cacheSwamiWave[idx].BulishColor == bulishColor && cacheSwamiWave[idx].MaxLength == maxLength && cacheSwamiWave[idx].MinLength == minLength && cacheSwamiWave[idx].NeutralColor == neutralColor && cacheSwamiWave[idx].EqualsInput(input))
                            return cacheSwamiWave[idx];

                SwamiWave indicator = new SwamiWave();
                indicator.BarsRequired = BarsRequired;
                indicator.CalculateOnBarClose = CalculateOnBarClose;
#if NT7
                indicator.ForceMaximumBarsLookBack256 = ForceMaximumBarsLookBack256;
                indicator.MaximumBarsLookBack = MaximumBarsLookBack;
#endif
                indicator.Input = input;
                indicator.BearishColor = bearishColor;
                indicator.BulishColor = bulishColor;
                indicator.MaxLength = maxLength;
                indicator.MinLength = minLength;
                indicator.NeutralColor = neutralColor;
                Indicators.Add(indicator);
                indicator.SetUp();

                SwamiWave[] tmp = new SwamiWave[cacheSwamiWave == null ? 1 : cacheSwamiWave.Length + 1];
                if (cacheSwamiWave != null)
                    cacheSwamiWave.CopyTo(tmp, 0);
                tmp[tmp.Length - 1] = indicator;
                cacheSwamiWave = tmp;
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
        /// Stocks and Commodities - April 2012 - Setting Strategies with SwamiCharts
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.SwamiWave SwamiWave(Color bearishColor, Color bulishColor, int maxLength, int minLength, Color neutralColor)
        {
            return _indicator.SwamiWave(Input, bearishColor, bulishColor, maxLength, minLength, neutralColor);
        }

        /// <summary>
        /// Stocks and Commodities - April 2012 - Setting Strategies with SwamiCharts
        /// </summary>
        /// <returns></returns>
        public Indicator.SwamiWave SwamiWave(Data.IDataSeries input, Color bearishColor, Color bulishColor, int maxLength, int minLength, Color neutralColor)
        {
            return _indicator.SwamiWave(input, bearishColor, bulishColor, maxLength, minLength, neutralColor);
        }
    }
}

// This namespace holds all strategies and is required. Do not change it.
namespace NinjaTrader.Strategy
{
    public partial class Strategy : StrategyBase
    {
        /// <summary>
        /// Stocks and Commodities - April 2012 - Setting Strategies with SwamiCharts
        /// </summary>
        /// <returns></returns>
        [Gui.Design.WizardCondition("Indicator")]
        public Indicator.SwamiWave SwamiWave(Color bearishColor, Color bulishColor, int maxLength, int minLength, Color neutralColor)
        {
            return _indicator.SwamiWave(Input, bearishColor, bulishColor, maxLength, minLength, neutralColor);
        }

        /// <summary>
        /// Stocks and Commodities - April 2012 - Setting Strategies with SwamiCharts
        /// </summary>
        /// <returns></returns>
        public Indicator.SwamiWave SwamiWave(Data.IDataSeries input, Color bearishColor, Color bulishColor, int maxLength, int minLength, Color neutralColor)
        {
            if (InInitialize && input == null)
                throw new ArgumentException("You only can access an indicator with the default input/bar series from within the 'Initialize()' method");

            return _indicator.SwamiWave(input, bearishColor, bulishColor, maxLength, minLength, neutralColor);
        }
    }
}
#endregion
