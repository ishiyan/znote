/* --------------------------------------------------------------
	StochRSI_on_Nyquist_v1_0.mq4
	Stochastic RSI Oscillator based on a Nyquist moving average serving as a price proxy,
	finally sharpened by an Inverse Fisher Transform.
	Copyright © 2013, Juergen Moeck
	--------------------------
	Nyquist Shannon Algorithm published in:
	Dr. Manfred G. Dürschner: Moving Averages 3.0, 2011
	Source: http://www.vtad.de/sites/files/forschung/M_Duerschner_Gleitende_Durchschnnitte_3.pdf
	Background: http://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem
-------------------------------------------------------------- */
#property copyright "Copyright © 2013, Juergen Moeck"
#property link      "simplex42fx@gmail.com"

#include <_simplex_nyquist.mqh>

#property indicator_separate_window 
#property indicator_buffers 1
#property indicator_color1 CornflowerBlue
#property indicator_width1 2

extern int 		rsiPeriod    		=    5;  // RSI period
extern int 		stochPeriod  		=    3;  // stochastic fastK period
extern int 		priPeriod 			=    0;	// iMA period (primary) 0: set default
extern int 		secPeriod 			=    8;	// Nyquist period (secondary)
extern int 		maMode    			=    3;
extern int     priceUsed         =    5;  // priceUsed Mode  ( 0...6 ) 
extern bool		useFisher			= true;  // use inverse Fisher transform
extern bool		useProxy 			= true;  // use price proxy
extern int     indicatorShift    =    0;  // 

double     prices[];
double     rsi[];
double     stoch[];

double filter1[];		// filter of price
double filter2[];		// filter of 1st signal
double nma[];			// Nyquist Moving Average

double alpha;
int drawBegin;


/* ----------------------------------------------------
	INIT
----------------------------------------------------*/
int init() {

	int draw_begin;
	//ArraySetAsSeries ( prices, true );

	checkNyquistPeriods( priPeriod, secPeriod );
	alpha = getNyquistAlpha(priPeriod, secPeriod);
	
	// indicator buffers mapping
   IndicatorBuffers ( 5 ) ;
   SetIndexBuffer ( 0, stoch ) ;
   SetIndexBuffer ( 1, rsi ) ;
   SetIndexBuffer ( 2, prices ) ;
   SetIndexBuffer ( 3, filter1 ) ;
   SetIndexBuffer ( 4, filter2 ) ;

   SetIndexStyle ( 0, DRAW_LINE ) ;

   draw_begin = priPeriod + secPeriod;
   SetIndexDrawBegin ( 0, draw_begin ) ;
   SetIndexShift ( 0, indicatorShift ) ;

   IndicatorDigits ( 2 ) ;
	
   string fisherName, proxyName;
	if (useFisher)	
		fisherName = "iFisher ";
	else
		fisherName = "";
	if (useProxy)	
		proxyName = " on Nyquist" + nyquistIndexLabel( priPeriod, secPeriod, priceUsed );
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

   // 1st filter
	for (shift = limit; shift >= 0; shift--) {
      filter1[shift] = iMA(NULL, 0, priPeriod, 0, maMode, priceUsed, shift);
      //filter1[shift] = iMA(NULL, timeFrame, priPeriod, 0, maMode, priceUsed, shift);
   }
	
   // 2nd filter based on 1st one
   for (shift = limit; shift >= 0; shift--) {
      filter2[shift] = iMAOnArray(filter1, 0, secPeriod, 0, maMode, shift);
   }
	
   // Nyquist calculation
   for (shift = limit; shift >= 0; shift--) {
		// calculate price array
		if (useProxy)
			prices[shift] = getNyquistMA( alpha, filter1[shift], filter2[shift] );
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