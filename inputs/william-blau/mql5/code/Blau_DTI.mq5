//+------------------------------------------------------------------+
//|                                                     Blau_DTI.mq5 |
//|                        Copyright 2011, MetaQuotes Software Corp. |
//|                                              http://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2011, MetaQuotes Software Corp." // copyright
#property link      "http://www.mql5.com"                       // URL
#property description "Directional Trend Index (William Blau)"  // description
#include <WilliamBlau.mqh>               // include file (terminal_data_folder\MQL5\Include)
//--- indicator settings
#property indicator_separate_window      // indicator in a separate window
#property indicator_buffers 11           // number of buffers used
#property indicator_plots   1            // number of graphic plots
//--- horizontal levels
#property indicator_level1 -25           // level #0
#property indicator_level2 25            // level #1
#property indicator_levelcolor Silver    // level line color
#property indicator_levelstyle STYLE_DOT // level line style
#property indicator_levelwidth 1         // level line width
//--- scale
#property indicator_minimum -100         // lower bound
#property indicator_maximum 100          // upper boud
//--- graphic plot #0 (Main)
#property indicator_label1  "DTI"        // label of graphic plot #0
#property indicator_type1   DRAW_LINE    // draw as a line
#property indicator_color1  Blue         // line color
#property indicator_style1  STYLE_SOLID  // line style
#property indicator_width1  1            // line width
//--- input parameters
input int    q=2;  // q - period of Momentum
input int    r=20; // r - 1st EMA, applied to Momentum
input int    s=5;  // s - 2nd EMA, applied to the 1st smoothing
input int    u=3;  // u - 3rd EMA, applied to the 2nd smoothing
//--- dynamic arrays
double MainBuffer[];        // DTI (graphic plot #0)
double HMUBuffer[];         // q-period Up Trend Momentum
double LMDBuffer[];         // q-period Down Trend Momentum
double HLMBuffer[];         // Composite q-period High/Low Momentum
double EMA_HLMBuffer[];     // r-period 1st EMA
double DEMA_HLMBuffer[];    // s-period 2nd EMA
double TEMA_HLMBuffer[];    // u-period 3rd EMA
double AbsHLMBuffer[];      // Composite q-period High/Low Momentum (absolute values)
double EMA_AbsHLMBuffer[];  // r-period 1st EMA (absolute values)
double DEMA_AbsHLMBuffer[]; // s-period 2nd EMA (absolute values)
double TEMA_AbsHLMBuffer[]; // u-period 3rd EMA (absolute values)
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
   SetIndexBuffer(0,MainBuffer,INDICATOR_DATA);                 // DTI
   // buffers, used for intermediate calculations
   SetIndexBuffer(1,HMUBuffer,INDICATOR_CALCULATIONS);          // q-period Up Trend Momentum
   SetIndexBuffer(2,LMDBuffer,INDICATOR_CALCULATIONS);          // q-period Down Trend Momentum
   SetIndexBuffer(3,HLMBuffer,INDICATOR_CALCULATIONS);          // Composite q-period High/Low Momentum
   SetIndexBuffer(4,EMA_HLMBuffer,INDICATOR_CALCULATIONS);      // r-period 1st EMA
   SetIndexBuffer(5,DEMA_HLMBuffer,INDICATOR_CALCULATIONS);     // s-period 2nd EMA
   SetIndexBuffer(6,TEMA_HLMBuffer,INDICATOR_CALCULATIONS);     // u-period 3rd EMA
   SetIndexBuffer(7,AbsHLMBuffer,INDICATOR_CALCULATIONS);       // Composite q-period High/Low Momentum (absolute values)
   SetIndexBuffer(8,EMA_AbsHLMBuffer,INDICATOR_CALCULATIONS);   // r-period 1st EMA (absolute values)
   SetIndexBuffer(9,DEMA_AbsHLMBuffer,INDICATOR_CALCULATIONS);  // s-period 2nd EMA (absolute values)
   SetIndexBuffer(10,TEMA_AbsHLMBuffer,INDICATOR_CALCULATIONS); // u-period 3rd EMA (absolute values)
