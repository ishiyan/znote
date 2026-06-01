//+------------------------------------------------------------------+
//|                                                     Blau_TSI.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // URL
#property description "True Strength Index (William Blau)"      // description
#include <WilliamBlau.mqh>               // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window      // indicator in a separate window
#property indicator_buffers 10           // number of buffers used
#property indicator_plots   1            // graphic plots
//--- horizontal levels
#property indicator_level1 -25           // level #0 (vertical)
#property indicator_level2 25            // level #1 (vertical)
#property indicator_levelcolor Silver    // level color
#property indicator_levelstyle STYLE_DOT // level style
#property indicator_levelwidth 1         // level width
//--- indicator min/max
#property indicator_minimum -100         // minimum
#property indicator_maximum 100          // maximum
//--- graphic plot #0 (Main)
#property indicator_label1  "TSI"        // label for graphic plot #0
#property indicator_type1   DRAW_LINE    // draw as a line
#property indicator_color1  Blue         // line color
#property indicator_style1  STYLE_SOLID  // line style
#property indicator_width1  1            // line width
//--- input parameters
input int    q=2;  // q - period of Momentum
input int    r=20; // r - 1st EMA, applied to Momentum
input int    s=5;  // s - 2nd EMA, applied to the 1st smoothing
input int    u=3;  // u - 3rd EMA, applied to the 2nd smoothing
input ENUM_APPLIED_PRICE AppliedPrice=PRICE_CLOSE; // AppliedPrice - price type
//--- dynamic arrays
double MainBuffer[];        // TSI (graphic plot #0)
double PriceBuffer[];       // price array
double MtmBuffer[];         // q-period Momentum
double EMA_MtmBuffer[];     // r-period 1st EMA
double DEMA_MtmBuffer[];    // s-period 2nd EMA
double TEMA_MtmBuffer[];    // u-period 3rd EMA
double AbsMtmBuffer[];      // q-period Momentum (absolute value)
double EMA_AbsMtmBuffer[];  // r-period 1st EMA (absolute value)
double DEMA_AbsMtmBuffer[]; // s-period 2nd EMA (absolute value)
double TEMA_AbsMtmBuffer[]; // u-period 3rd EMA (absolute value)
//--- global variables
int    begin1, begin2, begin3, begin4; // starting index
int    rates_total_min; // rates total min
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- indicator buffers
   // graphic plot #0
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);                // TSI
   // intermediate buffers; (not used for plot)
   SetIndexBuffer(1,PriceBuffer,INDICATOR_CALCULATIONS);       // price array
   SetIndexBuffer(2,MtmBuffer,INDICATOR_CALCULATIONS);         // q-period Momentum
   SetIndexBuffer(3,EMA_MtmBuffer,INDICATOR_CALCULATIONS);     // r-period 1st EMA
   SetIndexBuffer(4,DEMA_MtmBuffer,INDICATOR_CALCULATIONS);    // s-period 2nd EMA
   SetIndexBuffer(5,TEMA_MtmBuffer,INDICATOR_CALCULATIONS);    // u-period 3rd EMA
   SetIndexBuffer(6,AbsMtmBuffer,INDICATOR_CALCULATIONS);      // q-period моментум (absolute value)
   SetIndexBuffer(7,EMA_AbsMtmBuffer,INDICATOR_CALCULATIONS);  // r-period 1st EMA (absolute value)
   SetIndexBuffer(8,DEMA_AbsMtmBuffer,INDICATOR_CALCULATIONS); // s-period 2nd EMA (absolute value)
   SetIndexBuffer(9,TEMA_AbsMtmBuffer,INDICATOR_CALCULATIONS); // u-period 3rd EMA (absolute value)
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"TSI");             // label of graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_TYPE,DRAW_LINE);    // draw as a line
   PlotIndexSetInteger(0,PLOT_LINE_COLOR,Blue);        // line color
   PlotIndexSetInteger(0,PLOT_LINE_STYLE,STYLE_SOLID); // line style
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,1);           // line width
*/
//--- precision
   IndicatorSetInteger(INDICATOR_DIGITS,2);
/*
//--- horizontal levels
   IndicatorSetInteger(INDICATOR_LEVELS,2);                // number of levels
   IndicatorSetDouble(INDICATOR_LEVELVALUE,0,-25);         // level #0
   IndicatorSetDouble(INDICATOR_LEVELVALUE,1,25);          // level #1
   IndicatorSetInteger(INDICATOR_LEVELCOLOR,Silver);       // level color
   IndicatorSetInteger(INDICATOR_LEVELSTYLE,STYLE_DOT);    // level style
   IndicatorSetInteger(INDICATOR_LEVELWIDTH,1);            // level width
   IndicatorSetString(INDICATOR_LEVELTEXT,0,"Oversold");   // level 0 description "Oversold"
   IndicatorSetString(INDICATOR_LEVELTEXT,1,"Overbought"); // level 1 description "Overbought"
//--- indicator scale
   IndicatorSetDouble(INDICATOR_MINIMUM,-100); // minimum
   IndicatorSetDouble(INDICATOR_MAXIMUM,100);  // maximum
*/
//---
   begin1=q-1;        //                             - MtmBuffer[], AbsMtmBuffer[]
   begin2=begin1+r-1; // or =(q-1)+(r-1)             - EMA_...[]
   begin3=begin2+s-1; // or =(q-1)+(r-1)+(s-1)       - DEMA_...[]
   begin4=begin3+u-1; // or =(q-1)+(r-1)+(s-1)+(u-1) - TEMA_...[], MainBuffer[]
   //
   rates_total_min=begin4+1; // rates total min
//--- starting index for plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- short indicator name
   string shortname=PriceName(AppliedPrice)+","+string(q)+","+string(r)+","+string(s)+","+string(u);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_TSI("+shortname+")");
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
//--- check rates
   if(rates_total<rates_total_min) return(0);
//--- calc PriceBuffer[]
   CalculatePriceBuffer(
                        AppliedPrice,        // price type
                        rates_total,         // rates total
                        prev_calculated,     // bars, calculated at previous tick
                        Open,High,Low,Close, // Open[], High[], Low[], Close[]
                        PriceBuffer          // price buffer
                       );
//--- calculation of  mtm and |mtm|
   if(prev_calculated==0)      // at first call
     {
      pos=begin1;              // calc all values starting from begin1
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
   // r-period 1st EMA
   ExponentialMAOnBufferWB(
                           rates_total,     // rates total
                           prev_calculated, // bars, calculated at previous call
                           begin1,          // starting index
                           r,               // smoothing period
                           MtmBuffer,       // input array
                           EMA_MtmBuffer    // output array
                          );
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin1,r,AbsMtmBuffer,EMA_AbsMtmBuffer);
   // s-period 2nd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_MtmBuffer,DEMA_MtmBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_AbsMtmBuffer,DEMA_AbsMtmBuffer);
   // u-period 3rd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_MtmBuffer,TEMA_MtmBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_AbsMtmBuffer,TEMA_AbsMtmBuffer);
//--- TSI calculation (graphic plot #0)
   if(prev_calculated==0)      // at first call
     {
      pos=begin4;              // calc all values starting from begin4
      for(i=0;i<pos;i++)       // 
         MainBuffer[i]=0.0;    // zero values
     }
   else pos=prev_calculated-1; // overwise calc only last bar
   // calculation of MainBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      value1=100*TEMA_MtmBuffer[i];
      value2=TEMA_AbsMtmBuffer[i];
      MainBuffer[i]=(value2>0)?value1/value2:0;
     }
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+