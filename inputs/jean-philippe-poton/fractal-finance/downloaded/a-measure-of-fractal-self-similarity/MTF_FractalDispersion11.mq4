
//+------------------------------------------------------------------------------------------------------------------+
//|                                                                              MTF_FractalDispersion11.mqh            |
//|                                                                              jppoton [jppoton@yahoo.com]         |
//|                                                                                                                  |
//|                                                                                                                  | 
//|  This indicator provides with an estimation of the dispersion of several timeframes'Fractal Dimensions (computed |
//|  by FGDI.mq4) around the value of the fractal dimension taken from the longest timeframe.                        |  
//|  It is pretty obvious why the dipersion is taken around this value and not around the mean for instance, anyway, |
//|  I provide all the theoretical details and justifications on my blog (http://fractalfinance.blogspot.com/).      |                                                       |
//|                                                                                                                  |
//|  The TimeFrames covered are from 5mn to the day (i.e. 5,15,30,60,240,1440), any of these TimeFrame can be        |
//|  excluded (by setting its weight to 0) or weighted to make one TimeFrame more significant, by default, all       |
//|  the weights (which must be integer) are set to 1.                                                               | 
//|                                                                                                                  |
//|                                                                                                                  |   
//|  HOW TO USE INPUT PARAMETERS :                                                                                   |   
//|  -----------------------------                                                                                   |   
//|                                                                                                                  |   
//|      1) e_period [ integer >= 1 ]                                              =>  30                            |   
//|                                                                                                                  |   
//|         The indicator will compute the historical market volatility over this period.                            |   
//|         Choose its value according to the average of trend lengths, within the TF you are trading in.            |   
//|                                                                                                                  |   
//|      2) e_type_data [ int = {PRICE_CLOSE = 0,                                                                    |   
//|                              PRICE_OPEN  = 1,                                                                    |   
//|                              PRICE_HIGH  = 2,                                                                    |   
//|                              PRICE_LOW   = 3,                                                                    |   
//|                              PRICE_MEDIAN    (high+low)/2              = 4,                                      |   
//|                              PRICE_TYPICAL   (high+low+close)/3        = 5,                                      |   
//|                              PRICE_WEIGHTED  (high+low+close+close)/4  = 6}    => PRICE_CLOSE                    |   
//|                                                                                                                  |   
//|         Defines on which price type the Fractal Dimension is computed.                                           |   
//|                                                                                                                  |
//|      3) M5w                                                                    => 1                              |
//|      4) M15w                                                                   => 1                              |
//|      5) M30w                                                                   => 1                              |
//|      6) M60w                                                                   => 1                              |
//|      7) M240w                                                                  => 0                              | 
//|      8) M1440w                                                                 => 0                              |
//|         Defines the weights to be applied to the given timeframe value of the fractal dimension                  |   
//|                                                                                                                  |   
//| v1.1 - April 2010                                                                                                |   
//+------------------------------------------------------------------------------------------------------------------+
#property link      "jppoton@yahoo.com"
//---
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_color1 Orange
#property indicator_width1 2
//************************************************************
// Private vars
//************************************************************
//---- input buffer
double InputBuffer[];
//---- output buffer
double OutputBuffer[];
int N;
//************************************************************
// Constant
//************************************************************
string INDICATOR_NAME="MTF_FracDisp";
string FILENAME      ="MTF_FractalDispersion11.mq4";
//************************************************************
// Input parameters
//************************************************************
extern int    e_period      =30;
extern int    e_type_data   =PRICE_CLOSE;
extern int    M5w           =1;
extern int    M15w          =1;
extern int    M30w          =1;
extern int    M60w          =1;
extern int    M240w         =0;
extern int    M1440w        =0;
//+-----------------------------------------------------------------------+
//| FUNCTION : init                                                       |                                                                                                                                                                                                                                                      
//| Initialization function                                               |                                   
//| Check the user input parameters and convert them in appropriate types.|                                                                                                    
//+-----------------------------------------------------------------------+
int init()
  {
   // Check e_period input parameter
   if(e_period < 2 )
     {
      Alert( "[ 10-ERROR  " + FILENAME + " ] input parameter \"e_period\" must be >= 1 (" + e_period + ")" );
      return( -1 );
     }
   if(e_type_data < PRICE_CLOSE || e_type_data > PRICE_WEIGHTED )
     {
      Alert( "[ 20-ERROR  " + FILENAME + " ] input parameter \"e_type_data\" unknown (" + e_type_data + ")" );
      return( -1 );
     }
   N=M1440w+M240w+M60w+M30w+M15w+M5w;
   if (N==0||N==1) 
     {
      Alert( "At least two timeframes must be selected" );
      return(-1);
     }   
   IndicatorBuffers( 1 );
   SetIndexBuffer( 0, OutputBuffer );
   SetIndexStyle( 0, DRAW_LINE, STYLE_SOLID, 2 );
   IndicatorShortName( INDICATOR_NAME );
   SetIndexLabel( 0, INDICATOR_NAME );
   SetIndexDrawBegin( 0, 2 * e_period );  
//----
   return(0);
  }
