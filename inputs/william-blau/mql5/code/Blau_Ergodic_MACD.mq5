//+------------------------------------------------------------------+
//|                                            Blau_Ergodic_MACD.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // url
#property description "Ergodic MACD-Oscillator (William Blau)"  // description
#include <WilliamBlau.mqh>                 // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window        // indicator in a separate window
#property indicator_buffers 6              // number of buffers used
#property indicator_plots   2              // number of graphic plots
//--- graphic plot #0 (Main)
#property indicator_label1  "Ergodic"      // label of graphic plot #0
#property indicator_type1   DRAW_HISTOGRAM // draw as a histogram
#property indicator_color1  Silver         // histogram color
#property indicator_style1  STYLE_SOLID    // histogram style
#property indicator_width1  2              // histogram width
//--- graphic plot #1 (Signal Line)
#property indicator_label2  "Signal"       // label of graphic plot #1
#property indicator_type2   DRAW_LINE      // draw as a line
#property indicator_color2  Red            // line color
#property indicator_style2  STYLE_SOLID    // line style
#property indicator_width2  1              // line width
//--- input parameters
input int    r=20; // r - 1st EMA(slow), applied to price
input int    s=5;  // s - 2nd EMA(fast), applied to price
input int    u=3;  // u - 3rd EMA, applied to MACD
input int    ul=3; // ul - period of a Signal Line
input ENUM_APPLIED_PRICE AppliedPrice=PRICE_CLOSE; // AppliedPrice - price type
//--- dynamic arrays
double MainBuffer[];       // Ergodic: u-period 3rd EMA (graphic plot #0)
double SignalBuffer[];     // Signal Line: ul-period EMA, applied to Ergodic (graphic plot #1)
double PriceBuffer[];      // price array
double EMA1_PriceBuffer[]; // r-period 1st EMA (slow), applied to price
double EMA2_PriceBuffer[]; // s-period 2nd EMA (fast), applied to price
double MACDBuffer[];       // moving averages convergence/divergence
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
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);               // Ergodic: u-period 3rd EMA
   // graphic plot #1
   SetIndexBuffer(1,SignalBuffer,INDICATOR_DATA);             // Signal Line: ul-period EMA, applied to Ergodic
   // buffers for intermediate calculations
   SetIndexBuffer(2,PriceBuffer,INDICATOR_CALCULATIONS);      // price array
   SetIndexBuffer(3,EMA1_PriceBuffer,INDICATOR_CALCULATIONS); // r-period 1st EMA (slow), applied to price
   SetIndexBuffer(4,EMA2_PriceBuffer,INDICATOR_CALCULATIONS); // s-period 2nd EMA (fast), applied to price
   SetIndexBuffer(5,MACDBuffer,INDICATOR_CALCULATIONS);       // moving averages convergence/divergence
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"Ergodic");           // label of graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_TYPE,DRAW_HISTOGRAM); // draw as a histogram
   PlotIndexSetInteger(0,PLOT_LINE_COLOR,Silver);        // histogram color
   PlotIndexSetInteger(0,PLOT_LINE_STYLE,STYLE_SOLID);   // histogram style
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,2);             // histogram width
//--- graphic plot #1 (Signal Line)
   PlotIndexSetString(1,PLOT_LABEL,"Signal");            // label of graphic plot #1
   PlotIndexSetInteger(1,PLOT_DRAW_TYPE,DRAW_LINE);      // draw as a line
   PlotIndexSetInteger(1,PLOT_LINE_COLOR,Red);           // line color
   PlotIndexSetInteger(1,PLOT_LINE_STYLE,STYLE_SOLID);   // line style
   PlotIndexSetInteger(1,PLOT_LINE_WIDTH,1);             // line width
*/
//--- precision
   IndicatorSetInteger(INDICATOR_DIGITS,_Digits);
//---
   begin1=0;                     
   begin2=begin1+MathMax(r,s)-1; // or =(max(r,s)-1)              - MACDBuffer[], EMA1_PriceBuffer[]
   begin3=begin2;                // or =(max(r,s)-1)              - EMA2_PriceBuffer[]
   begin4=begin3+u-1;            // or =(max(r,s)-1)+(u-1)        - MainBuffer[]
   begin5=begin4+ul-1;           // or =(max(r,s)-1)+(u-1)+(ul-1) - SignalBuffer[]
   //
   rates_total_min=begin5+1;     // rates total min
//--- starting index for plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- starting index for plot #1
   PlotIndexSetInteger(1,PLOT_DRAW_BEGIN,begin5);
//--- indicator short name
   string shortname=PriceName(AppliedPrice)+","+string(r)+","+string(s)+","+string(u)+","+string(ul);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_Ergodic_MACD("+shortname+")");
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
                        AppliedPrice,        // price type
                        rates_total,         // rates total
                        prev_calculated,     // bars, calculated at previous call
                        Open,High,Low,Close, // Open[], High[], Low[], Close[]
                        PriceBuffer          // target array
                       );
//--- calculation of moving average convergence/divergence
   if(prev_calculated==0)      // at first call
     {
      pos=begin2;              // 
      for(i=0;i<pos;i++)       // pos
         MACDBuffer[i]=0.0;    // zero values
     }
   else pos=prev_calculated-1; // overwise calculate only last value
   // r-period 1st EMA: calculation of EMA1_PriceBuffer[]
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin1,r,PriceBuffer,EMA1_PriceBuffer);
   // s-period 2nd EMA: calculation of EMA2_PriceBuffer[]
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin1,s,PriceBuffer,EMA2_PriceBuffer);
   // calculation of MACDBuffer[]
   for(i=pos;i<rates_total;i++)
      MACDBuffer[i]=EMA2_PriceBuffer[i]-EMA1_PriceBuffer[i];
//--- EMA smoothing
   // u-period 3rd EMA (graphic plot #0)
   ExponentialMAOnBufferWB(
                           rates_total,     // rates total
                           prev_calculated, // bars, calculated at previous call
                           begin3,          // starting index
                           u,               // smoothing period
                           MACDBuffer,      // input array
                           MainBuffer       // target array
                          );
//--- calculation of a Signal Line (graphic plot #1)
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin4,ul,MainBuffer,SignalBuffer);
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+