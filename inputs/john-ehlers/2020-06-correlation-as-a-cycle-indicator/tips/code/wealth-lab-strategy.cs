Wealth-Lab strategy code (C#):
using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;
using TASCIndicators;

namespace WealthLab.Strategies
{
	public class TASC2020_06 : WealthScript
	{
		private StrategyParameter paramShort;
		private StrategyParameter paramStop;

		public TASC2020_06()
		{
			paramShort = CreateParameter("Short enabled", 0, 0, 1, 1);
			paramStop = CreateParameter("S/L %", 10, 5, 30, 5);
		}

		protected override void Execute()
		{
			var ca = CorrelationAngle.Series(Close, 14, 0);
			var State = new DataSeries(Close, "BinaryWave");
			bool shortTrades = paramShort.ValueInt == 1;
			var stopLoss = paramStop.Value;

			for(int bar = GetTradingLoopStartBar( 20 ); bar < Bars.Count; bar++)
			{
				bool upTrend = false, downTrend = false;
				/* Compute and plot market state */
				if (bar > 0)
				{
					if (Math.Abs(ca[bar] - ca[bar - 1]) < 9 && ca[bar] < 0)
						State[bar] = -1;
					if (Math.Abs(ca[bar] - ca[bar - 1]) < 9 && ca[bar] >= 0)
						State[bar] = 1;

					upTrend = State[bar] == 1 && State[bar-1] == 1;
					downTrend = State[bar] == -1 && State[bar-1] == -1;
				}

				if(upTrend)
					SetBackgroundColor(bar, Color.FromArgb(30, Color.Green));
				if (downTrend)
					SetBackgroundColor(bar, Color.FromArgb(30, Color.Red));
				
				if (IsLastPositionActive)
				{
					Position p = LastPosition;
					
					if (!ExitAtStop(bar + 1, p, p.RiskStopLevel, 
						string.Format("SL {0}%", stopLoss)))
					{	
						if (p.PositionType == PositionType.Long)
						{
							switch (p.EntrySignal)
							{
								case "Breakout":
									if (downTrend)
										SellAtMarket(bar + 1, p, "Trend change");
								else
									SellAtStop(bar + 1, p, Lowest.Series(Low, 20)[bar]); 
								break;
								case "Dip buy": 
									SellAtLimit(bar + 1, p, Highest.Series(High, 5)[bar]); break;
								default: break;
							}
						}
						else
						{
							CoverAtStop(bar + 1, p, Highest.Series(High, 10)[bar]);
						}
					}
				}
				else
				{
					if (bar > 0)
					{
						RiskStopLevel = Close[bar] * (1 - (stopLoss / 100d));
						if (upTrend) {
							BuyAtStop(bar + 1, Highest.Series(High, 20)[bar], "Breakout");
						}
						else
						if (downTrend && shortTrades) {
							ShortAtStop(bar + 1, Lowest.Series(Low, 10)[bar], "Breakdown");
						}
						else {
							BuyAtLimit(bar + 1, Low[bar] * 0.95, "Dip buy");
						}
					}
				}
			}
			
			ChartPane paneCA = CreatePane( 30,true,true);
			ChartPane paneBW = CreatePane( 30,false,true);
			PlotSeries( paneCA,ca,Color.DarkBlue,LineStyle.Solid,2);
			PlotSeries( paneBW,State,Color.DarkBlue,LineStyle.Solid,2);
			DrawHorzLine( paneCA,0,Color.DarkCyan,LineStyle.Solid,2);
			DrawHorzLine( paneBW,0,Color.DarkCyan,LineStyle.Solid,2);
			HideVolume();
		}
	}
}
