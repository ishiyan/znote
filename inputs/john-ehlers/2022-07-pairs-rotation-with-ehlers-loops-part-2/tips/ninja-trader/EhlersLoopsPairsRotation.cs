#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.IO;
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
	public class EhlersLoopsPairsRotation : Indicator
	{
		private double hpa1;
		private double hpb1;
		private double hpc1;
		private double hpc2;
		private double hpc3;
		private double ssa1;
		private double ssb1;
		private double ssc1;
		private double ssc2;
		private double ssc3;
		private Series<double> HP1;
		private Series<double> HP2;
		private Series<double> Price1;
		private Series<double> Price1MS;
		private Series<double> Price2;
		private Series<double> Price2MS;
		private string path;
		private StreamWriter sw;
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The Ehlers Loops Pairs Rotation Indicator was published in the July 2022 Technical Analysis of Stocks and Commodities article titled 'Charting the Rotation - Pairs Rotation with Ehlers Loops' by John F. Ehlers.";
				Name										= @"Ehlers Loops Pairs Rotation";
				Calculate									= Calculate.OnBarClose;
				IsOverlay									= false;
				DisplayInDataBox							= true;
				DrawOnPricePanel							= true;
				DrawHorizontalGridLines						= true;
				DrawVerticalGridLines						= true;
				PaintPriceMarkers							= true;
				ScaleJustification							= NinjaTrader.Gui.Chart.ScaleJustification.Right;
				//Disable this property if your indicator requires custom values that cumulate with each new market data event. 
				//See Help Guide for additional information.
				IsSuspendedWhileInactive					= true;
				SecondarySeries								= "RTX";
				LPPeriod									= 20;
				HPPeriod									= 125;
				GenerateCSV									= false;
				path 										= NinjaTrader.Core.Globals.UserDataDir + "EhlersLoopsPairsRotation.csv";
				AddPlot(Brushes.Red, "Price1RMS");
				AddPlot(Brushes.Gold, "Price2RMS");
				AddLine(Brushes.RoyalBlue, 0, "ZeroLine");
				
			}
			else if (State == State.Configure)
			{
				AddDataSeries(SecondarySeries);
			}
			else if (State == State.DataLoaded)
			{
				HP1 		= new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				HP2 		= new Series<double>(BarsArray[1], MaximumBarsLookBack.TwoHundredFiftySix);
				Price1 		= new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				Price1MS 	= new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				Price2 		= new Series<double>(BarsArray[1], MaximumBarsLookBack.TwoHundredFiftySix);
				Price2MS 	= new Series<double>(BarsArray[1], MaximumBarsLookBack.TwoHundredFiftySix);
			}
			else if(State == State.Terminated)
			{
				if (sw != null)
				{
					sw.Close();
					sw.Dispose();
					sw = null;
				}
			}
		}

		protected override void OnBarUpdate()
		{
			hpa1 = Math.Exp(-1.414*3.14159/HPPeriod);
			hpb1 = 2 * hpa1 * Math.Cos((Math.PI/180) * (1.414 * 180 / HPPeriod));
			hpc2 = hpb1;
			hpc3 = -hpa1 * hpa1;
			hpc1 = (1 + hpc2 - hpc3) / 4;
			ssa1 = Math.Exp(-1.414 * 3.14159 / LPPeriod);
			ssb1 = 2 * ssa1 * Math.Cos((Math.PI/180) * (1.414 * 180 / LPPeriod));
			ssc2 = ssb1;
			ssc3 = -ssa1 * ssa1;
			ssc1 = 1 - ssc2 - ssc3;
			
			if (BarsInProgress == 0)
			{
				//Normalized roofing filter for Data1 (horizontal plot)
				
				// 2 pole Butterworth Highpass Filter
				if (CurrentBar < 3)
					HP1[0] = 0;
				else
					HP1[0] = hpc1 * (Close[0] - 2 * Close[1] + Close[2]) + hpc2 * HP1[1] + hpc3 * HP1[2];
				
				// Smooth with a Super Smoother Filter
				if (CurrentBar < 3)
					Price1[0] = 0;
				else
					Price1[0] = ssc1 * (HP1[0] + HP1[1]) / 2 + ssc2 * Price1[1] + ssc3 * Price1[2];
				
				// Scale Price in terms of Standard Deviations
				if (CurrentBar == 1)
					Price1MS[0] = Price1[0] * Price1[0];
				else
					Price1MS[0] = 0.0242 * Price1[0] * Price1[0] + .9758 * Price1MS[1];
				
				if (Price1MS[0] != 0)
					Price1RMS[0] = Price1[0] / (Math.Sqrt(Price1MS[0]));
			}
			if(BarsInProgress == 1)
			{
				//Normalized Roofing Filter for Data2 (horizontal plot);
				
				// 2 pole Butterworth Highpass Filter
				if (CurrentBar < 3)
					HP2[0] = 0;
				else
					HP2[0] = hpc1 * (Close[0] - 2 * Close[1] + Close[2]) + hpc2 * HP2[1] + hpc3 * HP2[2];
				
				// Smooth with a Super Smoother Filter
				if (CurrentBar < 3)
					Price2[0] = 0;
				else
					Price2[0] = ssc1 * (HP2[0] + HP2[1]) / 2 + ssc2 * Price2[1] + ssc3 * Price2[2];
				
				// Scale Price in terms of Standard Deviations
				if (CurrentBar == 1)
					Price2MS[0] = Price2[0] * Price2[0];
				else
					Price2MS[0] = 0.0242 * Price2[0] * Price2[0] + .9758 * Price2MS[1];
				
				if (Price2MS[0] != 0)
					Price2RMS[0] = Price2[0] / (Math.Sqrt(Price2MS[0]));
				
				if(GenerateCSV)
				{
					sw = File.AppendText(path);  // Open the path for writing
					sw.WriteLine(Time[0].Date + "," + Price1RMS[0] + "," + Price2RMS[0]); // Append a new line to the file
					sw.Close(); // Close the file to allow future calls to access the file again.
				}
			}
			
		}

		#region Properties
		[NinjaScriptProperty]
		[Display(Name="Secondary Series", Description="Secondary Instrument to be plotted with primary.", Order=1, GroupName="Parameters")]
		public string SecondarySeries
		{ get; set; }
		
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Low-Pass Period", Description="Period for low-pass filter", Order=2, GroupName="Parameters")]
		public int LPPeriod
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="High-pass Period", Description="Period for high-pass filter", Order=3, GroupName="Parameters")]
		public int HPPeriod
		{ get; set; }
		
		[NinjaScriptProperty]
		[Display(Name="Generate CSV", Description="Check to generate CSV for exploration/study.  File will be generated in your Documents > NinjaTrader 8 folder.", Order=4, GroupName="Parameters")]
		public bool GenerateCSV
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Price1RMS
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Price2RMS
		{
			get { return Values[1]; }
		}

		#endregion

	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private EhlersLoopsPairsRotation[] cacheEhlersLoopsPairsRotation;
		public EhlersLoopsPairsRotation EhlersLoopsPairsRotation(string secondarySeries, int lPPeriod, int hPPeriod, bool generateCSV)
		{
			return EhlersLoopsPairsRotation(Input, secondarySeries, lPPeriod, hPPeriod, generateCSV);
		}

		public EhlersLoopsPairsRotation EhlersLoopsPairsRotation(ISeries<double> input, string secondarySeries, int lPPeriod, int hPPeriod, bool generateCSV)
		{
			if (cacheEhlersLoopsPairsRotation != null)
				for (int idx = 0; idx < cacheEhlersLoopsPairsRotation.Length; idx++)
					if (cacheEhlersLoopsPairsRotation[idx] != null && cacheEhlersLoopsPairsRotation[idx].SecondarySeries == secondarySeries && cacheEhlersLoopsPairsRotation[idx].LPPeriod == lPPeriod && cacheEhlersLoopsPairsRotation[idx].HPPeriod == hPPeriod && cacheEhlersLoopsPairsRotation[idx].GenerateCSV == generateCSV && cacheEhlersLoopsPairsRotation[idx].EqualsInput(input))
						return cacheEhlersLoopsPairsRotation[idx];
			return CacheIndicator<EhlersLoopsPairsRotation>(new EhlersLoopsPairsRotation(){ SecondarySeries = secondarySeries, LPPeriod = lPPeriod, HPPeriod = hPPeriod, GenerateCSV = generateCSV }, input, ref cacheEhlersLoopsPairsRotation);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.EhlersLoopsPairsRotation EhlersLoopsPairsRotation(string secondarySeries, int lPPeriod, int hPPeriod, bool generateCSV)
		{
			return indicator.EhlersLoopsPairsRotation(Input, secondarySeries, lPPeriod, hPPeriod, generateCSV);
		}

		public Indicators.EhlersLoopsPairsRotation EhlersLoopsPairsRotation(ISeries<double> input , string secondarySeries, int lPPeriod, int hPPeriod, bool generateCSV)
		{
			return indicator.EhlersLoopsPairsRotation(input, secondarySeries, lPPeriod, hPPeriod, generateCSV);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.EhlersLoopsPairsRotation EhlersLoopsPairsRotation(string secondarySeries, int lPPeriod, int hPPeriod, bool generateCSV)
		{
			return indicator.EhlersLoopsPairsRotation(Input, secondarySeries, lPPeriod, hPPeriod, generateCSV);
		}

		public Indicators.EhlersLoopsPairsRotation EhlersLoopsPairsRotation(ISeries<double> input , string secondarySeries, int lPPeriod, int hPPeriod, bool generateCSV)
		{
			return indicator.EhlersLoopsPairsRotation(input, secondarySeries, lPPeriod, hPPeriod, generateCSV);
		}
	}
}

#endregion
