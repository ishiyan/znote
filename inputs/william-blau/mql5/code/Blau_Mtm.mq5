//+------------------------------------------------------------------+
//|                                                     Blau_Mtm.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // url
#property description "q-period Momentum (William Blau)"        // description
#include <WilliamBlau.mqh>              // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window     // indicator in a separate window
#property indicator_buffers 5           // number of buffers used
#property indicator_plots   1           // number of plots
//--- main graphic plot #0
#property indicator_label1  "Mtm"       // graphic plot label #0
#property indicator_type1   DRAW_LINE   // draw as a line
#property indicator_color1  Blue        // color
#property indicator_style1  STYLE_SOLID // line style - solid line
#property indicator_width1  1           // line width
//--- input parameters
input int    q=2;  // q - period of Momentum
input int    r=20; // r - 1st EMA, applied to momentum
input int    s=5;  // s - 2nd EMA, applied to the 1st EMA
input int    u=3;  // u - 3rd EMA, applied to the 2nd EMA
input ENUM_APPLIED_PRICE AppliedPrice=PRICE_CLOSE; // AppliedPrice - price type
//--- dynamic arrays
double MainBuffer[];     // u-period 3rd EMA (for graphic plot #0)
double PriceBuffer[];    // price array
double MtmBuffer[];      // q-period Momentum
double EMA_MtmBuffer[];  // r-period 1st EMA
double DEMA_MtmBuffer[]; // s-period 2nd EMA
//--- global variables
int    begin1, begin2, begin3, begin4; // data starting indexes
int    rates_total_min; // total rates min
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- indicator buffers
   // plot buffers
   // graphic plot #0
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);             // u-period 3rd EMA
   // buffers for intermediate calculations
   SetIndexBuffer(1,PriceBuffer,INDICATOR_CALCULATIONS);    // price buffer
   SetIndexBuffer(2,MtmBuffer,INDICATOR_CALCULATIONS);      // q-period Momentum
   SetIndexBuffer(3,EMA_MtmBuffer,INDICATOR_CALCULATIONS);  // r-period 1st EMA
   SetIndexBuffer(4,DEMA_MtmBuffer,INDICATOR_CALCULATIONS); // s-period 2nd EMA
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"Mtm");             // label
   PlotIndexSetInteger(0,PLOT_DRAW_TYPE,DRAW_LINE);    // drawing type as a line
   PlotIndexSetInteger(0,PLOT_LINE_COLOR,Blue);        // line color
   PlotIndexSetInteger(0,PLOT_LINE_STYLE,STYLE_SOLID); // line style
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,1);           // line width
*/
//--- precision
   IndicatorSetInteger(INDICATOR_DIGITS,_Digits);
//---
   begin1=q-1;        //                             - MtmBuffer[]
   begin2=begin1+r-1; // or =(q-1)+(r-1)             - EMA_MtmBuffer[]
   begin3=begin2+s-1; // or =(q-1)+(r-1)+(s-1)       - DEMA_MtmBuffer[]
   begin4=begin3+u-1; // or =(q-1)+(r-1)+(s-1)+(u-1) - MainBuffer[]
   //
   rates_total_min=begin4+1; // minimal size
//--- starting index for plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- short indicator name
   string shortname=PriceName(AppliedPrice)+","+string(q)+","+string(r)+","+string(s)+","+string(u);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_Mtm("+shortname+")");
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
//--- calc PriceBuffer[]
   CalculatePriceBuffer(
                        AppliedPrice,        // applied price
                        rates_total,         // rates total
                        prev_calculated,     // bars, calculated at previous call
                        Open,High,Low,Close, // Open[], High[], Low[], Close[] arrays
                        PriceBuffer          // price buffer
                       );
//--- calculation of q-period Momentum
   if(prev_calculated==0)      // at first call
     {
      pos=begin1;              // calc all values starting from begin1
      for(i=0;i<pos;i++)       // pos values
         MtmBuffer[i]=0.0;     // zero values
     }
   else pos=prev_calculated-1; // overwise recalc only last value
   // calculate MtmBuffer[]
   for(i=pos;i<rates_total;i++)
      MtmBuffer[i]=PriceBuffer[i]-PriceBuffer[i-(q-1)];
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
   // s-period 2nd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_MtmBuffer,DEMA_MtmBuffer);
   // u-period 3rd EMA (for plot #0)
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_MtmBuffer,MainBuffer);
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+