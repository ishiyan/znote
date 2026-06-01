//+------------------------------------------------------------------+
//|                                                     Blau_CMI.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // URL
#property description "Candle Momentum Index (William Blau)"    // description
#include <WilliamBlau.mqh>               // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window      // indicator in a separate window
#property indicator_buffers 11           // number of buffers used
#property indicator_plots   1            // number of graphic plots
//--- horizontal levels
#property indicator_level1 -25           // level #0
#property indicator_level2 25            // level #1
#property indicator_levelcolor Silver    // level color
#property indicator_levelstyle STYLE_DOT // level line style
#property indicator_levelwidth 1         // level width
//--- indicator scale
#property indicator_minimum -100         // lower bound
#property indicator_maximum 100          // upper bound
//--- graphic plot #0 (Main)
#property indicator_label1  "CMI"        // label of graphic plot #0
#property indicator_type1   DRAW_LINE    // draw as a line
#property indicator_color1  Blue         // line color
#property indicator_style1  STYLE_SOLID  // line style
#property indicator_width1  1            // line width
//--- input parameters
input int    q=1;  // q - period of Candlestick Momentum
input int    r=20; // r - 1st EMA, applied to Candlestick Momentum
input int    s=5;  // s - 2nd EMA, applied to the 1st smoothing
input int    u=3;  // u - 3rd EMA, applied to the 2nd smoothing
input ENUM_APPLIED_PRICE AppliedPrice1=PRICE_CLOSE; // AppliedPrice1 - price type [close]
input ENUM_APPLIED_PRICE AppliedPrice2=PRICE_OPEN;  // AppliedPrice2 - price type [open]
//--- dynamic arrays
double MainBuffer[];         // CMI (for graphic plot #0)
double Price1Buffer[];       // price array [close prices]
double Price2Buffer[];       // price array [open prices]
double CMtmBuffer[];         // q-period Candlestick Momentum
double EMA_CMtmBuffer[];     // r-period 1st EMA
double DEMA_CMtmBuffer[];    // s-period 2nd EMA
double TEMA_CMtmBuffer[];    // u-period 3rd EMA
double AbsCMtmBuffer[];      // q-period Candlestick Momentum (absolute values)
double EMA_AbsCMtmBuffer[];  // r-period 1st EMA (absolute values)
double DEMA_AbsCMtmBuffer[]; // s-period 2nd EMA (absolute values)
double TEMA_AbsCMtmBuffer[]; // u-period 3rd EMA (absolute values)
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
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);                  // CMI
   // buffers, used for intermediate calculations
   SetIndexBuffer(1,Price1Buffer,INDICATOR_CALCULATIONS);        // price array [close]
   SetIndexBuffer(2,Price2Buffer,INDICATOR_CALCULATIONS);        // price array [open]
   SetIndexBuffer(3,CMtmBuffer,INDICATOR_CALCULATIONS);          // q-period Candlestick Momentum
   SetIndexBuffer(4,EMA_CMtmBuffer,INDICATOR_CALCULATIONS);      // r-period 1st EMA
   SetIndexBuffer(5,DEMA_CMtmBuffer,INDICATOR_CALCULATIONS);     // s-period 2nd EMA
   SetIndexBuffer(6,TEMA_CMtmBuffer,INDICATOR_CALCULATIONS);     // u-period 3rd EMA
   SetIndexBuffer(7,AbsCMtmBuffer,INDICATOR_CALCULATIONS);       // q-period Candlestick Momentum (absolute values)
   SetIndexBuffer(8,EMA_AbsCMtmBuffer,INDICATOR_CALCULATIONS);   // r-period 1st EMA (absolute values)
   SetIndexBuffer(9,DEMA_AbsCMtmBuffer,INDICATOR_CALCULATIONS);  // s-period 2nd EMA (absolute values)
   SetIndexBuffer(10,TEMA_AbsCMtmBuffer,INDICATOR_CALCULATIONS); // u-period 3rd EMA (absolute values)
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"CMI");             // label of graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_TYPE,DRAW_LINE);    // draw as a line
   PlotIndexSetInteger(0,PLOT_LINE_COLOR,Blue);        // line color
   PlotIndexSetInteger(0,PLOT_LINE_STYLE,STYLE_SOLID); // line style
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,1);           // line width
*/
//--- precision
   IndicatorSetInteger(INDICATOR_DIGITS,2);
