/* --------------------------------------------------------------------------
   Aroon_Nyquist_v1_0.mq4
	Aroon Oscillator based on a Nyquist moving average serving as a price proxy,
	finally sharpened by an Inverse Fisher Transform
	Copyright © 2013, Juergen Moeck
   -----------
	Nyquist Shannon Algorithm published in:
	Dr. Manfred G. Dürschner: Moving Averages 3.0, 2011
	Source: http://www.vtad.de/sites/files/forschung/M_Duerschner_Gleitende_Durchschnnitte_3.pdf
	Background: http://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem
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
#property  indicator_color4 CornflowerBlue
#property  indicator_width4 2

// Aroon parameters
extern int aroonPeriod = 5;
// Nyquist parameters
extern int priPeriod =   0;		// iMA period (primary) 0: set default
extern int secPeriod =   8;		// Nyquist period (secondary)
extern int priceUsed =   0;
extern int maMode    =   3;
// general parameters
extern int maxBars = 800;
extern bool showNyquistFisher = true;
extern bool showDirectFisher  = false;
extern bool showDirectAroon   = false;
extern bool showNyquistAroon  = false;

double arOscNMA[];
double arOscDirect[];
double filter1[];		// filter of price
double filter2[];		// filter of 1st signal
double nma[];			// Nyquist Moving Average
double iFishDirect[];	// inverse Fisher transform of direct Aroon
double iFishNMA[];		// inverse Fisher transform of NMA Aroon

double alpha;
int drawBegin;


/* -----------------------------------------------------------
   init
   ---------------------------------------------------------- */
int init() {
   if (maxBars >= Bars) 
      maxBars = Bars;

	checkNyquistPeriods( priPeriod, secPeriod );
	alpha = getNyquistAlpha(priPeriod, secPeriod);
	
   IndicatorBuffers(7);
	
   SetIndexBuffer(0, arOscNMA);
   SetIndexBuffer(1, arOscDirect);
   SetIndexBuffer(2, iFishDirect);
   SetIndexBuffer(3, iFishNMA);
	
   SetIndexDrawBegin(0, Bars - maxBars + aroonPeriod + 1);
   SetIndexDrawBegin(1, Bars - maxBars + aroonPeriod + 1);
   SetIndexDrawBegin(2, Bars - maxBars + aroonPeriod + 1);
   SetIndexDrawBegin(3, Bars - maxBars + aroonPeriod + 1);
	
	if (showNyquistAroon) {
		SetIndexStyle(0, DRAW_LINE, STYLE_DOT);
		SetIndexLabel(0, "AroonNyq" );
	}
	else {
		SetIndexStyle(0, DRAW_NONE);
	}

	if (showDirectAroon) {
		SetIndexStyle(1, DRAW_LINE, STYLE_DOT);
		SetIndexLabel(1, "AroonDirect" );
	}
	else {
		SetIndexStyle(1, DRAW_NONE);
	}

	if (showDirectFisher) {
		SetIndexStyle(2, DRAW_LINE, STYLE_SOLID);
		SetIndexLabel(2, "iFishDirect" );
	}
	else {
		SetIndexStyle(2, DRAW_NONE);
	}

	if (showNyquistFisher) {
		SetIndexStyle(3, DRAW_LINE, STYLE_SOLID);
		SetIndexLabel(3, "iFishNyq" );
	}
	else {
		SetIndexStyle(3, DRAW_NONE);
	}
	
   SetIndexBuffer(4, filter1);
   SetIndexBuffer(5, filter2);
   SetIndexBuffer(6, nma);
	
   IndicatorDigits(0);
   IndicatorShortName("iFisher{Aroon(" + aroonPeriod + ") Nyquist" + nyquistIndexLabel( priPeriod, secPeriod, priceUsed ) + "}" );

   return(0);
}


/* -----------------------------------------------------------
   start
   ---------------------------------------------------------- */
int start(){
   //double ArOsc, HighBar = 0, LowBar = 0;
   double aHi, aLo;
   int limit, shift;
   int countedBars = IndicatorCounted();

   if (countedBars < 0) 
		return(-1);
   limit = maxBars - aroonPeriod - 1;

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
	
   // Aroon loop on Nyquist MA
	for(shift=limit; shift>=0; shift--) {
      aHi = getHighestIndex(nma, aroonPeriod, shift);
      aLo = getLowestIndex (nma, aroonPeriod, shift);
      arOscNMA[shift-aroonPeriod+1] = 100.0 * (aLo - aHi) / aroonPeriod;
   }
	
   // inverse Fisher transform loop on Nyquist Aroon
	for(shift=limit; shift>=0; shift--) {
      iFishNMA[shift] = 100.0 * InFisher(arOscNMA[shift]);
   }
	
   // Aroon loop on prices directly
   for(shift=limit; shift>=0; shift--) {
      aHi = iHighest(NULL, 0, MODE_HIGH, aroonPeriod, shift);
      aLo = iLowest(NULL, 0, MODE_LOW, aroonPeriod, shift);
      arOscDirect[shift] = 100.0 * (aLo - aHi) / aroonPeriod;
   }
	
   // inverse Fisher transform loop on direct Aroon
	for(shift=limit; shift>=0; shift--) {
      iFishDirect[shift] = 100.0 * InFisher(arOscDirect[shift]);
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