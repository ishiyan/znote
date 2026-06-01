//+------------------------------------------------------------------+
//|                                                     Blau_HLM.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // URL
#property description "q-period Composite High-Low Momentum (William Blau)" // description
#include <WilliamBlau.mqh>              // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window     // indicator in a separate window
#property indicator_buffers 6           // number of buffers used
#property indicator_plots   1           // number of graphic plots
//--- graphic plot #0 (Main)
#property indicator_label1  "HLM"       // label of graphic plot #0
#property indicator_type1   DRAW_LINE   // draw as a line
#property indicator_color1  Blue        // line color
#property indicator_style1  STYLE_SOLID // line style
#property indicator_width1  1           // line width
//--- input parameters
input int    q=2;  // q - period of Momentum
input int    r=20; // r - 1st EMA, applied to Momentum
input int    s=5;  // s - 2nd EMA, applied to the 1st smoothing
input int    u=3;  // u - 3rd EMA, applied to the 2nd smoothing
//--- dynamic arrays
double MainBuffer[];     // u-period 3rd EMA (graphic plot #0)
double HMUBuffer[];      // q-period Up Trend Momentum
double LMDBuffer[];      // q-period Down Trend Momentum
double HLMBuffer[];      // Composite High/Low Momentum (H)
double EMA_HLMBuffer[];  // r-period 1st EMA
double DEMA_HLMBuffer[]; // s-period 2nd EMA
//--- global variables
int    begin1, begin2, begin3, begin4; // starting indexes
int    rates_total_min; // rates total min
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- indicator buffers
   // graphic plot #0
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);             // u-period 3rd EMA
   // buffers, used for intermediate calculations
   SetIndexBuffer(1,HMUBuffer,INDICATOR_CALCULATIONS);      // q-period Momentum (up trend)
   SetIndexBuffer(2,LMDBuffer,INDICATOR_CALCULATIONS);      // q-period Momentum (down trend)
   SetIndexBuffer(3,HLMBuffer,INDICATOR_CALCULATIONS);      // Composite q-period High/Low Momentum
   SetIndexBuffer(4,EMA_HLMBuffer,INDICATOR_CALCULATIONS);  // r-period 1st EMA
   SetIndexBuffer(5,DEMA_HLMBuffer,INDICATOR_CALCULATIONS); // s-period 2nd EMA
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"HLM");             // label of graphic plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_TYPE,DRAW_LINE);    // draw as a line
   PlotIndexSetInteger(0,PLOT_LINE_COLOR,Blue);        // line color
   PlotIndexSetInteger(0,PLOT_LINE_STYLE,STYLE_SOLID); // line style
   PlotIndexSetInteger(0,PLOT_LINE_WIDTH,1);           // line width
*/
//--- precision
   IndicatorSetInteger(INDICATOR_DIGITS,_Digits);
//---
   begin1=q-1;        //                             - HLMBuffer[], HMUBuffer[], LMDBuffer[]
   begin2=begin1+r-1; // or =(q-1)+(r-1)             - EMA_HLMBuffer[]
   begin3=begin2+s-1; // or =(q-1)+(r-1)+(s-1)       - DEMA_HLMBuffer[]
   begin4=begin3+u-1; // or =(q-1)+(r-1)+(s-1)+(u-1) - MainBuffer[]
   //
   rates_total_min=begin4+1; // rates total min
//--- starting bar index for plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- indicator short name
   string shortname=string(q)+","+string(r)+","+string(s)+","+string(u);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_HLM("+shortname+")");
//--- OnInit done
   return(0);
  }
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(
                const int rates_total,     // rates total
                const int prev_calculated, // number of bars, calculated at previous call
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
//--- calculation of q-period Composite High/Low Momentum
   if(prev_calculated==0)      // at first call
     {
      pos=begin1;              // 
      for(i=0;i<pos;i++)       // 
        {
         HLMBuffer[i]=0.0;     // zero values
         HMUBuffer[i]=0.0;     //
         LMDBuffer[i]=0.0;     //
        }
     }
   else pos=prev_calculated-1; // overwise calculate only last value
   // calculation of HLMBuffer[], HMUBuffer[], LMDBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      HMUBuffer[i]=High[i]-High[i-(q-1)];    HMUBuffer[i]=(HMUBuffer[i]>0)?HMUBuffer[i]:0;
      LMDBuffer[i]=-1*(Low[i]-Low[i-(q-1)]); LMDBuffer[i]=(LMDBuffer[i]>0)?LMDBuffer[i]:0;
      HLMBuffer[i]=HMUBuffer[i]-LMDBuffer[i];
     }
//--- EMA smoothing
   // r-period 1st EMA
   ExponentialMAOnBufferWB(
                           rates_total,     // rates total
                           prev_calculated, // number of bars, calculated at previous call
                           begin1,          // starting index
                           r,               // smoothing period
                           HLMBuffer,       // input array
                           EMA_HLMBuffer    // target array
                          );
   // s-period 2nd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_HLMBuffer,DEMA_HLMBuffer);
   // u-period 3rd EMA (graphic plot #0)
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_HLMBuffer,MainBuffer);
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+