/*
//--- horizontal levels
   IndicatorSetInteger(INDICATOR_LEVELS,2);                // number of indicator levels
   IndicatorSetDouble(INDICATOR_LEVELVALUE,0,-25);         // level #0
   IndicatorSetDouble(INDICATOR_LEVELVALUE,1,25);          // level #1
   IndicatorSetInteger(INDICATOR_LEVELCOLOR,Silver);       // level color
   IndicatorSetInteger(INDICATOR_LEVELSTYLE,STYLE_DOT);    // level line style
   IndicatorSetInteger(INDICATOR_LEVELWIDTH,1);            // level line width
   IndicatorSetString(INDICATOR_LEVELTEXT,0,"Oversold");   // description of level #0 "Oversold"
   IndicatorSetString(INDICATOR_LEVELTEXT,1,"Overbought"); // description of level #1 "Overbought"
//--- scale
   IndicatorSetDouble(INDICATOR_MINIMUM,-100); // lower bound
   IndicatorSetDouble(INDICATOR_MAXIMUM,100);  // upper bound
*/
//---
   begin1=q-1;        //                             - CMtmBuffer[], AbsCMtmBuffer[]
   begin2=begin1+r-1; // or =(q-1)+(r-1)             - EMA_...[]
   begin3=begin2+s-1; // or =(q-1)+(r-1)+(s-1)       - DEMA_...[]
   begin4=begin3+u-1; // or =(q-1)+(r-1)+(s-1)+(u-1) - TEMA_...[], MainBuffer[]
   //
   rates_total_min=begin4+1; // rates total min
//--- starting index
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- short indicator name
   string shortname=PriceName(AppliedPrice1)+","+PriceName(AppliedPrice2)+","+string(q)+","+string(r)+","+string(s)+","+string(u);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_CMI("+shortname+")");
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
//--- calculation of Price1Buffer[] and Price2Buffer[]
   CalculatePriceBuffer(
                        AppliedPrice1,       // price type [close prices]
                        rates_total,         // rates_total
                        prev_calculated,     // bars, calculated at previous call
                        Open,High,Low,Close, // Open[], High[], Low[], Close[]
                        Price1Buffer         // target array
                       );
   CalculatePriceBuffer(AppliedPrice2,rates_total,prev_calculated,Open,High,Low,Close,Price2Buffer);
//--- calculation of cmtm and |cmtm|
   if(prev_calculated==0)      // at first call
     {
      pos=begin1;              // 
      for(i=0;i<pos;i++)       // 
        {
         CMtmBuffer[i]=0.0;    // zero values
         AbsCMtmBuffer[i]=0.0; //
        }
     }
   else pos=prev_calculated-1; // overwise recalculate only last value
   // calculation of CMtmBuffer[] and AbsCMtmBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      CMtmBuffer[i]=Price1Buffer[i]-Price2Buffer[i-(q-1)];
      AbsCMtmBuffer[i]=MathAbs(CMtmBuffer[i]);
     }
//--- EMA smoothing
   // r-period 1st EMA
   ExponentialMAOnBufferWB(
                           rates_total,     // rates total
                           prev_calculated, // bars, calculated at previous call
                           begin1,          // starting index
                           r,               // smoothing period
                           CMtmBuffer,      // input array
                           EMA_CMtmBuffer   // target array
                          );
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin1,r,AbsCMtmBuffer,EMA_AbsCMtmBuffer);
   // s-period 2nd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_CMtmBuffer,DEMA_CMtmBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_AbsCMtmBuffer,DEMA_AbsCMtmBuffer);
   // u-period 3rd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_CMtmBuffer,TEMA_CMtmBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_AbsCMtmBuffer,TEMA_AbsCMtmBuffer);
//--- calculation of CMI (graphic plot #0)
   if(prev_calculated==0)      // at first call
     {
      pos=begin4;              // 
      for(i=0;i<pos;i++)       // 
         MainBuffer[i]=0.0;    // zero values
     }
   else pos=prev_calculated-1; // overwise recalculate only last value
   // calculation of MainBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      value1=100*TEMA_CMtmBuffer[i];
      value2=TEMA_AbsCMtmBuffer[i];
      MainBuffer[i]=(value2>0)?value1/value2:0;
     }
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+