/* --------------------------------------------------------------------------
   Aroon_iMA_v1_0.mq4
	Aroon Oscillator based on a standard moving average (iMA) serving as a price proxy,
	finally sharpened by an Inverse Fisher Transform
	Copyright © 2013, Juergen Moeck
   -------------------------------------------------------------------------- */
#property copyright "Copyright © 2013, Juergen Moeck"
#property link      "simplex42fx@gmail.com"

#include <_simplex_nyquist.mqh>

#property  indicator_separate_window
#property  indicator_buffers 4
#property  indicator_color1 DarkOrange
#property  indicator_width1 1
#property  indicator_color2 Aqua
#property  indicator_width2 1
#property  indicator_color3 Crimson
#property  indicator_width3 1
#property  indicator_color4 ForestGreen
#property  indicator_width4 2

// Aroon parameters
extern int aroonPeriod =  5;
// iMA parameters
extern int maPeriod  =   10;
extern int maMode    =    3;
extern int priceUsed =    5;
// general parameters
extern int maxBars = 800;
extern bool showProxyFisher = true;
extern bool showPriceFisher = false;
extern bool showProxyAroon  = false;
extern bool showPriceAroon  = false;

double proxy[];			// Moving Average as a price proxy
double aroonProxy[];		// Aroon Oscillator on proxy array
double aroonPrice[];		// Aroon Oscillator on price array
double iFishPrice[];		// inverse Fisher transform of aroonPrice
double iFishProxy[];		// inverse Fisher transform of aroonProxy


/* -----------------------------------------------------------
   init
   ---------------------------------------------------------- */
int init() {
   if (maxBars >= Bars) 
      maxBars = Bars;

   IndicatorBuffers(5);
	
   SetIndexBuffer(0, aroonProxy);
   SetIndexBuffer(1, aroonPrice);
   SetIndexBuffer(2, iFishPrice);
   SetIndexBuffer(3, iFishProxy);
	
   SetIndexDrawBegin(0, Bars - maxBars + maPeriod + 1);
   SetIndexDrawBegin(1, Bars - maxBars + maPeriod + 1);
   SetIndexDrawBegin(2, Bars - maxBars + maPeriod + 1);
   SetIndexDrawBegin(3, Bars - maxBars + maPeriod + 1);
	
	if (showProxyAroon) {
		SetIndexStyle(0, DRAW_LINE, STYLE_DOT);
		SetIndexLabel(0, "AroonProxy" );
	}
	else {
		SetIndexStyle(0, DRAW_NONE);
	}

	if (showPriceAroon) {
		SetIndexStyle(1, DRAW_LINE, STYLE_DOT);
		SetIndexLabel(1, "AroonDirect" );
	}
	else {
		SetIndexStyle(1, DRAW_NONE);
	}

	if (showPriceFisher) {
		SetIndexStyle(2, DRAW_LINE, STYLE_SOLID);
		SetIndexLabel(2, "iFishPrice" );
	}
	else {
		SetIndexStyle(2, DRAW_NONE);
	}

	if (showProxyFisher) {
		SetIndexStyle(3, DRAW_LINE, STYLE_SOLID);
		SetIndexLabel(3, "iFishProxy" );
	}
	else {
		SetIndexStyle(3, DRAW_NONE);
	}
	
   SetIndexBuffer(4, proxy);
	
	string proxyName = iMA_IndexLabel( maPeriod, maMode, priceUsed );
   IndicatorDigits(0);
   IndicatorShortName("iFisher{Aroon(" + aroonPeriod + ") iMA" + proxyName + "}" );

   return(0);
}


/* -----------------------------------------------------------
   start
   ---------------------------------------------------------- */
int start(){
   double CyclePrice = 0.0;
   double aHi, aLo;
   int limit, shift;
   int countedBars = IndicatorCounted();

   if (countedBars < 0) 
		return(-1);
   limit = maxBars - aroonPeriod - 1;

   // iMA calculation
   for (shift = limit; shift >= 0; shift--) {
		proxy[shift] = iMA(NULL, 0, maPeriod, 0, maMode, priceUsed, shift);
   }
	
   // Aroon loop on proxy array
	for(shift=limit; shift>=0; shift--) {
      aHi = getHighestIndex(proxy, aroonPeriod, shift);
      aLo = getLowestIndex (proxy, aroonPeriod, shift);
      aroonProxy[shift-aroonPeriod+1] = 100.0 * (aLo - aHi) / aroonPeriod;
   }
	
   // inverse Fisher transform loop on proxy Aroon
	for(shift=limit; shift>=0; shift--) {
      iFishProxy[shift] = 100.0 * InFisher(aroonProxy[shift]);
   }
	
   // Aroon loop on prices directly
   for(shift=limit; shift>=0; shift--) {
      aHi = iHighest(NULL, 0, MODE_HIGH, aroonPeriod, shift);
      aLo = iLowest(NULL, 0, MODE_LOW, aroonPeriod, shift);
      aroonPrice[shift] = 100.0 * (aLo - aHi) / aroonPeriod;
   }
	
   // inverse Fisher transform loop on direct Aroon
	for(shift=limit; shift>=0; shift--) {
      iFishPrice[shift] = 100.0 * InFisher(aroonPrice[shift]);
   }
	
   return(0);
}


/* --------------------------------------------------------------------------
   Copyright (c) Juergen Moeck, 2013
   END OF PROGRAM FILE
   -------------------------------------------------------------------------- */

/* Following just some comment templates ... */

/* -----------------------------------------------------------
   ...
   ----------------------------------------------------------- */

// -----------------------------------------------------------
//
// -----------------------------------------------------------