//+------------------------------------------------------------------+
//| FUNCTION : deinit                                                |
//| Custor indicator deinitialization function                       |
//+------------------------------------------------------------------+
int deinit()
  {
   return(0);
  }
//+------------------------------------------------------------------+
//| FUNCTION : start                                                 |
//| This callback is fired by metatrader for each tick               |
//+------------------------------------------------------------------+
int start()
  {
   int counted_bars = IndicatorCounted();
   if(counted_bars < 0)  return(-1);
   if(counted_bars > 0)   counted_bars--;
   int limit = Bars - counted_bars;
   if(counted_bars==0) limit-=1+e_period;
   
   _computeLastNbBars(limit);
//----
   return( 0 );
  }
//+================================================================================================================+
//+=== FUNCTION : _computeLastNbBars                                                                            ===+
//+===                                                                                                          ===+
//+===                                                                                                          ===+
//+=== This callback is fired by metatrader for each tick                                                       ===+
//+===                                                                                                          ===+
//+=== In :                                                                                                     ===+
//+===    - lastBars : these "n" last bars must be repainted                                                    ===+
//+===                                                                                                          ===+
//+================================================================================================================+
double TmpArray[];
//+------------------------------------------------------------------+
//| FUNCTION : _computeLastNbBars                                    |
//| This callback is fired by metatrader for each tick               |
//| In : - lastBars : these "n" last bars must be repainted          | 
//+------------------------------------------------------------------+
void _computeLastNbBars( int lastBars )
  {
   int pos;
   switch( e_type_data )
     {
      case PRICE_CLOSE    : ArrayCopy(TmpArray,Close,0,0,WHOLE_ARRAY); FractalDispersion( lastBars, TmpArray ); break;
      case PRICE_OPEN     : ArrayCopy(TmpArray,Open,0,0,WHOLE_ARRAY); FractalDispersion( lastBars, TmpArray ); break;
      case PRICE_HIGH     : ArrayCopy(TmpArray,High,0,0,WHOLE_ARRAY); FractalDispersion( lastBars, TmpArray ); break;
      case PRICE_LOW      : ArrayCopy(TmpArray,Low,0,0,WHOLE_ARRAY); FractalDispersion( lastBars, TmpArray ); break;
      case PRICE_MEDIAN   :
         for( pos=lastBars; pos>=0; pos--)InputBuffer[pos]=(High[pos]+Low[pos])/2.0; FractalDispersion( lastBars, InputBuffer );
         break;
      case PRICE_TYPICAL  :
         for( pos=lastBars; pos>=0; pos--)InputBuffer[pos]=(High[pos]+Low[pos]+Close[pos])/3.0; FractalDispersion( lastBars, InputBuffer );
         break;
      case PRICE_WEIGHTED :
         for( pos=lastBars; pos>=0; pos--)InputBuffer[pos]=(High[pos]+Low[pos]+Close[pos]+Close[pos])/4.0; FractalDispersion( lastBars, InputBuffer );
         break;
      default :
         Alert( "[ 20-ERROR  " + FILENAME + " ] the imput parameter e_type_data <" + e_type_data + "> is unknown" );
     }
  }
