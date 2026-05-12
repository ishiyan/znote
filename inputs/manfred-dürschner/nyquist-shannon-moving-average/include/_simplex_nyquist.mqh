/* --------------------------------------------------------------
	_simplex_nyquist.mqh
   Version 1.0
	Copyright © 2013, Juergen Moeck
   First edition: June 2013 ... ongoing ...
	-----------
	This mqh file holds functions used in following indicators:
   - NyquistMA_v1_0.mq4
   - Aroon_Nyquist_v1_0.mq4
   - Aroon_iMA_v1_0.mq4
	- StochRSI_on_Nyquist_v1_0.mq4
	- StochRSI_on_iMA_v1_0.mq4
	-----------
	Nyquist Shannon Algorithm published in:
	Dr. Manfred G. Dürschner: Moving Averages 3.0, 2011
	Source: http://www.vtad.de/sites/files/forschung/M_Duerschner_Gleitende_Durchschnnitte_3.pdf
	Background: http://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem
-------------------------------------------------------------- */
#property copyright "Copyright © 2013, Juergen Moeck"
#property link      "simplex42fx@gmail.com"


/* ----------------------------------------------------
	checkNyquistPeriods
---------------------------------------------------- */
void checkNyquistPeriods( int& _pri, int& _sec ) {
	bool al = false;
	int __pri = _pri;
	if (_pri < 4) {
		_pri = 4;
		if (__pri != 0)
			al = true;
	}
	if (_sec < 2) {
		_sec = 2;
		al = true;
	}
	if (_pri < _sec * 2) {
		_pri = _sec * 4;  // intentionally 4 - no mistyping!
		if (__pri != 0)
			al = true;
	}
	if (al)
		Alert("Nyquist periods reset to: primary: " + _pri + ", secondary: " + _sec);
	return;
}


/* ----------------------------------------------------
	getNyquistAlpha
---------------------------------------------------- */
double getNyquistAlpha( int _pri, int _sec ) {
	double out;
	double lambda = _pri / _sec;	// Dürschner, ibd. p. 16
	out  = lambda * (_pri-1) / (_pri-lambda);
	return ( out );
}


/* ----------------------------------------------------
	determine Nyquist standard index label
---------------------------------------------------- */
string nyquistIndexLabel( int per1, int per2, int pri = 99 ) {
	string out, sPrice = "";
	if (pri >= 0 && pri < 7)
		sPrice = GetPriceStringStd( pri, "", "", true );
	if (StringLen(sPrice) > 0)
		sPrice = StringConcatenate(", ", sPrice);
   out = " [" + per1 + ", " + per2 + sPrice + "]" ;
	return ( out );
}


/* ----------------------------------------------------
	getNyquistMA
---------------------------------------------------- */
double getNyquistMA( double _alpha, double _v1, double _v2 ) {
	double out;
	out = (_alpha + 1.0) * _v1 - _alpha * _v2;
	return ( out );
}


/* ----------------------------------------------------
	GetPriceStringStd
---------------------------------------------------- */
string GetPriceStringStd( int iPrice, string leftB="", string rightB="", bool showLong=false ) {
	string out;
	if (showLong) {
		switch (iPrice) {
			case 0  : out = "Close";	break;
			case 1  : out = "Open";	break;
			case 2  : out = "High";	break;
			case 3  : out = "Low";	break;
			case 4  : out = "Median";	break;
			case 5  : out = "Typical";	break;
			case 6  : out = "Weighted";	break;
			default : out = "UNKNOWN";	break;
		}
	} 
	else {
		switch (iPrice) {
			case 0  : out = "C";	break;
			case 1  : out = "O";	break;
			case 2  : out = "H";	break;
			case 3  : out = "L";	break;
			case 4  : out = "HL/2";	break;
			case 5  : out = "HLC/3";	break;
			case 6  : out = "HLCC/4";	break;
			default : out = "VOID";	break;
		}
	} 
	out = StringConcatenate(leftB, out, rightB);
	return ( out );
}


/* -----------------------------------------------------------
   initBuffer_1
   ---------------------------------------------------------- */
