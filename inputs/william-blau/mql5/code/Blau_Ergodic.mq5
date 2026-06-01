//+------------------------------------------------------------------+
//|                                                 Blau_Ergodic.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // URL
#property description "Ergodic Oscillator (William Blau)"       // description
#include <WilliamBlau.mqh>                 // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window        // indicator in a separate window
#property indicator_buffers 11             // number of buffers
#property indicator_plots   2              // indicator plots
//--- horizontal levels
#property indicator_level1 -25             // level #0
#property indicator_level2 25              // level #1
#property indicator_levelcolor Silver      // level color
#property indicator_levelstyle STYLE_DOT   // level style
#property indicator_levelwidth 1           // level width
//--- min/max
#property indicator_minimum -100           // minimum
#property indicator_maximum 100            // maximum
//--- graphic plot #0 (Main)
#property indicator_label1  "Ergodic"      // graphic plot #0
#property indicator_type1   DRAW_HISTOGRAM // draw as a histogram
#property indicator_color1  Silver         // histogram color
#property indicator_style1  STYLE_SOLID    // line style
#property indicator_width1  2              // line width
//--- graphic plot #1 (Signal Line)
#property indicator_label2  "Signal"       // graphic plot #1
#property indicator_type2   DRAW_LINE      // draw as a line
#property indicator_color2  Red            // line color
#property indicator_style2  STYLE_SOLID    // line style
#property indicator_width2  1              // line width
//--- input parameters
input int    q=2;  // q - period of Momentum
input int    r=20; // r - 1st EMA, applied to Momentum
input int    s=5;  // s - 2nd EMA, applied to the 1st smoothing
input int    u=3;  // u - 3rd EMA, applied to the 2nd smoothing
input int    ul=3; // ul- period of a Signal Line
input ENUM_APPLIED_PRICE AppliedPrice=PRICE_CLOSE; // AppliedPrice - price type
//--- dynamic arrays
double MainBuffer[];        // Ergodic (graphic plot #0)
double SignalBuffer[];      // Signal line: ul-period EMA of Ergodic (graphic plot #1)
double PriceBuffer[];       // price array
double MtmBuffer[];         // q-period Momentum
double EMA_MtmBuffer[];     // r-period of the 1st EMA
double DEMA_MtmBuffer[];    // s-period of the 2nd EMA
double TEMA_MtmBuffer[];    // u-period of the 3rd EMA
double AbsMtmBuffer[];      // q-period Momentum (absolute value)
double EMA_AbsMtmBuffer[];  // r-period of the 1st EMA (absolute value)
double DEMA_AbsMtmBuffer[]; // s-period of the 2nd EMA (absolute value)
double TEMA_AbsMtmBuffer[]; // u-period of the 3rd EMA (absolute value)
//--- global variables
int    begin1, begin2, begin3, begin4, begin5; // starting indexes
int    rates_total_min; // rates total min
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- indicator buffers
   // graphic plot #0
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);                 // Ergodic
   // graphic plot #1
   SetIndexBuffer(1,SignalBuffer,INDICATOR_DATA);               // signal line: ul-period EMA of Ergodic
   // buffers for intermediate calculations
   SetIndexBuffer(2,PriceBuffer,INDICATOR_CALCULATIONS);        // price array
   SetIndexBuffer(3,MtmBuffer,INDICATOR_CALCULATIONS);          // q-period моментум
   SetIndexBuffer(4,EMA_MtmBuffer,INDICATOR_CALCULATIONS);      // r-period of the 1st EMA
   SetIndexBuffer(5,DEMA_MtmBuffer,INDICATOR_CALCULATIONS);     // s-period of the 2nd EMA
   SetIndexBuffer(6,TEMA_MtmBuffer,INDICATOR_CALCULATIONS);     // u-period of the 3rd EMA
   SetIndexBuffer(7,AbsMtmBuffer,INDICATOR_CALCULATIONS);       // q-period Momentum (absolute value)
   SetIndexBuffer(8,EMA_AbsMtmBuffer,INDICATOR_CALCULATIONS);   // r-period of the 1st EMA (absolute value)
   SetIndexBuffer(9,DEMA_AbsMtmBuffer,INDICATOR_CALCULATIONS);  // s-period of the 2nd EMA (absolute value)
   SetIndexBuffer(10,TEMA_AbsMtmBuffer,INDICATOR_CALCULATIONS); // u-period of the 3rd EMA (absolute value)
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"Ergodic");           // label of graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_TYPE,DRAW_HISTOGRAM); // draw as a histogram
   PlotIndexSetInteger(0,PLOT_LINE_COLOR,Silver);        // line color
   PlotIndexSetInteger(0,PLOT_LINE_STYLE,STYLE_SOLID);   // line style
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,2);             // line width
//--- graphic plot #1 (Signal Line)
   PlotIndexSetString(1,PLOT_LABEL,"Signal");            // label of graphic plot #1
   PlotIndexSetInteger(1,PLOT_DRAW_TYPE,DRAW_LINE);      // draw as a line
   PlotIndexSetInteger(1,PLOT_LINE_COLOR,Red);           // line color
   PlotIndexSetInteger(1,PLOT_LINE_STYLE,STYLE_SOLID);   // line style
   PlotIndexSetInteger(1,PLOT_LINE_WIDTH,1);             // line width
