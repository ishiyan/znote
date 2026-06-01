//+------------------------------------------------------------------+
//|                                                    Blau_CMtm.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // URL
#property description "q-period Candle Momentum (William Blau)" // description
#include <WilliamBlau.mqh>              // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window     // indicator in a separate window
#property indicator_buffers 6           // number of buffers
#property indicator_plots   1           // number of plots
//--- graphic plot #0 (Main)
#property indicator_label1  "CMtm"      // label of graphic plot #0
#property indicator_type1   DRAW_LINE   // draw as a line
#property indicator_color1  Blue        // line color
#property indicator_style1  STYLE_SOLID // line style
#property indicator_width1  1           // line width
//--- input parameters
input int    q=1;  // q - period of Candlestick Momentum
input int    r=20; // r - 1st EMA, applied to Candlestick Momentum
input int    s=5;  // s - 2nd EMA, applied to the 1st smoothing
input int    u=3;  // u - 3rd EMA, applied to the 2nd smoothing
input ENUM_APPLIED_PRICE AppliedPrice1=PRICE_CLOSE; // AppliedPrice1 - price type [close price]
input ENUM_APPLIED_PRICE AppliedPrice2=PRICE_OPEN;  // AppliedPrice2 - price type [open price]
//--- dynamic arrays
double MainBuffer[];      // u-period 3rd EMA (graphic plot #0)
double Price1Buffer[];    // Close prices array
double Price2Buffer[];    // Open prices array
double CMtmBuffer[];      // q-period Momentum
double EMA_CMtmBuffer[];  // r-period 1st EMA
double DEMA_CMtmBuffer[]; // s-period 2nd EMA
//--- global variables
int    begin1, begin2, begin3, begin4; // starting index
int    rates_total_min; // total rates min
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- indicator buffers
   // graphic plot #0
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);              // u-period 3rd EMA
   // buffers for intermediate calculations
   SetIndexBuffer(1,Price1Buffer,INDICATOR_CALCULATIONS);    // price array [close]
   SetIndexBuffer(2,Price2Buffer,INDICATOR_CALCULATIONS);    // price array [open]
   SetIndexBuffer(3,CMtmBuffer,INDICATOR_CALCULATIONS);      // q-period Candlestick Momentum
   SetIndexBuffer(4,EMA_CMtmBuffer,INDICATOR_CALCULATIONS);  // r-period 1st EMA
   SetIndexBuffer(5,DEMA_CMtmBuffer,INDICATOR_CALCULATIONS); // s-period 2nd EMA
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"ÑMtm");            // label of graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_TYPE,DRAW_LINE);    // draw as a line
   PlotIndexSetInteger(0,PLOT_LINE_COLOR,Blue);        // line color
   PlotIndexSetInteger(0,PLOT_LINE_STYLE,STYLE_SOLID); // line style
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,1);           // line width
*/
//--- precision
   IndicatorSetInteger(INDICATOR_DIGITS,_Digits);
//---
   begin1=q-1;        //                            - ÑMtmBuffer[]
   begin2=begin1+r-1; // or =(q-1)+(r-1)             - EMA_ÑMtmBuffer[]
   begin3=begin2+s-1; // or =(q-1)+(r-1)+(s-1)       - DEMA_ÑMtmBuffer[]
   begin4=begin3+u-1; // or =(q-1)+(r-1)+(s-1)+(u-1) - MainBuffer[]
   //
   rates_total_min=begin4+1; // total rates min
//--- starting index for plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- short indicator name
   string shortname=PriceName(AppliedPrice1)+","+PriceName(AppliedPrice2)+","+string(q)+","+string(r)+","+string(s)+","+string(u);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_ÑMtm("+shortname+")");
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
//--- check rates
   if(rates_total<rates_total_min) return(0);
//--- calculation of  Price1Buffer[] and Price2Buffer[]
   CalculatePriceBuffer(
                        AppliedPrice1,       // price type [close price]
                        rates_total,         // rates total
                        prev_calculated,     // bars, calculated at previous call
                        Open,High,Low,Close, // Open[], High[], Low[], Close[]
                        Price1Buffer         // target array [close price]
                       );
   CalculatePriceBuffer(AppliedPrice2,rates_total,prev_calculated,Open,High,Low,Close,Price2Buffer);
//--- calculation of q-period Candlestick Momentum
   if(prev_calculated==0)      // at first call
     {
      pos=begin1;              // 
      for(i=0;i<pos;i++)       // pos data
         CMtmBuffer[i]=0.0;    // zero values
     }
   else pos=prev_calculated-1; // overwise recalculate only last value
   // calculation of CMtmBuffer[]
   for(i=pos;i<rates_total;i++)
      CMtmBuffer[i]=Price1Buffer[i]-Price2Buffer[i-(q-1)];
//--- EMA smoothing
   // r-period 1st EMA
   ExponentialMAOnBufferWB(
                           rates_total,     // rates total
                           prev_calculated, // bars, calculated at previous call
                           begin1,          // starting bar index
                           r,               // smoothing period
                           CMtmBuffer,      // input array
                           EMA_CMtmBuffer   // target array
                          );
   // s-period 2st EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_CMtmBuffer,DEMA_CMtmBuffer);
   // u-period 3rd EMA (graphic plot #0)
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_CMtmBuffer,MainBuffer);
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+