int initBuffer_1(int iBuffers, double& array[], int iDrawBegin, 
               string label = "", int type = DRAW_NONE, int style = EMPTY, 
					int width = EMPTY, color clr = EMPTY, int arrow = 0, double emptyVal = EMPTY_VALUE) {
	
	//if ( clr == EMPTY )
		//clr = GetBufferColor(iBuffers);
	
	SetIndexBuffer(iBuffers, array);
   SetIndexLabel(iBuffers, label);
   SetIndexEmptyValue(iBuffers, emptyVal);
   SetIndexDrawBegin(iBuffers, iDrawBegin);
   SetIndexShift(iBuffers, 0);
   //SetIndexStyle(iBuffers, type, style, width, clr);
   SetIndexStyle(iBuffers, type, style, width);
   SetIndexArrow(iBuffers, arrow);
	
	ArrayInitialize( array, 0.0);
	
   iBuffers++;
	return(iBuffers);
}


/* ----------------------------------------------------
	getMAString
---------------------------------------------------- */
string getMAString( int iMode, string leftB="", string rightB="" ) {
	string out;
	switch (iMode) {
		case 0  : out = "SMA";	break;
		case 1  : out = "EMA";	break;
		case 2  : out = "SMMA";	break;
		case 3  : out = "LWMA";	break;
		default : out = "?";	break;
	}
	out = StringConcatenate(leftB, out, rightB);
	return ( out );
}


/* -----------------------------------------------------------
	Inverse Fisher Transform
   ----------------------------------------------------------- */
double InFisher ( double x ) {
   double out;
	double y = MathExp ( 2 * x );
	if ( y == -1.0 )
		out = 0.0;
	else
		out = ( y - 1.0 ) / ( y + 1.0 );
	return ( out ); 
}


/* -----------------------------------------------------------
   getStochOnArray
	calculates Stochastics fast %k on values of a given array
   ----------------------------------------------------------- */
double getStochOnArray(double& inArray[], int stochPeriod, int i) {
	double smallest,      // smallest value
			largest,        // largest value
			fastK,          // Stochastic Fast %K
			enum,           // enumerator of fastK
			denom;          // denominator of fastK
   int 	pos=0;          // array index of min / max values
   
   pos = ArrayMinimum(inArray, stochPeriod, i);		// index with min value
   smallest = inArray[pos];
 
   pos = ArrayMaximum(inArray, stochPeriod, i);		// index with max value
   largest = inArray[pos];
 
   enum  = inArray[i] - smallest;
   denom = MathMax(0.000001, largest-smallest); 	// MathMax: avoid divide by zero
      
   fastK = (enum / denom) * 100.0;
   
   return(fastK);
}


/* ----------------------------------------------------
	determine iMA standard index label
---------------------------------------------------- */
string iMA_IndexLabel( int per, int method = 99, int pri = 99 ) {
	string out, sPrice = "", sMethod = "";
	if (pri >= 0 && pri < 7)
		sPrice = GetPriceStringStd( pri, "", "", true );
	if (method >= 0 && method < 4)
		sMethod = getMAString( method );
	if (StringLen(sPrice) > 0)
		sPrice = StringConcatenate(", ", sPrice);
	if (StringLen(sMethod) > 0)
		sMethod = StringConcatenate(", ", sMethod);
	
	out = StringConcatenate("[", per, sMethod, sPrice, "]");

	return ( out );
}


/* -----------------------------------------------------------
   getLowestIndex
   ----------------------------------------------------------- */
int getLowestIndex(double& inArray[], int depth, int offset) {
	int i, out = offset;
   if (offset - depth < 0) 
		depth = offset;
   double compare = inArray[offset];
	for (i=offset; i > offset - depth; i--) {
		if (inArray[i] < compare) {
			out = i;
			compare = inArray[i];
		}
	}
	return(out);
}


/* -----------------------------------------------------------
   getHighestIndex
   ----------------------------------------------------------- */
int getHighestIndex(double& inArray[], int depth, int offset) {
	int i, out = offset;
   if (offset - depth < 0) 
		depth = offset;
   double compare = inArray[offset];
	
	for (i=offset; i > offset - depth; i--) {
		if (inArray[i] > compare) {
			out = i;
			compare = inArray[i];
		}
	}
	return(out);
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