//+------------------------------------------------------------------+
//| FUNCTION : FractalDispersion                                     |
//| Compute the dispersion of the fractal dimensions around the      | 
//| chosen TimeFrame from input data.                                |
//| In :                                                             |
//|    - lastBars : these "n" last bars must be repainted            |
//|    - inputData : data array on which the FGDI will be applied     |
//+------------------------------------------------------------------+
void FractalDispersion( int lastBars, double &inputData[] )
  {
   int    pos;
   double M5fdi[];
   double M15fdi[];
   double M30fdi[];
   double M60fdi[];
   double M240fdi[];
   double M1440fdi[];
   double M5dev,M15dev,M30dev,M60dev,M240dev,M1440dev,sigma;
   
   int size=lastBars*288;
   
   ArrayResize(M5fdi,size);
   ArrayResize(M15fdi,size);
   ArrayResize(M30fdi,size);
   ArrayResize(M60fdi,size);
   ArrayResize(M240fdi,size);
   ArrayResize(M1440fdi,size);
   
//----
   for( pos=lastBars; pos>=0; pos-- )
     {
//----Calculation of the fractal dimension on all the timeframes and storage of their values in M_fdi[] arrays
      if (iCustom(Symbol(),5,"FGDI",e_period,e_type_data,1.5,0,pos)==EMPTY_VALUE)
         {M5fdi[pos]=iCustom(Symbol(),5,"FGDI",e_period,e_type_data,1.5,1,pos);}
         else
         {M5fdi[pos]=iCustom(Symbol(),5,"FGDI",e_period,e_type_data,1.5,0,pos);}
      
      if (iCustom(Symbol(),15,"FGDI",e_period,e_type_data,1.5,0,pos)==EMPTY_VALUE)
         {M15fdi[pos]=iCustom(Symbol(),15,"FGDI",e_period,e_type_data,1.5,1,pos);}
         else
         {M15fdi[pos]=iCustom(Symbol(),15,"FGDI",e_period,e_type_data,1.5,0,pos);}
      
      if (iCustom(Symbol(),30,"FGDI",e_period,e_type_data,1.5,0,pos)==EMPTY_VALUE)
         {M30fdi[pos]=iCustom(Symbol(),30,"FGDI",e_period,e_type_data,1.5,1,pos);}
         else
         {M30fdi[pos]=iCustom(Symbol(),30,"FGDI",e_period,e_type_data,1.5,0,pos);}
      
      if (iCustom(Symbol(),60,"FGDI",e_period,e_type_data,1.5,0,pos)==EMPTY_VALUE)
         {M60fdi[pos]=iCustom(Symbol(),60,"FGDI",e_period,e_type_data,1.5,1,pos);}
         else
         {M60fdi[pos]=iCustom(Symbol(),60,"FGDI",e_period,e_type_data,1.5,0,pos);}
      
      if (iCustom(Symbol(),240,"FGDI",e_period,e_type_data,1.5,0,pos)==EMPTY_VALUE)
         {M240fdi[pos]=iCustom(Symbol(),240,"FGDI",e_period,e_type_data,1.5,1,pos);}
         else
         {M240fdi[pos]=iCustom(Symbol(),240,"FGDI",e_period,e_type_data,1.5,0,pos);}
      if (iCustom(Symbol(),1440,"FGDI",e_period,e_type_data,1.5,0,pos)==EMPTY_VALUE)
         {M1440fdi[pos]=iCustom(Symbol(),1440,"FGDI",e_period,e_type_data,1.5,1,pos);}
         else
         {M1440fdi[pos]=iCustom(Symbol(),1440,"FGDI",e_period,e_type_data,1.5,0,pos);}          
     
//------------------------------------------------------------------------------------------------------
//----Calculation of the deviation between the fractal dimensions of different timeframes, this 
//----necessitates to shift the indexes between different arrays in order to have homogeneous values of
//----the fractal dimension, i.e, values that correspond to the same instant.
//------------------------------------------------------------------------------------------------------         
      if (M1440w>0)
         {M5dev=M5w*MathPow(M5fdi[pos*288]-M1440fdi[pos],2);
          M15dev=M15w*MathPow(M15fdi[pos*96]-M1440fdi[pos],2);
          M30dev=M30w*MathPow(M30fdi[pos*48]-M1440fdi[pos],2);
          M60dev=M60w*MathPow(M60fdi[pos*24]-M1440fdi[pos],2);
          M240dev=M240w*MathPow(M240fdi[pos*6]-M1440fdi[pos],2);
          M1440dev=0.0;}
      else if (M240w>0)
              {M5dev=M5w*MathPow(M5fdi[pos*48]-M240fdi[pos],2);
               M15dev=M15w*MathPow(M15fdi[pos*16]-M240fdi[pos],2);
               M30dev=M30w*MathPow(M30fdi[pos*8]-M240fdi[pos],2);
               M60dev=M60w*MathPow(M60fdi[pos*4]-M240fdi[pos],2);
               M240dev=0.0;
               M1440dev=0.0;}
           else if (M60w>0)
                   {M5dev=M5w*MathPow(M5fdi[pos*12]-M60fdi[pos],2);
                    M15dev=M15w*MathPow(M15fdi[pos*4]-M60fdi[pos],2);
                    M30dev=M30w*MathPow(M30fdi[pos*2]-M60fdi[pos],2);
                    M60dev=0.0;
                    M240dev=0.0;
                    M1440dev=0.0;}
                else if (M30w>0)
                        {M5dev=M5w*MathPow(M5fdi[pos*6]-M30fdi[pos],2);
                         M15dev=M15w*MathPow(M15fdi[pos*2]-M30fdi[pos],2);
                         M30dev=0.0;
                         M60dev=0.0;
                         M240dev=0.0;
                         M1440dev=0.0;}
                     else if (M15w>0)
                             {M5dev=M5w*MathPow(M5fdi[pos*3]-M15fdi[pos],2);
                              M15dev=0.0;
                              M30dev=0.0;
                              M60dev=0.0;
                              M240dev=0.0;
                              M1440dev=0.0;}
                          else 
                             {return;}
      if (N>1)                            
         {sigma=MathSqrt((M5dev+M15dev+M60dev+M240dev+M1440dev)/(N-1));}
         else
         {sigma=0;}   
      
      OutputBuffer[pos]=10*sigma;   
     } 
  }

