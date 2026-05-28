#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

//This namespace holds Indicators in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Indicators
{
    public class AutoCorrelation : Indicator
    {
        private List<Series<int>> color1Series;
        private List<Series<int>> color2Series;
        private double[] _corr = new double[160];
        private SharpDX.Direct2D1.Brush[,] brushMatrix;
        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = @"AutoCorrelation Indicator by John F. Ehlers - Made for the topic for the February 2025 Traders' Tips is an article by John Ehlers titled “Drunkard’s Walk:  Theory And Measurement By Autocorrelation.”";
                Name = "AutoCorrelation";
                Calculate = Calculate.OnBarClose;
                IsOverlay = false;
                DisplayInDataBox = false;
                DrawOnPricePanel = true;
                DrawHorizontalGridLines = true;
                DrawVerticalGridLines = true;
                PaintPriceMarkers = false;
                ArePlotsConfigurable = false;
                ScaleJustification = NinjaTrader.Gui.Chart.ScaleJustification.Right;
                IsSuspendedWhileInactive = true;
                Length = 20;
                brushMatrix = new SharpDX.Direct2D1.Brush[256, 256];
            }
            if (State == State.Configure)
            {
                for (int i = 0; i <= 100; i++)
                {
                    AddPlot(new Stroke(Brushes.Blue), PlotStyle.Dot, "Plot" + i);
                }
            }
            if (State == State.DataLoaded)
            {
                color1Series = new List<Series<int>>();
                color2Series = new List<Series<int>>();
                for (int i = 0; i < 100; i++)
                {
                    color1Series.Add(new Series<int>(this, MaximumBarsLookBack.Infinite));
                    color2Series.Add(new Series<int>(this, MaximumBarsLookBack.Infinite));
                }
            }
        }

        protected override void OnBarUpdate()
        {
            var filtered = UltimateSmoother(Close, Length);

            if (CurrentBar <  Length) return;

            for (int lag = 0; lag < 100; lag++)
            {
                double sx = 0, sy = 0, sxx = 0, sxy = 0, syy = 0;
                for (int j = 0; j < Length; j++)
                {

                    double x = filtered[j];
                    double y = filtered[Math.Min(CurrentBar, lag + j)];
                    sx += x;
                    sy += y;
                    sxx += x * x;
                    sxy += x * y;
                    syy += y * y;
                }

                double denom = Math.Sqrt((Length * sxx - sx * sx) * (Length * syy - sy * sy));
                _corr[lag + 1] = denom > 0 ? (Length * sxy - sx * sy) / denom : 0;
            }

            for (int i = 0; i < 100; i++)
            {
                double corr = _corr[i + 1];
                int color1 = 255;
                int color2 = 255;

                if (corr >= 0)
                {
                    color1 = (int)(255 * (1 - corr));
                }
                else
                {
                    color2 = (int)(255 * (1 + corr));
                }

                Values[i][0] = i;

                color1Series[i][0] = color1;
                color2Series[i][0] = color2;
            }
        }

        #region Custom Rendering
        public override void OnRenderTargetChanged()
        {
            if (brushMatrix != null)
            {
                for (int i = 0; i <= 255; i++)
                {
                    for (int j = 0; j <= 255; j++)
                    {
                        if (brushMatrix[i, j] != null)
                        {
                            brushMatrix[i, j].Dispose();
                        }
                    }
                }
            }

            if (RenderTarget != null)
            {
                for (int i = 0; i <= 255; i++)
                {
                    for (int j = 0; j <= 255; j++)
                    {
                        SolidColorBrush color = new SolidColorBrush(Color.FromArgb((byte)255, (byte)i, (byte)j, 0));
                        brushMatrix[i, j] = color.ToDxBrush(RenderTarget);
                    }
                }
            }
        }

        protected override void OnRender(ChartControl chartControl, ChartScale chartScale)
        {
            if (ChartBars != null)
            {
                int visibleBars = ChartBars.ToIndex - ChartBars.FromIndex;
                int ellepiseSize = (int)Math.Max(1, visibleBars * 0.03);
                for (int barIndex = ChartBars.FromIndex; barIndex <= ChartBars.ToIndex; barIndex++)
                {
                    for (int i = 0; i < Values.Length - 1; i++)
                    {
                        int color1 = color1Series[i].GetValueAt(barIndex);
                        int color2 = color2Series[i].GetValueAt(barIndex);
                        if (color1 <= 0 || color2 <= 0) continue;
                        SharpDX.Direct2D1.Brush dxBrush = brushMatrix[color1, color2];
                        double price = Values[i].GetValueAt(barIndex);
                        if (price <= 0) continue;
                        float y = chartScale.GetYByValue(price);
                        float x = chartControl.GetXByBarIndex(ChartBars, barIndex);
                        RenderTarget.FillEllipse(new SharpDX.Direct2D1.Ellipse(new SharpDX.Vector2(x, y), Math.Min(10, ellepiseSize * 10), 5), dxBrush);
                    }
                }
            }
        }

        #endregion

        [Range(5, int.MaxValue), NinjaScriptProperty]
        [Display(Name = "Length", GroupName = "NinjaScriptParameters", Order = 0)]
        public int Length
        { get; set; }
    }
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private AutoCorrelation[] cacheAutoCorrelation;
		public AutoCorrelation AutoCorrelation(int length)
		{
			return AutoCorrelation(Input, length);
		}

		public AutoCorrelation AutoCorrelation(ISeries<double> input, int length)
		{
			if (cacheAutoCorrelation != null)
				for (int idx = 0; idx < cacheAutoCorrelation.Length; idx++)
					if (cacheAutoCorrelation[idx] != null && cacheAutoCorrelation[idx].Length == length && cacheAutoCorrelation[idx].EqualsInput(input))
						return cacheAutoCorrelation[idx];
			return CacheIndicator<AutoCorrelation>(new AutoCorrelation(){ Length = length }, input, ref cacheAutoCorrelation);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.AutoCorrelation AutoCorrelation(int length)
		{
			return indicator.AutoCorrelation(Input, length);
		}

		public Indicators.AutoCorrelation AutoCorrelation(ISeries<double> input , int length)
		{
			return indicator.AutoCorrelation(input, length);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.AutoCorrelation AutoCorrelation(int length)
		{
			return indicator.AutoCorrelation(Input, length);
		}

		public Indicators.AutoCorrelation AutoCorrelation(ISeries<double> input , int length)
		{
			return indicator.AutoCorrelation(input, length);
		}
	}
}

#endregion