/*
//--- graphic plot #0 (Main)
   PlotIndexSetString(0,PLOT_LABEL,"DTI");             // label of graphic plot #0
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
   IndicatorSetInteger(INDICATOR_LEVELCOLOR,Silver);       // level line color
   IndicatorSetInteger(INDICATOR_LEVELSTYLE,STYLE_DOT);    // level line style
   IndicatorSetInteger(INDICATOR_LEVELWIDTH,1);            // level line width
   IndicatorSetString(INDICATOR_LEVELTEXT,0,"Oversold");   // description of level #0 "Oversold"
   IndicatorSetString(INDICATOR_LEVELTEXT,1,"Overbought"); // description of level #1 "Overbought"
//--- scale
   IndicatorSetDouble(INDICATOR_MINIMUM,-100); // lower bound
   IndicatorSetDouble(INDICATOR_MAXIMUM,100);  // upper bound
*/
//---
   begin1=q-1;        //                             - HLMBuffer[], AbsHLMBuffer[], HMUBuffer[], LMDBuffer[]
   begin2=begin1+r-1; // or =(q-1)+(r-1)             - EMA_...[]
   begin3=begin2+s-1; // or =(q-1)+(r-1)+(s-1)       - DEMA_...[]
   begin4=begin3+u-1; // or =(q-1)+(r-1)+(s-1)+(u-1) - TEMA_...[], MainBuffer[]
   //
   rates_total_min=begin4+1; // rates total min
//--- starting bar index for plot #0
   PlotIndexSetInteger(0,PLOT_DRAW_BEGIN,begin4);
//--- indicator short name
   string shortname=string(q)+","+string(r)+","+string(s)+","+string(u);
   IndicatorSetString(INDICATOR_SHORTNAME,"Blau_DTI("+shortname+")");
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
//--- calculation of HLM and |HLM|
   if(prev_calculated==0)      // at first call
     {
      pos=begin1;              // 
      for(i=0;i<pos;i++)       // 
        {
         HLMBuffer[i]=0.0;     // zero values
         AbsHLMBuffer[i]=0.0;  //
         HMUBuffer[i]=0.0;     //
         LMDBuffer[i]=0.0;     //
        }
     }
   else pos=prev_calculated-1; // overwise calculate only last value
   // calculation of HLMBuffer[], AbsHLMBuffer[], HMUBuffer[], LMDBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      HMUBuffer[i]=High[i]-High[i-(q-1)];    HMUBuffer[i]=(HMUBuffer[i]>0)?HMUBuffer[i]:0;
      LMDBuffer[i]=-1*(Low[i]-Low[i-(q-1)]); LMDBuffer[i]=(LMDBuffer[i]>0)?LMDBuffer[i]:0;
      HLMBuffer[i]=HMUBuffer[i]-LMDBuffer[i];
      AbsHLMBuffer[i]=MathAbs(HLMBuffer[i]);
     }
//--- EMA smoothing
   // r-period 1st EMA
   ExponentialMAOnBufferWB(
                           rates_total,     // rates total
                           prev_calculated, // bars, calculated at previous call
                           begin1,          // starting index
                           r,               // smoothing period
                           HLMBuffer,       // input array
                           EMA_HLMBuffer    // target array
                          );
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin1,r,AbsHLMBuffer,EMA_AbsHLMBuffer);
   // s-period 2nd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_HLMBuffer,DEMA_HLMBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin2,s,EMA_AbsHLMBuffer,DEMA_AbsHLMBuffer);
   // u-period 3rd EMA
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_HLMBuffer,TEMA_HLMBuffer);
   ExponentialMAOnBufferWB(rates_total,prev_calculated,begin3,u,DEMA_AbsHLMBuffer,TEMA_AbsHLMBuffer);
//--- calculation of DTI (graphic plot #0)
   if(prev_calculated==0)      // at first call
     {
      pos=begin4;              // 
      for(i=0;i<pos;i++)       // 
         MainBuffer[i]=0.0;    // zero values
     }
   else pos=prev_calculated-1; // overwise calculate only last value
   // calculation of MainBuffer[]
   for(i=pos;i<rates_total;i++)
     {
      value1=100*TEMA_HLMBuffer[i];
      value2=TEMA_AbsHLMBuffer[i];
      MainBuffer[i]=(value2>0)?value1/value2:0;
     }
//--- OnCalculate done. Return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+