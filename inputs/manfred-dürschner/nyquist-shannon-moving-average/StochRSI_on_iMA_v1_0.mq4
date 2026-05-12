/* --------------------------------------------------------------
	StochRSI_on_iMA_v1_0.mq4
	Stochastic RSI Oscillator based on a standard moving average (iMA) 
	serving as a price proxy, finally sharpened by an Inverse Fisher Transform.
	Copyright © 2013, Juergen Moeck
-------------------------------------------------------------- */
#property copyright "Copyright © 2013, Juergen Moeck"
#property link      "simplex42fx@gmail.com"

#include <_simplex_nyquist.mqh>

#property indicator_separate_window 
#property indicator_buffers 1
#property indicator_color1 ForestGreen
#property indicator_width1 2

extern int     rsiPeriod         =    5;  // RSI period
extern int     stochPeriod       =    3;  // stochastic fastK period
extern int 		maPeriod 			=   15;		// iMA period (primary) 0: set default
extern int 		maMode    			=    3;
extern int     priceUsed         =    5;  // priceUsed Mode  ( 0...6 ) 
extern bool		useFisher			= true;  // use inverse Fisher transform
extern bool		useProxy 			= true;  // use price proxy
extern int     indicatorShift    =    0;  // 

double     prices[];
double     rsi[];
double     stoch[];


/* ----------------------------------------------------
	init
----------------------------------------------------*/
int init() {

	int draw_begin;

	// indicator buffers mapping
   IndicatorBuffers ( 3 ) ;
   SetIndexBuffer ( 0, stoch ) ;
   SetIndexBuffer ( 1, rsi ) ;
   SetIndexBuffer ( 2, prices ) ;

   SetIndexStyle ( 0, DRAW_LINE ) ;

   draw_begin = maPeriod;
   SetIndexDrawBegin ( 0, draw_begin ) ;
   SetIndexShift ( 0, indicatorShift ) ;

   IndicatorDigits ( 2 ) ;
	
   string fisherName, proxyName;
	if (useFisher)	
		fisherName = "iFisher ";
	else
		fisherName = "";
	if (useProxy)	
		proxyName = " on iMA" + iMA_IndexLabel( maPeriod, maMode, priceUsed );
	else
		proxyName = GetPriceStringStd( priceUsed, "[", "]", true );
	IndicatorShortName ( fisherName + "StochRSI(" + rsiPeriod + ", " + stochPeriod + ")" + proxyName  ) ;

   return ( 0 ) ;
}


/* ----------------------------------------------------
	START
----------------------------------------------------*/
int start (  ) {
   int limit,shift,i;
   int counted_bars = IndicatorCounted();
	
   if ( counted_bars>0 ) 
		counted_bars--;
   limit = Bars - counted_bars;

   // iMA calculation
   for (shift = limit; shift >= 0; shift--) {
		// calculate price array
		if (useProxy)
			prices[shift] = iMA(NULL, 0, maPeriod, 0, maMode, priceUsed, shift);
		else
			prices[shift] = iMA(NULL, 0, 1, 0, MODE_SMA, priceUsed, shift);
   }
	
   // RSI loop
	for ( shift=limit; shift>=0; shift-- ) {
		rsi[shift] = 2.0 * iRSIOnArray ( prices, 0, rsiPeriod, shift ) - 100.0;
	}

   // Stochastic loop
	for ( shift=limit; shift>=0; shift-- ) {
		if (useFisher)
			stoch[shift] = 100.0 * InFisher( getStochOnArray(rsi, stochPeriod, shift) )  ;
		else
			stoch[shift] = getStochOnArray(rsi, stochPeriod, shift);
	}
   return ( 0 ) ;
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