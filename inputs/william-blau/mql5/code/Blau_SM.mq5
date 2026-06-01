//+------------------------------------------------------------------+
//|                                                      Blau_SM.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // URL
#property description "q-period Stochastic Momentum (William Blau)" // description
#include <WilliamBlau.mqh>              // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window     // indicator in a separate window
#property indicator_buffers 7           // number of buffers used
#property indicator_plots   1           // number of plots
//--- graphic plot #0 (Main)
#property indicator_label1  "SM"        // label of plot #0
#property indicator_type1   DRAW_LINE   // draw as a line
#property indicator_color1  Blue        // line color
#property indicator_style1  STYLE_SOLID // line style
#property indicator_width1  1           // line width
//--- input parameters
input int    q=5;  // q - period of Stochastic Momentum
input int    r=20; // r - 1st EMA, applied to Stochastic Momentum
input int    s=5;  // s - 2nd EMA, applied to the 1st smoothing
input int    u=3;  // u - 3rd EMA, applied to the 2nd smoothing
input ENUM_APPLIED_PRICE AppliedPrice=PRICE_CLOSE; // AppliedPrice - price type
//--- dynamic arrays, used for the calculation
double MainBuffer[];    // u-period 3rd EMA (graphic plot #0)
double PriceBuffer[];   // price array
double LLBuffer[];      // minimal value (q bars)
double HHBuffer[];      // maximal value (q bars)
double SMBuffer[];      // q-period Stochastic Momentum
double EMA_SMBuffer[];  // r-period 1st EMA
double DEMA_SMBuffer[]; // s-period 2nd EMA
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
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);            // u-period 3rd EMA
   // buffers, used for intermediate calculations
   SetIndexBuffer(1,PriceBuffer,INDICATOR_CALCULATIONS);   // price array
   SetIndexBuffer(2,LLBuffer,INDICATOR_CALCULATIONS);      // min value (q bars)
   SetIndexBuffer(3,HHBuffer,INDICATOR_CALCULATIONS);      // max value (q bars)
   SetIndexBuffer(4,SMBuffer,INDICATOR_CALCULATIONS);      // q-period Stochastic Momentum
   SetIndexBuffer(5,EMA_SMBuffer,INDICATOR_CALCULATIONS);  // r-period 1st EMA
   SetIndexBuffer(6,DEMA_SMBuffer,INDICATOR_CALCULATIONS); // s-period 2nd EMA
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"SM");              // label of graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_TYPE,DRAW_LINE);    // draw as a line
   PlotIndexSetInteger(0,PLOT_LINE_COLOR,Blue);        // line color
   PlotIndexSetInteger(0,PLOT_LINE_STYLE,STYLE_SOLID); // line style
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,1);           // line width
*/
//--- precision
   IndicatorSetInteger(INDICATOR_DIGITS,_Digits);
//---
   begin1=q-1;        //                             - SMBuffer[], LLBuffer[], HHBuffer[]
   begin2=begin1+r-1; // or =(q-1)+(r-1)             - EMA_SMBuffer[]
   begin3=begin2+s-1; // or =(q-1)+(r-1)+(s-1)       - DEMA_SMBuffer[]
   begin4=begin3+u-1; // or =(q-1)+(r-1)+(s-1)+(u-1) - MainBuffer[]
   //
   rates_total_min=begin4+1; // rates total min
//--- starting index for graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- indicator short name
   string shortname=PriceName(AppliedPrice)+","+string(q)+","+string(r)+","+string(s)+","+string(u);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_SM("+shortname+")");
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
   int i,k,pos;
   double min,max;
//--- check rates min
   if(rates_total<rates_total_min) return(0);
//--- calculation of PriceBuffer[]
   CalculatePriceBuffer(
                        AppliedPrice,        // price type
                        rates_total,         // rates total
                        prev_calculated,     // bars, calculated at previous call
                        Open,High,Low,Close, // Open[], High[], Low[], Close[]
                        PriceBuffer          // target array
                       );
//--- calculation of q-period Stochastic Momentum
   // zero arrays SMBuffer[], LLBuffer[], HHBuffer[]
   if(prev_calculated==0)      // at first call
     {
      pos=begin1;              // starting from 0
      for(i=0;i<pos;i++)       // pos values
        {
         SMBuffer[i]=0.0;      // zero values
         LLBuffer[i]=0.0;      //
         HHBuffer[i]=0.0;      //
        }
     }
   else pos=prev_calculated-1; // overwise calculate only last value
   // calculation of SMBuffer[], LLBuffer[], HHBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      // calculation of LLBuffer[] - search for the minimal price (q period)
      // calculation of HHBuffer[] - search for the maximal price (q period)
      min=1000000.0;
      max=-1000000.0;
      for(k=i-(q-1);k<=i;k++)
        {
         if(min>Low[k])  min=Low[k];
         if(max<High[k]) max=High[k];
        }
      LLBuffer[i]=min;
      HHBuffer[i]=max;
      // calculation of SMBuffer[] - q-period Stochastic Momentum
      SMBuffer[i]=PriceBuffer[i]-0.5*(LLBuffer[i]+HHBuffer[i]);
     }
//--- EMA smoothing
   // r-period 1-st EMA
   ExponentialMAOnBufferWB(
                           rates_total,     // rates total
                           prev_calculated, // bars, calculated at previous call
                           begin1,          // starting index
                           r,               // smoothing period
                           SMBuffer,        // input array
                           EMA_SMBuffer     // target array
                          );
   // s-period 2nd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_SMBuffer,DEMA_SMBuffer);
   // u-period 3rd EMA (graphic plot #0)
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_SMBuffer,MainBuffer);
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+