*/
//--- precision
   IndicatorSetInteger(INDICATOR_DIGITS,2);
/*
//--- horizontal levels
   IndicatorSetInteger(INDICATOR_LEVELS,2);                // number of indicator levels
   IndicatorSetDouble(INDICATOR_LEVELVALUE,0,-25);         // level #0
   IndicatorSetDouble(INDICATOR_LEVELVALUE,1,25);          // level #1
   IndicatorSetInteger(INDICATOR_LEVELCOLOR,Silver);       // level color
   IndicatorSetInteger(INDICATOR_LEVELSTYLE,STYLE_DOT);    // level style
   IndicatorSetInteger(INDICATOR_LEVELWIDTH,1);            // level width
   IndicatorSetString(INDICATOR_LEVELTEXT,0,"Oversold");   // level #0 "Oversold"
   IndicatorSetString(INDICATOR_LEVELTEXT,1,"Overbought"); // level #1 "Overbought"
//--- min/max values
   IndicatorSetDouble(INDICATOR_MINIMUM,-100); // min
   IndicatorSetDouble(INDICATOR_MAXIMUM,100);  // max
*/
//---
   begin1=q-1;         //                                    - MtmBuffer[], AbsMtmBuffer[]
   begin2=begin1+r-1;  // or =(q-1)+(r-1)                    - EMA_...[]
   begin3=begin2+s-1;  // or =(q-1)+(r-1)+(s-1)              - DEMA_...[]
   begin4=begin3+u-1;  // or =(q-1)+(r-1)+(s-1)+(u-1)        - TEMA_...[], MainBuffer[]
   begin5=begin4+ul-1; // or =(q-1)+(r-1)+(s-1)+(u-1)+(ul-1) - SignalBuffer[]
   //
   rates_total_min=begin5+1; // rates total min
//--- starting bar index for plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- starting bar index for plot #1
   PlotIndexSetInteger(1,PLOT_DRAW_BEGIN,begin5);
//--- short indicator name
   string shortname=PriceName(AppliedPrice)+","+string(q)+","+string(r)+","+string(s)+","+string(u)+","+string(ul);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_Ergodic("+shortname+")");
//--- OnInit done
   return(0);
  }
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(
                const int rates_total,     // rates total
                const int prev_calculated, // bars, calculated at previous call
                const datetime &Time[],    // Time
                const double &Open[],      // Open
                const double &High[],      // High
                const double &Low[],       // Low
                const double &Close[],     // Close
                const long &TickVolume[],  // Tick Volume
                const long &Volume[],      // Real Volume
                const int &Spread[]        // Spread
               )
  {
   int i,pos;
   double value1,value2;
//--- rates total
   if(rates_total<rates_total_min) return(0);
//--- calculation of PriceBuffer[]
   CalculatePriceBuffer(
                        AppliedPrice,        // price type
                        rates_total,         // rates total
                        prev_calculated,     // bars, calculated at the previous call
                        Open,High,Low,Close, // Open[], High[], Low[], Close[]
                        PriceBuffer          // price array
                       );
//--- calculation of mtm and |mtm|
   if(prev_calculated==0)      // at first call
     {
      pos=begin1;              // starting from begin1
      for(i=0;i<pos;i++)       // pos
        {
         MtmBuffer[i]=0.0;     // zero values
         AbsMtmBuffer[i]=0.0;  //
        }
     }
   else pos=prev_calculated-1; // overwise calc only last bar
   // calculate MtmBuffer[] and AbsMtmBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      MtmBuffer[i]=PriceBuffer[i]-PriceBuffer[i-(q-1)];
      AbsMtmBuffer[i]=MathAbs(MtmBuffer[i]);
     }
//--- EMA smoothing
   // r-period of the 1st EMA
   ExponentialMAOnBufferWB(
                           rates_total,     // rates total
                           prev_calculated, // bars, calculated at previous call
                           begin1,          // starting index
                           r,               // smoothing period
                           MtmBuffer,       // input array
                           EMA_MtmBuffer    // output array
                          );
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin1,r,AbsMtmBuffer,EMA_AbsMtmBuffer);
   // s-period of 2nd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_MtmBuffer,DEMA_MtmBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_AbsMtmBuffer,DEMA_AbsMtmBuffer);
   // u-period 3rd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_MtmBuffer,TEMA_MtmBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_AbsMtmBuffer,TEMA_AbsMtmBuffer);
//--- calculation of Ergodic (graphic plot #0)
   if(prev_calculated==0)      // at first call
     {
      pos=begin4;              // starting from begin4
      for(i=0;i<pos;i++)       // pos
         MainBuffer[i]=0.0;    // zero values
     }
   else pos=prev_calculated-1; // overwise calculate only last bar
   // calculation of MainBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      value1=100*TEMA_MtmBuffer[i];
      value2=TEMA_AbsMtmBuffer[i];
      MainBuffer[i]=(value2>0)?value1/value2:0;
     }
//--- calculation of Signal Line (graphic plot #1)
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin4,ul,MainBuffer,SignalBuffer);
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+