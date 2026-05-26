C# code:

using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using WealthLab;
using WealthLab.Indicators;
using TASCIndicators;	// The EC filter and Least Error

namespace WealthLab.Strategies
{
	public class ZeroLag1011 : WealthScript
	{
		private StrategyParameter paramLength;
		private StrategyParameter paramGain;
		private StrategyParameter paramThresh;
		
		public ZeroLag1011()
		{
			paramLength = CreateParameter("Length", 32, 2, 100, 1);
			paramGain = CreateParameter("Gain Limit", 22, 2, 100, 1);
			paramThresh = CreateParameter("Threshold", 0.75, 0.5, 2, 0.25);
		}
		
		protected override void Execute()
		{
			int Length = paramLength.ValueInt;
			int GainLimit = paramGain.ValueInt;
			double Thresh = paramThresh.Value;
			
			// Data series
			EMA ema = EMA.Series( Close, Length, EMACalculation.Modern );
			EC ec = EC.Series( Close, Length, GainLimit );
			LeastError le = LeastError.Series( Close, Length, GainLimit );
			
			SetBarColors( Color.LimeGreen, Color.OrangeRed );
			
			// This EMA-based indicator is "unstable": allow it to stabilize
			for(int bar = Length * 3; bar < Bars.Count; bar++)
			{
				SetBackgroundColor( bar, Color.Black );
				
				// Detect crossover/crossunder and LeastError above threshold
				bool maXo = CrossOver( bar, ec, ema ) & ( le[bar] > Thresh );
				bool maXu = CrossUnder( bar, ec, ema ) & ( le[bar] > Thresh );
					
				// The initial trade
				if (Positions.Count == 0){
					if ( maXo ) 
						BuyAtMarket( bar + 1 );
					else if( maXu )
						ShortAtMarket( bar + 1 );
				}
					// All subsequent trades of the SAR system
				else 
				{
					Position p = LastPosition;	
					if ( p.PositionType == PositionType.Long )  {
						if ( maXu )  {
							SellAtMarket( bar + 1, p );
							ShortAtMarket( bar + 1 );
						}
					}
					else  {
						if ( maXo ) {
							CoverAtMarket( bar + 1, p );
							BuyAtMarket( bar + 1 );
						}
					}
				}	
			}
			
			// Plotting the EC, EMA, and Least Error
			WealthLab.LineStyle solid = LineStyle.Solid;
			PlotSeries( PricePane, ec, Color.Gold, solid, 1 );
			PlotSeries( PricePane, ema, Color.Red, solid, 1 );
			ChartPane lePane = CreatePane( 30,true,true );
			PlotSeries( lePane, le, Color.LimeGreen, solid, 2 );
			DrawHorzLine( lePane, Thresh, Color.Blue, LineStyle.Dashed, 2 );
			HideVolume();
		}
	}
}

