/* --------------------------------------------------------------------------
   NyquistMA_v1_0.mq4
	Double Smoothed Moving Average according to Nyquist-Shannon-Theorem
   Copyright (c) Juergen Moeck, 2013
   -----------
	Nyquist Shannon Algorithm published in:
	Dr. Manfred G. Dürschner: Moving Averages 3.0, 2011
	Source: http://www.vtad.de/sites/files/forschung/M_Duerschner_Gleitende_Durchschnnitte_3.pdf
	Background: http://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem
   -----------
	Code of initBuffer_1() based on an idea of Witold Wozniak, http://www.mqlsoft.com
   -------------------------------------------------------------------------- */
#property copyright "Copyright © 2013, Juergen Moeck"
#property link      "simplex42fx@gmail.com"

#include <_simplex_nyquist.mqh>

#property indicator_chart_window
#property indicator_buffers 3
#property indicator_color1 ForestGreen
#property indicator_color2 Gray
#property indicator_color3 DarkGray
#property indicator_width1  2
#property indicator_width2  1
#property indicator_width3  1

extern int priPeriod =   0;		// iMA period (primary) 0: set default
extern int secPeriod =   8;		// Nyquist period (secondary)
extern int priceUsed =   0;
extern int maMode    =   3;
extern bool showPrimary = false;

double filter1[];		// filter of price
double filter2[];		// filter of 1st signal
double nma[];			// Nyquist Moving Average

double alpha;
int drawBegin;


/* -----------------------------------------------------------
   init
   ---------------------------------------------------------- */
int init() {

	checkNyquistPeriods( priPeriod, secPeriod );
	alpha = getNyquistAlpha(priPeriod, secPeriod);
	
	int buffers = 0;
   drawBegin = priPeriod;
   buffers = initBuffer_1(buffers, nma, drawBegin, "Nyq(" + getMAString(maMode) + ", " + GetPriceStringStd(priceUsed) + ", " + secPeriod + ")", DRAW_LINE);
   if (showPrimary) {
		buffers = initBuffer_1(buffers, filter1, drawBegin, "iMA(" + GetPriceStringStd(priceUsed) + "|" + priPeriod + ")", DRAW_LINE);
		buffers = initBuffer_1(buffers, filter2, drawBegin, "iMA 2nd", DRAW_LINE);
	}
   else {
		buffers = initBuffer_1(buffers, filter1, drawBegin, "");
		buffers = initBuffer_1(buffers, filter2, drawBegin, "");
	}
   IndicatorBuffers(buffers);
   IndicatorShortName("Nyquist MA(" + priPeriod + ")");
   IndicatorDigits ( 5 ) ;
	
	return(0);
}


/* -----------------------------------------------------------
   start
   ---------------------------------------------------------- */
int start() {
   if (Bars <= drawBegin) return(0);

   int countedBars = IndicatorCounted();
   if (countedBars < 0) 
		return(-1);
   if (countedBars > 0) 
		countedBars--;
   int shift, limit = Bars - countedBars - 1;

   // 1st filter
	for (shift = limit; shift >= 0; shift--) {
      filter1[shift] = iMA(NULL, 0, priPeriod, 0, maMode, priceUsed, shift);
   }
	
   // 2nd filter based on 1st one
   for (shift = limit; shift >= 0; shift--) {
      filter2[shift] = iMAOnArray(filter1, 0, secPeriod, 0, maMode, shift);
   }
	
   // Nyquist calculation
   for (shift = limit; shift >= 0; shift--) {
      nma[shift] = getNyquistMA( alpha, filter1[shift], filter2[shift] );
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