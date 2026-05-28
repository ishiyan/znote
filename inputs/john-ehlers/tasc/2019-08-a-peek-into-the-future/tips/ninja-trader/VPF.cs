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
	public class VPF : Indicator
	{
		private double F1, G1, S1, SumC = 0;
		private double Bandwidth = 0.25;
		private double Order, count = 0;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"The Voss Predictive Filter indicator from August 2019 Technical Analysis of Stocks & Commodities.";
				Name										= "VPF";
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
				Period					= 20;
				Predict					= 3;
				AddPlot(Brushes.LightCoral, "Filter");
				AddPlot(Brushes.SkyBlue, "Voss");
				BarsRequiredToPlot = 0;
			}
			else if (State == State.Configure)
			{
			}
		}

		protected override void OnBarUpdate()
		{
			if(CurrentBar == 0)
			{
				Order = 3*Predict;
				F1 = Math.Cos((2*Math.PI)/Period);
				G1 = Math.Cos((Bandwidth*2*Math.PI)/Period);
				S1 = 1/G1 - Math.Sqrt(1/(G1*G1) - 1);
			}
			
			if(CurrentBar < Order)
			{
				Filter[0] = 0;
				Voss[0] = 0;
				return;
			}
			
			//Band Limit the input data with a wide bank BandPass Filter
			Filter[0] = 0.5*(1 - S1)*(Close[0] - Close[2]) + F1*(1 + S1)*Filter[1] - S1*Filter[2];
			
			SumC = 0;
			for(count = 0; count < Order; count++)
			{
				SumC += ((count + 1) / Order) * Voss[(int)(Order - count)];
			}
			Voss[0] = ((3 + Order) / 2)*Filter[0] - SumC;
		}

		#region Properties
		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Period", Order=1, GroupName="Parameters")]
		public int Period
		{ get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name="Predict", Order=2, GroupName="Parameters")]
		public int Predict
		{ get; set; }

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Filter
		{
			get { return Values[0]; }
		}

		[Browsable(false)]
		[XmlIgnore]
		public Series<double> Voss
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
		private VPF[] cacheVPF;
		public VPF VPF(int period, int predict)
		{
			return VPF(Input, period, predict);
		}

		public VPF VPF(ISeries<double> input, int period, int predict)
		{
			if (cacheVPF != null)
				for (int idx = 0; idx < cacheVPF.Length; idx++)
					if (cacheVPF[idx] != null && cacheVPF[idx].Period == period && cacheVPF[idx].Predict == predict && cacheVPF[idx].EqualsInput(input))
						return cacheVPF[idx];
			return CacheIndicator<VPF>(new VPF(){ Period = period, Predict = predict }, input, ref cacheVPF);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.VPF VPF(int period, int predict)
		{
			return indicator.VPF(Input, period, predict);
		}

		public Indicators.VPF VPF(ISeries<double> input , int period, int predict)
		{
			return indicator.VPF(input, period, predict);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.VPF VPF(int period, int predict)
		{
			return indicator.VPF(Input, period, predict);
		}

		public Indicators.VPF VPF(ISeries<double> input , int period, int predict)
		{
			return indicator.VPF(input, period, predict);
		}
	}
}

#endregion
