// 
// Copyright (C) 2017, WhenToTrade.com
// www.whentotrade.com
// Book: Decoding The Hidden Market Rhythm - Part 1 (2017)
// Chapter 10: Cycle Swing Indicator
// Link: https://www.amazon.com/dp/1974658244
//
// License: 
// This work is licensed under a Creative Commons Attribution 4.0 International License.
// You are free to share the material in any medium or format and remix, transform, and build upon the material for any purpose, 
// even commercially. You must give appropriate credit to the authors book and website, provide a link to the license, and indicate 
// if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use. 
//

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
	public class WTTCycleSwingIndicator : Indicator
	{
		//used arrays for calculation
		double[] sourceValues= new double[50];
		double[] cycle1= new double[50];
		double[] cycle2= new double[50];
		double[] cycle3= new double[50];
		double[] wtt_processed= new double[50];
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description				= @"CSI: Smooth and fast momentum indicator based on dominant cycle acceleration. wwww.whentotrade.com";
				Name					= "WTT Cycle Swing Indicator";
				Calculate				= Calculate.OnBarClose;
				IsOverlay				= false;
				DisplayInDataBox			= true;
				DrawOnPricePanel			= true;
				DrawHorizontalGridLines			= true;
				DrawVerticalGridLines			= true;
				PaintPriceMarkers			= true;
				ScaleJustification			= NinjaTrader.Gui.Chart.ScaleJustification.Right;
				IsSuspendedWhileInactive		= true;
				AddPlot(Brushes.Crimson, "CSI");
				AddLine(Brushes.SlateBlue,	0,	NinjaTrader.Custom.Resource.NinjaScriptIndicatorZeroLine);
			}
			else if (State == State.Configure)
			{
			}
			else if (State == State.DataLoaded)
			{
			}
		}

		protected override void OnBarUpdate()
		{
			//Add your custom indicator logic here.
			if (CurrentBar + 1 <= 52) 
			{
				CSI[0]=0;
				return;
			}
			
			 //--- calculate indicator values
			      
			//--- prepare data	
			for(int p=0;p<50;p++)
			   sourceValues[p]=Close[49-p];
	
			 //--- pre-process dominant cycle momentum
			 double thrust1=iWTT_CSI_processor(sourceValues,1);
			 double thrust2=iWTT_CSI_processor(sourceValues,10);

			 //--- get the final cycle acceleration (aka swing)
			 CSI[0]=thrust1-thrust2;
			
		}
		
		//+------------------------------------------------------------------+
		//| www.WhenToTrade.com Cycle Swing Pre-Processor                    |
		//+------------------------------------------------------------------+
	  	double iWTT_CSI_processor(double[] raw, int CycleCount)
	  	{
		   double wtt1=0,wtt2=0,wtt3=0,wtt4=0,wtt5=0,_wtt1=0,_wtt2=0,_wtt3=0,_wtt4=0,_wtt5=0;
		   double momentum,acceleration,swing; 
		   
		   int cycs=50;
		   double waveThrottle=160*CycleCount;

		   for(int i=0;i<cycs;i++) wtt_processed[i]=raw[i];

		   if(cycs <= 5) return 0;

		   cycle1[0]= 1.0+waveThrottle;
		   cycle2[0]=-2.0*waveThrottle;
		   cycle3[0]=     waveThrottle;

		   for(int i=1;i<cycs-2;i++)
		     {
		      cycle1[i]= 6.0*waveThrottle+1.0;
		      cycle2[i]=-4.0*waveThrottle;
		      cycle3[i]=     waveThrottle;
		     }

		   cycle1[1]      = 1.0+waveThrottle*5.0;
		   cycle1[cycs-1] = 1.0+waveThrottle;
		   cycle1[cycs-2] = 1.0+waveThrottle*5.0;
		   cycle2[cycs-2] =-2.0*waveThrottle;
		   cycle2[cycs-1] = 0.0;
		   cycle3[cycs-2] = 0.0;
		   cycle3[cycs-1] = 0.0;

		   for(int i=0;i<cycs;i++)
		     {
		      swing=cycle1[i]-wtt4*wtt1-_wtt5*_wtt2;
		      if(swing==0) break;
		      momentum= cycle2[i];
		      _wtt1  = wtt1;
		      wtt1   = (momentum-wtt4*wtt2)/swing;
		      cycle2[i]=wtt1;

		      acceleration=cycle3[i];
		      _wtt2  = wtt2;
		      wtt2   = acceleration/swing;
		      cycle3[i]=wtt2;

		      cycle1[i]=(raw[i]-_wtt3*_wtt5-wtt3*wtt4)/swing;
		      _wtt3  = wtt3;
		      wtt3   = cycle1[i];
		      wtt4   = momentum-wtt5*_wtt1;
		      _wtt5  = wtt5;
		      wtt5   = acceleration;
		     }

		   wtt2 = 0;
		   wtt1 = cycle1[cycs-1];
		   wtt_processed[cycs-1]=wtt1;
		   for(int i=cycs-2; i>=0; i--)
		     {
		      wtt_processed[i]=cycle1[i]-cycle2[i]*wtt1-cycle3[i]*wtt2;
		      wtt2=wtt1;
		      wtt1=wtt_processed[i];
		     }
		     
		   return wtt_processed[49];

	  	}

		#region Properties

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> CSI
		{
			get { return Values[0]; }
		}
		#endregion

	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private WTTCycleSwingIndicator[] cacheWTTCycleSwingIndicator;
		public WTTCycleSwingIndicator WTTCycleSwingIndicator()
		{
			return WTTCycleSwingIndicator(Input);
		}

		public WTTCycleSwingIndicator WTTCycleSwingIndicator(ISeries<double> input)
		{
			if (cacheWTTCycleSwingIndicator != null)
				for (int idx = 0; idx < cacheWTTCycleSwingIndicator.Length; idx++)
					if (cacheWTTCycleSwingIndicator[idx] != null &&  cacheWTTCycleSwingIndicator[idx].EqualsInput(input))
						return cacheWTTCycleSwingIndicator[idx];
			return CacheIndicator<WTTCycleSwingIndicator>(new WTTCycleSwingIndicator(), input, ref cacheWTTCycleSwingIndicator);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.WTTCycleSwingIndicator WTTCycleSwingIndicator()
		{
			return indicator.WTTCycleSwingIndicator(Input);
		}

		public Indicators.WTTCycleSwingIndicator WTTCycleSwingIndicator(ISeries<double> input )
		{
			return indicator.WTTCycleSwingIndicator(input);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.WTTCycleSwingIndicator WTTCycleSwingIndicator()
		{
			return indicator.WTTCycleSwingIndicator(Input);
		}

		public Indicators.WTTCycleSwingIndicator WTTCycleSwingIndicator(ISeries<double> input )
		{
			return indicator.WTTCycleSwingIndicator(input);
		}
	}
}

#endregion
