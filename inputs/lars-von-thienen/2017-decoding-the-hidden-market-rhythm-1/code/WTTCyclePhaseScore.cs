// 
// Copyright (C) 2017 CC BY, WhenToTrade.com
// www.whentotrade.com
// Warning: Might take long for initial calculation for historical data on chart!
// Rate limits: You need an API key allowing rate limites to calculate for each (historical) bar
//              demo key might not work with history on chart
// Info: You must use a valid WTT API key to run this script
// Book: Decoding The Hidden Market Rhythm - Part 1 (2017)
// Chapter 9: Cycle Phasing Oscillator
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
using System.Net.Http;
#endregion

//This namespace holds Indicators in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Indicators
{
	using Newtonsoft.Json; // Additional reference to package needed
	
	public class WTTCyclePhaseScore : Indicator
	{
		List<double> closeList = new List<double>();
		HttpClient client = new HttpClient();
				
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"Plots the phasing score oscillator of the active dominant cycles";
				Name										= "WTT Cycle Phase Score";
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
				AddPlot(Brushes.Orange, "DominantCyclePhase");
				
				minCycleLength			= 30;
				maxCycleLength			= 290;
				apiKey					= "";
				
				//WhenToTrade API URL
				client.BaseAddress = new Uri("https://api.marketcycles.online/");
			}
			else if (State == State.Configure)
			{
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar>751) //start once 700 bars are available as lookback
			{
					string APIresultContent="";
				
					//Get and prepare the close data array
					//--- prepare data	
					closeList.Clear();
					for(int p=0;p<=750;p++)
						closeList.Add(Close[750-p]);
					 											
				    //Call the WhenToTrade Cycles API endpoint POST CycleExplorer
					//Load the close dataset for HTTP API POST call
	                var contents = JsonConvert.SerializeObject(closeList.ToArray());
	                StringContent POSTcontent = new StringContent(contents, Encoding.UTF8, "application/json");

					//POST API CALL
	                var response = client.PostAsync("/api/CycleExplorer?minCycleLength="+minCycleLength+"&maxCycleLength="+maxCycleLength+"&plotForward=0&includeTimeseries=false&api_Key="+apiKey, POSTcontent).Result;			
					
					//Check for network errors
					if( response.IsSuccessStatusCode)
				    {
				        APIresultContent = response.Content.ReadAsStringAsync().Result;
				    }
				    else
				    {
				        string msg = response.Content.ReadAsStringAsync().Result;
				        Draw.TextFixed(this, "apierror", "API ERROR:"+msg, TextPosition.TopLeft);
						return;
				    }
		       
				
					// Decode the cycle data from API call
					var dominantCycle = JsonConvert.DeserializeObject<dynamic>(APIresultContent);
					
					// Test for return errors from API?
					string statusCode=dominantCycle.StatusCode !=null ? dominantCycle.StatusCode : "";
					bool error = statusCode.IndexOf("error", StringComparison.OrdinalIgnoreCase) >= 0;
					if (error)
					{
						Draw.TextFixed(this, "apierror", "API ERROR:"+statusCode, TextPosition.TopLeft);
						return;
					}
					
					//get key cycle information from return object
		            var cyclelength = dominantCycle.length;
					
					//Variant A: use score of dominant cycle
					//var cyclePhase = dominantCycle.phase_score;
					
					//Variant B: use the phasing score of long- and short-term cycle
					var cyclePhase = dominantCycle.PhasingScore;
					
					DominantCyclePhase[0]=cyclePhase;
		            								
			}		
		}
		
		//dont show the individual API key on screen
		public override string DisplayName
		{
		  get { return Name + "("+minCycleLength+","+maxCycleLength+")"; }
		}

		#region Properties
		
		[Range(10, 291)]
		[NinjaScriptProperty]
		[Display(Name="minCycleLength", Description="Minimum cycle length range", Order=1, GroupName="Parameters")]
		public int minCycleLength
		{ get; set; }
		
		[Range(10, 291)]
		[NinjaScriptProperty]
		[Display(Name="maxCycleLength", Description="Maximzm cycle length range", Order=2, GroupName="Parameters")]
		public int maxCycleLength
		{ get; set; }
		
		[NinjaScriptProperty]
		[Display(Name="API KEY", Description="WTT API key", Order=3, GroupName="WhenToTrade")]
		public string apiKey
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> DominantCyclePhase
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
		private WTTCyclePhaseScore[] cacheWTTCyclePhaseScore;
		public WTTCyclePhaseScore WTTCyclePhaseScore(int minCycleLength, int maxCycleLength, string apiKey)
		{
			return WTTCyclePhaseScore(Input, minCycleLength, maxCycleLength, apiKey);
		}

		public WTTCyclePhaseScore WTTCyclePhaseScore(ISeries<double> input, int minCycleLength, int maxCycleLength, string apiKey)
		{
			if (cacheWTTCyclePhaseScore != null)
				for (int idx = 0; idx < cacheWTTCyclePhaseScore.Length; idx++)
					if (cacheWTTCyclePhaseScore[idx] != null && cacheWTTCyclePhaseScore[idx].minCycleLength == minCycleLength && cacheWTTCyclePhaseScore[idx].maxCycleLength == maxCycleLength && cacheWTTCyclePhaseScore[idx].apiKey == apiKey && cacheWTTCyclePhaseScore[idx].EqualsInput(input))
						return cacheWTTCyclePhaseScore[idx];
			return CacheIndicator<WTTCyclePhaseScore>(new WTTCyclePhaseScore(){ minCycleLength = minCycleLength, maxCycleLength = maxCycleLength, apiKey = apiKey }, input, ref cacheWTTCyclePhaseScore);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.WTTCyclePhaseScore WTTCyclePhaseScore(int minCycleLength, int maxCycleLength, string apiKey)
		{
			return indicator.WTTCyclePhaseScore(Input, minCycleLength, maxCycleLength, apiKey);
		}

		public Indicators.WTTCyclePhaseScore WTTCyclePhaseScore(ISeries<double> input , int minCycleLength, int maxCycleLength, string apiKey)
		{
			return indicator.WTTCyclePhaseScore(input, minCycleLength, maxCycleLength, apiKey);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.WTTCyclePhaseScore WTTCyclePhaseScore(int minCycleLength, int maxCycleLength, string apiKey)
		{
			return indicator.WTTCyclePhaseScore(Input, minCycleLength, maxCycleLength, apiKey);
		}

		public Indicators.WTTCyclePhaseScore WTTCyclePhaseScore(ISeries<double> input , int minCycleLength, int maxCycleLength, string apiKey)
		{
			return indicator.WTTCyclePhaseScore(input, minCycleLength, maxCycleLength, apiKey);
		}
	}
}

#endregion
