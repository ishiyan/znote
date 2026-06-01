//+------------------------------------------------------------------+
//|                                                     Blau_MDI.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // URL
#property description "Mean Deviation Index (William Blau)"     // description
#include <WilliamBlau.mqh>              // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window     // indicator in a separate window
#property indicator_buffers 5           // number of buffers
#property indicator_plots   1           // number of graphic plots
//--- graphic plot #0 (Main)
#property indicator_label1  "MDI"       // label of graphic plot #0
#property indicator_type1   DRAW_LINE   // draw as a line
#property indicator_color1  Blue        // line color
#property indicator_style1  STYLE_SOLID // line style
#property indicator_width1  1           // line width
//--- input parameters
input int    r=20; // r - 1st EMA, applied to price
input int    s=5;  // s - 2nd EMA, applied to average deviation
input int    u=3;  // u - 3rd EMA, applied to the 2nd smoothing
input ENUM_APPLIED_PRICE AppliedPrice=PRICE_CLOSE; // AppliedPrice - price type
//--- dynamic arrays, used for the calculation
double MainBuffer[];      // u-period 3rd EMA (graphic plot #0)
double PriceBuffer[];     // price array
double EMA_PriceBuffer[]; // r-period 1st EMA (price)
double MDBuffer[];        // average deviation
double DEMA_MDBuffer[];   // s-period 2nd EMA
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
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);              // u-period 3rd EMA
   // buffers for intermediate calculations
   SetIndexBuffer(1,PriceBuffer,INDICATOR_CALCULATIONS);     // price array
   SetIndexBuffer(2,EMA_PriceBuffer,INDICATOR_CALCULATIONS); // r-period 1st EMA (price)
   SetIndexBuffer(3,MDBuffer,INDICATOR_CALCULATIONS);        // average deviation
   SetIndexBuffer(4,DEMA_MDBuffer,INDICATOR_CALCULATIONS);   // s-period 2nd EMA
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"MDI");             // label of graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_TYPE,DRAW_LINE);    // draw as a line
   PlotIndexSetInteger(0,PLOT_LINE_COLOR,Blue);        // line color
   PlotIndexSetInteger(0,PLOT_LINE_STYLE,STYLE_SOLID); // line style
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,1);           // line width
*/
//--- precision
   IndicatorSetInteger(INDICATOR_DIGITS,_Digits);
//---
   begin1=0;          //                         
   begin2=begin1+r-1; // or =0+(r-1)             - MDBuffer[], EMA_PriceBuffer[]
   begin3=begin2+s-1; // or =0+(r-1)+(s-1)       - DEMA_MDBuffer[]
   begin4=begin3+u-1; // or =0+(r-1)+(s-1)+(u-1) - MainBuffer[]
   //
   rates_total_min=begin4+1; // rates total min
//--- starting index for graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- short indicator name
   string shortname=PriceName(AppliedPrice)+","+string(r)+","+string(s)+","+string(u);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_MDI("+shortname+")");
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
//--- calculation of PriceBuffer[]
   CalculatePriceBuffer(
                        AppliedPrice,        // applied price
                        rates_total,         // rates total
                        prev_calculated,     // bars, calculated at previous call
                        Open,High,Low,Close, // Open[], High[], Low[], Close[]
                        PriceBuffer          // target array
                       );
//--- calculation of the standard deviation
   if(prev_calculated==0)      // at first call
     {
      pos=begin2;              // starting from 0
      for(i=0;i<pos;i++)       // pos bars
         MDBuffer[i]=0.0;      // zero values
     }
   else pos=prev_calculated-1; // overwise calculate only last value
   // r-period 1st EMA: calculation of EMA_PriceBuffer[]
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin1,r,PriceBuffer,EMA_PriceBuffer);
   // calculation of MDBuffer[]
   for(i=pos;i<rates_total;i++)
      MDBuffer[i]=PriceBuffer[i]-EMA_PriceBuffer[i];
//--- EMA smoothing
   // s-period 2nd EMA
   ExponentialMAOnBufferWB(
                           rates_total,     // rates total
                           prev_calculated, // bars, calculated at previous call
                           begin2,          // starting index
                           s,               // smoothing period
                           MDBuffer,        // input array
                           DEMA_MDBuffer    // target array
                          );
   // u-period 3rd EMA (graphic plot #0)
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_MDBuffer,MainBuffer);
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+