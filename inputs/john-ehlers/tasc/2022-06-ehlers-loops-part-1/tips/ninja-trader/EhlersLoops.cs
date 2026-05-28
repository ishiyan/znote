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
	public class EhlersLoops : Indicator
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
		private Series<double> HP;
		private Series<double> VolHP;
		private Series<double> Price;
		private Series<double> PriceMS;
		private Series<double> Vol;
		private Series<double> VolMS;
		private string path;
		private StreamWriter sw;
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The Ehlers Loops Indicator was published in the June 2022 Technical Analysis of Stocks and Commodities article titled 'Rotation In Motion - Ehlers Loops Part 1' by John F. Ehlers.";
				Name										= @"Ehlers Loops";
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
				LPPeriod									= 20;
				HPPeriod									= 125;
				GenerateCSV									= false;
				path 										= NinjaTrader.Core.Globals.UserDataDir + "EhlersLoops.csv";
				AddPlot(Brushes.Red, "PriceRMS");
				AddPlot(Brushes.Gold, "VolRMS");
				AddLine(Brushes.RoyalBlue, 0, "ZeroLine");
				
			}
			else if (State == State.DataLoaded)
			{
				HP 		= new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				VolHP 	= new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				Price 	= new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				PriceMS = new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				Vol 	= new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
				VolMS 	= new Series<double>(this, MaximumBarsLookBack.TwoHundredFiftySix);
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
			
			//Normalized roofing filter for price
			
			// 2 pole Butterworth Highpass Filter
			if (CurrentBar < 3)
				HP[0] = 0;
			else
				HP[0] = hpc1 * (Close[0] - 2 * Close[1] + Close[2]) + hpc2 * HP[1] + hpc3 * HP[2];
			
			// Smooth with a Super Smoother Filter
			if (CurrentBar < 3)
				Price[0] = 0;
			else
				Price[0] = ssc1 * (HP[0] + HP[1]) / 2 + ssc2 * Price[1] + ssc3 * Price[2];
			
			// Scale Price in terms of Standard Deviations
			if (CurrentBar == 1)
				PriceMS[0] = Price[0] * Price[0];
			else
				PriceMS[0] = 0.0242 * Price[0] * Price[0] + .9758 * PriceMS[1];
			
			if (PriceMS[0] != 0)
				PriceRMS[0] = Price[0] / (Math.Sqrt(PriceMS[0]));
			
			//Normalized Roofing Filter for Volume
			
			// 2 Pole Butterworth Highpass Filter
			if(CurrentBar < 3)
				VolHP[0] = 0;
			else 
				VolHP[0] = hpc1*(Volume[0] - 2 * Volume[1] + Volume[2]) + hpc2 * VolHP[1] + hpc3 * VolHP[2];
			
			// Smooth with a Super Smoother Filter
			if (CurrentBar < 3)
				Vol[0] = 0;
			else
				Vol[0] = ssc1 * (VolHP[0] + VolHP[1])/2 + ssc2 * Vol[1] + ssc3 * Vol[2];
			
			//Scale Vol in terms of Standard Deviations
			if (CurrentBar == 1)
				VolMS[0] = Vol[0] * Vol[0];
			else
				VolMS[0] = 0.0242 * Vol[0] * Vol[0]  + 0.9758 * VolMS[1];
			
			if (VolMS[0] != 0)
				VolRMS[0] = Vol[0] / Math.Sqrt(VolMS[0]);
			
			if(GenerateCSV)
			{
				sw = File.AppendText(path);  // Open the path for writing
				sw.WriteLine(Time[0].Date + "," + VolRMS[0] + "," + PriceRMS[0]); // Append a new line to the file
				sw.Close(); // Close the file to allow future calls to access the file again.
			}
			
			
		}

		#region Properties
		
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Low-Pass Period", Description="Period for low-pass filter", Order=1, GroupName="Parameters")]
		public int LPPeriod
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="High-pass Period", Description="Period for high-pass filter", Order=2, GroupName="Parameters")]
		public int HPPeriod
		{ get; set; }
		
		[NinjaScriptProperty]
		[Display(Name="Generate CSV", Description="Check to generate CSV for exploration/study.  File will be generated in your Documents > NinjaTrader 8 folder.", Order=3, GroupName="Parameters")]
		public bool GenerateCSV
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> PriceRMS
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> VolRMS
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
		private EhlersLoops[] cacheEhlersLoops;
		public EhlersLoops EhlersLoops(int lPPeriod, int hPPeriod, bool generateCSV)
		{
			return EhlersLoops(Input, lPPeriod, hPPeriod, generateCSV);
		}

		public EhlersLoops EhlersLoops(ISeries<double> input, int lPPeriod, int hPPeriod, bool generateCSV)
		{
			if (cacheEhlersLoops != null)
				for (int idx = 0; idx < cacheEhlersLoops.Length; idx++)
					if (cacheEhlersLoops[idx] != null && cacheEhlersLoops[idx].LPPeriod == lPPeriod && cacheEhlersLoops[idx].HPPeriod == hPPeriod && cacheEhlersLoops[idx].GenerateCSV == generateCSV && cacheEhlersLoops[idx].EqualsInput(input))
						return cacheEhlersLoops[idx];
			return CacheIndicator<EhlersLoops>(new EhlersLoops(){ LPPeriod = lPPeriod, HPPeriod = hPPeriod, GenerateCSV = generateCSV }, input, ref cacheEhlersLoops);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.EhlersLoops EhlersLoops(int lPPeriod, int hPPeriod, bool generateCSV)
		{
			return indicator.EhlersLoops(Input, lPPeriod, hPPeriod, generateCSV);
		}

		public Indicators.EhlersLoops EhlersLoops(ISeries<double> input , int lPPeriod, int hPPeriod, bool generateCSV)
		{
			return indicator.EhlersLoops(input, lPPeriod, hPPeriod, generateCSV);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.EhlersLoops EhlersLoops(int lPPeriod, int hPPeriod, bool generateCSV)
		{
			return indicator.EhlersLoops(Input, lPPeriod, hPPeriod, generateCSV);
		}

		public Indicators.EhlersLoops EhlersLoops(ISeries<double> input , int lPPeriod, int hPPeriod, bool generateCSV)
		{
			return indicator.EhlersLoops(input, lPPeriod, hPPeriod, generateCSV);
		}
	}
}

#endregion
