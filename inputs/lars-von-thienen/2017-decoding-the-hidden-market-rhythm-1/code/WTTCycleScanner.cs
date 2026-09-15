// 
// Copyright (C) 2017, WhenToTrade.com
// www.whentotrade.com
// Info: You must use a valid WTT API key to run this script
// Info: Ensure that the Newtonsoft DLL is available
// Book: Decoding The Hidden Market Rhythm - Part 1 (2017)
// Chapter 2: How to detect cycles
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
	using System.Net.Http;
	using Newtonsoft.Json; // Additional reference to package needed
	
	public class WTTCycleScanner : Indicator
	{
			
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"WhenToTrade.com Cycle Scanner";
				Name										= "WTT Cycle Scanner";
				Calculate									= Calculate.OnBarClose;
				IsOverlay									= true;
				//Disable this property if your indicator requires custom values that cumulate with each new market data event. 
				//See Help Guide for additional information.
				IsSuspendedWhileInactive					= true;
				AmplitudeMulti					= 1;
				BartelsLimit					= 49;
				MinCycleLength					= 5;
				MaxCycleLength					= 300;
				SortByStrength					= true;
				Api_Key					= string.Empty;
			}
			else if (State == State.Configure)
			{
			}
		}

		protected override void OnBarUpdate()
		{
			if (Count - 2 == CurrentBar) //start cycle scanner on last finished, closed bar
			{
					string APIresultContent="";
				
					//Get and prepare the close data array
		            int seriesCount = Close.Count - 1;
		            List<double> closeList = new List<double>();
		            for (int i = 0; i <= seriesCount; i++)
					{
						if (Time.GetValueAt(i).Date <= endDate.Date || endDate.Date==null || endDate.Date>=DateTime.MinValue)	
		                	closeList.Add(Close.GetValueAt(i));
					}
											
				    //Call the WhenToTrade Cycles API endpoint POST CycleScanner
					using (var client = new HttpClient())
		            {
						//WhenToTrade API URL
		                client.BaseAddress = new Uri("https://api.marketcycles.online/");			

						//Load the close dataset for HTTP API POST call
		                var contents = JsonConvert.SerializeObject(closeList.ToArray());
		                StringContent POSTcontent = new StringContent(contents, Encoding.UTF8, "application/json");

						//POST API CALL
		                var response = client.PostAsync("/api/CycleScanner?includeSpectrum=false&minCycleLength="+MinCycleLength+"&maxCycleLength="+MaxCycleLength+"&api_Key="+Api_Key, POSTcontent).Result;			
						
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
		            }
				
					// Decode the scanner results data from API call
					var scannerResults = JsonConvert.DeserializeObject<dynamic>(APIresultContent);
					
					// Test for return errors from API?
					string statusCode=scannerResults.StatusCode !=null ? scannerResults.StatusCode : "";
					bool error = statusCode.IndexOf("error", StringComparison.OrdinalIgnoreCase) >= 0;
					if (error)
					{
						Draw.TextFixed(this, "apierror", "API ERROR:"+statusCode, TextPosition.TopLeft);
						return;
					}
					
					//Print to script log
					Print(scannerResults.PeaksString);
					
					//Print active cycles on chart
					string activeCycles="";
					foreach(var dc in scannerResults.peaks)
					{
						activeCycles+=" "+dc.CycleLength;
					}
					var cycleLength=scannerResults.peaks[0].CycleLength;
					
					Draw.TextFixed(this, "dcinfo","Active Cycles:"+activeCycles, TextPosition.TopLeft);
			}
			
			
		}
		
		//dont show the individual API key on screen
		public override string DisplayName
		{
		  get { return Name + "("+MinCycleLength+","+MaxCycleLength+")"; }
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, double.MaxValue)]
		[Display(Name="AmplitudeMulti", Order=1, GroupName="Parameters")]
		public double AmplitudeMulti
		{ get; set; }

		[NinjaScriptProperty]
		[Range(10, int.MaxValue)]
		[Display(Name="BartelsLimit", Order=2, GroupName="Parameters")]
		public int BartelsLimit
		{ get; set; }

		[NinjaScriptProperty]
		[Range(5, int.MaxValue)]
		[Display(Name="MinCycleLength", Order=3, GroupName="Parameters")]
		public int MinCycleLength
		{ get; set; }

		[NinjaScriptProperty]
		[Range(20, int.MaxValue)]
		[Display(Name="MaxCycleLength", Order=4, GroupName="Parameters")]
		public int MaxCycleLength
		{ get; set; }

		[NinjaScriptProperty]
		[Display(Name="SortByStrength", Order=5, GroupName="Parameters")]
		public bool SortByStrength
		{ get; set; }
	
		[NinjaScriptProperty]
		[Display(Name="endDate", Description="Analysis End", Order=6, GroupName="Parameters")]
		public DateTime endDate
		{ get; set; }
		
		[NinjaScriptProperty]
		[Display(Name="Api_Key", Order=1, GroupName="WhenToTrade API")]
		public string Api_Key
		{ get; set; }
		
		#endregion

	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private WTTCycleScanner[] cacheWTTCycleScanner;
		public WTTCycleScanner WTTCycleScanner(double amplitudeMulti, int bartelsLimit, int minCycleLength, int maxCycleLength, bool sortByStrength, DateTime endDate, string api_Key)
		{
			return WTTCycleScanner(Input, amplitudeMulti, bartelsLimit, minCycleLength, maxCycleLength, sortByStrength, endDate, api_Key);
		}

		public WTTCycleScanner WTTCycleScanner(ISeries<double> input, double amplitudeMulti, int bartelsLimit, int minCycleLength, int maxCycleLength, bool sortByStrength, DateTime endDate, string api_Key)
		{
			if (cacheWTTCycleScanner != null)
				for (int idx = 0; idx < cacheWTTCycleScanner.Length; idx++)
					if (cacheWTTCycleScanner[idx] != null && cacheWTTCycleScanner[idx].AmplitudeMulti == amplitudeMulti && cacheWTTCycleScanner[idx].BartelsLimit == bartelsLimit && cacheWTTCycleScanner[idx].MinCycleLength == minCycleLength && cacheWTTCycleScanner[idx].MaxCycleLength == maxCycleLength && cacheWTTCycleScanner[idx].SortByStrength == sortByStrength && cacheWTTCycleScanner[idx].endDate == endDate && cacheWTTCycleScanner[idx].Api_Key == api_Key && cacheWTTCycleScanner[idx].EqualsInput(input))
						return cacheWTTCycleScanner[idx];
			return CacheIndicator<WTTCycleScanner>(new WTTCycleScanner(){ AmplitudeMulti = amplitudeMulti, BartelsLimit = bartelsLimit, MinCycleLength = minCycleLength, MaxCycleLength = maxCycleLength, SortByStrength = sortByStrength, endDate = endDate, Api_Key = api_Key }, input, ref cacheWTTCycleScanner);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.WTTCycleScanner WTTCycleScanner(double amplitudeMulti, int bartelsLimit, int minCycleLength, int maxCycleLength, bool sortByStrength, DateTime endDate, string api_Key)
		{
			return indicator.WTTCycleScanner(Input, amplitudeMulti, bartelsLimit, minCycleLength, maxCycleLength, sortByStrength, endDate, api_Key);
		}

		public Indicators.WTTCycleScanner WTTCycleScanner(ISeries<double> input , double amplitudeMulti, int bartelsLimit, int minCycleLength, int maxCycleLength, bool sortByStrength, DateTime endDate, string api_Key)
		{
			return indicator.WTTCycleScanner(input, amplitudeMulti, bartelsLimit, minCycleLength, maxCycleLength, sortByStrength, endDate, api_Key);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.WTTCycleScanner WTTCycleScanner(double amplitudeMulti, int bartelsLimit, int minCycleLength, int maxCycleLength, bool sortByStrength, DateTime endDate, string api_Key)
		{
			return indicator.WTTCycleScanner(Input, amplitudeMulti, bartelsLimit, minCycleLength, maxCycleLength, sortByStrength, endDate, api_Key);
		}

		public Indicators.WTTCycleScanner WTTCycleScanner(ISeries<double> input , double amplitudeMulti, int bartelsLimit, int minCycleLength, int maxCycleLength, bool sortByStrength, DateTime endDate, string api_Key)
		{
			return indicator.WTTCycleScanner(input, amplitudeMulti, bartelsLimit, minCycleLength, maxCycleLength, sortByStrength, endDate, api_Key);
		}
	}
}

#endregion
